#!/usr/bin/env python3
from collections import Counter
from difflib import SequenceMatcher
import json
from pathlib import Path
import re

ROOT = Path('/mnt/d/FILES for Yvaine/WUT/Match/robocup/2026NGZR')
BASE = ROOT / 'test-results/realcompetition-scr12-vs-scr13-20260921'
VERSIONS = ('scr1.2', 'scr1.3')
REPETITIONS = (1, 2)


def run_dir(version, repetition):
    suffix = '' if repetition == 1 else '-r{}'.format(repetition)
    return BASE / ('runs-' + version + suffix)


def load_result(version, repetition, number):
    stage = 1 if number == 2 else 2
    folder = run_dir(version, repetition) / ('{:02d}-s{}-it'.format(number, stage))
    summary = folder / 'summary.json'
    if summary.exists():
        row = json.loads(summary.read_text(encoding='utf-8'))
    else:
        error = folder / 'runner-error.json'
        row = json.loads(error.read_text(encoding='utf-8')) if error.exists() else {}
    server = folder / 'server.log'
    text = server.read_text(encoding='utf-8', errors='replace') if server.exists() else ''
    actions = []
    for match in re.finditer(r'^\s*\[([^|\]]+)\|([^\]]*)\]', text, re.M):
        actions.append('{}|{}'.format(' '.join(match.group(1).split()), ' '.join(match.group(2).split())))
    row['action_sequence'] = actions
    row['folder'] = str(folder)
    return row


def average(values):
    values = [value for value in values if value is not None]
    return sum(values) / len(values) if values else None


def fmt(value):
    if value is None:
        return '—'
    if isinstance(value, float) and not value.is_integer():
        return '{:.1f}'.format(value)
    return str(int(value))


def must_near_count(number):
    text = (ROOT / '题目' / 'realcompetiton_2024' / ('{:02d}.xml'.format(number))).read_text(
        encoding='utf-8', errors='replace')
    return len(re.findall(r'\(:cons_notnot\s+\(:info\s+\((?:near|nextto)\b', text))


records = {}
for number in range(1, 37):
    records[number] = {
        version: [load_result(version, repetition, number) for repetition in REPETITIONS]
        for version in VERSIONS
    }

stable = []
clean = []
rows = []
for number, versions in records.items():
    all_scored = all(run.get('official_score') is not None
                     for version in VERSIONS for run in versions[version])
    old_scores = [run.get('official_score') for run in versions['scr1.2']]
    new_scores = [run.get('official_score') for run in versions['scr1.3']]
    old_raw = [run.get('raw_score') for run in versions['scr1.2']]
    new_raw = [run.get('raw_score') for run in versions['scr1.3']]
    row = {
        'case': '{:02d}'.format(number),
        'must_near': must_near_count(number),
        'stable': all_scored,
        'all_ok': all(run.get('status') == 'ok'
                      for version in VERSIONS for run in versions[version]),
        'old_scores': old_scores,
        'new_scores': new_scores,
        'old_average': average(old_scores),
        'new_average': average(new_scores),
        'raw_old_average': average(old_raw),
        'raw_new_average': average(new_raw),
    }
    row['delta'] = (row['new_average'] - row['old_average']
                    if row['old_average'] is not None and row['new_average'] is not None else None)
    row['old_actions'] = [len(run['action_sequence']) for run in versions['scr1.2']]
    row['new_actions'] = [len(run['action_sequence']) for run in versions['scr1.3']]
    row['same_sequence'] = [versions['scr1.2'][index]['action_sequence'] ==
                            versions['scr1.3'][index]['action_sequence']
                            for index in range(2)]
    rows.append(row)
    if all_scored:
        stable.append(row)
    if row['all_ok']:
        clean.append(row)

