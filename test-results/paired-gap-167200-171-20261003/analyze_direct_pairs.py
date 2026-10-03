#!/usr/bin/env python3
"""Read-only paired diagnosis with official answer-set reconciliation."""
import argparse, collections, csv, hashlib, itertools, json, re, shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
CATEGORIES=['qualification-too-strict','probe-coverage-gap','no-location-clue','constraint-gate-strict','legacy-lucky','ordering-cascade','group-search-gap','retry-bound','deadline','terminal/score-disagreement','other']

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8') as f: json.dump(v,f,ensure_ascii=False,indent=2)
def csvsave(p,rows,fields):
    with p.open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for row in rows: w.writerow({k:json.dumps(row.get(k),ensure_ascii=False) if isinstance(row.get(k),(list,dict)) else row.get(k) for k in fields})
def clean(p): return re.sub(r'\x1b\[[0-9;]*m','',p.read_text(errors='replace'))
def events(p):
    return [dict(index=i+1,line=n,action=m.group(1).strip(),feedback=m.group(2).strip()) for i,(n,m) in enumerate(
        (n,m) for n,l in enumerate(p.read_text(errors='replace').splitlines(),1) for m in [re.match(r'^\s*\[([^|]*)\|([^\]]*)\]',l)] if m)]
def values(p):
    t=p.read_text();assert 'SATISFIABLE' in t
    pairs=set((int(a),int(b)) for a,b in re.findall(r'value\((\d+),(\d+)\)',t))
    return {40:sorted(a for a,b in pairs if b==40),20:sorted(a for a,b in pairs if b==20)}
def firstdiff(a,b,feedback=True):
    i=0; keys=('action','feedback') if feedback else ('action',)
    while i<min(len(a),len(b)) and all(a[i][k]==b[i][k] for k in keys): i+=1
    return dict(common_prefix=i,event_index=i+1 if i<max(len(a),len(b)) else None,old=a[i] if i<len(a) else None,new=b[i] if i<len(b) else None)

def ground_tasks(run):
    text=(run/'runtime/vbase.lp').read_text()
    props=collections.defaultdict(set)
    for p,n in re.findall(r'\b([a-z][a-z0-9_]*)\((\d+)\)\.',text): props[p].add(int(n))
    result={}
    for line in (run/'runtime/vtask.lp').read_text().splitlines():
        m=re.search(r'task\((\d+),\s*(\w+)\(([^)]*)\)\)\s*:\s*(.*?)\s*\}1',line)
        assert m,line
        number,verb,args,conds=m.groups();args=[a.strip() for a in args.split(',')]
        variables=sorted(set(a for a in args if a[0].isupper()))
        choices={v:set(props['obj']) for v in variables}
        for prop,v in re.findall(r'(\w+)\(([A-Z])\)',conds): choices[v]&=props[prop]
        bindings=[]
        for vals in itertools.product(*(sorted(choices[v]) for v in variables)):
            assignment=dict(zip(variables,vals));bindings.append([assignment.get(a,a) for a in args])
        result[int(number)]=dict(verb=verb,bindings=bindings,asp=line)
    return result

def initial_state(case):
    import xml.etree.ElementTree as ET
    env=ET.parse(str(case)).getroot().find('env'); s=dict(at={},inside={},opened={},hold=0,plate=0)
    text=' '.join(''.join(e.itertext()) for name in ('info','mis','err/r','extra') for e in env.findall(name))
    for verb,args in re.findall(r'\((at|inside|hold|plate|opened|closed)\s+([\d\s]+)\)',text):
        a=[int(v) for v in args.split()]
        if verb in ('at','inside'): s[verb][a[0]]=a[1]
        elif verb in ('opened','closed'): s['opened'][a[0]]=verb=='opened'
        else:s[verb]=a[0]
    return s
