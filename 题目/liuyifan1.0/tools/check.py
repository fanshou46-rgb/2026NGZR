#!/usr/bin/env python3
"""Static XML/2025-guide checks and independent witness state simulation."""
import copy
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from design import SUITE, facts

def location(objects,i):
    o=objects[i]
    return location(objects,o['inside']) if o.get('inside') else o['at']

def predicate(ins,objects,robot,hold):
    x=ins['x']; y=ins['y']; a=ins['action']; o=objects[x]
    if a=='near':
        near=(not o.get('inside') and not objects[y].get('inside') and location(objects,x)==location(objects,y))
        return not near if ins['kind']=='must_not' else near
    if a=='inside' or a=='putin': return o.get('inside')==y
    if a=='closed' or a=='close': return o['closed']
    if a=='opened' or a=='open': return not o['closed']
    if a=='goto': return robot==location(objects,x)
    if a=='puton': return hold!=x and not o.get('inside') and location(objects,x)==location(objects,y)
    if a=='give': return hold!=x and not o.get('inside') and location(objects,x)==location(objects,1)
    raise ValueError(a)

def simulate(c):
    objects={o['id']:copy.deepcopy(o) for o in c['objects']}
    robot=c['robot']; hold=0; cost=0; broken=set()
    constraints=[i for i in c['instructions'] if i['kind'] in ('must','must_not')]
    assert all(predicate(i,objects,robot,hold) for i in constraints),'initial constraint broken'
    for a in c['witness']:
        name=a[0]; x=a[1]; o=objects.get(x)
        if name=='Move':
            assert robot!=x
            robot=x
            if hold: objects[hold]['at']=x
            cost+=4
        elif name=='PickUp':
            assert hold==0 and o['size']=='small' and not o.get('inside') and location(objects,x)==robot
            hold=x; cost+=2
        elif name=='PutDown':
            assert hold==x
            hold=0; o['at']=robot; cost+=2
        elif name in ('Open','Close'):
            assert hold==0 and o.get('type')=='container' and location(objects,x)==robot
            assert o['closed']==(name=='Open')
            o['closed']=name=='Close'; cost+=2
        elif name=='PutIn':
            y=a[2]
            assert hold==x and not objects[y]['closed'] and location(objects,y)==robot
            o.pop('at',None); o['inside']=y; hold=0; cost+=2
        else: raise ValueError(name)
        for j,i in enumerate(constraints):
            if not predicate(i,objects,robot,hold): broken.add(j)
    goals=sum(predicate(i,objects,robot,hold) for i in c['instructions'] if i['kind']=='task')
    preserved=len(constraints)-len(broken) if goals else 0
    assert goals==c['expected_goals'],(c['id'],goals)
    assert preserved==c['expected_constraints'],(c['id'],preserved)
    base=goals*40+preserved*20-cost
    # These constructive bounds also establish the 200..1000 theoretical-score range.
    assert base>=200
    upper=c['goals']*40+c['constraints']*20+100
    assert upper<=1000
    return dict(reference_goals=goals,reference_constraints=preserved,
        reference_action_cost=cost,reference_base_score=base,
        conservative_score_upper_bound=upper,broken_constraint_indices=sorted(broken))

def check():
    rows=[]
    for c in json.loads((SUITE/'manifest.json').read_text(encoding='utf-8')):
        root=ET.parse(str(SUITE/(c['id']+'.xml'))).getroot(); env=root.find('env')
        expected='off' if c['stage']==1 else 'on'
        assert all(env.get(k)==expected for k in ('mis','err','ans'))
        objs=c['objects']; assert [o['id'] for o in objs]==list(range(1,len(objs)+1))
        assert [o['id'] for o in objs if o['sort']=='human']==[1]
        bigloc=[o['at'] for o in objs if o['size']=='big']; assert len(set(bigloc))==len(bigloc)
        identities=[(o['sort'],o.get('color')) for o in objs]; assert len(set(identities))==len(identities)
        actual=[]
        for tag in ('info','mis','err/r','extra'):
            actual+=re.findall(r'\([^()]+\)',env.findtext(tag) or '')
        expectedfacts=['(hold 0)','(plate 0)','(at 0 {})'.format(c['robot'])]
        expectedfacts += ['('+' '.join(map(str,f))+')' for o in objs for f in facts(o)]
        assert sorted(actual)==sorted(expectedfacts),'XML truth differs from manifest'
        it=root.findtext('instr'); depth=0
        for ch in it:
            depth+=(ch=='(')-(ch==')'); assert depth>=0
        assert depth==0 and it.strip().startswith('(:ins')
        assert it.strip()=='(:ins\n'+'\n'.join(i['it'] for i in c['instructions'])+'\n)'
        sentences=[s.strip()+'.' for s in root.findtext('nl').split('.') if s.strip()]
        assert len(sentences)==len(c['instructions'])
        keys=[]
        for i,s in zip(c['instructions'],sentences):
            keys.append((i['kind'],i['action'],i['x'],i['y']))
            assert re.sub(r'[^a-z .]','',s.lower())==i['nt'].lower(),'NT changes words'
            participants=[objs[i['x']-1]]+([objs[i['y']-1]] if i['y'] else [])
            assert sum(o['size']=='small' for o in participants)<=1
            if i['action']=='goto': assert not participants[0].get('inside')
            for o in participants:
                if o['size']=='small': assert o['color'] in i['it'] and o['color'] in i['nt'].lower()
        assert len(set(keys))==len(keys),'duplicate instruction'
        for field in c.get('mis',[])+c.get('extra',[]):
            assert field[0] in ('at','inside','plate','opened','closed')
        for r,w in c.get('errors',[]):
            assert r[0] in ('at','inside','plate','opened','closed') and w[0] in ('at','inside','opened','closed')
            assert r[1]==w[1] and r[1]!=0
        rows.append(dict(id=c['id'],status='pass',**simulate(c)))
    (SUITE/'static-validation.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS: six XMLs, unique instructions, IT/NT correspondence, true initial constraints, legal witness plans')
    return rows

if __name__=='__main__': check()
