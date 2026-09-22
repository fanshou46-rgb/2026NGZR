#!/usr/bin/env python3
"""Build and compare src1.3.2 and src1.3.3A on all 36 realcompetition cases."""

import collections
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys


ROOT = Path('/mnt/d/FILES for Yvaine/WUT/Match/robocup/2026NGZR')
SDK = Path('/mnt/d/FILES for Yvaine/WUT/Match/robocup/NFSQ4.2')
RESULT_ROOT = ROOT / 'test-results/realcompetition-src132-vs-src133A-all36-20260922'
VERSIONS = ('src1.3.2', 'src1.3.3A')
CASES = tuple(range(1, 37))
RUN_PREFIX = 'runs-full-'

sys.path.insert(0, str(ROOT / 'src1.1.2 (x)' / 'tools'))
from baseline import run_case


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(version):
    source = ROOT / version
    output = RESULT_ROOT / ('build-' + version)
    executable = output / 'example'
    if executable.exists():
        return executable
    output.mkdir(parents=True, exist_ok=True)
    sources = (
        'main.cpp', 'rdfw.cpp', 'parser.cpp', 'deadline_manager.cpp',
        'terminal_checker.cpp', 'score_evaluator.cpp', 'candidate_plan.cpp')
    command = [
        'g++', '-std=c++11', '-O2', '-g', '-Wall', '-Wextra',
        '-I' + str(source), '-I' + str(SDK / 'include'),
        '-I' + str(SDK / 'src'),
    ] + [str(source / name) for name in sources] + [
        '-L' + str(SDK / 'lib'), '-lframe', '-lutility', '-lboost_thread',
        '-lboost_system', '-lboost_chrono', '-lboost_date_time',
        '-lboost_regex', '-lpthread',
        '-ldl', '-o', str(executable),
    ]
    with (output / 'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    metadata = {
        'command': command,
        'source_sha256': {
            name: digest(source / name) for name in sources
        },
    }
    (output / 'build.json').write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    return executable


def run_version(version, executable):
    source = ROOT / version
    output = RESULT_ROOT / (RUN_PREFIX + version)
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for number in CASES:
        case = ROOT / '题目/realcompetiton_2024/{:02d}.xml'.format(number)
        result = run_case(
            SDK, source, executable, case, 2, 'it',
            output / '{:02d}-s2-it'.format(number), 5000, None)
        result['id'] = '{:02d}'.format(number)
        results.append(result)
        (output / 'suite.json').write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        print(version, result['id'], result['status'],
              result.get('official_score'), result.get('action_count'),
              result.get('platform_seconds'), flush=True)
    return results


def action_sequence(path):
    text = path.read_text(encoding='utf-8', errors='replace')
    sequence = []
    for match in re.finditer(
            r'^\s*\[([A-Za-z_]+)(?:\s+([^|]*?))?\|[^\]]*\]\s*$', text, re.M):
        operation = match.group(1)
        arguments = (match.group(2) or '').strip()
        sequence.append(operation + ((' ' + arguments) if arguments else ''))
    return sequence


def observation_sequence(path):
    text = path.read_text(encoding='utf-8', errors='replace')
    return [match.group(0).strip() for match in re.finditer(
        r'^\s*\[(?:Ask[A-Za-z_]*|Sense)\b[^\]]*\]\s*$', text, re.M)]


def is_strict_prefix(left, right):
    return len(left) < len(right) and left == right[:len(left)]


