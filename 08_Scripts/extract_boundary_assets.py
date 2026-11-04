#!/usr/bin/env python3
"""Extract source assets for the corrected course maps, without running a model.

Run with the host's QGIS Python. All input and output paths are explicit and the
script never writes outside --root. Source geometries and attributes stay dated.
The GeoPackage contains viewport assets, not a newly invented course boundary.
"""
import argparse
import collections
import concurrent.futures
from datetime import datetime, timezone
import json
import math
import multiprocessing
import os
from pathlib import Path
import platform
import re
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from qgis.core import (Qgis, QgsApplication, QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform, QgsFeature, QgsFeatureRequest,
                       QgsField, QgsGeometry, QgsPointXY, QgsProject,
                       QgsRectangle, QgsVectorFileWriter, QgsVectorLayer)
from qgis.PyQt.QtCore import QVariant

GML = '{http://www.opengis.net/gml}'
SOURCE_DATES = {
    '神田川流域（想定最大規模）': '2018-03-30',
    '荒川水系神田川流域（想定最大規模）': '2024-02-15',
    '荒川水系神田川流域（計画規模）': '2024-02-15',
    '隅田川・新河岸川流域（想定最大規模）': '2021-03-30',
}


def clean(value):
    if value is None or value == QVariant():
        return None
    if isinstance(value, (int, float, str, bool)):
        return value
    return str(value)


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def xml_members(handle):
    iterator = ET.iterparse(handle, events=('start', 'end'))
    _, root = next(iterator)
    for event, element in iterator:
        if event == 'end' and element.tag.endswith('cityObjectMember'):
            if len(element):
                yield element[0]
            element.clear()
            root.clear()


def load_codes(raw):
    codes = {}
    for path in sorted(raw.rglob('*codelists*.zip')):
        with ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith('.xml') and not Path(name).name.startswith('._'):
                    try:
                        root = ET.fromstring(archive.read(name))
                    except ET.ParseError:
                        continue
                    mapping = {}
                    for item in root.iter(GML + 'Definition'):
                        mapping[item.findtext(GML + 'name')] = item.findtext(GML + 'description')
                    codes[Path(name).name] = mapping
    return codes


def attributes(element, codes):
    values = {}
    for item in element.iter():
        key = item.tag.split('}')[-1]
        if len(item) or not item.text or key in ('posList', 'pos', 'textureCoordinates', 'imageURI'):
            continue
        text = item.text.strip()
        if not text:
            continue
        values.setdefault(key, [])
        if text not in values[key]:
            values[key].append(text)
        if 'codeSpace' in item.attrib:
            label = codes.get(Path(item.attrib['codeSpace']).name, {}).get(text)
            if label:
                values.setdefault(key + '_label', [])
                if label not in values[key + '_label']:
                    values[key + '_label'].append(label)
    return {key: value[0] if len(value) == 1 else json.dumps(value, ensure_ascii=False)
            for key, value in values.items()}


def source_streams(raw, category):
    """One original member per physical source. Duplicate records are resolved later."""
    for path in sorted(raw.rglob('*.gml')):
        if path.name.startswith('._'):
            continue
        kind = path.name.split('_')[1] if '_' in path.name else ''
        if kind == category:
            yield str(path.relative_to(raw)), path, None
    for path in sorted(raw.rglob('*.zip')):
        if not ('bbox_pack' in path.name or 'Flood_Selected' in path.name):
            continue
        with ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith('.gml') and ('_' + category + '_') in Path(name).name:
                    yield str(path.relative_to(raw)) + '::' + name, path, name


def open_stream(path, member):
    if member:
        archive = ZipFile(path)
        return archive, archive.open(member)
    return None, path.open('rb')


