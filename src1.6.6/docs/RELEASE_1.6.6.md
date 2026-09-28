# src1.6.6 — Canonical State / Compatibility View Convergence

基线为已完成并验证的 `src1.6.5`，本版位于独立目录。事实资格和值统一从 canonical query 获得，旧对象字段继续供规划使用。最终 97/97 CTest、96/96 ASan + UBSan 通过；官方 118 对中 117 对保持基础分、动作序列和目标数，约束数 118/118 相同。一对 06 IT 的时间门控尾部差异保留并调查，P10 IT/NT 保持 1.6.5 的修复行为。结论为 **B：canonical state 已基本收敛，可以进入 src1.6.7 State Model Closure / Release Hardening**，行为冻结仍需处理时间敏感风险。

## 1. 1.6.5 的双写状态现状

1.6.5 已将初始、Ask、Sense、动作反馈和约束推导记录为 `StateProvenance`，并以 `ResolvedState/DependenciesCurrent` 区分证据、事实和派生状态。但旧 `location/inside/isOpen/hold_id/plate_id` 仍是规划器实际使用的候选值；Source/Verified 数组与 provenance 同时存在。部分调用者先查询旧资格，再读取旧值，或直接通过字段相等判定任务完成，因而可能在 resolved UNKNOWN、弱冲突或支持失效时绕过新状态语义。

本版明确三种角色：provenance 是事实解析权威；对象字段是规划假设/关系缓存；Source/Verified 是 resolved 元数据镜像。raw verified=true 不等于当前依赖有效，旧字段保留值也不等于世界事实成立。

## 2. 全仓 direct-access audit

产品修改前已完成 [逐行 BEFORE 索引](DIRECT_ACCESS_BEFORE.md) 和 [人工语义复核](CANONICAL_AUDIT_REVIEW.md)，覆盖产品、声明、测试，以及 TerminalChecker、solver、binding、约束评估、guarded、投影和动作输入。完成后重新生成 [AFTER 索引](DIRECT_ACCESS_AFTER.md)，并按实际调用上下文复核 [最终审计表](CANONICAL_AUDIT_FINAL.md)。BEFORE 索引 1261 行，最终 AFTER 索引 1407 行；新增 API、快照和故障测试使访问行数增加，行数不是收敛指标。

逐行索引按函数定义和函数体范围追踪访问，safe/modify 为初筛；同一函数可混合多类访问，仍需按上下文复核。两个人工复核表明确区分 A 规划假设、B 事实查询、C 状态写入和 D 保存/恢复/debug，发布判断以实际语义复核为准。剩余旧字段访问的用途见第 14 节。

## 3. 曾绕过 canonical truth 的路径

| 原路径 | 错误模式 | 本版处理 |
|---|---|---|
| TerminalChecker / legacy 默认评估 | 资格通过后继续读旧字段，值可与 resolved 不同 | 资格和值由 Fact* 一次统一取得 |
| IsLocationVerified / IsInsideVerified / IsContainerStateVerified | 并行 verified 与依赖检查未完全覆盖 resolved UNKNOWN、heuristic | 兼容接口直接委托 ResolvedState |
| Give / TakeOut / pickup / putdown 等提前返回 | 同地、旧 outside、旧槽位直接宣布完成 | TaskFactSatisfied 和 canonical storage/inside/location |
| must-near direct anchor、已知事实保护 | 旧位置配合旧 verified 影响事实推导或覆盖保护 | FactLocation / FactInside；候选投票仍保留 |
| 第二条 Sense、Goto 的容器内容传播 | 关系推导缺少 inside/容器位置支持 | 保存两个依赖，支持资格失效即拒绝 |
| weak initial storage 后 Move | 成功移动把未经验证的携带关系升级为物体位置事实 | 物体位置作为 relation derived，依赖 canonical 槽位和机器人位置 |
| must-in、ParseInfo on/near/inside 的传播 | canonical 来源已知，仍复制可能不同的旧规划位置 | 已知来源值优先 FactLocation；UNKNOWN 才用候选并保持弱资格 |
| 容器成员缓存的传播 | 只确认 inside 已知，未确认其 canonical 值指向当前容器 | FactInside(item)==container 才允许传播事实 |
| mutation、Fini、not-inside 清除 | 字段、元数据或槽位 provenance 只更新一侧 | 包装同步、清除元数据、重置槽位记录 |