def satisfies(s,t):
    for a in t['bindings']:
        x=a[0];y=a[1] if len(a)>1 else None;stored=x in (s['hold'],s['plate'])
        v=t['verb']
        if v=='goto' and s['at'].get(x) is not None and s['at'].get(x)==s['at'].get(0):return True
        if v=='pickup' and stored:return True
        if v=='putin' and s['inside'].get(x)==y:return True
        if v=='takeout' and s['inside'].get(x)!=y:return True
        if v in ('puton','give'):
            if v=='give': x=a[-1];y=next(iter(s.get('human',[1])));stored=x in (s['hold'],s['plate'])
            if not stored and s['at'].get(x) is not None and s['at'].get(x)==s['at'].get(y):return True
        if v=='putdown' and not stored:return True
        if v in ('open','close') and s['opened'].get(x)==(v=='open'):return True
    return False
def replay(case,ev,tasks):
    s=initial_state(case); history={i:[0] if satisfies(s,t) else [] for i,t in tasks.items()}
    for e in ev:
        a=e['action'].split();v=a[0].lower();ids=[int(x) for x in a[1:] if x.isdigit()]
        if e['feedback']=='true':
            loc=s['at'].get(0)
            if v=='move':
                s['at'][0]=ids[0]
                for held in (s['hold'],s['plate']):
                    if held:s['at'][held]=ids[0]
            elif v in ('pickup','takeout'):
                s['hold']=ids[0];s['inside'].pop(ids[0],None);s['at'][ids[0]]=loc
            elif v=='putdown':
                s['hold']=0;s['at'][ids[0]]=loc;s['inside'].pop(ids[0],None)
            elif v=='putin':
                s['hold']=0;s['inside'][ids[0]]=ids[1];s['at'].pop(ids[0],None)
            elif v=='toplate':s['plate']=s['hold'];s['hold']=0
            elif v=='fromplate':s['hold']=s['plate'];s['plate']=0
            elif v in ('open','close'):s['opened'][ids[0]]=v=='open'
        for i,t in tasks.items():
            if satisfies(s,t):history[i].append(e['index'])
    return s,history

def excerpt(lines,markers):
    picked=set()
    for marker in markers:
        hits=[n for n,l in enumerate(lines,1) if marker in l]
        picked.update(hits[:2]+hits[-2:])
    return [dict(line=n,text=lines[n-1]) for n in sorted(picked)]
def refs(run,entries):return [dict(path='evidence/'+run.name+'/client.log',**e) for e in entries]
def measures(rows):
    x={'pairs':len(rows)}
    for a in ('baseline','current'):
        x[a]={k:sum(r[a][k] for r in rows) for k in ('final_goals','credited_constraints','base','action_cost','official_score')}
        x[a]['timeouts']=sum(bool(r[a]['platform_timed_out'] or r[a]['external_timeout']) for r in rows)
        x[a]['failures']=sum(r[a]['status']!='ok' for r in rows)
    x['goal_pairs']={k:sum((r['current']['final_goals']-r['baseline']['final_goals'])*sign>0 for r in rows) for k,sign in [('increase',1),('decrease',-1)]}
    x['goal_pairs']['equal']=len(rows)-sum(x['goal_pairs'].values())
    return x