summary = {
    'cases': 36,
    'repetitions': 2,
    'mode': 'it',
    'sdk': '/home/yifan/env-release-2026',
    'stable_cases': len(stable),
    'clean_cases': len(clean),
    'stable_official_total_1_2': sum(row['old_average'] for row in stable),
    'stable_official_total_1_3': sum(row['new_average'] for row in stable),
    'stable_raw_total_1_2': sum(row['raw_old_average'] for row in stable),
    'stable_raw_total_1_3': sum(row['raw_new_average'] for row in stable),
    'scored_runs_1_2': sum(run.get('official_score') is not None for versions in records.values()
                             for run in versions['scr1.2']),
    'scored_runs_1_3': sum(run.get('official_score') is not None for versions in records.values()
                             for run in versions['scr1.3']),
    'ok_runs_1_2': sum(run.get('status') == 'ok' for versions in records.values()
                         for run in versions['scr1.2']),
    'ok_runs_1_3': sum(run.get('status') == 'ok' for versions in records.values()
                         for run in versions['scr1.3']),
}
summary['stable_official_delta'] = (summary['stable_official_total_1_3'] -
                                    summary['stable_official_total_1_2'])
summary['stable_raw_delta'] = summary['stable_raw_total_1_3'] - summary['stable_raw_total_1_2']
summary['clean_official_total_1_2'] = sum(row['old_average'] for row in clean)
summary['clean_official_total_1_3'] = sum(row['new_average'] for row in clean)
summary['clean_official_delta'] = (summary['clean_official_total_1_3'] -
                                   summary['clean_official_total_1_2'])
clean_must_near = [row for row in clean if row['must_near']]
summary['clean_must_near_cases'] = len(clean_must_near)
summary['clean_must_near_total_1_2'] = sum(row['old_average'] for row in clean_must_near)
summary['clean_must_near_total_1_3'] = sum(row['new_average'] for row in clean_must_near)
summary['clean_must_near_delta'] = (summary['clean_must_near_total_1_3'] -
                                    summary['clean_must_near_total_1_2'])
summary['improved_cases'] = sum(row['delta'] > 0 for row in stable)
summary['regressed_cases'] = sum(row['delta'] < 0 for row in stable)
summary['unchanged_cases'] = sum(row['delta'] == 0 for row in stable)

(BASE / 'analysis.json').write_text(json.dumps({'summary': summary, 'cases': rows},
                                               ensure_ascii=False, indent=2), encoding='utf-8')

report = []
report.append('# scr1.2 与 scr1.3：realcompetiton_2024 对比报告')
report.append('')
report.append('- 环境：WSL Ubuntu-18.04，SDK `/home/yifan/env-release-2026`，IT 模式，单题 5000 ms。')
report.append('- 范围：01–36 全部 XML；每版重复 2 轮，共 144 次运行。')
report.append('- 02.xml 本身 XML 结束标签错误，两版两轮均无法由 cserver 载入。')
report.append('- “稳定可比”要求同一道题两版两轮均产生官方分数，共 {} 题。'.format(len(stable)))
report.append('')
report.append('## 汇总')
report.append('')
report.append('| 指标 | scr1.2 | scr1.3 | 差值 |')
report.append('|---|---:|---:|---:|')
report.append('| 稳定可比题官方分均值之和 | {} | {} | {:+.1f} |'.format(
    fmt(summary['stable_official_total_1_2']), fmt(summary['stable_official_total_1_3']),
    summary['stable_official_delta']))
report.append('| 稳定可比题原始分均值之和 | {} | {} | {:+.1f} |'.format(
    fmt(summary['stable_raw_total_1_2']), fmt(summary['stable_raw_total_1_3']), summary['stable_raw_delta']))
report.append('| 两版两轮均正常完成的 {} 题官方分 | {} | {} | {:+.1f} |'.format(
    summary['clean_cases'], fmt(summary['clean_official_total_1_2']),
    fmt(summary['clean_official_total_1_3']), summary['clean_official_delta']))
report.append('| 其中 {} 道正常完成的 must-near 题 | {} | {} | {:+.1f} |'.format(
    summary['clean_must_near_cases'], fmt(summary['clean_must_near_total_1_2']),
    fmt(summary['clean_must_near_total_1_3']), summary['clean_must_near_delta']))
report.append('| 产生分数的运行 | {} / 72 | {} / 72 | {:+d} |'.format(
    summary['scored_runs_1_2'], summary['scored_runs_1_3'],
    summary['scored_runs_1_3'] - summary['scored_runs_1_2']))
report.append('| 未超时且状态为 ok 的运行 | {} / 72 | {} / 72 | {:+d} |'.format(
    summary['ok_runs_1_2'], summary['ok_runs_1_3'], summary['ok_runs_1_3'] - summary['ok_runs_1_2']))
