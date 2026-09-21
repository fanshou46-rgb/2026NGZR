#!/usr/bin/env python3
"""Analyze score, terminal state, timing and action-sequence differences."""
from collections import Counter
import csv
import json
from pathlib import Path
import re

ROOT = Path('/mnt/d/FILES for Yvaine/WUT/Match/robocup/2026NGZR')
BASE = ROOT / 'test-results/realcompetition-src13-vs-src131-20260921'
VERSIONS = ('src1.3', 'src1.3.1')
REPETITIONS = (1, 2)


def folder(version, repetition, number):
    stage = 1 if number == 2 else 2
    return BASE / ('runs-{}-r{}'.format(version, repetition)) / (
        '{:02d}-s{}-it'.format(number, stage))


def load(version, repetition, number):
    path = folder(version, repetition, number)
    summary = path / 'summary.json'
    error = path / 'runner-error.json'
    row = json.loads((summary if summary.exists() else error).read_text(encoding='utf-8'))
    server = (path / 'server.log').read_text(encoding='utf-8', errors='replace')
    client = (path / 'client.log').read_text(encoding='utf-8', errors='replace')
    actions = []
    for match in re.finditer(r'^\s*\[([^|\]]+)\|([^\]]*)\]', server, re.M):
        actions.append('{}|{}'.format(
            ' '.join(match.group(1).split()), ' '.join(match.group(2).split())))
    row['action_sequence'] = actions
    row['action_commands'] = [action.split('|', 1)[0] for action in actions]
    row['folder'] = str(path)
    row['valid'] = not row.get('platform_error') and row.get('official_score') is not None

    answer = path / 'runtime/vanswer.txt'
    answer_text = answer.read_text(encoding='utf-8', errors='replace') if answer.exists() else ''
    values = [(int(item), int(score))
              for item, score in re.findall(r'value\((\d+),(-?\d+)\)', answer_text)]
    value_points = sum(score for _, score in values)
    if row['valid']:
        # An empty official answer set means that no goal/constraint earned points.
        row['final_goals'] = sum(score == 40 for _, score in set(values))
        row['credited_constraints'] = sum(score == 20 for _, score in set(values))
    evaluate = path / 'runtime/evaluelog.txt'
    evaluate_text = evaluate.read_text(encoding='utf-8', errors='replace') if evaluate.exists() else ''
    action_scores = re.findall(r'Current socre is:\s*(-?\d+)', evaluate_text)
    row['platform_action_cost'] = -int(action_scores[-1]) if action_scores else 0
    row['platform_deterministic_base'] = (
        value_points - row['platform_action_cost'] if row['valid'] else None)
    row['platform_time_bonus'] = (
        row['raw_score'] - row['platform_deterministic_base'] if row['valid'] else None)

    finals = re.findall(
        r'\[3A\]\[final\] goals=(\d+)/(\d+) \(unknown=(\d+)\), '
        r'constraints=(\d+)/(\d+) \(unknown=(\d+)\), base_score=(-?\d+), '
        r'action_cost=(\d+), elapsed=(\d+)ms,\s*remaining=(\d+)ms', client)
    if finals:
        values = [int(value) for value in finals[-1]]
        keys = ('goals', 'total_goals', 'unknown_goals', 'constraints',
                'total_constraints', 'unknown_constraints', 'base_score',
                'action_cost_snapshot', 'elapsed_ms', 'remaining_ms')
        row['snapshot'] = dict(zip(keys, values))
        row['snapshot_matches_platform_base'] = (
            row['snapshot']['base_score'] == row['platform_deterministic_base'])
        row['snapshot_action_cost_matches'] = (
            row['snapshot']['action_cost_snapshot'] == row['platform_action_cost'])
        row['snapshot_goals_match'] = row['snapshot']['goals'] == row.get('final_goals')
        row['snapshot_constraints_match'] = (
            row['snapshot']['constraints'] == row.get('credited_constraints'))
    else:
        row['snapshot'] = None

    stops = re.findall(r'\[3A\]\[StopGate\]\s*(.*)', client)
    row['stop_gate_messages'] = stops
    if any('all goals are SATISFIED' in message for message in stops):
        row['stop_category'] = 'all-goals'
    elif any(('estimate=' in message or 'deadline' in message) for message in stops):
        row['stop_category'] = 'deadline-gate'
    elif any('no executable candidate' in message for message in stops):
        row['stop_category'] = 'no-candidate'
    elif version == 'src1.3.1' and row['valid']:
        row['stop_category'] = 'normal-flow'
    else:
        row['stop_category'] = None
    return row


