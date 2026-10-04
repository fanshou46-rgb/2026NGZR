"""Aggregate every frozen pair, SDK scores and canonical disagreements."""
import collections,csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'validation/review176-20261004'
VERSIONS=['src1.7.5','src1.7.6']
FINAL=re.compile(r'\[3A\]\[final\] goals=(\d+)/(\d+) \(unknown=(\d+)\), constraints=(\d+)/(\d+) \(unknown=(\d+)\), base_score=(-?\d+), action_cost=(\d+)')
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def table(path,rows):
    with path.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    run=OUT/'raw/frozen-v2';audit=json.loads((run/'final-audit.json').read_text(encoding='utf8'));assert audit['runs']==416
    rows=json.loads((run/'results.json').read_text(encoding='utf8'));flat=[];pairs=collections.defaultdict(dict)
    for row in rows:
        r=row['result'];item={k:row[k] for k in ('suite','id','family','stage','mode','seed','version')}
        server=(Path(r['output'])/'server.log').read_text(encoding='utf8',errors='replace')
        client=(Path(r['output'])/'client.log').read_text(encoding='utf8',errors='replace')
        grades=re.findall(r'^# Score:\s*(-?\d+)',server,re.M)
        if r.get('raw_score') is not None:
            assert grades and int(grades[-1])==r['raw_score'] and min(int(grades[-1]),1000)==r['official_score']
        item.update(base=r.get('base'),raw_score=r.get('raw_score'),official_score=r.get('official_score'),goals=r.get('final_goals'),constraints=r.get('credited_constraints'),cost=r.get('action_cost'),seconds=r.get('platform_seconds'),sdk_timeout=bool(r.get('platform_timed_out')),external_timeout=bool(r.get('external_timeout')),status=r.get('status'),seed_confirmed=r.get('seed_confirmed'),actions=json.dumps(r.get('action_sequence',[]),ensure_ascii=False),trace=str(Path(r['output']).relative_to(ROOT)))
        matches=FINAL.findall(client);item.update(canonical_goals=None,canonical_base=None,canonical_cost=None,canonical_constraints=None)
        if r.get('official_score') is None:category='ungraded'
        elif not matches:category='no_final_claim'
        else:
            g,_,_,c,_,_,base,cost=map(int,matches[-1]);item.update(canonical_goals=g,canonical_base=base,canonical_cost=cost,canonical_constraints=c)
            category='goal_overcount' if g>r['final_goals'] else 'goal_undercount' if g<r['final_goals'] else 'other_difference' if any((c!=r['credited_constraints'],base!=r['base'],cost!=r['action_cost'])) else 'equal'
        item['category']=category;flat.append(item);pairs[(row['suite'],row['id'],row['mode'],row['seed'])][row['version']]=item
    table(OUT/'RUNS.csv',flat);summary={};regressions=[]
    for suite in sorted({r['suite'] for r in flat}):
        group={}
        for v in VERSIONS:
            part=[r for r in flat if r['suite']==suite and r['version']==v]
            group[v]={k:sum(r[k] or 0 for r in part) for k in ('base','raw_score','official_score','goals','constraints','cost','seconds')}
            group[v].update(runs=len(part),scored=sum(r['official_score'] is not None for r in part),sdk_timeouts=sum(r['sdk_timeout'] for r in part),external_timeouts=sum(r['external_timeout'] for r in part),status_failures=sum(r['status']!='ok' for r in part),canonical=dict(collections.Counter(r['category'] for r in part)))
        group['delta']={k:group[VERSIONS[1]][k]-group[VERSIONS[0]][k] for k in ('base','raw_score','official_score','goals','constraints','cost','seconds')}
        summary[suite]=group
    for key,pair in sorted(pairs.items()):
        assert set(pair)==set(VERSIONS);a,b=[pair[v] for v in VERSIONS]
        delta={k:(b[k]-a[k]) if a[k] is not None and b[k] is not None else None for k in ('base','raw_score','official_score','goals','constraints','cost','seconds')}
        if any(delta[k] is not None and delta[k]<0 for k in ('base','official_score','goals','constraints')) or any(delta[k] is not None and delta[k]>0 for k in ('cost','seconds')) or b['official_score'] is None or b['sdk_timeout']:
            regressions.append(dict(suite=key[0],id=key[1],mode=key[2],seed=key[3],**{'delta_'+k:v for k,v in delta.items()},baseline_trace=a['trace'],current_trace=b['trace']))
    if regressions:table(OUT/'REGRESSIONS.csv',regressions)
    refs=json.loads((run/'references.json').read_text(encoding='utf8'));assert len(refs)==16
    save(OUT/'SUMMARY.json',dict(suites=summary,pairs=len(pairs),regression_or_cost_time_increase_pairs=len(regressions),reference_runs=len(refs),reference_sdk_timeouts=sum(bool(r['result'].get('platform_timed_out')) for r in refs),server_raw_score_verified=sum(r['raw_score'] is not None for r in flat),policy='SDK grades authoritative; per-question min(raw,1000); costs count every attempted action; all scored timeouts retained'))
    save(OUT/'frozen-audit.json',json.loads((run/'frozen-audit.json').read_text(encoding='utf8')));save(OUT/'final-audit.json',audit)
    controls=[p for k,p in pairs.items() if k[0]=='stage1_control']
    save(OUT/'STAGE1_AUDIT.json',dict(pairs=len(controls),same_actions=sum(p[VERSIONS[0]]['actions']==p[VERSIONS[1]]['actions'] for p in controls),same_goals=sum(p[VERSIONS[0]]['goals']==p[VERSIONS[1]]['goals'] for p in controls),same_base=sum(p[VERSIONS[0]]['base']==p[VERSIONS[1]]['base'] for p in controls),scope='four selected Stage1 controls, one seed IT/NT; relation correction may deliberately change action sequences'))
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
