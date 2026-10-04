"""Generate reports from every frozen production pair; no score substitution."""
import collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'validation/review177-20261004'
VERSIONS=('src1.7.6','src1.7.7')
NAMES={'old':'旧回归24题','seen175':'已见175题12道','seen176':'已见176题8道','holdout177':'新增177题8道','competition':'六道比赛样本','stage1_control':'四道Stage1控制'}
ORDER=tuple(NAMES)
def main():
    summary=json.loads((OUT/'SUMMARY.json').read_text(encoding='utf8'));suites=summary['suites']
    unit=json.loads((OUT/'checks/unit-summary.json').read_text(encoding='utf8'))
    sanitizer=json.loads((OUT/'checks/sanitizer-summary.json').read_text(encoding='utf8'))
    publication=json.loads((OUT/'checks/staged-publication-audit.json').read_text(encoding='utf8'))
    inputs=json.loads((OUT/'checks/executed-input-tooling.json').read_text(encoding='utf8'))
    rows=json.loads((OUT/'raw/frozen-v1/results.json').read_text(encoding='utf8'))
    refs=json.loads((OUT/'raw/frozen-v1/references.json').read_text(encoding='utf8'))
    assert summary['pairs']==152 and len(rows)==304 and len(refs)==16
    assert all(r['result']['status']=='ok' and not r['result']['external_timeout'] and not r['result']['platform_timed_out'] for r in refs)
    lines=['# 1.7.7 可见性概率区间与探索损失复核','',
    '在已提交 1.7.6 上独立建立 1.7.7，旧版本保持不变。完整联合策略尚未完成；本轮接入生产的是局部联合可见性场景、未覆盖概率质量与条件更新，并修复可见性模拟、独立 at 证据及探索终态损失。成绩以下列重新运行的官方 SDK 矩阵为准。','',
    '## 本轮解决什么','',
    '1. 1.7.6 把一个代表 inside/柜门当成物品能否被看到的唯一原因。实际 SDK 允许显式 at、多个 inside 与槽位共存。返回桌边的候选因此误报丢掉杯子送达，预测 gain1/loss1/utility−5。1.7.7 模拟 Sense 使用所有可见原因的并集，独立反例变为 gain1/loss0/utility35；真实 SDK 六项关系测试逐动作核对 Sense ID。',
    '2. 可见不等于独立 at。新证据字段区别 UNKNOWN、确认没有 at（−2）和确认地点（含 0）；成功动作按 SDK 更新，失败不写成功事实。模拟 PickUp、终态及零动作完成捷径不会将已确认无 at 的开柜可见物当作已送达。字段参与投影、事务及缓存。UNKNOWN at 下仍有旧路线估价，全部事实闭合尚未完成。',
    '3. 观察候选构造最多 32 个局部场景，保留独立 at、全部确认父边、槽位和柜门，用有效公开 Sense 条件化，输出可见性上下界。尾部、未知及支持缺失进入 residual，不重分给已知场景。生产使用下界；仍不是任务完成概率或已校准成功率。',
    '4. 条件更新采用已覆盖权重下界与 residual 上界的保守包络；事件 ID 支持去重，非法似然先校验而不改状态。已覆盖似然为零但 residual>0 时结果为未知区间 [0,1]；没有任何支持时保留先验并报失败。完整联合行动后验尚未持久接入。',
    '5. 已确认多个正确询问答案时，当前模型不知道 SDK 的选答顺序，候选标记 unmodeled_truthful_reply_order；不编造答案概率。真实提问仍可能错误。槽位排除、合法物理反馈和任务证据独立保留。',
    '6. 原探索以 Move4/120ms 代替已完成 goto 的 40 分损失，默认未来必定返回。本版扣实际预测丢失目标每项 40 分；没有完整恢复路线就不承诺恢复。expected_gain 仍含启发式目标机会值，完整约束/时间/封顶收益反馈树仍待实现。','',
    '## 冻结协议与新题','',
    '24 道旧题、12 道已见175题、8 道已见176题，各用第一种子 × IT/NT × 两版，共 176 次；8 道新177题和提前固定比赛样本 01/09/19/24/31/36，用两个种子 × IT/NT × 两版，共 112 次。四道 Stage1 控制 × 第一种子 × IT/NT × 两版，共 16 次。合计 304 次、152 对；旧题组没有跑第二种子。每题 5000ms，串行轮换顺序，运行中没有并行构建或修改参与源/输入/工具/SDK/二进制。随机种子不冻结墙钟截止。',
    '新题四族：显式 at 与远处闭柜、两物共享父容器、槽位转移与双父、双槽同物。ID/地点/目标顺序独立变化，生成器不读取机器人分数。第一次作者预检在 k03a NT 到达 5 秒，12/16 动作、G3；相同 IT 路径完成 16 动作用时 4.645 秒。此时机器人矩阵尚未开始，原题/工具/日志全部保存。随后对四族统一把书的显式 at 放在书桌，使书送达成为已满足控制，参考路径不再运输书，保留对应 inside 关系；六目标数量不变。最终 16 次参考 IT/NT 均实际 G6/C0、约定动作数/成本、无硬截止及外部超时。参考只证明可解性，不证明最优，也不供机器人。新题在本轮后归为已见回归；不能把书控制目标的成绩增量解释为新完成运输任务。',
    '局部场景 coverage 的 .75/.5 是查看新题机器人成绩前冻结的开发假设，未按结果拟合；仍需独立校准。','',
    '## 官方结果','',
    '每组为全部格合计，时间也是合计。基础分=40G+20C−K，G=0 时不计约束分；K 包含所有成功及失败尝试。SDK 原始分含时间奖励，正式分逐题 min(raw,1000)，SDK 自身不自动封顶。缺失评分与截止均保留，不能拿内部自报当成绩。','',
    '| 题集 | 版本 | 有分/运行 | 基础分 | SDK原始分 | 正式分 | G | C | K | 平台秒数 | 硬截止 |',
    '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for suite in ORDER:
        for version in VERSIONS:
            r=suites[suite][version]
            lines.append('| {} | {} | {}/{} | {} | {} | {} | {} | {} | {} | {:.3f} | {} |'.format(NAMES[suite],version,r['scored'],r['runs'],r['base'],r['raw_score'],r['official_score'],r['goals'],r['constraints'],r['cost'],r['seconds'],r['sdk_timeouts']))
    lines+=['','| 1.7.6→1.7.7 | 基础分 | 正式分 | G | C | K | 秒数 |','|---|---:|---:|---:|---:|---:|---:|']
    for suite in ORDER:
        d=suites[suite]['delta'];lines.append('| {} | {:+d} | {:+d} | {:+d} | {:+d} | {:+d} | {:+.3f} |'.format(NAMES[suite],d['base'],d['official_score'],d['goals'],d['constraints'],d['cost'],d['seconds']))
    lines+=['', '逐题退化或成本/时间增加共 {} 对，全部见 [REGRESSIONS.csv](REGRESSIONS.csv)。{} 个服务器原始分与逐格记录核对；全部动作、硬截止、失败和原始路径见 [RUNS.csv](RUNS.csv)。'.format(summary['regression_or_cost_time_increase_pairs'],summary['server_raw_score_verified']),'',
    '## 逐动作复核','']
    analysis=OUT/'TRACE_ANALYSIS.md'
    if analysis.exists():lines.append(analysis.read_text(encoding='utf8'))
    else:raise RuntimeError('Actual trace analysis is required before publication')
    lines+=['','## 内部完成判定与真实终态','','| 题集 | 版本 | 类别及格数 |','|---|---|---|']
    for suite in ORDER:
        for version in VERSIONS:lines.append('| {} | {} | {} |'.format(NAMES[suite],version,json.dumps(suites[suite][version]['canonical'],ensure_ascii=False)))
    lines+=['','equal 为 G/C/K/base 全部一致；goal_overcount/goal_undercount 为高报/低报；other_difference 为其它分歧；no_final_claim 为没有最终自报。低报也不是完全正确，不能只统计高报为零。Stage1 配对动作和目标核对见 STAGE1_AUDIT.json。','',
    '## 检查与证据','',
    '最终普通/直接 SDK {0}/{0}，其中 29 项直接 SDK，耗时 {1:.2f} 秒。新增 16 项普通概率/可见性/终态反例；已有六项关系 SDK 测试增加每次动作后实际 Sense ID 与模拟的比较，未增加直接 SDK 的测试项数。最后新增“开柜可见但无独立 at”用例先失败，发现零动作捷径仍查旧位置，修正后最终全通过；前序编译和单测失败日志保留。'.format(unit['tests'],unit['seconds']),
    '最终 ASan/UBSan/泄漏 {0}/{0}，{1:.2f} 秒，不含 SDK 子进程。较早 290 项草稿检查完成时源码仍在迭代，只作为草稿日志保留，不作最终证据；最终检查在冻结的 79 个相关源码/测试/构建/输入字节上完成，后续均未变。'.format(sanitizer['tests'],sanitizer['seconds']),
    '证据包保留全部生产、参考、作者预检失败、构建/测试失败与执行源码。每个归档 CRC 及每项 SHA 已核对，生成二进制用哈希/构建配方记录，完全相同 SDK 资源保留一份；manifest 列出所有排除项。',
    '发布核对 {} 个文件，{} 个 Git 字节与执行字节完全一致（本版检查相关 {} 个）；{} 个历史题/索引/工具仅有 Git LF 与本机 CRLF 差异。历史文件保持原样，全部 {} 个冻结输入/工具的执行字节另存 checks/executed-input-tooling.zip；本版核心与 words.txt 不允许换行等价替代。'.format(len(publication['expected_sha256']),publication['exact_git_and_workspace_files'],publication['checked_files'],len(publication['historical_git_line_ending_differences']),inputs['files']),
    '', '## 尚未完善与下一步','',
    '概率模型仍未完整：可见性概率不是完成概率，单物先验只是参考支持；残余场景覆盖、持久联合动作后验、未知柜门恢复路线、多正确询问选答顺序、完整终态/约束/时间/封顶奖励与执行闭环仍需补齐。参数未经独立数据校准；未知显式 at 下还存在旧路线估价。',
    '后续优先用同一反馈树比较直接任务、观察、失败和恢复的相对停止收益；用公开反馈更新联合状态，完成多父/双槽/门未知支持，独立记录不支持的观察；再冻结参数，用下一批独立结构题校准并验证完整比赛题。不能把局部通过或单组提分称为完整联合模型完成。',
    '', '模型公式与固定 GitHub 依据见 [概率说明](../../src1.7.7/docs/PROBABILITY_1.7.7.md)，机器人每步实际决策见 [流程](../../src1.7.7/docs/ROBOT_FLOW_1.7.7.md)。','']
    (OUT/'REPORT.md').write_text('\n'.join(lines),encoding='utf8')
    release='# 1.7.7 可见性概率区间与探索终态损失\n\n独立保留 1.7.6。生产观察候选增加最多 32 个联合可见性场景，未覆盖质量保留为 residual，按公开 Sense 更新并使用概率下界。补独立 at 证据、共存关系可见性模拟及终态捷径；探索扣实际预测目标损失，多正确询问顺序未知时拒绝该项概率估价。\n\n320/320 普通及直接 SDK、291/291 内存检查；304 次真实 SDK 配对及全部退化见 [报告](../../validation/review177-20261004/REPORT.md)。完整联合动作策略和校准仍未完成。公式和边界见 [概率说明](PROBABILITY_1.7.7.md)，逐步流程见 [实际决策](ROBOT_FLOW_1.7.7.md)。复制的旧文档记录历史版本。\n'
    (ROOT/'src1.7.7/docs/RELEASE_1.7.7.md').write_text(release,encoding='utf8')
    (ROOT/'src1.7.7/README.md').write_text('# src1.7.7 可见性概率与探索损失检查点\n\n生产观察使用局部联合场景、公开反馈条件更新及概率区间，保留未覆盖质量。独立 at、inside 与槽位可共存；修复可见性模拟、送达捷径和探索终态损失。\n\n[版本说明](docs/RELEASE_1.7.7.md)、[304 次正式 SDK 对比与全部退化](../validation/review177-20261004/REPORT.md)、[概率模型和剩余边界](docs/PROBABILITY_1.7.7.md)、[每步实际决策](docs/ROBOT_FLOW_1.7.7.md)。完整联合行动策略与概率/时间校准仍需完善；其它复制文档属于历史记录。\n',encoding='utf8')
if __name__=='__main__':main()
