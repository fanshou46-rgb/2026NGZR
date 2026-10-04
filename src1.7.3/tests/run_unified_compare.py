#!/usr/bin/env python3
"""Default/default paired official evaluation; no deletions, no selective reruns."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import zipfile

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1]
ROOT = SOURCE.parent
BASELINE = ROOT / 'src1.6.7-200ms'
sys.path.insert(0, str(SOURCE / 'tests'))
from compare_legal import build
from run_guarded_compare import load_runner, base_score

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def product(source):
    return {p.name: sha(p) for p in source.iterdir() if p.suffix in ('.cpp','.hpp','.txt')}

def cases():
    rows = json.loads((ROOT / 'src1.6.7/test-results/validation-20260928/full-release-results.json').read_text())
    items = {}
    for row in rows:
        if row['mode'] == 'it':
            p = Path(row['case'])
            assert p.exists(), p
            items[str(p)] = dict(path=str(p), stage=row['stage'], suite='release')
    for number in range(1,37):
        if number in (2,4,5): continue
        p = ROOT / '题目/realcompetiton_2024' / ('%02d.xml' % number)
        flags = dict(re.findall(r'(mis|err|ans)="(on|off)"', re.search(r'<env\s+([^>]+)>',p.read_text()).group(1)))
        stage = 1 if all(flags.get(k) == 'off' for k in ('mis','err','ans')) else 2
        items[str(p)] = dict(path=str(p), stage=stage, suite='realcompetition')
    p = SOURCE / 'tests/fixtures/unified/01-no-positive-prefix.xml'
    items[str(p)] = dict(path=str(p), stage=1, suite='unified')
    result = sorted(items.values(), key=lambda v: (v['suite'],v['path']))
    assert len(result) == 71, len(result)
    for i,v in enumerate(result): v.update(id='c%03d' % (i+1),sha256=sha(Path(v['path'])))
    return result

def summarize(out, rows):
    fields = ('official_score','base','final_goals','credited_constraints','action_cost')
    summary = {}
    for scope in ('all','stage1','stage2','it','nt','round1','round2'):
        part = [r for r in rows if scope == 'all' or scope == 'stage'+str(r['stage']) or
                scope == r['mode'] or scope == 'round'+str(r['round'])]
        item = {'pairs':len(part)}
        for arm in ('baseline','current'):
            values = [r[arm] for r in part]
            item[arm] = {k:sum(v[k] or 0 for v in values) for k in fields}
            item[arm].update(timeouts=sum(v['platform_timed_out'] or v['external_timeout'] for v in values),
                failures=sum(v['status'] != 'ok' for v in values),unscored=sum(v['official_score'] is None for v in values),
                seconds=sum(v['platform_seconds'] or 0 for v in values))
        for k in ('official_score','base','final_goals'):
            delta = [(r['current'][k] or 0)-(r['baseline'][k] or 0) for r in part]
            item[k+'_pairs'] = dict(improved=sum(d>0 for d in delta),equal=sum(d==0 for d in delta),
                worsened=sum(d<0 for d in delta),delta=sum(delta))
        item['same_action_pairs'] = sum(r['baseline']['action_sequence']==r['current']['action_sequence'] for r in part)
        summary[scope] = item
    save(out/'summary.json',summary)
    regressions = [r for r in rows if any((r['current'][k] or 0)<(r['baseline'][k] or 0)
        for k in ('official_score','base','final_goals')) or
        (r['current']['platform_timed_out'] or r['current']['external_timeout']) and
        not (r['baseline']['platform_timed_out'] or r['baseline']['external_timeout'])]
    save(out/'regressions.json',regressions)
    columns = ['id','case','stage','mode','round','order','score_old','score_new','base_old','base_new',
        'G_old','G_new','C_old','C_new','K_old','K_new','seconds_old','seconds_new','timeout_old','timeout_new','same_actions']
    with (out/'pairs.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.writer(stream); writer.writerow(columns)
        for r in rows:
            a,b=r['baseline'],r['current']
            writer.writerow([r['id'],r['path'],r['stage'],r['mode'],r['round'],r['order']]+[
                v[k] for k in fields+('platform_seconds',) for v in (a,b)]+[
                a['platform_timed_out'] or a['external_timeout'], b['platform_timed_out'] or b['external_timeout'],
                a['action_sequence']==b['action_sequence']])
    return summary,regressions

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--sdk',type=Path,default=Path('/home/yifan/env-release-2026'))
    p.add_argument('--rounds',type=int,default=2)
    args=p.parse_args(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False)
    selected=cases(); fingerprints={v:product(path) for v,path in [('baseline',BASELINE),('current',SOURCE)]}
    save(out/'input-audit.json',dict(products=fingerprints,cases=selected,seed=20260924,rounds=args.rounds,
        deadline_ms=5000,policy='both normal default, no mode environment, serial alternating AB/BA, retain every run',
        exclusions={'02':'existing malformed XML','04/05':'existing official scoring failures'},
        os=subprocess.check_output(['uname','-a']).decode(),compiler=subprocess.check_output(['g++','--version']).decode()))
    executables={}
    for arm,version in [('baseline',BASELINE.name),('current',SOURCE.name)]:
        print('BUILD',arm,flush=True); executables[arm]=build(version,args.sdk,out/('build-'+arm))
    assets=out/'assets'; assets.mkdir()
    (assets/'words.txt').write_bytes((BASELINE/'words.txt').read_bytes().replace(b'\r\n',b'\n'))
    seed=Path('/tmp/rdfw17-seed-%d.so' % os.getpid())
    subprocess.run(['g++','-shared','-fPIC',str(SOURCE/'tests/seed_rng.cpp'),'-ldl','-o',str(seed)],check=True)
    os.environ.update(LD_PRELOAD=str(seed),RDFW_TEST_SEED='20260924',RDFW_STAGE_TIMING='0')
    os.environ.pop('RDFW_TASK_GROUP_MODE',None)
    runner=load_runner(ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py')
    rows=[]; total=len(selected)*2*args.rounds
    for round_id in range(1,args.rounds+1):
        for item in selected:
            for mode in ('it','nt'):
                order=['baseline','current'] if (len(rows)+round_id)%2 else ['current','baseline']
                row=dict(item,mode=mode,round=round_id,order='/'.join(order))
                for arm in order:
                    run=out/'runs'/('r%d-%s-%s-%s' % (round_id,item['id'],mode,arm))
                    result=runner(args.sdk,assets,executables[arm],Path(item['path']),item['stage'],mode,run,5000,None)
                    result['output']=str(run); result['base']=base_score(result)
                    text=(run/'server.log').read_text(errors='replace')
                    client=(run/'client.log').read_text(errors='replace')
                    result['seed_confirmed']='[RDFW_TEST_SEED] 20260924' in text
                    assert result['seed_confirmed'],run
                    actions=re.findall(r'^\s*\[([A-Za-z_]+)(?:\s[^|]*)?\|',text,re.M)
                    result['action_cost']=sum(4 if a.lower()=='move' else 1 if a.lower()=='sense' else 2 for a in actions)
                    result['action_sequence']=re.findall(r'^\s*\[([A-Za-z_]+(?:\s+[^|]*?)?)\|',text,re.M)
                    result['decisions']=[re.sub(r'\x1b\[[0-9;]*m','',line) for line in client.splitlines()
                        if any(t in line for t in ('[Scheduler]','[GuardedDecision]','[Deadline]','[3A][final]'))]
                    row[arm]=result
                rows.append(row); save(out/'results.json',rows)
                if len(rows)%10==0: summarize(out,rows)
                a,b=row['baseline'],row['current']
                print('%d/%d r%d %s %s G %s->%s base %s->%s official %s->%s' %
                    (len(rows),total,round_id,Path(item['path']).name,mode,a['final_goals'],b['final_goals'],
                    a['base'],b['base'],a['official_score'],b['official_score']),flush=True)
    assert fingerprints=={v:product(path) for v,path in [('baseline',BASELINE),('current',SOURCE)]}
    assert all(sha(Path(v['path']))==v['sha256'] for v in selected)
    save(out/'final-audit.json',dict(products_unchanged=True,inputs_unchanged=True,completed_pairs=len(rows),
        binaries={k:sha(v) for k,v in executables.items()},harness_sha256=sha(Path(__file__)),seed_sha256=sha(seed)))
    summarize(out,rows)
    with zipfile.ZipFile(str(out/'raw-evidence.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        shared=next((out/'runs').glob('*/runtime/iclingo'))
        shared_hash=sha(shared)
        z.write(str(shared),'shared-sdk/iclingo')
        for path in sorted((out/'runs').rglob('*')):
            if path.is_file():
                if path.name=='iclingo':
                    assert sha(path)==shared_hash, path
                else:
                    z.write(str(path),str(path.relative_to(out)))
        z.writestr('shared-sdk/manifest.json',json.dumps(dict(
            iclingo_sha256=shared_hash,policy='Identical per-run iclingo stored once; every log, input and ASP output retained.'),indent=2))
    print('COMPLETE',out,flush=True)

if __name__=='__main__': main()
