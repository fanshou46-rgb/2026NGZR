#!/usr/bin/env python3
"""Unchanged fixed solver, official SDK, isolated runs, complete raw evidence."""
import argparse
from collections import Counter
import difflib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from check import check

SUITE=Path(__file__).resolve().parents[1]
ROOT=SUITE.parents[1]
SOURCE=ROOT/'src1.3.3-fixed'
sys.path.insert(0,str(SOURCE/'tests'))
from compare_legal import build, trace
from baseline import run_case,digest

def compile_extra(sdk,out):
    ref=out/'reference-client'
    cmd=['g++','-std=c++11','-O2','-I'+str(sdk/'include'),str(SUITE/'tools/reference_client.cpp'),
         '-L'+str(sdk/'lib'),'-lframe','-lutility','-lboost_thread','-lboost_system',
         '-lboost_chrono','-lboost_date_time','-lboost_regex','-lpthread','-ldl','-o',str(ref)]
    subprocess.run(cmd,check=True)
    parser=out/'parse-snapshot'
    cmd=['g++','-std=c++11','-O2','-DFIXED_VERSION','-I'+str(SOURCE/'tests/stubs'),
         '-I'+str(SOURCE),str(SOURCE/'tests/parse_snapshot.cpp')]
    cmd += [str(p) for p in sorted(SOURCE.glob('*.cpp')) if p.name!='main.cpp']
    cmd += ['-o',str(parser)]
    subprocess.run(cmd,check=True)
    return ref,parser

