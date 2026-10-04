#!/usr/bin/env python3
"""Verify and package a completed deadline comparison without deleting files.

Repeated immutable evaluator resources are verified and stored once. All
per-run generated ASP files, inputs, summaries and logs remain in the archive.
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import shutil
import zipfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    runs, output = args.runs.resolve(), args.output.resolve()
    final = json.loads((runs / 'final-audit.json').read_text())
    rows = json.loads((runs / 'results.json').read_text())
    assert len(rows) == final['completed_pairs']
    assert final['baseline_unchanged'] and final['sdk_unchanged'] and final['cases_unchanged']
    output.mkdir(parents=True, exist_ok=False)
    for path in sorted(runs.iterdir()):
        if path.is_file() and path.name != 'raw-evidence.zip':
            shutil.copy2(str(path), str(output / path.name))
    for arm in ('300ms', '200ms'):
        folder = output / ('build-' + arm)
        folder.mkdir()
        for name in ('build.json', 'build.log'):
            shutil.copy2(str(runs / folder.name / name), str(folder / name))
        assert sha(runs / folder.name / 'example') == final['executable_sha256'][arm]
    with zipfile.ZipFile(str(output / 'binaries.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
        for arm in ('300ms', '200ms'):
            path = runs / ('build-' + arm) / 'example'
            archive.write(str(path), str(path.relative_to(runs)))
        archive.write(str(runs / 'seed_rng.so'), 'seed_rng.so')
    # SDK files are copied into each isolated runtime by the original runner.
    # Deduplication occurs only after every copy has a matching byte hash.
    shared_names = {'iclingo', 'evaluate.lp', 'forcons.lp', 'fortask.lp',
                    'show.lp', 'vrunact.sh', 'vruntask.sh'}
    shared, members = {}, []
    with zipfile.ZipFile(str(output / 'raw-evidence.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((runs / 'runs').rglob('*')):
            if not path.is_file():
                continue
            relative = path.relative_to(runs)
            if path.parent.name == 'runtime' and path.name in shared_names:
                digest = sha(path)
                if path.name not in shared:
                    shared[path.name] = digest
                    archive.write(str(path), 'shared-sdk/' + path.name)
                else:
                    assert shared[path.name] == digest, ('SDK copy changed', path)
                members.append(dict(path=str(relative), shared='shared-sdk/' + path.name,
                                    sha256=digest))
            else:
                archive.write(str(path), str(relative))
        for path in sorted((runs / 'assets').rglob('*')):
            if path.is_file():
                archive.write(str(path), str(path.relative_to(runs)))
        archive.writestr('shared-sdk-map.json', json.dumps(members, indent=2))
    groups = collections.defaultdict(list)
    for row in rows:
        groups[(row['planner_mode'], row['suite'], row['case'], row['mode'])].append(row)
    fields = ['planner_mode', 'suite', 'case', 'mode', 'pairs', 'goals_300', 'goals_200',
              'goals_delta', 'score_300', 'score_200', 'score_delta', 'base_delta',
              'goals_improved', 'goals_worsened', 'timeouts_300', 'timeouts_200', 'action_changed']
    impacts = []
    variations = []
    with (output / 'case-summary.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for key, group in sorted(groups.items()):
            for arm in ('300ms', '200ms'):
                goal_values = sorted(set(r[arm]['final_goals'] for r in group
                                         if r[arm]['final_goals'] is not None))
                signatures = {tuple(r[arm]['action_sequence']) for r in group}
                base_values = sorted(set(r[arm]['base'] for r in group
                                         if r[arm]['base'] is not None))
                if len(signatures) > 1 or len(goal_values) > 1 or len(base_values) > 1:
                    variations.append(dict(planner_mode=key[0], suite=key[1], case=key[2],
                        mode=key[3], arm=arm, goal_values=goal_values, base_values=base_values,
                        action_variants=len(signatures), samples=[dict(round=r['round'],
                            goals=r[arm]['final_goals'], base=r[arm]['base'],
                            score=r[arm]['official_score'], seconds=r[arm]['platform_seconds'],
                            action_count=r[arm]['action_count']) for r in group]))
            value = dict(zip(fields[:4], key))
            value['pairs'] = len(group)
            for prefix, field in [('goals', 'final_goals'), ('score', 'official_score')]:
                for short, arm in [('300', '300ms'), ('200', '200ms')]:
                    value[prefix + '_' + short] = sum(row[arm][field] or 0 for row in group)
                value[prefix + '_delta'] = value[prefix + '_200'] - value[prefix + '_300']
            value['base_delta'] = sum((row['200ms']['base'] or 0) -
                                     (row['300ms']['base'] or 0) for row in group)
            goal_deltas = [(r['200ms']['final_goals'] or 0) - (r['300ms']['final_goals'] or 0) for r in group]
            value['goals_improved'], value['goals_worsened'] = sum(d > 0 for d in goal_deltas), sum(d < 0 for d in goal_deltas)
            for short, arm in [('300', '300ms'), ('200', '200ms')]:
                value['timeouts_' + short] = sum(r[arm]['platform_timed_out'] or r[arm]['external_timeout'] for r in group)
            value['action_changed'] = sum(r['300ms']['action_sequence'] != r['200ms']['action_sequence'] for r in group)
            writer.writerow(value)
            if value['goals_delta'] or value['base_delta'] or value['timeouts_300'] or value['timeouts_200']:
                impacts.append(value)
    lines = ['## 逐题影响与交付归档', '',
             '| Planner | 题目 | 输入 | 重复 | 目标合计差值 | 官方总分差值 | 基础分差值 | 目标提高/下降 | 超时 300→200 |',
             '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for value in impacts:
        lines.append('| {} | {} | {} | {} | {:+d} | {:+d} | {:+d} | {}/{} | {}→{} |'.format(
            value['planner_mode'], Path(value['case']).name, value['mode'], value['pairs'],
            value['goals_delta'], value['score_delta'], value['base_delta'],
            value['goals_improved'], value['goals_worsened'], value['timeouts_300'], value['timeouts_200']))
    score_only = [r for r in rows if r['300ms']['action_sequence'] == r['200ms']['action_sequence']
                  and all(r['300ms'][f] == r['200ms'][f] for f in ('base', 'final_goals', 'credited_constraints'))
                  and r['300ms']['official_score'] != r['200ms']['official_score']]
    lines += ['', '另有 {} 对动作、目标、约束和基础分完全一致而官方总分不同，'
              '归类为时间奖励变化；全部保留在 pairs.csv 中。'.format(len(score_only)), '',
              'case-summary.csv 提供逐题逐模式的三轮汇总。raw-evidence.zip 保留所有运行日志、'
              '输入、summary 和动态 ASP 文件；相同的 SDK 资源按字节哈希核对后仅存一份，'
              'shared-sdk-map.json 记录各运行路径映射。binaries.zip 保存两版独立二进制与种子库。', '',
              '测试工具在第 10 对写 CSV 时因字段切片错误中断；修正后核对输入和二进制哈希续跑。'
              '前 10 对原始结果保留，没有以重跑替换，详见 resume-audit.json。']
    (output / 'binary-repeat-variation.json').write_text(json.dumps(
        variations, ensure_ascii=False, indent=2), encoding='utf-8')
    if variations:
        lines += ['', '### 同二进制重复的行为波动', '',
                  '下列组的三轮运行使用相同二进制、题目和随机种子，仍出现不同动作或基础分。'
                  '这些是现有墙钟搜索/门控波动的实测证据；配对差值全部保留，不能把每次差值都归因于参数。', '',
                  '| Planner | 题目 | 输入 | 预留 | 目标数取值 | 基础分取值 | 动作变体数 |',
                  '|---|---|---|---|---|---|---:|']
        for value in variations:
            lines.append('| {} | {} | {} | {} | {} | {} | {} |'.format(
                value['planner_mode'], Path(value['case']).name, value['mode'], value['arm'],
                value['goal_values'], value['base_values'], value['action_variants']))
        lines += ['', '完整逐轮记录见 binary-repeat-variation.json。']
    report_path = output / 'REPORT.md'
    report_path.write_text(report_path.read_text() + '\n' + '\n'.join(lines) + '\n', encoding='utf-8')
    manifest = {p.relative_to(output).as_posix(): sha(p) for p in sorted(output.rglob('*')) if p.is_file()}
    (output / 'package-sha256.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    with zipfile.ZipFile(str(output / 'raw-evidence.zip')) as archive:
        assert archive.testzip() is None
    with zipfile.ZipFile(str(output / 'binaries.zip')) as archive:
        assert archive.testzip() is None
    print('Packaged', len(rows), 'pairs into', output, flush=True)


if __name__ == '__main__':
    main()