路线尝试、容量判断和动作反馈成功仍按原政策执行；它们不独立证明零动作世界事实。

## 4. Canonical query layer

数据流为：

`Evidence → StateProvenance → ResolutionEligible + DependenciesCurrent → ResolvedState → Fact* → Terminal / solver / anchor / projection evidence`。

最小 API 在 `rdfw.hpp` 与新增 `canonical_state.cpp`：`FactValue`、`FactLocation`、`FactInside`、`FactContainerState`、`IsStoredFact`、`IsNotStoredFact`、`TaskFactSatisfied`。旧 Is*Verified 接口只保留兼容适配，不读取并行数组决定事实资格。

ResolutionEligible 拒绝无效字段/对象、状态域错误、未验证、UNKNOWN、UNKNOWN source、CONSTRAINT_HEURISTIC，以及局部 hold/plate/inside 互斥冲突。DependenciesCurrent 检查已记录支持约束是否仍存在、eligible/certain，依赖 revision/value 是否一致，并要求支持本身通过同一个 ResolutionEligible；最多两个事实依赖、递归深度上限 8。调用方不再拼接 Verified、Source 和依赖资格。

弱冲突可以保留旧规划候选，但 resolved UNKNOWN。历史冲突 claim 不被丢弃；新的强 Sense/成功动作可证明新时刻状态，不能因为过去值不同永久拒绝当前观察。查询不改对象、provenance、revision、支持或 ledger；只在显式计时模式累计性能计数，测试 23 核对 1000 次查询后状态快照不变。

Stage 1 的官方 ASP `at` 不等于 inside 传播出的物理位置，`ScoreFactLocation` 保留既有评分表达并先检查 canonical location。测试 28 防止 resolved UNKNOWN 从 `score_locations` 重新取得资格。评分公式和存放谓词口径未改变。

## 5. Mutation 收敛

`ApplyStateValue` 收敛普通 location、inside、container value 写入；inside 写入同时维护容器成员缓存。`MarkDirectLocationEvidence/SetInsideEvidence/SetContainerEvidence → UpdateProvenance` 更新 claim、resolved、revision 和兼容镜像，再由关系/约束包装附加依赖和支持。`MarkUnresolved` 降级元数据和镜像，但保留可用于规划的旧字段。

`SetHold/SetPlate` 包装 Robot 的兼容字段转换，同步槽位 provenance、物体 inside/location 和成员缓存。Move 更新机器人 canonical location；携带物体的位置传播由 canonical 槽位强度和两个依赖决定。两条 Sense、parse、约束修正和动作包装使用这些路径，not-inside 清除与 Fini 不再留下旧事实资格。

依赖资格不能纠正一个从错误候选值复制出的结论。因此 parse/:info/must-in 的关系位置传播在来源有事实时直接取 FactLocation；容器缓存内容传播必须确认 FactInside 的值恰好等于该容器。未知来源仍可提供规划候选，但不能用旧值配合 canonical 资格授予事实。

内部仍有先写字段、再标记证据的短暂 staging，这是现有动作/解析实现的兼容收敛；期间不调用终态评估。没有重写所有对象类、完整依赖图或事件历史。

## 6. Compatibility view 当前角色

旧 location/inside/isOpen/hold/plate 服务路线、候选、风险、shadow 动作预测及序列化。Source/Verified 镜像 resolved metadata，不是当前依赖资格缓存。inferred-by-must-near 标记用于候选传播和排除派生 anchor，不赋予事实强度。头文件明确这些边界，保留旧接口避免破坏 planner。

