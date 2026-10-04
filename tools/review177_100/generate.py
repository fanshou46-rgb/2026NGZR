"""45 new dependency structures, paired information levels; no planner scores read."""
from common import *
import collections, copy, random, re, xml.etree.ElementTree as ET
sys.path.insert(0,str(OLD))
import build_suite as b
import scenario_design as sd
import offline_check as oc
import guide_audit as ga
COUNTS={'A01':3,'A02':3,'A03':3,'A04':2,'A05':3,'B01':2,'B02':3,'B03':3,'B04':2,'B05':2,'C01':2,'C02':3,'C03':3,'C04':2,'C05':3,'D01':2,'D02':2,'D03':2}
PAIRED={'B01','C01','C03','C05'}
class NewScenario(sd.Scenario):
    def __init__(self,cat,n):
        # New seeds only choose decoration; novelty is the dependency transformation below.
        number=41+n if cat not in PAIRED else 41+(0 if n<=2 else n)
        if cat in ('B01','C01'):number=41 if n==1 else 42
        super().__init__(cat,number)
        self.number=n;self.title+='：新增跨柜取出依赖' if self.kind=='full' else '：新增运输与门依赖'
        r=self.roles
        if self.kind=='full':
            target=7 if cat in PAIRED and n<=2 else (7,5,4)[n-1]
            if cat=='B03' and target==5:target=4 # takeout and putin cannot require opposite final membership
            if cat=='C02':target=4 if n==2 else 7 # protected closet remains closed
            self.w.at.pop(r['blue'],None);self.w.inside[r['blue']]=target
            self.jobs=[b.task(j.pred,*((r['blue'],target) if j.pred=='takeout' and j.args[0]==r['blue'] else j.args)) for j in self.jobs]
            self.goals=[b.task(t.pred,*((r['blue'],target) if t.pred=='takeout' and t.args[0]==r['blue'] else t.args)) for t in self.goals]
            if cat in ('A01','A03'):
                replacement=b.task('puton',r['blue'],self.dest);slot=2
            else:
                replacement=b.task('takeout',r['blue'],target)
                slot=next(i for i,t in enumerate(self.goals) if t.pred=='close' and t.args==(4,))
            self.goals[slot]=replacement
            if not any(j.args[0]==r['blue'] for j in self.jobs):self.jobs.append(b.task('takeout',r['blue'],target))
            if replacement.pred=='puton':self.jobs.append(replacement)
            if n==3 and cat not in ('B02','B04'):
                # Third structure shares the source with the book, rather than merely rotating colors.
                self.w.at.pop(r['bottle'],None);self.w.inside[r['bottle']]=4
                if cat=='B03':self.w.inside[r['right']]=7
            # The old stationary blue object is now an active cross-container object.
            if cat=='C01':self.core=[t for t in self.core if not(t.pred=='near' and t.args[0]==r['blue'] and t.positive)]
            if cat=='C01':self.core.append(b.restriction('near',r['carry'],8,positive=True))
            if cat=='A02':self.w.robot=self.w.at[7]
            if cat=='A03':self.w.inside[r['book']]=7
            if cat=='A04':
                self.w.inside.pop(r['book'],None);self.w.at[r['book']]=self.w.at[self.dest]
                self.w.objects[r['book']]['sort']='can'
            if cat=='A05':self.w.robot=self.w.at[self.dest]
            if cat=='D03':
                old=b.task('putin',r['bottle'],5);new=b.task('puton',r['bottle'],self.dest)
                self.jobs=[new if j==old else j for j in self.jobs];self.goals=[new if t==old else t for t in self.goals]
                self.final_pair=(r['left'],r['carry'])
                self.goals[4]=b.task('pickup',r['left']);self.goals[5]=b.task('pickup',r['carry']);self.goals[6]=b.task('goto',r['bottle'])
            self.novelty=f'新增从容器{target}取出蓝物的依赖；独立来源、复用投放目的柜、共享交付来源柜三类拓扑，与双槽或最终聚集耦合。'
        elif cat=='C03':
            self.w.at.pop(r['bottle'],None);self.w.inside[r['bottle']]=4 if n==3 else 7
            self.protected=7 if n==2 else 4
            self.core=[b.restriction('closed',self.protected,positive=True) if t.pred=='closed' and t.args==(4,) else t for t in self.core]
            self.novelty='瓶子新增从微波炉到衣柜的运输依赖；反事实仅切换受保护门。'
        elif cat=='C05':
            self.w.at.pop(r['carry'],None);self.w.inside[r['carry']]=4 if n==3 else 5
            if n==2:
                target=r['risk0'];self.core=[b.restriction('plate',target) if t.pred=='near' and t.args==(target,self.dest) else t for t in self.core]
            self.novelty='最终携带物新增衣柜取出依赖；风险分支与共享闭门约束耦合。反事实仅替换风险0的一条禁止关系。'
            # Drop an unused distractor rather than exceed the wire-size budget.
            removed={r['blue'],r['right']};ids={i:j for j,i in enumerate([i for i in self.w.objects if i not in removed],1)}
            self.w.objects={ids[i]:o for i,o in self.w.objects.items() if i not in removed}
            self.w.at={ids[i]:loc for i,loc in self.w.at.items() if i not in removed}
            self.w.inside={ids[i]:ids[c] for i,c in self.w.inside.items() if i not in removed}
            self.roles={role:ids[i] for role,i in self.roles.items() if i not in removed};self.roles['blue']=self.roles['risk1']
            def remap(t):return b.task(t.pred,*[ids[i] for i in t.args]) if t.kind=='task' else b.restriction(t.pred,*[ids[i] for i in t.args],positive=t.positive,inner=t.inner)
            self.jobs=list(map(remap,self.jobs));self.goals=list(map(remap,self.goals));self.risk=list(map(remap,self.risk));self.core=list(map(remap,self.core))
        elif cat=='C04':
            self.w.at.pop(r['carry'],None);self.w.inside[r['carry']]=7 if n==1 else 4
            self.novelty='第三个携带目标新增闭柜取出依赖，容量冲突叠加开门空手要求。'
        else:
            old=b.task('give',1,r['book']);new=b.task('puton',r['book'],8 if n==1 else 2)
            self.jobs=[new if j==old else j for j in self.jobs];self.goals=[new if t==old else t for t in self.goals]
            self.novelty='书的交付目标改为沙发送达，运输终点与三个固定goto收尾竞争。'
        self.w.invariant();assert len(self.goals)==7
    def plan(self,variant='primary'):
        p=b.Planner(self.w,visibility='E04' in self.tags);r=self.roles
        if 'E05' in self.tags:p.emit('askloc',4)
        if self.category in ('B02','B04'):
            p.move(self.w.at[self.dest]);p.emit('putdown',r['bottle']);p.emit('fromplate',r['left']);p.move(self.w.at[1]);p.emit('putdown',r['left'])
        for j in self.jobs:
            obj=j.args[1] if j.pred=='give' else j.args[0]
            if self.category=='C03' and variant=='keep_protected_closed' and self.w.inside.get(obj)==self.protected:continue
            p.deliver(j)
        if self.category=='C05' and variant=='execute_risky_branch':
            for j in self.risk:p.deliver(j)
            p.door(6,False)
        p.door(4,False);p.door(5,False)
        if any(t.pred=='open' and t.args==(7,) for t in self.goals):p.door(7,True)
        if self.dual:
            plate,hand=self.final_pair
            if variant=='wrong_slot':plate,hand=hand,plate
            if self.category=='C04' and variant=='alternative_subset':
                hand=r['carry'];p.door(7,True) # before occupying the hand
            p.fetch(plate);p.emit('toplate',plate);p.fetch(hand)
        else:
            p.fetch(r['carry'])
            if variant=='wrong_slot':p.emit('toplate',r['carry'])
        p.move(self.w.at[1 if variant=='finish_at_human' else self.dest])
        return p.actions

