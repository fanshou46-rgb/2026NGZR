"""Audit logged probability ranges and execution gates, without changing priors."""
import collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'validation/review177-20261004'
def main():
    rows=json.loads((OUT/'raw/frozen-v1/results.json').read_text(encoding='utf8'))
    assert len(rows)==304
    counts=collections.Counter();reject=collections.Counter();examples={};bad=[]
    for row in rows:
        if row['version']!='src1.7.7':continue
        for line in (Path(row['result']['output'])/'client.log').read_text(encoding='utf8',errors='replace').splitlines():
            if '[Probe] {' not in line:continue
            event=json.loads(line.split('[Probe] ',1)[1]);kind=event.get('kind');counts[event['event']]+=1
            if event['event']=='candidate':
                if not event['eligible']:reject[event['reason']]+=1
                if kind!='AskLoc':
                    lower=event['information_estimate'];upper=event['probability_upper'];residual=event['residual_mass']
                    if not (0<=lower<=upper+1e-6 and upper<=1+1e-6 and 0<=residual<=1+1e-6):bad.append(dict(trace=row['result']['output'],event=event))
                    counts['physical_candidate_records']+=1
                    counts['physical_records_with_residual']+=residual>0
                    counts['physical_records_with_goal_loss']+=event['terminal_goal_loss']>0
                    counts['physical_unknown_0_to_1_records']+=lower==0 and upper==1
                    if residual>0 and 'residual' not in examples:examples['residual']=dict(id=row['id'],suite=row['suite'],event=event)
                if event['reason']=='unmodeled_truthful_reply_order':counts['unsupported_answer_order']+=1
            if event['event']=='execute' and not event['eligible']:bad.append(dict(trace=row['result']['output'],event=event))
    assert not bad,bad
    result=dict(counts=dict(counts),candidate_rejections=dict(reject),violations=bad,examples=examples,
                scope='Logged records, not independent samples. Ranges are relative to declared prior, not empirically calibrated; [0,1] does not uniquely identify support failure. residual field is maximum per-target residual, not union residual. An executed observation need not complete a task.')
    (OUT/'PROBE_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(dict(counts=dict(counts),violations=len(bad)),ensure_ascii=False))
if __name__=='__main__':main()
