#!/usr/bin/env python3
"""Deterministic authoring of six 2025-rule prototypes; Python 3.6+."""
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

SUITE = Path(__file__).resolve().parents[1]

def big(i, sort, loc, closed=None):
    o = dict(id=i, sort=sort, size='big', at=loc)
    if closed is not None:
        o.update(type='container', closed=closed)
    return o

def small(i, sort, color, at=None, inside=None):
    o = dict(id=i, sort=sort, size='small', color=color)
    o.update({'inside':inside} if inside is not None else {'at':at})
    return o

def phrase(o):
    return 'the ' + (o.get('color', '') + ' ' if 'color' in o else '') + o['sort']

def instr(kind, action, x, y=None):
    cond = '(sort X {})'.format(x['sort'])
    if 'color' in x: cond += ' (color X {})'.format(x['color'])
    if action in ('open','close') and kind == 'task': cond += ' (type X container)'
    if y:
        cond += ' (sort Y {})'.format(y['sort'])
        if 'color' in y: cond += ' (color Y {})'.format(y['color'])
        if action in ('putin','takeout','inside'): cond += ' (type Y container)'
    if action == 'give': pred = '(give human X)'
    else: pred = '({} X{})'.format(action, ' Y' if y else '')
    if kind == 'task':
        it = '(:task {} (:cond {}))'.format(pred, cond)
        if action == 'goto': nt = 'Go to {}.'.format(phrase(x))
        elif action == 'give': nt = 'Give {} to me.'.format(phrase(x))
        elif action in ('close','open'): nt = '{} {}.'.format(action.capitalize(), phrase(x))
        elif action == 'puton': nt = 'Put {} on {}.'.format(phrase(x), phrase(y))
        elif action == 'putin': nt = 'Put {} in {}.'.format(phrase(x), phrase(y))
        else: raise ValueError(action)
    else:
        info = '(:info {} (:cond {}))'.format(pred, cond)
        it = info if kind == 'info' else '({} {})'.format(':cons_not' if kind=='must_not' else ':cons_notnot',info)
        relation = {'inside':'in', 'near':'near', 'closed':'closed', 'opened':'opened'}[action]
        nt = '{} {} {}{}.'.format(phrase(x).capitalize(),
            'is' if kind == 'info' else 'must not be' if kind=='must_not' else 'must be', relation,
            ' '+phrase(y) if y else '')
    return dict(kind=kind, action=action, x=x['id'], y=y['id'] if y else None, it=it, nt=nt)

def action(name, *args): return [name] + list(args)

def transfer(obj, src, dst):
    return [action('Move',src),action('PickUp',obj),action('Move',dst),action('PutDown',obj)]

