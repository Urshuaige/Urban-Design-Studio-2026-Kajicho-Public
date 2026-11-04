#!/usr/bin/env python3
"""Normalize the saved JMA CSV without imputation; preserve quality/homogeneity."""
import csv,json,math,statistics
from pathlib import Path
from datetime import datetime,timedelta,timezone
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'04_Data/Raw/Public_Baseline_2026-10-14/JMA'
OUT=ROOT/'04_Data/Ready/Public_Baseline_2026-10-14';OUT.mkdir(parents=True,exist_ok=True)
rows=list(csv.reader((RAW/'Tokyo_2025_hourly_original.csv').read_text(encoding='cp932').splitlines()))
assert rows[3][1]=='気温(℃)' and rows[4][10]=='風向'
# Map positions only after asserting the official multi-row header.
cols=['timestamp_jst','temperature_c','temperature_qc','temperature_homogeneity','rain_mm','rain_no_event','rain_qc','rain_homogeneity','wind_ms','wind_qc','wind_from_ja','wind_direction_qc','wind_homogeneity','rh_pct','rh_qc','rh_homogeneity','solar_mj_m2','solar_qc','solar_homogeneity','sunshine_h','sunshine_no_event','sunshine_qc','sunshine_homogeneity','station_pressure_hpa','pressure_qc','pressure_homogeneity']
directions=['北','北北東','北東','東北東','東','東南東','南東','南南東','南','南南西','南西','西南西','西','西北西','北西','北北西']
degrees={d:i*22.5 for i,d in enumerate(directions)}
out=[]
for row in rows[6:]:
 assert len(row)==len(cols)
 r=dict(zip(cols,row));dt=datetime.strptime(row[0],'%Y/%m/%d %H:%M:%S').replace(tzinfo=timezone(timedelta(hours=9)))
 r['timestamp_jst']=dt.isoformat();r['observation_day']=(dt-timedelta(seconds=1)).date().isoformat();r['observation_hour']=dt.hour or 24
 r['station_id']='s47662';r['wind_from_deg']=degrees.get(r['wind_from_ja'],'')
 r['solar_mean_w_m2']=float(r['solar_mj_m2'])*1e6/3600 if r['solar_qc']=='8' and r['solar_mj_m2'] else ''
 r['wind_u_east_ms']=r['wind_v_north_ms']=''
 if r['wind_qc']=='8' and r['wind_direction_qc']=='8' and r['wind_from_deg']!='':
  a=math.radians(r['wind_from_deg']);r['wind_u_east_ms']=-float(r['wind_ms'])*math.sin(a);r['wind_v_north_ms']=-float(r['wind_ms'])*math.cos(a)
 out.append(r)
assert len(out)==8760 and len({r['timestamp_jst'] for r in out})==8760
assert all(datetime.fromisoformat(b['timestamp_jst'])-datetime.fromisoformat(a['timestamp_jst'])==timedelta(hours=1) for a,b in zip(out,out[1:]))
def write(name,rs):
 with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
write('Tokyo_2025_hourly.csv',out)
monthly=[]
for month in range(1,13):
 rs=[r for r in out if int(r['observation_day'][5:7])==month]
 monthly.append({'month':month,'hours':len(rs),'temperature_mean_c':round(statistics.mean(float(r['temperature_c']) for r in rs),3),'hourly_temperature_max_c':max(float(r['temperature_c']) for r in rs),'wind_valid_hours':sum(r['wind_qc']=='8' for r in rs),'wind_mean_ms':round(statistics.mean(float(r['wind_ms']) for r in rs if r['wind_qc']=='8'),3),'rh_mean_pct':round(statistics.mean(float(r['rh_pct']) for r in rs),3),'rain_total_mm':round(sum(float(r['rain_mm']) for r in rs),2),'solar_total_mj_m2':round(sum(float(r['solar_mj_m2']) for r in rs),2)})
write('Tokyo_2025_monthly.csv',monthly)
summer=[r for r in out if r['observation_day'][5:7] in ['06','07','08','09']]
wind_counts=Counter(r['wind_from_ja'] for r in summer if r['wind_direction_qc']=='8')
write('Tokyo_2025_summer_wind.csv',[{'direction_ja':d,'from_deg':degrees.get(d,''),'hours':n,'share_valid':n/sum(wind_counts.values())} for d,n in wind_counts.most_common()])
days=defaultdict(list)
for r in summer:days[r['observation_day']].append(r)
eligible={d:rs for d,rs in days.items() if len(rs)==24 and all(r['wind_qc']=='8' and r['wind_direction_qc']=='8' for r in rs)}
# Descriptive selection with explicit rules, not a typical meteorological year.
hot=max(eligible,key=lambda d:max(float(r['temperature_c']) for r in eligible[d]))
maxes={d:max(float(r['temperature_c']) for r in rs) for d,rs in eligible.items()};med=statistics.median(maxes.values());median=min(eligible,key=lambda d:(abs(maxes[d]-med),d))
scenarios=[]
for label,day in [('summer_peak_hourly_temperature',hot),('summer_median_daily_hourly_max',median)]:
 for r in eligible[day]:scenarios.append({'sample':label,**r})
write('Tokyo_2025_sample_days.csv',scenarios)
audit={'station':'Tokyo s47662','period':'2025-01-01 01:00 to 2026-01-01 00:00 JST','rows':len(out),'unique_hourly_timestamps':len(out),'quality_counts':{c:dict(Counter(r[c] for r in out)) for c in cols if c.endswith('_qc')},'homogeneity_values':{c:sorted({r[c] for r in out}) for c in cols if c.endswith('_homogeneity')},'missing_wind_timestamps':[r['timestamp_jst'] for r in out if r['wind_qc']!='8'],'sample_days':{'hottest_hourly_temperature':hot,'median_daily_hourly_max':median},'no_imputation':True,'notes':['JMA date-literal mode converts 24:00 to next-day 00:00.','The monthly grouping uses the original observation day, hours 1–24.','Solar W/m2 is previous-hour average, converted from MJ/m2.','Wind direction is meteorological from-bearing clockwise from north.','Q8 normal; Q5 quasi-normal; Q4 insufficient; Q2 doubtful; Q1 missing; Q0 not observed.','JMA background station observations are not pedestrian-height local wind.'],'sources':['https://www.data.jma.go.jp/risk/obsdl/index.php','https://www.data.jma.go.jp/risk/obsdl/top/help3.html']}
(OUT/'Weather_Quality.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));print(json.dumps(audit,ensure_ascii=False,indent=2))