report.append('')
report.append('稳定可比题中：{} 题提升、{} 题下降、{} 题不变。'.format(
    summary['improved_cases'], summary['regressed_cases'], summary['unchanged_cases']))
report.append('')
report.append('## 逐题得分')
report.append('')
report.append('| 题号 | must-near 数 | 1.2 两轮 | 1.3 两轮 | 均值差 | 两轮步骤相同 |')
report.append('|---:|---:|---:|---:|---:|:---:|')
for row in rows:
    old = '/'.join(fmt(value) for value in row['old_scores'])
    new = '/'.join(fmt(value) for value in row['new_scores'])
    same = '/'.join('是' if value else '否' for value in row['same_sequence'])
    report.append('| {} | {} | {} | {} | {} | {} |'.format(
        row['case'], row['must_near'], old, new,
        ('{:+.1f}'.format(row['delta']) if row['delta'] is not None else '—'), same))

report.append('')
report.append('## must-near 题目结论')
report.append('')
for row in rows:
    if row['must_near']:
        report.append('- {}：{} 条 must-near，1.2={}，1.3={}，均值差={}。'.format(
            row['case'], row['must_near'], '/'.join(fmt(v) for v in row['old_scores']),
            '/'.join(fmt(v) for v in row['new_scores']),
            '{:+.1f}'.format(row['delta']) if row['delta'] is not None else '—'))

report.append('')
report.append('## 日志中的关键执行步骤差异')
report.append('')
report.append('- **13.xml（稳定改进）**：1.2 在共同的 6 步之后继续执行失败的 `Move 1`、`AskLoc 4` 和 `Sense`；1.3 由 must-near 证据直接完成零动作预验证。两轮分别少 3/4 步，官方分均值提升 16。')
report.append('- **11.xml（截止时刻敏感）**：第二轮前 37 步完全一致；1.2 在超时前多完成最后一个 `Move 7` 回到聚合点，1.3 停在 `PickUp 17` 后。该轮因此是 449 对 53；第一轮两版均为 53。')
report.append('- **29/30.xml（主要总分回归）**：两轮共同动作前缀基本相同。1.2 在 `Move 12`（聚合点）处超时，分别保住 21/25 个 goto 目标；1.3 又执行 `PutDown 10` 和离开聚合点的 `Move 15` 后超时，只剩 2 个目标，单题分别下降 766/926。两题都没有 must-near 约束，属于 5 秒边界上的聚合收尾问题。')
report.append('- **35/36.xml（完成度改善但官方分封顶）**：1.3 两轮都在 5 秒内正常完成 45 个目标；1.2 多轮超时或只完成 29–36 个目标。由于官方单题封顶 1000，官方总分看不出收益，但原始分明显提高。')
report.append('- **06–08、14–16、18–24 的小幅变化**主要伴随 AskLoc 返回值、Sense 次数或 5 秒截断位置变化；两轮间波动较大，不能仅凭当前两轮归因于 must-near 语义。')

(BASE / 'report.md').write_text('\n'.join(report) + '\n', encoding='utf-8')

diff_report = ['# 执行步骤差异', '']
for number, versions in records.items():
    for repetition in REPETITIONS:
        old = versions['scr1.2'][repetition - 1]['action_sequence']
        new = versions['scr1.3'][repetition - 1]['action_sequence']
        if old == new:
            continue
        matcher = SequenceMatcher(a=old, b=new)
        changes = [opcode for opcode in matcher.get_opcodes() if opcode[0] != 'equal']
        diff_report.append('## {:02d} / 第 {} 轮'.format(number, repetition))
        diff_report.append('')
        diff_report.append('- 1.2：{} 步；1.3：{} 步。'.format(len(old), len(new)))
        for tag, i1, i2, j1, j2 in changes:
            diff_report.append('- `{}`：1.2[{}:{}] → 1.3[{}:{}]'.format(tag, i1 + 1, i2, j1 + 1, j2))
            if old[i1:i2]: diff_report.append('  - 1.2：`{}`'.format(' → '.join(old[i1:i2])))
            if new[j1:j2]: diff_report.append('  - 1.3：`{}`'.format(' → '.join(new[j1:j2])))
        diff_report.append('')

(BASE / 'action-differences.md').write_text('\n'.join(diff_report) + '\n', encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
