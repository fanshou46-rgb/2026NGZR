"""Checkpointed builds and serial SDK runs; no result replacement or hidden truth input."""
from pathlib import Path
import argparse, importlib.util, json, os, shutil, subprocess, sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
LAB=ROOT/'experiments/full_probability'
SDK=Path('/tmp/env-release-2026-search')

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path));m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m

sys.path.insert(0,str(ROOT/'tools/review177_100'))
helper=module('full_compare',ROOT/'src1.7.7/tests/run_probe_compare.py')
pipe=module('full_audit_pipeline',ROOT/'tools/review177_100/pipeline.py')
pipe.OUT=LAB

def command(args,log,cwd=None):
    log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w') as f:subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT,check=True,cwd=cwd)

def build(checkpoint,native=False):
    source=LAB/'source';out=LAB/'builds'/checkpoint;out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise RuntimeError('Use a new checkpoint; previous build evidence is retained')
    if native:
        # WSL-native I/O shortens compilation only. Compiler options and SDK
        # remain helper.build's official protocol; input bytes are verified.
        cache=Path('/tmp/full-probability-builds')/checkpoint
        assert not cache.exists(),'Native checkpoint workspace already exists'
        cache.mkdir(parents=True);out.mkdir()
        original=helper.fingerprints(source)
        shutil.copytree(str(source),str(out/'source'))
        shutil.copytree(str(out/'source'),str(cache/'source'))
        assert helper.fingerprints(cache/'source')==original
        try:helper.build(cache/'source',cache/'robot',SDK)
        finally:
            if (cache/'robot').exists():
                for f in (cache/'robot').iterdir():
                    if f.is_file():shutil.copy2(str(f),str(out/f.name))
        unit=cache/'checks';logs=LAB/'checks';logs.mkdir(exist_ok=True)
        try:
            command(['cmake','-H'+str(cache/'source/tests'),'-B'+str(unit),'-DCMAKE_BUILD_TYPE=Release','-DOFFICIAL_SDK='+str(SDK)],logs/(checkpoint+'-configure.log'))
            command(['cmake','--build',unit,'--','-j2'],logs/(checkpoint+'-build.log'))
            command(['ctest','--output-on-failure'],logs/(checkpoint+'-ctest.log'),str(unit))
        finally:
            retained=logs/checkpoint;retained.mkdir(exist_ok=True)
            if unit.exists():
                for f in unit.rglob('*'):
                    if f.is_file() and (f.suffix in ('.log','.json') or f.name=='CMakeCache.txt'):
                        q=retained/f.relative_to(unit);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(str(f),str(q))
        assert helper.fingerprints(source)==original==helper.fingerprints(cache/'source')
        passed=dict(ctest=True,checkpoint=checkpoint,native_workspace=str(cache),
            test_binaries={f.name:helper.sha(f) for f in unit.iterdir() if f.is_file() and os.access(str(f),os.X_OK)})
        (out/'checks-passed.json').write_text(json.dumps(passed)+'\n')
        print('CHECKPOINT BUILD AND TEST PASS',checkpoint,flush=True)
        return
    helper.build(source,out,SDK)
    # Freeze before testing, including failing checkpoints. A failed test is
    # evidence about these exact bytes and must survive later repairs.
    assert json.loads((out/'build.json').read_text())['sources']==helper.fingerprints(source)
    shutil.copytree(str(source),str(out/'source'))
    unit=LAB/'checks'/checkpoint
    command(['cmake','-H'+str(source/'tests'),'-B'+str(unit),'-DCMAKE_BUILD_TYPE=Release','-DOFFICIAL_SDK='+str(SDK)],unit.parent/(checkpoint+'-configure.log'))
    command(['cmake','--build',unit,'--','-j2'],unit.parent/(checkpoint+'-build.log'))
    command(['ctest','--output-on-failure'],unit.parent/(checkpoint+'-ctest.log'),str(unit))
    assert json.loads((out/'build.json').read_text())['sources']==helper.fingerprints(source)
    (out/'checks-passed.json').write_text(json.dumps(dict(ctest=True,checkpoint=checkpoint))+'\n')
    print('CHECKPOINT BUILD AND TEST PASS',checkpoint,flush=True)

