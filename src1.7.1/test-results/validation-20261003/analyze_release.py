#!/usr/bin/env python3
"""Post-process retained paired evidence without changing product or input files."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import re

def load(p):
    return json.loads(p.read_text(encoding='utf-8'))

def save(p,data):
    with p.open('x',encoding='utf-8') as out:
        json.dump(data,out,ensure_ascii=False,indent=2)

def delta(r,key):
    a,b=r['baseline'].get(key),r['current'].get(key)
    return b-a if a is not None and b is not None else None

def key(r):
    return '%s/%s/r%s'%(r['id'],r['mode'],r['round'])

def events(r,event):
    return [e for e in r['current']['probe_events'] if e['event']==event]

def is_early_stop(r):
    remaining=None
    for line in r['baseline']['decisions']:
        m=re.search(r'greedy task=18446744073709551615 marginal=0 remaining_ms=(\d+)',line)
        if m: remaining=int(m.group(1))
        if '[Scheduler] stop reason=no_qualified_positive_single' in line and remaining is not None and remaining>=300:
            return True
    return False

def measures(rows):
    scored=[r for r in rows if r['kind']=='scored']
    result={'pairs':len(rows),'scored_pairs':len(scored),'unique_inputs':len(set(r['id'] for r in rows))}
    for arm in ('baseline','current'):
        result[arm]={}
        for k in ('official_score','raw_score','base','final_goals','credited_constraints','action_cost','platform_seconds'):
            values=[r[arm].get(k) for r in scored if r[arm].get(k) is not None]
            result[arm][k]={'sum':sum(values),'count':len(values),'missing':len(scored)-len(values)}
        result[arm]['status']=dict(collections.Counter(r[arm].get('status') for r in scored))
        result[arm]['timeouts']=sum(bool(r[arm].get('platform_timed_out') or r[arm].get('external_timeout')) for r in scored)
    result['paired']={}
    for k in ('official_score','base','final_goals','credited_constraints'):
        values=[delta(r,k) for r in scored if delta(r,k) is not None]
        result['paired'][k]={'increase':sum(d>0 for d in values),'equal':sum(d==0 for d in values),
            'decrease':sum(d<0 for d in values),'missing':len(scored)-len(values),'delta_sum':sum(values)}
    feedback=[e for r in rows for e in events(r,'feedback')]
    replans=[e for r in rows for e in events(r,'replan')]
    completed=set()
    for r in rows:
        for e in events(r,'task_completed'):
            for t in e['completed_tasks']:
                completed.add((key(r),e['signature'],e['revision_before'],t))
    result['probes']={'total':len(feedback),'received_feedback':sum(e['received_feedback'] for e in feedback),
        'related_new_information':sum(e['related_new_evidence'] for e in feedback),
        'no_related_information':sum(not e['related_new_evidence'] for e in feedback),
        'effective_after_replan':sum(e['effective'] for e in replans),
        'no_progress_after_replan':sum(not e['effective'] for e in replans),
        'candidate_restored_events':sum(bool(e['restored_tasks']) for e in replans),
        'restored_task_occurrences':sum(len(e['restored_tasks']) for e in replans),
        'completed_restored_task_occurrences':len(completed),
        'kind':dict(collections.Counter(e['kind'] for e in feedback)),
        'max_per_run':max([len(events(r,'feedback')) for r in rows] or [0]),
        'move_failure':sum(e['move_failed'] for e in feedback),
        'exception_or_execution_failure':sum(bool(e['failure']) for e in feedback),
        'evidence_source_change_flags':{k:sum(bool(e[k]) for e in feedback) for k in
            ('sense_evidence_changes','action_success_evidence_changes','action_failure_evidence_changes')},
        'candidate_rejections':dict(collections.Counter(e['reason'] for r in rows for e in events(r,'candidate') if not e['eligible'])),
        'execution_rejections':dict(collections.Counter(e['reason'] for r in rows for e in events(r,'execution_rejected'))),
        'stop_reasons':dict(collections.Counter(e['reason'] for r in rows for e in events(r,'stop')))}
    early=[r for r in scored if r['stage']==2 and is_early_stop(r)]
    recovered=[r for r in early if any(e['restored_tasks'] for e in events(r,'replan'))]
    result['early_stop_recovery']={'pairs':len(early),'recovered_pairs':len(recovered),
        'input_ids':sorted(set(r['id'] for r in early)),
        'recovered_input_ids':sorted(set(r['id'] for r in recovered)),
        'subsequently_completed_pairs':sum(bool(events(r,'task_completed')) for r in recovered),
        'official_goal_gain_pairs':sum(delta(r,'final_goals') is not None and delta(r,'final_goals')>0 for r in early)}
    return result

def audit(rows):
    violations=[]; checked=0
    for r in rows:
        hist={}; count=collections.Counter(); closed=False; active=None; normal_task=None
        client=Path(r['current']['output'])/'client.log'
        text=client.read_text(errors='replace') if client.exists() else ''
        for line in re.sub(r'\x1b\[[0-9;]*m','',text).splitlines():
            m=re.search(r'\[Scheduler\] greedy task=(\d+) marginal=(-?\d+)',line)
            if m: normal_task=int(m.group(1))
            if '[Probe] ' not in line: continue
            e=json.loads(line.split('[Probe] ',1)[1])
            if e['event']=='execute':
                checked+=1; count[e['signature']]+=1
                if r['stage']!=2 or r['kind']!='scored' or normal_task!=2**64-1:
                    violations.append((key(r),'probe_outside_no_task_stage2'))
                if closed or sum(count.values())>8 or count[e['signature']]>2:
                    violations.append((key(r),'probe_bound'))
                if not e['eligible'] or e['constraint_result']!='constraint_safe' or e['kind'] not in ('MoveSense','SenseCurrentLocationOnly'):
                    violations.append((key(r),'authorization'))
                previous=hist.get(e['signature'])
                if previous and (previous['revision_after']==e['revision_before'] or not previous['related_new_evidence'] or
                                 previous['related_context_after']==e['related_context_before']):
                    violations.append((key(r),'duplicate_or_no_info_reopen'))
                active=e
            elif e['event']=='feedback':
                if not active or e['signature']!=active['signature']:
                    violations.append((key(r),'missing_execute'))
                expected=2 if e['kind']=='MoveSense' else 1
                if e['issued_actions']>expected or e['move_failed'] and e['sense_attempted']:
                    violations.append((key(r),'action_whitelist'))
                hist[e['signature']]=e; active=None
            if e.get('closed_reason'): closed=True
        if active: violations.append((key(r),'missing_feedback'))
        if r['current']['legacy_production_execution']: violations.append((key(r),'must_choose_one_production'))
        if r['kind']=='scored' and (r['current']['platform_timed_out'] or r['current']['external_timeout']) and events(r,'feedback'):
            violations.append((key(r),'probe_run_timeout_requires_inspection'))
    return {'checked_probes':checked,'violations':violations}

def invalid_summary(rows):
    result={}
    for layer in ('xml','syntax','domain','semantics'):
        part=[r for r in rows if r['kind']=='invalid' and r['expected_layer']==layer]
        result[layer]={'pairs':len(part),'inputs':sorted(set(r['id'] for r in part))}
        for arm in ('baseline','current'):
            result[layer][arm]={}
            for mode in ('it','nt'):
                p=[r for r in part if r['mode']==mode]
                result[layer][arm][mode]={'status':dict(collections.Counter(r[arm].get('status') for r in p)),
                    'timeouts':sum(bool(r[arm].get('platform_timed_out') or r[arm].get('external_timeout')) for r in p),
                    'unscored':sum(r[arm].get('official_score') is None for r in p),
                    'client_exits':dict(collections.Counter(str(r[arm].get('client_exit')) for r in p))}
    return result

def greedy_audit(rows):
    decisions=[];errors=[]
    for r in rows:
        if r['kind']!='scored':continue
        for arm in ('baseline','current'):
            candidates={};filtered=set();order=[]
            for line in (Path(r[arm]['output'])/'client.log').read_text(errors='replace').splitlines():
                m=re.search(r'\[3B\]\[Candidate\] phase=greedy-round rank=(\d+) task_index=(\d+).*marginal_score=(-?\d+)',line)
                if m:
                    rank,task,gain=map(int,m.groups())
                    if rank==1:candidates={};filtered=set();order=[]
                    candidates[task]=gain;order.append((rank,task));continue
                m=re.search(r'\[Scheduler\] filtered task=(\d+)',line)
                if m:filtered.add(int(m.group(1)));continue
                m=re.search(r'\[Scheduler\] greedy task=(\d+) marginal=(-?\d+)',line)
                if not m:continue
                task,gain=map(int,m.groups());remaining=[t for _,t in sorted(order) if t not in filtered]
                expected=remaining[0] if remaining else 2**64-1
                valid=task==expected and gain==(candidates[task] if remaining else 0)
                value={'pair':key(r),'arm':arm,'selected':task,'expected':expected,'marginal':gain,'valid':valid}
                decisions.append(value)
                if not valid:errors.append(value)
                candidates={};filtered=set();order=[]
    return {'decisions':decisions,'errors':errors,'checked':len(decisions)}

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();rows=load(a.root/'results.json');a.output.mkdir(exist_ok=False)
    assert len(rows)==1084 and len([r for r in rows if r['kind']=='scored'])==1004
    final=load(a.root/'final-audit.json');assert final['products_unchanged'] and final['inputs_unchanged']
    scopes={'all':rows,'stage1':[r for r in rows if r['kind']=='scored' and r['stage']==1],
        'stage2':[r for r in rows if r['kind']=='scored' and r['stage']==2],
        'legacy':[r for r in rows if r['suite']=='legacy'],
        'normal_comprehensive':[r for r in rows if r['suite']=='comprehensive' and r['kind']=='scored'],
        'invalid':[r for r in rows if r['kind']=='invalid']}
    save(a.output/'metrics.json',{s:measures(rs) for s,rs in scopes.items()})
    save(a.output/'runtime-audit.json',audit(rows));save(a.output/'invalid-summary.json',invalid_summary(rows))
    save(a.output/'greedy-audit.json',greedy_audit(rows))
    invalid=[]
    for case_id in sorted(set(r['id'] for r in scopes['invalid'])):
        part=[r for r in scopes['invalid'] if r['id']==case_id]
        invalid.append({'id':case_id,'expected_layer':part[0]['expected_layer'],'mutation':part[0]['mutation'],
            'runs':[{'pair':key(r),'mode':r['mode'],'baseline':{k:r['baseline'].get(k) for k in
                ('status','error','official_score','final_goals','action_sequence','client_exit','platform_timed_out','external_timeout')},
                'current':{k:r['current'].get(k) for k in
                ('status','error','official_score','final_goals','action_sequence','client_exit','platform_timed_out','external_timeout')}} for r in part]})
    save(a.output/'invalid-runs.json',invalid)
    grouped={}
    for r in rows:
        if r['kind']!='scored':continue
        group=grouped.setdefault(r['id'],{'id':r['id'],'stage':r['stage'],'path':r['path'],'suite':r['suite'],'pairs':[]})
        group['pairs'].append({'pair':key(r),'base_delta':delta(r,'base'),'official_delta':delta(r,'official_score'),
            'goal_delta':delta(r,'final_goals'),'probes':len(events(r,'feedback')),
            'restored':sum(bool(e['restored_tasks']) for e in events(r,'replan')),
            'completed':bool(events(r,'task_completed')),'baseline_early_stop':is_early_stop(r)})
    save(a.output/'per-input.json',list(grouped.values()))
    regressions=[r for r in rows if r['kind']=='scored' and any(delta(r,k) is not None and delta(r,k)<0 for k in
        ('official_score','base','final_goals'))]
    save(a.output/'regression-index.json',[{'pair':key(r),'id':r['id'],'stage':r['stage'],'path':r['path'],
        'base_delta':delta(r,'base'),'official_delta':delta(r,'official_score'),'goal_delta':delta(r,'final_goals'),
        'constraint_delta':delta(r,'credited_constraints'),'action_cost_delta':delta(r,'action_cost'),
        'explanation':('新增 Probe 成本，目标与计分约束相同' if delta(r,'base') is not None and delta(r,'base')<0 and
            delta(r,'final_goals')==0 and delta(r,'credited_constraints')==0 and events(r,'feedback') else
            '仅官方时间奖励变化' if delta(r,'base')==0 and delta(r,'final_goals')==0 and delta(r,'credited_constraints')==0 and
            r['baseline']['action_sequence']==r['current']['action_sequence'] else '需结合原始动作与门控日志解释'),
        'probes':len(events(r,'feedback')),'baseline':r['baseline']['output'],'current':r['current']['output']} for r in regressions])
    stage1=[]
    for r in scopes['stage1']:
        old,new=r['baseline']['action_sequence'],r['current']['action_sequence']
        if old==new and delta(r,'base')==0:continue
        common=0
        for x,y in zip(old,new):
            if x!=y:break
            common+=1
        details={'pair':key(r),'path':r['path'],'base_delta':delta(r,'base'),'goal_delta':delta(r,'final_goals'),
            'official_delta':delta(r,'official_score'),'common_action_prefix':common,'baseline_actions':old,'current_actions':new,
            'baseline_decisions':r['baseline']['decisions'],'current_decisions':r['current']['decisions'],
            'probes':len(events(r,'feedback'))}
        stage1.append(details)
    save(a.output/'stage1-differences.json',stage1)
    with (a.output/'pairs.csv').open('x',encoding='utf-8',newline='') as out:
        columns=['id','stage','suite','kind','expected_layer','mode','round','order']
        columns+=[arm+'_'+k for arm in ('baseline','current') for k in
            ('status','official_score','raw_score','base','final_goals','credited_constraints','action_cost','platform_seconds','platform_timed_out','external_timeout','client_exit')]
        columns+=['probes','related_information','candidate_restored_events','subsequently_completed','baseline_early_stop']
        writer=csv.DictWriter(out,fieldnames=columns);writer.writeheader()
        for r in rows:
            record={k:r.get(k) for k in ('id','stage','suite','kind','expected_layer','mode','round','order')}
            for arm in ('baseline','current'):
                for k in ('status','official_score','raw_score','base','final_goals','credited_constraints','action_cost','platform_seconds','platform_timed_out','external_timeout','client_exit'):
                    record[arm+'_'+k]=r[arm].get(k)
            record.update(probes=len(events(r,'feedback')),related_information=sum(e['related_new_evidence'] for e in events(r,'feedback')),
                candidate_restored_events=sum(bool(e['restored_tasks']) for e in events(r,'replan')),
                subsequently_completed=bool(events(r,'task_completed')),baseline_early_stop=is_early_stop(r))
            writer.writerow(record)
    print('ANALYSIS COMPLETE',len(rows),'pairs;',len(regressions),'regressions;',len(stage1),'Stage 1 differences')

if __name__=='__main__':main()