def average(values):
    values = [value for value in values if value is not None]
    return sum(values) / len(values) if values else None


def fmt(value, digits=1):
    if value is None:
        return '—'
    if isinstance(value, float) and not value.is_integer():
        return ('{:.%df}' % digits).format(value)
    return str(int(value))


records = {
    number: {
        version: [load(version, repetition, number) for repetition in REPETITIONS]
        for version in VERSIONS
    } for number in range(1, 37)
}

comparable = [number for number in range(1, 37) if all(
    run['valid'] for version in VERSIONS for run in records[number][version])]


def version_summary(version):
    runs = [records[number][version][repetition - 1]
            for number in comparable for repetition in REPETITIONS]
    round_totals = {}
    for repetition in REPETITIONS:
        selected = [records[number][version][repetition - 1] for number in comparable]
        round_totals[str(repetition)] = {
            'official_score': sum(row['official_score'] for row in selected),
            'raw_score': sum(row['raw_score'] for row in selected),
            'final_goals': sum(row['final_goals'] for row in selected),
            'credited_constraints': sum(row['credited_constraints'] for row in selected),
            'action_count': sum(row['action_count'] for row in selected),
        }
    return {
        'valid_runs': sum(records[number][version][repetition - 1]['valid']
                          for number in range(1, 37) for repetition in REPETITIONS),
        'ok_runs': sum(records[number][version][repetition - 1].get('status') == 'ok'
                       for number in range(1, 37) for repetition in REPETITIONS),
        'platform_timeout_runs': sum(row.get('platform_timed_out', False) for row in runs),
        'average_platform_seconds': average([row.get('platform_seconds') for row in runs]),
        'round_totals': round_totals,
        'mean_official_total': average([item['official_score'] for item in round_totals.values()]),
        'mean_raw_total': average([item['raw_score'] for item in round_totals.values()]),
        'mean_final_goals': average([item['final_goals'] for item in round_totals.values()]),
        'mean_constraints': average([item['credited_constraints'] for item in round_totals.values()]),
        'mean_action_count': average([item['action_count'] for item in round_totals.values()]),
    }


cases = []
for number in range(1, 37):
    old = records[number]['src1.3']
    new = records[number]['src1.3.1']
    old_scores = [run.get('official_score') if run['valid'] else None for run in old]
    new_scores = [run.get('official_score') if run['valid'] else None for run in new]
    old_average = average(old_scores)
    new_average = average(new_scores)
    same_sequence = [old[index]['action_sequence'] == new[index]['action_sequence']
                     for index in range(2)]
    same_commands = [old[index]['action_commands'] == new[index]['action_commands']
                     for index in range(2)]
    common_prefix = []
    command_common_prefix = []
    for index in range(2):
        count = 0
        for left, right in zip(old[index]['action_sequence'], new[index]['action_sequence']):
            if left != right:
                break
            count += 1
        common_prefix.append(count)
        count = 0
        for left, right in zip(old[index]['action_commands'], new[index]['action_commands']):
            if left != right:
                break
            count += 1
        command_common_prefix.append(count)
    cases.append({
        'case': '{:02d}'.format(number),
        'comparable': number in comparable,
        'score_1_3': old_scores,
        'score_1_3_1': new_scores,
        'average_1_3': old_average,
        'average_1_3_1': new_average,
        'delta': (new_average - old_average
                  if old_average is not None and new_average is not None else None),
        'goals_1_3': [run.get('final_goals') for run in old],
        'goals_1_3_1': [run.get('final_goals') for run in new],
        'constraints_1_3': [run.get('credited_constraints') for run in old],
        'constraints_1_3_1': [run.get('credited_constraints') for run in new],
        'actions_1_3': [run.get('action_count') for run in old],
        'actions_1_3_1': [run.get('action_count') for run in new],
        'seconds_1_3': [run.get('platform_seconds') for run in old],
        'seconds_1_3_1': [run.get('platform_seconds') for run in new],
        'ok_1_3': [run.get('status') == 'ok' for run in old],
        'ok_1_3_1': [run.get('status') == 'ok' for run in new],
        'same_sequence': same_sequence,
        'same_commands': same_commands,
        'common_prefix': common_prefix,
        'command_common_prefix': command_common_prefix,
        'stop_category_1_3_1': [run.get('stop_category') for run in new],
    })