def source_polygons(element, transformer, lonlat_extent, buildings=False):
    """Return horizontal LOD1 model projection, retaining exterior/interior rings."""
    parents = [item for item in element.iter()
               if item.tag.split('}')[-1] in
               (('lod1Solid', 'lod1MultiSurface') if buildings else
                ('lod1MultiSurface', 'lod1Surface', 'lod1Geometry'))]
    polygons, heights = [], []
    xmin, ymin, xmax, ymax = lonlat_extent
    for parent in parents:
        for poly in parent.iter(GML + 'Polygon'):
            rings = []
            zvalues = []
            for ring_type in ('exterior', 'interior'):
                for ring in poly.findall(GML + ring_type):
                    coordinates = ring.find('.//' + GML + 'posList')
                    if coordinates is None or not coordinates.text:
                        continue
                    array = list(map(float, coordinates.text.split()))
                    dimension = int(coordinates.get('srsDimension', '3'))
                    if len(array) % dimension:
                        continue
                    points = []
                    for i in range(0, len(array), dimension):
                        lat, lon = array[i], array[i + 1]
                        points.append(QgsPointXY(lon, lat))
                        if dimension >= 3:
                            zvalues.append(array[i + 2])
                    if points and points[0] != points[-1]:
                        points.append(points[0])
                    if len(points) >= 4:
                        rings.append(points)
            heights.extend(zvalues)
            if not rings or (buildings and zvalues and max(zvalues) - min(zvalues) > .15):
                continue
            xx = [p.x() for p in rings[0]]
            yy = [p.y() for p in rings[0]]
            if max(xx) < xmin or min(xx) > xmax or max(yy) < ymin or min(yy) > ymax:
                continue
            geom = QgsGeometry.fromPolygonXY(rings)
            geom.transform(transformer)
            if not geom.isGeosValid():
                geom = geom.makeValid()
            if not geom.isEmpty() and geom.area() > .001:
                polygons.append(geom)
    if not polygons:
        return None, heights
    result = QgsGeometry.unaryUnion(polygons)
    if not result.isGeosValid():
        result = result.makeValid()
    result.convertToMultiType()
    return result, heights


def parse_source(task):
    """Parse one unchanged source in a separate process; only parent writes GPKG."""
    source, path, member, bbox, category, codes = task
    app = QgsApplication([], False)
    app.initQgis()
    project = QgsProject.instance()
    # CityGML EPSG:6697 supplies JGD2011 latitude, longitude, orthometric height.
    # Its horizontal coordinates are EPSG:6668; OSM and CLI bbox remain WGS84.
    transformer = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:6668'),
                                         QgsCoordinateReferenceSystem('EPSG:6677'), project)
    window = QgsGeometry.fromRect(QgsRectangle(*bbox))
    window.transform(QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),
                                           QgsCoordinateReferenceSystem('EPSG:6677'), project))
    archive, handle = open_stream(Path(path), member)
    rows, scanned = [], 0
    try:
        for element in xml_members(handle):
            scanned += 1
            geom, zvalues = source_polygons(element, transformer, bbox, buildings=category == 'bldg')
            if geom is None or not geom.intersects(window):
                continue
            if category != 'bldg':
                geom = geom.intersection(window)
                geom.convertToMultiType()
            rows.append((element.get(GML + 'id'), attributes(element, codes), bytes(geom.asWkb()),
                         max(zvalues) - min(zvalues) if zvalues else None))
    finally:
        handle.close()
        if archive:
            archive.close()
    return source, scanned, rows