def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;out.mkdir(exist_ok=False); raw=load(a.runs/'results.json');review=load(HERE/'case_review.json')
    assert len(raw)==284 and len(set(r['id'] for r in raw))==71
    assert len(set((r['id'],r['mode'],r['round']) for r in raw))==284
    for cid in set(r['id'] for r in raw): assert {(r['mode'],r['round']) for r in raw if r['id']==cid}=={('it',1),('it',2),('nt',1),('nt',2)}
    pairs=[];gaps=[];goalrows=[];traces=[];checks=[]
    for r in raw:
        arms={};ev={};vv={};canon={}
        for arm in ('baseline','current'):
            run=Path(r[arm]['output']); arms[arm]=run;ev[arm]=events(run/'server.log');vv[arm]=values(run/'runtime/vanswer.txt')
            cost=sum(4 if e['action'].split()[0].lower()=='move' else 1 if e['action'].split()[0].lower()=='sense' else 2 for e in ev[arm])
            base=40*len(vv[arm][40])+20*len(vv[arm][20])-cost
            assert r[arm]['final_goals']==len(vv[arm][40]) and r[arm]['credited_constraints']==len(vv[arm][20])
            assert r[arm]['base']==base and r[arm]['action_cost']==cost
            assert '[RDFW_TEST_SEED] 20260924' in (run/'server.log').read_text()
            cm=re.search(r'\[3A\]\[final\] goals=(\d+)/(\d+) \(unknown=(\d+)\), constraints=(\d+)/(\d+) \(unknown=(\d+)\), base_score=(-?\d+)',clean(run/'client.log'))
            canon[arm]=dict(zip(('G','total_G','unknown_G','C','total_C','unknown_C','base'),map(int,cm.groups()))) if cm else None
            checks.append(dict(pair='%s/%s/r%d'%(r['id'],r['mode'],r['round']),arm=arm,goals_ok=True,base_ok=True,seed_ok=True))
        key='%s-%s-r%d'%(r['id'],r['mode'],r['round']);d=firstdiff(ev['baseline'],ev['current']);ad=firstdiff(ev['baseline'],ev['current'],False)
        lost=sorted(set(vv['baseline'][40])-set(vv['current'][40]));gained=sorted(set(vv['current'][40])-set(vv['baseline'][40]))
        rec=dict(pair=key,id=r['id'],case=r['path'],sha256=r['sha256'],stage=r['stage'],mode=r['mode'],round=r['round'],order=r['order'],seed=20260924,
            G_old=r['baseline']['final_goals'],G_new=r['current']['final_goals'],C_old=r['baseline']['credited_constraints'],C_new=r['current']['credited_constraints'],
            base_old=r['baseline']['base'],base_new=r['current']['base'],K_old=r['baseline']['action_cost'],K_new=r['current']['action_cost'],
            score_old=r['baseline']['official_score'],score_new=r['current']['official_score'],raw_score_old=r['baseline']['raw_score'],raw_score_new=r['current']['raw_score'],
            seconds_old=r['baseline']['platform_seconds'],seconds_new=r['current']['platform_seconds'],status_old=r['baseline']['status'],status_new=r['current']['status'],
            timeout_old=r['baseline']['platform_timed_out'] or r['baseline']['external_timeout'],timeout_new=r['current']['platform_timed_out'] or r['current']['external_timeout'],
            goal_loss=r['baseline']['final_goals']-r['current']['final_goals'],base_loss=r['baseline']['base']-r['current']['base'],
            goal_component_loss=40*(r['baseline']['final_goals']-r['current']['final_goals']),constraint_component_loss=20*(r['baseline']['credited_constraints']-r['current']['credited_constraints']),
            cost_component_loss=r['current']['action_cost']-r['baseline']['action_cost'],old_only_goal_ids=lost,new_only_goal_ids=gained,
            first_behavior_index=d['event_index'],first_action_index=ad['event_index'],old_first_behavior=d['old'],new_first_behavior=d['new'],common_prefix=d['common_prefix'],
            canonical_old=canon['baseline'],canonical_new=canon['current'],primary='',secondary=[],safety='',mechanism='',safety_note='',evidence='')
        assert rec['base_loss']==rec['goal_component_loss']+rec['constraint_component_loss']+rec['cost_component_loss']
        if r['stage']==2 and rec['goal_loss']>0:
            rv=review.get(r['id'],dict(primary='other',secondary=[],safety='unresolved',mechanism='待审阅新出现的配对差异',safety_note='',old_markers=['[3A][final]'],new_markers=['[3A][final]']))
            if 'same_review_as' in rv:rv=review[rv['same_review_as']]
            rec.update({k:rv[k] for k in ('primary','secondary','safety','mechanism','safety_note')});rec['evidence']='pair-evidence/'+key+'.md'
            tasks=ground_tasks(arms['baseline']);assert tasks==ground_tasks(arms['current'])
            excerpts={};replays={}
            for arm in ('baseline','current'):
                run=arms[arm]; lines=clean(run/'client.log').splitlines();excerpts[arm]=refs(run,excerpt(lines,rv['old_markers' if arm=='baseline' else 'new_markers']))
                state,history=replay(Path(r['path']),ev[arm],tasks);replays[arm]=history
                assert {gid for gid,task in tasks.items() if satisfies(state,task)}==set(vv[arm][40]),'Replay/official mismatch: '+key+'/'+arm
                dest=out/'evidence'/run.name;dest.mkdir(parents=True)
                for fname in ('client.log','server.log','summary.json'):shutil.copyfile(str(run/fname),str(dest/fname))
                for fname in ('vanswer.txt','vstate.lp','vbase.lp','vtask.lp','vcons.lp'):shutil.copyfile(str(run/'runtime'/fname),str(dest/fname))
                shutil.copyfile(str(run/'runtime/tests/case.xml'),str(dest/'case.xml'))
            goaltrace=[]
            for gid in lost:
                h=replays['baseline'][gid];assert h,'No observed truth witness for lost goal '+key+'/'+str(gid)
                start=next((i for i in h if all(j in h for j in range(i,len(ev['baseline'])+1))),h[-1])
                witness=ev['baseline'][start-1] if start else dict(index=0,action='initial_truth',feedback='')
                assert start==0 or witness['feedback']=='true','Winning goal has no positive physical-action witness: '+key+'/'+str(gid)
                grow=dict(pair=key,id=r['id'],mode=r['mode'],round=r['round'],official_goal_id=gid,task=tasks[gid],
                    category=rv.get('goal_override',{}).get(str(gid),rv['primary']),safety=rv['safety'],goal_points_lost=40,
                    old_final_continuous_satisfaction_from_event=start,old_success_witness=witness,
                    old_server_log='evidence/'+arms['baseline'].name+'/server.log',new_server_log='evidence/'+arms['current'].name+'/server.log',
                    new_ever_satisfied=bool(replays['current'][gid]),new_satisfied_event_indices=replays['current'][gid],mechanism=rv['mechanism'])
                goalrows.append(grow);goaltrace.append(grow)
            tr=dict(pair=key,first_behavior=d,first_action=ad,classification=rv,official_old=vv['baseline'],official_new=vv['current'],canonical=canon,
                excerpts=excerpts,old_only_goals=goaltrace,new_only_goals=gained)
            if rv['safety']=='recoverable-safe-observed':
                assert canon['baseline'] and len(vv['baseline'][20])==canon['baseline']['total_C'],'Incomplete constraint credit in safe classification: '+key
            traces.append(tr);gaps.append(rec)
            md=['# '+key+' — '+rec['primary'],'',rec['mechanism'],'',rec['safety_note'],'',
                'G %s→%s；C %s→%s；K %s→%s；基础分 %s→%s。'%(rec['G_old'],rec['G_new'],rec['C_old'],rec['C_new'],rec['K_old'],rec['K_new'],rec['base_old'],rec['base_new']),
                '基础分损失 = 目标 %s + 约束 %s + 成本 %s = %s。'%(rec['goal_component_loss'],rec['constraint_component_loss'],rec['cost_component_loss'],rec['base_loss']),'',
                '首次行为分叉（包含动作反馈）：事件 %s；旧 `%s`；新 `%s`。'%(d['event_index'],d['old'],d['new']),'',
                '旧独有官方目标 ID：%s；新独有：%s。'%(lost,gained),'','## 目标终态证据','']
            for g in goaltrace:md.append('- 官方 goal%s `%s`，类别 `%s`；旧版持续满足起点：事件%s `%s`。'%(g['official_goal_id'],g['task'],g['category'],g['old_final_continuous_satisfaction_from_event'],g['old_success_witness']))
            for arm in ('baseline','current'):
                md+=['','## '+arm+' 客户端决策证据','']
                for e in excerpts[arm]:md+=['[%s:L%d](../%s#L%d)'%(Path(e['path']).name,e['line'],e['path'],e['line']),'```text',e['text'],'```']
                md+=['','[完整服务端动作反馈](../evidence/'+arms[arm].name+'/server.log) · [官方评分答案](../evidence/'+arms[arm].name+'/vanswer.txt)']
            dest=out/'pair-evidence';dest.mkdir(exist_ok=True);(dest/(key+'.md')).write_text('\n'.join(md)+'\n',encoding='utf-8')
        pairs.append(rec)
    fields=list(pairs[0]);csvsave(out/'pairs.csv',pairs,fields);csvsave(out/'gaps.csv',gaps,fields)
    csvsave(out/'goal-gaps.csv',goalrows,list(goalrows[0]));save(out/'pair-traces.json',traces)
    summary=[]
    for cat in CATEGORIES:
        part=[r for r in gaps if r['primary']==cat]; goals=[g for g in goalrows if g['category']==cat]
        summary.append(dict(category=cat,pairs=len(part),unique_inputs=len(set(r['id'] for r in part)),goal_loss=sum(r['goal_loss'] for r in part),base_loss=sum(r['base_loss'] for r in part),
            goal_component_loss=sum(r['goal_component_loss'] for r in part),constraint_component_loss=sum(r['constraint_component_loss'] for r in part),cost_component_loss=sum(r['cost_component_loss'] for r in part),
            goal_level_old_only_count=len(goals),goal_level_points=40*len(goals),safe_recoverable_pairs=sum(r['safety']=='recoverable-safe-observed' for r in part),
            representative=part[0]['evidence'] if part else '',secondary_pair_count=sum(cat in r['secondary'] for r in gaps)))
    csvsave(out/'category-summary.csv',summary,list(summary[0]))
    ms={scope:measures([r for r in raw if scope=='all' or scope=='stage'+str(r['stage']) or scope==r['mode']]) for scope in ('all','stage1','stage2','it','nt')}
    ms['negative_stage2']=dict(pairs=len(gaps),unique_inputs=len(set(r['id'] for r in gaps)),goal_loss=sum(r['goal_loss'] for r in gaps),base_loss=sum(r['base_loss'] for r in gaps),
        safe= {k:sum(r[k] for r in gaps if r['safety']=='recoverable-safe-observed') for k in ('goal_loss','base_loss')},safe_pairs=sum(r['safety']=='recoverable-safe-observed' for r in gaps),
        constraint_trade_pairs=sum(r['safety']=='successful-constraint-trade' for r in gaps),legacy_lucky_pairs=sum(r['primary']=='legacy-lucky' for r in gaps))
    save(out/'metrics.json',ms)
    repeat=[]
    for cid in sorted(set(r['id'] for r in raw)):
        for mode in ('it','nt'):
            rr=[r for r in raw if r['id']==cid and r['mode']==mode]
            for arm in ('baseline','current'):
                repeat.append(dict(id=cid,mode=mode,arm=arm,same_actions=rr[0][arm]['action_sequence']==rr[1][arm]['action_sequence'],same_G=rr[0][arm]['final_goals']==rr[1][arm]['final_goals'],same_base=rr[0][arm]['base']==rr[1][arm]['base']))
    save(out/'repeat-audit.json',repeat)
    freeze=load(a.runs/'final-audit.json');assert freeze['products_unchanged'] and freeze['inputs_unchanged'] and not freeze['violations']
    audit=dict(pairs=284,runs=len(checks),inputs=71,full_grid=True,official_goal_and_constraint_recount=True,action_cost_and_base_recount=True,component_reconciliation=True,
        category_sum_goal_loss=sum(s['goal_loss'] for s in summary),category_sum_base_loss=sum(s['base_loss'] for s in summary),goal_rows=len(goalrows),
        unexpected_gap_ids=sorted(set(r['id'] for r in gaps)-set(review)),repeat_differences=[r for r in repeat if not all(r[k] for k in ('same_actions','same_G','same_base'))],freeze=freeze,
        safety_definition='Observed old-only goals achieved with real positive action feedback / final official truth; every official constraint credited in baseline. A proposed new policy counterfactual was not executed.',
        causal_scope='Trace-supported mechanism under one seed; repeated rounds are not independent random samples. First action divergence alone is not sufficient to identify the loss mechanism.')
    assert audit['category_sum_goal_loss']==ms['negative_stage2']['goal_loss'] and audit['category_sum_base_loss']==ms['negative_stage2']['base_loss']
    save(out/'analysis-validation.json',audit)
    save(out/'source-receipt.json',dict(runs_root=str(a.runs),results_sha256=sha(a.runs/'results.json'),input_audit_sha256=sha(a.runs/'input-audit.json'),review_sha256=sha(HERE/'case_review.json'),analysis_sha256=sha(Path(__file__)),authority='Official SDK server actions and vanswer value(id,40/20), supported by unchanged source code and original XML; canonical client summaries are separately reported.'))
    print(json.dumps(dict(metrics=ms['negative_stage2'],categories=summary,repeat_differences=audit['repeat_differences']),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