summary = {
    'cases': 36,
    'comparable_cases': len(comparable),
    'excluded_cases': ['{:02d}'.format(number) for number in range(1, 37)
                       if number not in comparable],
    'repetitions': 2,
    'runs': 144,
    'src1.3': version_summary('src1.3'),
    'src1.3.1': version_summary('src1.3.1'),
}
for metric in ('mean_official_total', 'mean_raw_total', 'mean_final_goals',
               'mean_constraints', 'mean_action_count'):
    summary[metric + '_delta'] = summary['src1.3.1'][metric] - summary['src1.3'][metric]
summary['improved_cases'] = sum(row['delta'] > 0 for row in cases if row['comparable'])
summary['regressed_cases'] = sum(row['delta'] < 0 for row in cases if row['comparable'])
summary['unchanged_cases'] = sum(row['delta'] == 0 for row in cases if row['comparable'])
summary['paired_identical_action_sequences'] = sum(
    value for row in cases if row['comparable'] for value in row['same_sequence'])
summary['paired_identical_command_sequences'] = sum(
    value for row in cases if row['comparable'] for value in row['same_commands'])
paired_runs = [(records[number]['src1.3'][repetition - 1],
                records[number]['src1.3.1'][repetition - 1])
               for number in comparable for repetition in REPETITIONS]
summary['paired_new_command_is_strict_prefix'] = sum(
    len(new['action_commands']) < len(old['action_commands']) and
    old['action_commands'][:len(new['action_commands'])] == new['action_commands']
    for old, new in paired_runs)
summary['paired_new_has_fewer_actions'] = sum(
    len(new['action_commands']) < len(old['action_commands']) for old, new in paired_runs)
summary['paired_new_has_more_actions'] = sum(
    len(new['action_commands']) > len(old['action_commands']) for old, new in paired_runs)
summary['paired_same_action_count'] = sum(
    len(new['action_commands']) == len(old['action_commands']) for old, new in paired_runs)
new_runs = [records[number]['src1.3.1'][repetition - 1]
            for number in comparable for repetition in REPETITIONS]
summary['src1.3.1_stop_categories'] = dict(Counter(
    run['stop_category'] for run in new_runs))
snapshot_runs = [run for run in new_runs if run.get('snapshot')]
summary['snapshot_checks'] = {
    'runs_with_final_snapshot': len(snapshot_runs),
    'base_matches_platform': sum(run.get('snapshot_matches_platform_base', False)
                                 for run in snapshot_runs),
    'action_cost_matches_platform': sum(run.get('snapshot_action_cost_matches', False)
                                        for run in snapshot_runs),
    'goals_match_official': sum(run.get('snapshot_goals_match', False)
                                for run in snapshot_runs),
    'constraints_match_official': sum(run.get('snapshot_constraints_match', False)
                                      for run in snapshot_runs),
}
summary['snapshot_checks']['base_conservative_under'] = sum(
    run['snapshot']['base_score'] < run['platform_deterministic_base']
    for run in snapshot_runs)
