#!/usr/bin/env python3
"""Offline XML/IT/NT and reference-plan checks. Never starts the platform."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
TASK_ARITY = dict(goto=1, pickup=1, putdown=1, open=1, close=1,
                  puton=2, putin=2, takeout=2, give=2)
INFO_ARITY = dict(near=2, on=2, inside=2, plate=1, opened=1, closed=1, hold=1)


class Invalid(ValueError):
    def __init__(self, layer, message):
        self.layer = layer
        super().__init__(message)


def require(ok, message, layer='structure'):
    if not ok:
        raise Invalid(layer, message)


def sexps(text):
    tokens = re.findall(r'\(|\)|[^\s()]+', text)
    roots, stack = [], []
    for tok in tokens:
        if tok == '(':
            node = []
            (stack[-1] if stack else roots).append(node)
            stack.append(node)
        elif tok == ')':
            require(bool(stack), 'unmatched closing parenthesis', 'syntax')
            stack.pop()
        else:
            require(bool(stack), 'atom outside expression', 'syntax')
            stack[-1].append(tok)
    require(not stack, 'unclosed parenthesis', 'syntax')
    return roots


@dataclass(frozen=True)
class Term:
    kind: str
    pred: str
    args: tuple[int, ...]
    positive: bool = True
    inner: str = 'info'

    def key(self):
        pred, args = self.pred, self.args
        if self.kind == 'constraint' and self.inner == 'info' and pred in ('near', 'on'):
            pred, args = 'near', tuple(sorted(args))
        if self.inner == 'task' or self.kind == 'task':
            if pred == 'give':
                pred, args = 'puton', (args[1], args[0])
        return (self.kind, pred, args, self.positive, self.inner)

    def data(self):
        return dict(kind=self.kind, pred=self.pred, args=list(self.args),
                    positive=self.positive, inner=self.inner)


@dataclass
class World:
    objects: dict[int, dict]
    robot: int
    at: dict[int, int]
    inside: dict[int, int]
    opened: set[int]
    hand: int = 0
    plate: int = 0

    def copy(self):
        return deepcopy(self)

    @property
    def locations(self):
        return set(self.at[i] for i, o in self.objects.items() if o['size'] == 'big')

    def position(self, obj):
        if obj == 0:
            return self.robot
        if obj in (self.hand, self.plate):
            return self.robot
        return self.at.get(obj)

    def same(self, a, b):
        return self.position(a) is not None and self.position(a) == self.position(b)

    def visible(self):
        return sorted(i for i in self.objects if self.position(i) == self.robot
                      or (i in self.inside and self.inside[i] in self.opened
                          and self.position(self.inside[i]) == self.robot))

    def invariant(self):
        require(self.robot in self.locations, 'robot location outside declared domain', 'state')
        require(self.hand == 0 or self.hand != self.plate, 'same object in both slots', 'state')
        for i, o in self.objects.items():
            if o['size'] == 'small':
                ways = int(i in self.at) + int(i in self.inside) + int(i == self.hand) + int(i == self.plate)
                require(ways == 1, f'object {i}: expected exactly one placement, got {ways}', 'state')
            else:
                require(i in self.at and i not in self.inside and i not in (self.hand, self.plate),
                        f'big object {i} has invalid placement', 'state')
        for i, c in self.inside.items():
            require(self.objects[c].get('type') == 'container', f'{i} inside non-container {c}', 'state')
        require(self.opened <= {i for i, o in self.objects.items() if o.get('type') == 'container'},
                'door state on non-container', 'state')

    def step(self, action):
        op, *args = action
        if op == 'move':
            loc, = args
            require(loc in self.locations and loc != self.robot, f'illegal move {loc}', 'action')
            self.robot = loc
        elif op == 'sense':
            require(not args, 'sense arity', 'action')
        elif op == 'askloc':
            a, = args
            require(a == 0 or a in self.objects, 'askloc unknown object', 'action')
        elif op in ('open', 'close'):
            a, = args
            require(self.objects[a].get('type') == 'container' and self.same(0, a), 'door unreachable', 'action')
            require(not self.hand, 'door operation needs empty hand', 'action')
            require((a in self.opened) == (op == 'close'), 'door already in requested state', 'action')
            if op == 'open':
                self.opened.add(a)
            else:
                self.opened.remove(a)
        elif op == 'pickup':
            a, = args
            require(self.objects[a]['size'] == 'small' and not self.hand and a != self.plate,
                    'pickup slot/type violation', 'action')
            require(a in self.at and self.same(0, a), 'pickup object not exposed here', 'action')
            del self.at[a]
            self.hand = a
        elif op == 'putdown':
            a, = args
            require(self.hand == a and a != 0, 'putdown object not in hand', 'action')
            self.hand = 0
            self.at[a] = self.robot
        elif op == 'toplate':
            a, = args
            require(self.hand == a and a != 0 and not self.plate, 'toplate slot violation', 'action')
            self.hand, self.plate = 0, a
        elif op == 'fromplate':
            a, = args
            require(self.plate == a and a != 0 and not self.hand, 'fromplate slot violation', 'action')
            self.hand, self.plate = a, 0
        elif op in ('putin', 'takeout'):
            a, c = args
            require(self.objects[a]['size'] == 'small' and self.objects[c].get('type') == 'container',
                    'container action type violation', 'action')
            require(c in self.opened and self.same(0, c), 'container closed or unreachable', 'action')
            if op == 'putin':
                require(self.hand == a, 'putin needs held object', 'action')
                self.hand = 0
                self.inside[a] = c
            else:
                require(not self.hand and self.inside.get(a) == c, 'takeout precondition', 'action')
                del self.inside[a]
                self.hand = a
        else:
            raise Invalid('action', f'unknown action {op}')
        self.invariant()
        if op == 'sense':
            return dict(visible=self.visible())
        if op == 'askloc':
            a = args[0]
            return dict(truth_answer=['inside', a, self.inside[a]] if a in self.inside
                        else ['at', a, self.position(a)])
        return {}

    def snapshot(self):
        return dict(robot=self.robot, hand=self.hand, plate=self.plate,
                    at={str(k): v for k, v in sorted(self.at.items())},
                    inside={str(k): v for k, v in sorted(self.inside.items())}, opened=sorted(self.opened))


def goal(world, pred, args):
    a = args[0]
    out = a not in (world.hand, world.plate)
    if pred == 'goto': return world.same(0, a)
    if pred == 'pickup': return not out
    if pred == 'putdown': return out
    if pred == 'puton': return out and world.same(a, args[1])
    if pred == 'give': return args[1] not in (world.hand, world.plate) and world.same(a, args[1])
    if pred == 'putin': return world.inside.get(a) == args[1]
    if pred == 'takeout': return world.inside.get(a) != args[1]
    if pred == 'open': return a in world.opened
    if pred == 'close': return a not in world.opened
    raise Invalid('domain', f'unknown goal {pred}')


def holds(world, term):
    if term.kind == 'task':
        return goal(world, term.pred, term.args)
    a, *rest = term.args
    p = term.pred
    if term.inner == 'task': raw = goal(world, p, term.args)
    elif p in ('near', 'on'): raw = world.same(a, rest[0])
    elif p == 'inside': raw = world.inside.get(a) == rest[0]
    elif p == 'plate': raw = world.plate == a
    elif p == 'hold': raw = world.hand == a
    elif p == 'opened': raw = a in world.opened
    elif p == 'closed': raw = a not in world.opened
    else: raise Invalid('domain', f'unknown constraint {p}')
    return raw if term.positive else not raw


def label(objects, obj):
    o = objects[obj]
    return ('the ' + o['color'] + ' ' + o['sort']) if o['size'] == 'small' else 'the ' + o['sort']


def parse_nl(sentence, objects):
    """Independent grammar for the controlled English actually used in this suite."""
    labels = {}
    for obj in objects:
        name = label(objects, obj)
        require(name not in labels, f'ambiguous noun phrase {name}', 'semantics')
        labels[name] = obj
    def noun(s):
        require(s in labels, f'unknown noun phrase {s}', 'semantics')
        return labels[s]
    s = sentence.strip().lower()
    require(s.endswith('.'), 'sentence needs final period', 'semantics')
    s = s[:-1]
    if ' must ' in s:
        subject, relation = s.split(' must ', 1)
        positive = not relation.startswith('not ')
        if not positive: relation = relation[4:]
        patterns = [('be near ', 'near'), ('be in ', 'inside')]
        if relation == 'be on the plate':
            return Term('constraint', 'plate', (noun(subject),), positive)
        if relation in ('be opened', 'be closed'):
            return Term('constraint', relation[3:], (noun(subject),), positive)
        for prefix, pred in patterns:
            if relation.startswith(prefix):
                return Term('constraint', pred, (noun(subject), noun(relation[len(prefix):])), positive)
        raise Invalid('semantics', f'unsupported constraint sentence {sentence}')
    negative = s.startswith('do not ')
    if negative: s = s[7:]
    pred, args = None, None
    for prefix, p in [('go to ', 'goto'), ('pick up ', 'pickup'), ('open ', 'open'), ('close ', 'close')]:
        if s.startswith(prefix): pred, args = p, (noun(s[len(prefix):]),)
    if s.startswith('put ') and s.endswith(' down'):
        pred, args = 'putdown', (noun(s[4:-5]),)
    elif s.startswith('put '):
        for sep, p in [(' on ', 'puton'), (' in ', 'putin')]:
            if sep in s:
                x, y = s[4:].split(sep)
                pred, args = p, (noun(x), noun(y))
    elif s.startswith('give '):
        x, y = s[5:].split(' to ')
        pred, args = 'give', (noun(y), noun(x))
    elif s.startswith('take out '):
        x, y = s[9:].split(' from ')
        pred, args = 'takeout', (noun(x), noun(y))
    require(pred is not None, f'unrecognized sentence {sentence}', 'semantics')
    return Term('constraint', pred, args, False, 'task') if negative else Term('task', pred, args)


def ground_instruction(node, objects):
    require(isinstance(node, list) and len(node) >= 2, 'instruction shape', 'syntax')
    kind, positive, inner = 'task', True, 'info'
    if node[0] in (':cons_not', ':cons_notnot'):
        require(len(node) == 2, 'constraint arity', 'syntax')
        kind, positive = 'constraint', node[0] == ':cons_notnot'
        node = node[1]
        require(isinstance(node, list) and node and node[0] in (':task', ':info'), 'constraint body', 'syntax')
        inner = node[0][1:]
        require(not (positive and inner == 'task'), 'positive task constraint unsupported', 'domain')
    require(len(node) == 3 and node[0] == (':task' if kind == 'task' else ':' + inner), 'instruction arity', 'syntax')
    call, cond = node[1:]
    require(isinstance(call, list) and call, 'empty predicate', 'syntax')
    arities = TASK_ARITY if kind == 'task' or inner == 'task' else INFO_ARITY
    require(call[0] in arities, f'unknown predicate {call[0]}', 'domain')
    require(len(call) == arities[call[0]] + 1, f'wrong arity {call[0]}', 'domain')
    require(isinstance(cond, list) and len(cond) > 1 and cond[0] == ':cond', 'bad condition', 'syntax')
    variables = set(a for a in call[1:] if a in ('X', 'Y'))
    require(all(a in ('X', 'Y', 'human') for a in call[1:]), 'unexpected argument', 'domain')
    selected = {}
    for v in variables:
        terms = [c for c in cond[1:] if isinstance(c, list) and len(c) == 3 and c[1] == v]
        require(terms and all(c[0] in ('sort', 'color', 'type') for c in terms), 'bad descriptor', 'domain')
        matches = [i for i, o in objects.items() if all(o.get(c[0]) == c[2] for c in terms)]
        require(len(matches) == 1, f'{v}: expected unique object, found {matches}', 'semantics')
        selected[v] = matches[0]
    require(all(isinstance(c, list) and len(c) == 3 and c[1] in variables for c in cond[1:]),
            'unbound or malformed condition', 'domain')
    args = tuple(1 if a == 'human' else selected[a] for a in call[1:])
    p = call[0]
    if p in ('open', 'close', 'opened', 'closed'):
        require(objects[args[0]].get('type') == 'container', 'door predicate type mismatch', 'domain')
    if p in ('inside', 'putin', 'takeout'):
        require(objects[args[0]]['size'] == 'small' and objects[args[1]].get('type') == 'container',
                'inside predicate type mismatch', 'domain')
    if p in ('pickup', 'putdown', 'puton', 'plate', 'hold'):
        require(objects[args[0]]['size'] == 'small', 'small-object predicate type mismatch', 'domain')
    if p == 'give':
        require(args[0] == 1 and objects[args[1]]['size'] == 'small', 'give type mismatch', 'domain')
    return Term(kind, p, args, positive, inner)


def load_case(path):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise Invalid('xml', str(exc)) from exc
    require(root.tag == 'test' and [x.tag for x in root] == ['env', 'instr', 'nl'], 'XML section layout', 'xml')
    env = root.find('env')
    require([x.tag for x in env] == ['info', 'mis', 'err', 'extra'], 'environment sections', 'xml')
    require([x.tag for x in env.find('err')] == ['r', 'w'], 'error sections', 'xml')
    facts = {}
    for section in ('info', 'mis', 'err/r', 'err/w', 'extra'):
        facts[section] = [tuple(x) for x in sexps(env.findtext(section) or '')]
        require(all(all(isinstance(a, str) for a in x) for x in facts[section]), 'nested state fact', 'state')
    require(not facts['extra'], 'extra facts not used by this suite', 'state')
    truth = facts['info'] + facts['mis'] + facts['err/r']
    require(len(truth) == len(set(truth)), 'duplicate true state fact', 'state')
    objects = {}
    for f in truth:
        if f[0] in ('sort', 'size', 'color', 'type'):
            require(len(f) == 3 and f[1].isdigit(), 'attribute fact shape', 'state')
            attrs = objects.setdefault(int(f[1]), {})
            require(f[0] not in attrs, 'duplicate object attribute', 'state')
            attrs[f[0]] = f[2]
    require(sorted(objects) == list(range(1, len(objects) + 1)), 'object IDs must be consecutive', 'state')
    require(objects[1].get('sort') == 'human', 'human must be object 1', 'state')
    at, inside, opened, closed = {}, {}, set(), set()
    hand = plate = robot = None
    for f in truth:
        p = f[0]
        if p in ('sort', 'size', 'color', 'type'): continue
        require(p in ('at', 'inside', 'hold', 'plate', 'opened', 'closed'), f'unknown fact {p}', 'state')
        require(len(f) == (3 if p in ('at', 'inside') else 2), 'fact arity', 'state')
        require(all(x.isdigit() for x in f[1:]), 'numeric state argument required', 'state')
        a = int(f[1])
        require(a == 0 or a in objects, 'state references unknown object', 'state')
        if p == 'at':
            if a == 0:
                require(robot is None, 'duplicate robot position', 'state')
                robot = int(f[2])
            else:
                require(a not in at, 'duplicate object position', 'state')
                at[a] = int(f[2])
        elif p == 'inside':
            require(a not in inside and int(f[2]) in objects, 'inside reference/duplicate', 'state')
            inside[a] = int(f[2])
        elif p == 'hold':
            require(hand is None, 'duplicate hand state', 'state')
            hand = a
        elif p == 'plate':
            require(plate is None, 'duplicate plate state', 'state')
            plate = a
        elif p == 'opened': opened.add(a)
        elif p == 'closed': closed.add(a)
    require(None not in (hand, plate, robot), 'missing robot state', 'state')
    for i, o in objects.items():
        require('sort' in o and o.get('size') in ('small', 'big'), f'object attributes {i}', 'state')
        if o['size'] == 'small': require('color' in o, 'small object missing color', 'state')
    containers = {i for i, o in objects.items() if o.get('type') == 'container'}
    require(opened.isdisjoint(closed) and opened | closed == containers, 'incomplete/inconsistent door states', 'state')
    world = World(objects, robot, at, inside, opened, hand, plate)
    world.invariant()
    require(len(facts['err/r']) == len(facts['err/w']), 'error pairing count', 'state')
    for right, wrong in zip(facts['err/r'], facts['err/w']):
        require(right != wrong and right[1] == wrong[1], 'bad true/false pair', 'state')
        require(wrong[0] in ('at', 'inside') and len(wrong) == 3, 'unsupported false fact', 'state')
        require(wrong not in truth, 'false fact actually true', 'state')
        if wrong[0] == 'inside':
            require(objects[int(wrong[1])]['size'] == 'small' and int(wrong[2]) in containers,
                    'false inside type mismatch', 'state')
        else: require(int(wrong[2]) in world.locations, 'false location outside domain', 'state')
    instr = sexps(root.findtext('instr') or '')
    require(len(instr) == 1 and instr[0] and instr[0][0] == ':ins', 'instruction root', 'syntax')
    terms = [ground_instruction(n, objects) for n in instr[0][1:]]
    require(len({t.key() for t in terms}) == len(terms), 'semantic duplicate instruction', 'semantics')
    lines = [x.strip() for x in (root.findtext('nl') or '').splitlines() if x.strip()]
    require(len(lines) == len(terms), 'IT/NT clause count differs', 'semantics')
    for i, (term, sentence) in enumerate(zip(terms, lines), 1):
        require(term.key() == parse_nl(sentence, objects).key(), f'IT/NT mismatch at clause {i}', 'semantics')
    compact = lambda x: ' '.join((x or '').split())
    envelope = '<test><name>{}</name><es>(:domain {}  {})</es><ts>{}</ts></test>'
    packet = {}
    for mode, tag in [('it', 'instr'), ('nt', 'nl')]:
        payload = envelope.format(path.name, compact(env.findtext('info')), compact(env.findtext('err/w')),
                                  compact(root.findtext(tag)))
        packet[mode] = len(payload.encode('utf-8'))
    return dict(root=root, facts=facts, truth=sorted(truth), world=world, terms=terms, packets=packet)


def replay(initial, terms, actions):
    w = initial.copy()
    goals = [(i, t) for i, t in enumerate(terms, 1) if t.kind == 'task']
    cons = [(i, t) for i, t in enumerate(terms, 1) if t.kind == 'constraint']
    first_bad = {i: 0 for i, t in cons if not holds(w, t)}
    states, evidence = [w.copy()], []
    for k, action in enumerate(actions, 1):
        observation = w.step(action)
        for i, t in cons:
            if not holds(w, t): first_bad.setdefault(i, k)
        states.append(w.copy())
        if observation: evidence.append(dict(step=k, action=action, **observation))
    return dict(final=w, states=states, observation_evidence=evidence,
                goal_ids=[i for i, t in goals if holds(w, t)],
                unmet_goal_ids=[i for i, t in goals if not holds(w, t)],
                violated_constraint_ids=sorted(first_bad), first_violation_step=first_bad,
                restored_goal_ids=[i for i, t in goals if holds(initial, t) and holds(w, t)
                                   and any(not holds(s, t) for s in states[1:-1])])


def check_tradeoff_structure(initial, terms, primary, reference):
    """Check the assumptions behind the four short, case-specific upper-bound arguments."""
    category, roles = reference['category'], reference['roles']
    gs = {t.key(): i for i, t in enumerate(terms, 1) if t.kind == 'task'}
    cs = {t.key(): i for i, t in enumerate(terms, 1) if t.kind == 'constraint'}
    def cons(pred, args, positive):
        k = Term('constraint', pred, tuple(args), positive).key()
        require(k in cs, f'proof missing constraint {k}', 'proof')
        return cs[k]
    if category == 'C03':
        lock = cons('closed', (4,), True)
        require(4 not in initial.opened, 'proof source initially open', 'proof')
        needed = []
        for t in terms:
            if t.kind != 'task': continue
            obj = t.args[1] if t.pred == 'give' else t.args[0]
            if initial.inside.get(obj) == 4 and t.pred in ('give', 'puton', 'putin', 'takeout', 'pickup'):
                needed.append(t)
        require(len(needed) >= 2, 'shared lock must affect several goals', 'proof')
        require(primary['violated_constraint_ids'] == [lock] and not primary['unmet_goal_ids'],
                'witness does not attain the one-lock-loss bound', 'proof')
        return dict(verified=True, unavoidable_loss='one 20-point constraint or at least one 40-point goal')
    if category == 'C04':
        pickup = [t.args[0] for t in terms if t.kind == 'task' and t.pred == 'pickup']
        require(len(pickup) == len(set(pickup)) == 3, 'three distinct pickup goals required', 'proof')
        require(len(primary['unmet_goal_ids']) == 1 and not primary['violated_constraint_ids'],
                'capacity witness must lose one goal only', 'proof')
        return dict(verified=True, pickup_goals=3, carrying_slots=2, unavoidable_goal_loss=40)
    if category == 'C05':
        cons('closed', (6,), True)
        require(6 not in initial.opened, 'risk source is open initially', 'proof')
        risk_goal_ids = []
        for key in ('risk0', 'risk1'):
            obj = roles[key]
            require(initial.inside.get(obj) == 6, 'risk object not in protected container', 'proof')
            cons('inside', (obj, 6), True)
            matches = [(i, t) for i, t in enumerate(terms, 1) if t.kind == 'task'
                       and ((t.pred == 'give' and t.args[1] == obj) or (t.pred == 'puton' and t.args[0] == obj))]
            require(len(matches) == 1, 'risk object must have one benefit target', 'proof')
            i, t = matches[0]
            dest = 1 if t.pred == 'give' else t.args[1]
            cons('near', (obj, dest), False)
            require(sum(t.kind == 'task' and obj in t.args for t in terms) == 1,
                    'additional risk-object goals would change proof', 'proof')
            risk_goal_ids.append(i)
        require(set(primary['unmet_goal_ids']) == set(risk_goal_ids)
                and not primary['violated_constraint_ids'], 'safe branch bound not attained', 'proof')
        return dict(verified=True, safe_goals=5, risky_goals=2,
                    extra_goal_points=40, unavoidable_per_goal_constraint_loss=40,
                    shared_constraint_loss_if_any_risky_goal=20)
    require(category == 'D02', 'unknown tradeoff category', 'proof')
    fixed = [(i, t) for i, t in enumerate(terms, 1)
             if t.kind == 'task' and t.pred == 'goto' and initial.objects[t.args[0]]['size'] == 'big']
    require(len(fixed) == 3 and len({initial.position(t.args[0]) for _, t in fixed}) == 3,
            'three distinct fixed endpoints required', 'proof')
    require(len(primary['unmet_goal_ids']) == 2
            and set(primary['unmet_goal_ids']) <= {i for i, _ in fixed}
            and not primary['violated_constraint_ids'], 'endpoint bound not attained', 'proof')
    return dict(verified=True, distinct_fixed_endpoints=3, maximum_simultaneous_fixed_goto=1)


def check_one(path, entry, reference):
    parsed = load_case(path)
    terms, initial = parsed['terms'], parsed['world']
    gs = [t for t in terms if t.kind == 'task']
    cs = [t for t in terms if t.kind == 'constraint']
    nominal = 40 * len(gs) + 20 * len(cs)
    require(nominal == entry['nominal_gross'] == reference['nominal_gross'] and 200 <= nominal <= 900, 'nominal points or cap', 'budget')
    require(3 <= len(gs) <= 7, 'task count must be 3 to 7', 'budget')
    from guide_audit import audit
    require(not audit(path), 'guide audit failed: ' + str(audit(path)), 'guide')
    require(len(set(t.pred for t in gs)) >= 4, 'fewer than four goal action types', 'coverage')
    mechanisms = {('task-state' if t.inner == 'task' else t.pred) for t in cs}
    require(len(mechanisms) >= 3, 'fewer than three constraint mechanisms', 'coverage')
    require(all(holds(initial, t) for t in cs), 'constraint already false at initial state', 'state')
    require(max(parsed['packets'].values()) < 3900, f'packet exceeds guard: {parsed["packets"]}', 'packet')
    flag = 'off' if entry['stage'] == 1 else 'on'
    require(all(parsed['root'].find('env').get(k) == flag for k in ('mis', 'err', 'ans')), 'stage flags', 'structure')
    if entry['stage'] == 1:
        require(not parsed['facts']['mis'] and not parsed['facts']['err/r'], 'Stage 1 must be complete', 'state')
    else:
        require(parsed['facts']['mis'] or parsed['facts']['err/r'], 'Stage 2 needs information perturbation', 'state')
    runs = []
    primary = None
    for plan in reference['plans']:
        result = replay(initial, terms, plan['actions'])
        require(len(result['goal_ids']) == plan['expected_completed_goals'], f'{plan["name"]}: goal count differs', 'witness')
        require(len(result['violated_constraint_ids']) == plan['expected_violated_constraints'],
                f'{plan["name"]}: violation count differs', 'witness')
        if plan['role'] == 'primary': primary = result
        runs.append(dict(name=plan['name'], role=plan['role'], action_count=len(plan['actions']),
                         completed_goals=len(result['goal_ids']), total_goals=len(gs),
                         violated_constraint_ids=result['violated_constraint_ids'],
                         first_violation_step=result['first_violation_step'],
                         unmet_goal_ids=result['unmet_goal_ids'], final_state=result['final'].snapshot(),
                         observation_evidence=result['observation_evidence']))
    require(primary is not None, 'missing primary witness', 'witness')
    if entry['kind'] == 'full':
        require(not primary['unmet_goal_ids'] and not primary['violated_constraint_ids'], 'full witness is not full', 'witness')
    selected_checks = {}
    if 'E04' in entry['tags']:
        target, container = reference['focus']['visibility']
        before, after = [], []
        for e in primary['observation_evidence']:
            if e['action'][0] == 'sense':
                s = primary['states'][e['step']]
                if s.same(0, container) and s.inside.get(target) == container:
                    (after if container in s.opened else before).append(target in e['visible'])
        require(before and after and not any(before) and all(after), 'visibility before/after evidence missing', 'focus')
        selected_checks['E04'] = 'closed: hidden; opened: visible'
    if 'E05' in entry['tags']:
        container = reference['focus']['query_container']
        contents = sorted(i for i, c in initial.inside.items() if c == container)
        participants = {a for g in gs for a in g.args}
        require(len(set(contents) & participants) >= 2, 'shared container does not unlock multiple target objects', 'focus')
        require(any(a == ['askloc', container] for a in reference['plans'][0]['actions']), 'missing container query', 'focus')
        if entry['stage'] == 2:
            require(('at', str(container), str(initial.position(container))) in parsed['facts']['mis'],
                    'shared container location not hidden', 'focus')
        selected_checks['E05'] = dict(container=container, target_contents=sorted(set(contents) & participants))
    if 'E07' in entry['tags']:
        hand, plate = reference['focus']['final_slots']
        require(primary['final'].hand == hand and primary['final'].plate == plate, 'final slot assignment', 'focus')
        require(Term('task', 'pickup', (hand,)).key() in {t.key() for t in gs}
                and Term('task', 'pickup', (plate,)).key() in {t.key() for t in gs}, 'missing double pickup goals', 'focus')
        require(Term('constraint', 'plate', (hand,), False).key() in {t.key() for t in cs}, 'hand item not forbidden on plate', 'focus')
        selected_checks['E07'] = dict(hand=hand, plate=plate)
    if entry['category'] == 'A05':
        require(len(primary['restored_goal_ids']) >= 2, 'A05 lacks two broken-and-restored goals', 'focus')
    if entry['category'] == 'C05':
        require(not any(holds(initial, g) for g in gs), 'C05 already has an initially achieved goal', 'focus')
        first = reference['plans'][0]['actions'][:3]
        require(len(replay(initial, terms, first)['goal_ids']) >= 1, 'C05 three-step fallback not achieved', 'focus')
    if entry['category'] in ('B02', 'B04'):
        require(initial.hand and initial.plate, 'slot-unlock initial state must occupy both slots', 'focus')
    if entry['category'] == 'B03':
        blue, redcup = reference['roles']['blue'], reference['roles']['right']
        require(initial.inside.get(blue) == 4 and initial.inside.get(redcup) == 5
                and Term('task', 'putin', (blue, 5)).key() in {g.key() for g in gs}
                and Term('task', 'putin', (redcup, 4)).key() in {g.key() for g in gs}, 'container swap design missing', 'focus')
    if entry['category'] == 'B04':
        obj = reference['roles']['bottle']
        dest = reference['focus']['pair_destination']
        keys = {c.key() for c in cs}
        for big in range(1, 9):
            if big == dest: continue
            ban = Term('constraint', 'give', (1, obj), False, 'task') if big == 1 else Term('constraint', 'puton', (obj, big), False, 'task')
            require(ban.key() in keys, 'B04 buffer exclusion incomplete', 'focus')
        require(Term('constraint', 'plate', (obj,), False).key() in keys, 'B04 plate shortcut remains', 'focus')
    if entry['category'] == 'D01':
        mobile = [t.args[0] for t in gs if t.pred == 'goto' and initial.objects[t.args[0]]['size'] == 'small']
        require(len(mobile) >= 2 and len({initial.position(i) for i in mobile}) >= 2,
                'D01 targets not initially distributed', 'focus')
    proof = check_tradeoff_structure(initial, terms, primary, reference) if entry['kind'] == 'tradeoff' else {'verified': True, 'method': 'constructive full witness'}
    return dict(id=entry['id'], passed=True, goals=len(gs), constraints=len(cs), nominal_gross=nominal,
                goal_action_types=sorted(set(t.pred for t in gs)), constraint_mechanisms=sorted(mechanisms),
                estimated_packet_bytes=parsed['packets'], focus_checks=selected_checks,
                plans=runs, correctness_argument=proof, platform_executed=False), parsed


def main():
    catalogue = json.loads((HERE / 'catalogue.json').read_text(encoding='utf-8'))
    require(len({e['sha256'] for e in catalogue['cases']}) == len(catalogue['cases']),
            'duplicate XML files in the suite', 'quota')
    results, parsed_cases, errors = [], {}, []
    for entry in catalogue['cases']:
        path = HERE / entry['path']
        try:
            require(hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], 'case file hash changed', 'integrity')
            if entry['kind'] == 'invalid':
                try:
                    load_case(path)
                except Invalid as exc:
                    require(exc.layer == entry['expected_layer'], f'wrong rejection layer: {exc.layer}', 'negative-test')
                    load_case(HERE / entry['source_path'])
                    results.append(dict(id=entry['id'], passed=True, expected_invalid=True,
                                        detected_layer=exc.layer, reason=str(exc), platform_executed=False))
                else:
                    raise Invalid('negative-test', 'intentional error was not detected')
            else:
                reference = json.loads((HERE / entry['reference']).read_text(encoding='utf-8'))
                result, parsed = check_one(path, entry, reference)
                results.append(result)
                parsed_cases[entry['id']] = parsed
        except (Invalid, KeyError, ValueError, TypeError, IndexError) as exc:
            errors.append(dict(id=entry['id'], layer=getattr(exc, 'layer', 'unexpected'), error=str(exc)))
    pairs = Counter(e['pair_id'] for e in catalogue['cases'] if e['kind'] != 'invalid')
    for pair_id, count in pairs.items():
        try:
            require(count == 2, 'stage pair count', 'pair')
            a, b = parsed_cases[pair_id + '-s1'], parsed_cases[pair_id + '-s2']
            require(a['truth'] == b['truth'], 'stage pair true worlds differ', 'pair')
            require(a['terms'] == b['terms'] and a['root'].findtext('nl') == b['root'].findtext('nl'),
                    'stage pair instructions differ', 'pair')
        except (Invalid, KeyError) as exc:
            errors.append(dict(id=pair_id, layer='pair', error=str(exc)))
    flips = []
    for pair in catalogue['counterfactual_pairs']:
        try:
            a, b = [parsed_cases[x] for x in pair]
            require(a['truth'] == b['truth'], 'counterfactual true worlds differ', 'counterfactual')
            ta, tb = a['terms'], b['terms']
            diffs = [(x, y) for x, y in zip(ta, tb) if x != y]
            require(len(ta) == len(tb) and len(diffs) == 1, 'counterfactual must change exactly one clause', 'counterfactual')
            x, y = diffs[0]
            require(x.kind == y.kind == 'constraint' and x.pred == y.pred == 'plate'
                    and not x.positive and not y.positive and x.args != y.args, 'counterfactual wrong difference', 'counterfactual')
            # A plan that is valid for one plate restriction must fail its swapped restriction.
            entries = {e['id']: e for e in catalogue['cases']}
            ref_a = json.loads((HERE / entries[pair[0]]['reference']).read_text(encoding='utf-8'))
            ref_b = json.loads((HERE / entries[pair[1]]['reference']).read_text(encoding='utf-8'))
            require(not replay(a['world'], ta, ref_a['plans'][0]['actions'])['violated_constraint_ids'], 'left plan invalid', 'counterfactual')
            require(not replay(b['world'], tb, ref_b['plans'][0]['actions'])['violated_constraint_ids'], 'right plan invalid', 'counterfactual')
            require(replay(a['world'], ta, ref_b['plans'][0]['actions'])['violated_constraint_ids']
                    and replay(b['world'], tb, ref_a['plans'][0]['actions'])['violated_constraint_ids'],
                    'counterfactual did not invalidate old slot allocation', 'counterfactual')
            flips.append(dict(cases=pair, passed=True))
        except (Invalid, KeyError) as exc:
            errors.append(dict(id=' / '.join(pair), layer='counterfactual', error=str(exc)))
    totals = Counter(e['kind'] for e in catalogue['cases'])
    require(totals == dict(full=140, tradeoff=40, invalid=20), f'unexpected quota {totals}', 'quota')
    summary = dict(status='passed' if not errors else 'failed', total_cases=len(catalogue['cases']),
                   kinds=dict(totals), passed_cases=len(results), stage_pairs=len(pairs),
                   counterfactual_pairs=len(flips), platform_executed=False, scores_measured=False,
                   maximum_estimated_packet_bytes=max((max(r.get('estimated_packet_bytes', {'none': 0}).values())
                                                        for r in results), default=0),
                   focus_case_counts={tag: sum(tag in e.get('tags', []) for e in catalogue['cases'])
                                      for tag in ('E04', 'E05', 'E07', 'E10')},
                   errors=errors, counterfactual_results=flips, results=results)
    (HERE / 'validation_report.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('results', 'counterfactual_results')}, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