def plans(s):
    alt={'C03':'keep_protected_closed','C04':'alternative_subset','C05':'execute_risky_branch','D02':'finish_at_human'}.get(s.category,'wrong_slot')
    return {'primary':s.plan(),alt:s.plan(alt)}
def assemble(s, group):
    action_plans=plans(s);traces=[w for other in group for aa in plans(other).values() for w in oc.replay(other.w,[],aa)['states']]
    cons=list(s.core);keys={t.key() for other in group for t in other.core}
    active=sorted({a for g in s.goals for a in g.args if s.w.objects[a]['size']=='small'})
    candidates=[b.restriction('plate',o) for o in active]
    candidates += [b.restriction(pred,o,big) for pred,bigs in [('inside',range(4,8)),('near',range(1,9))] for big in bigs for o in active]
    for t in candidates:
        if len(cons)>=30:break
        if t.key() not in keys and all(oc.holds(w,t) for w in traces):cons.append(t);keys.add(t.key())
    assert len(cons)==30,(s.category,len(cons))
    s.terms=s.goals+cons
    # The packet guard is measured with the final filenames and a full envelope below.
    s.g_count=7;s.c_count=30;s.nominal=880
    pp=[]
    for name,aa in action_plans.items():
        rr=oc.replay(s.w,s.terms,aa)
        pp.append(dict(name=name,role='primary' if name=='primary' else 'counterexample' if s.kind=='full' else 'comparison',actions=aa,
            expected_completed_goals=len(rr['goal_ids']),expected_violated_constraints=len(rr['violated_constraint_ids']),
            completed_goal_ids=rr['goal_ids'],violated_constraint_ids=rr['violated_constraint_ids']))
    expected={'C03':(7,1),'C04':(6,0),'C05':(5,0),'D02':(5,0)}.get(s.category,(7,0))
    assert (pp[0]['expected_completed_goals'],pp[0]['expected_violated_constraints'])==expected,(s.category,pp)
    proofs={'C03':(20,'全解必须打开受保护容器；全解至少失去一条20分约束，不全解至少失去40分目标。'),
        'C04':(40,'三个不同携带目标而只有手/托盘两个槽，至少失去一个目标。'),
        'C05':(80,'枚举两个风险目标的四种完成子集：每项至少失去inside约束，另有目的地或托盘限制；任意取出还失去共享闭门约束。四种毛分均不超过五安全目标方案。'),
        'D02':(80,'三个固定不同地点goto最终至多满足一个，至少失去两个目标。')}
    proof=dict(kind='constructive',statement='真值参考完成7目标，保持30约束；不构成自主Stage2策略或最优耗时证明。')
    if s.kind=='tradeoff':
        loss,statement=proofs[s.category];proof=dict(kind='structural_upper_bound',theoretical_gross_upper=880-loss,statement=statement)
    s.reference=dict(category=s.category,title=s.title,scene=s.number,roles=s.roles,novelty=s.novelty,nominal_gross=880,proof=proof,plans=pp,
        platform_executed=False,scores_measured=False,validation_scope='truth-informed witness only',
        clauses=[dict(id=i,**t.data(),english=b.english(t,s.w.objects),purpose=b.reason(t,s.w.objects) if t.kind=='constraint' else '最终状态目标') for i,t in enumerate(s.terms,1)])
    return s