def compare(left_results, right_results):
    rows = []
    for left, right in zip(left_results, right_results):
        number = left['id']
        left_sequence = action_sequence(
            RESULT_ROOT / (RUN_PREFIX + 'src1.3.2') /
            (number + '-s2-it/server.log'))
        right_sequence = action_sequence(
            RESULT_ROOT / (RUN_PREFIX + 'src1.3.3A') /
            (number + '-s2-it/server.log'))
        left_observations = observation_sequence(
            RESULT_ROOT / (RUN_PREFIX + 'src1.3.2') /
            (number + '-s2-it/server.log'))
        right_observations = observation_sequence(
            RESULT_ROOT / (RUN_PREFIX + 'src1.3.3A') /
            (number + '-s2-it/server.log'))
        first_difference = None
        for index, pair in enumerate(zip(left_sequence, right_sequence)):
            if pair[0] != pair[1]:
                first_difference = index
                break
        if first_difference is None and len(left_sequence) != len(right_sequence):
            first_difference = min(len(left_sequence), len(right_sequence))
        row = {
            'id': number,
            'status_1.3.2': left['status'],
            'status_1.3.3A': right['status'],
            'score_1.3.2': left.get('official_score'),
            'score_1.3.3A': right.get('official_score'),
            'score_delta': (right['official_score'] - left['official_score'])
                if left.get('official_score') is not None
                and right.get('official_score') is not None else None,
            'goals_1.3.2': left.get('final_goals'),
            'goals_1.3.3A': right.get('final_goals'),
            'constraints_1.3.2': left.get('credited_constraints'),
            'constraints_1.3.3A': right.get('credited_constraints'),
            'actions_1.3.2': len(left_sequence),
            'actions_1.3.3A': len(right_sequence),
            'seconds_1.3.2': left.get('platform_seconds'),
            'seconds_1.3.3A': right.get('platform_seconds'),
            'exact_action_sequence': left_sequence == right_sequence,
            'same_observation_sequence': left_observations == right_observations,
            'src132_action_is_strict_prefix': is_strict_prefix(
                left_sequence, right_sequence),
            'first_action_difference': first_difference,
            'action_sequence_1.3.2': left_sequence,
            'action_sequence_1.3.3A': right_sequence,
            'observation_sequence_1.3.2': left_observations,
            'observation_sequence_1.3.3A': right_observations,
            'action_counts_1.3.2': dict(collections.Counter(
                action.split(' ', 1)[0].lower() for action in left_sequence)),
            'action_counts_1.3.3A': dict(collections.Counter(
                action.split(' ', 1)[0].lower() for action in right_sequence)),
        }
        rows.append(row)
    (RESULT_ROOT / 'comparison.json').write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    columns = [key for key in rows[0] if not key.startswith('action_sequence_')
               and not key.startswith('action_counts_')
               and not key.startswith('observation_sequence_')]
    with (RESULT_ROOT / 'comparison.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows({key: row[key] for key in columns} for row in rows)
    return rows


def main():
    global RUN_PREFIX, SDK, RESULT_ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--run-label', default='full',
        help='unique label for raw run directories (default: full)')
    parser.add_argument(
        '--sdk', type=Path, default=SDK,
        help='competition SDK root')
    parser.add_argument(
        '--result-root', type=Path, default=RESULT_ROOT,
        help='directory for builds, raw runs, and comparison files')
    args = parser.parse_args()
    if not re.match(r'^[A-Za-z0-9._-]+$', args.run_label):
        parser.error('run label may contain only letters, digits, dot, underscore, or dash')
    RUN_PREFIX = 'runs-' + args.run_label + '-'
    SDK = args.sdk.resolve()
    RESULT_ROOT = args.result_root.resolve()
    compat = Path('/opt/boost174-compat/usr/lib/x86_64-linux-gnu')
    paths = [str(path) for path in (compat, SDK / 'lib') if path.exists()]
    if os.environ.get('LD_LIBRARY_PATH'):
        paths.append(os.environ['LD_LIBRARY_PATH'])
    os.environ['LD_LIBRARY_PATH'] = ':'.join(paths)
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 7932))
    executables = {version: build(version) for version in VERSIONS}
    results = {
        version: run_version(version, executables[version]) for version in VERSIONS
    }
    rows = compare(results['src1.3.2'], results['src1.3.3A'])
    failures = sum(row['status_1.3.2'] != 'ok'
                   or row['status_1.3.3A'] != 'ok' for row in rows)
    print('comparison complete:', len(rows), 'cases,', failures, 'failed pairs')
    return int(failures != 0)


if __name__ == '__main__':
    raise SystemExit(main())
