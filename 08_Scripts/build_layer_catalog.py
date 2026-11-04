#!/usr/bin/env python3
"""Build shared layer/field catalogs by reading GeoPackages without changing them."""
import argparse
import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def catalog(root):
    layers, fields = [], []
    for path in sorted((root / "04_Data/Ready").rglob("*.gpkg")):
        if path.name.startswith("._"):
            continue
        rel = path.relative_to(root).as_posix()
        with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
            geometry = {row[0]: row[1:] for row in db.execute(
                "SELECT table_name,column_name,geometry_type_name,srs_id FROM gpkg_geometry_columns")}
            for table, kind, srs in db.execute(
                    "SELECT table_name,data_type,srs_id FROM gpkg_contents ORDER BY table_name"):
                quoted = '"' + table.replace('"', '""') + '"'
                count = db.execute("SELECT count(*) FROM " + quoted).fetchone()[0]
                columns = db.execute("PRAGMA table_info(" + quoted + ")").fetchall()
                geom = geometry.get(table, ("", "", srs))
                layers.append({"dataset_path": rel, "layer": table, "data_type": kind,
                               "geometry_column": geom[0], "geometry_type": geom[1],
                               "crs": "EPSG:" + str(srs), "records": count,
                               "id_fields": ";".join(c[1] for c in columns
                                                    if c[1] in {"building_id", "plateau_building_id", "gml_id", "id"})})
                for _, name, dtype, required, default, primary in columns:
                    fields.append({"dataset_path": rel, "layer": table, "field": name,
                                   "sqlite_type": dtype.upper(), "not_null": required,
                                   "primary_key": primary,
                                   "is_geometry": int(name == geom[0]),
                                   "default_value": default if default is not None else ""})
    return layers, fields


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-directory", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output_directory or root / "04_Data/Metadata"
    layers, fields = catalog(root)
    if not layers:
        raise SystemExit("No GeoPackage layers found under 04_Data/Ready")
    write_csv(output / "Layer_Catalog.csv", layers)
    write_csv(output / "Layer_Fields.csv", fields)
    print(json.dumps({"layers": len(layers), "fields": len(fields),
                      "output_directory": str(output)}))


if __name__ == "__main__":
    main()
