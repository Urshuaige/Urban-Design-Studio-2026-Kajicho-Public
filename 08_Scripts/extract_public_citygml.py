#!/usr/bin/env python3
"""Stream CityGML; preserve codes, source IDs and horizontal JGD2011 geometry.
EPSG:6697 posList axis order is latitude, longitude, orthometric height.
Only LOD1 surfaces for thematic layers; no building surface union is redone.
"""
from pathlib import Path
import xml.etree.ElementTree as ET,json,collections,sys
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'04_Data/Raw/Public_Baseline_2026-10-14/PLATEAU';OUT=ROOT/'04_Data/Ready/Public_Baseline_2026-10-14';OUT.mkdir(exist_ok=True,parents=True)
GML='{http://www.opengis.net/gml}';CORE='{http://www.opengis.net/citygml/2.0}'
BBOX=(139.767,35.687,139.776,35.695)
ids={f['properties']['id'] for f in json.loads((ROOT/'04_Data/Ready/Simulation_Demo/plateau_buildings_6677.geojson').read_text())['features']}
code_dir=next(p for p in RAW.rglob('codelists') if p.is_dir() and p.parent.name.endswith('_codelists'))
codes={}
for p in code_dir.glob('*.xml'):
 if p.name.startswith('._'):continue
 try:
  rt=ET.parse(p).getroot();codes[p.name]={d.findtext(GML+'name'):d.findtext(GML+'description') for d in rt.iter(GML+'Definition')}
 except ET.ParseError:continue

def attributes(b):
 out={};units={}
 for e in b.iter():
  n=e.tag.split('}')[-1]
  if len(e) or not e.text or n in ['posList','pos','textureCoordinates','imageURI','lowerCorner','upperCorner']:continue
  s=e.text.strip()
  if not s:continue
  if n=='value':continue
  out.setdefault(n,[])
  if s not in out[n]:out[n].append(s)
  if 'codeSpace' in e.attrib:
   value=codes.get(Path(e.attrib['codeSpace']).name,{}).get(s)
   if value:out.setdefault(n+'_label',[]).append(value)
  if 'uom' in e.attrib:units[n]=e.attrib['uom']
 for e in b.iter():
  if e.tag.split('}')[-1] in ['stringAttribute','intAttribute','doubleAttribute']:
   out['generic_'+e.get('name','')]=[v.text for v in e if v.text]
 out={k:v[0] if len(v)==1 else v for k,v in out.items()}
 out['units']=units
 return out

def geom(b):
 polys=[]
 # geometry only from LOD1, except URF uses lod1MultiSurface as expected.
 parents=[e for e in b.iter() if e.tag.split('}')[-1] in ['lod1MultiSurface','lod1Surface','lod1Geometry']]
 for parent in parents:
  for p in parent.iter(GML+'Polygon'):
   rings=[]
   for kind in ['exterior','interior']:
    for ring in p.findall(GML+kind):
     pos=ring.find('.//'+GML+'posList')
     if pos is None or not pos.text:continue
     a=list(map(float,pos.text.split()));assert len(a)%3==0
     pts=[[a[i+1],a[i]] for i in range(0,len(a),3)]
     if pts and pts[-1]!=pts[0]:pts.append(pts[0])
     rings.append(pts)
   if rings:polys.append(rings)
 if not polys:return None
 coords=[xy for p in polys for r in p for xy in r]
 if max(x[0] for x in coords)<BBOX[0] or min(x[0] for x in coords)>BBOX[2] or max(x[1] for x in coords)<BBOX[1] or min(x[1] for x in coords)>BBOX[3]:return None
 return {'type':'MultiPolygon','coordinates':polys}

def members(path):
 it=ET.iterparse(path,events=('start','end'));_,root=next(it)
 for ev,e in it:
  if ev=='end' and e.tag==CORE+'cityObjectMember':
   yield e[0]
   e.clear();root.clear()

buildings={};duplicates=[]
for p in ([] if '--flood-only' in sys.argv else RAW.rglob('*bldg*.gml')):
 if p.name.startswith('._'):continue
 n=0
 for b in members(p):
  id=b.get(GML+'id')
  if id not in ids:continue
  a=attributes(b);a.update({'id':id,'source_file':str(p.relative_to(ROOT)),'object_type':b.tag.split('}')[-1]})
  if id in buildings:duplicates.append(id)
  buildings[id]=a;n+=1
 print(p.name,'matched',n,flush=True)
if '--flood-only' not in sys.argv:(OUT/'CityGML_Building_Attributes.json').write_text(json.dumps(buildings,ensure_ascii=False,indent=2))
audit={'source_ids':len(ids),'matched_ids':len(buildings),'missing_ids':sorted(ids-set(buildings)),'duplicate_ids':duplicates,'bbox':BBOX,'layers':{}}
if '--flood-only' in sys.argv:audit=json.loads((OUT/'CityGML_Extraction_Quality.json').read_text())
for typ in (['fld'] if '--flood-only' in sys.argv else ['urf','luse','tran','fld']):
 features=[];seen=set();total=0
 paths=[p for p in RAW.rglob('*.gml') if not p.name.startswith('._') and (('_'+typ+'_') in p.name)]
 for p in paths:
  n=0
  for b in members(p):
   total+=1;g=geom(b)
   if not g:continue
   id=b.get(GML+'id');key=(str(p.parent.relative_to(RAW)),id)
   if key in seen:continue
   seen.add(key);a=attributes(b);a.update({'gml_id':id,'object_type':b.tag.split('}')[-1],'source_file':str(p.relative_to(ROOT))})
   features.append({'type':'Feature','properties':{k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in a.items()},'geometry':g});n+=1
  print(typ,p.name,'bbox',n,flush=True)
 out={'type':'FeatureCollection','crs':{'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::6668'}},'features':features}
 (OUT/('CityGML_'+typ+'_source_extent.geojson')).write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
 audit['layers'][typ]={'files':len(paths),'scanned_objects':total,'bbox_selected_objects':len(features)}
(OUT/'CityGML_Extraction_Quality.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));print(json.dumps(audit,ensure_ascii=False)[:1500])
