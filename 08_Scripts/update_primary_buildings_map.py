#!/usr/bin/env python3
"""Install the repaired analysis layer and optional face styles in the public map."""
import json
from pathlib import Path
from qgis.core import (
    QgsApplication, QgsCategorizedSymbolRenderer, QgsFillSymbol,
    QgsProject, QgsRendererCategory, QgsVectorLayer, QgsWkbTypes,
)

ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "04_Data/Ready/QGIS_Current_2026-11-04"
PROJECT = DELIVERY / "Kajicho_Current_Data.qgz"
app = QgsApplication([], False)
app.initQgis()
project = QgsProject.instance()
assert project.read(str(PROJECT))
age, = project.mapLayersByName("Primary building age · supplied years")
assert age.isValid() and age.featureCount() == 277 and not QgsWkbTypes.hasZ(age.wkbType())
root = age.renderer().rootRule()
for rule in root.children():
    if 'IS NULL' in rule.filterExpression():
        rule.setFilterExpression('"Byear" = 0 OR "Byear" IS NULL')
        rule.setLabel("Unknown")
    elif rule.filterExpression() == '"Byear" < 1970':
        rule.setFilterExpression('"Byear" > 0 AND "Byear" < 1970')
meta = age.metadata()
meta.setAbstract("One valid 2D model projection per published Primary Area building. "
                 "Use Byear for the supplied construction-year categories. 0 denotes an unknown year. "
                 "The 2D table joins public building attributes by ID. See Building_Fields.csv.")
age.setMetadata(meta)
tree = project.layerTreeRoot()
for duplicate in project.mapLayersByName("Primary buildings · full attributes") + project.mapLayersByName("Building surfaces · visualisation"):
    project.removeMapLayer(duplicate)
group_name = "Primary buildings · full data and 3D appearance"
old_group = tree.findGroup(group_name)
if old_group is not None and not old_group.children():
    tree.removeChildNode(old_group)
info = tree.insertGroup(1, group_name)
info.setExpanded(False)
for filename, table, name, count in [
    ("Primary_Buildings_Full.gpkg", "primary_buildings", "Primary buildings · full attributes", 277),
    ("Primary_Building_Surfaces.gpkg", "building_surfaces", "Building surfaces · visualisation", 6949),
]:
    layer = QgsVectorLayer(f"{DELIVERY / 'data' / filename}|layername={table}", name, "ogr")
    assert layer.isValid() and layer.featureCount() == count and layer.crs() == project.crs()
    if table == "building_surfaces":
        palette = {"Base": "#bbb7b1", "Roof": "#d9a896", "Wall": "#dedbd5", "Other": "#e6e2de"}
        symbols = [
            QgsRendererCategory(k, QgsFillSymbol.createSimple({
                "color": color, "outline_color": "#6f625b", "outline_width": "0.13"}), k)
            for k, color in palette.items()
        ]
        layer.setRenderer(QgsCategorizedSymbolRenderer("surface", symbols))
    project.addMapLayer(layer, False)
    info.addLayer(layer).setItemVisibilityChecked(False)
assert project.write()
project.clear()
assert project.read(str(PROJECT))
invalid = [l.name() for l in project.mapLayers().values() if not l.isValid()]
assert not invalid, invalid
print(json.dumps({"layers": len(project.mapLayers()), "invalid": invalid,
                  "new_layers": 2}, ensure_ascii=False))
app.exitQgis()
