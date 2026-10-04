"""Supplement pair receipts with official goal IDs and raw public feedback."""
from pathlib import Path
import json,csv,re,zipfile,collections
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
def path(value):
    marker='/validation/review177-100-20261004/'
    return OUT/value.split(marker,1)[1]
def official(r):
    p=path(r['result']['output'])
    if not(p/'runtime.zip').exists():return {'goals':None,'constraints':None}
    with zipfile.ZipFile(p/'runtime.zip') as z:
        text=z.read('vanswer.txt').decode(errors='replace') if 'vanswer.txt' in z.namelist() else ''
        log=z.read('evaluelog.txt').decode(errors='replace') if 'evaluelog.txt' in z.namelist() else None
    charges=[int(v) for v in re.findall(r'Executing the action:[^\n]*?\s+score\s+(-?\d+)',log or '')]
    cost={'sdk_charged_cost':-sum(charges) if log is not None else None,'sdk_charged_actions':len(charges) if log is not None else None}
    if not re.search(r'^SATISFIABLE\s*$',text,re.M):return dict(goals=None,constraints=None,**cost)
    values=set((int(i),int(k)) for i,k in re.findall(r'value\((\d+),(\d+)\)',text))
    return dict(goals=sorted(i for i,k in values if k==40),constraints=sorted(i for i,k in values if k==20),**cost)
def feedback(r):
    p=path(r['result']['output'])/'server.log'
    return re.findall(r'^\s*\[([^\n]*\|[^\n]*)\]\s*$',p.read_text(errors='replace'),re.M) if p.exists() else []
def table(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    rr=[json.loads(l) for l in (OUT/'results.jsonl').read_text(encoding='utf8').splitlines()]
    assert len(rr)==6726
    indexed={r['key']:r for r in rr};cache={};fb={};pairs=[];unit=[];failed=[];cost_disagreements=[];grouped=collections.defaultdict(dict)
    for r in rr:
        o=official(r);cache[r['key']]=o;fb[r['key']]=feedback(r)
        if r['result'].get('official_score') is not None and r['result'].get('final_goals') is not None:
            assert len(o['goals'])==r['result']['final_goals'],r['key']
            assert len(o['constraints'])==r['result']['credited_constraints'],r['key']
        grouped[(r['suite'],r['id'],r['mode'],r['round'])][r['arm']]=r
        unit.append(dict(key=r['key'],official_goal_ids=json.dumps(o['goals']),official_constraint_ids=json.dumps(o['constraints']),sdk_charged_cost=o.get('sdk_charged_cost'),sdk_charged_actions=o.get('sdk_charged_actions')))
        if o.get('sdk_charged_cost') is not None and o['sdk_charged_cost']!=r['result'].get('action_cost'):cost_disagreements.append(dict(key=r['key'],action_stream_cost=r['result'].get('action_cost'),sdk_charged_cost=o['sdk_charged_cost']))
        for i,e in enumerate(fb[r['key']],1):
            if re.search(r'\bfalse\b',e):failed.append(dict(key=r['key'],suite=r['suite'],id=r['id'],stage=r['stage'],mode=r['mode'],round=r['round'],arm=r['arm'],action_index=i,feedback=e))
    table('OFFICIAL_IDS.csv',unit)
    if failed:table('FAILED_ACTIONS.csv',failed)
    if cost_disagreements:table('COST_DISAGREEMENTS.csv',cost_disagreements)
    for key,arms in grouped.items():
        if '177' not in arms:continue
        b=arms['177']
        for arm,a in arms.items():
            if arm=='177':continue
            ar,br=a['result'],b['result'];af,bf=fb[a['key']],fb[b['key']];p=0
            while p<min(len(af),len(bf)) and af[p]==bf[p]:p+=1
            changed=ar.get('base')!=br.get('base') or ar.get('final_goals')!=br.get('final_goals')
            ca,cb=cache[a['key']],cache[b['key']]
            lost=None if ca['goals'] is None or cb['goals'] is None else sorted(set(ca['goals'])-set(cb['goals']))
            gained=None if ca['goals'] is None or cb['goals'] is None else sorted(set(cb['goals'])-set(ca['goals']))
            row=dict(suite=key[0],id=key[1],mode=key[2],round=key[3],control=arm,first_public_feedback_divergence=p,
                     baseline_next_feedback=af[p] if p<len(af) else '<STOP>',latest_next_feedback=bf[p] if p<len(bf) else '<STOP>',
                     lost_official_goal_ids=json.dumps(lost),gained_official_goal_ids=json.dumps(gained),goal_or_base_changed=changed,
                     evidence=b['key']+'-vs-'+arm+'.md')
            pairs.append(row)
            file=OUT/'pair-evidence'/row['evidence']
            if not file.exists():continue
            lines=['\n## 官方目标与公共反馈补充','',json.dumps(row,ensure_ascii=False,indent=2),'',
                   '首个动作/反馈分叉是定位入口；关键决策须结合下列候选和停止原因。相同种子不保证动作分叉后还消费同一随机序列。']
            for title,r in [('基线',a),('最新版',b)]:
                lines+=['',f'### {title}完整调度/候选/执行/终态日志','']
                client=path(r['result']['output'])/'client.log'
                if client.exists():lines += [x for x in client.read_text(errors='replace').splitlines() if any(t in x for t in ('[Scheduler]','[GuardedDecision]','[3B][Candidate]','[3B][Deadline]','[Probe]','[3A][final]'))]
            with file.open('a',encoding='utf8') as f:f.write('\n'.join(lines)+'\n')
    table('DECISION_DIVERGENCES.csv',pairs)
    save=dict(runs=len(rr),official_ids_verified=sum(r['result'].get('official_score') is not None and r['result'].get('final_goals') is not None for r in rr),pairs=len(pairs),failed_actions=len(failed),cost_disagreements=cost_disagreements,scope='official final ASP IDs and SDK charged action costs; first raw public feedback/action mismatch; detailed candidate/stop logs. These are trace locators, not automatic causal labels.')
    (OUT/'TRACE_AUDIT.json').write_text(json.dumps(save,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(save,ensure_ascii=False))
if __name__=='__main__':main()
