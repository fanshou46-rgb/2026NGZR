#!/usr/bin/env python3
"""Write the delivery report from all retained pairs and verification logs."""
import argparse
import json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument('output',type=Path); args=p.parse_args(); out=args.output
    rows=json.loads((out/'results.json').read_text()); summary=json.loads((out/'summary.json').read_text())
    regressions=json.loads((out/'regressions.json').read_text()); audit=json.loads((out/'selection-and-clock-audit.json').read_text())
    a,b=summary['all']['baseline'],summary['all']['current']
    lines=['# src1.7 验证与交付报告','',
        '新版本路径：`src1.7/`。以仓库 HEAD f3088813 时最新的 `src1.6.7-200ms/` 为基线，旧版本未修改或删除。',
        '正常启动默认执行 greedy，guarded 是同一轮决策内自动尝试的优化步骤；策略环境变量已从生产代码移除。', '',
        '## 实现与源码核对','',
        '- 原普通循环按 task_index 推进；新循环每轮完整生成候选、过滤后按边际基础分/预计耗时/输入稳定 ID 选择。执行后重新读取反馈并生成候选。',
        '- 原 guarded 仅凭环境变量开启且只尝试一次，比较旧索引顺序的后续；新版本自动尝试并比较完整 greedy 后续、任务组后停止、任务组后继续 greedy、立即停止。',
        '- 原约束交换会用组合收益仅放行首任务；新版本单任务门控只接受自身证明，组合收益须绑定完整验证任务组及其必要 greedy 后续。',
        '- 原 MustChooseOne 按风险/索引兜底且不检查 CandidatePlan.eligible，可执行已标记不合格的任务。该入口与本次资格筛选要求冲突，生产流程不再调用；获得资格的恢复任务在统一循环重新生成。',
        '- 原 takeout 比较器在缺失 Y 时等价关系不传递，同优先级混入 putdown 也可形成环；新版本使用完整分组键和稳定输入 ID。索引用于寻址，ID 用于同分排序。',
        '- 嵌套预览原来重置预计动作耗时；新版本扣除已投影前缀，guarded 所有比较共用固定剩余时间，执行前再检查真实墙钟。',
        '- 保留 Stage 1 / 非 Multi-GOTO 的 guarded 支持范围，Stage 2 自动使用 greedy。保留证据来源及历史约束资格，弱证据不升级。',
        '- 保留 5000 ms 总期限、200 ms 普通余量、100 ms Multi-GOTO 尾部预留；guarded 每次最多 25 ms、整题累计 100 ms。候选生成和所有搜索计算均消耗总期限。',
        '- 失败任务同状态版本不重试，每任务至多 3 次、整题有界决策次数；物理/证据无进展检查排除计数、成本和版本递增。模拟恢复失败记录、任务标记、账本、执行反馈和新增调度状态。',
        '- 单 GOTO 参与普通 greedy；多 GOTO 延后既有聚合，聚合后用同一调度循环做必要修复。明确停止后不再执行尾部或恢复。',
        '- 评分源文件和终态检查源文件与基线一致，基础分仍为 `40G + 20 I(G>0) C - K`。G>0 是整题当前/预测终态条件，允许子计划只恢复约束或分享已有目标资格。','',
        '统一流程及复跑命令见 `../../docs/UNIFIED_SCHEDULER.md`。新增测试在 `../../tests/unified_scheduler_tests.cpp`。','',
        '## 验证范围','',
        'WSL2 Ubuntu-18.04 / g++ 7.5.0 / 官方 env-release-2026 SDK，生产版本分别完整编译链接。',
        '本地及 SDK 评分语义测试 146/146 通过，包括 20 项新统一调度用例；搜索超时测试、旧模式变量被忽略测试和原状态/账本回归均执行。',
        '最终源码 ASan/UBSan + leak detection 145/145 通过（该构建未重复链接外部 SDK 评分测试，SDK 评分测试在上述 146 项构建内通过）。内存检查和配对计时没有并行。',
        '第一份完整 284 对后，内存检查发现继承的 isMultiGotoMode 在直接预览前未初始化；只补默认 false，并再次运行完整配对。Plan 原已显式赋 false。修复前全部 284 对与 2 项 UBSan 失败日志保留在 pre-initialization/；下面统计最终源码的第二份完整配对，不替换或隐藏修复前数据。',
        'initialization-patch-audit.json 验证两次源码差异只有该初始化一行；源码、输入与二进制哈希分别记录。','',
        '默认对默认：33 道可原样评分的历史比赛题、37 道继承 release fixtures、1 道新组合收益题；固定种子 20260924，IT/NT，5000 ms，串行交替 AB/BA，两轮，共 %d 对 / %d 次运行。'% (len(rows),len(rows)*2),
        '没有设置策略环境变量，StageTiming 关闭。原题 02 XML 非法、04/05 既有官方评分失败，按原配对协议排除；输入未修复。继承 fixtures 含边界/冲突压力场景，不能据此宣称比赛题合法性审查全部通过。',
        '官方分按 1000 封顶，raw_score 另存。失败/超时保留在分母，缺失指标汇总按 0 并单独统计；有分数的超时保留其实际分数。两轮预先确定，未选择性补跑或替换结果。','',
        '| 范围 | 配对数 | 官方总分 旧→新 | 基础分 旧→新 | 目标数 旧→新 | 约束数 旧→新 | 动作成本 旧→新 | 超时 旧→新 |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for scope,v in summary.items():
        x,y=v['baseline'],v['current']
        lines.append('| %s | %d | %d→%d | %d→%d | %d→%d | %d→%d | %d→%d | %d→%d |' %
            (scope,v['pairs'],x['official_score'],y['official_score'],x['base'],y['base'],x['final_goals'],y['final_goals'],
             x['credited_constraints'],y['credited_constraints'],x['action_cost'],y['action_cost'],x['timeouts'],y['timeouts']))
    lines += ['', '总平台耗时：旧 %.3f 秒，新 %.3f 秒。失败数：%d→%d；缺失评分：%d→%d。' %
        (a['seconds'],b['seconds'],a['failures'],b['failures'],a['unscored'],b['unscored']),
        '官方总分提高/相同/下降的配对数：%d/%d/%d；基础分：%d/%d/%d；目标数：%d/%d/%d。' %
        tuple(summary['all'][k+'_pairs'][field] for k in ('official_score','base','final_goals') for field in ('improved','equal','worsened')), '',
        '## 全部退化与时间波动','',
        '%d 个配对出现官方分、基础分、目标数下降或新增超时，全部逐项列在 [REGRESSIONS.md](REGRESSIONS.md)，原始记录为 regressions.json；未只报告改善题。'%len(regressions),
        '阶段 2 中，原约束门控可借组合收益放行首任务，新版要求绑定验证序列且保持 guarded 原支持边界，因此部分原先能继续的约束交换被过滤。这类在尚有明显剩余时间时停止的退化属于决策变化。',
        '例如历史题 06、10、22 的明显目标下降，以及若干题的额外动作成本，须结合各次日志评估；不以平台总分的时间奖励遮盖基础分变化。',
        '题 22 的旧默认流程大量调用 MustChooseOne，新版候选被原资格条件筛除（eligible=false）且约 0.2 秒便停止，仍有约 4.8 秒余量；此退化涉及不再绕过资格的旧兜底入口，不应只归因为移除了借用任务组收益的门控。',
        '%d 个配对两版动作序列完全相同。仅当动作、基础分与官方终态指标均相同而官方分变化时，才归为墙钟奖励变化；动作不同还会改变后续观测的随机调用消费，不能仅归因于墙钟。'%audit['same_action_pairs'],
        '其中 %d 个配对满足上述纯墙钟奖励差异条件。'%audit['pure_clock_score_change'],
        '同种子两轮的每版动作是否变化、基础分变化、官方分与耗时变化见 selection-and-clock-audit.json。重复只用于观察时间敏感性，未作为独立随机样本。',
        '日志审核了 %d 轮真实 greedy 基准选择，%d 项不一致：筛除后的首个最高收益/稳定同分候选与实际记录一致。'% (audit['greedy_baselines'],len(audit['errors'])), '',
        '## 结论与未验证范围','']
    if b['official_score']<a['official_score'] or b['final_goals']<a['final_goals']:
        lines += ['建议保留 src1.7 作为已实现、可复跑的开发版本；当前配对存在实质退化，不建议替换比赛主版本。',
            '统一执行流程和保护条件已经验证，Stage 2 的收益损失仍需后续独立版本处理。本次没有扩大 guarded 支持范围、引入概率模型或改变评分以掩盖退化。']
    else:
        lines += ['建议保留 src1.7，结合全部退化表决定具体比赛配置采用；本结果仅覆盖此次固定题集与种子。']
    lines += ['官方 SDK 的运行与评分已经实际执行；没有验证其它 SDK/操作系统、更多随机种子、全部 2026 题集或真实比赛部署，也不声称竞赛组织方正式验收。','',
        '## 证据文件','',
        '- pairs.csv / results.json：每题每轮官方分、基础分、G、C、K、耗时、超时、状态、动作序列、决策日志。',
        '- raw-evidence.zip：所有 server/client 日志、原始输入、summary、官方 ASP 终态；没有只封装改善运行。',
        '- input-audit.json / final-audit.json / build-*/build.json：种子、源码/输入/SDK/二进制哈希与编译命令，运行前后未改变的审计。',
        '- unit-config.log / unit-build.log / unit-ctest.log / sanitizer-*：完整本地验证证据。',
        '- greedy-decisions.json / selection-and-clock-audit.json：每轮选择核对与预先固定的两轮时间波动比较。','']
    (out/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    decline=['# src1.7 全部退化配对','',
        '收录任一官方分/基础分/目标数下降及新增超时的所有配对；时间奖励造成的微小分差同样保留。',
        '每行对应 results.json 的 id、mode、round。原始日志在 raw-evidence.zip 的 runs/r{round}-{id}-{mode}-{arm}/。','',
        '| ID / 题目 | 阶段/模式/轮 | 官方分 旧→新 | 基础分 旧→新 | G 旧→新 | C 旧→新 | K 旧→新 | 秒 旧→新 | 超时 旧→新 | 动作相同 |',
        '|---|---|---:|---:|---:|---:|---:|---:|---|---|']
    for r in regressions:
        x,y=r['baseline'],r['current']
        pairs=['%s→%s'%(x[k],y[k]) for k in ('official_score','base','final_goals','credited_constraints','action_cost')]
        decline.append('| %s / %s | %d/%s/r%d | %s | %.3f→%.3f | %s→%s | %s |' %
            (r['id'],Path(r['path']).name,r['stage'],r['mode'],r['round'],' | '.join(pairs),x['platform_seconds'] or 0,y['platform_seconds'] or 0,
             x['platform_timed_out'] or x['external_timeout'],y['platform_timed_out'] or y['external_timeout'],x['action_sequence']==y['action_sequence']))
    (out/'REGRESSIONS.md').write_text('\n'.join(decline)+'\n',encoding='utf-8')

if __name__=='__main__': main()
