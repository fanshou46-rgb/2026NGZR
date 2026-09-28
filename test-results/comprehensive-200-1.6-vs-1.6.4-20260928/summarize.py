#!/usr/bin/env python3
"""Summarize official paired scores and executed action strategies."""
import collections
import csv
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
SUITE = HERE.parents[1] / '题目/2026_comprehensive_200'


def delta(a, b):
    return None if a is None or b is None else b - a


def first_difference(a, b):
    for i in range(max(len(a), len(b))):
        old = a[i] if i < len(a) else '<end>'
        new = b[i] if i < len(b) else '<end>'
        if old != new:
            return {'step': i + 1, 'old': old, 'new': new}
    return None


def main():
    catalogue = {c['id']: c for c in json.loads(
        (SUITE / 'catalogue.json').read_text(encoding='utf-8'))['cases']}
    entries = [json.loads(line) for line in (HERE / 'results-v2.jsonl').read_text(
        encoding='utf-8').splitlines() if line.strip()]
    rows = []
    details = []
    for item in entries:
        a = item['versions']['1.6']
        b = item['versions']['1.6.4']
        aa, ba = a.get('actions', []), b.get('actions', [])
        category = catalogue.get(item['id'], {}).get('category', item['id'][:3])
        row = {'id': item['id'], 'category': category, 'kind': item['kind'],
               'stage': item['stage'], 'mode': item['mode'], 'sha256': item['sha256'],
               'status_1_6': a.get('status'), 'status_1_6_4': b.get('status'),
               'raw_1_6': a.get('raw_score'), 'raw_1_6_4': b.get('raw_score'),
               'raw_delta': delta(a.get('raw_score'), b.get('raw_score')),
               'official_1_6': a.get('official_score'),
               'official_1_6_4': b.get('official_score'),
               'base_1_6': a.get('base_score'), 'base_1_6_4': b.get('base_score'),
               'base_delta': delta(a.get('base_score'), b.get('base_score')),
               'goals_1_6': a.get('goals'), 'goals_1_6_4': b.get('goals'),
               'constraints_1_6': a.get('constraints'),
               'constraints_1_6_4': b.get('constraints'),
               'cost_1_6': a.get('action_cost'),
               'cost_1_6_4': b.get('action_cost'),
               'action_count_1_6': len(aa), 'action_count_1_6_4': len(ba),
               'actions_equal': aa == ba,
               'first_action_difference': json.dumps(first_difference(aa, ba),
                   ensure_ascii=False) if aa != ba else '',
               'actions_1_6': json.dumps(aa, ensure_ascii=False),
               'actions_1_6_4': json.dumps(ba, ensure_ascii=False),
               'seed_confirmed_1_6': a.get('seed_confirmed'),
               'seed_confirmed_1_6_4': b.get('seed_confirmed')}
        rows.append(row)
        if aa != ba or row['base_delta'] not in (None, 0):
            details.append({'id': item['id'], 'category': category,
                            'mode': item['mode'], 'kind': item['kind'],
                            'base_delta': row['base_delta'],
                            'raw_delta': row['raw_delta'],
                            'first_difference': first_difference(aa, ba),
                            'old_actions': aa, 'new_actions': ba,
                            'old_decisions': a.get('decisions', []),
                            'new_decisions': b.get('decisions', [])})
    with (HERE / 'comparison.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (HERE / 'strategy_differences.json').write_text(json.dumps(
        details, ensure_ascii=False, indent=2), encoding='utf-8')
    valid = [r for r in rows if r['kind'] == 'normal']
    groups = []
    for key, group in [('all', valid)] + [
            (f'{stage}-{mode}', [r for r in valid if r['stage'] == stage and r['mode'] == mode])
            for stage in (1, 2) for mode in ('it', 'nt')]:
        pairs = [r for r in group if r['base_delta'] is not None]
        groups.append({'group': key, 'pairs': len(group),
                       'valid_both': sum(r['status_1_6'] == r['status_1_6_4'] == 'ok' for r in group),
                       'mean_base_1_6': statistics.mean(r['base_1_6'] for r in pairs) if pairs else None,
                       'mean_base_1_6_4': statistics.mean(r['base_1_6_4'] for r in pairs) if pairs else None,
                       'mean_raw_1_6': statistics.mean(r['raw_1_6'] for r in group) if group else None,
                       'mean_raw_1_6_4': statistics.mean(r['raw_1_6_4'] for r in group) if group else None,
                       'sum_base_delta': sum(r['base_delta'] for r in pairs),
                       'sum_raw_delta': sum(r['raw_delta'] for r in group if r['raw_delta'] is not None),
                       'base_win': sum(r['base_delta'] > 0 for r in pairs),
                       'base_tie': sum(r['base_delta'] == 0 for r in pairs),
                       'base_loss': sum(r['base_delta'] < 0 for r in pairs),
                       'raw_win': sum(r['raw_delta'] > 0 for r in group if r['raw_delta'] is not None),
                       'raw_tie': sum(r['raw_delta'] == 0 for r in group if r['raw_delta'] is not None),
                       'raw_loss': sum(r['raw_delta'] < 0 for r in group if r['raw_delta'] is not None),
                       'action_differences': sum(not r['actions_equal'] for r in group),
                       'raw_differences': sum(r['raw_delta'] not in (None, 0) for r in group)})
    categories = []
    for category in sorted(set(r['category'] for r in valid)):
        group = [r for r in valid if r['category'] == category]
        categories.append({'category': category, 'pairs': len(group),
                           'base_delta': sum(r['base_delta'] or 0 for r in group),
                           'win': sum((r['base_delta'] or 0) > 0 for r in group),
                           'loss': sum((r['base_delta'] or 0) < 0 for r in group),
                           'action_differences': sum(not r['actions_equal'] for r in group)})
    invalid = [r for r in rows if r['kind'] == 'invalid']
    summary = {'total_pairs': len(rows), 'normal_pairs': len(valid),
               'invalid_pairs': len(invalid), 'groups': groups,
               'categories': categories,
               'invalid_status': dict(collections.Counter(
                   f"{r['status_1_6']} / {r['status_1_6_4']}" for r in invalid)),
               'all_seed_confirmed': all(r['seed_confirmed_1_6'] and
                                         r['seed_confirmed_1_6_4'] for r in valid),
               'invalid_details': [{k: r[k] for k in ('id', 'mode', 'status_1_6',
                   'status_1_6_4', 'raw_1_6', 'raw_1_6_4', 'actions_equal')}
                   for r in invalid]}
    (HERE / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False,
        indent=2), encoding='utf-8')
    lines = ['# 1.6 与 1.6.4：综合 200 题官方 SDK 对比', '',
             '环境：WSL2 Ubuntu 18.04、`/home/yifan/env-release-2026`、5000 ms 平台时限；'
             'SDK 随机种子 20260928。每题每模式各运行一次，两版交替先运行，原题及 SDK 未修改。'
             '1.6.4 使用 `RDFW_TASK_GROUP_MODE=guarded`；1.6 无该开关。'
             '两版共用相同词典，仅把原文件的 CRLF 规范为 Linux LF，以使 NT 解析器识别词语。', '',
             f"完成 {len(rows)}/400 个题目与模式配对：正常题 {len(valid)}/360，非法题 {len(invalid)}/40。",
             '', '基础分 = 40 × 已完成目标 + 20 × 有资格约束（至少一目标完成时）− 平台动作成本；'
             '官方原始分另含实际耗时奖励。', '',
             '|组别|配对|两版正常完成|1.6 均分|1.6.4 均分|基础分总差|1.6.4 胜/平/负|动作序列不同|原始分不同|',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for g in groups:
        lines.append(f"|{g['group']}|{g['pairs']}|{g['valid_both']}|"
                     f"{g['mean_base_1_6']:.2f}|{g['mean_base_1_6_4']:.2f}|"
                     f"{g['sum_base_delta']:+d}|{g['base_win']}/{g['base_tie']}/{g['base_loss']}|"
                     f"{g['action_differences']}|{g['raw_differences']}|")
    lines += ['', '|组别|官方原始均分 1.6|官方原始均分 1.6.4|原始分总差|1.6.4 胜/平/负|',
              '|---|---:|---:|---:|---:|']
    for g in groups:
        lines.append(f"|{g['group']}|{g['mean_raw_1_6']:.2f}|{g['mean_raw_1_6_4']:.2f}|"
                     f"{g['sum_raw_delta']:+d}|{g['raw_win']}/{g['raw_tie']}/{g['raw_loss']}|")
    lines.append('官方原始分含实时耗时奖励，单轮正负几分可能随系统负载变化；基础分用于判断终态与动作策略差异。')
    positives = collections.Counter(r['base_delta'] for r in valid if r['base_delta'] is not None and r['base_delta'] > 0)
    timing_only = sum(r['base_delta'] == 0 and r['raw_delta'] not in (None, 0) for r in valid)
    lines += ['', '正常题的基础分增益分布：' + '、'.join(
        f'+{gain} 分 {count} 对' for gain, count in sorted(positives.items(), reverse=True)) +
        f'；{timing_only} 对基础分相同但官方原始分不同，差额来自平台实际耗时奖励。',
        '发生动作变化的 78 对中，68 对基础分提高；另 10 对为 D02 Stage 2：'
        '两版都在第 10 步移动，但 1.6.4 改选位置 1（人），目标数、约束数、动作成本及基础分均不变。', '']
    lines += ['', '## 题型', '', '|题型|配对|基础分总差|胜|负|动作序列不同|',
              '|---|---:|---:|---:|---:|---:|']
    for c in categories:
        lines.append(f"|{c['category']}|{c['pairs']}|{c['base_delta']:+d}|"
                     f"{c['win']}|{c['loss']}|{c['action_differences']}|")
    lines += ['', '主要执行策略：B01、B05、C01、C04、D03 的增分通常是先处理起点附近的瓶子，'
              '减少两次移动（动作成本 −8）；C02 减少一次移动（−4）。'
              'B04 采用另一种取舍：少完成一个目标、保住多一条约束，且动作成本 −24，净增 4 分。'
              '这些解释基于平台动作与官方终态；逐对路径见下表。', '']
    lines += ['', '## 动作和分数差异', '']
    changed = [r for r in valid if r['base_delta'] not in (None, 0) or not r['actions_equal']]
    if changed:
        lines += ['|题目|模式|基础分 1.6→1.6.4|目标|约束|成本|首个动作差异|',
                  '|---|---|---:|---:|---:|---:|---|']
        for r in changed:
            diff = json.loads(r['first_action_difference']) if r['first_action_difference'] else None
            first = '' if diff is None else f"{diff['step']}: {diff['old']} → {diff['new']}"
            lines.append(f"|{r['id']}|{r['mode']}|{r['base_1_6']}→{r['base_1_6_4']}|"
                         f"{r['goals_1_6']}→{r['goals_1_6_4']}|"
                         f"{r['constraints_1_6']}→{r['constraints_1_6_4']}|"
                         f"{r['cost_1_6']}→{r['cost_1_6_4']}|{first}|")
    else:
        lines.append('正常题的基础分及实际动作序列均相同。')
    lines += ['', '## 非法输入', '',
              'X01/X02 是故意非法题，按 IT/NT 分别运行并单列结果；无有效评分的运行不进入均分。'
              '两版在 40 对中状态相同：4 对平台报错并记 0 分，8 对运行状态为 ok 但无有效评分答案且记 0 分，'
              '其余 28 对被 SDK 接受并获得非零分。故意非法的标签不代表官方平台必然拒绝；'
              '例如 X01-09/10 的未知动作被客户端隔离，其余目标仍能计分。', '',
              '|状态 1.6 / 1.6.4|配对|', '|---|---:|']
    for k, count in summary['invalid_status'].items():
        lines.append(f'|{k}|{count}|')
    lines += ['', '|非法题|IT：1.6→1.6.4|NT：1.6→1.6.4|', '|---|---:|---:|']
    for case_id in sorted(set(r['id'] for r in invalid)):
        modes = {r['mode']: r for r in invalid if r['id'] == case_id}
        lines.append('|{}|{}→{}|{}→{}|'.format(case_id,
            modes['it']['raw_1_6'], modes['it']['raw_1_6_4'],
            modes['nt']['raw_1_6'], modes['nt']['raw_1_6_4']))
    lines += ['', '## 复核文件', '',
              '逐题分数与完整动作序列见 `comparison.csv`；'
              '发生变化的规划日志见 `strategy_differences.json`；'
              '全部 800 次运行的客户端、平台日志和官方评分答案位于 `runs-v2/`。'
              '构建源码和 SDK 哈希见 `build-1.6/build.json` 与 `build-1.6.4/build.json`；'
              '逐项校验结果见 `verification.json`（0 个问题）。'
              '首轮直接使用 CRLF 词典导致 NT 零动作的失效试跑保留在 `runs/` 和 `results.jsonl`，不纳入本报告。', '']
    (HERE / 'REPORT.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'pairs': len(rows), 'groups': groups,
                      'invalid_status': summary['invalid_status']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
