#!/usr/bin/env python3
"""Run the src1.3.3A safety regression focus set on the local SDK."""

import json
import os
import argparse
from pathlib import Path
import sys

ROOT = Path('/mnt/d/FILES for Yvaine/WUT/Match/robocup/2026NGZR')
SDK = Path('/mnt/d/FILES for Yvaine/WUT/Match/robocup/NFSQ4.2')
SOURCE = ROOT / 'src1.3.3A'
EXECUTABLE = ROOT / 'test-results/src1.3.3A-build/example'
RESULT_ROOT = ROOT / 'test-results/realcompetition-src133A-input-safety-20260922'
DEFAULT_OUTPUT_NAME = 'runs-fast'
FOCUS = (11, 13, 16, 19, 21, 22, 23, 24, 28, 29, 30, 34, 35, 36)

sys.path.insert(0, str(ROOT / 'src1.1.2 (x)' / 'tools'))
from baseline import run_case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cases', type=int, nargs='*', help='optional case numbers')
    parser.add_argument('--output-name', default=DEFAULT_OUTPUT_NAME)
    args = parser.parse_args()
    focus = tuple(args.cases) if args.cases else FOCUS
    output = RESULT_ROOT / args.output_name

    compat = Path('/opt/boost174-compat/usr/lib/x86_64-linux-gnu')
    sdk_lib = SDK / 'lib'
    paths = [str(path) for path in (compat, sdk_lib) if path.exists()]
    old_path = os.environ.get('LD_LIBRARY_PATH', '')
    if old_path:
        paths.append(old_path)
    os.environ['LD_LIBRARY_PATH'] = ':'.join(paths)

    if not EXECUTABLE.exists():
        raise RuntimeError('build src1.3.3A executable before running regression')
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for number in focus:
        case = ROOT / '题目/realcompetiton_2024/{:02d}.xml'.format(number)
        result = run_case(
            SDK, SOURCE, EXECUTABLE, case, 2, 'it',
            output / '{:02d}-s2-it'.format(number), 5000, None)
        result['id'] = '{:02d}'.format(number)
        results.append(result)
        (output / 'suite.json').write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        print(result['id'], result['status'], result.get('official_score'),
              result.get('platform_seconds'), flush=True)
    return int(any(item['status'] != 'ok' for item in results))


if __name__ == '__main__':
    raise SystemExit(main())
