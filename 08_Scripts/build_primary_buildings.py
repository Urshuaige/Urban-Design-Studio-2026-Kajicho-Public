#!/usr/bin/env python3
"""Build the Primary Area analysis and appearance layers from public inputs."""
import csv
import json
import re
import sqlite3
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path

from shapely import make_valid, union_all
from shapely.geometry import Polygon, mapping
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "04_Data/Ready/QGIS_Current_2026-11-04"
THEMES = {
    "energy": ("D009_building_energy_carbon", "gml_id"),
    "people": ("D088_current_building_allocation", "gml_id"),
    "chronology": ("D008_building_2011_evidence", "gml_id"),
    "renewal": ("D236_renewal_buildings", "asset_id"),
}
PREFERRED = (
    "gml_id", "asset_id", "building_id", "building_use_en", "building_use_ja",
    "height_m", "levels", "plan_area_m2", "floor_proxy_m2", "footprint_area_m2",
    "official_height_m", "official_storeys", "official_site_area_m2",
    "official_total_floor_area_m2", "construction_year_status", "age_evidence",
    "age_year_exact", "age_year_from", "age_year_to", "age_confidence",
    "zone_en", "far_pct", "bcr_pct", "land_use_en", "planning_status",
    "annual_energy_kwh", "annual_co2_kg", "energy_status",
    "people_residents_main", "people_work_floor_m2", "people_residents_source_year",
    "energy_energy_est_gj_y", "energy_co2_est_t_y", "energy_work_share",
    "renewal_renew_grade", "chronology_epoch_2011",
)
EXTRA_PRIORITY = (
    "usage_code", "detailed_use", "survey_year", "model_year", "raw_height_m",
    "raw_levels", "construction_year", "structure_code", "basement_storeys",
    "height_source", "levels_source", "town_name_ja", "town_code", "current_status",
    "geometry_status", "age_display", "age_method", "age_note", "pub_built_year",
    "pub_year_from", "pub_year_status", "pub_source_url", "public_floor_area",
    "land_use_overlap_pct", "flood_note", "fire_prevention_en", "height_control_en",
    "special_far_en", "district_plans_en", "urban_renaissance_en",
)


def dbf_rows(path):
    data = path.read_bytes()
    n, header, stride = struct.unpack_from("<IHH", data, 4)
    fields = []
    start = 1
    for p in range(32, header - 1, 32):
        descriptor = data[p:p + 32]
        fields.append((descriptor[:11].split(b"\0")[0].decode(), chr(descriptor[11]),
                       start, descriptor[16], descriptor[17]))
        start += descriptor[16]
    for i in range(n):
        raw = data[header + i * stride:header + (i + 1) * stride]
        assert raw[:1] == b" "
        values = {}
        for name, kind, offset, width, decimal in fields:
            value = raw[offset:offset + width].strip().decode("utf-8")
            if not value or set(value) == {"*"}:
                value = None
            elif kind in ("N", "F"):
                value = float(value) if decimal else int(value)
            values[name] = value
        yield values


def polygon_parts(g):
    if g.geom_type == "Polygon" and g.area > 0:
        yield g
    elif hasattr(g, "geoms"):
        for part in g.geoms:
            yield from polygon_parts(part)


def models(path):
    data = path.read_bytes()
    assert struct.unpack_from("<i", data, 32)[0] == 15
    offset = 100
    while offset < len(data):
        fid, size = struct.unpack_from(">ii", data, offset)
        base = offset + 8
        assert struct.unpack_from("<i", data, base)[0] == 15
        n, m = struct.unpack_from("<ii", data, base + 36)
        start = base + 44
        breaks = (*struct.unpack_from(f"<{n}i", data, start), m)
        xy = list(struct.iter_unpack("<2d", data[start + 4 * n:start + 4 * n + 16 * m]))
        z = struct.unpack_from(f"<{m}d", data, start + 4 * n + 16 * m + 16)
        rings = [list(zip(xy[a:b], z[a:b], strict=True)) for a, b in zip(breaks, breaks[1:])]
        yield fid, [[(*xy, z) for xy, z in ring] for ring in rings]
        offset = base + size * 2


def layer(name):
    with sqlite3.connect(PACKAGE / "data" / f"{name}.gpkg") as conn:
        conn.row_factory = sqlite3.Row
        table, geom = conn.execute("SELECT table_name,column_name FROM gpkg_geometry_columns").fetchone()
        return [{k: r[k] for k in r.keys() if k not in (geom, "fid")} for r in conn.execute(f'SELECT * FROM "{table}"')]


def write_layer(path, features, kind, name=None):
    cmd = ["ogr2ogr", "-f", "ESRI Shapefile" if path.suffix == ".shp" else "GPKG",
           str(path), "/vsistdin/", "-a_srs", "EPSG:6677", "-nlt", kind]
    if name:
        cmd += ["-nln", name, "-lco", "FID=record_id", "-dsco", "VERSION=1.2"]
    if path.suffix == ".shp":
        cmd += ["-lco", "ENCODING=UTF-8", "-lco", "RESIZE=YES"]
    subprocess.run(cmd, input=json.dumps({"type": "FeatureCollection", "features": features},
                                         ensure_ascii=False).encode(), check=True)


def feature(attrs, geometry):
    return {"type": "Feature", "properties": attrs, "geometry": geometry}


