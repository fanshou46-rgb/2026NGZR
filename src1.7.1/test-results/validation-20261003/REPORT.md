# src1.7.1 发布验证报告

独立版本 `src1.7.1` 基于 `src1.7`（仓库基线提交 ecafa0bc）。新增 Stage 2 停滞分支的有界、目标导向 Probe；正常 greedy、Stage 1、基础分、canonical authority、mutation、约束交换、deadline 参数和 guarded 支持范围保持。未改动旧版本、题源或既有结果，未删除文件。

设计见 [PROBE_LAYER.md](../../docs/PROBE_LAYER.md)，权威/异常闭合审计见 [PROBE_AUDIT.md](../../docs/PROBE_AUDIT.md)。新增普通候选与 Probe 类型分离，MustChooseOne 只有只读 proposal / 日志权限。

## 验证协议与范围

WSL Ubuntu-18.04、g++ 7.5.0、官方 `/home/yifan/env-release-2026` SDK。普通及 SDK 语义验证 183/183 通过，含 37 项 Probe 专项测试；Debug ASan/UBSan + leak detection 182/182 通过。另将最终客户端用 ASan/UBSan 插桩后，链接真实 SDK 运行 8 个 IT/NT 场景，全部通过；官方 SDK 静态库本身未重新插桩。内存检查、编译与正式配对计时没有并行。

原 71 输入按基线哈希解析搬迁后的当前路径；comprehensive 全部 200 输入中 180 正常题进入成绩比较，20 故意非法题独立记录。总共 271 个输入，固定种子 20260924、5000 ms、IT/NT、预先确定两轮、串行交替 AB/BA、StageTiming 关闭，共 1084 对 / 2168 次运行；其中 1004 对正常成绩、80 对非法输入。原 71 协议仍排除历史原题 02 的 XML 错误、04/05 的既有官方评分错误，没有修题或扩大排除。

两轮同种子用于观察墙钟敏感性，不作为独立随机样本。正式比较运行前后源码和输入 SHA-256 均一致，编译命令、SDK/二进制哈希保存在 full-release/input-audit.json、build-*/build.json 和 final-audit.json。

首次 sanitizer 默认 PIE 的启动失败在未改动 1.7 上也复现；采用 1.7 既有验收的非 PIE 配置后全量通过。一次全量比较启动因含空格的 LD_PRELOAD 路径未加载种子，在首个运行的种子校验处中止；该中止记录保留，正式比较改用无空格的 WSL 产物路径。早期 SDK 冒烟、测试失败、启动失败及各轮修复前记录均保留，不替换为成功日志。

修复前另一次完整 1084 对比较发现 c001 NT 两轮各少完成 3 个目标：单任务无正收益，但原 Multi-GOTO 完整聚合尾部有正收益，8 次 Probe 占用了尾部预算。接入处补齐原完整尾部投影、原 100 ms 余量及原约束交换检查；有合法正收益尾部时直接交回原流程。这项修复没有改变原 planner、selector 或参数。随后对最终源码重新执行全部预定 1084 对，没有挑选替换单次结果。修复前源码快照、完整配对和原始日志见 pre-tail-check-source/、analysis/ 和 pre-tail-check-evidence.zip。

## 正常输入成绩

官方分采用平台分数，含时间奖励和 1000 封顶；raw_score 另存。基础分逐次用官方 ASP 的 G、C 和实际 SDK 动作成本计算 `40G + 20 I(G>0) C - K` 后汇总，不以时间奖励掩盖退化。缺失值不虚构，仍保留在配对分母并单列缺失数量。非法输入不加入本表。

| 范围 | 配对数 | 官方总分 1.7 → 1.7.1 | 基础分 | G | C | K | 超时 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 全部正常 | 1004 | 725080 → 728146 | 644848 → 653144 | 5161 → 5401 | 23190 → 23190 | 25392 → 26696 | 0 → 0 |
| 原 71 | 284 | 107500 → 110576 | 85908 → 94204 | 1841 → 2081 | 1002 → 1002 | 7772 → 9076 | 0 → 0 |
| 正常 comprehensive | 720 | 617580 → 617570 | 558940 → 558940 | 3320 → 3320 | 22188 → 22188 | 17620 → 17620 | 0 → 0 |
| Stage 1 | 480 | 343402 → 343398 | 306816 → 306816 | 2476 → 2476 | 11172 → 11172 | 15664 → 15664 | 0 → 0 |
| Stage 2 | 524 | 381678 → 384748 | 338032 → 346328 | 2685 → 2925 | 12018 → 12018 | 9728 → 11032 | 0 → 0 |

