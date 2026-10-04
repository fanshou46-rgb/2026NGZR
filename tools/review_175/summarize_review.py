"""Strict summary of the frozen review: missing results are never zero scores."""
import collections, csv, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'validation/review175-20261004'
RUN=OUT/'frozen-v5'
VERSIONS=['src1.7.3','src1.7.4','src1.7.5']
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 rows=json.loads((RUN/'results.json').read_text(encoding='utf8'))
 audit=json.loads((RUN/'final-audit.json').read_text(encoding='utf8'))
 assert len(rows)==432 and audit['runs']==432 and audit['reference_runs']==24
 keys={(r['id'],r['mode'],r['seed'],r['version']) for r in rows};assert len(keys)==432
 assert all(r['result']['seed_confirmed'] for r in rows)
 def totals(part):
  result={}
  for version in VERSIONS:
   subset=[r['result'] for r in part if r['version']==version]
   complete=[r for r in subset if all(r.get(k) is not None for k in ('base','raw_score','official_score','final_goals','credited_constraints','action_cost','platform_seconds'))]
   item={'runs':len(subset),'scored':len(complete),'missing':len(subset)-len(complete)}
   for k in ('base','raw_score','official_score','final_goals','credited_constraints','action_cost','platform_seconds'):
    item[k]=round(sum(r[k] for r in complete),3)
   item.update(sdk_timeouts=sum(bool(r.get('platform_timed_out')) for r in subset),external_timeouts=sum(bool(r.get('external_timeout')) for r in subset),
               crashes=sum(r.get('client_exit') not in (None,0) for r in subset),harness_errors=sum('error' in r for r in subset),
               platform_errors=sum(bool(r.get('platform_error')) for r in subset),status_failed=sum(r.get('status')!='ok' for r in subset),
               probes=sum(sum(e['event']=='execute' for e in r['probe_events']) for r in subset))
   result[version]=item
  return result
 summary={'all':totals(rows)}
 for field in ('suite','family','stage','mode','seed','stress'):
  summary[field]={str(v):totals([r for r in rows if r[field]==v]) for v in sorted({r[field] for r in rows},key=str)}
 flat=[];bykey=collections.defaultdict(dict);violations=[]
 for r in rows:
  result=r['result'];bykey[(r['id'],r['mode'],r['seed'])][r['version']]=r
  path=Path(result['output']);server=(path/'server.log').read_text(encoding='utf8',errors='replace')
  # Original Linux absolute paths can be resolved from their repository suffix on Windows.
  flat.append({k:r[k] for k in ('id','family','suite','stress','stage','mode','seed','version')})
  flat[-1].update({k:result.get(k) for k in ('base','raw_score','official_score','final_goals','credited_constraints','action_cost','platform_seconds','platform_timed_out','external_timeout','client_exit','status')})
  ungraded=result.get('official_score') is None or result.get('platform_seconds') is None
  flat[-1]['diagnostic_ungraded_goals']=result.get('final_goals') if ungraded else None
  if ungraded:
   for field in ('base','action_cost','final_goals','credited_constraints'):flat[-1][field]=None
  flat[-1]['failed_actions']=None if ungraded else len(re.findall(r'\[[^\r\n]*\|false\]',server))
  flat[-1]['actions']='; '.join(result['action_sequence']);flat[-1]['trace']=str(path.relative_to(ROOT))
  executed=[e for e in result['probe_events'] if e['event']=='execute'];counts=collections.Counter();seen=set()
  for e in executed:
   key=(e['signature'],e['world_revision']);counts[e['signature']]+=1
   if (key in seen and e['kind']!='AskLoc') or counts[e['signature']]>(3 if e['kind']=='AskLoc' else 2):violations.append([r['id'],r['mode'],r['seed'],r['version'],'probe_repeat'])
   if e['constraint_result']!='constraint_safe' and not (e['constraint_result']=='bounded_score_trade' and e.get('constraint_risk_count',99)<=2 and e.get('authorized_constraint_risk_count',99)<=2 and e.get('expected_gain',-1)>0):violations.append([r['id'],r['mode'],r['seed'],r['version'],'probe_authorization'])
   seen.add(key)
  if len(executed)>8 or r['stage']==1 and executed or result['legacy_production_execution']:violations.append([r['id'],r['mode'],r['seed'],r['version'],'execution_boundary'])
 comparisons={};regressions=[]
 for before,after in list(zip(VERSIONS,VERSIONS[1:]))+[(VERSIONS[0],VERSIONS[-1])]:
  label=before+' -> '+after;part=[]
  for key,arms in sorted(bykey.items()):
   a=arms[before]['result'];b=arms[after]['result']
   if any(r.get(k) is None for r in (a,b) for k in ('base','raw_score','official_score','final_goals','credited_constraints','action_cost','platform_seconds')):continue
   delta={k:round(b[k]-a[k],3) for k in ('base','raw_score','official_score','final_goals','credited_constraints','action_cost','platform_seconds')}
   delta.update(same_actions=a['action_sequence']==b['action_sequence'],suite=arms[before]['suite'])
   part.append(delta)
   if any(delta[k]<0 for k in ('base','raw_score','official_score','final_goals','credited_constraints')) or delta['action_cost']>0 or (b.get('platform_timed_out') and not a.get('platform_timed_out')):
    regressions.append(dict(comparison=label,id=key[0],mode=key[1],seed=key[2],family=arms[before]['family'],**delta))
  comparisons[label]={'paired':len(part),'excluded_missing':len(bykey)-len(part),'delta':{k:round(sum(r[k] for r in part),3) for k in ('base','raw_score','official_score','final_goals','credited_constraints','action_cost','platform_seconds')},
      'base_improved':sum(r['base']>0 for r in part),'base_worsened':sum(r['base']<0 for r in part),'base_equal':sum(r['base']==0 for r in part),
      'goals_worsened':sum(r['final_goals']<0 for r in part),'same_actions':sum(r['same_actions'] for r in part)}
 scoped_comparisons={}
 for suite in ('old','new'):
  scoped_comparisons[suite]={}
  for before,after in [('src1.7.3','src1.7.5'),('src1.7.4','src1.7.5')]:
   pairs=[]
   for key,arms in bykey.items():
    if arms[before]['suite']!=suite:continue
    a=arms[before]['result'];b=arms[after]['result']
    if any(r.get(k) is None for r in (a,b) for k in ('base','raw_score','official_score','final_goals','credited_constraints','action_cost','platform_seconds')):continue
    pairs.append({k:round(b[k]-a[k],3) for k in ('base','raw_score','official_score','final_goals','credited_constraints','action_cost','platform_seconds')})
   scoped_comparisons[suite][before+' -> '+after]=dict(paired=len(pairs),delta={k:round(sum(r[k] for r in pairs),3) for k in ('base','raw_score','official_score','final_goals','credited_constraints','action_cost','platform_seconds')},base_improved=sum(r['base']>0 for r in pairs),base_worsened=sum(r['base']<0 for r in pairs),base_equal=sum(r['base']==0 for r in pairs),goals_worsened=sum(r['final_goals']<0 for r in pairs))
 save('SUMMARY.json',dict(totals=summary,comparisons=comparisons,scoped_comparisons=scoped_comparisons,violations=violations))
 for name,data in [('RUNS.csv',flat),('REGRESSIONS.csv',regressions)]:
  with (OUT/name).open('w',encoding='utf8',newline='') as f:
   writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
 print(json.dumps(dict(all=summary['all'],comparisons=comparisons,violations=violations),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
