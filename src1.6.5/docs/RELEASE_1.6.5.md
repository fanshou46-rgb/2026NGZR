# src1.6.5 — Evidence / Fact / Derived State 分层

基线：已验证的 `src1.6.4`。本版本为独立目录；未修改基线、旧版本、官方 SDK 或原题。`words.txt` 使用 LF 换行。

## 1. 审计与原状态模型

输入从 `ParseEnvSentence/ParseEnv`、`ParseInfo`、`GetSmallObjectStatus/GetBigObjectStatus`、两条 Sense 管线和九种动作包装进入。1.6.4 将对象 `location/inside/isOpen` 等字段作为规划值，以并行 `Source/Verified` 数组记录来源及终态强度；`objectLocationInferredByMustNear` 另标记组内推导。`TerminalChecker` 读取这些字段及数组，任务/约束绑定由静态 id、sort、color、type 构成，投影逐项快照并恢复对象及并行数组。`hold_id/plate_id` 由 `Robot` setter 和动作包装管理，`on` 只保存在小物体中，`near` 以同地位置表达。

原跨层写入点：初始描述和 Ask 直接覆盖规划位置，即使 Stage 2 未验证；`ParseInfo` 曾将补充信息写成已验证的 inside/opened/closed/plate；Sense 和动作结果直接修改对象字段并覆写来源；must-near、must-in、容器内容物位置推导与当前字段共用存储。must-near 有局部撤销，其他关系多依靠来源标记与 TerminalChecker 的约束资格检查。`CandidatePlan` 投影保存并行数组，但不存在独立的证据记录或事实依赖快照。

数据流现在明确为：

`initial / Ask / Sense / action feedback / :info` → 有界 `StateClaim` → 规划假设和 `StateProvenance.resolved_value` → 带依赖的派生状态 → binding / TerminalChecker / planning。

这里的对象字段仍是兼容旧算法的**规划假设**。证据冲突且不能定真时，规划假设可以保留一个可执行候选位置，但 `resolved_value=UNKNOWN` 且终态不把它当作已验证事实。这样不以主观来源优先级决定世界真值，也不让弱证据冲突强迫导航策略重排。

## 2. 新状态结构与冲突规则

`StateProvenance` 对 location、inside、container state 及 robot hold/plate 保存：最近收到的 claim、一个相异的 claim、当前 resolved 值、来源、验证标记、revision、最多两个事实依赖，以及支持约束索引。must-in 保存单一支持索引，must-near 和开关状态保存本题相关约束索引列表。证据历史为常数大小，约束列表受本题约束数限制；没有概率、权重或全量历史。原 `Source/Verified` 数组保留为兼容视图，新增查询 `Provenance`、`HasContradictoryEvidence`、`DependenciesCurrent`、`ResolvedState`。最后一个查询只返回已验证且依赖仍有效的值；弱假设、UNKNOWN 和过期派生值返回空 claim。`Provenance` 用于检查来源快照，不能替代合法事实查询。兼容性的 heuristic 来源仍不授予事实资格，也不引入 candidate score 或 task preference。

Stage 2 初始描述和 Ask 仍为弱证据。弱位置/inside 与后续弱回答冲突时两条 claim 均保留，resolved 值为 UNKNOWN；导航假设可以采用后来的位置，终态保持 UNKNOWN。Sense 和成功动作按平台可观察结果建立已验证事实；动作失败不凭空建立成功事实。Stage 2 普通 `:info` 只形成弱 claim：官方 SDK `src/evaluate.cpp` 的 `cti_to_asp` 对 `I_INFO` 明确返回 ignore，不能证明其为官方世界真值。Stage 1 的已知世界语义保持不变。

## 3. Derived 依赖和失效

must-near 推导的位置记录锚点位置 revision 和组件相关的支持约束；容器内容物位置记录 inside 与容器位置两个依赖；must-in 推导的 inside 记录支持约束索引；must-open/closed 记录相关开关约束。支持约束的 `constraint_eligible` 变为 false，或 `constraint_uncertain` 变为 true，派生状态即失去事实资格。`DependenciesCurrent` 对所有依赖类型递归检查 revision、值和约束资格，深度超过 8 或存在循环时保守失效。原 must-near 刷新时清除过期位置的行为保留。`ParseInfo` 的 on/near/inside 位置传播也记录其位置或 inside 前提。

