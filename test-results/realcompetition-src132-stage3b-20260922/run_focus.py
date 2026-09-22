#!/usr/bin/env python3
"""Run the Stage 3B focus set against the locally available competition SDK."""

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path('/mnt/d/FILES for Yvaine/WUT/Match/robocup/2026NGZR')
SDK = Path('/mnt/d/FILES for Yvaine/WUT/Match/robocup/NFSQ4.2')
SOURCE = ROOT / 'src1.3.2'
BUILD = ROOT / 'test-results/realcompetition-src132-stage3b-20260922/build'
EXECUTABLE = BUILD / 'example'
OUTPUT = ROOT / 'test-results/realcompetition-src132-stage3b-20260922/runs-fixed'
FOCUS = (11, 13, 16, 19, 21, 22, 23, 24, 28, 29, 30, 34, 35, 36)

sys.path.insert(0, str(ROOT / 'src1.1.2 (x)' / 'tools'))
from baseline import run_case


def build():
    BUILD.mkdir(parents=True, exist_ok=True)
    sources = ('main.cpp', 'rdfw.cpp', 'parser.cpp', 'deadline_manager.cpp',
               'terminal_checker.cpp', 'score_evaluator.cpp', 'candidate_plan.cpp')
    command = [
        'g++', '-std=c++11', '-O2', '-g', '-Wall', '-Wextra',
        '-I' + str(SOURCE), '-I' + str(SDK / 'include'), '-I' + str(SDK / 'src'),
    ] + [str(SOURCE / name) for name in sources] + [
        '-L' + str(SDK / 'lib'), '-lframe', '-lutility', '-lboost_thread',
        '-lboost_chrono', '-lboost_date_time', '-lboost_regex', '-lpthread',
        '-ldl', '-o', str(EXECUTABLE),
    ]
    with (BUILD / 'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)


def main():
    compat = Path('/opt/boost174-compat/usr/lib/x86_64-linux-gnu')
    if compat.exists():
        old_path = os.environ.get('LD_LIBRARY_PATH', '')
        os.environ['LD_LIBRARY_PATH'] = str(compat) + (':' + old_path if old_path else '')
    if not EXECUTABLE.exists():
        build()
    OUTPUT.mkdir(parents=True, exist_ok=False)
    results = []
    for number in FOCUS:
        case = ROOT / '题目/realcompetiton_2024/{:02d}.xml'.format(number)
        result = run_case(
            SDK, SOURCE, EXECUTABLE, case, 2, 'it',
            OUTPUT / '{:02d}-s2-it'.format(number), 5000, None)
        result['id'] = '{:02d}'.format(number)
        results.append(result)
        (OUTPUT / 'suite.json').write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        print(result['id'], result['status'], result.get('official_score'),
              result.get('platform_seconds'), flush=True)
    return int(any(item['status'] != 'ok' for item in results))


if __name__ == '__main__':
    raise SystemExit(main())
