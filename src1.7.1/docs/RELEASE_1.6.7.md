# src1.6.7 — State Model Closure / Release Hardening

**结论：状态架构达到 freeze；本轮统一 release gate 通过，当前验证的 SDK / 平台 / 题集配置达到 release-ready。** 118/118 官方配对保持基础分、动作序列、目标数和约束数；五项官方总分差异全部属于时间奖励取整。36/36 self-pair 保持行为。现有 wall-clock deadline sensitivity 继续存在，其门控政策和搜索预算保持冻结。

基线为已验证的独立 src1.6.6，保护快照覆盖其 163 个文件。src1.6.7 位于新目录；产品变化为 CMakeLists.txt、rdfw.hpp/cpp、canonical_state.cpp、terminal_checker.cpp 和新增 state_mutation.cpp。score_evaluator、task_group_search、deadline_manager、candidate_plan、legacy_priority、parser、question_preflight 的 cpp/hpp 哈希全部保持基线值。本版按既有 planner、评分与搜索政策运行，新增状态能力限于 mutation 异常保护与纯实现优化。

## 1. Direct access closure

[完整语义复核](MUTATION_CLOSURE.md)、[逐行索引](DIRECT_ACCESS_AFTER.md) 与 [机器审计](mutation-audit.json) 覆盖本版所有产品、头文件、测试和 stub。索引包含 1640 个访问行、296 个赋值/容器操作初筛行，未分类事实写入为 0。计数包括局部结果、声明、fixture 和代码注释附近访问；别名 erase 的归属由语义复核表补充。

| 剩余 direct accesses | 为什么安全 |
|---|---|
| private StageStateValue、Robot slot 原语、provenance / Source / Verified / dependency / support 写入 | 属于 canonical mutation 实现；staging 必须在 active StateMutation 中；可写 provenance 引用先触发局部保存，commit 同步 mirror |
| 容器成员的插入、erase、DeleteObjectInside | 改写 owning container 前保存成员列表；与 inside 和 provenance 在同一异常边界 |
| 初始化、类型替换、capacity、ParseEnv、Fini | construction / teardown；运行期容量 reserve 全部完成后才 resize，默认值不给事实资格 |
| 原 projection snapshot / restore、局部 journal rollback | 恢复 claims、resolved、revision、依赖、支持、成员和兼容数组；使用 noexcept move/swap |
| on、must-near component/lock、路线/风险/任务缓存 | planning hypothesis / cache；默认 terminal、完成判定和 zero-action 通过 canonical API，on 仍由 location/inside/storage 表达 |
| 显式 planning hypothesis、序列化/debug、测试人工故障与压力 fixture | 角色明确；fixture/stub 不进入比赛二进制，debug 编码和查询不改变事实 |

公共 legacy 字段保留；freeze 的对象是事实权威、API 语义和生产调用边界。静态索引与当前代码的人工 alias review 共同构成写入闭环。

## 2. Mutation 的失败与异常一致性

普通 evidence、inside/location/container、slot、Sense、relation、ParseInfo 与 constraint correction 使用嵌套共享的局部 journal。它保存首次触及的对象/成员/provenance；槽位、sensed cache 与 ledger 按需保存。正常返回提交，异常展开恢复。support push_back、成员插入、容量准备与复合 relation 写入的分配失败均有 regression。

真实动作在调用 SDK 前准备相关状态。明确 false 返回保留原事实；平台调用异常或成功后的内部更新异常，恢复内部结构并撤销受影响事实与槽位的资格，增加 revision，清除相关旧 Sense 记录，将 constraint credit 降为 uncertain。canonical 随后返回 UNKNOWN，避免旧状态继续作为已证事实。shadow 路径恢复完整原快照。已尝试动作的成本与平台调用 bookkeeping 继续按既有政策记录。

恢复不分配内存；StateProvenance 的 nothrow move 有 compile-time assertion。allocator fault 在 stack unwinding 中持续生效。projection restore 从复制/成员重建改为 move/swap，ledger 初始化在 restore guard 建立之后执行。比赛正常 query 路径没有新增全量 consistency scan；局部 journal 只处理 touched records。原成员扫描及原 projection 全图快照保持，异常路径的 uncertainty fill 属于错误恢复。

同一 `mutation_failure_tests.cpp` 编译到原 1.6.6 与当前版：四个 before probes 都触发基线断言失败，当前都通过。它们分别证明 inside/member 分配失败、derived support 分配失败、ParseInfo 复合写入失败及 foreign storage pointer 问题。新增 28 个 failure cases 还覆盖九种动作的 false 返回及逐次分配失败、Sense、slot、location、must-in 和 projection restore。原有 state/canonical 行为断言保留。

## 3. Canonical / terminal / projection 性能

