"""All paired regressions and real repeat disagreements, never selective reruns."""
from pathlib import Path
import json,argparse,collections
ROOT=Path(__file__).resolve().parents[2];LAB=ROOT/'experiments/full_probability'
def main():
    p=argparse.ArgumentParser();p.add_argument('checkpoint');p.add_argument('--suite',default='smoke');a=p.parse_args()
    records=[json.loads(x) for x in (LAB/(a.checkpoint+'-'+a.suite+'.jsonl')).read_text().splitlines() if x]
    paired={};repeated={};groups={}
    metrics=['final_goals','credited_constraints','action_cost','base','raw_score','official_score','platform_seconds']
    for row in records:
        paired.setdefault((row['id'],row['mode'],row['repeat']),{})[row['arm']]=row
        repeated.setdefault((row['id'],row['mode'],row['arm']),{})[row['repeat']]=row
    changes=[];regressions=[]
    for key,pair in paired.items():
        if set(pair)!=set(['lab','167_200']):continue
        lab=pair['lab'];base=pair['167_200'];diff={}
        for metric in metrics:
            v,b=lab['result'].get(metric),base['result'].get(metric)
            diff[metric]=None if v is None or b is None else v-b
        for label in [('all',),('stage',lab['stage']),('mode',lab['mode']),('family',lab['family']),('repeat',lab['repeat'])]:
            g=groups.setdefault(str(label),dict(pairs=0,delta=collections.Counter(),missing=collections.Counter(),formal=collections.Counter()))
            g['pairs']+=1
            lf,bf=lab['result'].get('official_score'),base['result'].get('official_score')
            g['formal']['lab_scored_sum']+=lf if lf is not None else 0
            g['formal']['baseline_scored_sum']+=bf if bf is not None else 0
            g['formal']['lab_missing']+=lf is None;g['formal']['baseline_missing']+=bf is None
            g['formal']['missing_as_zero_delta']+=(lf if lf is not None else 0)-(bf if bf is not None else 0)
            for m,d in diff.items():
                if d is None:g['missing'][m]+=1
                else:g['delta'][m]+=d
        if any(diff[m] is None or diff[m]<0 for m in ['final_goals','base','official_score']):
            lseq,bseq=lab['result']['action_sequence'],base['result']['action_sequence'];prefix=0
            while prefix<min(len(lseq),len(bseq)) and lseq[prefix]==bseq[prefix]:prefix+=1
            regressions.append(dict(case=key,delta=diff,common_prefix=prefix,lab_next=lseq[prefix:prefix+1],baseline_next=bseq[prefix:prefix+1],lab=lab['key'],baseline=base['key']))
    counts=collections.Counter()
    for key,pair in repeated.items():
        if set(pair)!=set([0,1]):continue
        first,second=pair[0]['result'],pair[1]['result'];counts[key[2]+'_pairs']+=1
        gck=['final_goals','credited_constraints','action_cost']
        missing=any(first.get(m) is None or second.get(m) is None for m in gck)
        changed=any(first.get(m)!=second.get(m) for m in gck)
        counts[key[2]+'_gck_missing']+=missing
        counts[key[2]+'_gck_changed']+=changed and not missing
        counts[key[2]+'_gck_identical']+=not missing and not changed
        counts[key[2]+'_action_sequence_changed']+=first['action_sequence']!=second['action_sequence']
        if first['action_sequence']!=second['action_sequence'] or missing or changed:
            counts[key[2]+'_changed']+=1
            changes.append(dict(case=key,first=pair[0]['key'],repeat=pair[1]['key'],metrics={m:[first.get(m),second.get(m)] for m in metrics}))
    result=dict(checkpoint=a.checkpoint,suite=a.suite,scope='development only; one seed plus repeat, no independent CI',groups=groups,repeat_counts=dict(counts),repeat_disagreements=changes,regressions=regressions)
    (LAB/(a.checkpoint+'-'+a.suite+'-analysis.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(all=groups.get(str(('all',))),repeat_counts=dict(counts),regressions=len(regressions)),ensure_ascii=False))
if __name__=='__main__':main()
