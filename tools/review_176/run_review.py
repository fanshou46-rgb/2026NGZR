"""Serial real-SDK comparison; immutable sources, all pairs, no cherry-picked reruns."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
VERSIONS=['src1.7.5','src1.7.6']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def load(name,p):
    s=importlib.util.spec_from_file_location(name,str(p));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def core(p):return {q.name:sha(q) for q in p.iterdir() if q.suffix in ('.cpp','.hpp','.h') or q.name=='words.txt'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--sdk',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    sdk=a.sdk.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    helper=load('helper',ROOT/'src1.7.6/tests/run_probe_compare.py')
    runner=load('runner',ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py')
    groups=[];inputs={}
    for label,directory in [('old','generalization_20261004'),('seen175','generalization_175_20261004_v4'),('holdout176','generalization_176_20261004')]:
        directory=ROOT/'题目'/directory
        cat=json.loads((directory/'catalogue.json').read_text(encoding='utf8'))
        inputs[str((directory/'catalogue.json').relative_to(ROOT))]=sha(directory/'catalogue.json')
        for c in cat['cases']:
            f=directory/c['path'];assert sha(f)==c['sha256'];inputs[str(f.relative_to(ROOT))]=sha(f)
        groups.append((label,directory,cat['cases']))
    competition=[]
    for n in (1,9,19,24,31,36):
        f=ROOT/'题目/realcompetiton_2024'/('%02d.xml'%n)
        competition.append(dict(id=f.stem,path=f.name,family='competition_sample',stage=2));inputs[str(f.relative_to(ROOT))]=sha(f)
    groups.append(('competition',ROOT/'题目/realcompetiton_2024',competition))
    controls=[]
    for label,folder,cases in groups[:3]:
        for c in cases:
            if c['id'] in ('g01a','h03a','j01a','j02a'):controls.append(('stage1_control',folder,dict(c,stage=1)))
    sources={v:core(ROOT/v) for v in VERSIONS};metadata={};exe={}
    previous=ROOT/'validation/review175-20261004/frozen-v2/build-current'
    m=json.loads((previous/'build.json').read_text(encoding='utf8'))
    assert all(m['sources'].get(k)==v for k,v in sources['src1.7.5'].items())
    assert sha(previous/'example')==m['binary_sha256'];exe['src1.7.5']=previous/'example';metadata['src1.7.5']=m
    exe['src1.7.6']=helper.build(ROOT/'src1.7.6',out/'build-current',sdk)
    metadata['src1.7.6']=json.loads((out/'build-current/build.json').read_text())
    assets=out/'assets';assets.mkdir();(assets/'words.txt').write_bytes((ROOT/'src1.7.6/words.txt').read_bytes().replace(b'\r\n',b'\n'))
    reference=out/'reference'
    subprocess.run(['g++','-std=c++11','-O2','-I'+str(sdk/'include'),str(ROOT/'tools/review_175/reference_client.cpp'),'-L'+str(sdk/'lib'),'-lframe','-lutility','-lboost_thread','-lboost_system','-lboost_chrono','-lboost_date_time','-lboost_regex','-lpthread','-o',str(reference)],check=True)
    seedso=out/'seed.so';subprocess.run(['g++','-shared','-fPIC',str(ROOT/'src1.7.6/tests/seed_rng.cpp'),'-ldl','-o',str(seedso)],check=True)
    toolpaths=[Path(__file__).resolve(),ROOT/'tools/review_176/generate_holdout.py',ROOT/'src1.7.6/tests/run_probe_compare.py',ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py',ROOT/'tools/review_175/reference_client.cpp',ROOT/'src1.7.6/tests/seed_rng.cpp']
    tooling={str(p.relative_to(ROOT)):sha(p) for p in toolpaths}
    sdk_model=helper.sdk_model(sdk);bins={str(p.relative_to(sdk)):sha(p) for p in [sdk/'bin/cserver',sdk/'lib/libasp.so',sdk/'lib/libframe.a',sdk/'res/iclingo']}
    save(out/'frozen-audit.json',dict(sources=sources,inputs=inputs,tooling=tooling,sdk=sdk_model,sdk_binaries=bins,builds=metadata,reference_sha256=sha(reference),seed_sha256=sha(seedso),policy='all 24 old + all 12 seen175 + all 8 new176 + 6 preselected competition; IT/NT x 2 seeds x 2 versions = 400; four Stage1 controls x IT/NT x 2 versions = 16; rotated serial order; all failures retained; no concurrent builds or input changes'))
    os.environ.update(LD_PRELOAD=str(seedso),RDFW_STAGE_TIMING='0',RDFW_TEST_SEED='2026100401');os.environ.pop('RDFW_TASK_GROUP_MODE',None)
    refs=[]
    for c in groups[2][2]:
        plan=out/(c['id']+'-reference.txt');plan.write_text('\n'.join(' '.join(map(str,a)) for a in c['reference_actions'])+'\n');os.environ['RDFW_REFERENCE_PLAN']=str(plan)
        for mode in ('it','nt'):
            run=out/'references'/(c['id']+'-'+mode)
            r=helper.extract(run,runner.run_case(sdk,assets,reference,groups[2][1]/c['path'],2,mode,run,5000,None),2026100401)
            refs.append(dict(id=c['id'],mode=mode,result=r));save(out/'references.json',refs)
            expected=sum(4 if a[0]=='Move' else 2 for a in c['reference_actions'])
            assert r.get('official_score') is not None and r.get('final_goals')==6 and r.get('credited_constraints')==0 and r.get('action_cost')==expected and len(r['action_sequence'])==len(c['reference_actions']) and 'REFERENCE_ACTION_FAILED' not in (run/'client.log').read_text(),(c['id'],mode,r)
        print('REFERENCE',c['id'],'G=6',flush=True)
    os.environ.pop('RDFW_REFERENCE_PLAN',None);rows=[]
    def pair(label,folder,c,seed,mode,rotate):
        os.environ['RDFW_TEST_SEED']=str(seed);order=VERSIONS[rotate:]+VERSIONS[:rotate]
        for v in order:
            run=out/'runs'/(label+'-'+str(seed)+'-'+c['id']+'-'+mode+'-'+v)
            try:r=runner.run_case(sdk,assets,exe[v],folder/c['path'],c['stage'],mode,run,5000,None)
            except Exception as e:r=dict(status='harness_error',error=repr(e),official_score=None,platform_seconds=None)
            r=helper.extract(run,r,seed)
            if r.get('official_score') is None or r.get('platform_seconds') is None:r['base']=None;r['action_cost']=None
            rows.append(dict(suite=label,id=c['id'],family=c['family'],stage=c['stage'],seed=seed,mode=mode,version=v,order=order,result=r));save(out/'results.json',rows)
        print('RUNS',len(rows),'/416',label,c['id'],mode,seed,[(x['version'],x['result'].get('base'),x['result'].get('final_goals')) for x in rows[-2:]],flush=True)
    for si,seed in enumerate((2026100401,2026100402)):
        for gi,(label,folder,cases) in enumerate(groups):
            for ci,c in enumerate(cases):
                for mi,mode in enumerate(('it','nt')):pair(label,folder,c,seed,mode,(si+gi+ci+mi)%2)
    for ci,(label,folder,c) in enumerate(controls):
        for mi,mode in enumerate(('it','nt')):pair(label,folder,c,2026100401,mode,(ci+mi)%2)
    for v in VERSIONS:assert core(ROOT/v)==sources[v] and sha(exe[v])==metadata[v]['binary_sha256']
    for p,h in inputs.items():assert sha(ROOT/p)==h
    for p,h in tooling.items():assert sha(ROOT/p)==h
    assert helper.sdk_model(sdk)==sdk_model
    for p,h in bins.items():assert sha(sdk/p)==h
    assert len(rows)==416 and len(refs)==16
    save(out/'final-audit.json',dict(sources_unchanged=True,inputs_unchanged=True,tools_unchanged=True,sdk_unchanged=True,runs=len(rows),reference_runs=len(refs),seed_unconfirmed=sum(not r['result']['seed_confirmed'] for r in rows)))
if __name__=='__main__':main()