def surface_kind(ring, low):
    xyz = np.asarray(ring)
    centered = xyz - xyz[0]
    normal = np.cross(centered[:-1], centered[1:]).sum(axis=0)
    norm = np.linalg.norm(normal)
    if norm < 1e-9:
        return "Other"
    if abs(normal[2]) / norm < .3:
        return "Wall"
    if max(xyz[:, 2]) <= low + .35:
        return "Base"
    return "Roof"


def short_names(names):
    used = set()
    result = {}
    for name in names:
        slug = re.sub("[^a-zA-Z0-9_]", "_", name)
        alias = slug[:10]
        i = 1
        while alias.lower() in used:
            end = str(i)
            alias = slug[:10 - len(end)] + end
            i += 1
        used.add(alias.lower())
        result[name] = alias
    return result


def main(source, stage):
    stage.mkdir(parents=True, exist_ok=True)
    web = json.loads((ROOT / "website/study-atlas/building_age_current.geojson").read_text())
    current = {f["properties"]["gml_id"]: f["properties"] for f in web["features"]
               if f["properties"]["in_primary"] == 1}
    assert len(current) == 277
    tables = {}
    for tag, (name, key) in THEMES.items():
        rows = layer(name)
        counts = Counter(r[key] for r in rows)
        tables[tag] = (key, {r[key]: r for r in rows if r[key] and counts[r[key]] == 1},
                       list(rows[0]))
    attrs, surfaces = [], []
    matches = Counter()
    raw_names = ()
    for (fid, rings), raw in zip(models(source), dbf_rows(source.with_suffix(".dbf")), strict=True):
        raw_names = tuple(raw)
        row = raw.copy()
        # Source year 0 is an explicit unknown only in the Shapefile.
        row["Byear"] = raw["Byear"]
        p = current[row["id"]]
        assert row["Byear"] == p["age_year_exact"], fid
        row.update({k: v for k, v in p.items() if k not in row})
        for t, (key, records, names) in tables.items():
            matched = records.get(p.get(key))
            matches[t] += matched is not None
            row.update({f"{t}_{k}": matched.get(k) if matched else None for k in names})
        xy = [Polygon([(x, y) for x, y, z in ring]) for ring in rings]
        parts = [q for g in xy for q in polygon_parts(g if g.is_valid else make_valid(g))]
        g = union_all(parts)
        assert g.area > 0 and g.is_valid and not g.has_z
        attrs.append(feature(row, mapping(g)))
        low = min(z for ring in rings for x, y, z in ring)
        for index, ring in enumerate(rings, 1):
            surfaces.append(feature({"bldg_id": row["id"], "part_id": index,
                                     "surface": surface_kind(ring, low)},
                                    {"type": "Polygon", "coordinates": [ring]}))
    assert len(attrs) == 277 and len({x["properties"]["id"] for x in attrs}) == 277
    assert sum(f["properties"]["Byear"] is not None for f in attrs) == 221
    write_layer(stage / "Primary_Buildings_Full.gpkg", attrs, "MULTIPOLYGON", "primary_buildings")
    write_layer(stage / "Primary_Building_Surfaces.gpkg", surfaces, "POLYGONZ", "building_surfaces")
    fields = list(dict.fromkeys(k for f in attrs for k in f["properties"]))
    for f in attrs:
        for k in fields:
            f["properties"].setdefault(k, None)
    widths = {}
    for name in fields:
        values = [f["properties"][name] for f in attrs if f["properties"][name] is not None]
        if any(isinstance(v, (list, dict, str)) for v in values):
            widths[name] = max((len(str(v).encode()) for v in values), default=1)
        else:
            widths[name] = 24 if any(isinstance(v, float) for v in values) else 11
    # Keep the original fields and prefer current measures, then the rest of
    # the current building register. The full GeoPackage retains every source column.
    ordered = list(dict.fromkeys([*raw_names, *PREFERRED, *EXTRA_PRIORITY, *next(iter(current.values())), *fields]))
    included = []
    budget = 1
    for n in ordered:
        if n not in widths or widths[n] > 254 or len(included) == 255:
            continue
        width = max(1, widths[n])
        if budget + width <= 3940:
            included.append(n)
            budget += width
    assert set(PREFERRED) <= set(included) | {k for k in PREFERRED if widths.get(k, 0) > 254}
    aliases = short_names(included)
    shp = stage / "Buildings_Kajicho_BYear0.shp"
    plain = [feature({aliases[k]: (f["properties"][k] or 0) if k == "Byear"
                     else f["properties"][k] for k in included}, f["geometry"]) for f in attrs]
    write_layer(shp, plain, "MULTIPOLYGON")
    dbf = shp.with_suffix(".dbf").read_bytes()
    _, record_bytes = struct.unpack_from("<HH", dbf, 8)
    assert record_bytes <= 4000, record_bytes
    with (stage / "Building_Fields.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["full_field", "shapefile_field", "source"])
        for k in fields:
            origin = next((t for t in THEMES if k.startswith(t + "_")), "current register")
            writer.writerow([k, aliases.get(k, ""), "supplied age" if k in raw_names else origin])
    receipt = dict(records=len(attrs), recorded_years=221, unknown_years=56, epsg=6677,
                   data_source="Published Primary age PolygonZ, 24 November 2026 projection",
                   full_fields=len(fields), shp_fields=len(included), dbf_record_bytes=record_bytes,
                   theme_unique_key_matches=matches,
                   surface_counts=Counter(f["properties"]["surface"] for f in surfaces))
    (stage / "README.metadata.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
