#!/usr/bin/env python3
"""Extract the two wards' published tables and create a separate calculation demo."""
import csv
import json
import re
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'04_Data/Ready/Carbon'
OUT.mkdir(parents=True,exist_ok=True)
SOURCE_URL='https://all62.jp/wp-content/uploads/2026/08/houdou_20260528_01.pdf'
YEARS=[1990,1995,2000]+list(range(2005,2024))+[2023]
SECTORS={'産業部門':'Industry','家庭':'Household','業務':'Business','運輸部門':'Transport','廃棄物部門':'Waste','合計':'Total'}


def save(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)


reader=PdfReader(ROOT/'04_Data/Raw/Carbon/All62_Special_Wards_1990-2023_2026-08.pdf')
records,ghg,checks=[],[],[]
for page,code,ward in [(12,'13101','千代田区'),(13,'13102','中央区')]:
    text=reader.pages[page-1].extract_text()
    sector_text=text.split('部門 1990',1)[1]
    totals=None
    for jp,en in SECTORS.items():
        line=re.search(r'^'+re.escape(jp)+r'\s+([^\n]+)',sector_text,re.M)[1]
        nums=[int(n.replace(',','')) for n in re.findall(r'\d[\d,]*',line)]
        assert len(nums)==len(YEARS),(ward,jp,len(nums),len(YEARS))
        if en=='Total':totals=nums
        for i,(year,value) in enumerate(zip(YEARS,nums)):
            method='unadjusted_reference' if i==len(YEARS)-1 else 'non_fossil_adjusted_basis' if year==2023 else 'unadjusted_historical'
            records.append(dict(ward_code=code,ward_name=ward,fiscal_year=year,sector=en,
                co2_kt=value,co2_t=value*1000,electricity_factor_basis=method,
                evidence_type='published_estimate',source_page=page,source_url=SOURCE_URL))
    top=text.split('部門 1990',1)[0]
    ghg_nums=[int(n.replace(',','')) for n in re.findall(r'\d[\d,]*',re.search(r'^合計\s+([^\n]+)',top,re.M)[1])][1:]
    co2_nums=[int(n.replace(',','')) for n in re.findall(r'\d[\d,]*',re.search(r'（CO2）\s+([^\n]+)',top)[1])][1:]
    assert co2_nums==totals,(ward,'CO2 differs between tables')
    assert len(ghg_nums)==len(YEARS)
    for i,(year,value) in enumerate(zip(YEARS,ghg_nums)):
        method='unadjusted_reference' if i==len(YEARS)-1 else 'non_fossil_adjusted_basis' if year==2023 else 'unadjusted_historical'
        ghg.append(dict(ward_code=code,ward_name=ward,fiscal_year=year,ghg_kt_co2eq=value,
            electricity_factor_basis=method,evidence_type='published_estimate',source_page=page,source_url=SOURCE_URL))
        rows=[r for r in records if r['ward_code']==code and r['fiscal_year']==year and r['electricity_factor_basis']==method]
        difference=sum(r['co2_kt'] for r in rows if r['sector']!='Total')-next(r['co2_kt'] for r in rows if r['sector']=='Total')
        assert abs(difference)<=3,(ward,year,difference)
        checks.append(dict(ward_code=code,fiscal_year=year,electricity_factor_basis=method,sector_sum_minus_total_kt=difference))

save('Ward_CO2_By_Sector_1990-2023.csv',records)
save('Ward_GHG_Total_1990-2023.csv',ghg)
save('Carbon_Table_Checks.csv',checks)
latest=[r for r in records if r['fiscal_year']==2023 and r['electricity_factor_basis']=='non_fossil_adjusted_basis']
save('Ward_CO2_2023_Published.csv',latest)
factors=[]
for year,adjusted,unadjusted in [(2021,.451,.457),(2022,.376,.457),(2023,.408,.475),(2024,.421,.485)]:
    for kind,value in [('adjusted',adjusted),('unadjusted',unadjusted)]:
        factors.append(dict(supplier='TEPCO Energy Partner',fiscal_year=year,factor_type=kind,
            kg_co2_per_kwh=value,scope='Purchased electricity; supplier and menu must match actual contract',
            source_url='https://www.tepco.co.jp/about/esg/environment/carbon-neutrality/ghg-data-j.html',
            retrieved_on='2026-10-13'))
save('TEPCO_Electricity_Factors_2021-2024.csv',factors)
demo=[]
for name,efficiency,pv in [('Base',0,0),('Efficiency',.2,0),('Efficiency_PV',.2,20000)]:
    load=100000*(1-efficiency);purchased=max(0,load-pv)
    demo.append(dict(example_id='FICTIONAL_BUILDING_01',scenario=name,evidence_type='illustrative_assumptions',
        baseline_kwh_per_year=100000,efficiency_reduction_fraction=efficiency,
        onsite_pv_self_consumed_kwh_per_year=pv,purchased_kwh_per_year=purchased,
        factor_kg_co2_per_kwh=.421,operational_electricity_co2_t_per_year=round(purchased*.421/1000,3),
        formula='purchased_kwh * factor_kg_co2_per_kwh / 1000',factor_year=2024,
        scope='Electricity only; excludes fuel, transport, embodied emissions and export credits'))
save('DEMO_Illustrative_Building_Electricity.csv',demo)
with (OUT/'Building_Energy_Input_Template.csv').open('w',encoding='utf-8-sig',newline='') as f:
    csv.writer(f).writerow(['building_id','period_start','period_end','metered_kwh','supplier','tariff_menu',
        'electricity_factor_kg_co2_kwh','factor_year','factor_type','gas_m3','gas_factor_kg_co2_m3',
        'floor_area_m2','use_type','data_status','source','privacy_and_share_scope'])
summary=dict(co2_rows=len(records),ghg_rows=len(ghg),published_latest=latest,
    max_rounding_difference_kt=max(abs(r['sector_sum_minus_total_kt']) for r in checks),
    interpretation='2023 published values use a changed electricity-factor basis; reference rows preserve the old basis. Ward estimates remain ward-level.',
    demo=demo)
(ROOT/'03_Theme_B/Common_Foundation/Sources/carbon_extraction_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps({'co2_rows':len(records),'ghg_rows':len(ghg),'max_rounding_difference_kt':summary['max_rounding_difference_kt'],'latest_total':[(r['ward_name'],r['co2_kt']) for r in latest if r['sector']=='Total']},ensure_ascii=False))
