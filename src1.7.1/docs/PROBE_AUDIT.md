# src1.7.1 canonical / mutation / action authority 审计

本次产品改动集中在新增 `probe_layer.hpp/.cpp`、`rdfw.hpp` 的私有状态与接口、`rdfw.cpp` 的接入点，以及 CMake 版本/编译列表。继承产品 C++ 文件只有 `rdfw.hpp` 和 `rdfw.cpp` 改动。

## 冻结语义的证据

`test-results/validation-20261003/authority-audit-tail-final.json` 保留最终基线/当前 SHA-256 和逐函数结果。以下产品文件与 `src1.7` 字节相同：candidate_plan、canonical_state、state_mutation、deadline_manager、score_evaluator、terminal_checker、task_group_search、legacy_priority、parser 和 question_preflight 的相关 `.cpp/.hpp`。

以下函数体与基线完全相同：SelectGreedyCandidate、BuildTaskGroupPlan、CalculateTaskRisk、RefreshTaskStates、ShouldStartConstraintTrade、TryGuardedDecision、Move、SenseCurrentLocationOnly、Sense、SolveTask、ZeroActionPreCheck、ExecuteMultiGotoAggregation、UpdateConstraintLedger、ResolvedState、UpdateProvenance、ReceiveWeakClaim、ResolutionEligible、DecisionProgressSignature。

新增接入点如下：

| 位置 | 实际改动 | 权威边界 |
| --- | --- | --- |
| Plan / Fini | 重置本题 Probe 状态 | 不重置或修改既有事实语义 |
| ExecuteMainTaskLoop | 无 best 的 Stage 2 分支尝试 Probe；反馈后标记恢复/完成 | 正常 task 选择函数不变 |
| RecordAction | active Probe 的白名单、预算、状态保护 | 非 Probe 路径不进入新保护 |
| RecordActionOutcome | 记录 Probe 收到的真实反馈 | 原更新路径保持 |
| MustChooseOne | 只读 proposal 日志 | 不调用 SDK 或决定 execute/stop |

Probe 不修改 CandidatePlan 的 task eligibility，没有新的事实权威、ScoreEvaluator 参数或 guarded 搜索范围。

## 新增访问清单

`probe_layer.cpp` 对事实读取使用 FactValue / FactLocation / FactInside / FactContainerState、Provenance、DependenciesCurrent 和原终态查询。收到的弱 claim 只用于带来源的具体地点 hypothesis。

直接读取 `location` 用于 canonical 机器人位置与动作包装器镜像一致性校验；直接读取 `hold_id`、`plate_id` 用于已知 canonical storage 与 SDK 包装器镜像的保守一致性检查。这些读取不会建立或覆盖 canonical fact。对象 id、sort、type、条件、关系列表用于既有任务/约束绑定和地点线索；不会读取公共 legacy location/inside/container 字段来证明任务完成。

新文件没有 ApplyStateValue、StageStateValue、MarkDirectLocationEvidence、SetInsideEvidence、SetContainerEvidence、ReceiveWeakClaim、MutableProvenance 或 Plug 直接调用。合法 Probe 的所有物理动作和观察均由原包装器提交证据；源码中的 canonical_state / state_mutation 本次没有改动。

## 投影与异常闭合

Move 投影复用原 final-move 完整投影及 ScopeExit 快照恢复，生产 task 上下文为 -1。包装器内部自动展开的 cleanup 动作在完整投影后被拒绝；生产动作入口仍有第二层白名单阻止状态偏离后的隐藏动作。

生成/授权投影不会递归进入 Probe。专项测试对比 DebugStateSnapshot、SDK 调用数、已有 Probe history/feedback，验证普通候选、shadow continuation、Move 投影恢复没有泄漏。

明确 Move 失败保留原事实并停止；包装器抛异常时继续使用原 StateMutation 的撤销/未知化语义。Probe 外层只记录结果、释放 active pointer、恢复 task_index、丢弃当前序列，不修补事实。Sense 抛异常同样沿用原观察异常恢复，不伪造反馈。

## 执行与有界性验证

直接调用 MustChooseOne 的测试覆盖 Stage 1 和 Stage 2，SDK 调用数为零，canonical snapshot、ledger、task enable/ask 状态相同。Stage 1 和 shadow 的直接 Probe 执行入口也拒绝。

37 项 Probe 专项测试包含真实主循环的“无候选 → Probe Sense → 完整重规划 → 正常 task 执行”，以及同 signature 的不同任务/fact 列表不能绕过 retry 限制。尾部检查同时覆盖正收益单任务和只有完整聚合计划才有正收益的情形，证明 continuation 投影恢复快照且不调用 SDK。Probe 不增加 scheduler_steps；8/2/2 达到后锁定关闭，但正常 greedy 仍可执行。

完整 SDK 配对日志进一步审计执行次数、signature/revision 重复、白名单序列、constraint_safe 授权、Stage 1 零 Probe、执行前无正常候选、重规划反馈及 deadline。结果与异常记录在发布报告中给出。静态审计与专项测试用于核对修改边界；不把简单文本扫描当作通用 C++ alias-analysis 证明。

## 内存检查构建记录

普通验证为 Release、本地桩和官方 SDK 语义测试，共 183 项。ASan/UBSan 为 Debug、本地可插桩测试，共 182 项；官方 SDK 静态库本身未重新插桩，官方语义测试另在普通验证中执行。另用真实 SDK 链接、客户端带 ASan/UBSan 的二进制运行两种 Probe 与 Stage 1 场景，记录在独立 SDK sanitizer 证据中，不加入正常性能对照。

首次 sanitizer 使用默认 PIE，在部分进程进入主函数前崩溃且没有 ASan 报告；未改动 1.7 同配置也复现。采用 1.7 既有验收使用的 `-fno-pie` / `-no-pie` 后，182 项最终检查全部通过，没有 sanitizer 报告。首次失败、基线复现、调整后的各轮日志均保留，最终依据为 `sanitizer-tail-final.log`，不覆盖原失败记录。

构建与验证入口见 [PROBE_LAYER.md](PROBE_LAYER.md)。本次没有删除文件、修改既有版本或修补题源。