`BuildTaskGroupPlan` 的保存/恢复加入所有 provenance 容器以及 hold/plate 元数据。投影运行相同动作包装，因此成功、失败、约束和依赖元数据与真实执行共用转移路径。原 `CandidatePlan.evidence` 在状态恢复后才采集，实际显示投影前信息；现在于恢复前采集投影终态，并用带依赖校验的查询输出 `verified`。新增测试将投影的 action-success 事实与真实动作后的事实逐项核对。

## 4. 行为边界

未改评分公式、严格区间支配、legacy 优先级、候选顺序/搜索、任务调度、5000 ms 截止和完整投影门控。Stage 2 弱冲突不授予目标满足。一次开发中曾把初始位置与 Ask 位置冲突直接清除规划值：06 的导航路线变化，基础分 298→154。原题初始 `at(4,8)` 为可能错误的初始信息，Ask 给出 `at(4,5)`；两者均是弱证据，无法证明其中任何一个为事实。修复为保留规划假设 `5`、resolved UNKNOWN，定向 03/06/29 重测回到相同动作。该失败实验不作为发布结果。

另一个最小语义复现：Stage 2 初始容器开关未验证，随后收到普通 `:info (closed X)`。1.6.4 的 `ParseInfo` 会把 `closed` 标为 verified，使零动作检查直接判定 close 已完成；SDK 的评分输入明确忽略普通 `:info`，所以该结论缺少世界事实依据。1.6.5 保存收到的 closed claim，但终态仍为 UNKNOWN，直到 Sense、可证明的动作反馈或有效约束给出支持。

最终回归发现并保留 P10 的 IT/NT 两个语义差异。最小复现为：设置 `must-near(book,table)`；移动书至位置 3；Sense 观察到书，关系传播将桌子的位置推导为 3；该支持约束已失去确定资格。1.6.4 的 TerminalChecker 会拒绝这一约束来源，但 `IsLocationVerified(table)` 仍返回 true，`SolveTask_PutOn(cup,table)` 的同地提前返回条件因此错误通过。1.6.5 的统一资格查询返回 false，原动作逻辑执行 Sense，平台反馈 `5 3 6 4` 中没有桌子，随后两次 AskLoc(2) 均返回 `not_known`。这证明桌子不能继续作为位置 3 的已验证事实。新增用例 17 覆盖支持约束不确定后的事实查询和终态失效。

两种模式共同的前四步为 `PickUp(4), Move(3), Sense, PutDown(4)`；新版追加 `PickUp(5), Sense, AskLoc(2), AskLoc(2)`。双方目标数 5、约束数 0；动作成本 9→16，基础分 191→184。新状态判断正确拒绝缺少支持的结论，额外动作沿用已有求解逻辑，并不保证能完成任务或提高分数。dry-run 的 Sense 使用当前规划假设，仍无法预测真实平台会否发现桌子；这一隐藏观察预测边界保留为后续工作。

## 5. 文件和测试

产品修改集中在 `rdfw.hpp`、`rdfw.cpp`、`stage_timing.hpp`、`CMakeLists.txt`；本版本新增 `tests/state_layer_tests.cpp` 和验证脚本，调整 `tests/recovery_evidence_tests.cpp` 中 Stage 2 普通 `:info` 的旧断言。原 20 个 state invariant 用例原样保留。新增 19 个最小用例覆盖：证据/事实区分、弱初始、Ask、成功/失败、冲突、派生依赖与失效、终态、投影恢复、dry-run、UNKNOWN、约束资格及 hold/plate 来源；补充开关状态支持、must-near 约束不确定化，以及安全事实查询与循环依赖。官方语义测试仍使用 SDK 原评分器。

## 6. 验证矩阵

WSL Ubuntu 18.04 / g++ 7.5.0、官方 `/home/yifan/env-release-2026`、原 realcompetition 题及原 1.6.4 矩阵，固定随机种子，同 SDK 和题源。构建源码、SDK 和 118 对题源 SHA-256 核对通过，见 `../test-results/validation-20260928/audit.json`。

| 项目 | 最终结果 |
|---|---:|
| CTest，含官方评分语义和原 20 个 state invariant | 50/50 |
| ASan + UBSan（非 PIE，WSL 兼容构建） | 49/49 |
| 原 86 对 | 84/86 同基础分、同动作；P10 IT/NT 语义差异见第 4 节 |
| 03/06/29，IT/NT，三轮 | 18/18 同基础分、同动作 |
| guarded off | 14/14 同基础分、同动作 |
| 合计 | 116/118 同基础分、同动作；236 次有效官方运行 |
| 硬超时 / 动作成本不匹配 | 0 / 0（236/236 次成本核对） |

