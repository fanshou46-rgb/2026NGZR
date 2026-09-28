#!/usr/bin/env python3
"""A/B smoke comparison using the existing isolated official-platform runner.

No XML rewriting/validation or simulator is introduced. Python 3.6+, Linux SDK.
"""
import argparse
import json
from pathlib import Path
import re
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src1.1.2 (x)' / 'tools'))
from baseline import digest, run_case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cases', nargs='+', type=int, default=list(range(1, 37)))
    parser.add_argument('--versions', nargs='+', choices=['src1.3.3A', 'src1.3.3B'],
                        default=['src1.3.3A', 'src1.3.3B'])
    args = parser.parse_args()
    sdk = args.sdk.resolve()
    output = args.output.resolve()
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 7932))
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for version in args.versions:
        source = ROOT / version
        build = output / ('build-' + version)
        build.mkdir()
        executable = build / 'example'
        sources = sorted(source.glob('*.cpp'))
        command = ['g++', '-std=c++11', '-O2', '-g', '-Wall', '-Wextra',
                   '-I' + str(source), '-I' + str(sdk / 'include'), '-I' + str(sdk / 'src')]
        command += [str(p) for p in sources]
        command += ['-L' + str(sdk / 'lib'), '-lframe', '-lutility', '-lboost_thread',
                    '-lboost_system', '-lboost_chrono', '-lboost_date_time',
                    '-lboost_regex', '-lpthread', '-ldl', '-o', str(executable)]
        with (build / 'build.log').open('w') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        (build / 'build.json').write_text(json.dumps({
            'command': command, 'source_sha256': {p.name: digest(p) for p in sources},
            'sdk_sha256': {str(p.relative_to(sdk)): digest(p) for p in
                           [sdk / 'bin/cserver', sdk / 'lib/libasp.so', sdk / 'lib/libframe.a']}
        }, indent=2), encoding='utf-8')
        for number in args.cases:
            case_id = '{:02d}'.format(number)
            run_output = output / version / case_id
            result = run_case(sdk, source, executable,
                              ROOT / '题目' / 'realcompetiton_2024' / (case_id + '.xml'),
                              2, 'it', run_output, 5000, None)
            result.update(version=version, id=case_id)
            client = (run_output / 'client.log').read_text(encoding='utf-8', errors='replace')
            result['preflight'] = re.findall(r'\[Preflight\] task[^\r\n]+', client)
            result['world_errors'] = re.findall(r'\[Preflight\]\[World\][^\r\n]+', client)
            result['duplicate_keys'] = re.findall(r'\[Preflight\]\[Duplicate\] ([^\r\n]+)', client)
            results.append(result)
            (output / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2),
                                                encoding='utf-8')
            print(version, case_id, result['status'], result.get('official_score'),
                  result['action_count'], result['preflight'], flush=True)


if __name__ == '__main__':
    main()
