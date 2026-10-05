"""Development latency observations from executed receipts, never hypothetical labels.

Use only repeat 0 to fit descriptive estimates. Keep every executed outcome,
including failures; repeats remain separate diagnostic evidence. Does not modify
robot inputs or produce a probability calibration claim.
"""
from pathlib import Path
import argparse,collections,hashlib,json,math,statistics,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];LAB=ROOT/'experiments/full_probability'

def describe(values):
    if not values:return dict(count=0,median_ms=None,p90_ms=None,mean_ms=None,min_ms=None,max_ms=None)
    ordered=sorted(values)
    return dict(count=len(values),median_ms=statistics.median(values)/1e6,
        p90_ms=ordered[max(0,int(math.ceil(.9*len(values)))-1)]/1e6,
        mean_ms=sum(values)/len(values)/1e6,min_ms=ordered[0]/1e6,max_ms=ordered[-1]/1e6)

def main():
    p=argparse.ArgumentParser();p.add_argument('checkpoint');p.add_argument('--suite',default='smoke2-full');a=p.parse_args()
    journal=LAB/(a.checkpoint+'-'+a.suite+'.jsonl')
    rows=[json.loads(line) for line in journal.read_text().splitlines() if line]
    audit=json.loads((LAB/(a.checkpoint+'-'+a.suite+'-receipts.json')).read_text())
    assert not audit['failed_runs'],'Latency fitting requires complete SDK receipt audit'
    hashes={row['key']:row['log_sha256'] for row in audit['runs']}
    outcomes=collections.defaultdict(list);actions=collections.defaultdict(list);source=[];all_values=[]
    for row in rows:
        if row['arm']!='lab' or row['repeat']!=0:continue
        raw=(LAB/'runs'/row['key']/'client.log').read_bytes();digest=hashlib.sha256(raw).hexdigest()
        assert hashes[row['key']]==digest,'Receipt audit is stale'
        receipts=[]
        for line in raw.decode('utf8',errors='replace').splitlines():
            if '[ExecutionEvidence] {' in line:
                r=json.loads(line.split('[ExecutionEvidence] ',1)[1])
                if r['event']=='finalized':receipts.append(r)
        assert [r['id'] for r in receipts]==list(range(1,len(receipts)+1))
        for r in receipts:
            ns=r['sdk_ns'];assert isinstance(ns,int) and ns>=0
            outcomes[r['action']+'/'+r['outcome']].append(ns);actions[r['action']].append(ns);all_values.append(ns)
        source.append(dict(key=row['key'],log_sha256=digest,executed_receipts=len(receipts)))
    result=dict(checkpoint=a.checkpoint,suite=a.suite,repeat=0,source_journal_sha256=hashlib.sha256(journal.read_bytes()).hexdigest(),
        observations=source,all=describe(all_values),actions={k:describe(v) for k,v in sorted(actions.items())},
        outcomes={k:describe(v) for k,v in sorted(outcomes.items())},
        scope='executed development SDK durations only; unexecuted candidates have no labels; model computation and dispatch excluded; first repeats only; descriptive unvalidated estimates, not a hard deadline bound or a calibrated probability')
    output=LAB/(a.checkpoint+'-'+a.suite+'-sdk-latency.json');assert not output.exists(),'Frozen latency evidence already exists'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(all=result['all'],actions=result['actions'],outcomes=result['outcomes']),ensure_ascii=False))

if __name__=='__main__':main()
