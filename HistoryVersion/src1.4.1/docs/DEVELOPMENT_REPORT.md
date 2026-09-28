# src1.4.1 开发报告

基于当前 `src1.4`，本轮只处理事实证据来源与执行后的目标回收。审计了 `DESIGN.md`、`SCORE_REPORT.md`、`STRATEGY_REPORT.md` 和现行代码；后两份报告中的 04 故障属于更早版本。实际 `src1.4` 已有 04 的 6/6、2/2，也已消除柜门的重复 Close/Sense。本版保持这一结果，并补齐通用语义。

## 1. 真实根因

- 世界事实值分别存在对象的 `location`、`inside`、`isOpen`，可信性由三个 `...Verified` 数组表示。原先没有与每个事实对应的来源记录，约束修正、Sense、动作反馈和 AskLoc 的强弱关系只能靠调用处零散判断。
- `TerminalChecker` 按事实值及 `Verified` 判断 Stage 2 终态，`ZeroActionPreCheck` 使用这个结果；`SolveTask` 内又有局部完成判断。来源缺失使状态修正与后续验证的理由难以追踪，也容易把弱推断或 Ask 回答当作已验证事实。
- `UpdateTaskList`、成功/失败路径和 MultiGoto 会修改 `isEnable`；风险值留在任务上。旧候选只在阶段入口重新构建，且会先按 `isEnable` 过滤。旧列表为空时 `StopGate` 可能结束后续阶段，所以终态变化后仍有收益的任务可能没有再次进入候选扫描。
- 当前 `src1.4` 的 04 已通过可靠 must-closed 修正、零动作完成和既有 goto 路径解决了报告中的具体动作问题。本轮没有把题号或对象当作特殊情况。

## 2. 修改文件与核心数据流

- `rdfw.hpp/.cpp`：新增每对象三个事实来源数组，与三个 `Verified` 标志并行；在初始环境、显式 info、约束修正、Sense、动作成功/失败和 AskLoc 的状态写入点同步更新。dry-run 保存并恢复来源、世界修订号及失败修订号；真实动作和接受的观察/回答更新世界修订号。
- `rdfw.cpp`：`RefreshTaskStates` 读取当前 `TerminalChecker` 结果，将未完成且不在当前修订号失败的旧 disabled 任务重新启用；`EvaluateShadowCandidates` 重新计算风险并重建 CandidatePlan。计划结束后刷新任务状态；`StopGate` 遇到旧列表无可执行项时，全量重扫全部目标（包括 goto），不以旧列表直接锁死正常停止。MultiGoto 后另执行有限次 `ExecuteTerminalRecovery`：只选当前合法、dry-run 完成、期限内且边际基础分为正的计划；每轮执行后再评估终态。
- `tests/recovery_evidence_tests.cpp`：增加 A～F 的定向回归；`tests/CMakeLists.txt` 注册到 CTest；顶层 `CMakeLists.txt` 更新测试选项说明。

## 3. 当前 provenance / evidence 语义

每类事实同时记录**值、来源、是否足以用于 Stage 2 终态判定**。来源包括 `UNKNOWN`、`INITIAL`、`EXPLICIT_INFO`、`CONSTRAINT_DERIVED`、`CONSTRAINT_HEURISTIC`、`SENSE`、`ACTION_SUCCESS`、`ACTION_FAILURE`、`ASK_ANSWER`。Stage 1 初值可验证；Stage 2 初值仍是弱证据。可靠的 must-closed / must-inside 和有可信锚点的 must-near 推导可验证；依赖未验证位置的传播仅记为 heuristic，不升级为 Sense 强度。直接 Sense、成功动作及可确证的失败反馈可以验证其实际证明的事实；AskLoc 回答保持弱证据，不能覆盖已有可信事实。来源用于审计，`Verified` 决定 Stage 2 的已满足/zero-action 判断。事实值满足但证据不足仍是 UNKNOWN。