summary['snapshot_checks']['base_optimistic_over'] = sum(
    run['snapshot']['base_score'] > run['platform_deterministic_base']
    for run in snapshot_runs)
summary['snapshot_checks']['goals_conservative_under'] = sum(
    run['snapshot']['goals'] < run['final_goals'] for run in snapshot_runs)
summary['snapshot_checks']['goals_optimistic_over'] = sum(
    run['snapshot']['goals'] > run['final_goals'] for run in snapshot_runs)
snapshot_mismatches = []
for number in comparable:
    for repetition in REPETITIONS:
        run = records[number]['src1.3.1'][repetition - 1]
        if run.get('snapshot_matches_platform_base', True) and run.get('snapshot_goals_match', True):
            continue
        snapshot_mismatches.append({
            'case': '{:02d}'.format(number),
            'repeat': repetition,
            'snapshot_goals': run['snapshot']['goals'],
            'official_goals': run['final_goals'],
            'snapshot_constraints': run['snapshot']['constraints'],
            'official_constraints': run['credited_constraints'],
            'snapshot_base': run['snapshot']['base_score'],
            'platform_base': run['platform_deterministic_base'],
            'action_cost': run['platform_action_cost'],
            'stop_category': run['stop_category'],
        })

(BASE / 'analysis.json').write_text(
    json.dumps({'summary': summary, 'cases': cases,
                'snapshot_mismatches': snapshot_mismatches}, ensure_ascii=False, indent=2),
    encoding='utf-8')

with (BASE / 'comparison.csv').open('w', newline='', encoding='utf-8-sig') as stream:
    writer = csv.writer(stream)
    writer.writerow(['case', '1.3 scores', '1.3.1 scores', 'mean delta',
                     '1.3 goals', '1.3.1 goals', '1.3 actions', '1.3.1 actions',
                     '1.3 seconds', '1.3.1 seconds', '1.3.1 stop categories'])
    for row in cases:
        writer.writerow([
            row['case'], '/'.join(fmt(v) for v in row['score_1_3']),
            '/'.join(fmt(v) for v in row['score_1_3_1']), fmt(row['delta']),
            '/'.join(fmt(v) for v in row['goals_1_3']),
            '/'.join(fmt(v) for v in row['goals_1_3_1']),
            '/'.join(fmt(v) for v in row['actions_1_3']),
            '/'.join(fmt(v) for v in row['actions_1_3_1']),
            '/'.join(fmt(v, 3) for v in row['seconds_1_3']),
            '/'.join(fmt(v, 3) for v in row['seconds_1_3_1']),
            '/'.join(str(v) for v in row['stop_category_1_3_1']),
        ])

