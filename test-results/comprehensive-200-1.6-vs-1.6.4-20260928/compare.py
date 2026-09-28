#!/usr/bin/env python3
"""Run the comprehensive suite against two unchanged clients and the official SDK."""
import collections
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SUITE = ROOT / '题目/2026_comprehensive_200'
SDK = Path('/home/yifan/env-release-2026')
SOURCES = {'1.6': ROOT / 'HistoryVersion/src1.6', '1.6.4': ROOT / 'src1.6.4'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def baseline_runner():
    path = ROOT / 'HistoryVersion/src1.1.2 (x)/tools/baseline.py'
    spec = importlib.util.spec_from_file_location('baseline', str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_case


def build(label, source):
    directory = OUT / ('build-' + label)
    directory.mkdir(exist_ok=True)
    executable = directory / 'example'
    sources = sorted(source.glob('*.cpp'))
    command = ['g++', '-std=c++11', '-O2', '-g', '-Wall', '-Wextra',
               '-I' + str(source), '-I' + str(SDK / 'include'),
               '-I' + str(SDK / 'src')] + [str(p) for p in sources] + [
               '-L' + str(SDK / 'lib'), '-lframe', '-lutility',
               '-lboost_thread', '-lboost_system', '-lboost_chrono',
               '-lboost_date_time', '-lboost_regex', '-lpthread', '-ldl',
               '-o', str(executable)]
    if not executable.exists():
        with (directory / 'build.log').open('w') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    (directory / 'build.json').write_text(json.dumps({
        'command': command, 'executable_sha256': sha(executable),
        'source_sha256': {p.name: sha(p) for p in source.iterdir()
                          if p.suffix in ('.cpp', '.hpp', '.txt')},
        'sdk_sha256': {str(p.relative_to(SDK)): sha(p) for p in [
            SDK / 'bin/cserver', SDK / 'lib/libasp.so', SDK / 'lib/libframe.a']}
        }, ensure_ascii=False, indent=2), encoding='utf-8')
    return executable


def setup_seed():
    lib = OUT / 'seed_rng.so'
    if not lib.exists():
        subprocess.run(['g++', '-shared', '-fPIC',
                        str(ROOT / 'src1.6.4/tests/seed_rng.cpp'),
                        '-ldl', '-o', str(lib)], check=True)
    clean_dir = Path(tempfile.mkdtemp(prefix='rdfw-comprehensive-seed-'))
    shutil.copy2(str(lib), str(clean_dir / 'seed_rng.so'))
    os.environ['LD_PRELOAD'] = str(clean_dir / 'seed_rng.so')
    os.environ['RDFW_TEST_SEED'] = '20260928'
    os.environ['RDFW_TASK_GROUP_MODE'] = 'guarded'
    os.environ['RDFW_STAGE_TIMING'] = '0'


def summarize(result, run_dir):
    server = (run_dir / 'server.log').read_text(encoding='utf-8', errors='replace') if (run_dir / 'server.log').exists() else ''
    client = (run_dir / 'client.log').read_text(encoding='utf-8', errors='replace') if (run_dir / 'client.log').exists() else ''
    actions = re.findall(r'^\s*\[([A-Za-z_]+(?:\s+[^|]*?)?)\|[^\]]*\]\s*$', server, re.M)
    action_cost = sum(4 if a.split()[0].lower() == 'move' else
                      1 if a.split()[0].lower() == 'sense' else 2 for a in actions)
    goals = result.get('final_goals')
    constraints = result.get('credited_constraints')
    decisions = [line for line in client.splitlines() if any(k in line for k in
                 ('[3A]', '[3B]', '[TradeoffDecision]', '[GuardedDecision]',
                  '[MultiGoto]', '[MultiPuton]', '[Defer]', '[Preflight]'))]
    return {'status': result.get('status'), 'raw_score': result.get('raw_score'),
            'official_score': result.get('official_score'),
            'base_score': None if goals is None or constraints is None else
                40 * goals + (20 * constraints if goals else 0) - action_cost,
            'goals': goals, 'constraints': constraints, 'action_cost': action_cost,
            'actions': actions, 'action_counts': dict(collections.Counter(
                a.split()[0].lower() for a in actions)),
            'observations': re.findall(r'^\s*(\[(?:Ask\w*|Sense)\b[^\]]*\])\s*$', server, re.M),
            'decisions': decisions, 'platform_seconds': result.get('platform_seconds'),
            'platform_timed_out': result.get('platform_timed_out'),
            'external_timeout': result.get('external_timeout'),
            'client_exit': result.get('client_exit'), 'server_exit': result.get('server_exit'),
            'seed_confirmed': '[RDFW_TEST_SEED] 20260928' in server,
            'output': str(run_dir.relative_to(OUT))}


def run():
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 7932))
    runner = baseline_runner()
    binaries = {label: build(label, source) for label, source in SOURCES.items()}
    setup_seed()
    assets = OUT / 'assets-v2'
    assets.mkdir(exist_ok=True)
    (assets / 'words.txt').write_bytes((ROOT / 'src1.6.4/words.txt').read_bytes().replace(b'\r\n', b'\n'))
    manifest = json.loads((SUITE / 'run_manifest.json').read_text(encoding='utf-8'))
    invalid = json.loads((SUITE / 'invalid/expected_errors.json').read_text(encoding='utf-8'))
    entries = [dict(x, kind='normal') for x in manifest]
    entries += [dict(id=x['id'], path=x['path'], kind='invalid', mode=mode,
                     stage=1) for x in invalid for mode in ('it', 'nt')]
    rows_path = OUT / 'results-v2.jsonl'
    completed = set()
    if rows_path.exists():
        for line in rows_path.read_text(encoding='utf-8').splitlines():
            try:
                x = json.loads(line)
                completed.add((x['id'], x['mode']))
            except json.JSONDecodeError:
                pass
    with rows_path.open('a', encoding='utf-8') as stream:
        for index, item in enumerate(entries):
            key = (item['id'], item['mode'])
            if key in completed:
                continue
            path = SUITE / item['path']
            pair = {}
            order = list(SOURCES) if index % 2 == 0 else list(reversed(list(SOURCES)))
            for label in order:
                run_dir = OUT / 'runs-v2' / item['id'] / item['mode'] / label
                try:
                    result = runner(SDK, assets, binaries[label], path,
                                    item['stage'], item['mode'], run_dir, 5000, None)
                    pair[label] = summarize(result, run_dir)
                except Exception as exc:
                    pair[label] = {'status': 'harness_exception', 'error': repr(exc),
                                   'output': str(run_dir.relative_to(OUT))}
            row = dict(id=item['id'], path=item['path'], stage=item['stage'],
                       kind=item['kind'], mode=item['mode'], sha256=sha(path),
                       versions=pair)
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
            stream.flush()
            print(index + 1, '/', len(entries), item['id'], item['mode'],
                  [(k, pair[k].get('status'), pair[k].get('raw_score')) for k in SOURCES],
                  flush=True)


if __name__ == '__main__':
    run()