def main():
    BANK.mkdir(parents=True,exist_ok=False);entries=[];flips=[];offline=[]
    for cat,count in COUNTS.items():
        scenarios=[NewScenario(cat,n) for n in range(1,count+1)]
        for s in scenarios:
            group=scenarios[:2] if cat in PAIRED and s.number<=2 else [s]
            assemble(s,group);pid=f'{cat}-{s.number:02d}';ref=BANK/'references'/(pid+'.json');save(ref,s.reference)
            card=[f'# {pid} {s.title}',s.novelty,f'类别：{s.kind}；7目标、30约束，名义毛分880。',s.reference['proof']['statement'],
                'Stage1提供完整事实；Stage2隐藏/误导位置并启用随机回答。参考仅证明物理可解性。', '## 初态',json.dumps(b.environment_facts(s),ensure_ascii=False),'## 目标及约束']
            card += [f"{c['id']}. {c['english']}" for c in s.reference['clauses']]
            card += ['## 参考与比较方案',json.dumps(s.reference['plans'],ensure_ascii=False,indent=2)]
            (BANK/'cards').mkdir(exist_ok=True);(BANK/'cards'/(pid+'.md')).write_text('\n\n'.join(card)+'\n',encoding='utf8')
            for stage in (1,2):
                cid=pid+f'-s{stage}';path=BANK/'cases'/f'stage{stage}'/(cid+'.xml');path.parent.mkdir(parents=True,exist_ok=True)
                text,perturb=b.make_xml(s,stage);path.write_text(text,encoding='utf8')
                issues=ga.audit(path);data=oc.load_case(path);assert not issues,(cid,issues)
                assert len({t.key() for t in data['terms']})==len(data['terms'])
                assert max(data['packets'].values())<3900,(cid,data['packets'])
                for plan in s.reference['plans']:
                    actual=oc.replay(data['world'],data['terms'],plan['actions']);assert actual['goal_ids']==plan['completed_goal_ids'];assert actual['violated_constraint_ids']==plan['violated_constraint_ids']
                entries.append(dict(id=cid,pair_id=pid,category=cat,family=cat,stage=stage,kind=s.kind,path=path.relative_to(BANK).as_posix(),reference=ref.relative_to(BANK).as_posix(),goals=7,constraints=30,nominal_gross=880,information_perturbation=perturb,sha256=sha(path),novelty=s.novelty,cluster=f'{cat}-counterfactual' if cat in PAIRED and s.number<=2 else pid))
                offline.append(dict(id=cid,guide_issues=issues,max_packet=max(data['packets'].values()),reference_verified=True))
        if cat in PAIRED:
            a,c=scenarios[:2];assert b.environment_facts(a)==b.environment_facts(c)
            assert a.goals==c.goals
            da={t.key() for t in a.terms};dc={t.key() for t in c.terms};assert len(da-dc)==len(dc-da)==1,(cat,da-dc,dc-da)
            flips.append(dict(left=f'{cat}-01',right=f'{cat}-02',removed=list(da-dc),added=list(dc-da)))
    # Five distinct mutations per invalid family, from fresh cases.
    normal=[e for e in entries if e['kind']=='full' and e['stage']==1]
    b.HERE=BANK
    invalid=b.make_invalid(normal)
    selected=[e for e in invalid if int(e['id'][-2:])%2==1]
    keep={e['path'] for e in selected}
    for e in invalid:
        if e['path'] not in keep:(BANK/e['path']).unlink()
    for e in selected:
        e.update(stage=1, family=e['category'],cluster=e['id'])
        try:oc.load_case(BANK/e['path']);raise AssertionError('negative accepted offline '+e['id'])
        except (oc.Invalid,ET.ParseError) as exc:e['offline_error']=str(exc)
    entries+=selected;assert collections.Counter(e['kind'] for e in entries)=={'full':70,'tradeoff':20,'invalid':10}
    save(BANK/'catalogue.json',dict(title='1.7.7 独立100题对照',cases=entries,counterfactual_pairs=flips,seed_policy='generation does not read robot results',new_structure='new cross-container extraction/dependency/terminal transport topology; old families retained'))
    save(BANK/'offline-audit.json',dict(normal=90,guide_passed=90,references=90,invalid_expected=10,counterfactual_scene_pairs=4,cases=offline))
    save(BANK/'invalid/expected_errors.json',selected)
    save(BANK/'run_manifest.json',[dict(id=e['id'],path=e['path'],stage=e['stage'],mode=m) for e in entries if e['kind']!='invalid' for m in ('it','nt')])
    for stage in (1,2):(BANK/'cases'/f'stage{stage}'/'test.list').write_text('\n'.join(Path(e['path']).name for e in entries if e['kind']!='invalid' and e['stage']==stage)+'\n',encoding='utf8')
    print('GENERATED 100; offline/guide passed 90; 4 exact counterfactual scene pairs',flush=True)
if __name__=='__main__':main()
