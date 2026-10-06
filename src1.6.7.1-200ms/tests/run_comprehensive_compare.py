#!/usr/bin/env python3
"""Serial, append-only 1.6.7-200ms / 1.6.7.1-200ms official comprehensive-200 comparison.

The bank and the SDK are immutable. Invalid cases are retained separately.
All attempted actions and SDK grades come from the official server stream.
Python 3.6+; run on the compatible Linux SDK platform.
"""
import argparse
import collections
import csv
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
import time

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1]
ROOT = SOURCE.parent
BANK = ROOT / '题目/2026_comprehensive_200'
BASELINE = ROOT / 'src1.6.7-200ms'
ARMS = ('baseline', 'current')
FIELDS = ('final_goals', 'credited_constraints', 'action_cost', 'base', 'official_score', 'platform_seconds')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def product(source):
    return {p.name: sha(p) for p in sorted(source.iterdir())
            if p.is_file() and (p.suffix in ('.cpp', '.hpp', '.h') or p.name in ('words.txt', 'CMakeLists.txt'))}


def sdk_files(sdk):
    result = {}
    for folder in ('src', 'include', 'res'):
        for p in sorted((sdk / folder).rglob('*')):
            if p.is_file(): result[p.relative_to(sdk).as_posix()] = sha(p)
    for relative in ('bin/cserver', 'bin/vrunact.sh', 'bin/vruntask.sh',
                     'lib/libasp.so', 'lib/libframe.a', 'lib/libutility.a'):
        result[relative] = sha(sdk / relative)
    return result