old = summary['src1.3']
new = summary['src1.3.1']
report = [
    '# src1.3 与 src1.3.1：realcompetition2024 对比报告', '',
    '- 36 题、每版 2 轮、共 144 次；IT 模式，cserver 单题时限 5000 ms。',
    '- 02.xml 存在 `Error reading end tag`，两版均为平台输入错误，排除总分比较。',
    '- 下表为其余 35 题两轮总分的均值；官方分按单题 1000 封顶，原始分不封顶。', '',
    '## 汇总', '',
    '| 指标 | src1.3 | src1.3.1 | 差值 |',
    '|---|---:|---:|---:|',
    '| 35 题官方分总和（两轮均值） | {} | {} | {:+.1f} |'.format(
        fmt(old['mean_official_total']), fmt(new['mean_official_total']),
        summary['mean_official_total_delta']),
    '| 35 题原始分总和（两轮均值） | {} | {} | {:+.1f} |'.format(
        fmt(old['mean_raw_total']), fmt(new['mean_raw_total']),
        summary['mean_raw_total_delta']),
    '| 最终完成目标总数（两轮均值） | {} | {} | {:+.1f} |'.format(
        fmt(old['mean_final_goals']), fmt(new['mean_final_goals']),
        summary['mean_final_goals_delta']),
    '| 最终满足约束总数（两轮均值） | {} | {} | {:+.1f} |'.format(
        fmt(old['mean_constraints']), fmt(new['mean_constraints']),
        summary['mean_constraints_delta']),
    '| 动作总数（两轮均值） | {} | {} | {:+.1f} |'.format(
        fmt(old['mean_action_count']), fmt(new['mean_action_count']),
        summary['mean_action_count_delta']),
    '| 平台硬超时运行（70 次有效运行） | {} | {} | {:+d} |'.format(
        old['platform_timeout_runs'], new['platform_timeout_runs'],
        new['platform_timeout_runs'] - old['platform_timeout_runs']),
    '| 正常退出运行（全部 72 次） | {} | {} | {:+d} |'.format(
        old['ok_runs'], new['ok_runs'], new['ok_runs'] - old['ok_runs']),
    '| 平均平台时间/题 | {:.3f}s | {:.3f}s | {:+.3f}s |'.format(
        old['average_platform_seconds'], new['average_platform_seconds'],
        new['average_platform_seconds'] - old['average_platform_seconds']), '',
    '- 两轮官方分总和：src1.3=`{}/{}`；src1.3.1=`{}/{}`。'.format(
        old['round_totals']['1']['official_score'], old['round_totals']['2']['official_score'],
        new['round_totals']['1']['official_score'], new['round_totals']['2']['official_score']),
    '',
    '35 道可比题中：{} 题提升、{} 题下降、{} 题不变。'.format(
        summary['improved_cases'], summary['regressed_cases'], summary['unchanged_cases']), '',
    '## 执行逻辑结论', '',
    '- src1.3.1 的 70 次有效运行中，stop gate 最终分类：`{}`。'.format(
        summary['src1.3.1_stop_categories']),
    '- 同轮配对的 70 组中，{} 组动作命令完全一致（含返回值的完整轨迹为 {} 组）；1.3.1 有 {} 组动作更少、{} 组更多、{} 组数量相同。'.format(
        summary['paired_identical_command_sequences'], summary['paired_identical_action_sequences'],
        summary['paired_new_has_fewer_actions'], summary['paired_new_has_more_actions'],
        summary['paired_same_action_count']),
    '- 其中 {} 组的 1.3.1 命令序列是 1.3 的严格前缀，直接体现 stop gate 在原执行路径上提前终止。'.format(
        summary['paired_new_command_is_strict_prefix']),
    '- src1.3.1 消除了本次有效运行中的平台硬超时，但大量长计划在剩余约 1–2 秒时被 1000/1750 ms 固定估时与 300 ms margin 拦截。',
    '- 这减少了动作与运行时间，也丢失了部分可在 5 秒前取得的 goal；当前参数偏保守。', '',
    '### 典型执行差异', '',
    '- **11 题（正向）**：goal 数保持 1，动作从 37 降到 28，均分提高 46；stop gate 避免了末段低收益动作。',
    '- **19/21/28/29/30 题（负向）**：多目标在最终聚合位置一次结算。1.3.1 在聚合前以 `estimate=1000ms` 停止，19/21/29/30 两轮均变成 0 goal；30 题均分下降 944。',
    '- **13 题（非纯 stop-gate 回归）**：1.3 为 6 步；1.3.1 反复 `PickUp 5`/`AskLoc 5`，增至 23/28 步，说明 Stage 2 初始状态/终态语义调整也改变了原执行分支。',
    '- **22–24 题**：每题从 35 goal 降为 25 goal，官方分从封顶 1000 降为 968；提前停止没有保住封顶分。',
    '- **25–27 题**：动作命令与官方得分保持一致，但 checker 只报告 15/35 goal；这是 snapshot 覆盖不足，不是 planner 行为变化。', '',
    '## ScoreEvaluator 核对', '',
    '- 最终 snapshot：`{}`。'.format(summary['snapshot_checks']),
    '- `deterministic_base_score` 与平台的“目标/约束分 − 动作成本”分开核对；官方 `# Score` 还包含时间奖励，因此不应直接相等。', '',
    '- 其中 35 次基础分偏低，是 UNKNOWN 带来的保守下界；但 16 题第 1 轮偏高 140 分，说明当前 checker 还不是始终安全的下界。',
    '- 16 题中 checker 把 `putdown` 视为“当前未持有即完成”，而平台只给了另外两个 goal；这个误判触发了 `all-goals` 提前退出。', '',
    '### snapshot 不一致明细', '',
    '| 题/轮 | goals snapshot→平台 | constraints snapshot→平台 | base snapshot→平台 | 动作成本 |',
    '|:---|---:|---:|---:|---:|',
]
for mismatch in snapshot_mismatches:
    report.append('| {}/{} | {}→{} | {}→{} | {}→{} | {} |'.format(
        mismatch['case'], mismatch['repeat'], mismatch['snapshot_goals'],
        mismatch['official_goals'], mismatch['snapshot_constraints'],
        mismatch['official_constraints'], mismatch['snapshot_base'],
        mismatch['platform_base'], mismatch['action_cost']))
