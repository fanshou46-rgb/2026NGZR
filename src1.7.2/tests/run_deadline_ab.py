#!/usr/bin/env python3
"""Isolated 300/200 ms comparison, Python 3.6+, serial official SDK runs.

Only the planner safety parameter may differ in the product files. Every pair
shares its input, server seed and planner mode. All runs, including failures,
are retained. A new output directory is required; this tool deletes no files.
"""
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
import time
import zipfile

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1]
ROOT = SOURCE.parent
BASELINE = ROOT / 'src1.6.7'
sys.path.insert(0, str(BASELINE / 'tests'))
from compare_legal import build
from run_guarded_compare import load_runner, base_score


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def tree(path):
    return {p.relative_to(path).as_posix(): sha(p) for p in sorted(path.rglob('*'))
            if p.is_file()}


def product_audit():
    left = {p.name: sha(p) for p in BASELINE.iterdir() if p.is_file()}
    right = {p.name: sha(p) for p in SOURCE.iterdir() if p.is_file()}
    assert set(left) == set(right), 'product file set changed'
    changed = [name for name in left if left[name] != right[name]]
    assert changed == ['rdfw.hpp'], changed
    old = (BASELINE / 'rdfw.hpp').read_bytes()
    new = (SOURCE / 'rdfw.hpp').read_bytes()
    assert old.count(b'plan_safety_margin{300}') == 1
    assert new == old.replace(b'plan_safety_margin{300}', b'plan_safety_margin{200}')
    return dict(baseline=left, current=right, changed=changed,
                exact_parameter_only=True)


def cases():
    # Preserve the previously validated release fixtures; add every scoreable
    # original realcompetiton case. Broken originals are explicitly excluded.
    rows = json.loads((BASELINE / 'test-results/validation-20260928/full-release-results.json').read_text())
    items = {}
    for row in rows:
        if row['mode'] == 'it':
            path = Path(row['case'])
            assert path.exists(), path
            items[str(path)] = dict(path=path, stage=row['stage'], suite='release')
    for number in range(1, 37):
        if number in (2, 4, 5):
            continue
        path = ROOT / '题目/realcompetiton_2024' / ('{:02d}.xml'.format(number))
        flags = dict(re.findall(r'(mis|err|ans)="(on|off)"',
                     re.search(r'<env\s+([^>]+)>', path.read_text()).group(1)))
        stage = 1 if all(flags.get(k) == 'off' for k in ('mis', 'err', 'ans')) else 2
        items[str(path)] = dict(path=path, stage=stage, suite='realcompetition')
    result = sorted(items.values(), key=lambda x: (x['suite'], str(x['path'])))
    for i, item in enumerate(result):
        item.update(id='c{:03d}'.format(i + 1), sha256=sha(item['path']))
    return result


def stats(rows):
    result = {}
    for arm in ('300ms', '200ms'):
        values = [row[arm] for row in rows]
        result[arm] = dict(runs=len(values),
            completed_goals=sum(v['final_goals'] or 0 for v in values),
            official_total=sum(v['official_score'] or 0 for v in values),
            raw_total=sum(v['raw_score'] or 0 for v in values),
            base_total=sum(v['base'] or 0 for v in values),
            timeouts=sum(v['platform_timed_out'] or v['external_timeout'] for v in values),
            platform_timeouts=sum(v['platform_timed_out'] for v in values),
            external_timeouts=sum(v['external_timeout'] for v in values),
            failures=sum(v['status'] != 'ok' for v in values),
            unscored=sum(v['official_score'] is None for v in values),
            missing_goal_evaluation=sum(v['final_goals'] is None for v in values))
        result[arm]['timeout_rate'] = result[arm]['timeouts'] / max(1, len(values))
    for field in ('final_goals', 'official_score', 'base'):
        deltas = [(row['200ms'][field] or 0) - (row['300ms'][field] or 0) for row in rows]
        result[field + '_pairs'] = dict(improved=sum(d > 0 for d in deltas),
            equal=sum(d == 0 for d in deltas), worsened=sum(d < 0 for d in deltas),
            total_delta=sum(deltas))
    result['action_changed_pairs'] = sum(row['300ms']['action_sequence'] !=
        row['200ms']['action_sequence'] for row in rows)
    return result


