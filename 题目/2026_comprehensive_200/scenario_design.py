"""Guide-compliant designs: seven goals, one small object per instruction."""
from build_suite import (SPECS, COLORS, World, Planner, task, restriction, formal,
                         english, reason, holds, replay, require, make_xml)

class Scenario:
    def __init__(self, category, number):
        self.category, self.number = category, number
        self.title, _, _, self.kind = SPECS[category]
        self.g_count, self.c_count = 7, 31
        self.flip_family = category in ('B01','C01')
        self.seed = (number-1)//2 if self.flip_family else number-1
        self.forbid_left = self.flip_family and number%2==0
        self.tags = [tag for tag,cats in [('E04',('A02','C02')),('E05',('A01','A03')),('E07',('B05','D03'))] if category in cats]
        if self.flip_family and number<=4: self.tags.append('E10')
        sorts = ['human','table','desk','cupboard','closet','microwave','refrigerator','sofa']
        objects={i:dict(sort=s,size='big',**({'type':'container'} if i in range(4,8) else {})) for i,s in enumerate(sorts,1)}
        import random
        locs=list(range(2,9)); random.Random(category+str(self.seed)).shuffle(locs)
        at={1:1,**dict(zip(range(2,9),locs))}
        self.dest=2 if self.seed%2==0 else 3
        self.source=5-self.dest
        self.w=World(objects,at[self.source],at,{},set())
        self.roles={}
        for role,sort,color,place in [('left','can','red',self.source),('right','cup','white',self.source),
                                      ('book','book','white',('inside',4)),('bottle','bottle','green',self.source),
                                      ('carry','can','black',8),('blue','bottle','blue',8)]:
            self.add(role,sort,color,place)
        r=self.roles
        if 'E05' in self.tags or category in ('B03','C03'):
            self.w.at.pop(r['blue']); self.w.inside[r['blue']]=4
        if category=='C02':
            self.w.at.pop(r['blue']); self.w.inside[r['blue']]=5
        if category=='B03':
            self.w.at.pop(r['right']); self.w.inside[r['right']]=5
        if category in ('B02','B04'):
            self.w.hand=r['bottle']; self.w.plate=r['left']
            self.w.at.pop(r['bottle']); self.w.at.pop(r['left'])
        if category=='D01': self.w.at[r['right']]=self.w.at[8]
        self.dual = category in ('B01','C01','B05','D03','C04')
        self.final_pair = (r['left'],r['right']) if self.flip_family or category=='C04' else (r['right'],r['carry'])
        if self.forbid_left: self.final_pair=self.final_pair[::-1]
        self.jobs=[]
        def job(pred,*args):
            t=task(pred,*args); self.jobs.append(t); return t
        give=job('give',1,r['book'])
        put=job('putin',r['bottle'],7 if category=='C02' else 5)
        self.goals=[give,put,task('close',4),task('close',5),task('open',7),task('pickup',r['carry']),task('goto',self.dest)]
        if 'E05' in self.tags or category=='C03':
            self.goals[4]=job('takeout',r['blue'],4)
        if category in ('B02','B04'):
            self.jobs.remove(put)
            self.goals[1]=job('putdown',r['bottle'])
            self.goals[4]=job('give',1,r['left'])
        if category=='B03':
            self.jobs.remove(put)
            self.goals[1]=job('putin',r['blue'],5)
            self.goals[4]=job('putin',r['right'],4)
        if self.dual:
            ordered_pair = sorted(self.final_pair)
            self.goals[4]=task('pickup',ordered_pair[0])
            self.goals[5]=task('pickup',ordered_pair[1])
            if category=='C04': self.goals[6]=task('pickup',r['carry'])
        if category=='D01':
            self.jobs=[job for job in self.jobs if job==give]
            self.goals=[give,job('puton',r['left'],self.dest),job('puton',r['right'],self.dest),
                        task('goto',r['left']),task('goto',r['right']),task('close',4),task('pickup',r['carry'])]
        if category=='D02':
            self.goals=[give,put,task('close',4),task('pickup',r['carry']),
                        task('goto',1),task('goto',self.source),task('goto',self.dest)]
        self.risk=[]
        if category=='C05':
            for k,(sort,color,dest) in enumerate([('cup','green',self.dest),('book','black',self.source)]):
                self.add('risk'+str(k),sort,color,('inside',6))
                self.risk.append(task('puton',r['risk'+str(k)],dest))
            self.jobs=[job('puton',r['left'],self.dest),give,put]
            self.goals=self.jobs+[task('open',7),task('pickup',r['carry'])]+self.risk
        self.core=[restriction('closed',6,positive=True)]
        # Protect a stationary small object relative to furniture; never small-small near.
        if not self.dual and category not in ('B02','B04','D01','C05'):
            self.core.append(restriction('near',r['left'],self.source,positive=True))
        if category=='C01': self.core.append(restriction('near',r['blue'],8,positive=True))
        if self.dual and category!='C04': self.core.append(restriction('plate',self.final_pair[1]))
        if not self.dual: self.core.append(restriction('plate',r['carry']))
        self.core += [restriction('plate',r['book']),restriction('plate',r['bottle'])]
        if category=='C03': self.core.append(restriction('closed',4,positive=True))
        if category=='C02': self.core.append(restriction('closed',5,positive=True))
        if category=='B04':
            for big in range(1,9):
                if big!=self.dest:
                    self.core.append(restriction('give',1,r['bottle'],inner='task') if big==1 else restriction('puton',r['bottle'],big,inner='task'))
        if category=='C05':
            for t in self.risk:
                obj,dest=t.args
                self.core += [restriction('inside',obj,6,positive=True),restriction('near',obj,dest)]
        self.w.invariant()
        require(len(self.goals)==7,'goal quota')

    def add(self,role,sort,color,place):
        i=len(self.w.objects)+1
        color=COLORS[(COLORS.index(color)+self.seed)%6]
        self.w.objects[i]=dict(sort=sort,size='small',color=color)
        self.roles[role]=i
        if isinstance(place,tuple): self.w.inside[i]=place[1]
        else: self.w.at[i]=self.w.at[place]

    def plan(self,variant='primary'):
        p=Planner(self.w,visibility='E04' in self.tags); r=self.roles
        if 'E05' in self.tags: p.emit('askloc',4)
        if self.category in ('B02','B04'):
            p.move(self.w.at[self.dest]); p.emit('putdown',r['bottle'])
            p.emit('fromplate',r['left']); p.move(self.w.at[1]); p.emit('putdown',r['left'])
        for j in self.jobs:
            obj=j.args[1] if j.pred=='give' else j.args[0]
            if self.category=='C03' and variant=='keep_cupboard_closed' and self.w.inside.get(obj)==4: continue
            p.deliver(j)
        if self.category=='C05' and variant=='execute_risky_branch':
            for j in self.risk: p.deliver(j)
            p.door(6,False)
        p.door(4,False); p.door(5,False)
        if any(t.pred=='open' and t.args==(7,) for t in self.goals): p.door(7,True)
        if self.dual:
            plate,hand=self.final_pair
            if variant=='wrong_slot': plate,hand=hand,plate
            if self.category=='C04' and variant=='alternative_subset': hand=r['carry']
            p.fetch(plate); p.emit('toplate',plate); p.fetch(hand)
        else:
            p.fetch(r['carry'])
            if variant=='wrong_slot': p.emit('toplate',r['carry'])
        p.move(self.w.at[1 if variant=='finish_at_human' else self.dest])
        return p.actions

    def assemble(self):
        comparison={'C03':'keep_cupboard_closed','C04':'alternative_subset','C05':'execute_risky_branch','D02':'finish_at_human'}
        variants=['primary', comparison.get(self.category,'wrong_slot')]
        action_plans={v:self.plan(v) for v in variants}
        traces=[w for actions in action_plans.values() for w in replay(self.w,[],actions)['states']]
        active=sorted({a for g in self.goals for a in g.args if self.w.objects[a]['size']=='small'})
        candidates=[]
        # Short resource restrictions first; then mix alternate-container and route bans.
        excluded=set(self.final_pair) if self.dual else {self.roles['carry']}
        candidates.extend(restriction('plate',o) for o in active if o not in excluded)
        for k in range(8):
            for o in active:
                if k<4: candidates.append(restriction('inside',o,k+4))
                candidates.append(restriction('near',o,k+1))
        cons=list(self.core); seen={t.key() for t in cons}
        for t in candidates:
            if len(cons)>=31: break
            if t.key() not in seen and all(holds(w,t) for w in traces): cons.append(t); seen.add(t.key())
        # Keep complete protocol envelopes below the repository's conservative 3900-byte guard.
        # Points are derived from actual legal clauses; no task inflation to reach a nominal score.
        from xml.etree import ElementTree as ET
        while True:
            self.terms=self.goals+cons
            sizes=[]
            for stage in (1,2):
                root=ET.fromstring(make_xml(self,stage)[0]); compact=lambda s:' '.join((s or '').split())
                for tag in ('instr','nl'):
                    packet='<test><name>'+f'{self.category}-{self.number:02d}-s{stage}.xml'+'</name><es>(:domain '+compact(root.findtext('env/info'))+'  '+compact(root.findtext('env/err/w'))+')</es><ts>'+compact(root.findtext(tag))+'</ts></test>'
                    sizes.append(len(packet.encode()))
            if max(sizes)<3900: break
            require(len(cons)>len(self.core),'core packet too long')
            cons.pop()
        self.c_count=len(cons); self.nominal=280+20*self.c_count
        plans=[]
        for name,actions in action_plans.items():
            rr=replay(self.w,self.terms,actions)
            plans.append(dict(name=name,role='primary' if name=='primary' else 'counterexample' if self.kind=='full' else 'comparison',
                actions=actions,expected_completed_goals=len(rr['goal_ids']),expected_violated_constraints=len(rr['violated_constraint_ids']),
                completed_goal_ids=rr['goal_ids'],violated_constraint_ids=rr['violated_constraint_ids']))
        expected={'C03':(7,1),'C04':(6,0),'C05':(5,0),'D02':(5,0)}
        require((plans[0]['expected_completed_goals'],plans[0]['expected_violated_constraints'])==expected.get(self.category,(7,0)),f'{self.category}: {plans[0]}')
        if self.kind=='full': require(plans[1]['expected_violated_constraints']==1,'counterexample must isolate one restriction')
        focus=dict(core_constraint_ids=list(range(8,8+len(self.core))),pair_destination=self.dest)
        if 'E04' in self.tags: focus['visibility']=[self.roles['book'],4]
        if 'E05' in self.tags: focus['query_container']=4
        if 'E07' in self.tags: focus['final_slots']=[self.final_pair[1],self.final_pair[0]]
        if 'E10' in self.tags: focus['forbidden_plate_object']=self.final_pair[1]
        proofs={
            'C03':(20,'多个目标要求取出关闭碗柜中的物体。完成全部目标必然损失保持关闭的20分；不全部完成则至少损失一个40分目标。主方案只损失该约束。'),
            'C04':(40,'三个不同物体分别要求最终携带；手与托盘共两个槽位，最终最多满足两个。主方案只遗漏其中一个目标且保持全部约束。'),
            'C05':(80,'五个安全目标和两个风险目标。每完成一个风险目标增加40分，却必然损失保持inside与禁止目的地near两条约束共40分；执行任一风险目标还会损失共用闭门约束20分。完成五个安全目标且不违约达到毛分上界。'),
            'D02':(80,'三个goto分别指向不同地点的固定家具，最终最多满足一个。主方案仅遗漏两个goto目标且保持全部约束。')}
        if self.kind=='tradeoff':
            loss,statement=proofs[self.category]
            proof=dict(kind='structural_upper_bound',theoretical_gross_upper=self.nominal-loss,statement=statement+f'目标与约束毛分上界为{self.nominal-loss}；未计动作成本或时间。')
        else: proof=dict(kind='constructive',statement='主参考动作逐步合法，完成全部七个目标，并从初态起保持全部约束。')
        self.reference=dict(category=self.category,title=self.title,scene=self.number,nominal_gross=self.nominal,
            roles=self.roles,focus=focus,proof=proof,plans=plans,platform_executed=False,scores_measured=False,
            validation_scope='offline truth-informed witness, not autonomous Stage 2 policy',
            clauses=[dict(id=i,**t.data(),english=english(t,self.w.objects),purpose=reason(t,self.w.objects) if t.kind=='constraint' else '最终状态目标') for i,t in enumerate(self.terms,1)])
        return self