原 Plan/ShouldStartConstraintTrade 曾通过临时 stage=1 读取候选。本版将它们改为显式 planning hypothesis 入口，保留原奖励探测和 conservativeScore 政策，不再临时改变事实资格规则。TerminalChecker 默认入口及 LegacyPriorityChecker 默认入口均读取 canonical；假设入口只用于这两个规划探测。

## 7. Debug invariant / consistency

新增 `DebugStateConsistency` 检测 resolved/旧值不一致、镜像冲突、非法事实/依赖边界、槽位指针、互斥槽位、stored/inside/location 关系及容器成员缓存。人工破坏 verified、位置或槽位可以被检测。resolved UNKNOWN、失效依赖、非法状态域不能通过 query，测试分别验证。

`DebugStateSnapshot` 编码规划字段、两条 claim、resolved/source/verified、revision、依赖字段/对象/值/revision、支持索引和列表、Source/Verified、inferred 标记、成员缓存、槽位/指针、评分位置及约束资格。没有在正式比赛关键路径调用全量一致性扫描；可在测试主动调用。

## 8. 找到并修复的真实 bug

`tests/canonical_baseline_probe.cpp` 用同一测试源码分别编译未修改的 1.6.5 与当前版本。14 项在基线均触发预期断言失败，当前均通过，原始 before/after 日志归档。这些测试证明修复来自状态语义，不以官方分数提高作为理由。

| Probe | 最小问题 |
|---:|---|
| 0 | MarkUnresolved 后旧 IsLocationVerified 仍为 true |
| 1 | resolved location=5、旧 location=1 时 Terminal goto 错判同地完成 |
| 2 | Stage 2 弱同地 Give 零动作返回成功 |
| 3 | opposing putin 任务使弱 outside 的 TakeOut 提前完成 |
| 4 | SetHold 更新字段但物体 inside/location 元数据未同步 |
| 5 | not-inside 修正清除字段却留下旧 inside 资格 |
| 6 | 第二条 Sense 的内容位置未依赖失效的 inside 支持 |
| 7 | Fini 留下 HOLD provenance |
| 8 | weak initial held 经 Move 被升级为位置事实 |
| 9 | CONSTRAINT_HEURISTIC 可被误标为 verified fact |
| 10 | must-in 的来源 resolved=5、旧候选=1，错误派生出位置事实 1 |
| 11 | Stage 1 ParseInfo(on) 同样将旧候选复制为强事实 |
| 12 | stale 容器成员缓存配合已知但不同的 inside 值，传播错误位置事实 |
| 13 | inside 目标是 human 而非 container，仍通过旧 ResolvedState |

其他新增测试覆盖依赖支持自身无资格、支持约束移除、无效状态域、互斥槽位、score_locations 旁路及只读性。

## 9. 新增测试和既有测试保留

新增 29 个 `canonical_state_0..28` 与上述 10 个 `canonical_regression_0..9`。用户要求的覆盖关系如下：

| 要求 | canonical case |
|---|---|
| 旧 location 有值但 resolved UNKNOWN | 0、28 |
| stale derived 旧值、过期支持约束 | 1、2、24 |
| 假设仍可规划但不能成为 terminal fact | 3、12 |
| mutation 同步值、镜像与元数据 | 4、6、19、20 |
| query 与旧字段分离 | 5、12 |
| hold/plate/inside 一致及互斥 | 6、25、26 |
| opened/closed UNKNOWN | 7 |
| 弱冲突与新观察解析 | 8 |
| real vs shadow 动作序列、CandidatePlan | 9、10 |
| restore 的 revision、依赖、支持列表 | 10、11，完整快照比较 |
| solver early return | 13、16、17 |
| 静态 binding 不把失效 derived 当事实 | 14 |
| debug 检测人工不一致 | 5、15、26 |
| Sense 依赖传播、支持本身资格 | 18、21、27 |
| heuristic 拒绝和 query 只读 | 22、23 |
| 派生值必须取 canonical 来源 | 29、30，覆盖 must-in 和 :info on/near/inside |
| 缓存不能覆盖 canonical inside、非法 inside 目标 | 31、32 |

