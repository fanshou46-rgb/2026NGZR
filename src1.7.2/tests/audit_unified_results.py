#!/usr/bin/env python3
"""Audit every logged greedy baseline and separate repeat/clock differences."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re

def main():
    p=argparse.ArgumentParser(); p.add_argument('output',type=Path); args=p.parse_args()
    rows=json.loads((args.output/'results.json').read_text())
    decisions=[]; errors=[]
    for row in rows:
        path=Path(row['current']['output'])/'client.log'
        candidates={}; filtered=set(); rank_order=[]
        for line in path.read_text(errors='replace').splitlines():
            m=re.search(r'\[3B\]\[Candidate\] phase=greedy-round rank=(\d+) task_index=(\d+).*marginal_score=(-?\d+)',line)
            if m:
                rank,task,gain=map(int,m.groups())
                candidates[task]=gain; rank_order.append((rank,task)); continue
            m=re.search(r'\[Scheduler\] filtered task=(\d+)',line)
            if m: filtered.add(int(m.group(1))); continue
            m=re.search(r'\[Scheduler\] greedy task=(\d+) marginal=(-?\d+)',line)
            if not m: continue
            task,gain=map(int,m.groups())
            remaining=[t for _,t in sorted(rank_order) if t not in filtered]
            expected=remaining[0] if remaining else 2**64-1
            valid=task==expected and (gain==candidates[task] if remaining else gain==0)
            value=dict(id=row['id'],case=row['path'],mode=row['mode'],round=row['round'],
                       selected=task,expected=expected,marginal=gain,candidates=len(candidates),valid=valid)
            decisions.append(value)
            if not valid: errors.append(value)
            candidates={};filtered=set();rank_order=[]
    by_key=defaultdict(list)
    for r in rows: by_key[(r['id'],r['mode'])].append(r)
    variation=[]
    for key,part in by_key.items():
        part=sorted(part,key=lambda r:r['round'])
        if len(part)<2: continue
        value=dict(id=key[0],mode=key[1],case=part[0]['path'])
        for arm in ('baseline','current'):
            a,b=part[0][arm],part[1][arm]
            value[arm]=dict(same_actions=a['action_sequence']==b['action_sequence'],
                same_base=a['base']==b['base'],official_delta=(b['official_score'] or 0)-(a['official_score'] or 0),
                time_delta=(b['platform_seconds'] or 0)-(a['platform_seconds'] or 0))
        variation.append(value)
    same_actions=[r for r in rows if r['baseline']['action_sequence']==r['current']['action_sequence']]
    pure_clock=[r for r in same_actions if all(r['baseline'][k]==r['current'][k]
        for k in ('base','final_goals','credited_constraints')) and
        r['baseline']['official_score']!=r['current']['official_score']]
    result=dict(greedy_baselines=len(decisions),errors=errors,
        same_action_pairs=len(same_actions),
        same_actions_score_change=sum(r['baseline']['official_score']!=r['current']['official_score'] for r in same_actions),
        pure_clock_score_change=len(pure_clock),
        repeated_same_seed=variation,
        interpretation='Same action/base with score changes isolates wall-time bonus. Different action traces also change observation consumption; they are not attributable solely to wall time.')
    (args.output/'selection-and-clock-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (args.output/'greedy-decisions.json').write_text(json.dumps(decisions,ensure_ascii=False,indent=2),encoding='utf-8')
    print('greedy_baselines',len(decisions),'errors',len(errors),'same_action_pairs',len(same_actions))
    assert not errors, errors[:3]

if __name__=='__main__': main()
