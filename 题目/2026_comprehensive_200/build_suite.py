#!/usr/bin/env python3
"""Construct 200 questions and offline witnesses, without launching the platform."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
from offline_check import World, Term, holds, label, replay, load_case, require

HERE = Path(__file__).resolve().parent
SPECS = {
    'A01': ('位置缺失与依赖恢复', 7, 31, 'full'),
    'A02': ('错误位置与关系纠正', 7, 31, 'full'),
    'A03': ('不可靠回答与任务重排', 7, 31, 'full'),
    'A04': ('相似对象与语义绑定', 7, 31, 'full'),
    'A05': ('已满足目标的破坏与恢复', 7, 31, 'full'),
    'B01': ('双携带目标与槽位约束', 7, 31, 'full'),
    'B02': ('手与托盘占用后的解锁', 7, 31, 'full'),
    'B03': ('两柜互换与关门收尾', 7, 31, 'full'),
    'B04': ('暂存位置交叉限制', 7, 31, 'full'),
    'B05': ('交付收尾与双槽资源分配', 7, 31, 'full'),
    'C01': ('正负接近约束共同作用', 7, 31, 'full'),
    'C02': ('容器保护与受限搜索', 7, 31, 'full'),
    'C03': ('一次约束损失与整组收益', 7, 31, 'tradeoff'),
    'C04': ('三个携带目标与双槽容量冲突', 7, 31, 'tradeoff'),
    'C05': ('保底目标与继续执行的收益', 7, 31, 'tradeoff'),
    'D01': ('可移动对象聚集式多 goto', 7, 31, 'full'),
    'D02': ('固定目标终点选择', 7, 31, 'tradeoff'),
    'D03': ('聚集交付与最终携带联合收尾', 7, 31, 'full'),
}
COLORS = ['red', 'white', 'green', 'black', 'yellow', 'blue']
SMALL_SORTS = ['can', 'cup', 'bottle', 'book', 'remotecontrol']


def task(pred, *args):
    return Term('task', pred, tuple(args))


def restriction(pred, *args, positive=False, inner='info'):
    return Term('constraint', pred, tuple(args), positive, inner)


def description(objects, obj, var):
    o = objects[obj]
    result = f'(sort {var} {o["sort"]})'
    if o['size'] == 'small': result += f'(color {var} {o["color"]})'
    return result


def formal(t, objects):
    if t.pred == 'give':
        call = '(give human X)'
        cond = description(objects, t.args[1], 'X')
    else:
        variables = ['X', 'Y'][:len(t.args)]
        call = '(' + t.pred + ' ' + ' '.join(variables) + ')'
        cond = ''.join(description(objects, o, v) for o, v in zip(t.args, variables))
    if (t.kind == 'task' or t.inner == 'task') and t.pred in ('open', 'close'):
        cond += '(type X container)'
    if (t.kind == 'task' or t.inner == 'task') and t.pred in ('putin', 'takeout'):
        cond += '(type Y container)'
    body = f'(:{"task" if t.kind == "task" else t.inner} {call} (:cond {cond}))'
    if t.kind == 'constraint': body = f'(:cons_{"notnot" if t.positive else "not"} {body})'
    return body


def english(t, objects):
    n = [label(objects, x) for x in t.args]
    if t.kind == 'constraint' and t.inner == 'info':
        copula = ' must ' + ('' if t.positive else 'not ') + 'be '
        if t.pred == 'near': suffix = 'near ' + n[1]
        elif t.pred == 'inside': suffix = 'in ' + n[1]
        elif t.pred == 'plate': suffix = 'on the plate'
        elif t.pred in ('opened', 'closed'): suffix = t.pred
        else: raise ValueError(t)
        return (n[0] + copula + suffix).capitalize() + '.'
    if t.pred == 'puton': body = f'put {n[0]} on {n[1]}'
    elif t.pred == 'putin': body = f'put {n[0]} in {n[1]}'
    elif t.pred == 'give': body = f'give {n[1]} to {n[0]}'
    elif t.pred == 'pickup': body = f'pick up {n[0]}'
    elif t.pred == 'putdown': body = f'put {n[0]} down'
    elif t.pred == 'goto': body = f'go to {n[0]}'
    elif t.pred == 'open': body = f'open {n[0]}'
    elif t.pred == 'close': body = f'close {n[0]}'
    elif t.pred == 'takeout': body = f'take out {n[0]} from {n[1]}'
    else: raise ValueError(t)
    if t.kind == 'constraint': body = 'do not ' + body
    return body.capitalize() + '.'


def reason(t, objects):
    n = [label(objects, x) for x in t.args]
    if t.inner == 'task': return f'限制腾手暂存：{english(t, objects)}'
    if t.pred == 'near' and t.positive:
        return f'{n[0]} 与 {n[1]} 保持位置关系；移动该小物体离开对应家具会使关系失效。'
    if t.pred == 'near':
        return f'限制运输路线或暂存地点：{n[0]} 到达 {n[1]} 的位置会触发违约。'
    if t.pred == 'plate': return f'限制携带资源分配：{n[0]} 不可借托盘腾手。'
    if t.pred == 'inside' and t.positive: return f'保留容器归属：取出 {n[0]} 会永久失去这条约束。'
    if t.pred == 'inside': return f'限制容器缓冲：{n[0]} 不能暂放入 {n[1]}。'
    return f'门状态保护：{english(t, objects)}'


class Planner:
    def __init__(self, world, visibility=False):
        self.w = world.copy()
        self.actions = []
        self.visibility = visibility

    def emit(self, *action):
        self.w.step(list(action))
        self.actions.append(list(action))

    def move(self, loc):
        if self.w.robot != loc: self.emit('move', loc)

    def door(self, obj, opened):
        if (obj in self.w.opened) != opened:
            self.move(self.w.position(obj))
            if self.visibility and obj == 4 and opened: self.emit('sense')
            self.emit('open' if opened else 'close', obj)
            if self.visibility and obj == 4 and opened: self.emit('sense')

    def fetch(self, obj):
        require(not self.w.hand and obj != self.w.plate, 'planner fetch needs empty hand')
        if obj in self.w.inside:
            c = self.w.inside[obj]
            self.door(c, True)
            self.move(self.w.position(c))
            self.emit('takeout', obj, c)
        else:
            self.move(self.w.position(obj))
            self.emit('pickup', obj)

    def deliver(self, t):
        if holds(self.w, t): return
        if t.pred == 'putdown':
            require(self.w.hand == t.args[0], 'putdown target must already be held')
            self.emit('putdown', t.args[0])
            return
        if t.pred == 'takeout':
            self.fetch(t.args[0])
            self.emit('putdown', t.args[0])
            return
        if t.pred == 'give': obj, dest = t.args[1], t.args[0]
        else: obj, dest = t.args
        if t.pred == 'putin': self.door(dest, True)
        self.fetch(obj)
        self.move(self.w.position(dest))
        self.emit('putin', obj, dest) if t.pred == 'putin' else self.emit('putdown', obj)

    def pair(self, plate_item, hand_item, dest):
        require(not self.w.hand and not self.w.plate, 'pair needs both slots')
        require(self.w.same(plate_item, hand_item), 'bound pair initially split')
        self.fetch(plate_item)
        self.emit('toplate', plate_item)
        self.fetch(hand_item)
        self.move(self.w.position(dest))
        self.emit('putdown', hand_item)
        self.emit('fromplate', plate_item)
        self.emit('putdown', plate_item)



def environment_facts(s):
    w = s.w
    facts = [('hold', str(w.hand)), ('plate', str(w.plate)), ('at', '0', str(w.robot))]
    for obj, attrs in sorted(w.objects.items()):
        for key in ('sort', 'size', 'color'):
            if key in attrs: facts.append((key, str(obj), attrs[key]))
        if obj in w.at: facts.append(('at', str(obj), str(w.at[obj])))
        if obj in w.inside: facts.append(('inside', str(obj), str(w.inside[obj])))
        if attrs.get('type') == 'container':
            facts.append(('type', str(obj), 'container'))
            facts.append(('opened' if obj in w.opened else 'closed', str(obj)))
    return facts


def make_xml(s, stage):
    truth = environment_facts(s)
    info, missing, right, wrong = list(truth), [], [], []
    def conceal(fact):
        require(fact in info, f'cannot conceal {fact}')
        info.remove(fact)
        missing.append(fact)
    def falsify(fact, fake):
        require(fact in info and fake != fact, f'cannot falsify {fact}')
        info.remove(fact)
        right.append(fact)
        wrong.append(fake)
    def location(obj):
        return ('inside', str(obj), str(s.w.inside[obj])) if obj in s.w.inside else ('at', str(obj), str(s.w.at[obj]))
    if stage == 2:
        if 'E05' in s.tags:
            conceal(('at', '4', str(s.w.at[4])))
            conceal(location(s.roles['carry']))
            target = s.roles['bottle']
            falsify(location(target), ('at', str(target), str(s.w.at[7])))
        elif 'E04' in s.tags:
            target = s.roles['book']
            falsify(location(target), ('inside', str(target), '6' if s.category == 'C02' else '5'))
            conceal(location(s.roles['carry']))
        else:
            conceal(location(s.roles['book']))
            target = s.roles['blue']
            false_fact = ('at', str(target), str(s.w.at[6]))
            falsify(location(target), false_fact)
    render_facts = lambda fs: ' '.join('(' + ' '.join(f) + ')' for f in fs)
    root = ET.Element('test')
    flag = 'off' if stage == 1 else 'on'
    env = ET.SubElement(root, 'env', mis=flag, err=flag, ans=flag)
    ET.SubElement(env, 'info').text = '\n' + render_facts(info) + '\n'
    ET.SubElement(env, 'mis').text = render_facts(missing)
    err = ET.SubElement(env, 'err')
    ET.SubElement(err, 'r').text = render_facts(right)
    ET.SubElement(err, 'w').text = render_facts(wrong)
    ET.SubElement(env, 'extra').text = ''
    ET.SubElement(root, 'instr').text = '\n(:ins\n' + '\n'.join(formal(t, s.w.objects) for t in s.terms) + '\n)\n'
    ET.SubElement(root, 'nl').text = '\n' + '\n'.join(english(t, s.w.objects) for t in s.terms) + '\n'
    ET.indent(root, space='')
    body = '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding='unicode', short_empty_elements=False) + '\n'
    perturbation = dict(missing=[list(x) for x in missing], true_facts=[list(x) for x in right],
                        false_facts=[list(x) for x in wrong], stochastic_answers_enabled=stage == 2,
                        note='答案随机性仅由ans开关启用，本次未运行平台、未强制任何实际回答序列。')
    return body, perturbation


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def write_json(path, data):
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def make_invalid(entries):
    valid_sources = [e for e in entries if e['kind'] == 'full' and e['stage'] == 1]
    cases = []
    for index in range(1, 11):
        source = valid_sources[index - 1]
        original = (HERE / source['path']).read_text(encoding='utf-8')
        kind = (index - 1) // 2
        if kind == 0:
            body, layer, mutation = original.replace('</nl>', '', 1), 'xml', 'missing_nl_end_tag'
        elif kind == 1:
            body, layer, mutation = original.replace('<nl>\n', '<nl>\n&\n', 1), 'xml', 'unescaped_ampersand'
        elif kind == 2:
            body, layer, mutation = original.replace('(:ins\n', '(:ins(\n', 1), 'syntax', 'unbalanced_it_parenthesis'
        elif kind == 3:
            body, layer, mutation = original.replace('(pickup X)', '(pickup X Y)', 1), 'domain', 'wrong_task_arity'
        else:
            body, layer, mutation = original.replace('(pickup X)', '(teleport X)', 1), 'domain', 'unknown_task_predicate'
        require(body != original, 'invalid mutation had no effect')
        cid = f'X01-{index:02d}'
        path = HERE / 'invalid' / (cid + '.xml')
        write_text(path, body)
        cases.append(dict(id=cid, category='X01', kind='invalid', path=path.relative_to(HERE).as_posix(),
                          source_path=source['path'], expected_layer=layer, mutation=mutation,
                          tags=[], sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    for index in range(1, 11):
        source = valid_sources[index + 9]
        original = (HERE / source['path']).read_text(encoding='utf-8')
        root = ET.fromstring(original)
        lines = [x for x in root.findtext('nl').splitlines() if x.strip()]
        parsed = load_case(HERE / source['path'])
        kind = (index - 1) // 2
        if kind == 0:
            clause = next(i for i, t in enumerate(parsed['terms']) if t.kind == 'task' and t.pred == 'pickup')
            term = parsed['terms'][clause]
            other = next(i for i, o in parsed['world'].objects.items() if o['size'] == 'small' and i != term.args[0])
            lines[clause] = english(task('pickup', other), parsed['world'].objects)
            mutation = 'target_object_replaced'
        elif kind == 1:
            clause = next(i for i, x in enumerate(lines) if ' must not ' in x)
            lines[clause] = lines[clause].replace(' must not ', ' must ', 1)
            mutation = 'negation_removed'
        elif kind == 2:
            clause = next(i for i, t in enumerate(parsed['terms']) if t.kind == 'constraint' and t.pred == 'inside' and not t.positive)
            lines[clause] = lines[clause].replace(' be in ', ' be near ', 1)
            mutation = 'inside_changed_to_near'
        elif kind == 3:
            clause = next(i for i, t in enumerate(parsed['terms']) if t.kind == 'task' and t.pred == 'pickup')
            lines.pop(clause)
            mutation = 'one_sentence_omitted'
        else:
            clause = next(i for i, t in enumerate(parsed['terms']) if t.kind == 'task' and t.pred == 'close')
            lines[clause] = lines[clause].replace('Close ', 'Open ', 1)
            mutation = 'door_target_reversed'
        root.find('nl').text = '\n' + '\n'.join(lines) + '\n'
        body = '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding='unicode', short_empty_elements=False) + '\n'
        cid = f'X02-{index:02d}'
        path = HERE / 'invalid' / (cid + '.xml')
        write_text(path, body)
        cases.append(dict(id=cid, category='X02', kind='invalid', path=path.relative_to(HERE).as_posix(),
                          source_path=source['path'], expected_layer='semantics', mutation=mutation,
                          changed_clause=clause + 1, tags=[], sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    return cases


def main():
    from scenario_design import Scenario
    entries, flips = [], []
    for category in SPECS:
        for scene in range(1, 6):
            s = Scenario(category, scene).assemble()
            pair_id = f'{category}-{scene:02d}'
            reference_path = HERE / 'references' / (pair_id + '.json')
            write_json(reference_path, s.reference)
            for stage in (1, 2):
                cid = f'{pair_id}-s{stage}'
                path = HERE / 'cases' / f'stage{stage}' / (cid + '.xml')
                body, perturbation = make_xml(s, stage)
                write_text(path, body)
                entries.append(dict(id=cid, pair_id=pair_id, category=category, title=s.title,
                                    scene=scene, stage=stage, kind=s.kind, tags=s.tags,
                                    goals=s.g_count, constraints=s.c_count, nominal_gross=s.nominal,
                                    path=path.relative_to(HERE).as_posix(),
                                    reference=reference_path.relative_to(HERE).as_posix(),
                                    information_perturbation=perturbation,
                                    sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
            print(f'Generated {pair_id}', flush=True)
    for category in ('B01', 'C01'):
        for left, right in ((1, 2), (3, 4)):
            for stage in (1, 2): flips.append([f'{category}-{left:02d}-s{stage}', f'{category}-{right:02d}-s{stage}'])
    entries.extend(make_invalid(entries))
    catalogue = dict(title='2026 综合 200 题：离线正确性检查版', cases=entries,
                     counterfactual_pairs=flips, platform_executed=False, scores_measured=False,
                     verification='XML/IT/controlled NT/state/reference replay/counterfactual checks only')
    write_json(HERE / 'catalogue.json', catalogue)
    for stage in (1, 2):
        names = [Path(e['path']).name for e in entries if e.get('stage') == stage]
        write_text(HERE / 'cases' / f'stage{stage}' / 'test.list', '\n'.join(names) + '\n')
    write_json(HERE / 'run_manifest.json', [dict(id=e['id'], path=e['path'], stage=e['stage'], mode=mode)
               for e in entries if e['kind'] != 'invalid' for mode in ('it', 'nt')])
    write_json(HERE / 'invalid' / 'expected_errors.json', [e for e in entries if e['kind'] == 'invalid'])
    print('Generated 180 normal XML + 20 intentional negative XML; no platform launched.')


if __name__ == '__main__':
    main()