## 4. Candidate reactivation 与 Stop

动作或感知改变世界时增加 `world_revision`；CandidatePlan 结束后刷新任务，阶段扫描和最终扫描重新计算风险、资格、动作成本与边际分。失败任务只在同一修订号暂不重试，世界变化后可以回收。终态已自动满足的目标直接跳过，无需生成物理动作。Stop 前重新扫描未完成目标；最终回收只在确有合法、正收益、可在期限内完成的计划时执行。已满足的全部目标或期限到达仍会正常停止。

## 5. 回归结果

2026 官方 SDK，Ubuntu 18.04，5000 ms；01～06 各运行 IT/NT 一次，共 12 次有效。表中为 `src1.4 → src1.4.1`，列出的目标、约束、动作数、动作成本、内部基础分和官方基础分在 IT/NT 相同。官方基础分按官方目标/约束得分扣除动作成本，时间奖励未计入。

| 题 | Goals | Constraints | 动作数 | 动作成本 | 内部基础分 | 官方基础分 |
|---|---|---|---:|---:|---:|---:|
| 01 | 7/7 → 7/7 | 0/0 → 0/0 | 16 → 16 | 48 → 48 | 232 → 232 | 232 → 232 |
| 02 | 9/9 → 9/9 | 0/0 → 0/0 | 16 → 16 | 48 → 48 | 312 → 312 | 312 → 312 |
| 03 | 7/7 → 7/7 | 2/2 → 2/2 | 9 → 9 | 25 → 25 | 295 → 295 | 295 → 295 |
| 04 | 6/6 → 6/6 | 2/2 → 2/2 | 15 → 15 | 40 → 40 | 240 → 240 | 240 → 240 |
| 05 | 6/6 → 6/6 | 0/1 → 0/1 | 10 → 10 | 20 → 20 | 220 → 220 | 220 → 220 |
| 06 | 5/6 → 5/6 | 3/3 → 3/3 | 7 → 7 | 20 → 20 | 240 → 240 | 240 → 240 |

官方 12 次动作与反馈序列均和 `src1.4` 逐项一致。03 的 Sense 也仍在，弱/冲突证据没有造成提前完成。05 的约束计分资格没有恢复。

## 6. 04 完整动作序列

`src1.4` 与 `src1.4.1` 相同：

`PickUp(6) → Move(4) → PutDown(6) → Open(4) → PickUp(6) → PutIn(6,4) → Move(2) → PickUp(7) → Move(4) → PutIn(7,4) → Move(2) → PickUp(8) → Move(4) → PutIn(8,4) → Close(4)`

15 个动作均成功。结束时机器人位于 microwave 所在位置，goto 自动满足；cupboard.closed 来自可靠约束推导，未出现 `Move(3) → Close(3)[false] → Sense`。04 在当前基线已达到目标，因此新回收路径由定向测试验证，而没有人为改变此题动作流。

## 7. 新增测试与剩余问题

`recovery_evidence_tests` 覆盖：A 可靠 constraint-derived fact 可用于任务判断且不会顺带强信任未验证位置；B zero-action completion；C 冲突/弱推断不触发零动作；D 世界变化后旧 disabled/高风险 goto 可重新评估并执行；E StopGate 前全量重扫；F 已完成目标不产生动作。另验证显式 info 的来源与可信度。CTest 5/5 通过；正式客户端编译通过。

六题没有内部与官方基础分差异。06 仍保留原有高风险 give 的收益取舍，03 仍保留必要 Sense。最终回收只处理单个正收益 CandidatePlan，不求解需先做负收益动作的组合任务；更大题库尚未验证。本轮没有启动概率模型、Bayesian 或任务组调度。

完整数据：`test-results/liuyifan1.0-src1.4.1-verified-20260924/comparison.csv`、`trace_comparison.json`；04/05 的客户端、服务端与官方评测日志在各题 IT/NT 目录。