两版各 1004 对正常运行均完成评分。官方评分缺失：0 → 0。
官方分提高/相同/下降：31/913/60；基础分：20/948/36；目标数：20/984/0。

## Stage 1 冻结检查

480 对正常 Stage 1 中，新增 Probe 为 0；动作或基础分差异 0 对。
全部 Stage 1 动作序列和基础分相同，因此没有需要逐项解释的动作/基础分差异。
仅官方时间奖励变化的 Stage 1 配对为 22 对：动作、G、C、K 和基础分相同，符合纯墙钟差异的统计口径。

## Probe 恢复与成本

Stage 2 共 116 次 Probe：{'MoveSense': 92, 'SenseCurrentLocationOnly': 24}。最大单题运行次数 5。
收到反馈 116 次；获得相关新信息 108 次；无相关新信息 8 次；完整重规划后有效 108 次、无进展 8 次。
下一轮恢复正常候选的事件 56 次，恢复任务记录 196 条，随后成功完成的恢复任务记录 72 条。任务记录按运行/Probe/任务去重，同一任务跨 Probe 的恢复可能分别记录；这些指标不等于官方新增目标数。
真实来源 provenance 的变化标记汇总为 {'sense_evidence_changes': 112, 'action_success_evidence_changes': 100, 'action_failure_evidence_changes': 0}；Move 明确失败 0 次、执行异常/失败 0 次。来源变化字段是 0/1 标记，不是对象数量；原包装器来源语义保持。

基线 Stage 2 真正停止且仍剩至少 300 ms（一次 Sense 加原安全余量）的 486 对运行中，36 对在 Probe 后恢复正常候选（7.41%），其中 32 对随后完成恢复任务，20 对官方目标数提高。Multi-GOTO 的尾部转交不计为提前停止。
输入去重后：提前停止 122 个输入，恢复正常候选 9 个输入。恢复输入为 `c005`, `c011`, `c012`, `c031`, `c032`, `c033`, `c056`, `c058`, `c070`。

原 71 输入单独看：符合上述提前停止口径的 126 对中，36 对恢复正常候选（28.57%），32 对随后完成恢复任务。180 道正常 comprehensive 的基础分、G、C、K 全部相同；其中 Stage 2 的 360 对提前停止没有恢复，实际 Probe 为零，候选被相关约束安全未知、额外物理动作或没有合法可观察地点等边界拒绝。该题集没有探索收益，官方总分的 -10 来自时间奖励波动。

Probe 的信息价值与官方收益分开。部分观察获得新信息却未解除风险/约束或不完整投影，因此只增加成本；无具体线索、开放容器 INSIDE 歧义、容器开关状态和相关约束未知仍可能停止。没有恢复旧的 eligible=false task 执行兜底。

| 候选拒绝原因 | 次数 |
| --- | ---: |
| constraint_safety_unknown | 1205 |
| deadline | 37 |
| duplicate_related_revision | 48 |
| extra_physical_actions | 480 |

以上为候选日志条数，同一地点在多轮停滞中可再次被拒绝；这不代表实际重复执行。执行前拒绝：{}。
Probe 分支 stop/tail 原因汇总：{'qualified_goto_tail': 72, 'deadline': 29, 'constraint_rejected': 239, 'no_task_and_no_legal_probe': 256, 'duplicate_or_no_information': 20, 'same_probe_bound': 4}。qualified_goto_tail 是返回原尾部流程，其他原因与普通 scheduler 的最终停止日志结合读取。

## 非法输入：预期分类与实际处理

20 个故意非法输入全部运行并保留，均为原 catalogue 的 Stage 1 输入，因此没有 Probe。预期分类不等同于 SDK 必须拒绝：语法/对象域错误和语义不一致可能被既有容错或解释路径接受。本版冻结 Stage 1 和 parser，不修复或重新分类题源。

