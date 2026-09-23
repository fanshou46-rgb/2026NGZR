#!/usr/bin/env python3
"""Build A/B and run the 20 marked-illegal fault-model cases on official SDK."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src1.1.2 (x)' / 'tools'))
from baseline import run_case


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(version, sdk, output):
    source = ROOT / version
    build_dir = output / ('build-' + version)
    build_dir.mkdir()
    executable = build_dir / 'example'
    sources = sorted(source.glob('*.cpp'))
    command = [
        'g++', '-std=c++11', '-O2', '-g', '-Wall', '-Wextra',
        '-I' + str(source), '-I' + str(sdk / 'include'), '-I' + str(sdk / 'src')
    ] + [str(path) for path in sources] + [
        '-L' + str(sdk / 'lib'), '-lframe', '-lutility', '-lboost_thread',
        '-lboost_system', '-lboost_chrono', '-lboost_date_time', '-lboost_regex',
        '-lpthread', '-ldl', '-o', str(executable)
    ]
    with (build_dir / 'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    metadata = {
        'command': command,
        'source_sha256': {path.name: digest(path) for path in sources},
        'sdk_sha256': {str(path.relative_to(sdk)): digest(path) for path in
                       [sdk / 'bin/cserver', sdk / 'lib/libasp.so',
                        sdk / 'lib/libframe.a']}
    }
    (build_dir / 'build.json').write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    return executable


def action_sequence(text):
    return [match.group(1) + ((' ' + match.group(2).strip()) if match.group(2) else '')
            for match in re.finditer(
                r'^\s*\[([A-Za-z_]+)(?:\s+([^|]*?))?\|[^\]]*\]\s*$', text, re.M)]


def enrich(result, run_dir):
    client = (run_dir / 'client.log').read_text(encoding='utf-8', errors='replace') \
        if (run_dir / 'client.log').exists() else ''
    server = (run_dir / 'server.log').read_text(encoding='utf-8', errors='replace') \
        if (run_dir / 'server.log').exists() else ''
    result['action_sequence'] = action_sequence(server)
    result['preflight'] = re.findall(r'\[Preflight\] task[^\r\n]+', client)
    result['preflight_duplicates'] = re.findall(
        r'\[Preflight\]\[Duplicate\] ([^\r\n]+)', client)
    result['preflight_world_errors'] = re.findall(
        r'\[Preflight\]\[World\] ([^\r\n]+)', client)
    result['parser_errors'] = re.findall(
        r'(?:Isolated malformed instruction form|Ignoring malformed [^\r\n]+|'
        r'isolated instruction[^\r\n]+)', client, re.I)
    result['risk_skips'] = re.findall(r'([^\r\n]*风险系数是：[^\r\n]*)', client)
    return result


def compare(rows, results):
    by_key = {(result['version'], result['id']): result for result in results}
    comparisons = []
    for row in rows:
        left = by_key.get(('src1.3.3A', row['id']), {})
        right = by_key.get(('src1.3.3B', row['id']), {})
        left_actions = left.get('action_sequence', [])
        right_actions = right.get('action_sequence', [])
        first_difference = None
        for index in range(min(len(left_actions), len(right_actions))):
            if left_actions[index] != right_actions[index]:
                first_difference = {
                    'index': index, 'a': left_actions[index], 'b': right_actions[index]}
                break
        if first_difference is None and len(left_actions) != len(right_actions):
            index = min(len(left_actions), len(right_actions))
            first_difference = {
                'index': index,
                'a': left_actions[index] if index < len(left_actions) else None,
                'b': right_actions[index] if index < len(right_actions) else None}
        comparisons.append({
            'id': row['id'], 'stage': int(row['stage']), 'fault_id': row['fault_id'],
            'fault': row['fault'], 'expected_boundary': row['expected_boundary'],
            'a_status': left.get('status'), 'b_status': right.get('status'),
            'a_score': left.get('official_score'), 'b_score': right.get('official_score'),
            'score_delta_b_minus_a': ((right.get('official_score') or 0) -
                                      (left.get('official_score') or 0)),
            'a_actions': len(left_actions), 'b_actions': len(right_actions),
            'actions_equal': left_actions == right_actions,
            'first_action_difference': first_difference,
            'b_duplicates': right.get('preflight_duplicates', []),
            'b_world_errors': right.get('preflight_world_errors', []),
            'a_risk_skips': left.get('risk_skips', []),
            'b_risk_skips': right.get('risk_skips', [])
        })
    return comparisons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--manifest', type=Path,
                        default=ROOT / '题目' / 'illegal_fault_model_2026' / 'manifest.csv')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sdk = args.sdk.resolve()
    manifest = args.manifest.resolve()
    output = args.output.resolve()
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 7932))
    output.mkdir(parents=True, exist_ok=False)
    with manifest.open(encoding='utf-8-sig') as stream:
        rows = list(csv.DictReader(stream))
    results = []
    for version in ('src1.3.3A', 'src1.3.3B'):
        executable = build(version, sdk, output)
        for row in rows:
            case = manifest.parent / row['file']
            run_dir = output / version / row['id']
            try:
                result = run_case(sdk, ROOT / version, executable, case,
                                  int(row['stage']), 'it', run_dir, 5000, None)
            except Exception as error:
                result = {
                    'status': 'runner_error', 'official_score': None,
                    'raw_score': None, 'action_count': 0,
                    'error': '{}: {}'.format(type(error).__name__, error)}
            result.update({
                'version': version, 'id': row['id'], 'stage': int(row['stage']),
                'file': row['file'], 'fault_id': row['fault_id'], 'fault': row['fault'],
                'case_sha256': digest(case)})
            enrich(result, run_dir)
            results.append(result)
            (output / 'results.json').write_text(
                json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
            print(version, row['id'], result['status'], result.get('official_score'),
                  len(result['action_sequence']), flush=True)
    comparisons = compare(rows, results)
    (output / 'comparison.json').write_text(
        json.dumps(comparisons, ensure_ascii=False, indent=2), encoding='utf-8')
    with (output / 'comparison.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        fields = ['id', 'stage', 'fault_id', 'fault', 'a_status', 'b_status',
                  'a_score', 'b_score', 'score_delta_b_minus_a', 'a_actions',
                  'b_actions', 'actions_equal']
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(comparisons)


if __name__ == '__main__':
    main()