report.extend([
    '',
    '## 逐题结果', '',
    '| 题 | 1.3 两轮 | 1.3.1 两轮 | 均值差 | goals 1.3→1.3.1 | actions 1.3→1.3.1 | 1.3.1 停止类型 |',
    '|---:|---:|---:|---:|---:|---:|:---|',
])
for row in cases:
    report.append('| {} | {} | {} | {} | {}→{} | {}→{} | {} |'.format(
        row['case'], '/'.join(fmt(v) for v in row['score_1_3']),
        '/'.join(fmt(v) for v in row['score_1_3_1']),
        ('{:+.1f}'.format(row['delta']) if row['delta'] is not None else '—'),
        '/'.join(fmt(v) for v in row['goals_1_3']),
        '/'.join(fmt(v) for v in row['goals_1_3_1']),
        '/'.join(fmt(v) for v in row['actions_1_3']),
        '/'.join(fmt(v) for v in row['actions_1_3_1']),
        '/'.join(str(v) for v in row['stop_category_1_3_1'])))

ranked = sorted((row for row in cases if row['delta'] is not None),
                key=lambda row: row['delta'])
report.extend(['', '## 最大变化', '',
               '- 下降最多：{}。'.format(', '.join(
                   '{}({:+.1f})'.format(row['case'], row['delta']) for row in ranked[:6])),
               '- 提升最多：{}。'.format(', '.join(
                   '{}({:+.1f})'.format(row['case'], row['delta']) for row in ranked[-6:][::-1])),
               ''])
(BASE / 'report.md').write_text('\n'.join(report), encoding='utf-8')

diff = ['# 动作序列差异（首次分歧）', '']
for number in comparable:
    for repetition in REPETITIONS:
        old_run = records[number]['src1.3'][repetition - 1]
        new_run = records[number]['src1.3.1'][repetition - 1]
        old_actions = old_run['action_commands']
        new_actions = new_run['action_commands']
        prefix = cases[number - 1]['command_common_prefix'][repetition - 1]
        if old_actions == new_actions:
            continue
        diff.extend([
            '## {:02d} / 第 {} 轮'.format(number, repetition), '',
            '- 共同前缀 {} 步；1.3 共 {} 步，1.3.1 共 {} 步。'.format(
                prefix, len(old_actions), len(new_actions)),
            '- 首次分歧：1.3=`{}`；1.3.1=`{}`。'.format(
                old_actions[prefix] if prefix < len(old_actions) else '<结束>',
                new_actions[prefix] if prefix < len(new_actions) else '<结束>'),
            '- 1.3.1 stop gate：`{}`。'.format(new_run['stop_category']), '',
        ])
(BASE / 'action-differences.md').write_text('\n'.join(diff), encoding='utf-8')

print(json.dumps(summary, ensure_ascii=False, indent=2))