def cases():
    furniture = [big(1,'human',1),big(2,'table',2),big(3,'chair',3),big(4,'sofa',4)]
    objects = furniture + [small(5,'book','red',2),small(6,'cup','blue',2),
        small(7,'bottle','white',3),small(8,'can','green',3),
        small(9,'remotecontrol','yellow',4),small(10,'book','black',4)]
    yield dict(id='01', stage=1, title='自由终态汇聚', robot=2, objects=objects,
        instructions=[instr('task','goto',o) for o in objects[4:]]+[instr('task','goto',objects[1])],
        witness=sum([transfer(i,3 if i<9 else 4,2) for i in (7,8,9,10)],[]),
        intent='六个不同小物体 goto 与 table goto；搬到 table 后停留，同时完成七个终态目标。',
        expected_goals=7, expected_constraints=0,
        strategy='保留桌边红书、蓝杯，将白瓶、绿罐、黄遥控器、黑书搬到桌边，最终停在位置2。')
    objects = furniture + [small(5,'book','red',3),small(6,'cup','blue',3),
        small(7,'bottle','white',4),small(8,'can','green',4)]
    ins=[]
    for o in objects[4:]: ins += [instr('task','goto',o),instr('task','puton',o,objects[1])]
    ins += [instr('task','goto',objects[1])]
    yield dict(id='02', stage=1, title='搬运与到达共享终态', robot=2, objects=objects,
        instructions=ins, witness=sum([transfer(i,3 if i<7 else 4,2) for i in range(5,9)],[]),
        intent='四个 puton、四个小物体 goto、一个 table goto；同一布局满足九个不同目标。',
        expected_goals=9, expected_constraints=0,
        strategy='四件物体全部放到桌边，最终停在桌边；后续 goto 不应再移动已完成的物体。')
    objects = furniture + [small(5,'book','red',2),small(6,'cup','blue',2),
        small(7,'bottle','white',3),small(8,'can','green',3)]
    ins=[instr('must','near',objects[4],objects[1]),instr('must','near',objects[5],objects[1])]
    ins += [instr('task','goto',objects[4]),instr('task','goto',objects[5])]
    for o in objects[6:]: ins += [instr('task','puton',o,objects[1]),instr('task','goto',o)]
    ins += [instr('task','goto',objects[1])]
    yield dict(id='03', stage=2, title='must-near 纠错与缺失补全', robot=2, objects=objects,
        mis=[['at',6,2]], errors=[(['at',5,2],['at',5,4])], instructions=ins,
        witness=transfer(7,3,2)+transfer(8,3,2), intent='红书位置错误、蓝杯位置缺失；两个真实成立的 must-near 以 table 为可靠锚点。',
        expected_goals=7, expected_constraints=2,
        strategy='约束推断红书和蓝杯均在桌边并保留原位，只搬白瓶、绿罐到桌边。')
    objects=[big(1,'human',1),big(2,'table',2),big(3,'cupboard',3,True),big(4,'microwave',4,True),
        small(5,'book','red',inside=3),small(6,'cup','blue',2),small(7,'bottle','white',2),small(8,'can','green',2)]
    ins=[instr('info','closed',objects[3]),instr('must','inside',objects[4],objects[2]),
         instr('must','closed',objects[2])]
    ins += [instr('task','putin',o,objects[3]) for o in objects[5:]]
    ins += [instr('task','close',objects[3]),instr('task','goto',objects[3]),instr('task','close',objects[2])]
    plan=[action('Move',4),action('Open',4)]
    for i in (6,7,8): plan += [action('Move',2),action('PickUp',i),action('Move',4),action('PutIn',i,4)]
    plan += [action('Close',4)]
    yield dict(id='04', stage=2, title='容器状态纠错与合法语言扰动', robot=2, objects=objects,
        extra=[['closed',4]], errors=[(['inside',5,3],['at',5,4]),(['closed',3],['opened',3])],
        instructions=ins, noise=True, witness=plan,
        intent='错误红书位置、错误 cupboard 开关状态；extra 用 info 补充 microwave 关闭状态；NT只扰动物体名和颜色词。',
        expected_goals=6, expected_constraints=2,
        strategy='用 must-inside、must-closed 修正 cupboard 信息，保持红书和柜门不动；将蓝杯、白瓶、绿罐放入 microwave 并关门。')
    objects=[big(1,'human',1),big(2,'cupboard',2,True),big(3,'table',3),
        small(4,'book','red',2),small(5,'cup','blue',2),small(6,'bottle','white',2),small(7,'can','green',2)]
    ins=[instr('must','closed',objects[1])]+[instr('task','putin',o,objects[1]) for o in objects[3:]]
    ins += [instr('task','close',objects[1]),instr('task','goto',objects[1])]
    plan=[action('Open',2)]
    for i in range(4,8): plan += [action('PickUp',i),action('PutIn',i,2)]
    plan += [action('Close',2)]
    yield dict(id='05', stage=1, title='牺牲一个约束解锁四个目标', robot=2, objects=objects,
        instructions=ins, witness=plan, expected_goals=6, expected_constraints=0,
        intent='must-closed 与四个 putin 冲突；柜门重新关闭仍不能挽回全过程约束分。',
        strategy='打开 cupboard，依次放入四件物体，再关门；牺牲20约束分，新增160目标分，参考动作成本20。')
    objects=[big(1,'human',1),big(2,'table',2),big(3,'cupboard',3,True),big(4,'chair',4),
        small(5,'cup','red',inside=3),small(6,'book','blue',4),small(7,'bottle','white',4)]
    ins=[instr('must','closed',objects[2]),instr('must','inside',objects[4],objects[2]),
         instr('must_not','near',objects[4],objects[0]),instr('task','give',objects[4])]
    for o in objects[5:]: ins += [instr('task','puton',o,objects[1]),instr('task','goto',o)]
    ins += [instr('task','goto',objects[1])]
    plan=[action('PickUp',6),action('Move',2),action('PutDown',6)] + transfer(7,4,2)
    yield dict(id='06', stage=1, title='放弃低收益目标保住三个约束', robot=4, objects=objects,
        instructions=ins, witness=plan, expected_goals=5, expected_constraints=3,
        intent='交付红杯将破坏 must-closed、must-inside、must-not-near human 三个不同约束；完成另外五个兼容目标更有利。',
        strategy='不取红杯、不打开 cupboard；只搬蓝书、白瓶到桌边，完成五个目标并维护三个约束。')

