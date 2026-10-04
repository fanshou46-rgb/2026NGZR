"""Serial paired SDK comparison; freeze inputs/sources and retain every run."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, subprocess, sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
VERSIONS=['src1.7.3','src1.7.4','src1.7.5']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,str(p));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def core(p):return {q.name:sha(q) for q in p.iterdir() if q.suffix in ('.cpp','.hpp','.h') or q.name=='words.txt'}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--sdk',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
 parser.add_argument('--reuse-current',type=Path)
 args=parser.parse_args();sdk=args.sdk.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
 helper=load('helper',ROOT/'src1.7.5/tests/run_probe_compare.py');runner=load('runner',ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py')
 groups=[('old',ROOT/'题目/generalization_20261004',5000),('new',ROOT/'题目/generalization_175_20261004_v4',5000)]
 inputs={};catalogues={}
 for label,directory,budget in groups:
  cat=json.loads((directory/'catalogue.json').read_text(encoding='utf8'));catalogues[label]=cat
  inputs[str((directory/'catalogue.json').relative_to(ROOT))]=sha(directory/'catalogue.json')
  for c in cat['cases']:assert sha(directory/c['path'])==c['sha256'];inputs[str((directory/c['path']).relative_to(ROOT))]=c['sha256']
 sources={v:core(ROOT/v) for v in VERSIONS}
 toolpaths=[Path(__file__).resolve(),Path(__file__).resolve().parent/'generate_questions.py',ROOT/'src1.7.5/tests/run_probe_compare.py',ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py',ROOT/'tools/review_175/reference_client.cpp']
 tooling={str(p.relative_to(ROOT)):sha(p) for p in toolpaths};sdk_model=helper.sdk_model(sdk)
 sdk_bins={str(p.relative_to(sdk)):sha(p) for p in [sdk/'bin/cserver',sdk/'lib/libasp.so',sdk/'lib/libframe.a',sdk/'res/iclingo']}
 executables={};metadata={}
 for v in VERSIONS:
  if v!='src1.7.5' or args.reuse_current:
   b=args.reuse_current.resolve() if v=='src1.7.5' else ROOT/'validation/review-20261004/renamed-builds'/v
   m=json.loads((b/'build.json').read_text())
   assert all(m['sources'].get(k)==h for k,h in sources[v].items()),v
   assert sha(b/'example')==m['binary_sha256'];executables[v]=b/'example'
  else:
   b=out/'build-current';executables[v]=helper.build(ROOT/v,b,sdk);m=json.loads((b/'build.json').read_text())
  metadata[v]=m
 assets=out/'assets';assets.mkdir();(assets/'words.txt').write_bytes((ROOT/'src1.7.5/words.txt').read_bytes().replace(b'\r\n',b'\n'))
 ref=out/'reference';subprocess.run(['g++','-std=c++11','-O2','-I'+str(sdk/'include'),str(ROOT/'tools/review_175/reference_client.cpp'),'-L'+str(sdk/'lib'),'-lframe','-lutility','-lboost_thread','-lboost_system','-lboost_chrono','-lboost_date_time','-lboost_regex','-lpthread','-o',str(ref)],check=True)
 seedso=out/'seed.so';subprocess.run(['g++','-shared','-fPIC',str(ROOT/'src1.7.5/tests/seed_rng.cpp'),'-ldl','-o',str(seedso)],check=True)
 tooling['src1.7.5/tests/seed_rng.cpp']=sha(ROOT/'src1.7.5/tests/seed_rng.cpp')
 audit=dict(sources=sources,inputs=inputs,tooling=tooling,sdk=sdk_model,sdk_binaries=sdk_bins,builds=metadata,reference_sha256=sha(ref),seed_sha256=sha(seedso),policy='three versions; two modes; two fixed seeds; rotated serial order; no rerun replacement; old=5s new=5s separately reported')
 save(out/'frozen-audit.json',audit)
 os.environ.update(LD_PRELOAD=str(seedso),RDFW_STAGE_TIMING='0');os.environ.pop('RDFW_TASK_GROUP_MODE',None)
 refs=[];os.environ['RDFW_TEST_SEED']='2026100401'
 for c in catalogues['new']['cases']:
  plan=out/(c['id']+'-reference.txt');plan.write_text('\n'.join(' '.join(map(str,a)) for a in c['reference_actions'])+'\n');os.environ['RDFW_REFERENCE_PLAN']=str(plan)
  for mode in ('it','nt'):
   run=out/'reference-runs'/(c['id']+'-'+mode);r=runner.run_case(sdk,assets,ref,groups[1][1]/c['path'],2,mode,run,5000,None);r=helper.extract(run,r,2026100401)
   refs.append(dict(id=c['id'],mode=mode,result=r));save(out/'references.json',refs)
   expected_cost=sum(4 if a[0]=='Move' else 2 for a in c['reference_actions'])
   # A server timeout after the final action still has a real official grade.
   # Require every intended action and six actual goals; retain that timeout.
   assert r.get('official_score') is not None and r['final_goals']==6 and r['credited_constraints']==0 and r['action_cost']==expected_cost and len(r['action_sequence'])==len(c['reference_actions']) and 'REFERENCE_ACTION_FAILED' not in (run/'client.log').read_text(),(c['id'],mode,r)
  print('REFERENCE',c['id'],'passed',flush=True)
 os.environ.pop('RDFW_REFERENCE_PLAN',None);rows=[]
 for label,directory,budget in groups:
  for si,seed in enumerate(catalogues[label]['planner_seeds']):
   os.environ['RDFW_TEST_SEED']=str(seed)
   for ci,c in enumerate(catalogues[label]['cases']):
    for mi,mode in enumerate(('it','nt')):
     rotate=(si+ci+mi)%3;order=VERSIONS[rotate:]+VERSIONS[:rotate]
     for v in order:
      run=out/'runs'/(label+'-'+str(seed)+'-'+c['id']+'-'+mode+'-'+v)
      try:r=runner.run_case(sdk,assets,executables[v],directory/c['path'],c['stage'],mode,run,budget,None)
      except Exception as e:r=dict(status='harness_error',error=repr(e),official_score=None,platform_seconds=None)
      r=helper.extract(run,r,seed)
      if r.get('official_score') is None or r.get('platform_seconds') is None:r['base']=None;r['action_cost']=None
      rows.append(dict(suite=label,budget_ms=budget,id=c['id'],family=c['family'],stress=c['stress'],stage=c['stage'],seed=seed,mode=mode,version=v,order=order,result=r));save(out/'results.json',rows)
     print('RUNS',len(rows),'/432',label,seed,c['id'],mode,[(x['version'],x['result']['base'],x['result']['final_goals']) for x in rows[-3:]],flush=True)
 for v in VERSIONS:assert core(ROOT/v)==sources[v];assert sha(executables[v])==metadata[v]['binary_sha256']
 for p,h in inputs.items():assert sha(ROOT/p)==h
 for p,h in tooling.items():assert sha(ROOT/p)==h
 assert helper.sdk_model(sdk)==sdk_model
 for p,h in sdk_bins.items():assert sha(sdk/p)==h
 assert len(rows)==432 and len(refs)==24
 save(out/'final-audit.json',dict(sources_unchanged=True,inputs_unchanged=True,tools_unchanged=True,sdk_unchanged=True,runs=len(rows),reference_runs=len(refs),seed_unconfirmed=sum(not r['result']['seed_confirmed'] for r in rows)))
if __name__=='__main__':main()
