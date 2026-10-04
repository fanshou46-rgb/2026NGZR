"""Complete pair accounting; cluster intervals do not treat repeated seeds as independent."""
from common import *
import collections, csv, math, random, re, zipfile
FIELDS=('base','official_score','raw_score','final_goals','credited_constraints','action_cost','platform_seconds','failed_actions')
FINAL=re.compile(r'\[3A\]\[final\] goals=(\d+)/(\d+) \(unknown=(\d+)\), constraints=(\d+)/(\d+) \(unknown=(\d+)\), base_score=(-?\d+), action_cost=(\d+)')
def rows():return [json.loads(line) for line in (OUT/'results.jsonl').read_text(encoding='utf8').splitlines()]
def table(path,items):
    if not items:return
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
def summarize(part):
    result={k:sum(r['result'].get(k) or 0 for r in part) for k in FIELDS}
    result.update(runs=len(part),scored=sum(r['result'].get('official_score') is not None for r in part),
        sdk_timeouts=sum(bool(r['result'].get('platform_timed_out')) for r in part),external_timeouts=sum(bool(r['result'].get('external_timeout')) for r in part),
        seed_unconfirmed=sum(not r['result'].get('seed_confirmed') for r in part),statuses=dict(collections.Counter(r['result']['status'] for r in part)))
    result['official_score_missing_as_zero']=result['official_score']
    result['base_missing']=sum(r['result'].get('base') is None for r in part)
    return result
def branch(a,b):
    aa,bb=a['result']['action_sequence'],b['result']['action_sequence'];prefix=0
    while prefix<min(len(aa),len(bb)) and aa[prefix]==bb[prefix]:prefix+=1
    return dict(common_prefix=prefix,baseline_next=aa[prefix] if prefix<len(aa) else '<STOP>',latest_next=bb[prefix] if prefix<len(bb) else '<STOP>',baseline_actions=len(aa),latest_actions=len(bb))
def confidence(part,metric):
    # Primary inference uses only the three distinct seeds; fourth round is a wall-clock repeat.
    clusters=collections.defaultdict(lambda:[0.,0])
    for p in part:
        if p['round']==4 or p['delta_'+metric] is None:continue
        key=p['cluster'] or p['id'];clusters[key][0]+=p['delta_'+metric];clusters[key][1]+=1
    units=list(clusters.values())
    if not units:return dict(clusters=0,mean=None,lower=None,upper=None)
    rng=random.Random(177100);draws=[]
    for _ in range(10000):
        sampled=[units[rng.randrange(len(units))] for j in units]
        draws.append(sum(x[0] for x in sampled)/sum(x[1] for x in sampled))
    draws.sort();return dict(clusters=len(units),mean=sum(x[0] for x in units)/sum(x[1] for x in units),lower=draws[249],upper=draws[9749],replicates=10000,method='cluster percentile bootstrap; linked counterfactual scenes stay together; repeat round excluded')
