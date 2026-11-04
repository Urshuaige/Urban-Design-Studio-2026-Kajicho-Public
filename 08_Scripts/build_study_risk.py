#!/usr/bin/env python3
"""Join the saved 2022 Tokyo risk table to full census towns intersecting the study.
Risk values remain the official whole-town values. Intersection fractions describe
only the 2020 census geometry; they never weight risk amounts or ranks.
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import unicodedata

RISK_SOURCE_URL = "https://www.funenka.metro.tokyo.lg.jp/2024/01/all2.csv"
EXPECTED_RISK_SHA256 = "62ad9f4479f43ea254ed89bdfbc289ee9ccf7f18546a3713c29e6d63bbabbfb9"
WARD_NAMES = {"13101": "千代田区", "13102": "中央区"}
FOCUS_CODES = {"13101035001", "13101035002"}
SOURCE_FIELDS = [
    "区市町名", "町丁目名", "地盤分類",
    "建物倒壊危険度危険量（棟/ha）", "建物倒壊危険度順位", "建物倒壊危険度ランク",
    "火災危険度危険量（棟/ha）", "火災危険度順位", "火災危険度ランク",
    "災害時活動困難度困難係数",
    "総合危険度危険量（棟/ha）", "総合危険度順位", "総合危険度ランク",
]
VALUE_FIELDS = {
    "ground_classification": "地盤分類",
    "collapse": "建物倒壊危険度危険量（棟/ha）",
    "collapse_position": "建物倒壊危険度順位",
    "collapse_rank": "建物倒壊危険度ランク",
    "fire": "火災危険度危険量（棟/ha）",
    "fire_position": "火災危険度順位",
    "fire_rank": "火災危険度ランク",
    "response_difficulty": "災害時活動困難度困難係数",
    "overall": "総合危険度危険量（棟/ha）",
    "overall_position": "総合危険度順位",
    "overall_rank": "総合危険度ランク",
}
CROSSWALK = {
    "ward_code": "13101", "town_code": "131010360",
    "census_town_name": "神田鍛冶町",
    "official_town_name": "神田鍛冶町３丁目",
    "evidence": {
        "census_zip_member": "Chiyoda_2020.zip::r2ka13101.shp",
        "source_attributes": {
            "KEY_CODE": "131010360", "S_NAME": "神田鍛冶町",
            "S_AREA": "036003", "KIHON2": "03", "KCODE1": "0360-03",
        },
        "address_source_url": "https://www.city.chiyoda.lg.jp/documents/4227/3001hyoki.pdf",
        "address_source_page": "1, 神田鍛冶町 entry and note 3",
        "address_source_note": "三丁目のみ",
        "name_source_url": "https://www.city.chiyoda.lg.jp/koho/machizukuri/tochi/jukyohyoji/yomikata.html",
        "name_source_updated": "2025-06-20",
        "checked_on": "2026-10-18",
    },
    "rule": "An explicit code/name crosswalk to the only current Kanda-Kajicho chome. No fuzzy prefix matching.",
}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normalized_name(value):
    value = unicodedata.normalize("NFKC", value).strip()
    # Apply numeral conversion only to the chome suffix, leaving town-name text intact.
    for source, target in [("十", "10"), ("九", "9"), ("八", "8"), ("七", "7"),
                           ("六", "6"), ("五", "5"), ("四", "4"), ("三", "3"),
                           ("二", "2"), ("一", "1")]:
        value = value.replace(source + "丁目", target + "丁目")
    return value

def read_risk(path):
    digest = sha256(path)
    if digest != EXPECTED_RISK_SHA256:
        raise ValueError("Risk CSV differs from the saved official 2022 source. Review its year and schema before use.")
    with path.open(encoding="cp932", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != SOURCE_FIELDS:
            raise ValueError("Unexpected official risk CSV schema")
        records = [(number, dict(row)) for number, row in enumerate(reader, 2)]
    index = collections.defaultdict(list)
    for number, row in records:
        index[(row["区市町名"], normalized_name(row["町丁目名"]))].append((number, row))
    return records, index, digest

def build_rows(census_path, risk_index, scope_id="study_area"):
    with census_path.open(encoding="utf-8-sig", newline="") as handle:
        census = [row for row in csv.DictReader(handle) if float(row["scope_overlap_m2"]) > 0 and row["scope"] == scope_id]
    groups = collections.defaultdict(list)
    for row in census:
        groups[(row["ward_code"], row["town_code"])].append(row)
    output = []
    aliases = []
    for (ward_code, town_code), parts in sorted(groups.items()):
        names = {part["town_name"] for part in parts}
        if len(names) != 1:
            raise ValueError("One census town code has different names: " + town_code)
        town_name = next(iter(names))
        ward_name = WARD_NAMES[ward_code]
        risk_name = normalized_name(town_name)
        join_method = "exact_ward_and_normalized_chome_name"
        if (ward_code, town_code, town_name) == (
                CROSSWALK["ward_code"], CROSSWALK["town_code"], CROSSWALK["census_town_name"]):
            risk_name = normalized_name(CROSSWALK["official_town_name"])
            join_method = "explicit_verified_census_code_name_crosswalk"
            aliases.append(CROSSWALK)
        matches = risk_index.get((ward_name, risk_name), [])
        if len(matches) != 1:
            raise ValueError("Unmatched or ambiguous official town: " + ward_name + " / " + town_name)
        source_line, source = matches[0]
        ids = [part["fid"] for part in parts]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate census geometry-part ID: " + town_code)
        overlap = sum(float(part["scope_overlap_m2"]) for part in parts)
        full_area = sum(float(part["full_town_area_m2"]) for part in parts)
        if full_area <= 0 or overlap > full_area + 0.01:
            raise ValueError("Invalid intersection/full-town area: " + town_code)
        fraction = min(1.0, overlap / full_area)
        row = {
            "ward_code": ward_code, "ward_name": ward_name,
            "town_code": town_code, "town_name": town_name,
            "official_town_name": source["町丁目名"],
            "normalized_town_name": normalized_name(source["町丁目名"]),
            "focus": town_code in FOCUS_CODES,
            "geometry_part_count": len(parts), "census_part_ids": ids,
            "scope_overlap_m2": overlap, "full_census_town_area_m2": full_area,
            "town_overlap_fraction": fraction,
            "is_partial_census_unit": overlap < full_area - 0.01,
            "join_method": join_method, "source_csv_row_number": source_line,
            "source_row": source,
        }
        row.update({key: source[field] for key, field in VALUE_FIELDS.items()})
        for field in ["collapse", "fire", "overall", "response_difficulty"]:
            if float(row[field]) < 0:
                raise ValueError("Negative published risk value: " + town_code)
        for field in ["collapse_rank", "fire_rank", "overall_rank"]:
            if int(row[field]) not in range(1, 6):
                raise ValueError("Published rank outside 1-5: " + town_code)
        output.append(row)
    return census, output, aliases

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census-csv", type=Path, required=True)
    parser.add_argument("--risk-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="JSON path; matched-row CSV is written beside it")
    parser.add_argument("--boundary-geojson", type=Path)
    parser.add_argument("--scope", default="study_area")
    args = parser.parse_args()
    source_rows, index, digest = read_risk(args.risk_csv)
    parts, rows, aliases = build_rows(args.census_csv, index, args.scope)
    scope_ids = sorted({row["scope"] for row in parts})
    if len(scope_ids) != 1:
        raise ValueError("Census input must describe one study scope")
    scope = {"id": scope_ids[0]}
    boundary_path = args.boundary_geojson or args.census_csv.parent.parent / "study_boundary_6677.geojson"
    if boundary_path.exists():
        boundary = next(f["properties"] for f in json.loads(boundary_path.read_text())["features"] if f["properties"]["id"] == args.scope)
        scope.update({
            "boundary_geometry_sha256": boundary["geometry_sha256"],
            "boundary_file_sha256": sha256(boundary_path), "area_ha": boundary["area_ha"],
        })
    result = {
        "schema_version": 1, "processing_date": "2026-10-18",
        "source": {
            "document_title": "Tokyo 9th Regional Earthquake Risk Survey",
            "source_url": RISK_SOURCE_URL,
            "source_page": "https://www.funenka.metro.tokyo.lg.jp/area-hazard-level/regional-risk-list/chiyoda/index.html",
            "document_year": 2022, "document_release": "2022-09",
            "website_updated": "2024-03-01 (retained Chiyoda index record)",
            "download_date": "2026-10-15", "staged_remote_on": "2026-10-18",
            "filename": args.risk_csv.name, "sha256": digest,
            "encoding": "CP932", "table_rows": len(source_rows),
            "spatial_unit": "Full official town/chome",
            "license": "Tokyo official public table; source attribution retained; no independent license asserted",
        },
        "scope": scope,
        "census": {
            "filename": args.census_csv.name, "sha256": sha256(args.census_csv),
            "data_year": 2020, "crs": "EPSG:6677",
            "geometry_part_count": len(parts), "town_unit_count": len(rows),
            "area_method": "Sum full_town_area_m2 and scope_overlap_m2 over geometry parts of the same ward_code/town_code.",
            "fraction_scope": "Fraction of the full 2020 census geometry, not a split of the 2022 risk assessment.",
        },
        "join": {
            "status": "all_intersecting_census_towns_matched",
            "normalized_name_matches": len(rows) - len(aliases),
            "explicit_verified_crosswalks": aliases,
            "unmatched_units": [], "ambiguous_units": [],
            "normalization": "Unicode NFKC and Kanji-to-Arabic chome suffix only; exact ward plus name. One documented code/name alias.",
        },
        "interpretation": {
            "amount_units": "buildings/ha, as published for the full official risk unit",
            "rank_scale": [1, 2, 3, 4, 5],
            "risk_weighted_by_overlap": False, "risk_averaged_over_study": False,
            "definition": "Relative comparison of 5,192 Tokyo town units under common engineering-bedrock shaking. Ranks are not annual probabilities or individual-building assessments.",
            "composite": "Published overall risk includes emergency-response difficulty. Rounded components need not exactly reproduce it.",
            "partial_units": "All positive census intersections are retained, including small edge overlaps. Risk amounts and ranks still describe the full official town.",
        },
        "summary": {
            "official_town_units": len(rows), "census_geometry_parts": len(parts),
            "focus_units": sum(row["focus"] for row in rows),
            "partial_census_units": sum(row["is_partial_census_unit"] for row in rows),
        },
        "rows": rows,
    }
    focus = {row["town_code"]: row for row in rows if row["focus"]}
    if set(focus) != FOCUS_CODES or focus["13101035001"]["collapse"] != "4.15" or focus["13101035002"]["collapse"] != "3.81":
        raise ValueError("Kajicho focus rows do not match the preserved official source")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    csv_path = args.output.with_suffix(".csv")
    derived = [
        "ward_code", "ward_name", "town_code", "town_name", "official_town_name",
        "focus", "geometry_part_count", "census_part_ids", "scope_overlap_m2",
        "full_census_town_area_m2", "town_overlap_fraction", "is_partial_census_unit",
        "join_method", "source_csv_row_number", "source_csv_sha256",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=derived + SOURCE_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            out = {key: row[key] for key in derived if key in row}
            out["census_part_ids"] = ";".join(row["census_part_ids"])
            out["source_csv_sha256"] = digest
            out.update(row["source_row"])
            writer.writerow(out)
    print(json.dumps({"json": str(args.output), "csv": str(csv_path), **result["summary"]}))

if __name__ == "__main__":
    main()
