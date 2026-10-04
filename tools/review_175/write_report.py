"""Write the review from complete frozen records; never substitute historical runs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'validation/review175-20261004'
VERSIONS = ('src1.7.3', 'src1.7.4', 'src1.7.5')


def load(path):
    return json.loads(path.read_text(encoding='utf8'))


def table(totals):
    lines = ['| 版本 | 评分格/运行格 | 基础分 | SDK 原始分 | 正式分（逐题封顶） | G | C | K | 平台秒数合计 | SDK 超时 |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for v in VERSIONS:
        r = totals[v]
        lines.append('| {} | {}/{} | {} | {} | {} | {} | {} | {} | {:.3f} | {} |'.format(
            v, r['scored'], r['runs'], r['base'], r['raw_score'], r['official_score'], r['final_goals'],
            r['credited_constraints'], r['action_cost'], r['platform_seconds'], r['sdk_timeouts']))
    return '\n'.join(lines)


def delta_table(comparisons):
    lines = ['| 配对 | 对数 | 基础分变化 | SDK 原始分变化 | 正式分变化 | G 变化 | C 变化 | K 变化 | 平台秒数变化 |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for label, item in comparisons.items():
        d = item['delta']
        lines.append('| {} | {} | {:+} | {:+} | {:+} | {:+} | {:+} | {:+} | {:+.3f} |'.format(
            label, item['paired'], d['base'], d['raw_score'], d['official_score'], d['final_goals'],
            d['credited_constraints'], d['action_cost'], d['platform_seconds']))
    return '\n'.join(lines)


def main():
    s = load(OUT / 'SUMMARY.json')
    c = load(OUT / 'COMPETITION_SUMMARY.json')
    checks = load(OUT / 'checks/unit-summary.json')
    sanitizer = load(OUT / 'checks/sanitizer-summary.json')
    refs = load(OUT / 'frozen-v5/references.json')
    rows = load(OUT / 'frozen-v5/results.json')
    assert len(rows) == 432 and len(refs) == 24
    assert not s['violations']
    reference_timeouts = sum(bool(r['result'].get('platform_timed_out')) for r in refs)
    sample = [r for r in rows if r['id'] == 'g08a' and r['seed'] == 2026100401]
    sample_lines = ['| 版本 | 模式 | G | C | K | 基础分 | 正式分 | 秒数 | SDK 超时 |',
                    '|---|---|---:|---:|---:|---:|---:|---:|---|']
    for mode in ('it', 'nt'):
        for version in VERSIONS:
            r = next(x['result'] for x in sample if x['mode'] == mode and x['version'] == version)
            sample_lines.append('| {} | {} | {} | {} | {} | {} | {} | {:.3f} | {} |'.format(
                version, mode, r['final_goals'], r['credited_constraints'], r['action_cost'],
                r['base'], r['official_score'], r['platform_seconds'], bool(r.get('platform_timed_out'))))
    text = '''# 1.7.5 分数退化定位与放置证据恢复

## 结论

1.7.4 的证据修正是必要的，但没有补上取得确定性送达证据的动作路径；同时 Sense 的单容器推断和不必要的 inside 门槛会使合法目标失去候选资格。1.7.5 恢复部分目标，并修复独立联合内核的多个 inside 与双槽支持。它仍是开发检查点，性能结论必须逐题集看；下表的退化、额外动作及超时全部保留。

此前四版本审计中，1.7.2→1.7.3 基础分 +154、正式分 +306；1.7.3→1.7.4 基础分 -1227、正式分 -861、G -41。并非每一版都下降。这些是历史结果；本报告重新运行三版本，不把历史格替换进新表。

## 原因与实际修复

1. **证据门槛改变而路线不完整。** TakeOut→Move→PutDown 后，真实 SDK 仍可能保留 tray=A。1.7.4 不再把可见物品误判为托盘排除，却没有补验证动作；完整送达终态变 UNKNOWN，开柜破约束的损失仍算入，于是 g08 等题只移动/感知就停。
2. **感知不能提供唯一容器归属。** Sense 只返回 ID 集合，多个同地点容器无法由此区分。继承实现只记最后一个容器并清改 inside；1.7.5 删除这段推断，保留提示供动作验证。
3. **终态使用了无关前提。** SDK puton/give 等由槽位与显式地点判定，不要求 inside=NONE；本版移除这类终态与绑定资格中的无关 inside 门槛，未知存储事实仍不直接当成功。
4. **内核支持未闭合。** 官方允许 at 与多个 inside 共存、两个槽位同物。本版联合内核使用关系集合，PutIn 增加目标边、TakeOut 只删目标边；生产槽位赋值不再自动清掉另一个槽位。生产 inside 仍是单值，尚未完全修复。

新增 ConfirmOutsidePlacement：必要时尝试 PickUp→PutDown；PickUp 因托盘同物失败则 FromPlate→PutDown。每次使用真实公开反馈，长分支预算保留 300ms 加原安全余量。正常多 2 个动作/4 分成本，失败转移多 3 个动作/6 分成本；这些费用与时间真实记账，未伪装成免费验证。候选投影仍沿当前假设估价，尚不是完整联合反馈策略。

## 冻结协议

- 24 道上轮题 + 12 道新增题；IT/NT × 种子 2026100401/2026100402 × 三版，共 432 次。旧题每版 96 格，新题每版 48 格，分别统计。
- 新题四类结构 × 三次 ID/地点/任务顺序变换，每题 6 目标：更长闭柜路线、同地三个容器、托盘与柜内并存、多个目的地/重叠终态目标。题目设计未读规划器结果；所有原始草稿及预检失败保留。预检在正式比较前修正词表、XML 根节点和 SDK 合法 5 秒预算。
- 24 次 IT/NT 作者参考路径均有正式评分、6 目标、约定动作数/成本及零约束损失；参考动作不传给参赛机器人。参考路径用于检查可解性，不证明最优。
- Ubuntu-18.04 / g++7.5 / 同一真实 SDK，5 秒期限，串行轮换版本顺序；没有并行构建或运行中修改生产源码/题目/SDK/执行工具。前后源码、输入、工具、SDK 与执行二进制哈希一致，全部种子确认。固定随机种子不能冻结墙钟搜索截止，因此本轮与历史旧题成绩仍可能不同。
- 另加提前选定的六道真实比赛题 01/09/19/24/31/36，IT/NT × 两种子 × 三版共 72 次；它是独立补充样本，不代表完整比赛题库。主矩阵完成后串行执行，没有合并成完整题库结论。
- 失败评分不填零；SDK 硬截止但已获得正式评分的格保留，同时计入超时。所有退化、动作序列和失败状态在 CSV/原始证据中保留，未选取有利重跑替换。

## 旧题重新对照（每版 96 次）

{old_table}

{old_delta}

## 新增题（每版 48 次）

{new_table}

{new_delta}

## 六道真实比赛题样本（每版 24 次）

{competition_table}

{competition_delta}

G 为实际终态完成目标数，C 为获计分约束数，K 为实际尝试动作成本。基础分使用 SDK 实际终态 40G+20C-K；SDK 原始分另含 int((5-time)*10)×2 时间奖励。正式分沿用仓库 2026 规则的逐题 min(raw,1000)，不是 SDK 自动封顶，详见 [规则对照](../../docs/rules-diff-2025-2026.md)。旧题/新题原始分与封顶分相同，比赛样本存在超过 1000 的 SDK 原始分，因此两种口径都保留。表中的时间是逐运行平台时间的合计，绝非单题耗时。不能把少做动作、早停得到的时间奖励当成全部目标完成。

## 一条可追溯路径：g08a

{sample_table}

对应种子 2026100401。1.7.4 守住闭柜约束，但只完成 1 目标；1.7.5 愿意承担闭柜约束损失并恢复 4 目标。IT 格最后验证遇到硬截止，真实终态已完成 4 目标，但机器人没有充分时间完成全部证据检查；该超时原样保留。NT 格额外验证增加 K/耗时，正式分仍低于 1.7.3。这解释了“恢复目标”和“全面提分”不能等同。

每格原始动作/服务器评分见 [RUNS.csv](RUNS.csv)，全部指标退化或成本增加格见 [REGRESSIONS.csv](REGRESSIONS.csv)。补充样本逐格见 [COMPETITION_RUNS.csv](COMPETITION_RUNS.csv)。本次新题已经被观察，下一轮不能再称为未见过的留出题。

新增 retained_tray 族揭示三版共有的生产错误：h03a 等题里物品同时 tray=A、inside(A,Cupboard)。生产 FromPlate 会 ClearContainerMembership，再由 SetHold 把 inside 改成 NONE；真实 SDK 保留 inside。以 h03a/IT/2026100401 为例，三版动作相同，均没有 Open/TakeOut，服务器 G=5/base=154；1.7.5 最终日志却报 goals=6/6、base=194，并有 1245ms 余量。这不是来不及，而是错误关系证据导致少执行一个真实目标。新题作者参考路线实际执行 Open/TakeOut 并获得 G=6。该反例属于未修复的生产错误，不能因独立内核集合测试通过而忽略。

旧题 g04b/IT/2026100401 还保留一处目标退化：1.7.3 G=4/base=117，1.7.5 G=3/base=93，平台结束 2.394 秒。最后候选 incomplete_projection，询问所有回答分支价值归零，随后 no_task_and_no_legal_probe；这同样不是时间用尽。未知柜门与验证投影拒绝完整路线是下一轮排查重点，需把真实阻塞条件与候选估价同时修好。

## 检查与证据

普通与直接 SDK 测试 {unit_pass}/{unit_count}，其中 {official_count} 项为直接 SDK 检查；ASan/UBSan/泄漏检查 {san_pass}/{san_count}，耗时 {san_seconds} 秒。内存检查不包含直接 SDK 子进程测试。Probe 重复/授权/执行边界审计违规为 {violations}。

本版新增 SDK 多关系、双槽以及三种托盘真相（空 / 同物 / 其它物）的相同弱输入验证。旧单测里 Sense→inside=NONE、槽位互斥等错误假设已按 SDK 修正；原失败检查和构建日志全部保存。内存检查首次结果与任何修复/重试在摘要中单列，不能将诊断反例的 exit=0 解释为生产完全正确。

504 次生产运行的原始评分、逐题封顶分与 server.log 原文逐格一致。[CANONICAL_AUDIT.json](CANONICAL_AUDIT.json) 与 [CANONICAL_RUNS.csv](CANONICAL_RUNS.csv) 保留所有生产自报/SDK 分歧：新增题每版 12 格 goal_overcount，均为 retained_tray 族；1.7.5 旧题另有 5 格保守低报，不把低报与高报混成正确性通过。8 格 Stage 1 配对控制的实际动作、基础分和 G/C/K 一致，正式时间奖励有波动；仅证明这个控制范围。

参考最终 24 格 SDK 超时 {reference_timeouts}；之前预检的超时、非法预算/题目等单列在证据里，不混入最终生产矩阵。

完整证据：[evidence/manifest.json](evidence/manifest.json)，包含主矩阵、参考动作、补充比赛样本、执行源码/构建记录、全部失败与检查。归档逐项 CRC 与 SHA256 复核。生成的二进制及与归档固定 SDK 资源完全相同的重复文件由 SHA 记录，执行可复跑。三个预检题目草稿 ZIP 单独保留，不作为合法题库发布。

## 下一步优化顺序

1. **减少验证动作。** 已确认空手条件下，FromPlate(A) 失败可以证明 tray≠A；成功则再 PutDown(A)。每物通常省一个动作/2 分，并缩短路径。只记录该物的排除证据，不能推出整盘为空；未知/非空手失败不能提供这个结论。需要覆盖事务、revision、失败反馈和约束成本。
2. **拆开事实。** 生产逐容器保留真/假/未知 inside，区分 SDK 显式 at 与可见地点。官方动作只修改确实改变的关系；Sense 不推断不存在的边或槽位排除。
3. **修全路线估价。** ProjectVerification 的模拟 Sense 仍有 inside=NONE 继承推断；未知柜门路线又可能提前拒绝投影。先让模拟与执行证据一致，比较完整任务组的预期目标、约束、动作成本和 deadline，避免“有时间却停”和“验证过长”。
4. **概率模型接入生产。** 独立内核关系集合已修，真实联合先验、未覆盖质量、公开反馈策略分支、完整奖励、机会成本和 Probe 授权尚未接入。概率询问仍只是弱线索，不可直接变成 canonical 真值；采集没有被中间动作改变的后续观察作标签，再做校准。
5. **用新数据验证。** 下一版应先预注册新的未见结构与完整有效比赛题集，保留逐题退化并验证 Stage 1 行为。先修真实路径和语义，暂不增加模型规模或调参追逐本次题分。

开源接口借鉴及逐项代码边界见 [版本说明](../../src1.7.5/docs/RELEASE_1.7.5.md)，历史逐版新增功能见 [1.7.2—1.7.4 审计](../../docs/AUDIT_1.7.2_1.7.4.md)。
'''.format(old_table=table(s['totals']['suite']['old']),
           old_delta=delta_table(s['scoped_comparisons']['old']),
           new_table=table(s['totals']['suite']['new']),
           new_delta=delta_table(s['scoped_comparisons']['new']),
           competition_table=table(c['totals']), competition_delta=delta_table(c['comparisons']),
           sample_table='\n'.join(sample_lines), unit_pass=checks['passed'],
           unit_count=checks['ordinary_and_official_tests'], official_count=checks['official_direct_tests'],
           san_pass=sanitizer['passed'], san_count=sanitizer['tests'],
           san_seconds=sanitizer['seconds'], violations=len(s['violations']),
           reference_timeouts=reference_timeouts)
    (OUT / 'REPORT.md').write_text(text, encoding='utf8')


if __name__ == '__main__':
    main()
