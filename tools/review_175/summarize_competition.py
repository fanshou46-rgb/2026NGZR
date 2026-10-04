"""Summarize the preselected competition sample without dropping failed runs."""
import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'validation/review175-20261004'
RUN = OUT / 'frozen-competition'
VERSIONS = ['src1.7.3', 'src1.7.4', 'src1.7.5']
FIELDS = ('base', 'raw_score', 'official_score', 'final_goals', 'credited_constraints',
          'action_cost', 'platform_seconds')


def main():
    rows = json.loads((RUN / 'results.json').read_text(encoding='utf8'))
    audit = json.loads((RUN / 'final-audit.json').read_text(encoding='utf8'))
    assert len(rows) == audit['runs'] == 72
    assert len({(r['id'], r['mode'], r['seed'], r['version']) for r in rows}) == 72
    assert all(r['result']['seed_confirmed'] for r in rows)
    totals = {}
    pairs = collections.defaultdict(dict)
    flat = []
    for row in rows:
        pairs[(row['id'], row['mode'], row['seed'])][row['version']] = row['result']
        result = row['result']
        graded = all(result.get(k) is not None for k in FIELDS)
        item = {k: row[k] for k in ('id', 'mode', 'seed', 'version')}
        item.update({k: result.get(k) if graded else None for k in FIELDS})
        item.update({k: result.get(k) for k in ('status', 'client_exit',
                                              'platform_timed_out', 'external_timeout')})
        item['actions'] = '; '.join(result['action_sequence'])
        item['trace'] = str(Path(result['output']).relative_to(ROOT))
        flat.append(item)
    for version in VERSIONS:
        part = [r['result'] for r in rows if r['version'] == version]
        scored = [r for r in part if all(r.get(k) is not None for k in FIELDS)]
        item = dict(runs=len(part), scored=len(scored), missing=len(part)-len(scored))
        item.update({k: round(sum(r[k] for r in scored), 3) for k in FIELDS})
        item.update(sdk_timeouts=sum(bool(r.get('platform_timed_out')) for r in part),
                    external_timeouts=sum(bool(r.get('external_timeout')) for r in part),
                    crashes=sum(r.get('client_exit') not in (None, 0) for r in part),
                    harness_errors=sum('error' in r for r in part),
                    platform_errors=sum(bool(r.get('platform_error')) for r in part),
                    status_failed=sum(r.get('status') != 'ok' for r in part))
        totals[version] = item
    comparisons = {}
    for before in VERSIONS[:2]:
        valid = [p for p in pairs.values()
                 if all(r.get(k) is not None for r in (p[before], p[VERSIONS[-1]])
                        for k in FIELDS)]
        comparisons[before + ' -> ' + VERSIONS[-1]] = dict(
            paired=len(valid), excluded_missing=len(pairs)-len(valid),
            delta={k: round(sum(p[VERSIONS[-1]][k]-p[before][k] for p in valid), 3)
                   for k in FIELDS},
            base_improved=sum(p[VERSIONS[-1]]['base'] > p[before]['base'] for p in valid),
            base_worsened=sum(p[VERSIONS[-1]]['base'] < p[before]['base'] for p in valid),
            goals_worsened=sum(p[VERSIONS[-1]]['final_goals'] < p[before]['final_goals'] for p in valid))
    with (OUT / 'COMPETITION_RUNS.csv').open('w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0]))
        writer.writeheader()
        writer.writerows(flat)
    summary = dict(selection='01/09/19/24/31/36; 24 runs per version; not full competition suite',
                   totals=totals, comparisons=comparisons)
    (OUT / 'COMPETITION_SUMMARY.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
