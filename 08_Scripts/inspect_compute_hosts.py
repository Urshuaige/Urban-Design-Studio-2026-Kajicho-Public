#!/usr/bin/env python3
"""Read live CPU/GPU capacity; recommend placement without launching or stopping jobs."""
import argparse,concurrent.futures,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path

REMOTE=r'''python3 - <<'PY'
import os,json,time,subprocess,shutil
def cpu():
 x=list(map(int,open('/proc/stat').readline().split()[1:9]));return sum(x),x[3]+x[4]
a=cpu();time.sleep(1);b=cpu();idle=(b[1]-a[1])/max(1,b[0]-a[0])
mem={line.split(':')[0]:int(line.split()[1]) for line in open('/proc/meminfo') if line.startswith(('MemTotal:','MemAvailable:'))}
d={'hostname':os.uname().nodename,'logical_cpus':os.cpu_count(),'load_1_5_15':os.getloadavg(),'cpu_idle_fraction':idle,'unused_core_equivalent':round(idle*os.cpu_count(),1),'memory_gib':{k:round(v/1048576,1) for k,v in mem.items()},'gpu':[]}
if shutil.which('nvidia-smi'):
 p=subprocess.run(['nvidia-smi','--query-gpu=index,uuid,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=10)
 for line in p.stdout.strip().splitlines():
  v=[x.strip() for x in line.split(',')]
  if len(v)==6:
   d['gpu'].append({'index':v[0],'uuid':v[1],'name':v[2],'total_memory_mib':v[3],'free_memory_mib':v[4],'utilization_pct':v[5]})
 p=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_memory','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=10)
 d['gpu_processes']=p.stdout.strip().splitlines()
d['scheduler_commands']=[x for x in ['squeue','qstat'] if shutil.which(x)]
print(json.dumps(d))
PY'''
def inspect(host):
 try:
  p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10',host,REMOTE],capture_output=True,text=True,timeout=35)
  if p.returncode:return {'alias':host,'reachable':False,'reason':p.stderr.strip()[-200:]}
  d=json.loads(p.stdout.strip().splitlines()[-1]);d.update(alias=host,reachable=True);return d
 except Exception as e:return {'alias':host,'reachable':False,'reason':str(e)}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hosts',nargs='+',required=True,help='Your SSH host aliases');p.add_argument('--output',type=Path);a=p.parse_args()
 with concurrent.futures.ThreadPoolExecutor(max_workers=min(8,len(a.hosts))) as pool:rows=list(pool.map(inspect,a.hosts))
 live=[x for x in rows if x['reachable']];cpu=max(live,key=lambda x:(x['cpu_idle_fraction'],-x['load_1_5_15'][0]/x['logical_cpus']))['alias'] if live else None
 gpus=[]
 for h in live:
  for g in h['gpu']:
   try:
    occupied=any(line.startswith(g['uuid']+',') for line in h.get('gpu_processes',[]))
    if not occupied and float(g['utilization_pct'])<=5:gpus.append((float(g['free_memory_mib']),h['alias'],g['index']))
   except ValueError:pass
 best=max(gpus) if gpus else None
 d={'snapshot_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'hosts':rows,'capacity_hint':{'cpu':cpu,'gpu':{'host':best[1],'index':best[2]} if best else None},'selection_note':'Capacity hints only: check job memory, GPU compatibility, running processes and scheduler allocation. Explicit user placement overrides these hints.'}
 s=json.dumps(d,indent=2);print(s)
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(s+'\n')
if __name__=='__main__':main()
