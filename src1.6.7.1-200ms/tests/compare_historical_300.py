#!/usr/bin/env python3
"""Describe 200 ms results beside the earlier, separate 300 ms run."""
import argparse
import json
from pathlib import Path


FIELDS = ('final_goals', 'credited_constraints', 'action_cost', 'base',
          'official_score', 'platform_seconds')


def rows(path):
    values = [json.loads(line) for line in path.read_text(encoding='utf8').splitlines()]
    return {(v['id'], v['mode'], v['round']): v for v in values}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('current', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    old = root / 'src1.6.7.1/test-results/comprehensive200-20261005'
    new_rows = rows(args.current / 'results.jsonl')
    old_rows = rows(old / 'results.jsonl')
    assert len(new_rows) == len(old_rows) == 400
    assert set(new_rows) == set(old_rows)
    for key in new_rows:
        a, b = old_rows[key], new_rows[key]
        assert (a['sha256'], a['seed'], a['kind'], a['stage']) == (
            b['sha256'], b['seed'], b['kind'], b['stage'])
    old_input = json.loads((old / 'input-audit.json').read_text(encoding='utf8'))
    new_input = json.loads((args.current / 'input-audit.json').read_text(encoding='utf8'))
    sdk_source = [k for k in old_input['sdk'] if k.startswith(('src/', 'include/', 'res/'))]
    assert all(old_input['sdk'][k] == new_input['sdk'][k] for k in sdk_source)
    normal = [key for key, row in new_rows.items() if row['kind'] != 'invalid']
    assert len(normal) == 360
    variants = {
        'original_300ms_historical': (old_rows, 'baseline'),
        'h1_300ms_historical': (old_rows, 'current'),
        'original_200ms_current_run': (new_rows, 'baseline'),
        'h1_200ms_current_run': (new_rows, 'current'),
    }
    totals = {}
    for name, (data, arm) in variants.items():
        values = [data[key][arm] for key in normal]
        totals[name] = dict(sums={field: sum(v[field] for v in values) for field in FIELDS},
                            failures=sum(v['status'] != 'ok' for v in values),
                            sdk_deadlines=sum(bool(v['platform_timed_out']) for v in values))
    cross = {}
    for arm in ('baseline', 'current'):
        cross[arm] = dict(
            action_differences=sum(old_rows[k][arm]['action_sequence'] !=
                                   new_rows[k][arm]['action_sequence'] for k in normal),
            goal_differences=sum(old_rows[k][arm]['final_goals'] !=
                                 new_rows[k][arm]['final_goals'] for k in normal),
            base_differences=sum(old_rows[k][arm]['base'] !=
                                 new_rows[k][arm]['base'] for k in normal))
    output = dict(scope='360 normal matching question/mode/seed cells',
                  sdk_source_files_matched=len(sdk_source),
                  run_relationship='200ms arms are paired with each other; 300ms arms belong to an earlier separate run',
                  variants=totals, cross_run_differences=cross)
    (args.current / 'HISTORICAL_300.json').write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print('HISTORICAL_REFERENCE', json.dumps(cross))


if __name__ == '__main__':
    main()