def runs(checkpoint,suite,policy='mechanical'):
    build=LAB/'builds'/checkpoint;source=build/'source'
    receipt=json.loads((build/'build.json').read_text())
    if not source.exists():
        assert receipt['sources']==helper.fingerprints(LAB/'source')
        shutil.copytree(str(LAB/'source'),str(source))
    assert receipt['sources']==helper.fingerprints(source),'Source changed since checkpoint build'
    assert (build/'checks-passed.json').exists()
    assert helper.sha(build/'example')==receipt['binary_sha256']
    cat=json.loads((ROOT/'题目/independent_100_20261004/catalogue.json').read_text(encoding='utf8'))
    cases=[c for c in cat['cases'] if c['kind']!='invalid']
    if suite in ('smoke','smoke2'):
        selected=[];families=set()
        for c in cases:
            selected_stage=2 if suite=='smoke2' else 1
            if c['stage']==selected_stage and (c['family'] not in families or c['id']=='A01-02-s'+str(selected_stage)):
                selected.append(c);families.add(c['family'])
        cases=selected
    elif suite=='stage1':cases=[c for c in cases if c['stage']==1]
    assets=LAB/'assets'/'lab';assets.mkdir(parents=True,exist_ok=True)
    (assets/'words.txt').write_bytes((source/'words.txt').read_bytes().replace(b'\r\n',b'\n'))
    tag=suite if policy=='mechanical' else suite+'-'+policy
    journal=LAB/(checkpoint+'-'+tag+'.jsonl')
    done={r['key'] for r in pipe.records(journal)}
    # Same frozen baseline binary, fresh runs on the current host.
    baseline=ROOT/'validation/review177-100-20261004/builds/167_200/example'
    os.environ.update(LD_PRELOAD=str(ROOT/'validation/review177-100-20261004/builds/seed.so'),RDFW_STAGE_TIMING='0')
    os.environ.pop('RDFW_TASK_GROUP_MODE',None)
    _,runner=pipe.helpers()
    total=len(cases)*2*2*2
    for repeat in range(2):
        for ci,c in enumerate(cases):
            for mi,mode in enumerate(('it','nt')):
                order=('lab','167_200') if (ci+mi+repeat)%2==0 else ('167_200','lab')
                for arm in order:
                    key='-'.join([checkpoint,tag,c['id'],mode,'repeat'+str(repeat),arm])
                    if key in done:continue
                    run=LAB/'runs'/key
                    assert not run.exists(),'Unjournaled run retained: '+str(run)
                    case=dict(c,file=ROOT/'题目/independent_100_20261004'/c['path'],mode=mode)
                    os.environ['RDFW_FULL_MODEL']='full' if policy=='full' and arm=='lab' else ''
                    value=pipe.run_one(helper,runner,case,arm,2026100403,run,build/'example' if arm=='lab' else baseline,assets)
                    row=dict(key=key,checkpoint=checkpoint,suite=tag,policy=policy,id=c['id'],family=c['family'],stage=c['stage'],mode=mode,arm=arm,repeat=repeat,seed=2026100403,result=value)
                    pipe.append(journal,row);done.add(key)
                    print('SDK',len(done),'/',total,key,'G',value.get('final_goals'),'B',value.get('base'),'F',value.get('official_score'),flush=True)
    assert len(done)==total
    assert receipt['sources']==helper.fingerprints(source),'Source changed during SDK runs'
    rr=pipe.records(journal);pairs={}
    for r in rr:pairs.setdefault((r['id'],r['mode'],r['repeat']),{})[r['arm']]=r['result']
    regressions=[];delta={k:0 for k in ('final_goals','base','official_score')}
    for key,p in pairs.items():
        for k in delta:
            a,b=p['lab'].get(k),p['167_200'].get(k)
            if a is not None and b is not None:delta[k]+=a-b
        if any(p['lab'].get(k) is None or (p['167_200'].get(k) is not None and p['lab'][k]<p['167_200'][k]) for k in delta):
            regressions.append(dict(case=list(key),lab={k:p['lab'].get(k) for k in delta},baseline={k:p['167_200'].get(k) for k in delta}))
    result=dict(checkpoint=checkpoint,suite=tag,policy=policy,runs=len(rr),pairs=len(pairs),deltas=delta,regressions=regressions,
        warning='development regression, two repeats of one seed; not independent holdout or probability attribution')
    (LAB/(checkpoint+'-'+tag+'-summary.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['build','runs']);p.add_argument('--checkpoint',required=True)
    p.add_argument('--suite',choices=['smoke','smoke2','stage1','all'],default='smoke')
    p.add_argument('--policy',choices=['mechanical','full'],default='mechanical');p.add_argument('--native',action='store_true');a=p.parse_args()
    assert a.checkpoint.replace('_','').isalnum()
    if a.phase=='build':build(a.checkpoint,a.native)
    else:runs(a.checkpoint,a.suite,a.policy)

if __name__=='__main__':main()