real/shadow 的 10 步为 Open、TakeOut、ToPlate、Move、FromPlate、PutDown、PickUp、Move、PutIn、Close，每步比较全量状态。real 侧使用测试平台 stub 的成功反馈，shadow 侧不调用平台；另由官方语义测试和官方矩阵验证真实 SDK 行为。CandidatePlan 在投影后恢复原快照，真实 solver 执行结果与投影终态相同。

原 20 个 state invariant 的行为断言保留；13/14 号 fixture 原先只写 raw Verified/inside，迁移为证据 API setup。原 19 个 state layer 保留。three_a、recovery、interval、score_semantics 中同类 fixture setup 同步迁移，行为/评分断言未放宽；详见 `fixture-migration.diff`。binding 只根据静态属性产生候选，没有新增动态位置筛选或改变候选顺序。

## 10. CTest / sanitizer / 官方评分语义

环境为 WSL Ubuntu-18.04、g++ 7.5.0、CMake 3.10、同一官方 `/home/yifan/env-release-2026`。断言测试使用 `-UNDEBUG`；sanitizer 为 Debug、非 PIE，启用 ASan leak detection 与 UBSan halt_on_error。

| 项目 | 最终结果 |
|---|---:|
| 全部 CTest，含官方评分语义 | 97/97，0.39 s |
| ASan + UBSan | 96/96，1.87 s |
| 原 20 state invariant | 20/20 |
| 原 19 state layer | 19/19 |
| 新 canonical / before-after regression | 33/33 + 14/14 |
| 未改动 1.6.5 的最小 before probes | 14/14 预期断言失败 |

sanitizer 不链接未插桩的外部官方评分库，因此少一个 CTest；官方评分语义单独在普通构建中通过，使用 SDK 原评分器。before probes 的失败是修复前证据，不属于当前版本验收失败。

## 11. 118 对官方 regression

只采用最终 `/tmp/rdfw-166-final/build-release/build.json` 对应产品源码，固定种子 20260924，与已验证 1.6.5 二进制串行配对。同 SDK、题源、词表、5000 ms 期限。正式配对关闭 StageTiming，性能采样另行启用。

| 套件 | 对数 | 同基础分 / 动作 / 目标 / 约束 | 官方总分差异 |
|---|---:|---:|---:|
| 原全量 | 86 | 基础分/动作/目标 85/86；约束 86/86 | 5 |
| 03/06/29 IT/NT 第 1 轮 | 6 | 6/6 | 1 |
| 第 2 轮 | 6 | 6/6 | 0 |
| 第 3 轮 | 6 | 6/6 | 0 |
| guarded off | 14 | 14/14 | 0 |
| 合计 | 118 | 基础分/动作/目标 117/118；约束 118/118 | 6 |

236/236 次运行有效且成本核对通过；invalid、硬超时和动作成本不匹配均为 0。另运行六对性能采样及三对未改动基线自配对，不计入 118 对。

其中 5 对官方原始总分仅相差 2 分：全量 N06 Stage 2 IT、N07 Stage 1 IT/NT 均为 180→178；全量 real 06 NT 和定向第 1 轮 real 06 IT 均为 312→310。SDK `evaluate.cpp:1948-1949` 使用 `2 * int((5-time)*10)` 时间奖励；逐对用记录的 platform_seconds 验算，均精确解释，见 `official-time-differences.json`。第六对为下述有动作/基础分差异的 06 IT，不能归为单纯总分取整。

**保留的行为差异：全量 real 06 IT。** 共同动作前缀 44 步；基线额外执行 `Move(8), PickUp(20), Move(3), PutDown(20)`，目标 10→9、基础分 326→298、动作成本 134→122、官方分 332→310、运行 4.651→4.317 s。双方仍保留 3 条官方约束。新版最后的候选预计 420 ms，加既有 300 ms 安全余量需 720 ms，日志只剩 686 ms，原完整计划门控因此停止；基线完成一个额外任务后也因同一门控停止。没有修改 deadline、余量或门控。