针对 1.6.6 profiling 中的重复查询，TerminalChecker 增加单次 predicate 的固定栈 PairFacts，按需复用同一 immutable claim。递归依赖资格、深度 8、revision/value、domain、互斥、support eligibility/certainty 保持。raw dynamic_cast 避免 shared_ptr 临时引用计数，leaf fast path 保留同一资格答案；signature 直接追加 snapshot 编码，restore 使用 move/swap。所有查询缓存都在单次只读调用结束时失效。

**官方六对独立 StageTiming 采样**：双方 terminal 4828 次、projection 1016 次、平台动作 190 次，动作序列一致。

| 阶段 | 1.6.6 累计 ms | 1.6.7 累计 ms | 平均 μs，before → after | 最大单次 μs |
|---|---:|---:|---:|---:|
| canonical query | 44.105 | 13.806 | 0.02381 → 0.02361 | 53 → 70 |
| terminal | 111.186 | 63.420 | 23.03 → 13.14 | 162 → 83 |
| projection | 148.488 | 101.997 | 146.15 → 100.39 | 436 → 323 |
| state_update metadata | 0.503 | 0.557 | 0.03031 → 0.03356 | 40 → 4 |
| derived invalidation | 0.290 | 0.386 | 0.06872 → 0.09147 | 8 → 11 |

query 次数 1,852,448 → 584,762，减少 68.4%；query 总计时减少 68.7%，主要来自消除重复调用。terminal 总耗时减少 43.0%，projection 减少 31.3%。平台调用累计 18,435.386 → 18,473.824 ms，其波动远大于单次 query。各阶段计时 inclusive，不能相加；StageTiming 自身有计时开销，state_update 只覆盖 metadata 更新，完整 mutation journal 成本体现在 projection / action 周边。

**关闭 instrumentation 的 AB/BA 微基准**：同一测试源码分别链接原 1.6.6 与本版，8/64/192 个对象，长 support list 与深度 8 链，七轮交替顺序；每轮 query 100000 次、terminal 2000 次、projection 80 次。各 workload 的结果校验和和状态快照一致。

| 对象规模 | query 中位 ns，before → after | terminal 中位 μs | projection 中位 μs |
|---:|---:|---:|---:|
| 8 | 75.11 → 73.27 | 5.418 → 2.488 | 46.249 → 31.175 |
| 64 | 98.60 → 98.17 | 57.177 → 24.725 | 269.771 → 134.157 |
| 192 | 208.46 → 208.98 | 299.473 → 119.392 | 1367.810 → 604.743 |

独立 query 每次分配为 0，单次成本基本持平；收益集中于重复资格查询和 terminal/projection 复用。terminal 的每次分配为 25→25、193→193、581→577；projection 为约 328→329、1326→1327、3742→3727。局部异常保护保留必要快照分配，小规模并未减少 allocation。长支持列表的查询成本随支持数量增长，当前语义继续逐项核验。

原始数字与范围见 `micro-profile.json`、`micro-performance-summary.json`、`official-performance-summary.json` 和两个 raw evidence archives。query 最大值 70 μs 是本轮观测值；该采样不提供最坏执行时间保证。

## 4. Deadline sensitivity 与调度控制

两版同一 boundary test 各通过 73 个断言。测试使用 elapsed=0 的未启动 DeadlineManager，精确覆盖 0/1/50/99/100/299/399/400/401/5000 ms、六种 plan duration 的阈值 ±2 ms，以及 incomplete projection 拒绝。100 ms 动作加 300 ms safety 时，400 ms 恰好通过、399 ms 拒绝。短预算 preview 保持完整 100 ms 投影，实际执行仍由原门控拒绝。

**Deadline-sensitive 政策继续存在。** complete projection gating、300 ms safety、5000 ms 平台期限和搜索 CPU 预算都未改。实际 budget 来自 wall clock，跨临界区可以改变尾部动作。本轮正式 118 对和 36 个同二进制 controls 没有出现这种动作变化；同二进制仍有可测时间波动与取整分差。

06 IT 的正式 full pair 双方均为基础分 298、44 步、官方目标 9、约束 3；都在 complete-plan stop gate 停止。当前版结束日志 remaining=686 ms，与 420+300=720 ms 的候选需求保持同一拒绝侧。这里用于诊断既有边界，产品代码没有题号判断或针对题源的参数。

| self-pair 样本，各版每题每模式 6 次 | 1.6.6 时间范围 s | 1.6.7 时间范围 s | 基础分 |
|---|---:|---:|---:|
| 03 IT | 0.185–0.200 | 0.183–0.195 | 334 |
| 03 NT | 0.188–0.197 | 0.183–0.197 | 334 |
| 06 IT | 4.301–4.340 | 4.301–4.312 | 298 |
| 06 NT | 4.311–4.338 | 4.294–4.332 | 298 |
| 29 IT | 4.762–4.790 | 4.763–4.792 | 856 |
| 29 NT | 4.764–4.798 | 4.763–4.799 | 856 |