def facts(o):
    i=o['id']; result=[['sort',i,o['sort']],['size',i,o['size']]]
    if 'color' in o: result += [['color',i,o['color']]]
    result += [['inside',i,o['inside']]] if 'inside' in o else [['at',i,o['at']]]
    if o.get('type'): result += [['type',i,'container'],['closed' if o['closed'] else 'opened',i]]
    return result

def sexpr(f): return '('+' '.join(map(str,f))+')'

def render(c):
    omitted=c.get('mis',[])+c.get('extra',[])+[r for r,w in c.get('errors',[])]
    info=['(hold 0) (plate 0) (at 0 {})'.format(c['robot'])]
    info += [' '.join(sexpr(f) for f in facts(o) if f not in omitted) for o in c['objects']]
    flag='off' if c['stage']==1 else 'on'
    nt=[i['nt'] for i in c['instructions']]
    if c.get('noise'):
        allowed=set(o['sort'] for o in c['objects'])|{'red','blue','white','green'}
        def noise(m):
            s=m.group(0)
            return s[:1].upper()+'#'+s[1:] if s.lower() in allowed else s
        nt=[re.sub(r'[A-Za-z]+',noise,s) for s in nt]
    c['rendered_nt']=nt
    content=['<?xml version="1.0" encoding="UTF-8"?>','<test>',
        '<env mis="{0}" err="{0}" ans="{0}">'.format(flag),'<info>',*info,'</info>',
        '<mis>'+ ' '.join(map(sexpr,c.get('mis',[])))+'</mis>', '<err>',
        '<r>'+' '.join(sexpr(r) for r,w in c.get('errors',[]))+'</r>',
        '<w>'+' '.join(sexpr(w) for r,w in c.get('errors',[]))+'</w>','</err>',
        '<extra>'+' '.join(map(sexpr,c.get('extra',[])))+'</extra>','</env>',
        '<instr>','(:ins',*[escape(i['it']) for i in c['instructions']],')','</instr>',
        '<nl>',*[escape(s) for s in nt],'</nl>','</test>','']
    return '\n'.join(content)

def main():
    manifest=[]
    for c in cases():
        (SUITE/(c['id']+'.xml')).write_text(render(c),encoding='utf-8')
        (SUITE/'reference-plans').mkdir(exist_ok=True)
        (SUITE/'reference-plans'/(c['id']+'.txt')).write_text(
            '\n'.join(' '.join(map(str,a)) for a in c['witness'])+'\n',encoding='utf-8')
        c['goals']=sum(i['kind']=='task' for i in c['instructions'])
        c['constraints']=sum(i['kind'] in ('must','must_not') for i in c['instructions'])
        manifest.append(c)
    (SUITE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (SUITE/'test.list').write_text(''.join(c['id']+'.xml\n' for c in manifest),encoding='utf-8')
    print('Authored {} prototypes'.format(len(manifest)))

if __name__=='__main__': main()