同一 SHA-256 的未改动基线在三轮定向和性能采样中均为 298，新版也均为 298；额外三个自配对将两侧都设为同一个基线二进制，六次运行全部为 298、相同 44 步。这证明固定种子不固定 wall clock，基线自身也存在尾部变化。题 06 没有容器/inside/:info，新增加的传播修复不在其输入路径中；差异发生在共同动作前缀之后的时间资格，而非位置/inside 取值分歧。

这是时间敏感诊断，无法从该样本严格分离新增查询开销和平台调度波动；不把它当作 canonical 语义修复接受，也不替换原始配对凑成 118/118。基线原有时间敏感性和本版开销一起列为 release hardening 风险。`behavior-differences.json`、`deadline-variation.json`、`deadline-self-r*-results.json` 及对应原始日志保存完整证据；`investigate_deadline_variation.py` 可串行复现自配对。

各套 `*-results.json` 保存逐题分数、动作、计数、耗时和 SHA-256；`*-summary.json` 保存差异清单；`*-evidence.zip` 保留 server/client 日志和 answer set。开发中未完成或被中止的输出没有纳入发布证据。

## 12. P10 IT/NT

两种模式的 1.6.5 和 1.6.6 均为基础分 184、官方分 268、目标数 5、约束数 0、动作成本 16。动作均为：

`PickUp(4) → Move(3) → Sense → PutDown(4) → PickUp(5) → Sense → AskLoc(2) → AskLoc(2)`。

失去确定约束支持的桌子位置没有因旧字段残留重新成为事实。保持 1.6.5 的 canonical 修复，未退回 1.6.4 的错误 PutOn 同地提前返回。新测试 1/2/14/18/24 同时覆盖同类支持失效和终态拒绝。

## 13. 性能影响

对 03/06/29 IT/NT 六对独立采样，投影次数 1091→1016，terminal 次数 5166→4828，实际平台动作次数双方均为 190。原搜索使用 wall-clock 预算，查询开销和调度会改变预算内完成的投影数量；搜索策略未改。query 检查对象和已记录依赖/支持，没有每次遍历所有对象、扫描全部约束、复制完整证据历史或重建兼容视图。最多两个事实依赖、深度 8；支持列表为本题有界索引，查询成本还随该列表长度变化。

| 阶段 | 1.6.5 累计 ms | 1.6.6 累计 ms | 最大单次 μs，旧→新 |
|---|---:|---:|---:|
| terminal | 50.821 | 107.185 | 60→267 |
| projection | 84.026 | 142.502 | 320→431 |
| state_update | 0.336 | 0.427 | 0→6 |
| derived_invalidation | 0.319 | 0.312 | 5→8 |
| canonical_query | 未单独计时 | 42.665 | 新版 203 |

新版 canonical query 1,852,448 次，平均约 0.023 μs；state_update 16,596 次，平均约 0.026 μs；derived_invalidation 4220 次，平均约 0.074 μs。计时在纳秒累积，按每次运行输出整数微秒；零最大值表示低于输出分辨率。state_update 仅覆盖元数据写入，不代表完整动作/关系处理成本。最大 query 为 203 μs，不能把平均值解释成最坏延迟保证。

按单次平均计算，terminal 约 9.84→22.20 μs（2.26 倍），projection 约 77.02→140.26 μs（1.82 倍）；统一资格检查和包含 canonical metadata 的签名增加了工作。累计 terminal/projection 多约 56.4/58.5 ms，分布在六次运行中，且调用数量不同；阶段是 inclusive，不能相加为总额。性能采样双方动作相同、无硬超时，但全量另有 06 IT 时间边界差异，不能据此宣称性能无影响或总体提速。最大 projection 431 μs，当前局部 query 平均保持轻量；1.6.7 应继续监控大任务/长支持列表、签名分配和时间门控，优化必须保留 canonical 语义。原始数据为 `perf-target-performance-summary.json`。

