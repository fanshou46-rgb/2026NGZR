"""Descriptive prediction errors on audited EXECUTED primary SDK receipts only."""
from pathlib import Path
import argparse,collections,hashlib,json,math
from verify_receipts import ANSI,observed_branch
ROOT=Path(__file__).resolve().parents[2];LAB=ROOT/'experiments/full_probability'

def receipt_predictions(text):
    nodes={};selected={};receipts=[]
    for line in ANSI.sub('',text).splitlines():
        if '[FullPolicyCatalogue] {' in line:
            c=json.loads(line.split('[FullPolicyCatalogue] ',1)[1]);index={}
            def walk(node):
                if node.get('stop') is True:return
                index[len(index)+1]=node
                for branch in node['children']:walk(branch['node'])
            walk(c['root']);nodes[c['decision']]=index
        if '[FullPolicy] {' in line:
            p=json.loads(line.split('[FullPolicy] ',1)[1]);assert p['schema']=='full_policy.v2'
            assert p['receipt'] not in selected
            selected[p['receipt']]=nodes[p['decision']][p['node']]
        if '[ExecutionEvidence] {' in line:
            r=json.loads(line.split('[ExecutionEvidence] ',1)[1])
            if r['event']=='finalized':receipts.append(r)
    result=[]
    for r in receipts:
        if r['status']!='committed' or r['outcome'] not in ('succeeded','failed','observed'):
            result.append(dict(receipt=r['id'],labeled=False,reason='no_determinate_committed_sdk_reply'));continue
        node=selected[r['id']];assert node['action']==r['action'] and node['args']==r['args']
        child=observed_branch(node,r)
        mass=sum(b['probability'] for b in node['children'] if b['node'] is child) if child is not None else 0.0
        assert 0<=mass<=1+1e-7
        value=dict(receipt=r['id'],labeled=True,action=r['action'],permit=r['permit'],outcome=r['outcome'],
            predicted_received_reply_probability=min(1.0,mass),unrepresented_reply=child is None)
        if r['action'] not in ('Sense','AskLoc'):
            p=sum(b['probability'] for b in node['children'] if b['kind']==0 and b['success'])
            assert 0<=p<=1+1e-7
            value.update(predicted_success_probability=min(1.0,p),actual_success=int(r['outcome']=='succeeded'))
        result.append(value)
    return result

def summary(rows):
    known=[r for r in rows if r.get('labeled')];physical=[r for r in known if 'actual_success' in r]
    n=len(physical);bins=[]
    for i in range(10):
        selected=[r for r in physical if min(9,int(r['predicted_success_probability']*10))==i]
        if selected:bins.append(dict(bin=i,count=len(selected),mean_predicted=sum(r['predicted_success_probability'] for r in selected)/len(selected),
            actual_rate=sum(r['actual_success'] for r in selected)/len(selected)))
    observations={}
    for action in sorted({r['action'] for r in known}):
        a=[r for r in known if r['action']==action]
        observations[action]=dict(count=len(a),unrepresented=sum(r['unrepresented_reply'] for r in a),
            zero_received_probability=sum(r['predicted_received_reply_probability']==0 for r in a),
            mean_clipped_log_loss=sum(-math.log(max(1e-12,r['predicted_received_reply_probability'])) for r in a)/len(a))
    return dict(labeled_receipts=len(known),unlabeled_receipts=len(rows)-len(known),physical_count=n,
        mean_predicted_success=sum(r['predicted_success_probability'] for r in physical)/n if n else None,
        actual_success_rate=sum(r['actual_success'] for r in physical)/n if n else None,
        brier=sum((r['predicted_success_probability']-r['actual_success'])**2 for r in physical)/n if n else None,
        ece=sum(b['count']/n*abs(b['mean_predicted']-b['actual_rate']) for b in bins) if n else None,
        bins=bins,reply_log_scores=observations)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('checkpoint');parser.add_argument('--suite',default='smoke2-full');args=parser.parse_args()
    tag=args.checkpoint+'-'+args.suite;raw=(LAB/(tag+'.jsonl')).read_bytes()
    journal=[json.loads(l) for l in raw.splitlines() if l];audit=json.loads((LAB/(tag+'-receipts.json')).read_text())
    verified={r['key']:r for r in audit['runs']};rows=[];runs=[];skipped=[]
    for row in journal:
        if row['arm']!='lab' or row['repeat']!=0:continue
        if row['key'] not in verified:skipped.append(dict(key=row['key'],reason='raw receipt audit failed or missing'));continue
        data=(LAB/'runs'/row['key']/'client.log').read_bytes();sha=hashlib.sha256(data).hexdigest()
        assert sha==verified[row['key']]['log_sha256'],'audited log changed'
        values=receipt_predictions(data.decode('utf8',errors='replace'))
        rows.extend(dict(v,key=row['key'],case=row['id'],mode=row['mode']) for v in values)
        runs.append(dict(key=row['key'],log_sha256=sha,summary=summary(values)))
    target=LAB/(tag+'-executed-predictions.json');assert not target.exists(),'Existing diagnostic is immutable'
    result=dict(checkpoint=args.checkpoint,suite=args.suite,repeat=0,journal_sha256=hashlib.sha256(raw).hexdigest(),
        overall=summary(rows),by_permit={p:summary([r for r in rows if r.get('permit')==p]) for p in sorted({r.get('permit') for r in rows if r.get('permit')})},
        trajectories=runs,receipts=rows,skipped_runs=skipped,log_loss_epsilon=1e-12,
        scope='already used development trajectories; correlated selected actions and IT/NT are not independent samples. Actual SDK replies only, no labels for unexecuted candidates. Descriptive selected-action errors do not certify global calibration or causal improvement.')
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=args.checkpoint,overall=result['overall'],skipped=len(skipped))))
if __name__=='__main__':main()
