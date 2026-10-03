# src1.7.1：Stage 2 有界 Probe 层

本版本从 `src1.7` 独立复制。Probe 只在真实 Stage 2 主循环没有合格正边际收益单任务时获得入口；完整候选投影、任务资格、greedy 排序、constraint trade、基础分、canonical authority、mutation contract 和 deadline 参数沿用基线。当前已有合格 task 时不生成 Probe。Stage 1、shadow projection、greedy continuation 禁用 Probe。

## 调度接入

`ExecuteMainTaskLoop` 仍先生成整轮普通 `CandidatePlan`，调用原 `SelectGreedyCandidate`。仅在 `best == nullptr` 分支调用 `TryProbe`。支持范围内的 guarded 调用保持原位置和行为；Stage 2 的 guarded 支持范围未扩大。

有延后的 Multi-GOTO 时，Probe 先以原投影与原选择器检查包含尾部任务的候选集；没有正收益单任务时，再复用原完整 greedy continuation 投影检查聚合尾部。任一合格、完整、正收益且符合原预算/约束门控的尾部计划存在时，立即返回原尾部流程，不生成 Probe。尾部仍使用原 100 ms 预留。1.7 已有启动 Sense 保留，统计不计入新增 Probe。

每次 Probe 执行或失败后，立即返回主循环并重新生成完整候选。Probe 不执行任务后续、不增加 `task_attempts` 或 `scheduler_steps`。普通任务每次反馈后整轮失效的规则保持不变。

## 独立类型与阻塞分析

`probe_layer.hpp` 定义四类接口：

| 类型 | 含义 |
| --- | --- |
| `BlockingFact` | task 索引、稳定 ID、字段、对象、阻塞原因、具体地点及来源 |
| `ProbeCandidate` | 可授权的观察序列、目标事实、相关任务、状态上下文、约束结果、成本和估时 |
| `ProbePolicy` | 本题独立探索上限 |
| `ProbeExecutionRecord` | 真实执行反馈、前后 revisions、证据变化、下一轮恢复及随后完成的任务 |

`ProbeCandidate` 不继承 `CandidatePlan`。普通 `eligible` 的含义仍是任务可以基于当前 canonical facts 可靠完成。Probe 的 `eligible` 只授权有限观察动作。

停滞时先记录任务在当前投影中的筛选原因：风险资格、投影不完整、非正收益、deadline、constraint trade、失败 revision 或任务重试上限。已达到普通任务重试上限的任务不生成 Probe。随后只读查询 X、Y、give 的 human、有关容器及 canonical dependencies，对 UNKNOWN、未验证、冲突或依赖失效记录具体 fact。没有事实阻塞的任务不产生 Probe。

地点线索可来自对象的当前 canonical location，已有 received/conflicting weak claim，已知或弱 inside 所指容器的位置，既有 near/on/inside 关系中的另一端。已有 canonical location 优先，不用旧弱 claim 覆盖它。不会把任务期望目的地当作对象当前位置；没有具体地点依据时不搜索。

## 第一版动作

| Probe | 授权序列 | 成本 / 估时 |
| --- | --- | --- |
| `SenseCurrentLocationOnly` | 当前地点一次 Sense | 1 / 100 ms |
| `MoveSense` | 一次 Move(target)，成功后一次 Sense | 5 / 220 ms |

估时与成本直接复用既有 `CandidateAction`。普通计划安全余量仍为 200 ms，因此在未开始计时的精确测试里，Sense 需要至少 300 ms，MoveSense 需要至少 420 ms。

当前地点必须未被可靠感知，且存在相关阻塞事实。已有可靠缺席记录按基线规则使用。容器开关状态不能由既有 Sense 消除，不生成该 fact 的 Probe；开放或未证明关闭的容器中 INSIDE 的歧义也记录为未支持。LOCATION 仍可单独成为感知目标。未增加 Open、AskLoc、多个地点串联或盲扫。

同地点候选合并任务和 facts。确定性字典序为：独立 `(field, object)` 数量降序、去重未完成目标的 `40 × 目标数` 降序、动作成本升序、估时升序、任务稳定 ID、地点签名。该名义目标价值只用于 Probe 排序，不调用或改写官方收益预测。

## 约束与动作授权

Sense 视为零物理约束损失，仍核验 canonical 机器人位置、相关事实、deadline 和探索预算。

Move 通过原 `BuildTaskGroupPlan` 的 final-move 路径进行完整投影，使用 `task_index = -1` 的中性上下文，并复用原快照恢复。投影不得模拟 Sense 结果。授权投影必须恰好包含一个目标 Move；出现 PutDown、FromPlate 或其它动作直接拒绝。

安全检查依据实际可能改变的 LOCATION、canonical 携带状态、约束实际绑定和 provenance dependencies 确定相关约束。EVERY/条件绑定按原终态检查方式展开。无关 UNKNOWN 不阻止移动；相关约束必须具备 canonical 安全证明。当前仍有历史资格的约束若投影确定失效，一律拒绝，不使用普通 task 的收益交换机制。

门控结果为 `constraint_safe`、`constraint_known_loss`、`constraint_safety_unknown`，只有第一类可执行。正常 task 的 constraint trade 未修改。