def parse_pairs(parser,out,cases):
    out.mkdir(); rows=[]
    for c in cases:
        root=ET.parse(str(SUITE/(c['id']+'.xml'))).getroot(); env=root.find('env')
        visible='(:domain '+(env.findtext('info') or '')+' '+(env.findtext('err/w' if c['stage']==2 else 'err/r') or '')+')'
        e=out/(c['id']+'.env'); e.write_text(visible,encoding='utf-8')
        snaps=[]
        for mode,tag in [('it','instr'),('nt','nl')]:
            p=out/(c['id']+'.'+mode); p.write_text(root.findtext(tag),encoding='utf-8')
            r=subprocess.run([str(parser),str(SOURCE/'words.txt'),str(e),str(p),str(c['stage']),mode],
                stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
            log=r.stdout.decode('utf-8',errors='replace'); (out/(c['id']+'-'+mode+'.log')).write_text(log,encoding='utf-8')
            assert r.returncode==0,(c['id'],mode,r.returncode)
            # Give has two equivalent representations: IT literal human vs NT explicit Y.
            snap=[s for s in log.splitlines() if s.startswith('SNAP ')]
            snap=[re.sub(r'( give X=\d+, Y=)1,( CX=.* CY=)human/( useY=)1',r'\1\2/\g<3>0',s) for s in snap]
            snap=[re.sub(r'^(SNAP (?:must_info|not_info|info) \d+) in ',r'\1 inside ',s) for s in snap]
            snaps.append(snap)
        diff='\n'.join(difflib.unified_diff(snaps[0],snaps[1],fromfile='IT',tofile='NT',lineterm=''))
        (out/(c['id']+'.diff')).write_text(diff,encoding='utf-8')
        rows.append(dict(id=c['id'],semantic_equal=not diff))
        print('PARSE',c['id'],'equal',not diff,flush=True)
    (out/'comparison.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    return rows

def enrich(r,out):
    server=trace(out/'server.log'); client=trace(out/'client.log')
    events=re.findall(r'^[ \t]*\[([A-Za-z_]+)([^\r\n|\]]*)\|([^\r\n\]]*)\][ \t]*$',server,re.M)
    r['events']=[dict(action=a,args=b.strip(),reply=v.strip()) for a,b,v in events]
    assert all(e['action'] in ('Move','PickUp','PutDown','ToPlate','FromPlate','Open','Close','PutIn','TakeOut','AskLoc','Sense') for e in r['events'])
    r['actions']=dict(Counter(e['action'].lower() for e in r['events']))
    r['action_count']=len(r['events'])
    r['action_cost']=sum(4 if e['action'].lower()=='move' else 1 if e['action'].lower()=='sense' else 2 for e in r['events'])
    r['failed_actions']=[e for e in r['events'] if e['reply'].lower() in ('false','0','failed','fail')]
    r['evaluator_valid']=r['final_goals'] is not None
    if not r['evaluator_valid']: r['status']='evaluator_failed'
    r['base_score']=(40*r['final_goals']+20*r['credited_constraints']-r['action_cost']) if r['evaluator_valid'] else None
    r['efficiency_score']=r['raw_score']-r['base_score'] if r['evaluator_valid'] else None
    r['decisions']=[s for s in client.splitlines() if any(k in s for k in
        ('[MustNear]','[MustIn]','[AutoOpenClose]','[3A]','[Zero-Action]','Final-GOTO:',
         '[Preflight]','too many cons','风险系数是','Discarded','Task done','Task not done'))]
    answer=(out/'runtime/vanswer.txt').read_text(encoding='utf-8',errors='replace') if (out/'runtime/vanswer.txt').exists() else ''
    r['official_values']=sorted(set((int(i),int(v)) for i,v in re.findall(r'value\((\d+),(\d+)\)',answer)))
    r['output']=str(out.relative_to(ROOT))
    r['event_parser']='single-line canonical server action stream v1'
    # summary.json is derived data too; keep its counters consistent with trace.json.
    summary_path=out/'summary.json'
    summary=json.loads(summary_path.read_text(encoding='utf-8'))
    summary.update(actions=r['actions'],action_count=r['action_count'],event_parser=r['event_parser'])
    summary_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    return r

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--sdk',type=Path,default=Path('/home/yifan/env-release-2026'))
    ap.add_argument('--output',type=Path,required=True); ap.add_argument('--reuse-build',type=Path)
    ap.add_argument('--analyze-only',action='store_true'); args=ap.parse_args()
    if args.analyze_only:
        out=args.output.resolve(); rows=json.loads((out/'suite.json').read_text(encoding='utf-8'))
        for r in rows:
            runout=ROOT/r['output']; enrich(r,runout)
            (runout/'trace.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
        (out/'suite.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
        print('Reanalyzed',len(rows),'unchanged raw server/client logs'); return
    assert Path('/etc/os-release').exists() and 'VERSION_ID="18.04"' in Path('/etc/os-release').read_text()
    with socket.socket() as p: p.bind(('127.0.0.1',7932))
    check(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False)
    (out/'.gitattributes').write_text('* -text\n',encoding='utf-8')
    (out/'.gitignore').write_text('build-fixed/example\nreference-client\nparse-snapshot\nseed_rng.so\n**/runtime/iclingo\n',encoding='utf-8')
    source_hashes={p.name:digest(p) for p in SOURCE.iterdir() if p.suffix in ('.cpp','.hpp','.txt')}
    metadata=dict(release=Path('/etc/os-release').read_text(),kernel=subprocess.check_output(['uname','-a']).decode(),
        compiler=subprocess.check_output(['g++','--version']).decode(),sdk=str(args.sdk),limit_ms=5000,
        solver='src1.3.3-fixed',source_sha256=source_hashes,rule_basis='2025 local PDFs',
        case_sha256={p.name:digest(p) for p in sorted(SUITE.glob('*.xml'))})
    (out/'environment.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    if args.reuse_build:
        old=args.reuse_build.resolve()
        assert json.loads((old/'build-fixed/build.json').read_text())['source_sha256']==source_hashes
        (out/'build-fixed').mkdir()
        for name in ('example','build.json','build.log'):
            shutil.copy2(str(old/'build-fixed'/name),str(out/'build-fixed'/name))
        for name in ('reference-client','parse-snapshot'):
            shutil.copy2(str(old/name),str(out/name))
        exe=out/'build-fixed/example'; ref=out/'reference-client'; parser=out/'parse-snapshot'
        print('REUSE verified unchanged builds',flush=True)
    else:
        print('BUILD fixed',flush=True); exe=build('src1.3.3-fixed',args.sdk,out/'build-fixed')
        print('BUILD witness and parse snapshot',flush=True); ref,parser=compile_extra(args.sdk,out)
    cases=json.loads((SUITE/'manifest.json').read_text(encoding='utf-8'))
    parse_pairs(parser,out/'parse',cases)
    seed_dir=Path(tempfile.mkdtemp(prefix='liuyifan10-seed-'))
    shim=seed_dir/'seed_rng.so'
    subprocess.run(['g++','-shared','-fPIC',str(SOURCE/'tests/seed_rng.cpp'),'-ldl','-o',str(shim)],check=True)
    shutil.copy2(str(shim),str(out/'seed_rng.so'))
    rows=[]
    schedules=[('reference','natural',[c for c in cases],['it']),('fixed','natural',cases,['it','nt'])]
    schedules += [('fixed',str(seed),[c for c in cases if c['stage']==2],['it','nt']) for seed in (20260924,20260925)]
    for who,seed,selected,modes in schedules:
        if seed=='natural':
            os.environ.pop('LD_PRELOAD',None); os.environ.pop('RDFW_TEST_SEED',None)
        else:
            os.environ['LD_PRELOAD']=str(shim); os.environ['RDFW_TEST_SEED']=seed
        for c in selected:
            for mode in modes:
                key='{}-{}-{}-{}'.format(who,seed,c['id'],mode); runout=out/key
                if who=='reference': os.environ['LIUYIFAN_REFERENCE_PLAN']=str(SUITE/'reference-plans'/(c['id']+'.txt'))
                else: os.environ.pop('LIUYIFAN_REFERENCE_PLAN',None)
                r=run_case(args.sdk,SOURCE,ref if who=='reference' else exe,SUITE/(c['id']+'.xml'),c['stage'],mode,runout,5000,None)
                r.update(id=c['id'],who=who,seed=seed,title=c['title'])
                enrich(r,runout)
                if seed!='natural':
                    assert '[RDFW_TEST_SEED] '+seed in trace(runout/'server.log')
                if who=='reference':
                    assert r['status']=='ok' and r['final_goals']==c['expected_goals'] and r['credited_constraints']==c['expected_constraints'],r
                (runout/'trace.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
                rows.append(r); (out/'suite.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
                print(key,r['status'],r['raw_score'],'goals',r['final_goals'],'cons',r['credited_constraints'],'actions',r['action_count'],flush=True)
    assert source_hashes=={p.name:digest(p) for p in SOURCE.iterdir() if p.suffix in ('.cpp','.hpp','.txt')}
    (out/'source-unchanged.json').write_text(json.dumps(dict(verified=True,source_sha256=source_hashes),indent=2),encoding='utf-8')
    print('COMPLETE',len(rows),'official runs',flush=True)

if __name__=='__main__': main()
