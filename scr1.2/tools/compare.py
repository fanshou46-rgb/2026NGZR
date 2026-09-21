#!/usr/bin/env python3
"""Compare per-case results, preserving repeat variation and missing scores."""
import argparse
import collections
import csv
import json
from pathlib import Path
import statistics
from baseline import parse_evaluation


def load(folder):
    rows = []
    for summary in sorted(folder.glob('*/summary.json')):
        row = json.loads(summary.read_text(encoding='utf-8'))
        # Final answer is retained even for runs predating summary enrichment.
        answer = summary.parent / 'runtime/vanswer.txt'
        row.update(parse_evaluation(answer.read_text(encoding='utf-8', errors='replace')
                                   if answer.exists() else ''))
        row['run'] = summary.parent.name
        row['action_cost'] = sum(count * (4 if name == 'move' else 1 if name == 'sense' else 2)
                                 for name, count in row['actions'].items())
        if row['final_goals'] is not None and row['credited_constraints'] is not None:
            row['base_score'] = row['final_goals'] * 40 + row['credited_constraints'] * 20 - row['action_cost']
        else:
            row['base_score'] = None
        rows.append(row)
    return rows


def aggregate(rows):
    groups = collections.defaultdict(list)
    for row in rows:
        groups[(Path(row['case']).name, row['stage'], row['mode'], row['case_sha256'])].append(row)
    return groups


def mean(rows, key):
    values = [row[key] for row in rows]
    return statistics.mean(values) if values and all(v is not None for v in values) else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--before', required=True, type=Path)
    p.add_argument('--after', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    before, after = load(args.before), load(args.after)
    a, b = aggregate(before), aggregate(after)
    result = []
    for key in sorted(set(a) | set(b)):
        old, new = a.get(key, []), b.get(key, [])
        row = {'case': key[0], 'stage': key[1], 'mode': key[2], 'sha256': key[3],
               'before_runs': len(old), 'after_runs': len(new)}
        for label, group in [('before', old), ('after', new)]:
            row[label + '_failures'] = sum(r['status'] != 'ok' for r in group)
            for metric in ['raw_score', 'official_score', 'base_score', 'final_goals',
                           'credited_constraints', 'action_count', 'platform_seconds']:
                row[label + '_' + metric] = mean(group, metric)
            for action in ['askloc', 'sense', 'move']:
                row[label + '_' + action] = statistics.mean(
                    r['actions'].get(action, 0) for r in group) if group else None
        old_score, new_score = row['before_official_score'], row['after_official_score']
        row['score_delta'] = new_score - old_score if old_score is not None and new_score is not None else None
        result.append(row)
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    (args.output / 'runs.json').write_text(json.dumps({'before': before, 'after': after},
                                         ensure_ascii=False, indent=2), encoding='utf-8')
    with (args.output / 'comparison.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result[0]) if result else ['case'])
        writer.writeheader()
        writer.writerows(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