执行前重新投影并核验真实状态与 fact 上下文。原 `RecordAction` 增加仅在 `active_probe` 存在时运行的保护：精确动作名称/参数白名单、完整剩余动作预算、canonical 位置、Move 前 revision 和状态签名。该保护位于 SDK 调用和动作成本登记之前。Move 返回失败后不执行 Sense。

生产执行只调用原 `Move` 和 `SenseCurrentLocationOnly(true)` 包装器。它们的证据更新、ledger、StateMutation 明确失败/异常恢复语义不变。Probe 不直接写 `location`、`inside`、container 状态或 canonical provenance，不补造 verified fact。

## Legacy 与重试

`MustChooseOne()` 保留为只读日志包装器。`LegacyBlockedProposal()` 提取旧风险偏好，作为阻塞分析的首个 task hint；完整分析仍覆盖全部相关任务。Probe 最终排序不受该 hint 覆盖。直接调用包装器不会调用 SDK、改 task 状态、ledger 或事实，也不决定 execute/stop。

集中政策固定为 8/2/2：

| 上限 | 达到后的行为 |
| --- | --- |
| 本题最多 8 次 Probe | 锁定关闭本题 Probe |
| 同一观察身份最多 2 次 | 锁定关闭本题 Probe |
| 连续 2 次无进展 | 锁定关闭本题 Probe |

反馈后的正常重规划、任务执行和尾部判定仍运行。signature 为 `sense_at:<location>`，两种 Probe 共用身份，关联任务或 fact 列表改变不会重置次数。

同 revision 或相同相关 fact 上下文不能重试。跨 revision 重开需同时满足：上一 Probe 得到相关新信息、至少一个上次与本次共同目标 fact 的语义上下文发生变化、当前候选仍有未解决的可观察事实。仅添加/删除 fact、换 task、移动、缓存失效、成本增加或 revision 自增不能重开。此前无信息的观察身份不会因其它 revision 增长重开。

相关上下文比较字段值、received/conflicting claim、resolved source/value/verified、dependency validity 与 dependencies，排除纯版本号和机器人自身移动。Sense 进展比较从 Move 完成之后开始，因此移动引起的字段/缓存失效不是信息。基线认可的缺席记录可计入观察进展。任务恢复由下一轮完整投影及原资格筛选确认；随后成功完成另行记录。

## 日志与统计口径

所有新增日志以 `[Probe]` 加单行 JSON 输出，schema 为 `probe.v1`。事件包括 blocked_task、blocking_fact、unsupported_fact、legacy_proposal、candidate、execute、feedback、replan、task_completed、execution_rejected、stop。

日志包含地点依据、独立 fact 数、名义目标值、成本/估时/稳定 ID、资格/拒绝原因、8/2/2 预算、前后 world revisions、相关语义上下文和实际反馈。`sense_evidence_changes`、`action_success_evidence_changes`、`action_failure_evidence_changes` 是 0/1 变化标记，表示对应来源的 provenance 集合发生变化，不表示 SDK 返回的对象数。

分别统计收到反馈、相关新信息、下一轮恢复正常候选、随后完成任务。`effective` 表示相关信息或经完整重规划恢复正常候选；因此有效信息不保证最终多完成目标，也不保证抵消观察成本。无信息统计同时保留 feedback 的 `related_new_evidence=false` 和 replan 的 `effective=false`。

stop 原因区分 no_task_and_no_legal_probe、deadline、constraint_rejected、duplicate_or_no_information、probe_no_progress、total_probe_bound、same_probe_bound 和 qualified_goto_tail。混合拒绝原因保留在每个 candidate 中。

## 构建与复跑

在仓库根目录的 WSL Ubuntu-18.04 中运行：

```sh
bash src1.7.1/tests/build_probe.sh /tmp/rdfw171-product-new
bash src1.7.1/tests/validate_probe.sh
bash src1.7.1/tests/sanitize_probe.sh
python3 -B src1.7.1/tests/audit_probe_release.py --output /tmp/probe-authority-new.json
bash src1.7.1/tests/compare_probe.sh --output /tmp/rdfw171-paired-new --suite all --rounds 2
```

Windows 可在前面加 `wsl -d Ubuntu-18.04 --exec /bin/bash`。构建需要官方 SDK `/home/yifan/env-release-2026`。比较输出目录必须全新且路径不含空格（Linux `LD_PRELOAD` 的库路径限制），脚本不会删除文件或重跑替换不利结果。种子未加载时校验会中止；中止运行也保留。

比较按已有哈希解析原 71 输入的当前路径，再加载 comprehensive 的 180 正常题与 20 非法题。固定种子 20260924、5000 ms、IT/NT、两轮、串行 AB/BA、StageTiming 关闭。源码和题源运行前后再次校验。非法题按原 expected_layer 独立汇总，不进入成绩比较。

37 项专项测试覆盖正常 greedy 零 Probe、Stage 1/shadow 禁用、两种 Probe、弱事实与歧义、相关/无关 UNKNOWN、三态约束、隐藏物理动作、逐动作 deadline、明确失败/异常、投影恢复、重复/跨 revision 重开、fact 重组与 8/2/2 上限。尾部测试同时覆盖正收益单任务和“单任务均非正、完整聚合尾部仍正收益”的情形。

完整结果见 [RELEASE_1.7.1.md](RELEASE_1.7.1.md)；权威与 mutation 审计见 [PROBE_AUDIT.md](PROBE_AUDIT.md)。