纯 CPU 微基准隔离 canonical 实现成本；self-pair 固定同一二进制，显示平台/运行时调度波动；官方正式配对观察最终行为。这三层证据区分了实现开销与 baseline 自身 wall-clock nondeterminism。本轮原 1.6.6 controls 的行为 nondeterminism 为 0，时间 nondeterminism 仍可见；历史 1.6.6 报告中原 1.6.5 的尾部变化证据继续完整保留。有限重复次数不能排除未采样的 deadline 临界行为。

## 5. 每个官方 regression 差异的分类

正式 118 对由 full 86、三轮 target 各 6、guarded off 14 组成。236 次运行 valid、seed confirmed，硬超时和动作成本不匹配均为 0。118/118 的基础分、动作、目标数和约束数一致。

SDK 时间奖励公式为 `2 * int((5 - platform_seconds) * 10)`；以下五项均用保存的 platform_seconds 精确核对。

| 套件 / 题 / 模式 | 基础分 | 官方分 before → after | 时间 s | 分类 |
|---|---:|---:|---|---|
| full / N06 / Stage 2 IT | 80 | 180 → 178 | 0.000 → 0.001 | score quantization，bonus 100→98 |
| full / 29 / Stage 2 IT | 856 | 858 → 860 | 4.801 → 4.795 | score quantization，bonus 2→4 |
| target r1 / 06 / Stage 2 NT | 298 | 310 → 312 | 4.325 → 4.299 | score quantization，bonus 12→14 |
| target r3 / 29 / Stage 2 IT | 856 | 858 → 860 | 4.808 → 4.755 | score quantization，bonus 2→4 |
| target r3 / 29 / Stage 2 NT | 856 | 858 → 860 | 4.806 → 4.784 | score quantization，bonus 2→4 |

分类总计：semantic 0；timing 导致的动作/基础分差异 0；score quantization 5；baseline nondeterminism 导致的行为差异 0。另 current self-pair r1 / 06 NT 的官方分 310→312、时间 4.317→4.294 s，同样属于取整；它的两侧是同一二进制，行为一致。所有差异的完整行在 `difference-classification.json`，没有以重跑替换原 pair。

P10 IT/NT 双方继续为基础分 184、官方分 268、目标 5、约束 0、成本 16，保持既有 canonical 支持失效修复。

## 6. Release gate、哈希和证据

| Gate | 最终结果 |
|---|---:|
| CTest，含官方评分语义 | 126/126 |
| Debug ASan + UBSan，leak detection / halt_on_error | 125/125 |
| 原 state invariant / state layer | 20/20 + 19/19 |
| canonical / 原 semantic regressions | 33/33 + 14/14 |
| 新 mutation failure / exact deadline | 28/28 + 1/1（73 assertions） |
| 未修改 1.6.6 before probes | 4/4 预期断言失败，当前同源码通过 |
| 官方 paired regression | 118/118 行为一致 |
| 独立 performance paired / self-pair controls | 6 对 / 36 对，行为一致 |
| source / build / baseline / SDK / problem / seed audit | 全部 true |

运行环境为 WSL Ubuntu-18.04、g++ 7.5.0、CMake 3.10、同一 `/home/yifan/env-release-2026`。sanitizer 不链接未插桩的外部 libasp，因此少一项；SDK 评分语义由普通构建单独验证。`input-audit.json` 固定全部 884 个 SDK 文件的 SHA-256，末尾复核完整树未变；同时核对已验证 1.6.6 binary、当前 build source 与 binary、全部 118 official + 36 control 题源、固定种子库与词表 LF。

统一入口为 `tests/run_closure_gate.py`；本轮 output 为 `/tmp/rdfw-167-final-gate`，命令、构建和计时记录归档。`test-results/validation-20260928` 含 `audit.json`、`manifest.json`、各套 results/summary、差异分类、微基准、self controls、source.diff、发布 ELF 二进制及完整日志/answer archives。先前开发轮因补齐外部动作异常处理而中止，原始 partial pairs、build/binary 与日志保存在 `development-gate-interrupted-evidence.zip`，单独标明原因和范围。

## 7. Freeze / release-ready 判定

**State architecture freeze：达到。** 生产事实写入归入 canonical mutation，保留 direct access 均分类；query 权威、资格语义和支持模型闭环；失败/异常测试证明同步结构、provenance 与 mirror 的一致性。

**Release-ready：达到本轮验证配置的发布条件。** 普通、sanitizer、before/after regression、官方矩阵、timing controls 与 hash audit 全部通过；实现优化减少 terminal/projection 开销，正式配对无 semantic 或动作变化。保留的运行属性是既有 wall-clock deadline sensitivity，按原完整投影和安全余量政策执行；它不影响本轮状态架构冻结判断。

本版没有增加概率模型、多假设、source weighting、完整 dependency graph、event sourcing 或 planner redesign。局部 journal 只用于瞬时异常恢复，存续于本次 mutation。旧版本、SDK 与题源保持原字节，全程没有批量删除。