def build(source, dest, sdk):
    dest.mkdir(parents=True, exist_ok=False)
    # Local byte-identical source copies avoid WSL mount timing during builds.
    local = dest / 'source'
    local.mkdir()
    for name in product(source): shutil.copy2(str(source / name), str(local / name))
    assert product(local) == product(source)
    command = ['g++', '-std=c++11', '-O2', '-g', '-Wall', '-Wextra', '-pthread',
               '-I' + str(sdk / 'include'), '-I' + str(sdk / 'src'), '-I' + str(local)]
    command += [str(p) for p in sorted(local.glob('*.cpp'))]
    command += ['-L' + str(sdk / 'lib'), '-lframe', '-lutility', '-lboost_thread',
                '-lboost_system', '-lboost_chrono', '-lboost_date_time', '-lboost_regex',
                '-lpthread', '-ldl', '-o', str(dest / 'example')]
    with (dest / 'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    save(dest / 'build.json', dict(command=command, source=product(source), binary_sha256=sha(dest / 'example')))


def extract(run, result, seed):
    server = (run / 'server.log').read_text(errors='replace') if (run / 'server.log').exists() else ''
    client = (run / 'client.log').read_text(errors='replace') if (run / 'client.log').exists() else ''
    actions = re.findall(r'^\s*\[([A-Za-z_]+(?:\s+[^|]*?)?)\|', server, re.M)
    result['action_sequence'] = actions
    result['action_cost'] = sum(4 if a.split()[0].lower() == 'move' else
                                1 if a.split()[0].lower() == 'sense' else 2 for a in actions)
    g, c = result.get('final_goals'), result.get('credited_constraints')
    result['base'] = 40 * g + (20 * c if g else 0) - result['action_cost'] if (
        g is not None and c is not None and result.get('official_score') is not None) else None
    result['seed_confirmed'] = '[RDFW_TEST_SEED] ' + str(seed) in server
    result['failed_actions'] = len(re.findall(r'^\s*\[[^\n]*\|[^\n]*\bfalse\b', server, re.M))
    result['lifecycle_cancelled'] = '[Lifecycle] planner stopped' in client
    result['version_log'] = next((line for line in client.splitlines() if '[PlannerVersion]' in line), None)
    result['output'] = str(run)
    return result


def rows_at(path):
    return [json.loads(line) for line in path.read_text(encoding='utf8').splitlines()] if path.exists() else []


def summarize(out):
    rows = rows_at(out / 'results.jsonl')
    summary = {}
    for label, selected in [('normal', [r for r in rows if r['kind'] != 'invalid']),
                            ('invalid', [r for r in rows if r['kind'] == 'invalid'])] + [
                            ('stage' + str(stage), [r for r in rows if r['kind'] != 'invalid' and r['stage'] == stage])
                            for stage in (1, 2)]:
        group = dict(pairs=len(selected), arms={})
        for arm in ARMS:
            vv = [r[arm] for r in selected]
            group['arms'][arm] = dict(
                sums={k: sum(v[k] for v in vv if v.get(k) is not None) for k in FIELDS},
                missing={k: sum(v.get(k) is None for v in vv) for k in FIELDS},
                failed=sum(v.get('status') != 'ok' for v in vv),
                sdk_deadlines=sum(bool(v.get('platform_timed_out')) for v in vv),
                external_timeouts=sum(bool(v.get('external_timeout')) for v in vv),
                failed_actions=sum(v.get('failed_actions', 0) for v in vv),
                seed_unconfirmed=sum(not v['seed_confirmed'] for v in vv))
        group['changes'] = {k: dict(
            comparable=sum(r['baseline'].get(k) is not None and r['current'].get(k) is not None for r in selected),
            delta=sum(r['current'][k] - r['baseline'][k] for r in selected
                      if r['baseline'].get(k) is not None and r['current'].get(k) is not None),
            increased=sum(r['current'][k] > r['baseline'][k] for r in selected
                          if r['baseline'].get(k) is not None and r['current'].get(k) is not None),
            decreased=sum(r['current'][k] < r['baseline'][k] for r in selected
                          if r['baseline'].get(k) is not None and r['current'].get(k) is not None)) for k in FIELDS}
        group['action_differences'] = sum(r['baseline']['action_sequence'] != r['current']['action_sequence'] for r in selected)
        summary[label] = group
    save(out / 'SUMMARY.json', summary)
    regressions = [r for r in rows if r['kind'] != 'invalid' and any(
        r['baseline'].get(k) is not None and r['current'].get(k) is not None and r['current'][k] < r['baseline'][k]
        for k in ('final_goals', 'base', 'official_score'))]
    save(out / 'REGRESSIONS.json', regressions)
    save(out / 'BEHAVIOR_DIFFERENCES.json', [r for r in rows if r['kind'] != 'invalid' and any(
        r['baseline'].get(k) != r['current'].get(k) for k in ('final_goals', 'credited_constraints', 'action_cost', 'base', 'action_sequence'))])
    columns = ['id', 'category', 'kind', 'stage', 'mode', 'round', 'seed'] + [a + '_' + k for a in ARMS for k in FIELDS]
    with (out / 'PAIRS.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns); writer.writeheader()
        for row in rows:
            item = {k: row[k] for k in columns[:7]}
            item.update({a + '_' + k: row[a].get(k) for a in ARMS for k in FIELDS})
            writer.writerow(item)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--sdk-original', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=20260928)
    parser.add_argument('--rounds', type=int, default=1)
    parser.add_argument('--ids', nargs='*')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve(); sdk = args.sdk.resolve()
    catalogue = json.loads((BANK / 'catalogue.json').read_text(encoding='utf8'))['cases']
    assert len(catalogue) == 200 and sum(c['kind'] == 'invalid' for c in catalogue) == 20
    cases = [dict(c, stage=c.get('stage', 1)) for c in catalogue if not args.ids or c['id'] in args.ids]
    assert cases
    for c in cases: assert sha(BANK / c['path']) == c['sha256'], c['id']
    with socket.socket() as port: port.bind(('127.0.0.1', 7932))
    audit = dict(products={a: product(s) for a, s in [('baseline', BASELINE), ('current', SOURCE)]},
                 cases=cases, seed=args.seed, rounds=args.rounds, deadline_ms=5000,
                 sdk=sdk_files(sdk), sdk_original=sdk_files(args.sdk_original),
                 runner_sha256=sha(__file__), harness_sha256=sha(ROOT / 'HistoryVersion/src1.1.2 (x)/tools/baseline.py'),
                 compiler=subprocess.check_output(['g++', '--version']).decode(),
                 policy='default/default; serial AB/BA; IT/NT; shared seed; invalid separate; preserve all failures; LF runtime words only')
    source_keys = [k for k in audit['sdk'] if k.startswith(('src/', 'include/', 'res/'))]
    assert all(audit['sdk'][k] == audit['sdk_original'].get(k) for k in source_keys), 'SDK source/model mismatch'
    if args.resume:
        assert json.loads((out / 'input-audit.json').read_text()) == audit
    else:
        out.mkdir(parents=True, exist_ok=False)
        save(out / 'input-audit.json', audit)
        for arm, source in [('baseline', BASELINE), ('current', SOURCE)]:
            print('BUILD', arm, flush=True); build(source, out / ('build-' + arm), sdk)
        with (out / 'seed-build.log').open('w') as log:
            subprocess.run(['g++', '-shared', '-fPIC', str(SOURCE / 'tests/seed_rng.cpp'), '-ldl', '-o', str(out / 'seed.so')],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        assets = out / 'assets'; assets.mkdir()
        assert (BASELINE / 'words.txt').read_bytes() == (SOURCE / 'words.txt').read_bytes()
        (assets / 'words.txt').write_bytes((BASELINE / 'words.txt').read_bytes().replace(b'\r\n', b'\n'))
        save(out / 'build-audit.json', dict(binaries={a: sha(out / ('build-' + a) / 'example') for a in ARMS},
                                          seed_sha256=sha(out / 'seed.so'), runtime_words_sha256=sha(assets / 'words.txt')))
    build_audit = json.loads((out / 'build-audit.json').read_text())
    assert all(sha(out / ('build-' + a) / 'example') == build_audit['binaries'][a] for a in ARMS)
    os.environ.update(LD_PRELOAD=str(out / 'seed.so'), RDFW_TEST_SEED=str(args.seed), RDFW_STAGE_TIMING='0')
    os.environ.pop('RDFW_TASK_GROUP_MODE', None)
    runner = load_module('official_baseline', ROOT / 'HistoryVersion/src1.1.2 (x)/tools/baseline.py')
    journal = out / 'results.jsonl'; existing = rows_at(journal)
    done = {(r['id'], r['mode'], r['round']) for r in existing}
    assert len(done) == len(existing), 'duplicate journal pair'
    total = len(cases) * 2 * args.rounds; started = time.monotonic()
    for round_id in range(1, args.rounds + 1):
        for index, case in enumerate(cases):
            for mi, mode in enumerate(('it', 'nt')):
                key = (case['id'], mode, round_id)
                if key in done: continue
                order = ARMS if (index + mi + round_id) % 2 else tuple(reversed(ARMS))
                row = dict(id=case['id'], category=case['category'], kind=case['kind'], stage=case['stage'],
                           mode=mode, round=round_id, seed=args.seed, order=list(order), sha256=case['sha256'])
                for arm in order:
                    run = out / 'runs' / ('r%d-%s-%s-%s' % (round_id, case['id'], mode, arm))
                    assert not run.exists(), 'unrecorded run preserved; reconcile manually: ' + str(run)
                    try:
                        value = runner.run_case(sdk, out / 'assets', out / ('build-' + arm) / 'example',
                                                BANK / case['path'], case['stage'], mode, run, 5000, None)
                    except Exception as error:
                        value = dict(status='harness_or_platform_rejected', error=repr(error), official_score=None,
                                     raw_score=None, final_goals=None, credited_constraints=None,
                                     platform_seconds=None, platform_timed_out=False, external_timeout=False)
                    row[arm] = extract(run, value, args.seed)
                with journal.open('a', encoding='utf8') as stream:
                    stream.write(json.dumps(row, ensure_ascii=False) + '\n'); stream.flush(); os.fsync(stream.fileno())
                done.add(key)
                save(out / 'progress.json', dict(completed_pairs=len(done), total_pairs=total, sdk_runs=2 * len(done),
                                                last=key, elapsed_seconds=time.monotonic() - started))
                if len(done) % 10 == 0:
                    summarize(out)
                    print('PAIR', len(done), '/', total, *key, 'G', row['baseline'].get('final_goals'), '->', row['current'].get('final_goals'), flush=True)
    assert {a: product(s) for a, s in [('baseline', BASELINE), ('current', SOURCE)]} == audit['products']
    assert sdk_files(sdk) == audit['sdk'] and sdk_files(args.sdk_original) == audit['sdk_original']
    assert all(sha(BANK / c['path']) == c['sha256'] for c in cases)
    assert sha(__file__) == audit['runner_sha256']
    assert sha(ROOT / 'HistoryVersion/src1.1.2 (x)/tools/baseline.py') == audit['harness_sha256']
    assert all(sha(out / ('build-' + a) / 'example') == build_audit['binaries'][a] for a in ARMS)
    assert sha(out / 'seed.so') == build_audit['seed_sha256']
    assert sha(out / 'assets/words.txt') == build_audit['runtime_words_sha256']
    result = summarize(out)
    assert len(rows_at(journal)) == total
    save(out / 'final-audit.json', dict(pairs=total, sdk_runs=2 * total, sources_unchanged=True,
                                       sdk_unchanged=True, inputs_unchanged=True, binaries_unchanged=True,
                                       normal_seed_unconfirmed=result['normal']['arms']['baseline']['seed_unconfirmed'] +
                                       result['normal']['arms']['current']['seed_unconfirmed']))
    print('COMPLETE', out, flush=True)


if __name__ == '__main__': main()