| 预期层 | 输入数 | 配对数 | 1.7 IT / NT 状态 | 1.7.1 IT / NT 状态 |
| --- | ---: | ---: | --- | --- |
| xml | 4 | 16 | {'failed': 4, 'ok': 4} / {'failed': 4, 'ok': 4} | {'failed': 4, 'ok': 4} / {'failed': 4, 'ok': 4} |
| syntax | 2 | 8 | {'ok': 4} / {'ok': 4} | {'ok': 4} / {'ok': 4} |
| domain | 4 | 16 | {'ok': 8} / {'ok': 8} | {'ok': 8} / {'ok': 8} |
| semantics | 10 | 40 | {'ok': 20} / {'ok': 20} | {'ok': 20} / {'ok': 20} |

非法输入两版的状态/动作/基础分/目标/退出/超时差异 0 对。每题每模式每轮的错误、评分缺失、动作序列与 IT/NT 差异在 analysis-final/invalid-runs.json；预期错误层汇总在 analysis-final/invalid-summary.json。

## 退化、执行权与有界性

60 对正常运行出现官方分、基础分或目标数下降，全部列在 [REGRESSIONS.md](REGRESSIONS.md)，包含只增加 Probe 成本的运行及纯时间奖励差异，不选择性移除。逐输入四次配对在 analysis-final/per-input.json，全部逐次表在 analysis-final/pairs.csv。
其中 c011 四对均多完成 1 个目标，增加 36 动作成本，基础分 35→39；但总耗时从约 0.186–0.188 秒升至 1.591–1.615 秒，时间奖励减少，使官方分 131→105–107。这四对按官方分退化完整保留。
运行审计检查 116 次 Probe，授权/阶段/重复/重开/上限/失败后 Sense/MustChooseOne 生产动作违规 0 项。原候选日志与正常 greedy 选择核对 4044 轮，两版合计不一致 0 项。
冻结文件与关键函数的源码核对通过；新增 Probe 不直接写事实或调用 Plug SDK。正常输入没有新增超时，专项测试覆盖逐动作 deadline、隐藏清理、相关/无关 UNKNOWN、投影恢复、明确失败、mutation 异常和 8/2/2 边界。无限循环、同上下文重复执行和 production MustChooseOne 动作检查未发现违规。

## 交付与复跑

本版提供两种局部可验证 Probe，并能在部分原提前停止输入恢复普通候选。性能评价以本表和全部退化记录为准；同种子结果不能外推到其它随机回答或平台。本次未扩大搜索、引入贝叶斯模型或更改官方基础分/冻结语义。

- `../../tests/build_probe.sh`、`validate_probe.sh`、`sanitize_probe.sh`、`compare_probe.sh`：生产构建、测试、内存检查、全量复跑。比较输出必须使用全新无空格路径。
- `full-release/results.json` / `analysis-final/pairs.csv`：全部 1084 对，非法输入和缺失评分也保留。
- `raw-evidence.zip`：正式运行的全部 server/client 日志、原始输入、官方 ASP 状态/结果、summary、构建 metadata、种子和两版二进制；相同 SDK iclingo 只存一次，原 WSL 运行目录保留。
- `smoke-evidence.zip` / `seed-path-aborted-evidence.zip`：早期 SDK 冒烟及种子路径校验中止的完整证据，分别标注为诊断而非正式配对。
- `authority-audit-tail-final.json`、`full-release/final-audit.json`、`analysis-final/runtime-audit.json`、`analysis-final/greedy-audit.json`：冻结语义、输入/源码、执行权限和真实选择核对。
- `unit-tail-check-final.log`、`sanitizer-tail-final.log`、`sanitizer-tail-final-LastTest.log`、`sdk-sanitizer-tail-final.log`：最终通过的检查；此前失败和基线复现日志全部保留。
- `sdk-sanitizer-evidence.zip`：最终源码在真实 SDK 上的 8 次客户端插桩运行；pre-tail-sdk-sanitizer-evidence.zip 保留修复前同协议运行。
