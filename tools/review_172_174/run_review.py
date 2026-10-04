"""Frozen four-version comparison; all scores, missing results and traces retained."""
import argparse, collections, hashlib, importlib.util, json, os, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
VERSIONS=['src1.7.1','src1.7.2','src1.7.3','src1.7.4']
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,str(path));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
def core(source):return {p.name:sha(p) for p in source.iterdir() if p.is_file() and (p.suffix in ('.cpp','.hpp','.h') or p.name=='words.txt')}
def main():
 p=argparse.ArgumentParser();p.add_argument('--sdk',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--reuse-build-root',type=Path,help='Optional directory containing VERSION/build.json and VERSION/example; production hashes must match')
 args=p.parse_args()
 out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);sdk=args.sdk.resolve()
 helpers=load('helpers',ROOT/'src1.7.4/tests/run_probe_compare.py');runner=load('runner',ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py')
 directory=ROOT/'题目/generalization_20261004';catalogue=json.loads((directory/'catalogue.json').read_text(encoding='utf8'));cases=catalogue['cases']
 audit={'catalogue_sha256':sha(directory/'catalogue.json'),'sources':{},'binaries':{},'sdk':helpers.sdk_model(sdk),
        'sdk_binaries':{str(q.relative_to(sdk)):sha(q) for q in [sdk/'bin/cserver',sdk/'lib/libasp.so',sdk/'lib/libframe.a',sdk/'res/iclingo']},
        'compiler':subprocess.check_output(['g++','--version']).decode(),'policy':'24 cases x 4 versions x 2 seeds x IT/NT; rotated serial order; no rerun replacement',
        'reuse_scope':'All root production cpp/hpp/h and words.txt must match recorded build. Renamed tooling/docs are excluded from binary equivalence, and separately frozen.'}
 executables={}
 for version in VERSIONS:
  b=args.reuse_build_root.resolve()/version if args.reuse_build_root else out/('build-'+version)
  if not args.reuse_build_root:helpers.build(ROOT/version,b,sdk)
  metadata=json.loads((b/'build.json').read_text());sources=core(ROOT/version)
  assert all(metadata['sources'].get(k)==v for k,v in sources.items()),version
  assert set(k for k in metadata['sources'] if '/' not in k and Path(k).suffix in ('.cpp','.hpp','.h'))==set(k for k in sources if k!='words.txt')
  assert metadata['binary_sha256']==sha(b/'example')
  audit['sources'][version]=sources;audit['binaries'][version]={'sha256':sha(b/'example'),'build_metadata_sha256':sha(b/'build.json'),'build':str(b)}
  executables[version]=b/'example'
 audit['tooling']={str(q.relative_to(ROOT)):sha(q) for q in Path(__file__).resolve().parent.iterdir() if q.suffix in ('.cpp','.py','.json')}
 for q in (ROOT/'src1.7.4/tests/run_probe_compare.py',ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py'):
  audit['tooling'][str(q.relative_to(ROOT))]=sha(q)
 save(out/'frozen-audit.json',audit)
 for c in cases:assert sha(directory/c['path'])==c['sha256']
 assets=out/'assets';assets.mkdir();(assets/'words.txt').write_bytes((ROOT/'src1.7.4/words.txt').read_bytes().replace(b'\r\n',b'\n'))
 reference=out/'reference-client'
 subprocess.run(['g++','-std=c++11','-O2','-I'+str(sdk/'include'),str(Path(__file__).resolve().parent/'reference_client.cpp'),'-L'+str(sdk/'lib'),'-lframe','-lutility','-lboost_thread','-lboost_system','-lboost_chrono','-lboost_date_time','-lboost_regex','-lpthread','-o',str(reference)],check=True)
 seedso=out/'seed.so';subprocess.run(['g++','-shared','-fPIC',str(ROOT/'src1.7.4/tests/seed_rng.cpp'),'-ldl','-o',str(seedso)],check=True)
 os.environ.update(LD_PRELOAD=str(seedso),RDFW_STAGE_TIMING='0');os.environ.pop('RDFW_TASK_GROUP_MODE',None)
 references=[]
 for c in cases:
  plan=out/(c['id']+'-reference.txt');plan.write_text('\n'.join(' '.join(map(str,a)) for a in c['reference_actions'])+'\n')
  os.environ['RDFW_REFERENCE_PLAN']=str(plan);os.environ['RDFW_TEST_SEED']=str(catalogue['planner_seeds'][0])
  for mode in ('it','nt'):
   run=out/'reference-runs'/(c['id']+'-'+mode)
   result=runner.run_case(sdk,assets,reference,directory/c['path'],c['stage'],mode,run,5000,None)
   result=helpers.extract(run,result,catalogue['planner_seeds'][0]);references.append(dict(id=c['id'],mode=mode,result=result));save(out/'references.json',references)
   expected_cost=sum(4 if a[0]=='Move' else 2 for a in c['reference_actions'])
   assert result['status']=='ok' and result['final_goals']==c['reference_goals'] and result['credited_constraints']==c['reference_constraints'] and result['action_cost']==expected_cost and 'REFERENCE_ACTION_FAILED' not in (run/'client.log').read_text(),(c['id'],mode,result)
  print('REFERENCE',c['id'],'OK',flush=True)
 os.environ.pop('RDFW_REFERENCE_PLAN',None)
 rows=[]
 for seed_index,seed in enumerate(catalogue['planner_seeds']):
  os.environ['RDFW_TEST_SEED']=str(seed)
  for ci,c in enumerate(cases):
   for mi,mode in enumerate(('it','nt')):
    rotate=(ci+mi+seed_index)%4;order=VERSIONS[rotate:]+VERSIONS[:rotate]
    for version in order:
     run=out/'runs'/(str(seed)+'-'+c['id']+'-'+mode+'-'+version)
     try:result=runner.run_case(sdk,assets,executables[version],directory/c['path'],c['stage'],mode,run,5000,None)
     except Exception as e:result={'status':'harness_or_platform_rejected','error':repr(e),'official_score':None,'final_goals':None,'credited_constraints':None}
     result=helpers.extract(run,result,seed)
     if result.get('official_score') is None or result.get('platform_seconds') is None:
      result['base']=None;result['action_cost']=None
     row=dict(id=c['id'],family=c['family'],split=c['split'],stress=c['stress'],stage=c['stage'],mode=mode,seed=seed,version=version,order=order,result=result)
     rows.append(row);save(out/'results.json',rows)
    print('RUNS',len(rows),'/ 384',seed,c['id'],mode,'base',[(r['version'],r['result']['base']) for r in rows[-4:]],flush=True)
 for version in VERSIONS:assert core(ROOT/version)==audit['sources'][version]
 assert helpers.sdk_model(sdk)==audit['sdk']
 for relative,digest in audit['sdk_binaries'].items():assert sha(sdk/relative)==digest
 for version,metadata in audit['binaries'].items():assert sha(executables[version])==metadata['sha256']
 for rel,h in audit['tooling'].items():assert sha(ROOT/rel)==h
 for c in cases:assert sha(directory/c['path'])==c['sha256']
 assert sha(directory/'catalogue.json')==audit['catalogue_sha256']
 save(out/'final-audit.json',{'sources_unchanged':True,'sdk_unchanged':True,'inputs_unchanged':True,'tools_unchanged':True,'runs':len(rows),'reference_runs':len(references),'seed_unconfirmed':sum(not r['result']['seed_confirmed'] for r in rows)})
 print('COMPLETE',out,flush=True)
if __name__=='__main__':main()
