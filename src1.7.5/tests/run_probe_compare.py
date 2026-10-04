#!/usr/bin/env python3
"""Paired default/default SDK validation. Fresh output only; retain every result."""
import argparse
import collections
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1]
ROOT = SOURCE.parent
BASELINE = ROOT / 'src1.7.4'
SDK = Path('/home/yifan/env-release-2026')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def fingerprints(source):
    # Prune evidence before walking it: the files are excluded from product
    # hashes, and visiting tens of thousands of SDK outputs adds minutes on WSL.
    result={}
    for directory, children, files in os.walk(str(source)):
        children[:]=[name for name in children if name!='test-results']
        for name in files:
            path=Path(directory)/name
            if path.suffix in ('.cpp','.hpp','.h','.txt','.py','.sh'):
                result[path.relative_to(source).as_posix()]=sha(path)
    return result

def matching_input(path, expected):
    return path.is_file() and (sha(path)==expected or
        hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n")).hexdigest()==expected)

def cases(suite):
    result = []
    if suite in ('all', 'legacy'):
        audit = json.loads((ROOT/'src1.7/test-results/validation-20261002/input-audit.json').read_text())
        for item in audit['cases']:
            old = Path(item['path'])
            relative = old.as_posix().split('/2026NGZR/', 1)[1]
            candidates = [ROOT/relative]
            if relative.startswith('src1.6.'):
                candidates += [ROOT/'HistoryVersion'/relative, BASELINE/'tests'/relative.split('/tests/', 1)[1]]
            path = next((p for p in candidates if matching_input(p,item['sha256'])), None)
            assert path, (relative, item['sha256'])
            result.append(dict(item, path=str(path), sha256=sha(path), upstream_sha256=item['sha256'], kind='scored', suite='legacy'))
    if suite in ('all', 'comprehensive', 'invalid'):
        directory = ROOT/'题目/2026_comprehensive_200'
        catalogue = json.loads((directory/'catalogue.json').read_text())
        for item in catalogue['cases']:
            if suite=='invalid' and item['kind']!='invalid': continue
            if suite=='comprehensive' and item['kind']=='invalid': continue
            path = directory/item['path']
            assert matching_input(path,item['sha256']), path
            result.append(dict(id=item['id'], path=str(path), sha256=sha(path),
                stage=item.get('stage', 1), kind='invalid' if item['kind']=='invalid' else 'scored',
                expected_layer=item.get('expected_layer'), mutation=item.get('mutation'), suite='comprehensive'))
    return result

def build(source, out, sdk):
    out.mkdir()
    executable = out/'example'
    command = ['g++', '-std=c++11', '-O2', '-g', '-Wall', '-Wextra', '-I'+str(source),
               '-I'+str(sdk/'include'), '-I'+str(sdk/'src')]
    command += [str(p) for p in sorted(source.glob('*.cpp'))]
    command += ['-L'+str(sdk/'lib'), '-lframe', '-lutility', '-lboost_thread', '-lboost_system',
                '-lboost_chrono', '-lboost_date_time', '-lboost_regex', '-lpthread', '-ldl', '-o', str(executable)]
    with (out/'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    save(out/'build.json', dict(command=command, binary_sha256=sha(executable), sources=fingerprints(source)))
    return executable

def extract(run, value, seed):
    client = (run/'client.log').read_text(errors='replace') if (run/'client.log').exists() else ''
    server = (run/'server.log').read_text(errors='replace') if (run/'server.log').exists() else ''
    clean = re.sub(r'\x1b\[[0-9;]*m', '', client)
    value['action_sequence'] = re.findall(r'^\s*\[([A-Za-z_]+(?:\s+[^|]*?)?)\|', server, re.M)
    names = [a.split()[0].lower() for a in value['action_sequence']]
    value['action_cost'] = sum(4 if a=='move' else 1 if a=='sense' else 2 for a in names)
    g,c = value.get('final_goals'), value.get('credited_constraints')
    value['base'] = 40*g+(20*c if g else 0)-value['action_cost'] if g is not None and c is not None else None
    value['seed_confirmed'] = ('[RDFW_TEST_SEED] '+str(seed)) in server
    value['probe_events'] = []
    for line in clean.splitlines():
        if '[Probe] ' in line:
            value['probe_events'].append(json.loads(line.split('[Probe] ',1)[1]))
    value['decisions'] = [line for line in clean.splitlines() if any(s in line for s in
        ('[Scheduler]', '[GuardedDecision]', '[3A][final]', '[3B][Deadline]'))]
    value['early_stop'] = any('reason=no_qualified_positive_single' in line for line in value['decisions']) and any(
        int(ms)>=300 for ms in re.findall(r'greedy task=18446744073709551615 marginal=0 remaining_ms=(\d+)', clean))
    value['legacy_production_execution'] = 'legacy_must_choose_one_risk' in clean
    value['output'] = str(run)
    return value

def summary(out, rows):
    result = {}
    for scope in ('all', 'stage1', 'stage2', 'legacy', 'comprehensive', 'invalid'):
        part = [r for r in rows if scope=='all' or scope=='stage'+str(r['stage']) and r['kind']=='scored'
                or scope==r['suite'] or scope==r['kind']]
        scored = [r for r in part if r['kind']=='scored']
        item = dict(pairs=len(part), scored_pairs=len(scored))
        for arm in ('baseline','current'):
            item[arm] = {k:sum(r[arm].get(k) or 0 for r in scored) for k in
                ('official_score','base','final_goals','credited_constraints','action_cost')}
            item[arm].update(timeouts=sum(bool(r[arm].get('platform_timed_out') or r[arm].get('external_timeout')) for r in scored),
                failures=sum(r[arm].get('status')!='ok' for r in scored), unscored=sum(r[arm].get('official_score') is None for r in scored))
        item['same_actions'] = sum(r['baseline']['action_sequence']==r['current']['action_sequence'] for r in scored)
        item['base_pairs'] = dict(improved=sum((r['current']['base'] or 0)>(r['baseline']['base'] or 0) for r in scored),
            worsened=sum((r['current']['base'] or 0)<(r['baseline']['base'] or 0) for r in scored))
        events = [e for r in part for e in r['current']['probe_events']]
        feedback = [e for e in events if e['event']=='feedback']
        replans = [e for e in events if e['event']=='replan']
        rejected = collections.Counter(e['reason'] for e in events if e['event'] in ('candidate','execution_rejected') and not e.get('eligible',False))
        item['probes'] = dict(total=len(feedback), related_information=sum(e['related_new_evidence'] for e in feedback),
            effective=sum(e['effective'] for e in replans), no_information=sum(not e['effective'] for e in replans),
            task_candidate_restored=sum(bool(e['restored_tasks']) for e in replans), rejected=dict(rejected))
        early = [r for r in scored if r['stage']==2 and r['baseline']['early_stop']]
        item['early_stop_recovery'] = dict(eligible_pairs=len(early), recovered_pairs=sum(any(
            e['event']=='replan' and e['restored_tasks'] for e in r['current']['probe_events']) for r in early))
        result[scope] = item
    save(out/'summary.json',result)
    save(out/'regressions.json',[r for r in rows if r['kind']=='scored' and any(
        (r['current'].get(k) or 0)<(r['baseline'].get(k) or 0) for k in ('official_score','base','final_goals'))])
    save(out/'stage1-differences.json',[r for r in rows if r['kind']=='scored' and r['stage']==1 and
        (r['baseline']['action_sequence']!=r['current']['action_sequence'] or r['baseline']['base']!=r['current']['base'])])
    return result

def sdk_model(sdk):
    return {str(p.relative_to(sdk)):sha(p) for directory in ('src','include','res')
            for p in sorted((sdk/directory).rglob('*')) if p.is_file() and p.suffix in ('.cpp','.hpp','.h','.lp')}

def main():
    global BASELINE
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True); p.add_argument('--sdk',type=Path,default=SDK)
    p.add_argument('--baseline-source',type=Path,default=BASELINE); p.add_argument('--baseline-build',type=Path); p.add_argument('--current-build',type=Path);
    p.add_argument('--rounds',type=int,default=2); p.add_argument('--suite',choices=('all','legacy','comprehensive','invalid'),default='all')
    p.add_argument('--seed',type=int,default=20260924); p.add_argument('--limit',type=int); p.add_argument('--ids',nargs='*')
    args=p.parse_args(); BASELINE=args.baseline_source.resolve(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False)
    selected=cases(args.suite)
    if args.ids: selected=[c for c in selected if c['id'] in args.ids]
    if args.limit: selected=selected[:args.limit]
    with socket.socket() as port:
        port.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        port.bind(('127.0.0.1',7932))
    audits={'baseline':fingerprints(BASELINE),'current':fingerprints(SOURCE)}
    sdk_sources=sdk_model(args.sdk)
    save(out/'sdk-model-audit.json',sdk_sources)
    save(out/'input-audit.json',dict(products=audits,cases=selected,seed=args.seed,rounds=args.rounds,
        deadline_ms=5000,policy='default/default, serial alternating AB/BA, IT/NT, no deletion or selective rerun',
        compiler=subprocess.check_output(['g++','--version']).decode(),os=subprocess.check_output(['uname','-a']).decode(),
        sdk={str(f):sha(f) for f in [args.sdk/'bin/cserver',args.sdk/'lib/libasp.so',args.sdk/'lib/libframe.a']}))
    executables={}
    for arm,source in [('baseline',BASELINE),('current',SOURCE)]:
        reuse=getattr(args,arm+'_build')
        if reuse:
            metadata=json.loads((reuse/'build.json').read_text())
            assert metadata['sources']==fingerprints(source), 'reuse source mismatch'
            assert metadata['binary_sha256']==sha(reuse/'example'), 'reuse binary mismatch'
            executables[arm]=(reuse/'example').resolve()
            save(out/('reused-'+arm+'.json'),dict(path=str(reuse.resolve()),metadata=metadata))
        else: executables[arm]=build(source,out/('build-'+arm),args.sdk)
    seed=out/'seed.so'; subprocess.run(['g++','-shared','-fPIC',str(SOURCE/'tests/seed_rng.cpp'),'-ldl','-o',str(seed)],check=True)
    os.environ.update(LD_PRELOAD=str(seed),RDFW_TEST_SEED=str(args.seed),RDFW_STAGE_TIMING='0'); os.environ.pop('RDFW_TASK_GROUP_MODE',None)
    assets=out/'assets'; assets.mkdir(); (assets/'words.txt').write_bytes((BASELINE/'words.txt').read_bytes().replace(b'\r\n',b'\n'))
    spec=importlib.util.spec_from_file_location('baseline_runner',str(ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py'))
    runner=importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
    rows=[]
    for round_id in range(1,args.rounds+1):
        for case in selected:
            for mode in ('it','nt'):
                order=['baseline','current'] if (len(rows)+round_id)%2 else ['current','baseline']
                row=dict(case,mode=mode,round=round_id,order='/'.join(order))
                for arm in order:
                    run=out/'runs'/('r%d-%s-%s-%s'%(round_id,case['id'],mode,arm))
                    try:
                        value=runner.run_case(args.sdk,assets,executables[arm],Path(case['path']),case['stage'],mode,run,5000,None)
                    except Exception as error:
                        value=dict(status='harness_or_platform_rejected',error=str(error),official_score=None,raw_score=None,
                            final_goals=None,credited_constraints=None,platform_timed_out=False,external_timeout=False)
                        save(run/'failure.json',value)
                    row[arm]=extract(run,value,args.seed)
                    if case['kind']=='scored': assert row[arm]['seed_confirmed'], run
                rows.append(row); save(out/'results.json',rows)
                if len(rows)%10==0: summary(out,rows)
                print('%d/%d r%d %s %s G %s->%s base %s->%s probes=%d'%(len(rows),len(selected)*2*args.rounds,round_id,
                    case['id'],mode,row['baseline'].get('final_goals'),row['current'].get('final_goals'),
                    row['baseline']['base'],row['current']['base'],sum(e['event']=='feedback' for e in row['current']['probe_events'])),flush=True)
    assert audits=={'baseline':fingerprints(BASELINE),'current':fingerprints(SOURCE)}, 'sources changed during comparison'
    assert all(sha(Path(c['path']))==c['sha256'] for c in selected)
    assert sdk_sources==sdk_model(args.sdk), 'SDK model changed during comparison'
    violations=[]
    for r in rows:
        executes=[e for e in r['current']['probe_events'] if e['event']=='execute']; seen=set(); counts=collections.Counter()
        for e in executes:
            key=(e['signature'],e['world_revision']); counts[e['signature']]+=1
            if (key in seen and e['kind']!='AskLoc') or counts[e['signature']]>(3 if e['kind']=='AskLoc' else 2) or (e['constraint_result']!='constraint_safe' and not (e['constraint_result']=='bounded_score_trade' and e.get('constraint_risk_count',99)<=2 and e.get('authorized_constraint_risk_count',99)<=2 and e.get('expected_gain',-1)>0)): violations.append((r['id'],r['mode'],r['round'],'probe_authorization'))
            seen.add(key)
        if len(executes)>8 or r['stage']==1 and executes or r['current']['legacy_production_execution']: violations.append((r['id'],r['mode'],r['round'],'execution_boundary'))
    save(out/'final-audit.json',dict(products_unchanged=True,inputs_unchanged=True,sdk_model_unchanged=True,pairs=len(rows),
        binaries={a:sha(e) for a,e in executables.items()},violations=violations))
    summary(out,rows); print('COMPLETE',out,flush=True)

if __name__=='__main__': main()