目标和约束计数每对均相同。官方原始总分有 6 对差异：P10 IT/NT 均为 283→268，其中基础分减少 7 分，时间奖励减少 8 分；另 4 对基础分及动作完全相同，仅时间奖励相差 2 分，分别为全量 N01 Stage 1 NT（200→198）、realcompetiton_2024/01 IT（427→425）、01 NT（385→387），以及定向第一轮 06 IT（310→312）。真实比赛题的基础分和动作均一致。

原始 server/client 日志及 answer set 见同目录各套 `*-evidence.zip`，逐套结果和汇总见 `*-results.json`、`*-summary.json`，后者逐条保存官方总分差异。开发中 06 的弱冲突处理曾改变路线，该构建已废弃；发布结果只使用最终 `build.json` 对应源码。全部 50 个 CTest 与 49 个 sanitizer 用例均重跑通过；sanitizer 不重复运行外部官方评分器，因此数量少一个。投影恢复用例也明确核对依赖 revision 和支持约束列表。

## 7. 性能

状态记录每字段只保留两条不同 claim、两个事实依赖和本题支持约束索引。直接证据更新为常数时间；派生写入收集相关约束，查询只检查已保存的支持索引，最多向下 8 层，不遍历证据历史或全部对象。`StageTiming` 新增 `state_update` 与 `derived_invalidation` 两项，原有 `terminal` 与 `projection` 项保留；正式比较关闭计时，独立性能采样启用。投影复制有界元数据，不复制完整运行历史。

独立对 03/06/29 IT/NT 六对计时，双方投影次数均为 1016、TerminalChecker 次数均为 4834。累计 TerminalChecker：1.6.4 为 52.432 ms、1.6.5 为 47.114 ms；投影：78.067→77.934 ms；1.6.5 的状态元数据更新 13236 次合计 0.365 ms、must-near 派生刷新 4220 次合计 0.309 ms。单次最大 TerminalChecker 为 92→97 μs，投影 405→306 μs，元数据更新 34 μs，派生刷新 7 μs。元数据计时只覆盖字段写入，约束支持收集也包含在派生刷新或投影整体时间中；整数微秒累计对很短操作存在舍入。样本小且包含平台调度噪声，不能据此宣称总运行提速。原始分阶段数据见 `perf-target-performance-summary.json`；本组采样未见显著关键路径增长。

## 8. 未解决问题和下一步

对象字段仍为旧规划器的单一候选值，`Source/Verified` 与新元数据同步存在；更广泛的跨关系冲突、多个 must-near 约束的最小支持集和完整的运行时重放没有通用依赖图。Stage 2 的 Ask/Sense dry-run 仍无法预测平台隐藏状态。`on` 字段仍是兼容性注释，终态按位置、inside 与必要的验证/依赖判断；未来若让 `on` 独立参与任务，应先给它单独的证据与事实解析。当前接口已能供后续 belief layer 读取证据、resolved 值与依赖，但建议继续收敛状态层、移除兼容视图的双写风险，再冻结 1.6 系列并开启概率决策开发线。

支持列表目前采取保守失效：组件内保存的任一支持约束失效，相关派生结论即不可作事实；尚未求解替代支持路径。只有规范化后进入状态写入路径的 claim 被保留，失败动作诊断仍在原反馈记录中，未建立完整外部事件日志。证据最多保留两个不同值，适合比赛关键路径，无法重放全部历史。后续 belief layer 可以从这些来源接口接入，但还需按需要设计独立的有界事件输入接口。

## 9. 复现入口

在 WSL Ubuntu-18.04 中，`tests/run_release_matrix.py` 用原矩阵串行构建并回放 86 + 18 + 14 对及六对性能采样。参数为全新 `--output` 目录、已验证的 1.6.4 `--baseline` 可执行文件和固定种子的 `--seed-library`；输出目录存在时停止，以保留旧证据。`tests/package_state_release.py` 归档最终构建、CTest、sanitizer 与原始日志，`tests/audit_state_release.py` 检查归档的源码、SDK、题源、可执行文件及词表换行。

本次输出为 `/tmp/rdfw-165-closure`，单元构建 `/tmp/rdfw-165-unit`，sanitizer 构建 `/tmp/rdfw-165-asan-release`。归档到本版本 `test-results/validation-20260928`；最终 audit 所有检查为 true。基线 `tests/state_invariant_tests.cpp` 与本版本同名文件字节一致，20 项全部通过。
