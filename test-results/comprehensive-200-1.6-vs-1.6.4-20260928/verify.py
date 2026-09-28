#!/usr/bin/env python3
"""Audit all paired runs against retained platform summaries and build hashes."""
import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = {'1.6': ROOT / 'HistoryVersion/src1.6',
           '1.6.4': ROOT / 'src1.6.4'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = [json.loads(line) for line in (HERE / 'results-v2.jsonl').read_text(
        encoding='utf-8').splitlines() if line.strip()]
    issues = []
    keys = [(r['id'], r['mode']) for r in rows]
    if len(rows) != 400 or len(set(keys)) != 400:
        issues.append('expected exactly 400 unique case/mode pairs')
    status = collections.Counter()
    for row in rows:
        case = ROOT / '题目/2026_comprehensive_200' / row['path']
        if digest(case) != row['sha256']:
            issues.append('case hash mismatch: ' + row['id'])
        for label in SOURCES:
            data = row['versions'][label]
            path = HERE / data['output']
            retained = json.loads((path / 'summary.json').read_text(encoding='utf-8'))
            status[(row['kind'], label, data['status'])] += 1
            if not data.get('seed_confirmed'):
                issues.append('seed not confirmed: ' + str(path))
            if data['status'] != retained['status'] or data.get('raw_score') != retained['raw_score']:
                issues.append('summary mismatch: ' + str(path))
            if len(data.get('actions', [])) != retained['action_count']:
                issues.append('action count mismatch: ' + str(path))
            if data.get('platform_timed_out') or data.get('external_timeout'):
                issues.append('timeout: ' + str(path))
            goals, constraints = data.get('goals'), data.get('constraints')
            if goals is not None and constraints is not None:
                computed = 40 * goals + (20 * constraints if goals else 0) - data['action_cost']
                if computed != data['base_score']:
                    issues.append('base score mismatch: ' + str(path))
            if row['kind'] == 'normal' and data['status'] != 'ok':
                issues.append('normal case failed: ' + str(path))
    source_hashes = {}
    for label, source in SOURCES.items():
        build = json.loads((HERE / ('build-' + label) / 'build.json').read_text(
            encoding='utf-8'))
        exe = HERE / ('build-' + label) / 'example'
        if digest(exe) != build['executable_sha256']:
            issues.append('binary hash mismatch: ' + label)
        source_hashes[label] = build['source_sha256']
        for filename, expected in build['source_sha256'].items():
            if digest(source / filename) != expected:
                issues.append('source hash mismatch: ' + label + '/' + filename)
    result = {'pair_count': len(rows), 'run_count': len(rows) * 2,
              'status': {'/'.join(k): v for k, v in sorted(status.items())},
              'source_file_count': {k: len(v) for k, v in source_hashes.items()},
              'issues': issues}
    (HERE / 'verification.json').write_text(json.dumps(result, ensure_ascii=False,
        indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    return int(bool(issues))


if __name__ == '__main__':
    raise SystemExit(main())
