"""Supplement: fixed six existing competition questions, never chosen by scores."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def load(name,p):
 s=importlib.util.spec_from_file_location(name,str(p));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def core(p):return {q.name:sha(q) for q in p.iterdir() if q.suffix in ('.cpp','.hpp','.h') or q.name=='words.txt'}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--sdk',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
 out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);sdk=args.sdk.resolve()
 mainrun=ROOT/'validation/review175-20261004/frozen-v5'
 assert json.loads((mainrun/'final-audit.json').read_text())['runs']==432
 h=load('h',ROOT/'src1.7.5/tests/run_probe_compare.py');runner=load('r',ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py')
 versions=['src1.7.3','src1.7.4','src1.7.5'];exe={};sources={};metadata={}
 for v in versions:
  b=ROOT/'validation/review175-20261004/frozen-v2/build-current' if v=='src1.7.5' else ROOT/'validation/review-20261004/renamed-builds'/v
  m=json.loads((b/'build.json').read_text());sources[v]=core(ROOT/v)
  assert all(m['sources'].get(k)==x for k,x in sources[v].items()) and sha(b/'example')==m['binary_sha256']
  exe[v]=b/'example';metadata[v]=m
 cases=[ROOT/'题目/realcompetiton_2024'/('%02d.xml'%n) for n in (1,9,19,24,31,36)]
 inputs={str(p.relative_to(ROOT)):sha(p) for p in cases}
 tools=[Path(__file__).resolve(),ROOT/'src1.7.5/tests/run_probe_compare.py',ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py',ROOT/'src1.7.5/tests/seed_rng.cpp']
 tooling={str(p.relative_to(ROOT)):sha(p) for p in tools};model=h.sdk_model(sdk)
 save(out/'frozen-audit.json',dict(sources=sources,inputs=inputs,tooling=tooling,sdk=model,builds=metadata,seeds=[2026100401,2026100402],selection='01/09/19/24/31/36 selected before supplement results; existing competition sample, not full-suite reproduction'))
 assets=out/'assets';assets.mkdir();(assets/'words.txt').write_bytes((ROOT/'src1.7.5/words.txt').read_bytes().replace(b'\r\n',b'\n'))
 seedso=out/'seed.so';subprocess.run(['g++','-shared','-fPIC',str(ROOT/'src1.7.5/tests/seed_rng.cpp'),'-ldl','-o',str(seedso)],check=True)
 os.environ.update(LD_PRELOAD=str(seedso),RDFW_STAGE_TIMING='0');os.environ.pop('RDFW_TASK_GROUP_MODE',None);rows=[]
 for si,seed in enumerate((2026100401,2026100402)):
  os.environ['RDFW_TEST_SEED']=str(seed)
  for ci,p in enumerate(cases):
   for mi,mode in enumerate(('it','nt')):
    k=(si+ci+mi)%3;order=versions[k:]+versions[:k]
    for v in order:
     run=out/'runs'/(str(seed)+'-'+p.stem+'-'+mode+'-'+v)
     try:r=runner.run_case(sdk,assets,exe[v],p,2,mode,run,5000,None)
     except Exception as e:r=dict(status='harness_error',error=repr(e),official_score=None,platform_seconds=None)
     r=h.extract(run,r,seed)
     if r.get('official_score') is None or r.get('platform_seconds') is None:r['base']=None;r['action_cost']=None
     rows.append(dict(suite='competition_sample',id=p.stem,stage=2,mode=mode,seed=seed,version=v,order=order,result=r));save(out/'results.json',rows)
    print('COMPETITION',len(rows),'/72',p.stem,mode,seed,[(x['version'],x['result']['base'],x['result']['final_goals']) for x in rows[-3:]],flush=True)
 for v in versions:assert core(ROOT/v)==sources[v];assert sha(exe[v])==metadata[v]['binary_sha256']
 for p,x in inputs.items():assert sha(ROOT/p)==x
 for p,x in tooling.items():assert sha(ROOT/p)==x
 assert h.sdk_model(sdk)==model and len(rows)==72
 save(out/'final-audit.json',dict(sources_unchanged=True,inputs_unchanged=True,tooling_unchanged=True,sdk_unchanged=True,runs=72,seed_unconfirmed=sum(not x['result']['seed_confirmed'] for x in rows)))
if __name__=='__main__':main()
