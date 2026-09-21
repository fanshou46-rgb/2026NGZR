#!/usr/bin/env python3
import json
from pathlib import Path
import sys
import traceback

ROOT = Path('/mnt/d/FILES for Yvaine/WUT/Match/robocup/2026NGZR')
SDK = Path('/home/yifan/env-release-2026')
TOOLS = ROOT / 'scr1.1.2 (x)' / 'tools'
sys.path.insert(0, str(TOOLS))

from baseline import run_case


def run_version(version, repetition):
    source = ROOT / version
    executable = ROOT / 'test-results/realcompetition-scr12-vs-scr13-20260921' / ('build-' + version[3:]) / 'example'
    suffix = '' if repetition == 1 else '-r{}'.format(repetition)
    output = ROOT / 'test-results/realcompetition-scr12-vs-scr13-20260921' / ('runs-' + version + suffix)
    output.mkdir(parents=True, exist_ok=False)
    suite = []
    for number in range(1, 37):
        case = ROOT / '题目' / 'realcompetiton_2024' / ('{:02d}.xml'.format(number))
        stage = 1 if number == 2 else 2
        case_output = output / ('{:02d}-s{}-it'.format(number, stage))
        try:
            result = run_case(SDK, source, executable, case, stage, 'it', case_output, 5000, None)
        except Exception as error:
            result = {
                'case': str(case),
                'stage': stage,
                'mode': 'it',
                'status': 'runner-error',
                'raw_score': None,
                'official_score': None,
                'error': repr(error),
                'traceback': traceback.format_exc(),
            }
            (case_output / 'runner-error.json').write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        result['id'] = '{:02d}'.format(number)
        suite.append(result)
        (output / 'suite.json').write_text(
            json.dumps(suite, ensure_ascii=False, indent=2), encoding='utf-8')
        print(version, result['id'], result['status'], result.get('raw_score'), flush=True)


if __name__ == '__main__':
    run_version(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
