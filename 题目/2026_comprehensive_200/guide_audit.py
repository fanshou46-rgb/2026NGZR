"""Independent guide checks, in addition to executable-world checks; no platform calls."""
import json
import re
import sys
from collections import Counter
from pathlib import Path
from offline_check import load_case, sexps, Invalid

HERE = Path(__file__).resolve().parent
SMALL = {'book', 'can', 'remotecontrol', 'bottle', 'cup'}
BIG = set('human plant couch chair sofa bed table workspace worktable teapoy desk television airconditioner washmachine'.split())
CONTAINERS = {'closet', 'cupboard', 'refrigerator', 'microwave'}
COLORS = set('white black yellow blue green red'.split())
WORDS = SMALL | BIG | CONTAINERS | COLORS | set('the must not be near in on plate opened closed do go to pick up put down give take out from open close'.split())

def audit(path):
    issues = []
    def check(ok, code, detail):
        if not ok: issues.append(dict(code=code, detail=detail))
    try:
        d = load_case(path)
    except (Invalid, ValueError, KeyError) as exc:
        return [dict(code='parse_state_alignment', detail=str(exc))]
    w, terms = d['world'], d['terms']
    goals = [t for t in terms if t.kind == 'task']
    cons = [t for t in terms if t.kind == 'constraint']
    check(3 <= len(goals) <= 7, 'task_count', str(len(goals)))
    check(200 <= 40 * len(goals) + 20 * len(cons) <= 900, 'budget_with_bonus', str(40*len(goals)+20*len(cons)))
    bigpos = [w.at[i] for i,o in w.objects.items() if o['size'] == 'big']
    check(len(bigpos) == len(set(bigpos)), 'big_position_collision', str(bigpos))
    info = d['facts']['info']
    check([f[0] for f in info[:3]] == ['hold','plate','at'] and info[2][1] == '0', 'robot_order', str(info[:3]))
    seen = []
    for f in info[3:]:
        i = int(f[1])
        if not seen or seen[-1] != i: seen.append(i)
    check(seen == sorted(w.objects), 'object_block_order', str(seen))
    for i,o in w.objects.items():
        check(o['sort'] in SMALL|BIG|CONTAINERS, 'sort_vocabulary', str(i))
        check((o['sort'] in SMALL) == (o['size'] == 'small'), 'size_sort', str(i))
        check((o['sort'] in CONTAINERS) == (o.get('type') == 'container'), 'container_type', str(i))
        if o['size'] == 'small': check(o.get('color') in COLORS, 'small_color', str(i))
        else: check('color' not in o, 'big_color', str(i))
        fields = [f[0] for f in info[3:] if int(f[1]) == i]
        expected = ['sort','size'] + (['color'] if o['size']=='small' else [])
        expected += [p for p in ('at','inside') if p in fields]
        if o.get('type') == 'container': expected += ['type'] + [p for p in ('opened','closed') if p in fields]
        check(fields == expected, 'environment_field_order', f'{i}: {fields}')
    nodes = sexps(d['root'].findtext('instr'))[0][1:]
    for n,(node,t) in enumerate(zip(nodes,terms),1):
        body = node if node[0] == ':task' else node[1]
        call, cond = body[1:]
        small = [i for i in t.args if w.objects[i]['size']=='small']
        check(len(small) <= 1, 'two_small_objects', f'clause {n}')
        expected = []
        objs = t.args[1:] if t.pred=='give' else t.args
        variables = ['X','Y'][:len(objs)]
        check(call[1:] == (['human','X'] if t.pred=='give' else variables), 'variable_order', f'clause {n}')
        for obj,var in zip(objs,variables):
            expected.append(['sort',var,w.objects[obj]['sort']])
            if w.objects[obj]['size']=='small': expected.append(['color',var,w.objects[obj]['color']])
        is_task = t.kind=='task' or t.inner=='task'
        if is_task and t.pred in ('open','close'): expected.append(['type','X','container'])
        if is_task and t.pred in ('putin','takeout'): expected.append(['type','Y','container'])
        check(cond[1:] == expected, 'condition_schema_order', f'clause {n}: {cond[1:]} expected {expected}')
        check(not any(c[:2]==['color','Y'] for c in cond[1:]), 'color_Y', f'clause {n}')
        if t.pred in ('near','on','puton'):
            check(w.objects[t.args[0]]['size']=='small' and w.objects[t.args[1]]['size']=='big', 'relation_types', f'clause {n}')
        if t.kind=='task' and t.pred=='goto' and small:
            check(t.args[0] in w.at, 'goto_initial_target', f'clause {n}')
    words = set(re.findall(r'[a-z]+', d['root'].findtext('nl').lower()))
    check(not(words-WORDS), 'nl_vocabulary', str(sorted(words-WORDS)))
    check(max(d['packets'].values()) < 3900, 'packet_guard', str(d['packets']))
    return issues

def main():
    cat=json.loads((HERE/'catalogue.json').read_text(encoding='utf-8'))
    rows=[dict(id=e['id'],issues=audit(HERE/e['path'])) for e in cat['cases'] if e['kind']!='invalid']
    counts=Counter(code for r in rows for code in {i['code'] for i in r['issues']})
    result=dict(normal_cases=len(rows), passed=sum(not r['issues'] for r in rows), issue_case_counts=dict(counts),
        basis={'format':'docs/rules/question-guide-2025.pdf pages 1-4', 'scoring':'docs/rules/rules-2026.pdf',
               'task_count_3_to_7':'user supplied stricter requirement; not located in local PDFs',
               'distinct_big_positions':'user supplied requirement', 'vocabulary':'restricted subset of guide examples; full 2024 vocabulary not present'},
        platform_executed=False, scores_measured=False, cases=rows)
    dest=HERE/'audit'/('guide_before.json' if '--before' in sys.argv else 'guide_after.json')
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','basis')},ensure_ascii=False))
    return int(bool(counts)) if '--before' not in sys.argv else 0

if __name__=='__main__': sys.exit(main())
