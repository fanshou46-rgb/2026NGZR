#!/usr/bin/env python3
import argparse, collections, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OLD=Path('/tmp/rdfw17-final-paired-20261002')
NEW=Path('/tmp/rdfw171-tail-final-20261003')
DIRECT=Path('/tmp/rdfw-direct-167200-171-20261003')

def load(p): return json.loads(p.read_text())
def clean(p): return re.sub(r'\x1b\[[0-9;]*m','',p.read_text(errors='replace'))
def prior():
    old=load(OLD/'results.json'); new={ (r['id'],r['mode'],r['round']):r for r in load(NEW/'results.json') if r['suite']=='legacy'}
    return [dict(r, current=new[(r['id'],r['mode'],r['round'])]['current']) for r in old]

def profile(r,verbose=False):
    print('\nPAIR',r['id'],r['mode'],r['round'],r['stage'],r['path'])
    for arm in ('baseline','current'):
        v=r[arm]; print(arm,{k:v.get(k) for k in ('final_goals','credited_constraints','base','action_cost','official_score','platform_seconds','status')})
        run=Path(v['output']); s=clean(run/'server.log'); c=clean(run/'client.log')
        if verbose:
            print('SERVER',s)
            print('TASKS', (run/'runtime/vtask.lp').read_text())
            print('CONSTRAINTS',(run/'runtime/vcons.lp').read_text())
            print('FINAL',(run/'runtime/vanswer.txt').read_text())
        for n,line in enumerate(c.splitlines(),1):
            if any(t in line for t in ('[Scheduler]','[3A][final]','[TradeoffDecision]','legacy_choice=true','[Recovery','[Terminal','[3B][Deadline]','[Probe]')):
                if not verbose and '[Probe]' in line and not any(t in line for t in ('"event":"stop"','"event":"execute"','"event":"replan"','blocked_task')): continue
                print('L%d'%n,line)

def brief(r):
    print('\nPAIR',r['id'],r['mode'],r['round'],Path(r['path']).name)
    seq=[r[a]['action_sequence'] for a in ('baseline','current')]; i=0
    while i<min(map(len,seq)) and seq[0][i]==seq[1][i]: i+=1
    print('FIRST ACTION DIFF',i+1,'shared',seq[0][:i][-4:],'old',seq[0][i:i+9],'new',seq[1][i:i+9])
    for arm in ('baseline','current'):
        v=r[arm];run=Path(v['output']);lines=clean(run/'client.log').splitlines()
        print(arm,'G/C/B/K',*[v.get(k) for k in ('final_goals','credited_constraints','base','action_cost')])
        print('FINAL',re.findall(r'value\(\d+,\d+\)',(run/'runtime/vanswer.txt').read_text()))
        picks=[(n,l) for n,l in enumerate(lines,1) if '[3B][Candidate]' in l and 'legacy_choice=true' in l]
        print('LEGACY selections',[(n,re.search(r'task_index=(\d+).*?eligible=(\w+).*?complete=(\w+)',l).groups()) for n,l in picks])
        trade=[(n,l) for n,l in enumerate(lines,1) if '[TradeoffDecision]' in l and ('decision=execute' in l or 'requires_verified_group' in l)]
        print('TRADE sample',trade[:2],trade[-2:])
        sched=[(n,l) for n,l in enumerate(lines,1) if '[Scheduler] greedy' in l or '[Scheduler] stop' in l or '[3A][final]' in l]
        print('SCHED',sched[:3],sched[-4:])
        pe=[(n,json.loads(l.split('[Probe] ',1)[1])) for n,l in enumerate(lines,1) if '[Probe] ' in l]
        print('PROBE_COUNTS',dict(collections.Counter((e['event'],e.get('reason','')) for _,e in pe if e['event'] in ('stop','execute','candidate','replan'))))
        print('BLOCKING',[(n,e['reason']) for n,e in pe if e['event']=='blocking_fact'][:6])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--id');p.add_argument('--mode',default='it');p.add_argument('--round',type=int,default=1);p.add_argument('--direct',action='store_true');p.add_argument('--verbose',action='store_true');p.add_argument('--summary',action='store_true');p.add_argument('--brief',action='store_true');a=p.parse_args()
    rows=load(DIRECT/'results.json') if a.direct else prior()
    if a.summary:
        part=[r for r in rows if r['stage']==2 and r['baseline']['final_goals']>r['current']['final_goals']]
        print('negative',len(part),'unique',len(set(r['id'] for r in part)))
        for r in part:
            print(r['id'],r['mode'],r['round'],Path(r['path']).name,'G',r['baseline']['final_goals'],r['current']['final_goals'],'B',r['baseline']['base'],r['current']['base'])
    elif a.id:
        r=next(r for r in rows if r['id']==a.id and r['mode']==a.mode and r['round']==a.round)
        brief(r) if a.brief else profile(r,a.verbose)
    elif a.brief:
        for r in rows:
            if r['stage']==2 and r['baseline']['final_goals']>r['current']['final_goals'] and r['mode']=='it' and r['round']==1: brief(r)
