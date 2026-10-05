"""Locate the first public feedback or decision divergence in every SDK repeat.

This diagnoses real executions; equal public histories do not certify equal
wall-clock inputs or a calibrated hidden-state model. Never rerun or filter.
"""
from pathlib import Path
import argparse, hashlib, json, re

ROOT=Path(__file__).resolve().parents[2]; LAB=ROOT/'experiments/full_probability'
ANSI=re.compile(r'\x1b\[[0-9;]*m')

def fields(line):
    return dict(re.findall(r'(\w+)=([^\s]+)',line))

def evidence(row):
    raw=(LAB/'runs'/row['key']/'client.log').read_bytes()
    logs=ANSI.sub('',raw.decode('utf8',errors='replace')).splitlines()
    receipts=[]; policies={}; values={}; budgets={}; stops=[]
    for line in logs:
        if '[ExecutionEvidence] {' in line:
            r=json.loads(line.split('[ExecutionEvidence] ',1)[1])
            if r['event']=='finalized':receipts.append(r)
        if '[FullPolicy] {' in line:
            p=json.loads(line.split('[FullPolicy] ',1)[1]);policies[p['receipt']]=p
        if '[FullDecisionEvidence] ' in line:
            f=fields(line);values[int(f['decision'])]=f
        if '[FullModel] decision=' in line:
            f=fields(line);budgets[int(f['decision'])]=f
        if '[FullStopEvidence] ' in line:stops.append(fields(line))
    assert [r['id'] for r in receipts]==list(range(1,len(receipts)+1))
    return dict(receipts=receipts,policies=policies,values=values,budgets=budgets,
                stops=stops,log_sha256=hashlib.sha256(raw).hexdigest())

def public(r):
    return [r['action'],r['args'],r['feedback'],r['outcome'],r['status']]

def selected(e,index):
    if index>=len(e['receipts']):return dict(stop=e['stops'])
    r=e['receipts'][index];p=e['policies'].get(r['id'])
    d=p['decision'] if p else None
    return dict(receipt=public(r),policy_decision=d,canonical_before=r['before'],
                value=e['values'].get(d),budget=e['budgets'].get(d))

def main():
    p=argparse.ArgumentParser();p.add_argument('checkpoint');p.add_argument('--suite',default='smoke2-full');a=p.parse_args()
    path=LAB/(a.checkpoint+'-'+a.suite+'.jsonl')
    rows=[json.loads(s) for s in path.read_text().splitlines() if s]
    paired={}
    for r in rows:
        if r['arm']=='lab':paired.setdefault((r['id'],r['mode']),{})[r['repeat']]=r
    disagreements=[]; failures=[]; checked=0; same=0
    for key,pair in sorted(paired.items()):
        if set(pair)!={0,1}:
            failures.append(dict(case=key,reason='missing repeat'));continue
        try:
            first,second=pair[0],pair[1];x,y=evidence(first),evidence(second)
            checked+=1;ix=0
            while ix<min(len(x['receipts']),len(y['receipts'])) and public(x['receipts'][ix])==public(y['receipts'][ix]):ix+=1
            metrics={m:[first['result'].get(m),second['result'].get(m)] for m in ('final_goals','credited_constraints','action_cost','base','official_score')}
            stable=all(v[0] is not None and v[0]==v[1] for m,v in metrics.items() if m!='official_score')
            if stable and ix==len(x['receipts'])==len(y['receipts']):same+=1;continue
            kind='same_public_history_different_decision'
            if ix<min(len(x['receipts']),len(y['receipts'])):
                rx,ry=x['receipts'][ix],y['receipts'][ix]
                if (rx['action'],rx['args'])==(ry['action'],ry['args']):kind='same_command_different_public_feedback'
            if ix==len(x['receipts'])==len(y['receipts']):kind='same_public_stream_different_sdk_terminal_or_missing_score'
            history=[public(r) for r in x['receipts'][:ix]]
            disagreements.append(dict(case=key,first=first['key'],repeat=second['key'],metrics=metrics,
                common_public_receipts=ix,public_history_sha256=hashlib.sha256(json.dumps(history,separators=(',',':')).encode()).hexdigest(),
                first_divergence=kind,first_decision=selected(x,ix),repeat_decision=selected(y,ix),
                log_sha256=[x['log_sha256'],y['log_sha256']]))
        except (AssertionError,KeyError,ValueError,OSError) as error:
            failures.append(dict(case=key,reason=str(error) or 'repeat evidence assertion failed'))
    result=dict(checkpoint=a.checkpoint,suite=a.suite,checked_pairs=checked,identical_public_and_GCKB=same,
        disagreements=disagreements,failures=failures,
        scope='first public history/decision divergence of real repeats; wall-clock inputs can differ, no independent statistical sample or deterministic-policy certification')
    (LAB/(a.checkpoint+'-'+a.suite+'-repeat-evidence.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(checked_pairs=checked,identical=same,disagreements=len(disagreements),failures=len(failures))))

if __name__=='__main__':main()
