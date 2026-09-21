#!/usr/bin/env python3
"""Build and run paired clients against an unchanged official Linux SDK (Python 3.6+)."""
import argparse
import collections
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import time
import xml.etree.ElementTree as ET


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(source, sdk, output):
    output.mkdir(parents=True, exist_ok=False)
    command = ['g++', '-std=c++11', '-O2', '-g', '-Wall', '-Wextra',
               '-I' + str(sdk / 'include'), '-I' + str(sdk / 'src'),
               str(source / 'main.cpp'), str(source / 'rdfw.cpp'), str(source / 'parser.cpp'),
               '-L' + str(sdk / 'lib'), '-lframe', '-lutility', '-lboost_thread',
               '-lboost_system', '-lboost_chrono', '-lboost_date_time', '-lboost_regex',
               '-lpthread', '-ldl', '-o', str(output / 'example')]
    with (output / 'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    metadata = {'command': command, 'source_sha256': {
        p.name: digest(p) for p in sorted(source.iterdir())
        if p.is_file() and p.suffix in ('.cpp', '.hpp', '.txt')},
        'sdk_sha256': {str(p.relative_to(sdk)): digest(p) for p in
                       [sdk / 'bin/cserver', sdk / 'lib/libasp.so', sdk / 'lib/libframe.a']}}
    (output / 'build.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')


def parse_result(server_text, client_text, limit_ms):
    scores = re.findall(r'^# Score:\s*(-?\d+)', server_text, re.M)
    times = re.findall(r'^# Time:\s*([\d.]+)s', server_text, re.M)
    # Count exactly one canonical stream, never concatenated duplicated logs.
    actions = collections.Counter(a.lower() for a in re.findall(
        r'^\s*\[([A-Za-z_]+)(?:\s[^|]*)?\|', server_text, re.M))
    metrics = re.findall(r'^RDFW_METRICS (.+)$', client_text, re.M)
    elapsed = float(times[-1]) if times else None
    return {'raw_score': int(scores[-1]) if scores else None,
            'official_score': min(int(scores[-1]), 1000) if scores else None,
            'platform_seconds': elapsed,
            'platform_timed_out': elapsed is not None and elapsed * 1000 >= limit_ms,
            'actions': dict(actions), 'action_count': sum(actions.values()),
            'client_metrics': json.loads(metrics[-1]) if metrics else None}


def parse_evaluation(text):
    """Read the official final answer set; never substitute the client's task counter."""
    if not re.search(r'^SATISFIABLE\s*$', text, re.M):
        return {'final_goals': None, 'credited_constraints': None}
    values = set((int(i), int(score)) for i, score in re.findall(r'value\((\d+),(\d+)\)', text))
    return {'final_goals': sum(score == 40 for _, score in values),
            'credited_constraints': sum(score == 20 for _, score in values)}


