#!/usr/bin/env python3
"""Export the existing CFD geometry to WGS84 for the web locator maps.

Run with QGIS Python, which includes pyproj. No solver inputs are modified.
"""
import json
import math
from pathlib import Path

from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dist/data"
context = json.loads((DATA / "cfd-context.json").read_text())
domain = json.loads((DATA / "cfd-results.json").read_text())["domain"]
origin = domain["origin_epsg6677"]
project = Transformer.from_crs("EPSG:6677", "EPSG:4326", always_xy=True)


def coordinates(values):
    if isinstance(values[0], (int, float)):
        lon, lat = project.transform(values[0] + origin[0], values[1] + origin[1])
        return [round(lon, 7), round(lat, 7)]
    return [coordinates(v) for v in values]


def geometry(g):
    return {"type": g["type"], "coordinates": coordinates(g["coordinates"])}


def rectangle(bounds):
    x0, y0, x1, y1 = bounds[:4]
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    ring = []
    # Sample projected edges so a projected rectangle stays correctly located.
    for a, b in zip(corners, corners[1:]):
        n = max(1, math.ceil(math.dist(a, b) / 200))
        ring.extend([[a[0] + (b[0] - a[0]) * i / n,
                      a[1] + (b[1] - a[1]) * i / n] for i in range(n)])
    ring.append(ring[0])
    return geometry({"type": "Polygon", "coordinates": [ring]})


features = [
    {"type": "Feature", "properties": {"role": "design_area", "name": "Kajicho 1–2",
     "boundary_status": "current working boundary; course boundary pending confirmation"},
     "geometry": geometry(context["boundary"])},
    {"type": "Feature", "properties": {"role": "model_extent", "name": "Building envelope",
     "meaning": "bounding rectangle of retained building geometry, not an administrative boundary"},
     "geometry": rectangle(domain["built_bounds_m"])},
    {"type": "Feature", "properties": {"role": "domain", "name": "CFD domain",
     "size_m": [domain["domain_m"][2] - domain["domain_m"][0],
                domain["domain_m"][3] - domain["domain_m"][1], domain["domain_m"][4]]},
     "geometry": rectangle(domain["domain_m"])},
]
for b in context["buildings"]:
    features.append({"type": "Feature", "properties": {
        "role": "building", "id": b["id"], "core": b["core"], "height_m": b["h"]},
        "geometry": geometry(b["geometry"])})

x0, y0, x1, y1, _ = domain["domain_m"]
for role, y in [("inlet", y0), ("outlet", y1)]:
    features.append({"type": "Feature", "properties": {"role": role},
                     "geometry": geometry({"type": "LineString", "coordinates": [[x0, y], [x1, y]]})})

output = {"type": "FeatureCollection", "metadata": {
    "crs": "EPSG:4326 / GeoJSON longitude, latitude",
    "source_crs": "EPSG:6677 / JGD2011 Japan Plane Rectangular CS IX",
    "local_origin_m": origin, "source_files": ["cfd-context.json", "cfd-results.json"],
    "geometry_source": "PLATEAU Chiyoda 2025; existing retained CFD building footprints",
    "source_url": "https://www.geospatial.jp/ckan/dataset/plateau-13101-chiyoda-ku-2025",
    "data_year": 2025, "derived_date": "2026-10-14",
    "processing": "Add local origin, transform EPSG:6677 to EPSG:4326, round to 7 decimals. Domain and envelope edges sampled at <=200 m.",
    "basemap": {"provider": "OpenStreetMap", "tile_url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                "attribution": "© OpenStreetMap contributors", "license_url": "https://www.openstreetmap.org/copyright",
                "policy_url": "https://operations.osmfoundation.org/policies/tiles/",
                "access": "Live viewport tiles only; browser cache; no offline tile archive."},
}, "features": features}
path = DATA / "domain-map.geojson"
path.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
print(json.dumps({"output": str(path), "features": len(features), "buildings": len(context["buildings"]),
                  "origin_lonlat": coordinates([0, 0])}))
