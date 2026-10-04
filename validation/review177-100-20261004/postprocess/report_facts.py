"""Reporting statistics only. No evaluation input/strategy is changed."""
from pathlib import Path
import json,collections,statistics
OUT=Path(__file__).resolve().parents[1]
ARMS=('167','167_200','177','neutral','no_ask','legacy_visibility')
METRICS=('final_goals','credited_constraints','action_cost','base','raw_score','official_score','platform_seconds','failed_actions')
def stats(part):
    z={'runs':len(part)}
    for key in METRICS:
        values=[r['result'][key] for r in part if r['result'].get(key) is not None]
        z[key]=dict(n=len(values),missing=len(part)-len(values),sum=sum(values),mean=statistics.mean(values) if values else None)
    z['sdk_cutoff']=sum(bool(r['result'].get('platform_timed_out')) for r in part)
    z['external_timeout']=sum(bool(r['result'].get('external_timeout')) for r in part)
    z['statuses']=dict(collections.Counter(r['result']['status'] for r in part))
    return z
def main():
    rr=[]
    for line in (OUT/'results.jsonl').read_text(encoding='utf8').splitlines():
        try:rr.append(json.loads(line))
        except json.JSONDecodeError:break
    grouped=collections.defaultdict(dict)
    for r in rr:grouped[(r['suite'],r['id'],r['mode'],r['round'])][r['arm']]=r
    z={'runs':len(rr),'primary_rounds':[1,2,3],'repeat_excluded_from_primary':True,'cohorts':{},'model_controls':{},'repeats':{},'probe_operations':{}}
    for suite in ('new','historical','seen','invalid','excluded'):
        z['cohorts'][suite]={}
        for arm in ARMS:
            part=[r for r in rr if r['suite']==suite and r['arm']==arm]
            if not part:continue
            z['cohorts'][suite][arm]={'all_rounds':stats(part),'primary':stats([r for r in part if r['round']!=4]),'stages':{str(s):stats([r for r in part if r['stage']==s and r['round']!=4]) for s in (1,2)}}
    for arm in ARMS:
        if arm=='177':continue
        pairs=[(g[arm],g['177']) for k,g in grouped.items() if k[0]=='new' and arm in g and '177' in g]
        z['model_controls'][arm]={}
        for stage in (1,2):
            p=[(a,b) for a,b in pairs if a['stage']==stage and a['round']!=4]
            def delta(key):return sum(b['result'][key]-a['result'][key] for a,b in p if b['result'].get(key) is not None and a['result'].get(key) is not None)
            z['model_controls'][arm][str(stage)]=dict(pairs=len(p),same_actions=sum(a['result']['action_sequence']==b['result']['action_sequence'] for a,b in p),deltas={k:delta(k) for k in METRICS},goal_improvement=sum(b['result']['final_goals']>a['result']['final_goals'] for a,b in p),goal_decline=sum(b['result']['final_goals']<a['result']['final_goals'] for a,b in p),score_up_goal_down=sum(b['result']['official_score']>a['result']['official_score'] and b['result']['final_goals']<a['result']['final_goals'] for a,b in p))
        p=[(a,b) for a,b in pairs if a['round']==4]
        z['model_controls'][arm]['repeat']=dict(pairs=len(p),same_actions=sum(a['result']['action_sequence']==b['result']['action_sequence'] for a,b in p))
    for arm in ARMS:
        part=[]
        for k,g in grouped.items():
            if k[3]!=4 or arm not in g:continue
            a=grouped[(k[0],k[1],k[2],1)].get(arm)
            if a:part.append((a,g[arm]))
        z['repeats'][arm]=dict(pairs=len(part),action_changes=sum(a['result']['action_sequence']!=b['result']['action_sequence'] for a,b in part),goal_changes=sum(a['result'].get('final_goals')!=b['result'].get('final_goals') for a,b in part),by_stage={str(s):sum(a['result']['action_sequence']!=b['result']['action_sequence'] for a,b in part if a['stage']==s) for s in (1,2)})
    for arm in ARMS[2:]:
        part=[r for r in rr if r['suite']=='new' and r['arm']==arm and r['stage']==2 and r['round']!=4]
        events=[e for r in part for e in r['result'].get('probe_events',[])]
        action_counts=collections.Counter()
        for r in part:action_counts.update(r['result'].get('actions',{}))
        z['probe_operations'][arm]=dict(runs=len(part),sdk_action_counts=dict(action_counts),executed=dict(collections.Counter(e.get('kind') for e in events if e['event']=='execute')),rejected=dict(collections.Counter(e.get('reason') for e in events if e['event']=='candidate' and not e.get('eligible'))),guard_fallback=dict(collections.Counter(reason for r in part for line in r['result'].get('decisions',[]) for reason in __import__('re').findall(r'\[GuardedDecision\] outcome=greedy reason=(\S+)',line))))
    (OUT/'REPORT_FACTS.json').write_text(json.dumps(z,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('REPORT_FACTS',len(rr),'runs')
    print(json.dumps(z['model_controls'],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
