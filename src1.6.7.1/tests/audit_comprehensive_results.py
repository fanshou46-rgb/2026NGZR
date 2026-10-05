#!/usr/bin/env python3
"""Independently re-read official logs/answers and classify every paired change."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args(); out = args.output
    rows = [json.loads(line) for line in (out / 'results.jsonl').read_text(encoding='utf8').splitlines()]
    expected = json.loads((out / 'input-audit.json').read_text())
    keys = {(r['id'], r['mode'], r['round']) for r in rows}
    assert len(keys) == len(rows) == len(expected['cases']) * 2 * expected['rounds']
    errors = []; classification = []; hashes = {}
    for row in rows:
        actual = {}
        for arm in ('baseline', 'current'):
            value = row[arm]; run = Path(value['output'])
            server = (run / 'server.log').read_text(errors='replace')
            commands = re.findall(r'^\s*\[([A-Za-z_]+(?:\s+[^|]*?)?)\|', server, re.M)
            names = [c.split()[0].lower() for c in commands]
            assert all(c in ('move', 'sense', 'askloc', 'ask', 'pickup', 'putdown', 'toplate', 'fromplate', 'open', 'close', 'putin', 'takeout') for c in names), names
            cost = sum({'move': 4, 'sense': 1}.get(c, 2) for c in names)
            answer = run / 'runtime/vanswer.txt'
            text = answer.read_text(errors='replace') if answer.exists() else ''
            atoms = set((int(i), int(s)) for i, s in re.findall(r'value\((\d+),(\d+)\)', text))
            satisfiable = re.search(r'^SATISFIABLE\s*$', text, re.M)
            goals = sum(s == 40 for _, s in atoms) if satisfiable else None
            constraints = sum(s == 20 for _, s in atoms) if satisfiable else None
            scores = re.findall(r'^# Score:\s*(-?\d+)', server, re.M)
            raw = int(scores[-1]) if scores else None
            base = 40 * goals + (20 * constraints if goals else 0) - cost if goals is not None and constraints is not None and raw is not None else None
            recomputed = dict(action_cost=cost, final_goals=goals, credited_constraints=constraints,
                              raw_score=raw, official_score=min(raw, 1000) if raw is not None else None, base=base)
            for field, result in recomputed.items():
                if result != value.get(field): errors.append(dict(key=[row['id'], row['mode'], row['round'], arm], field=field, recomputed=result, saved=value.get(field)))
            if commands != value['action_sequence']: errors.append(dict(key=[row['id'], row['mode'], row['round'], arm], field='action_sequence'))
            actual[arm] = recomputed
            for p in [run / 'server.log', run / 'client.log', answer]:
                if p.exists(): hashes[p.relative_to(out).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
        a, b = row['baseline'], row['current']
        behavior = any(a.get(k) != b.get(k) for k in ('action_sequence', 'final_goals', 'credited_constraints', 'action_cost', 'base'))
        if row['kind'] == 'invalid': category = 'invalid-separate'
        elif behavior: category = 'behavior-difference-needs-repeat'
        elif a.get('raw_score') != b.get('raw_score'): category = 'time-bonus-only'
        else: category = 'identical-behavior-and-score'
        classification.append(dict(id=row['id'], mode=row['mode'], round=row['round'], category=category,
                                   before_time=a.get('platform_seconds'), after_time=b.get('platform_seconds'),
                                   before_bonus=a['raw_score'] - a['base'] if a.get('base') is not None else None,
                                   after_bonus=b['raw_score'] - b['base'] if b.get('base') is not None else None))
    save(out / 'independent-log-audit.json', dict(pairs=len(rows), runs=2 * len(rows), errors=errors, file_sha256=hashes))
    save(out / 'difference-classification.json', classification)
    assert not errors, errors[:3]
    print('INDEPENDENT_LOG_AUDIT', 2 * len(rows), 'runs, 0 mismatches')


if __name__ == '__main__': main()
