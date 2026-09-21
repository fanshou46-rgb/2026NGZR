#!/usr/bin/env python3
"""Build src1.3/src1.3.1 and run the 36 realcompetition2024 cases."""
import json
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path('/mnt/d/FILES for Yvaine/WUT/Match/robocup/2026NGZR')
SDK = Path('/home/yifan/env-release-2026')
BASE = ROOT / 'test-results/realcompetition-src13-vs-src131-20260921'
TOOLS = ROOT / 'src1.1.2 (x)' / 'tools'
sys.path.insert(0, str(TOOLS))

from baseline import digest, run_case

VERSIONS = ('src1.3', 'src1.3.1')
EXTRA_SOURCES = {
    'src1.3': (),
    'src1.3.1': ('deadline_manager.cpp', 'terminal_checker.cpp', 'score_evaluator.cpp'),
}


def build(version):
    source = ROOT / version
    output = BASE / ('build-' + version)
    output.mkdir(parents=True, exist_ok=False)
    sources = ['main.cpp', 'rdfw.cpp', 'parser.cpp'] + list(EXTRA_SOURCES[version])
    command = [
        'g++', '-std=c++11', '-O2', '-g', '-Wall', '-Wextra',
        '-I' + str(source), '-I' + str(SDK / 'include'), '-I' + str(SDK / 'src'),
    ] + [str(source / name) for name in sources] + [
        '-L' + str(SDK / 'lib'), '-lframe', '-lutility', '-lboost_thread',
        '-lboost_system', '-lboost_chrono', '-lboost_date_time', '-lboost_regex',
        '-lpthread', '-ldl', '-o', str(output / 'example'),
    ]
    with (output / 'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    metadata = {
        'command': command,
        'source_sha256': {
            path.name: digest(path) for path in sorted(source.iterdir())
            if path.is_file() and path.suffix in ('.cpp', '.hpp', '.txt')
        },
        'sdk_sha256': {
            str(path.relative_to(SDK)): digest(path)
            for path in (SDK / 'bin/cserver', SDK / 'lib/libasp.so', SDK / 'lib/libframe.a')
        },
    }
    (output / 'build.json').write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')


def run_version(version, repetition):
    source = ROOT / version
    executable = BASE / ('build-' + version) / 'example'
    output = BASE / ('runs-{}-r{}'.format(version, repetition))
    output.mkdir(parents=True, exist_ok=False)
    suite = []
    for number in range(1, 37):
        case = ROOT / '题目' / 'realcompetiton_2024' / ('{:02d}.xml'.format(number))
        stage = 1 if number == 2 else 2
        case_output = output / ('{:02d}-s{}-it'.format(number, stage))
        try:
            result = run_case(
                SDK, source, executable, case, stage, 'it', case_output, 5000, None)
        except Exception as error:
            case_output.mkdir(parents=True, exist_ok=True)
            result = {
                'case': str(case), 'stage': stage, 'mode': 'it',
                'status': 'runner-error', 'raw_score': None, 'official_score': None,
                'error': repr(error), 'traceback': traceback.format_exc(),
            }
            (case_output / 'runner-error.json').write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        result['id'] = '{:02d}'.format(number)
        result['repeat'] = repetition
        suite.append(result)
        (output / 'suite.json').write_text(
            json.dumps(suite, ensure_ascii=False, indent=2), encoding='utf-8')
        print(version, 'r{}'.format(repetition), result['id'], result['status'],
              result.get('raw_score'), flush=True)


def main():
    if len(sys.argv) < 2:
        raise SystemExit('usage: run_all.py build | VERSION REPETITION')
    if sys.argv[1] == 'build':
        for version in VERSIONS:
            build(version)
        return
    version = sys.argv[1]
    if version not in VERSIONS:
        raise SystemExit('unknown version: ' + version)
    repetition = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    run_version(version, repetition)


if __name__ == '__main__':
    main()