## 14. 剩余 direct access

剩余访问均有明确用途：A 路线/风险/候选、显式规划假设和 dry-run 预测；C 初始化、解析、证据/动作包装、关系转换的实现；D 快照、恢复、输出、debug 和人工故障 fixture。默认 TerminalChecker、约束谓词、任务完成、零动作返回、guarded 使用的 terminal/evidence 及事实 anchor 均走 canonical。

动态事实不参与静态 binding 筛选：绑定候选仍可具有 UNKNOWN 位置，随后由 canonical terminal 判定，而不是将 UNKNOWN 候选删掉改变搜索政策。`on` 保留兼容注释，现有终态依旧按位置、inside、存储表达；没有新增 on 事实能力。

`score_evaluator.*`、`task_group_search.*`、`deadline_manager.*`、`candidate_plan.cpp` 保持基线字节；评分、严格区间支配、搜索/候选排序、legacy fallback 算法、5000 ms 期限、complete projection gating 未改变。产品差异完整保存在 `source.diff`，10 个产品文件变化。

## 15. 剩余双写风险

公共对象字段和 provenance 可以被外部调用者直接改写，未通过 API 的写入能构造不一致；canonical 不从旧字段补资格，debug 可发现值/镜像/关系冲突。下一版适合加强写入封装、mutation staging 的异常安全及局部断言，而非重新设计规划器。

派生支持仍保守：任一保存的支持失效就拒绝事实，不寻找替代证明；约束 ledger 尚未初始化时沿用原支持资格启动规则。支持集不是完整依赖图，claim 只保留两个不同值，不能 replay 全部历史。跨关系通用冲突解析、独立 on 模型和 dry-run 隐藏观察预测属于后续能力。没有加入 Bayesian、概率、多假设、source weighting 或 event sourcing。

## 16. 是否适合冻结状态架构

选择 **B**。当前事实消费者的合法来源已收敛到同一个 provenance/资格/依赖解析，真实故障有 before/after 证据，终态与投影一致性及既有评分边界通过测试。117 对行为相同，剩余一对保留为时间门控风险，没有当作状态语义修复接受。可以进入 `src1.6.7 State Model Closure / Release Hardening`，集中处理封装、异常安全、更广规模的性能、时间敏感性和发布检查；不需要为当前已知事实旁路继续扩展状态能力。

冻结的是事实来源和 API 语义。公共兼容字段的物理删除、完整图或概率模型不作为此次成功条件；剩余 hardening 风险也不代表旧字段获得第二种事实答案权威。

## 复现及保护检查

完整测试命令见 [README](README.md)。本次普通构建 `/tmp/rdfw-166-unit`，sanitizer `/tmp/rdfw-166-asan`，before probe `/tmp/rdfw-166-baseline-probe`，最终官方输出 `/tmp/rdfw-166-final`。归档命令：

```sh
python3 /path/to/src1.6.6/tests/package_state_release.py \
  --runs /tmp/rdfw-166-final --unit /tmp/rdfw-166-unit --asan /tmp/rdfw-166-asan \
  --unit-summary /tmp/rdfw-166-ctest.log --asan-summary /tmp/rdfw-166-asan-ctest.log
python3 /path/to/src1.6.6/tests/finalize_release_evidence.py
python3 /path/to/src1.6.6/tests/audit_state_release.py
```

发布证据在 [test-results/validation-20260928](../test-results/validation-20260928/summary.json)。`audit.json` 全部 true：产品源码与最终构建一致，基线二进制与已验证 release 一致，基线 snapshot 的 151 个文件未变，所用官方 SDK 文件与基线一致，118 对题源哈希一致，同二进制 controls 通过核对，词表 LF。未修改 src1.6.5、旧版本、官方 SDK 或原题；未进行批量删除。
