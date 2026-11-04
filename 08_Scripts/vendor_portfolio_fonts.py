#!/usr/bin/env python3
"""Vendor Google Fonts subsets used by the Site, with CSS Composite Font ranges.
No page text is sent to the font service: only family names and weights are requested.
"""
from pathlib import Path
import re,json,urllib.request,concurrent.futures,hashlib
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist'
OUT=SITE/'fonts';OUT.mkdir(exist_ok=True)
texts=[]
for p in SITE.rglob('*'):
 if p.suffix in {'.html','.js','.json'} and 'vendor' not in p.parts:
  texts.append(p.read_text(errors='ignore'))
texts.extend(p.read_text(errors='ignore') for p in (ROOT/'06_Outputs/Portfolio_2026-10-15/research').glob('*.json'))
chars={ord(c) for c in ''.join(texts)}
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
def get(url):
 return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=40).read()
def match_ranges(s):
 for start,end in re.findall(r'U\+([0-9A-Fa-f]+)(?:-([0-9A-Fa-f]+))?',s):
  lo=int(start,16);hi=int(end,16) if end else lo
  if any(lo<=c<=hi for c in chars):return True
 return False
families=[('Noto Serif SC','Studio Serif ZH','400;600','notoserifsc'),('Noto Serif JP','Studio Serif JA','400;600','notoserifjp'),('Noto Sans SC','Studio UI ZH','400;600','notosanssc'),('Noto Sans JP','Studio UI JA','400;600','notosansjp'),('Libre Caslon Display','Studio Display Latin','400','librecaslondisplay'),('Source Serif 4','Studio Body Latin','400;600','sourceserif4'),('IBM Plex Sans','Studio UI Latin','400;600','ibmplexsans'),('IBM Plex Mono','Studio Mono','400','ibmplexmono')]
css=[];assets={};records=[]
for name,alias,weights,slug in families:
 url='https://fonts.googleapis.com/css2?family='+name.replace(' ','+')+':wght@'+weights+'&display=swap'
 response=get(url).decode();kept=0
 for block in re.findall(r'@font-face\s*\{[^}]+\}',response):
  rng=re.search(r'unicode-range:\s*([^;]+)',block)
  if rng and not match_ranges(rng[1]):continue
  if 'Latin' in alias or alias=='Studio Mono':
   if rng and not any(int(v,16)<0x250 for v in re.findall(r'U\+([0-9a-fA-F]+)',rng[1])):continue
  block=re.sub(r'font-family:\s*[^;]+;',"font-family: '"+alias+"';",block)
  for remote in re.findall(r'url\((https[^)]+)\)',block):
   fn=hashlib.sha256(remote.encode()).hexdigest()[:20]+'.woff2'
   assets[remote]=fn;block=block.replace(remote,'./fonts/'+fn)
  css.append(block);kept+=1
 license_url='https://raw.githubusercontent.com/google/fonts/main/ofl/'+slug+'/OFL.txt'
 (OUT/(slug+'-OFL.txt')).write_bytes(get(license_url))
 records.append({'family':name,'alias':alias,'weights':weights,'css_source':url,'license':license_url,'subsets':kept})
def dl(item):
 url,fn=item;p=OUT/fn
 if not p.exists():p.write_bytes(get(url))
 return p.stat().st_size
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:sizes=list(pool.map(dl,assets.items()))
# Explicit same-weight rules: Latin and digit overrides come after the CJK subsets.
for alias,latin in [('Studio Serif ZH','Studio Body Latin'),('Studio Serif JA','Studio Body Latin'),('Studio UI ZH','Studio UI Latin'),('Studio UI JA','Studio UI Latin')]:
 for block in list(css):
  if "font-family: '"+latin+"'" in block:
   b=block.replace("'"+latin+"'","'"+alias+"'")
   b=re.sub(r'unicode-range:\s*[^;]+;','unicode-range: U+0000-024F, U+1E00-1EFF;',b)
   b=b.replace('font-display: swap;','font-display: swap; size-adjust: 103%;' if 'Serif' in alias else 'font-display: swap; size-adjust: 98%;')
   css.append(b)
# Display uses the same CJK shape, with Caslon for Western letters.
for language in ['ZH','JA']:
 for block in list(css):
  if "font-family: 'Studio Serif "+language+"'" in block and 'size-adjust' not in block:
   css.append(block.replace('Studio Serif '+language,'Studio Display '+language))
 for block in list(css):
  if "font-family: 'Studio Display Latin'" in block:
   b=block.replace('Studio Display Latin','Studio Display '+language)
   b=re.sub(r'unicode-range:\s*[^;]+;','unicode-range: U+0000-024F, U+1E00-1EFF;',b)
   b=b.replace('font-display: swap;','font-display: swap; size-adjust: 108%;')
   css.append(b)
css.append('''
:root{--font-display:'Studio Display ZH','Noto Serif SC',serif;--font-body:'Studio Serif ZH','Noto Serif SC',serif;--font-ui:'Studio UI ZH','Noto Sans SC',system-ui,sans-serif;--font-code:'Studio Mono',ui-monospace,SFMono-Regular,Consolas,monospace;--type-display:clamp(48px,6vw,90px);--type-title:clamp(32px,3.4vw,52px);--type-heading:24px;--type-body:16px;--type-label:13px;--type-caption:12px}
:root:lang(ja){--font-display:'Studio Display JA','Noto Serif JP',serif;--font-body:'Studio Serif JA','Noto Serif JP',serif;--font-ui:'Studio UI JA','Noto Sans JP',system-ui,sans-serif}
:lang(ja){line-break:strict}code,pre,kbd,samp{font-family:var(--font-code);font-variant-ligatures:none}body{font-synthesis-style:none}h1,h2,h3,h4,p{overflow-wrap:break-word}
''')
(SITE/'typography.css').write_text('/* CSS Composite Font: unicode-range + size-adjust. Source: https://charlie5188.github.io/css-composite-font/ */\n'+'\n'.join(css))
(OUT/'manifest.json').write_text(json.dumps({'retrieved_on':'2026-10-15','method':'Self-hosted subsets; CJK selected by lang, Latin overridden by unicode-range. Fixed line-height in styles. Zero baseline offset. Page content not transmitted.','families':records,'files':len(sizes),'bytes':sum(sizes),'reference':'https://charlie5188.github.io/css-composite-font/'},indent=2))
print(json.dumps({'files':len(sizes),'bytes':sum(sizes),'characters_in_source':len(chars)}))
