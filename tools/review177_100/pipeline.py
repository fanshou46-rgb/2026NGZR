"""Serial official SDK audit with resumable append-only receipts and immutable inputs."""
from common import *
import argparse, collections, os, re, shutil, socket, subprocess, time, zipfile

def command(args,log,env=None,cwd=None):
    log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w') as f:subprocess.run(list(map(str,args)),stdout=f,stderr=subprocess.STDOUT,check=True,env=env,cwd=cwd)
def records(path):return [json.loads(line) for line in path.read_text(encoding='utf8').splitlines()] if path.exists() else []
def append(path,value):
    with path.open('a',encoding='utf8') as f:f.write(json.dumps(value,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
def archive_runtime(run):
    # Retain every non-shared file. Shared SDK byte hashes are separately frozen.
    runtime=run/'runtime'
    if not runtime.exists():return
    assets=[p for p in list((SDK/'res').glob('*.lp'))+[SDK/'res/iclingo',SDK/'bin/vrunact.sh',SDK/'bin/vruntask.sh'] if p.exists()]
    shared={p.name:sha(p) for p in assets};omitted={}
    dest=run/'runtime.zip'
    assert not dest.exists()
    with zipfile.ZipFile(str(dest),'w',zipfile.ZIP_DEFLATED,compresslevel=6) if sys.version_info>=(3,7) else zipfile.ZipFile(str(dest),'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(runtime.rglob('*')):
            if not p.is_file():continue
            rel=str(p.relative_to(runtime))
            if p.parent==runtime and p.name in shared and sha(p)==shared[p.name]:omitted[rel]=shared[p.name]
            else:z.write(str(p),rel)
        z.writestr('shared-sdk.json',json.dumps(omitted,indent=2))
    with zipfile.ZipFile(str(dest)) as z:assert z.testzip() is None
    resolved=runtime.resolve();assert OUT.resolve() in resolved.parents and resolved.name=='runtime'
    shutil.rmtree(str(resolved))
def run_one(helper,runner,case,arm,seed,run,exe,assets):
    os.environ['RDFW_TEST_SEED']=str(seed);os.environ['RDFW_AUDIT_ABLATION']=arm if arm in ('neutral','no_ask','legacy_visibility') else 'default'
    # Execute SDK's frequently rewritten ASP files on the Linux filesystem.
    # All arms use the same location; exact logs are transferred only after scoring.
    cache=Path('/tmp')/('robocup-'+OUT.name);cache.mkdir(exist_ok=True)
    workrun=cache/str(run.relative_to(OUT));workrun.parent.mkdir(parents=True,exist_ok=True)
    assert not workrun.exists(), 'Preserve and reconcile an interrupted Linux run before resume: '+str(workrun)
    localexe=cache/'binaries'/exe.parent.name/exe.name;localexe.parent.mkdir(parents=True,exist_ok=True)
    if not localexe.exists():shutil.copy2(str(exe),str(localexe))
    assert sha(localexe)==sha(exe)
    localassets=cache/'assets'/assets.name;localassets.mkdir(parents=True,exist_ok=True)
    if not(localassets/'words.txt').exists():shutil.copy2(str(assets/'words.txt'),str(localassets/'words.txt'))
    assert sha(localassets/'words.txt')==sha(assets/'words.txt')
    try:value=runner.run_case(SDK,localassets,localexe,case['file'],case['stage'],case['mode'],workrun,5000,None)
    except Exception as exc:value=dict(status='harness_error',error=repr(exc),raw_score=None,official_score=None,platform_seconds=None,final_goals=None,credited_constraints=None)
    try:value=helper.extract(workrun,value,seed)
    except json.JSONDecodeError as exc:
        # A killed client may leave an incomplete optional JSON log line. Never discard its SDK grade.
        text=(workrun/'server.log').read_text(errors='replace') if (workrun/'server.log').exists() else ''
        value['action_sequence']=re.findall(r'^\s*\[([A-Za-z_]+(?:\s+[^|]*?)?)\|',text,re.M)
        value['action_cost']=sum(4 if a.split()[0].lower()=='move' else 1 if a.split()[0].lower()=='sense' else 2 for a in value['action_sequence'])
        g,c=value.get('final_goals'),value.get('credited_constraints');value['base']=40*g+(20*c if g else 0)-value['action_cost'] if g is not None and c is not None else None
        value.update(seed_confirmed='[RDFW_TEST_SEED] '+str(seed) in text,probe_events=[],decisions=[],probe_parse_error=repr(exc))
    if value.get('official_score') is None:value['base']=None
    server=(workrun/'server.log').read_text(errors='replace') if (workrun/'server.log').exists() else ''
    value['failed_actions']=len(re.findall(r'^\s*\[[^\n]*\|[^\n]*\bfalse\b',server,re.M))
    # Error classes and failed attempts remain independently checkable in server.log.
    # Archive while the complete run is still present; then copy evidence to the repository.
    runtime=workrun/'runtime'
    if runtime.exists():
        shared={p.name:sha(p) for p in list((SDK/'res').glob('*.lp'))+[SDK/'res/iclingo',SDK/'bin/vrunact.sh',SDK/'bin/vruntask.sh']};omitted={}
        with zipfile.ZipFile(str(workrun/'runtime.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(runtime.rglob('*')):
                if not p.is_file():continue
                rel=p.relative_to(runtime).as_posix()
                if p.parent==runtime and p.name in shared and sha(p)==shared[p.name]:omitted[rel]=shared[p.name]
                else:z.write(str(p),rel)
            z.writestr('shared-sdk.json',json.dumps(omitted,indent=2))
        with zipfile.ZipFile(str(workrun/'runtime.zip')) as z:assert z.testzip() is None
        assert cache.resolve() in runtime.resolve().parents and runtime.name=='runtime';shutil.rmtree(str(runtime))
    run.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(str(workrun),str(run))
    value['executed_output']=str(workrun);value['output']=str(run)
    return value
def build():
    helper,runner=helpers();builds=OUT/'builds';builds.mkdir(exist_ok=True)
    os.environ.pop('RDFW_AUDIT_ABLATION',None)
    for arm,source in list(SOURCES.items())+[('experiment',OUT/'experiment/source')]:
        dest=builds/arm
        if (dest/'build.json').exists():
            receipt=json.loads((dest/'build.json').read_text());assert sha(dest/'example')==receipt['binary_sha256'];continue
        print('BUILD',arm,flush=True);helper.build(source,dest,SDK)
    command(['g++','-std=c++11','-O2','-I'+str(SDK/'include'),TOOLS/'reference_client.cpp','-L'+str(SDK/'lib'),'-lframe','-lutility','-lboost_thread','-lboost_system','-lboost_chrono','-lboost_date_time','-lboost_regex','-lpthread','-o',builds/'reference'],builds/'reference-build.log')
    command(['g++','-shared','-fPIC',ROOT/'src1.7.7/tests/seed_rng.cpp','-ldl','-o',builds/'seed.so'],builds/'seed-build.log')
    for arm in ARMS:
        source=SOURCES.get(arm,SOURCES['177']);assets=OUT/'assets'/arm;assets.mkdir(parents=True,exist_ok=True)
        (assets/'words.txt').write_bytes((source/'words.txt').read_bytes().replace(b'\r\n',b'\n'))
    # Check the complete default unit/SDK suite; no tests are weakened for ablated modes.
    for name,source in [('original',SOURCES['177']),('experiment',OUT/'experiment/source')]:
        dest=OUT/'checks'/('unit-'+name)
        command(['cmake','-H'+str(source/'tests'),'-B'+str(dest),'-DCMAKE_BUILD_TYPE=Release','-DOFFICIAL_SDK='+str(SDK)],OUT/'checks'/('configure-'+name+'.log'))
        command(['cmake','--build',dest,'--','-j2'],OUT/'checks'/('build-'+name+'.log'))
        command(['ctest','--output-on-failure'],OUT/'checks'/('ctest-'+name+'.log'),cwd=str(dest))
    unit=OUT/'checks/unit-experiment';source=OUT/'experiment/source'
    command(['g++','-std=c++11','-O2','-UNDEBUG','-I'+str(source),'-I'+str(source/'tests/stubs'),TOOLS/'ablation_tests.cpp',unit/'librdfw_test_core.a','-lpthread','-o',OUT/'checks/ablation-tests'],OUT/'checks/ablation-build.log')
    for mode in ('default','neutral','no_ask','legacy_visibility'):
        env=dict(os.environ,RDFW_AUDIT_ABLATION=mode)
        command([OUT/'checks/ablation-tests',unit/'words.txt'],OUT/'checks'/('ablation-'+mode+'.log'),env=env)
    print('BUILDS AND DEFAULT TESTS COMPLETE',flush=True)
def environment():
    os.environ.update(LD_PRELOAD=str(OUT/'builds/seed.so'),RDFW_STAGE_TIMING='0')
    os.environ.pop('RDFW_TASK_GROUP_MODE',None)
def preflight():
    environment();helper,runner=helpers();cat=json.loads((BANK/'catalogue.json').read_text(encoding='utf8'))
    dest=OUT/'preflight';dest.mkdir(exist_ok=True);journal=dest/'runs.jsonl';done={r['id']+'-'+r['mode'] for r in records(journal)}
    for c in cat['cases']:
        if c['kind']=='invalid':continue
        ref=json.loads((BANK/c['reference']).read_text(encoding='utf8'));plan=ref['plans'][0]
        for mode in ('it','nt'):
            key=c['id']+'-'+mode
            if key in done:continue
            path=dest/(key+'.plan');path.write_text('\n'.join(' '.join(map(str,a)) for a in plan['actions'])+'\n')
            os.environ['RDFW_REFERENCE_PLAN']=str(path)
            case=dict(c,file=BANK/c['path'],mode=mode)
            value=run_one(helper,runner,case,'177',SEEDS[0],dest/key,OUT/'builds/reference',OUT/'assets/177')
            expected_cost=sum(4 if a[0]=='move' else 1 if a[0]=='sense' else 2 for a in plan['actions'])
            expected_c=30-plan['expected_violated_constraints']
            client=(dest/key/'client.log').read_text(errors='replace')
            ok=value.get('final_goals')==plan['expected_completed_goals'] and value.get('credited_constraints')==expected_c and value.get('action_cost')==expected_cost and len(value['action_sequence'])==len(plan['actions']) and value.get('official_score') is not None and not value.get('platform_timed_out') and not value.get('external_timeout') and 'REFERENCE_ACTION_FAILED' not in client
            append(journal,dict(id=c['id'],mode=mode,expected_goals=plan['expected_completed_goals'],expected_constraints=expected_c,expected_cost=expected_cost,ok=ok,result=value))
            print('PREFLIGHT',len(records(journal)),'/180',key,'PASS' if ok else 'FAIL',value.get('final_goals'),value.get('credited_constraints'),value.get('platform_seconds'),flush=True)
            if not ok:raise RuntimeError('Author preflight failed: '+key+'; no planner run performed')
    os.environ.pop('RDFW_REFERENCE_PLAN',None)
    rr=records(journal);assert len(rr)==180 and all(r['ok'] for r in rr)
    save(dest/'audit.json',dict(runs=180,passed=180,robot_runs=0,all_official_grades=True))
def equivalence():
    environment();helper,runner=helpers();journal=OUT/'checks/equivalence.jsonl';done={r['key'] for r in records(journal)}
    chosen=[]
    cat=json.loads((ROOT/'题目/generalization_20261004/catalogue.json').read_text(encoding='utf8'))
    for c in cat['cases']:
        if c['id'] in ('g01a','g02a','g03a','g04a'):chosen.append(dict(c,file=ROOT/'题目/generalization_20261004'/c['path'],stage=1))
    for c in chosen:
        for mode in ('it','nt'):
            for arm in ('177','experiment'):
                key=c['id']+'-'+mode+'-'+arm
                if key in done:continue
                case=dict(c,mode=mode);run=OUT/'checks/equivalence'/key
                r=run_one(helper,runner,case,arm,SEEDS[0],run,OUT/'builds'/arm/'example',OUT/'assets/177')
                append(journal,dict(key=key,id=c['id'],mode=mode,arm=arm,result=r))
    paired=collections.defaultdict(dict)
    for r in records(journal):paired[(r['id'],r['mode'])][r['arm']]=r['result']
    assert paired
    for key,arms in paired.items():
        a,b=arms['177'],arms['experiment'];assert all(a[k]==b[k] for k in ('action_sequence','final_goals','credited_constraints','action_cost','base')),key
    save(OUT/'checks/equivalence-audit.json',dict(pairs=len(paired),all_actions_goals_constraints_cost_base_equal=True,scope='4 known short Stage1 inputs IT/NT; clocks not equated'))
    print('DEFAULT EQUIVALENCE',len(paired),'pairs',flush=True)
def freeze():
    helper,_=helpers();cat=json.loads((BANK/'catalogue.json').read_text(encoding='utf8'))
    assert json.loads((OUT/'preflight/audit.json').read_text())['passed']==180
    saved=json.loads((OUT/'original-source-hashes.json').read_text())
    assert saved=={k:core(p) for k,p in SOURCES.items()}
    inputs={str(p.relative_to(ROOT)):sha(p) for p in BANK.rglob('*') if p.is_file()}
    for cases in all_cases(helper):
        for c in cases:
            p=c['file'];inputs[p.relative_to(ROOT).as_posix()]=sha(p)
    for folder in ('generalization_20261004','generalization_175_20261004_v4','generalization_176_20261004','generalization_177_20261004'):
        p=ROOT/'题目'/folder/'catalogue.json';inputs[p.relative_to(ROOT).as_posix()]=sha(p)
    p=ROOT/'src1.7/test-results/validation-20261002/input-audit.json';inputs[p.relative_to(ROOT).as_posix()]=sha(p)
    sdkfiles={str(p.relative_to(SDK)):sha(p) for p in list((SDK/'res').glob('*.lp'))+[SDK/'res/iclingo',SDK/'bin/cserver',SDK/'bin/vrunact.sh',SDK/'bin/vruntask.sh',SDK/'lib/libasp.so',SDK/'lib/libframe.a',SDK/'lib/libutility.a']}
    tools={str(p.relative_to(ROOT)):sha(p) for p in list(TOOLS.glob('*.py'))+list(TOOLS.glob('*.cpp'))+[ROOT/'src1.7.7/tests/run_probe_compare.py',ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py']}
    binaries={arm:sha(OUT/'builds'/arm/'example') for arm in ('167','167_200','177','experiment')}
    builds={arm:json.loads((OUT/'builds'/arm/'build.json').read_text()) for arm in binaries}
    for arm in binaries:
        source=SOURCES.get(arm,OUT/'experiment/source')
        assert builds[arm]['binary_sha256']==binaries[arm]
        assert all(builds[arm]['sources'][name]==h for name,h in core(source).items())
    assets={arm:sha(OUT/'assets'/arm/'words.txt') for arm in ARMS}
    save(OUT/'frozen-audit.json',dict(original_sources=saved,experiment=core(OUT/'experiment/source'),inputs=inputs,tools=tools,sdk=sdkfiles,binaries=binaries,builds=builds,assets=assets,seed_binary=sha(OUT/'builds/seed.so'),seeds=SEEDS,deadline_ms=5000,source_commit='68fe263b096e0d3075da4c358fe9560a98ebf359',policy='serial rotated; default policy; no result deletion/replacement; sources/inputs/tools/SDK fixed; Linux temporary scoring filesystem; exact logs archived after grading'))
    shared=OUT/'shared-sdk.zip'
    with zipfile.ZipFile(str(shared),'w',zipfile.ZIP_DEFLATED) as z:
        for relative in sdkfiles:z.write(str(SDK/relative),relative)
    print('FROZEN BEFORE ROBOT MATRIX',flush=True)
def all_cases(helper):
    cat=json.loads((BANK/'catalogue.json').read_text(encoding='utf8'))
    new=[dict(c,suite='new',file=BANK/c['path']) for c in cat['cases'] if c['kind']!='invalid']
    legacy=[dict(c,suite='historical',family=c['suite'],file=Path(c['path']),cluster=c['id']) for c in helper.cases('legacy')]
    # The legacy loader covers 70 fixtures; append the 71st unified input explicitly.
    source=json.loads((ROOT/'src1.7/test-results/validation-20261002/input-audit.json').read_text())
    historical_families={c['id']:c['suite'] for c in source['cases']}
    for c in legacy:c['family']=historical_families[c['id']]
    present={c['id'] for c in legacy}
    for c in source['cases']:
        if c['id'] in present:continue
        relative=c['path'].split('/2026NGZR/',1)[1];p=ROOT/relative
        assert helper.matching_input(p,c['sha256'])
        legacy.append(dict(c,suite='historical',family=c['suite'],file=p,kind='scored',cluster=c['id']))
    assert len(legacy)==71,len(legacy)
    seen=[]
    for folder in ('generalization_20261004','generalization_175_20261004_v4','generalization_176_20261004','generalization_177_20261004'):
        path=ROOT/'题目'/folder;cat=json.loads((path/'catalogue.json').read_text(encoding='utf8'))
        for c in cat['cases']:seen.append(dict(c,suite='seen',file=path/c['path'],cluster=c['id']))
    assert len(seen)==52
    invalid=[dict(c,suite='invalid',file=BANK/c['path']) for c in json.loads((BANK/'catalogue.json').read_text(encoding='utf8'))['cases'] if c['kind']=='invalid']
    excluded=[dict(id='excluded-'+str(i),file=ROOT/'题目/realcompetiton_2024'/('%02d.xml'%i),stage=2,suite='excluded',family='historical_platform_invalid',kind='invalid') for i in (2,4,5)]
    return new,legacy,seen,invalid,excluded
def matrix():
    environment();helper,runner=helpers();assert (OUT/'frozen-audit.json').exists()
    journal=OUT/'results.jsonl';done={r['key'] for r in records(journal)};groups=all_cases(helper)
    scheduled=[]
    for suite,cases,rounds,arms in [('new',groups[0],range(4),ARMS),('historical',groups[1],range(4),ARMS[:3]),('seen',groups[2],range(2),ARMS[:3]),('invalid',groups[3],range(1),ARMS[:3]),('excluded',groups[4],range(1),ARMS[:3])]:
        for ri in rounds:
            for ci,c in enumerate(cases):
                for mi,mode in enumerate(('it','nt')):
                    rotation=(ri+ci+mi)%len(arms);order=arms[rotation:]+arms[:rotation]
                    for arm in order:
                        key=suite+'-'+c['id']+'-'+mode+'-r'+str(ri+1)+'-'+arm
                        scheduled.append(dict(key=key,case=c,mode=mode,round=ri+1,seed=SEEDS[ri],arm=arm,order=order))
    save(OUT/'schedule.json', [{k:v for k,v in s.items() if k!='case'} | {'id':s['case']['id'],'suite':s['case']['suite']} for s in scheduled] if sys.version_info>=(3,9) else [dict({k:v for k,v in s.items() if k!='case'},id=s['case']['id'],suite=s['case']['suite']) for s in scheduled])
    total=len(scheduled);assert total==6726,total # 4320+1704+624+60+18
    start=time.monotonic()
    for s in scheduled:
        if s['key'] in done:continue
        c=dict(s['case'],mode=s['mode']);arm=s['arm'];exe=OUT/'builds'/('experiment' if arm not in ARMS[:3] else arm)/'example'
        run=OUT/'runs'/s['key']
        if run.exists():raise RuntimeError('Unjournaled interrupted run retained; reconcile before resume: '+s['key'])
        value=run_one(helper,runner,c,arm,s['seed'],run,exe,OUT/'assets'/arm)
        row={k:s[k] for k in ('key','arm','round','seed','mode','order')};row.update({k:c.get(k) for k in ('id','suite','family','category','stage','kind','cluster','pair_id')});row['result']=value
        append(journal,row);done.add(s['key'])
        save(OUT/'progress.json',dict(completed=len(done),total=total,last=s['key'],result={k:value.get(k) for k in ('base','final_goals','credited_constraints','official_score','platform_seconds','status')},elapsed_seconds=time.monotonic()-start))
        if len(done)%12==0:print('MATRIX',len(done),'/',total,s['key'],'G',value.get('final_goals'),'B',value.get('base'),flush=True)
    audit=json.loads((OUT/'frozen-audit.json').read_text())
    assert audit['original_sources']=={k:core(p) for k,p in SOURCES.items()}
    assert audit['experiment']==core(OUT/'experiment/source')
    for p,h in audit['inputs'].items():assert sha(ROOT/p)==h,p
    for p,h in audit['tools'].items():assert sha(ROOT/p)==h,p
    for p,h in audit['sdk'].items():assert sha(SDK/p)==h,p
    for arm,h in audit['binaries'].items():assert sha(OUT/'builds'/arm/'example')==h,arm
    for arm,h in audit['assets'].items():assert sha(OUT/'assets'/arm/'words.txt')==h,arm
    assert sha(OUT/'builds/seed.so')==audit['seed_binary']
    rr=records(journal);assert len(rr)==total and len({r['key'] for r in rr})==total
    save(OUT/'final-audit.json',dict(runs=total,sources_unchanged=True,inputs_unchanged=True,tools_unchanged=True,sdk_unchanged=True,binaries_unchanged=True,suite_counts=dict(collections.Counter(r['suite'] for r in rr)),seed_unconfirmed=sum(not r['result']['seed_confirmed'] for r in rr)))
    print('COMPLETE',total,flush=True)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['build','preflight','equivalence','freeze','matrix']);args=parser.parse_args()
    with socket.socket() as s:s.bind(('127.0.0.1',7932))
    globals()[args.phase]()
if __name__=='__main__':main()