def stop(process):
    if process is not None and process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def run_case(sdk, source, executable, case, stage, mode, output, limit_ms, budget_ms):
    output.mkdir(parents=True, exist_ok=False)
    work = output / 'runtime'
    work.mkdir()
    (work / 'tests').mkdir()
    (work / 'log').mkdir()
    shutil.copy2(str(case), str(work / 'tests/case.xml'))
    (work / 'tests/test.list').write_text('case.xml\n', encoding='utf-8')
    # The evaluator writes files in cwd; isolate every run from the installed SDK.
    for item in list((sdk / 'res').glob('*.lp')) + [sdk / 'res/iclingo',
            sdk / 'bin/vrunact.sh', sdk / 'bin/vruntask.sh']:
        shutil.copy2(str(item), str(work / item.name))
    (work / 'iclingo').chmod(0o755)
    for script in work.glob('*.sh'):
        script.chmod(0o755)
    server_cmd = [str(sdk / 'bin/cserver'), '-td', str(work / 'tests'),
                  '-eval', str(sdk / 'lib/libasp'), '-log', str(work / 'log'),
                  '-mode', mode, '-test', '1', '-to', str(limit_ms)]
    client_cmd = [str(executable), '-stage', str(stage), '-nlp', str(int(mode == 'nt')),
                  '-err', str(int(stage == 2)), '-ask_2', str(int(stage == 2)),
                  '-path', str(source / 'words.txt')]
    if budget_ms is not None:
        client_cmd += ['-budget_ms', str(budget_ms)]
    server = client = None
    external_timeout = False
    started = time.monotonic()
    try:
        with (output / 'server.log').open('w') as slog, (output / 'client.log').open('w') as clog:
            server = subprocess.Popen(server_cmd, cwd=str(work), stdout=slog,
                                      stderr=subprocess.STDOUT, start_new_session=True)
            time.sleep(0.3)
            if server.poll() is not None:
                raise RuntimeError('cserver failed to start; inspect server.log')
            client = subprocess.Popen(client_cmd, cwd=str(work), stdout=clog,
                                      stderr=subprocess.STDOUT, start_new_session=True)
            try:
                client.wait(timeout=limit_ms / 1000.0 + 10)
            except subprocess.TimeoutExpired:
                external_timeout = True
            finally:
                stop(client)
                stop(server)
    finally:
        stop(client)
        stop(server)
    server_text = (output / 'server.log').read_text(encoding='utf-8', errors='replace')
    client_text = (output / 'client.log').read_text(encoding='utf-8', errors='replace')
    result = parse_result(server_text, client_text, limit_ms)
    answer = work / 'vanswer.txt'
    result.update(parse_evaluation(answer.read_text(encoding='utf-8', errors='replace')
                                  if answer.exists() else ''))
    result['platform_error'] = any(marker in server_text for marker in
        ['not found', 'not existed', 'can not be opened', 'Failed to begin', 'Syntax Error'])
    result.update({'case': str(case), 'case_sha256': digest(case), 'stage': stage,
                   'mode': mode, 'wall_seconds': time.monotonic() - started,
                   'external_timeout': external_timeout, 'client_exit': client.returncode,
                   'server_exit': server.returncode, 'commands': [server_cmd, client_cmd],
                   'limit_ms': limit_ms, 'budget_ms': budget_ms})
    result['status'] = ('ok' if result['raw_score'] is not None and client.returncode == 0
                        and not external_timeout and not result['platform_timed_out']
                        and not result['platform_error'] else 'failed')
    (output / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action')
    b = sub.add_parser('build')
    b.add_argument('--source', type=Path, required=True)
    b.add_argument('--sdk', type=Path, required=True)
    b.add_argument('--output', type=Path, required=True)
    r = sub.add_parser('run')
    r.add_argument('--source', type=Path, required=True)
    r.add_argument('--sdk', type=Path, required=True)
    r.add_argument('--executable', type=Path, required=True)
    r.add_argument('--manifest', type=Path, required=True)
    r.add_argument('--output', type=Path, required=True)
    r.add_argument('--limit-ms', type=int, default=5000)
    r.add_argument('--budget-ms', type=int)
    r.add_argument('--repeat', type=int, default=1)
    args = parser.parse_args()
    if args.action == 'build':
        build(args.source.resolve(), args.sdk.resolve(), args.output.resolve())
    elif args.action == 'run':
        # SDK uses fixed client port. Do not attach to another team's/live server.
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 7932))
        args.output = args.output.resolve()
        args.output.mkdir(parents=True, exist_ok=False)
        results = []
        with args.manifest.open(encoding='utf-8-sig') as stream:
            rows = list(csv.DictReader(stream))
        for repetition in range(args.repeat):
            for row in rows:
                case = (args.manifest.parent / row['path']).resolve()
                env = ET.parse(str(case)).getroot().find('env')
                stage = int(row['stage'])
                expected = 'off' if stage == 1 else 'on'
                if env is None or any(env.get(k) != expected for k in ('mis', 'err', 'ans')):
                    raise ValueError('stage/flags mismatch: ' + str(case))
                key = '{}-s{}-{}-r{}'.format(row['id'], stage, row['mode'], repetition + 1)
                result = run_case(args.sdk.resolve(), args.source.resolve(),
                                  args.executable.resolve(), case, stage, row['mode'],
                                  args.output / key, args.limit_ms, args.budget_ms)
                result['id'] = row['id']
                result['repeat'] = repetition + 1
                results.append(result)
                print(key, result['status'], result['raw_score'], flush=True)
                (args.output / 'suite.json').write_text(
                    json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        return int(any(r['status'] != 'ok' for r in results))
    else:
        parser.error('choose build or run')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
