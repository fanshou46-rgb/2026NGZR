"""Compare production claims with real SDK grades; preserve known disagreements."""
import collections
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'validation/review175-20261004'
FINAL = re.compile(r'\[3A\]\[final\] goals=(\d+)/(\d+) \(unknown=(\d+)\), '
                   r'constraints=(\d+)/(\d+) \(unknown=(\d+)\), '
                   r'base_score=(-?\d+), action_cost=(\d+)')


def main():
    details = []
    for run, count in (('frozen-v5', 432), ('frozen-competition', 72)):
        rows = json.loads((OUT / run / 'results.json').read_text(encoding='utf8'))
        assert len(rows) == count
        for row in rows:
            result = row['result']
            server = (Path(result['output']) / 'server.log').read_text(
                encoding='utf8', errors='replace')
            grades = re.findall(r'^# Score:\s*(-?\d+)', server, re.M)
            assert grades and int(grades[-1]) == result['raw_score']
            assert min(int(grades[-1]), 1000) == result['official_score']
            matches = FINAL.findall((Path(result['output']) / 'client.log').read_text(
                encoding='utf8', errors='replace'))
            item = {k: row[k] for k in ('suite', 'id', 'mode', 'seed', 'version')}
            item.update(canonical_goals=None, canonical_constraints=None,
                        canonical_base=None, canonical_cost=None,
                        sdk_goals=result.get('final_goals'), sdk_base=result.get('base'),
                        sdk_constraints=result.get('credited_constraints'),
                        sdk_cost=result.get('action_cost'), sdk_raw_score=result.get('raw_score'),
                        capped_official_score=result.get('official_score'))
            if result.get('official_score') is None:
                item['category'] = 'ungraded'
            elif not matches:
                item['category'] = 'no_final_claim'
            else:
                g, _, _, c, _, _, base, cost = map(int, matches[-1])
                item.update(canonical_goals=g, canonical_constraints=c,
                            canonical_base=base, canonical_cost=cost)
                item['category'] = ('goal_overcount' if g > result['final_goals'] else
                                    'goal_undercount' if g < result['final_goals'] else
                                    'other_difference' if any((c != result['credited_constraints'],
                                                               base != result['base'],
                                                               cost != result['action_cost'])) else 'equal')
            item['trace'] = str(Path(result['output']).relative_to(ROOT))
            details.append(item)
    summary = {}
    for suite in sorted({r['suite'] for r in details}):
        summary[suite] = {v: dict(collections.Counter(
            r['category'] for r in details if r['suite'] == suite and r['version'] == v))
            for v in ('src1.7.3', 'src1.7.4', 'src1.7.5')}
    (OUT / 'CANONICAL_AUDIT.json').write_text(json.dumps(
        dict(policy='SDK raw grades authoritative; official min(raw,1000) per repository competition rule; diagnostic categories are not passing assertions',
             server_score_checks=len(details), server_score_checks_passed=True,
             summary=summary), ensure_ascii=False, indent=2), encoding='utf8')
    with (OUT / 'CANONICAL_RUNS.csv').open('w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(details[0]))
        writer.writeheader()
        writer.writerows(details)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