class Extractor:
    def __init__(self, args):
        self.args = args
        self.root = args.root.resolve()
        self.raw = self.root / 'raw'
        self.output = self.root / 'assets'
        self.output.mkdir(parents=True, exist_ok=True)
        self.gpkg = self.output / 'assets.gpkg'
        if self.gpkg.exists():
            raise RuntimeError('Output exists: use a fresh --root or inspect the saved extraction first.')
        self.crs = QgsCoordinateReferenceSystem('EPSG:6677')
        self.project = QgsProject.instance()
        self.project.setCrs(self.crs)
        self.transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'), self.crs, self.project)
        self.lonlat_extent = args.bbox
        self.window = QgsGeometry.fromRect(QgsRectangle(*args.bbox))
        self.window.transform(self.transform)
        self.bounds = self.window.boundingBox()
        self.codes = load_codes(self.raw)
        self.layers = {}
        self.audit = {'schema_version': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
                      'host': platform.node(), 'pid': os.getpid(), 'python': sys.version,
                      'qgis': Qgis.QGIS_VERSION, 'crs': 'EPSG:6677', 'lonlat_viewport': args.bbox,
                      'extent_epsg6677': [self.bounds.xMinimum(), self.bounds.yMinimum(), self.bounds.xMaximum(), self.bounds.yMaximum()],
                      'course_boundary': 'Not defined here. Apply the registered course layers in the downstream analysis.',
                      'no_cfd': True, 'layers': {}, 'sources': [], 'coverage': []}

    def layer(self, name, geometry, fields):
        layer = QgsVectorLayer(geometry + '?crs=EPSG:6677', name, 'memory')
        layer.dataProvider().addAttributes([QgsField(key, kind) for key, kind in fields])
        layer.updateFields()
        self.layers[name] = layer
        return layer

    def add(self, layer, geom, values):
        if geom is None or geom.isEmpty():
            return
        feature = QgsFeature(layer.fields())
        feature.setGeometry(geom)
        feature.setAttributes([clean(value) for value in values])
        ok = layer.dataProvider().addFeatures([feature])[0]
        if not ok:
            raise RuntimeError('Failed adding feature to ' + layer.name())

    def source(self, source, kind, scanned, selected, note, **extra):
        entry = {'source_member': source, 'data_type': kind, 'scanned': scanned,
                 'selected': selected, 'note': note, **extra}
        self.audit['sources'].append(entry)
        print(json.dumps(entry, ensure_ascii=False), flush=True)

    def parsed_sources(self, category):
        tasks = [(source, str(path), member, self.lonlat_extent, category, self.codes)
                 for source, path, member in source_streams(self.raw, category)]
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.args.workers,
                mp_context=multiprocessing.get_context('spawn')) as pool:
            # Completion order does not determine provenance; source path priority does.
            yield from pool.map(parse_source, tasks)

    def buildings(self):
        S, D, I = QVariant.String, QVariant.Double, QVariant.Int
        layer = self.layer('buildings', 'MultiPolygon', [
            ('asset_id', S), ('ward_code', S), ('gml_id', S), ('building_id', S),
            ('usage', S), ('usage_code', S), ('detailed_use', S), ('height_m', D),
            ('height_source', S), ('levels', D), ('levels_source', S),
            ('plan_area_m2', D), ('floor_proxy_m2', D), ('survey_year', I),
            ('model_year', I), ('creation_date', S), ('source_member', S), ('source_attrs_json', S)])
        seen, duplicates = set(), 0
        for source, scanned, rows in self.parsed_sources('bldg'):
            selected = 0
            for gmlid, attrs, wkb, fallback_height in rows:
                    geom = QgsGeometry()
                    geom.fromWkb(wkb)
                    buildingid = attrs.get('buildingID', '')
                    ward = str(attrs.get('city') or buildingid[:5] or 'unknown')
                    key = (ward, gmlid)
                    if key in seen:
                        duplicates += 1
                        continue
                    seen.add(key)
                    height = number(attrs.get('measuredHeight'))
                    height_source = 'bldg:measuredHeight'
                    if height is None or height <= 0:
                        height = fallback_height
                        height_source = 'LOD1 zmax minus zmin'
                    levels = number(attrs.get('storeysAboveGround'))
                    # 9999/-9999 encode missing storeys in these original records.
                    # Preserve the original value in source_attrs_json.
                    if levels in (9999, -9999):
                        levels = None
                    levels_source = 'source'
                    if levels is None or levels <= 0:
                        levels = max(1, round(height / 3.3)) if height else None
                        levels_source = 'height / 3.3 m proxy' if levels else 'missing'
                    year = number(attrs.get('surveyYear'))
                    year = int(year) if year and year >= 1900 else None
                    area = geom.area()
                    self.add(layer, geom, [ward + ':' + str(gmlid), ward, gmlid, buildingid,
                        attrs.get('usage_label', '不明'), attrs.get('usage'), attrs.get('detailedUsage_label'),
                        height, height_source, levels, levels_source, area, area * levels if levels else None,
                        year, 2025, attrs.get('creationDate'), source, json.dumps(attrs, ensure_ascii=False)])
                    selected += 1
            self.source(source, 'buildings', scanned, selected,
                'Full LOD1 horizontal projection selected by viewport overlap. Ward from source city/buildingID. Not a surveyed footprint.',
                license='CC BY 4.0', model_year=2025)
        self.audit['building_duplicate_records_omitted'] = duplicates
        self.audit['building_wards'] = dict(collections.Counter(str(f['ward_code']) for f in layer.getFeatures()))
        self.audit['building_normalization'] = {
            'storeys_missing_sentinels': [9999, -9999],
            'sentinel_records': sum(number(json.loads(str(f['source_attrs_json'])).get('storeysAboveGround')) in (9999, -9999) for f in layer.getFeatures()),
            'rule': 'Missing/nonpositive/sentinel storeys use max(1, round(height_m / 3.3)) when a positive height is available; otherwise null. Original storeys preserved in source_attrs_json.',
            'levels_source_counts': dict(collections.Counter(str(f['levels_source']) for f in layer.getFeatures())),
            'floor_proxy': 'Full LOD1 horizontal projection area times normalized source/proxy levels. Not measured floor area.'}

    def citygml_themes(self):
        S, I = QVariant.String, QVariant.Int
        specs = {
            'luse': ('land_use', [('asset_id', S), ('gml_id', S), ('class', S), ('class_label', S),
                      ('orgLandUse_label', S), ('survey_year', I), ('model_year', I), ('source_member', S), ('source_attrs_json', S)]),
            'fld': ('flood', [('asset_id', S), ('gml_id', S), ('scenario', S), ('scenario_name', S), ('rank', S),
                     ('rank_label', S), ('source_date', S), ('scale', S), ('model_year', I), ('source_member', S), ('source_attrs_json', S)])}
        for category, (name, fields) in specs.items():
            layer = self.layer(name, 'MultiPolygon', fields)
            seen = set()
            for source, scanned, rows in self.parsed_sources(category):
                selected = duplicates = 0
                for gmlid, attrs, wkb, fallback_height in rows:
                        geom = QgsGeometry()
                        geom.fromWkb(wkb)
                        scenario = attrs.get('name', '') if category == 'fld' else ''
                        key = (gmlid, scenario)
                        if key in seen:
                            duplicates += 1
                            continue
                        seen.add(key)
                        geom = geom.intersection(self.window)
                        geom.convertToMultiType()
                        rawattrs = json.dumps(attrs, ensure_ascii=False)
                        if category == 'luse':
                            year = number(attrs.get('surveyYear'))
                            values = [gmlid, gmlid, attrs.get('class'), attrs.get('class_label'),
                                      attrs.get('orgLandUse_label'), int(year) if year and year >= 1900 else None,
                                      2025, source, rawattrs]
                        else:
                            scale = 'L1' if '_l1_' in source else 'L2'
                            values = [scenario + ':' + str(gmlid), gmlid, scenario, scenario, attrs.get('rank'),
                                      attrs.get('rank_label'), SOURCE_DATES.get(scenario), scale, 2025, source, rawattrs]
                        self.add(layer, geom, values)
                        selected += 1
                self.source(source, name, scanned, selected,
                    'Original source polygons intersected with viewport; source absence does not establish safety or completeness.',
                    duplicate_records_omitted=duplicates, license='CC BY 4.0', model_year=2025)

    def osm(self):
        S = QVariant.String
        fields = [('osm_id', S), ('name', S), ('tag', S), ('source_date', S)]
        layers = {key: self.layer(key, geometry, fields) for key, geometry in
                  [('osm_buildings', 'MultiPolygon'), ('roads', 'MultiLineString'),
                   ('rail', 'MultiLineString'), ('water', 'MultiPolygon'), ('water_lines', 'MultiLineString')]}
        path = self.raw / 'support/Kanda_Nihonbashi_OSM.json'
        data = json.loads(path.read_text())
        counts = collections.Counter()
        for item in data['elements']:
            tags = item.get('tags', {})
            coordinates = item.get('geometry')
            if not coordinates:
                continue
            points = [QgsPointXY(point['lon'], point['lat']) for point in coordinates]
            choices = []
            if tags.get('building') and len(points) > 3 and points[0] == points[-1]:
                choices.append(('osm_buildings', QgsGeometry.fromPolygonXY([points]), tags['building']))
            if tags.get('highway') and len(points) >= 2:
                choices.append(('roads', QgsGeometry.fromPolylineXY(points), tags['highway']))
            if tags.get('railway') in ('rail', 'subway') and len(points) >= 2:
                choices.append(('rail', QgsGeometry.fromPolylineXY(points), tags['railway']))
            if tags.get('natural') == 'water' and len(points) > 3 and points[0] == points[-1]:
                choices.append(('water', QgsGeometry.fromPolygonXY([points]), 'water'))
            if tags.get('waterway') and len(points) >= 2:
                choices.append(('water_lines', QgsGeometry.fromPolylineXY(points), tags['waterway']))
            for key, geom, kind in choices:
                geom.transform(self.transform)
                if not geom.intersects(self.window):
                    continue
                if not geom.isGeosValid():
                    geom = geom.makeValid()
                geom = geom.intersection(self.window)
                geom.convertToMultiType()
                self.add(layers[key], geom, [str(item['id']), tags.get('name'), kind, '2026-10-13'])
                counts[key] += 1
        self.source(str(path.relative_to(self.raw)), 'osm', len(data['elements']), dict(counts),
                    'Original snapshot acquired bbox139.763,35.682,139.787,35.698. Map records may be incomplete.',
                    source_url='https://www.openstreetmap.org/copyright', data_year='2026-10-13', license='ODbL 1.0')

    def vector(self, archive, member, key, geometry, fields, extract, encoding=None, full_geometry=False):
        source = QgsVectorLayer('/vsizip/' + str(archive) + '/' + member, key, 'ogr')
        if encoding:
            source.setProviderEncoding(encoding)
        if not source.isValid():
            raise RuntimeError('Invalid vector source: ' + str(archive) + '::' + member)
        layer = self.layers.get(key) or self.layer(key, geometry, fields)
        transformer = QgsCoordinateTransform(source.crs(), self.crs, self.project)
        reverse = QgsCoordinateTransform(self.crs, source.crs(), self.project)
        rect = reverse.transformBoundingBox(self.bounds)
        selected = 0
        for item in source.getFeatures(QgsFeatureRequest().setFilterRect(rect)):
            geom = QgsGeometry(item.geometry())
            geom.transform(transformer)
            if not geom.intersects(self.window):
                continue
            if not geom.isGeosValid():
                geom = geom.makeValid()
            attrs = {field.name(): clean(item[field.name()]) for field in item.fields()}
            values = extract(attrs, geom, str(archive.relative_to(self.raw)) + '::' + member)
            if not full_geometry:
                geom = geom.intersection(self.window)
            geom.convertToMultiType()
            self.add(layer, geom, values)
            selected += 1
        self.source(str(archive.relative_to(self.raw)) + '::' + member, key, source.featureCount(), selected,
                    'Full intersecting source geometry retained.' if full_geometry else 'Source geometry clipped to viewport.',
                    source_crs=source.crs().authid())

    def vectors(self):
        S, D, I = QVariant.String, QVariant.Double, QVariant.Int
        censusfields = [('ward_code', S), ('town_code', S), ('town_name', S), ('population_2020', I),
                        ('households_2020', I), ('repeat_flag', S), ('hcode', I), ('full_town_area_m2', D),
                        ('viewport_overlap_m2', D), ('source_member', S)]
        for ward in ('Chiyoda', 'Chuo'):
            archive = self.raw / ('support/' + ward + '_2020.zip')
            with ZipFile(archive) as z:
                member = next(name for name in z.namelist() if name.endswith('.shp'))
            self.vector(archive, member, 'census', 'MultiPolygon', censusfields,
                lambda a, g, s: [str(a.get('PREF', '')) + str(a.get('CITY', '')), str(a.get('KEY_CODE')),
                    a.get('S_NAME'), a.get('JINKO'), a.get('SETAI'), a.get('KIGO_E'), a.get('HCODE'),
                    g.area(), g.intersection(self.window).area(), s], encoding='CP932', full_geometry=True)
        stationfields = [('ward_code', S), ('name', S), ('line', S), ('source_member', S), ('source_attrs_json', S)]
        for ward in ('13101', '13102'):
            archive = self.raw / ('plateau/' + ward + '_related.zip')
            with ZipFile(archive) as z:
                members = [name for name in z.namelist() if name.endswith('_station.geojson')]
            for member in members:
                self.vector(archive, member, 'stations', 'MultiPoint', stationfields,
                    lambda a, g, s, w=ward: [w, a.get('駅名'), a.get('路線名'), s, json.dumps(a, ensure_ascii=False)])
        archive = self.raw / 'support/mlit_tokyo_geojson.zip'
        zonefields = [('ward_code', S), ('zone_name', S), ('FAR', D), ('BCR', D), ('source_year', I), ('source_member', S), ('source_attrs_json', S)]
        with ZipFile(archive) as z:
            members = [name for name in z.namelist() if name.endswith('_youto.geojson') and ('13101_' in name or '13102_' in name)]
        for member in members:
            self.vector(archive, member, 'zones', 'MultiPolygon', zonefields,
                lambda a, g, s: [str(a.get('Citycode')), a.get('YoutoName'), number(a.get('FAR')),
                                 number(a.get('BCR')), 2025, s, json.dumps(a, ensure_ascii=False)])
        greenfields = [('name', S), ('kind', S), ('species', S), ('source_year', S), ('source_member', S), ('source_attrs_json', S)]
        for filename in ('01_kouenryokuchi.zip', '02_gairoju.zip'):
            archive = self.raw / ('support/' + filename)
            with ZipFile(archive) as z:
                members = [name for name in z.namelist() if name.endswith('.shp')]
            for member in members:
                if filename.startswith('02'):
                    key, geometry, year = ('trees', 'MultiPoint', '2020') if '_pt.shp' in member else ('tree_routes', 'MultiLineString', '2024')
                else:
                    if member.endswith('_pt.shp'):
                        continue
                    key, geometry, year = 'parks', 'MultiPolygon', '2020/2024 source metadata'
                self.vector(archive, member, key, geometry, greenfields,
                    lambda a, g, s, y=year: [a.get('公園名') or a.get('路線名') or a.get('名称'),
                        a.get('区分'), a.get('樹種'), y, s, json.dumps(a, ensure_ascii=False)], encoding='CP932')

    def coverage(self):
        S = QVariant.String
        layer = self.layer('source_coverage', 'MultiPolygon', [('data_type', S), ('ward_code', S),
            ('status', S), ('meaning', S), ('source_member', S)])
        records = [
            ('osm', 'both', 'acquisition_window', 'Original Overpass query window; record completeness is not guaranteed.', 'support/Kanda_Nihonbashi_OSM.json'),
            ('buildings', 'both', 'viewport_selection', 'Source tiles span viewport; full source LOD1 objects are retained. Manifest lists ward counts and unknown attributes.', 'PLATEAU original members'),
            ('land_use', 'both', 'record_support', 'Only union of selected observed land-use polygons; missing areas require coverage reporting.', 'PLATEAU original members'),
            ('flood', 'both', 'positive_hazard_records', 'Union of recorded hazard polygons. Absence is not a surveyed safe area or full hazard-domain coverage.', 'plateau/Chiyoda_Flood_Selected_Original_Members.zip'),
            ('census', 'both', 'full_town_source', 'Complete town polygons and full-town totals retained. Viewport fractions do not supply exact partial-town population.', 'support/Chiyoda_2020.zip + Chuo_2020.zip'),
            ('stations', 'both', 'point_records', 'Separate source name/line point records; station entrances and interchange areas are not surveyed here.', 'plateau/13101_related.zip + 13102_related.zip'),
            ('zones', 'both', 'reference_gis', 'Source polygons from FY2025 planning GIS; parcel legal limits require official ward map review.', 'support/mlit_tokyo_geojson.zip'),
            ('green', 'both', 'inventory_records', 'Park, point tree and route inventories have distinct source dates and spatial coverage; route counts are not viewport tree counts.', 'support/01_kouenryokuchi.zip + 02_gairoju.zip')]
        for kind, ward, status, meaning, source in records:
            key = {'land_use': 'land_use', 'flood': 'flood'}.get(kind)
            geom = QgsGeometry.unaryUnion([f.geometry() for f in self.layers[key].getFeatures()]) if key else QgsGeometry(self.window)
            geom.convertToMultiType()
            self.add(layer, geom, [kind, ward, status, meaning, source])
            self.audit['coverage'].append(dict(data_type=kind, status=status, meaning=meaning,
                                               geometry_area_m2=geom.area()))

    def save(self):
        for name, layer in self.layers.items():
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = 'GPKG'
            options.layerName = name
            options.fileEncoding = 'UTF-8'
            options.actionOnExistingFile = (QgsVectorFileWriter.CreateOrOverwriteLayer
                if self.gpkg.exists() else QgsVectorFileWriter.CreateOrOverwriteFile)
            result = QgsVectorFileWriter.writeAsVectorFormatV3(layer, str(self.gpkg), self.project.transformContext(), options)
            if result[0] != QgsVectorFileWriter.NoError:
                raise RuntimeError(str(result))
            self.audit['layers'][name] = {'features': layer.featureCount(), 'geometry': QgsGeometry.displayString(layer.wkbType()) if hasattr(QgsGeometry, 'displayString') else str(layer.wkbType()),
                'fields': [{'name': field.name(), 'type': field.typeName()} for field in layer.fields()]}
        self.audit['completed_utc'] = datetime.now(timezone.utc).isoformat()
        self.audit['output_gpkg'] = str(self.gpkg)
        self.audit['output_bytes'] = self.gpkg.stat().st_size
        self.audit['source_roles'] = {'PLATEAU': 'Building/thematic models, CC BY4.0,2025 release; per-record survey year separate.',
            'OSM': 'Recorded routes/background, ODbL1.0,2026-10-13 snapshot.', 'census': 'Full official 2020 town unit boundaries/totals, e-Stat terms.',
            'planning': 'MLIT FY2025 reference polygons.', 'green': 'Tokyo inventory records, original attributes retained.'}
        self.audit['source_crs'] = {'CityGML': 'EPSG:6697; horizontal EPSG:6668, latitude-longitude axis order explicitly reversed.',
                                    'OSM': 'EPSG:4326', 'output': 'EPSG:6677'}
        (self.output / 'Source_Manifest.json').write_text(json.dumps(self.audit, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'completed': True, 'gpkg': str(self.gpkg), 'layers': self.audit['layers']}, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--bbox', type=float, nargs=4, default=[139.763, 35.682, 139.787, 35.698], metavar=('WEST', 'SOUTH', 'EAST', 'NORTH'))
    args = parser.parse_args()
    app = QgsApplication([], False)
    app.initQgis()
    extractor = Extractor(args)
    extractor.buildings()
    extractor.citygml_themes()
    extractor.osm()
    extractor.vectors()
    extractor.coverage()
    extractor.save()
    # QGIS-owned memory layers can outlive their providers during interpreter teardown.
    os._exit(0)


if __name__ == '__main__':
    main()