def summarize(out, rows, rounds):
    groups = {'all': stats(rows)}
    for mode in ('off', 'guarded'):
        subset = [r for r in rows if r['planner_mode'] == mode]
        groups[mode] = stats(subset)
        for suite in ('realcompetition', 'release'):
            part = [r for r in subset if r['suite'] == suite]
            if part:
                groups[mode + '/' + suite] = stats(part)
        for round_id in range(1, rounds + 1):
            part = [r for r in subset if r['round'] == round_id]
            if part:
                groups[mode + '/round' + str(round_id)] = stats(part)
    write_json(out / 'summary.json', groups)
    columns = ['id', 'case', 'suite', 'stage', 'mode', 'planner_mode', 'round', 'order',
               'goals_300', 'goals_200', 'goals_delta', 'score_300', 'score_200', 'score_delta',
               'base_300', 'base_200', 'base_delta', 'seconds_300', 'seconds_200',
               'timeout_300', 'timeout_200', 'status_300', 'status_200', 'actions_changed']
    with (out / 'pairs.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            a, b = row['300ms'], row['200ms']
            value = {k: row[k] for k in columns[:8]}
            for label, key in [('goals', 'final_goals'), ('score', 'official_score'), ('base', 'base')]:
                value[label + '_300'], value[label + '_200'] = a[key], b[key]
                value[label + '_delta'] = (b[key] or 0) - (a[key] or 0)
            value.update(seconds_300=a['platform_seconds'], seconds_200=b['platform_seconds'],
                timeout_300=a['platform_timed_out'] or a['external_timeout'],
                timeout_200=b['platform_timed_out'] or b['external_timeout'],
                status_300=a['status'], status_200=b['status'],
                actions_changed=a['action_sequence'] != b['action_sequence'])
            writer.writerow(value)
    return groups


def report(out, groups, rows, rounds):
    lines = ['# src1.6.7-200ms deadline 配对测试', '',
        '产品源码仅 rdfw.hpp 的 plan_safety_margin 从 300 改为 200 ms；'
        '5000 ms 总期限、Multi-GOTO 100 ms 尾部预留、搜索 CPU 预算、评分与排序保持原值。', '',
        '环境：WSL2 Ubuntu-18.04 / g++ 7.5.0 / 官方 env-release-2026 SDK；'
        '同题同种子 20260924、IT/NT、串行运行、按配对交替 AB/BA，关闭 StageTiming。', '',
        '主实验使用默认 off 模式：33 道可原样评分的历史比赛题和 37 道既有 release fixtures，'
        '{} 轮重复。另对 7 道 decision/combinatorial fixtures 运行 guarded 模式重复。'.format(rounds), '',
        '02 原题 XML 无法建立；04/05 原题无法生成有效官方评分，三题按既有验证记录排除，'
        '不修复输入、不计入分母。官方总分使用平台分数封顶 1000 后求和，raw_score 另存。'
        '全部失败和超时仍计入运行次数；缺失分数/目标按 0 汇总并单列缺失数，'
        '有评分的超时保留官方实际分数和官方终态目标数。', '',
        '| 范围 | 每版运行数 | 完成目标 300→200 | 官方总分 300→200 | 超时 300→200 | 超时率 300→200 |',
        '|---|---:|---:|---:|---:|---:|']
    for key, value in groups.items():
        a, b = value['300ms'], value['200ms']
        lines.append('| {} | {} | {}→{} | {}→{} | {}→{} | {:.2%}→{:.2%} |'.format(
            key, a['runs'], a['completed_goals'], b['completed_goals'],
            a['official_total'], b['official_total'], a['timeouts'], b['timeouts'],
            a['timeout_rate'], b['timeout_rate']))
    lines += ['', '## 配对变化', '', '| 范围 | 目标提高/持平/下降 | 总分提高/持平/下降 | 动作变化配对 |',
        '|---|---:|---:|---:|']
    for key in ('off', 'guarded'):
        value = groups[key]
        g, s = value['final_goals_pairs'], value['official_score_pairs']
        lines.append('| {} | {}/{}/{} | {}/{}/{} | {} |'.format(key,
            g['improved'], g['equal'], g['worsened'], s['improved'], s['equal'],
            s['worsened'], value['action_changed_pairs']))
    main = groups['off']
    a, b = main['300ms'], main['200ms']
    lines += ['', '主实验 {} 对：目标合计差值 {:+d}，官方总分差值 {:+d}，超时数差值 {:+d}。'.format(
        a['runs'], b['completed_goals'] - a['completed_goals'],
        b['official_total'] - a['official_total'], b['timeouts'] - a['timeouts']), '',
        '每版失败/缺失评分/缺失目标：300 ms = {}/{}/{}，200 ms = {}/{}/{}。'.format(
            a['failures'], a['unscored'], a['missing_goal_evaluation'],
            b['failures'], b['unscored'], b['missing_goal_evaluation']), '',
        '这是指定题集、固定随机种子和当前平台的重复结果；同种子重复用于观察墙钟波动，'
        '不代表独立随机场景。采用新参数应同时评估各轮收益、目标下降配对和超时变化。', '',
        '## 原始证据与复跑', '',
        '- pairs.csv：逐题逐轮配对结果；results.json：全部运行状态、目标、分数、动作和调用命令。',
        '- differences.json：所有目标/基础分/动作差异，以及首个动作分叉和末尾 deadline 日志。',
        '- input-audit.json / final-audit.json：产品唯一参数差异，基线、SDK、题目、二进制哈希及运行前后核对。',
        '- raw-evidence.zip：逐次 server/client 日志、summary、ASP 终态与运行输入。',
        '- build-300ms / build-200ms：相同编译参数的独立二进制和构建日志。',
        '- unit-ctest.log：原有本地测试；200 ms 精确边界测试更新测试期望，不修改 DeadlineManager API。', '',
        '```sh', 'python3 "{}/tests/run_deadline_ab.py" --output /tmp/rdfw-deadline-ab-new --rounds {}'.format(SOURCE, rounds), '```', '',
        'tests 与 docs 中继承的历史脚本/报告保留原文；本实验以本报告和 run_deadline_ab.py 为入口。']
    (out / 'REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--rounds', default=3, type=int)
    parser.add_argument('--sdk', default=Path('/home/yifan/env-release-2026'), type=Path)
    parser.add_argument('--resume', action='store_true',
                        help='Resume completed pairs after verifying all inputs and binaries')
    args = parser.parse_args()
    assert args.rounds > 0
    out = args.output.resolve()
    if not args.resume:
        out.mkdir(parents=True, exist_ok=False)
    audit = product_audit()
    baseline_tree, sdk_tree = tree(BASELINE), tree(args.sdk)
    selected = cases()
    snapshot = dict(product=audit, baseline_tree=baseline_tree,
        sdk_tree=sdk_tree, source_tree=tree(SOURCE),
        cases=[dict(item, path=str(item['path'])) for item in selected],
        platform=subprocess.check_output(['uname', '-a']).decode(),
        compiler=subprocess.check_output(['g++', '--version']).decode(),
        os_release=Path('/etc/os-release').read_text(),
        policy=dict(rounds=args.rounds, seed=20260924, deadline_ms=5000,
                    order='alternating AB/BA per pair', stage_timing=False))
    if args.resume:
        original = json.loads((out / 'input-audit.json').read_text())
        for field in ('product', 'baseline_tree', 'sdk_tree', 'cases', 'policy'):
            assert snapshot[field] == original[field], ('resume input mismatch', field)
        write_json(out / 'resume-audit.json', dict(inputs_unchanged=True,
            reason='CSV metadata slice fixed after first 10 pairs; original pairs retained',
            current_harness_sha256=sha(Path(__file__))))
    else:
        write_json(out / 'input-audit.json', snapshot)
    commands = json.loads((out / 'commands.json').read_text()) if args.resume else []
    def command(name, cmd, cwd=None):
        started = time.time()
        with (out / (name + '.log')).open('w') as log:
            result = subprocess.run([str(x) for x in cmd], cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        commands.append(dict(name=name, command=[str(x) for x in cmd],
                             exit_code=result.returncode, seconds=time.time() - started))
        write_json(out / 'commands.json', commands)
        if result.returncode:
            raise RuntimeError('{} failed; inspect its log'.format(name))
    print('Product audit: only plan_safety_margin 300 -> 200 ms', flush=True)
    executables = {}
    for arm, version in [('300ms', 'src1.6.7'), ('200ms', SOURCE.name)]:
        if args.resume:
            executables[arm] = out / ('build-' + arm) / 'example'
            metadata = json.loads((executables[arm].parent / 'build.json').read_text())
            assert sha(executables[arm]) == metadata['executable_sha256']
        else:
            print('Building', arm, flush=True)
            executables[arm] = build(version, args.sdk, out / ('build-' + arm))
    unit = out / 'unit'
    if not args.resume:
        command('unit-config', ['cmake', '-H' + str(SOURCE / 'tests'), '-B' + str(unit),
                          '-DCMAKE_BUILD_TYPE=Release', '-DOFFICIAL_SDK=' + str(args.sdk)])
        command('unit-build', ['cmake', '--build', unit, '--', '-j3'])
        command('unit-ctest', ['ctest', '--output-on-failure'], cwd=str(unit))
        command('unit-deadline', [unit / 'deadline_sensitivity_tests', unit / 'words.txt'])
    seed = out / 'seed_rng.so'
    if not args.resume:
        command('seed-build', ['g++', '-shared', '-fPIC', BASELINE / 'tests/seed_rng.cpp', '-ldl', '-o', seed])
    assert ' ' not in str(seed), 'LD_PRELOAD path must not contain spaces'
    assets = out / 'assets'
    if not args.resume:
        assets.mkdir()
        (assets / 'words.txt').write_bytes((BASELINE / 'words.txt').read_bytes().replace(b'\r\n', b'\n'))
    assert (assets / 'words.txt').read_bytes() == (BASELINE / 'words.txt').read_bytes().replace(b'\r\n', b'\n')
    os.environ.update(LD_PRELOAD=str(seed), RDFW_TEST_SEED='20260924', RDFW_STAGE_TIMING='0')
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 7932))
    run_case = load_runner(ROOT / 'HistoryVersion/src1.1.2 (x)/tools/baseline.py')
    rows = json.loads((out / 'results.json').read_text()) if args.resume else []
    differences = json.loads((out / 'differences.json').read_text()) if args.resume else []
    completed = {(r['round'], r['planner_mode'], r['id'], r['mode']) for r in rows}
    assert len(completed) == len(rows)
    guarded_cases = [item for item in selected if 'fixtures' in item['path'].parts and
                     item['path'].parent.name in ('decision', 'combinatorial_gain')]
    assert len(selected) == 70 and len(guarded_cases) == 7
    expected = (len(selected) + len(guarded_cases)) * 2 * args.rounds
    print('Official protocol: {} cases, {} guarded controls, {} pairs / {} runs'.format(
        len(selected), len(guarded_cases), expected, expected * 2), flush=True)
    for round_id in range(1, args.rounds + 1):
        for planner_mode, selection in [('off', selected), ('guarded', guarded_cases)]:
            os.environ['RDFW_TASK_GROUP_MODE'] = planner_mode
            for item in selection:
                assert sha(item['path']) == item['sha256']
                for mode in ('it', 'nt'):
                    if (round_id, planner_mode, item['id'], mode) in completed:
                        continue
                    order = ['300ms', '200ms'] if len(rows) % 2 == 0 else ['200ms', '300ms']
                    # Flip the initial arm on alternating rounds as well.
                    if round_id % 2 == 0:
                        order.reverse()
                    row = dict(id=item['id'], case=str(item['path']), case_sha256=item['sha256'],
                        suite=item['suite'], stage=item['stage'], mode=mode,
                        planner_mode=planner_mode, round=round_id, order='/'.join(order))
                    for arm in order:
                        run_dir = out / 'runs' / ('r{}-{}-{}-{}-{}'.format(
                            round_id, planner_mode, item['id'], mode, arm))
                        result = run_case(args.sdk, assets, executables[arm], item['path'],
                                          item['stage'], mode, run_dir, 5000, None)
                        result['output'] = str(run_dir)
                        result['base'] = base_score(result)
                        server_text = (run_dir / 'server.log').read_text(errors='replace')
                        client_text = (run_dir / 'client.log').read_text(errors='replace')
                        result['seed_confirmed'] = '[RDFW_TEST_SEED] 20260924' in server_text
                        assert result['seed_confirmed'], run_dir
                        result['action_sequence'] = re.findall(r'^\s*\[([A-Za-z_]+(?:\s+[^|]*?)?)\|', server_text, re.M)
                        result['deadline_tail'] = [re.sub(r'\x1b\[[0-9;]*m', '', line) for line in
                            client_text.splitlines() if any(marker in line for marker in
                            ('[StopGate]', '[Deadline]', '[3A][final]', '[3B][Remaining]'))][-18:]
                        row[arm] = result
                    a, b = row['300ms'], row['200ms']
                    if any(a[field] != b[field] for field in ('final_goals', 'base', 'action_sequence')):
                        i = next((i for i, (x, y) in enumerate(zip(a['action_sequence'], b['action_sequence'])) if x != y),
                                 min(len(a['action_sequence']), len(b['action_sequence'])))
                        differences.append(dict(row, first_action_divergence=i,
                            action_300=a['action_sequence'][i:i+3], action_200=b['action_sequence'][i:i+3]))
                    rows.append(row)
                    write_json(out / 'results.json', rows)
                    write_json(out / 'differences.json', differences)
                    if len(rows) % 10 == 0 or len(rows) == expected:
                        summarize(out, rows, args.rounds)
                    print('{}/{} r{} {} {} {} goals {}->{} score {}->{} timeout {}->{}'.format(
                        len(rows), expected, round_id, planner_mode, item['path'].name, mode,
                        a['final_goals'], b['final_goals'], a['official_score'], b['official_score'],
                        a['platform_timed_out'], b['platform_timed_out']), flush=True)
    assert len(rows) == expected
    assert tree(BASELINE) == baseline_tree, 'baseline changed during experiment'
    assert tree(args.sdk) == sdk_tree, 'SDK changed during experiment'
    assert product_audit() == audit
    assert all(sha(item['path']) == item['sha256'] for item in selected)
    write_json(out / 'final-audit.json', dict(baseline_unchanged=True, sdk_unchanged=True,
        cases_unchanged=True, product=audit, executable_sha256={k: sha(v) for k, v in executables.items()},
        seed_sha256=sha(seed), harness_sha256=sha(Path(__file__)),
        completed_pairs=len(rows), completed_runs=len(rows) * 2))
    groups = summarize(out, rows, args.rounds)
    report(out, groups, rows, args.rounds)
    with zipfile.ZipFile(str(out / 'raw-evidence.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder in ('runs', 'assets'):
            for path in sorted((out / folder).rglob('*')):
                if path.is_file():
                    archive.write(str(path), str(path.relative_to(out)))
    print('COMPLETE', out, json.dumps(groups['off'], ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