def main():
    rr=rows();audit=json.loads((OUT/'final-audit.json').read_text());assert len(rr)==audit['runs']==6726
    flat=[];grouped=collections.defaultdict(dict);probes={};violations=[]
    for r in rr:
        value=r['result'];p=Path(value['output']);client=(p/'client.log').read_text(errors='replace') if (p/'client.log').exists() else ''
        server=(p/'server.log').read_text(errors='replace') if (p/'server.log').exists() else ''
        scores=re.findall(r'^# Score:\s*(-?\d+)',server,re.M)
        if value.get('raw_score') is not None:assert scores and int(scores[-1])==value['raw_score'] and min(value['raw_score'],1000)==value['official_score']
        matches=FINAL.findall(client);category='ungraded' if value.get('official_score') is None else 'no_final_claim'
        canonical={k:None for k in ('canonical_goals','canonical_constraints','canonical_cost','canonical_base')}
        if matches and value.get('official_score') is not None:
            g,_,_,c,_,_,base,cost=map(int,matches[-1]);canonical=dict(canonical_goals=g,canonical_constraints=c,canonical_base=base,canonical_cost=cost)
            category='goal_overcount' if g>value['final_goals'] else 'goal_undercount' if g<value['final_goals'] else 'other_difference' if (c!=value['credited_constraints'] or base!=value['base'] or cost!=value['action_cost']) else 'equal'
        item={k:r.get(k) for k in ('key','suite','id','family','category','stage','kind','cluster','round','seed','mode','arm')}
        item.update({k:value.get(k) for k in FIELDS});item.update(status=value['status'],sdk_timeout=bool(value.get('platform_timed_out')),external_timeout=bool(value.get('external_timeout')),seed_confirmed=value.get('seed_confirmed'),canonical_category=category,trace=str(p.relative_to(ROOT)),**canonical)
        flat.append(item);grouped[(r['suite'],r['id'],r['mode'],r['round'])][r['arm']]=r
        if r['arm'] not in ('167','167_200'):
            counts=probes.setdefault(r['arm'],dict(events=collections.Counter(),rejections=collections.Counter()))
            for e in value.get('probe_events',[]):
                counts['events'][e['event']]+=1
                if e['event']=='candidate' and not e.get('eligible'):counts['rejections'][e.get('reason')]+=1
                if e['event']=='execute' and not e.get('eligible'):violations.append(dict(key=r['key'],event=e))
                if e['event']=='candidate' and e.get('kind')!='AskLoc':
                    lo,hi,res=e.get('information_estimate'),e.get('probability_upper'),e.get('residual_mass')
                    if not (0<=lo<=hi+1e-6<=1+1e-6 and 0<=res<=1):violations.append(dict(key=r['key'],event=e))
    table(OUT/'RUNS.csv',flat)
    pairs=[];regressions=[];changed=[];evidence=OUT/'pair-evidence';evidence.mkdir(exist_ok=True)
    for key,arms in grouped.items():
        if '177' not in arms:continue
        latest=arms['177']
        for control in arms:
            if control=='177':continue
            baseline=arms[control];a,b=baseline['result'],latest['result']
            item={k:latest.get(k) for k in ('suite','id','family','stage','kind','cluster','round','seed','mode')};item['control']=control
            item.update({'delta_'+k:b[k]-a[k] if b.get(k) is not None and a.get(k) is not None else None for k in FIELDS})
            item.update(baseline_trace=str(Path(a['output']).relative_to(ROOT)),latest_trace=str(Path(b['output']).relative_to(ROOT)),**branch(baseline,latest))
            pairs.append(item)
            negative=any(item['delta_'+k] is not None and item['delta_'+k]<0 for k in ('base','official_score','final_goals','credited_constraints'))
            costly=any(item['delta_'+k] is not None and item['delta_'+k]>0 for k in ('action_cost','platform_seconds','failed_actions'))
            timeout=bool(b.get('platform_timed_out') or b.get('external_timeout'))
            if negative or costly or timeout or b.get('official_score') is None:regressions.append(item)
            if item['delta_base'] or item['delta_final_goals'] or item['baseline_next']!=item['latest_next']:
                changed.append(item)
                name=latest['key']+'-vs-'+control+'.md'
                lines=[f"# {latest['key']} vs {control}",f"共同动作前缀 {item['common_prefix']}；下一动作：{item['baseline_next']} → {item['latest_next']}。",
                    '## 官方指标',json.dumps({k:item[k] for k in item if k.startswith('delta_')},ensure_ascii=False,indent=2),
                    '## 基线动作',json.dumps(a['action_sequence'],ensure_ascii=False), '## 最新版动作',json.dumps(b['action_sequence'],ensure_ascii=False),
                    '## 最新版候选/执行/停止日志（原始顺序）']
                lines += [json.dumps(e,ensure_ascii=False) for e in b.get('probe_events',[]) if e['event'] in ('execute','stop','candidate','execution_rejected')]
                lines += ['## 原始路径',item['baseline_trace'],item['latest_trace'],'日志中的首次动作分叉不是自动的因果结论；模块归因见总报告。']
                (evidence/name).write_text('\n\n'.join(lines)+'\n',encoding='utf8')
    table(OUT/'PAIRS.csv',pairs);table(OUT/'REGRESSIONS.csv',regressions);table(OUT/'BEHAVIOR_CHANGES.csv',changed)
    summary={}
    for suite in ('new','historical','seen','invalid','excluded'):
        part=[r for r in rr if r['suite']==suite]
        summary[suite]={arm:summarize([r for r in part if r['arm']==arm]) for arm in sorted({r['arm'] for r in part})}
    strata=[]
    for suite in ('new','historical','seen'):
        for dimension in ('stage','mode','family','round','kind'):
            for value in sorted({str(r.get(dimension)) for r in rr if r['suite']==suite}):
                for arm in sorted(summary[suite]):
                    part=[r for r in rr if r['suite']==suite and r['arm']==arm and str(r.get(dimension))==value]
                    strata.append(dict(suite=suite,dimension=dimension,value=value,arm=arm,**{k:v for k,v in summarize(part).items() if k!='statuses'}))
    table(OUT/'STRATA.csv',strata)
    ci={}
    for control in ('167','167_200','neutral','no_ask','legacy_visibility'):
        ci[control]={}
        for stage in ('all',1,2):
            part=[p for p in pairs if p['suite']=='new' and p['control']==control and (stage=='all' or p['stage']==stage)]
            ci[control][str(stage)]={metric:confidence(part,metric) for metric in ('base','final_goals','official_score')}
    save(OUT/'CONFIDENCE.json',ci)
    repeat=[]
    indexed={(r['suite'],r['id'],r['mode'],r['arm'],r['round']):r for r in rr}
    for r in rr:
        if r['round']!=4:continue
        a=indexed[(r['suite'],r['id'],r['mode'],r['arm'],1)];b=r
        repeat.append(dict(suite=r['suite'],id=r['id'],mode=r['mode'],arm=r['arm'],same_actions=a['result']['action_sequence']==b['result']['action_sequence'],**{'delta_'+k:b['result'][k]-a['result'][k] if b['result'].get(k) is not None and a['result'].get(k) is not None else None for k in FIELDS}))
    table(OUT/'REPEATS.csv',repeat)
    save(OUT/'PROBE_AUDIT.json',dict(arms={arm:{k:dict(v) for k,v in x.items()} for arm,x in probes.items()},violations=violations,scope='logged candidates are correlated; selected observations have selection bias; no claim of empirical probability calibration'))
    save(OUT/'SUMMARY.json',dict(suites=summary,runs=len(rr),comparisons=len(pairs),regression_or_cost_time_increase_pairs=len(regressions),behavior_change_pairs=len(changed),canonical={arm:dict(collections.Counter(r['canonical_category'] for r in flat if r['arm']==arm and r['suite'] not in ('invalid','excluded'))) for arm in ARMS},repeats=len(repeat),same_seed_different_actions=sum(not r['same_actions'] for r in repeat),ungraded=sum(r['official_score'] is None for r in flat),grade_verified=sum(r['raw_score'] is not None for r in flat)))
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
