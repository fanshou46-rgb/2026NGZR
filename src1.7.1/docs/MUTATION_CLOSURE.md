# src1.6.7 mutation closure review

事实权威保持 `Evidence → StateProvenance → ResolutionEligible / DependenciesCurrent → ResolvedState → Fact*`。公共对象字段服务候选与兼容视图，Source/Verified 镜像 resolved metadata。状态架构冻结对象是这些角色、资格规则和 mutation contract。

## 剩余 direct accesses 及安全边界

完整逐行索引在 `DIRECT_ACCESS_AFTER.json / .md`，计数和源码哈希在 `mutation-audit.json`。扫描覆盖本版全部 C++ 产品、头文件、测试和 stub；旧版本由 `BASELINE_SHA256.json` 固定。索引对字面量做 masking，区分局部结果赋值与世界写入。以下表补充别名写入和函数混合用途的人工复核。

| 访问类别 | 位置 / owner | 保留原因及安全边界 |
|---|---|---|
| canonical mutation 内部值写入 | `state_mutation.cpp::StageStateValue`、`ApplyStateValue`、`Robot::SetHold/SetPlate` | StageStateValue 为 private，缺少 active scope 时抛 logic_error；Robot 原语只由 RDFW 包装调用，包装先 journal 对象与槽位，再同步 provenance、inside/location 和成员 |
| provenance / metadata 内部写入 | `MutableProvenance`、`ReceiveWeakClaim`、`MarkUnresolved`、`UpdateProvenance`、`DependOn`、`SetConstraintSupport`、`RecordConstraintSupports` | MutableProvenance 在返回可写引用前保存相应对象或槽位；Source/Verified 由 UpdateProvenance/MarkUnresolved 同步；支持列表分配失败属于同一 journal |
| 成员缓存写入 | `ClearContainerMembership` 中的 `items.erase`、must-in 中的 `vec.erase`、`DeleteObjectInside`、`AddContainerMembership` | 别名 erase 前 touch owning container；插入前 touch container；Clear 先 touch item。保留原成员清理范围及去重政策，不产生额外事实答案 |
| ledger / Stage 1 score 表示 | `InitializeConstraintLedger`、`UpdateConstraintLedger`、ParseEnv | 两个 ledger 初始数组先构造再 swap；运行期 ledger、uncertain、score_locations 和 world_revision 在写入前保存。Stage 1 score_locations 仍需 canonical location 资格 |
| sensed absence cache | `InvalidateSenseAtLocation`、`SenseCurrentLocationOnly` | 首次改变对应位置前保存 observed IDs / container / flag；异常可恢复，外部动作状态未知时撤销关联位置的旧 Sense 资格 |
| graph / capacity 初始化 | `InitializeDynamicArrays`、Init、Ensure*、ParseEnvSentence、ParseEnv | 对象创建、类型替换和初始关系补全属于 construction；ParseEnv 后才使用完整模型。运行期 evidence capacity 的全部 reserve 先于 size 增长；容量变化不给事实资格 |
| teardown | Fini | 清空对象、兼容元数据和槽位 provenance，图不再作为事实模型使用 |
| snapshot / restore | `BuildTaskGroupPlan`、`StateMutation::rollback` | 保存完整 claim、resolved、revision、dependency、supports、成员与镜像；恢复采用 move/swap。projection 的全图快照是既有 dry-run 隔离，本版不在 query 中增加它 |
| planning cache | `on`、must-near component/lock、unable_site、约束动作风险表 | on 没有独立 canonical fact 能力；terminal 延续 location/inside/storage 表达。风险、路线、候选和组件表提供假设及行动选择，不能自行完成事实任务 |
| planning read / hypothesis | solver 路线、候选、容量、DryRunActionSucceeds、显式 evaluatePlanningHypothesis | completion / zero-action 与默认 TerminalChecker 继续走 canonical；静态 binding 不按动态 UNKNOWN 删除候选 |
| debug / serialization / local result | DebugStateSnapshot、AppendStateSnapshot、PlanStateSignature、Print、TerminalSummary | 只读状态编码或局部返回值；AppendStateSnapshot 与原字符串内容相同，避免 signature 的中间字符串分配 |
| debug/test/stress fixture | tests/*.cpp、tests/stubs | 手工污染候选或 metadata 用于验证旁路拒绝、失效支持、恢复、互斥和只读性；不链接比赛二进制。state_profile 的长支持列表、深度链属于专门压力 fixture |

本版没有未分类的事实写入。索引是可复核的静态审计，别名和 mixed owner 以本表及 source.diff 的语义复核为依据；它不提供任意 C++ 扩展的形式化 alias-analysis 证明。

## 正常、失败与异常的 mutation contract

普通 API 与 evidence/inside/location/container、slot、Sense、关系传播、ParseInfo、constraint correction 使用嵌套共享的 `StateMutation`。它按首次写入保存局部对象的三个 provenance、字段、Source/Verified、inferred flag 和成员列表。槽位、sensed cache、ledger 分别按需保存。正常退出提交；异常展开或显式取消通过 noexcept move/swap 恢复。

`ApplyStateValue` 的 inside 清理、赋值、成员插入与证据提交位于同一边界。`SetHold/SetPlate` 在改变 Robot 字段前保存槽位和 item，并拒绝不属于当前 objects 图的 foreign pointer。MarkDirectLocationEvidence / SetContainerEvidence 的 support push_back 失败会恢复旧 revision、claims、resolved 和镜像。弱证据冲突返回 false 是已接收冲突的正常结果：历史 claim 保留，外层继续执行既有 unresolved 政策。

真实原子动作在平台调用前准备 target、相关 contents、robot、slots、ledger 及 sensed locations。明确平台 false 返回保留原事实；平台调用异常或成功后的模型更新异常意味着外部状态可能已改变。此时恢复内部候选与成员结构，撤销 touched records 与 slots 的事实资格、提高 revision、清除相关 sensed cache，ledger 的确定性降为 uncertain。后续 canonical queries 返回 UNKNOWN，等待新观察。shadow mutation 没有外部副作用，因此恢复完整原快照。

恢复本身不分配内存：StateProvenance 的 nothrow move 有 static_assert，成员/provenance/vector 使用 swap/move，标量和 shared_ptr 赋值不分配。allocation fault 在整个 stack unwinding 期间保持启用，测试在展开结束后才恢复 allocator。RecordAction 的动作成本/平台调用记录是外部动作 bookkeeping，按原政策记录已尝试动作；它不属于世界事实 rollback。路线、风险和任务启用缓存可保留已完成步骤的调整，随后由既有 rescan / recovery 路径处理。

projection 在建立 restore guard 前只准备快照；InitializeConstraintLedger 移到 guard 之后。恢复 task、metadata、provenance、支持列表、反馈等复合类型采用 move，成员列表保存 shared_ptr 并 swap。query 和比赛正常路径没有新增全量 consistency assertion。原成员清理扫描和原 projection snapshot 范围保持；异常恢复的 constraint uncertainty fill 仅发生在错误退出路径。

## 失败证据与覆盖

同一个 mutation_failure_tests.cpp 编译到未修改 1.6.6 与本版。四个 before probes 分别证明 inside/member 插入分配失败、derived support 插入失败、ParseInfo 复合写入失败、foreign storage pointer 可破坏模型；基线四项断言失败，本版通过。

本版 28 个 mutation_failure cases 覆盖上述 API、projection restore、Sense、SetHold/SetPlate、must-in、location，以及九个原子动作的明确失败返回和逐次分配失败。原 20 state invariant、19 state layer、33 canonical、14 semantic regression 保留；截止时间边界测试单独增加。普通与 sanitizer 构建各自保留 allocator sweep 原始日志。

## 实现优化与语义保护

TerminalChecker 的 PairFacts 是单次 evaluatePair 的固定栈缓存，最多四个对象、五个字段，overflow 回退原 ResolvedState。资格递归、domain、互斥、revision/value、support eligibility/certainty 和深度 8 保持。缓存跨 mutation 的生命周期不存在。各谓词按需要查询，重复的 location / inside / storage / score qualification 复用同一 claim。

ResolutionEligible 的动态类型判断改用 raw dynamic_cast，省去临时 shared_ptr 引用计数；无依赖/无支持记录具有等价 leaf fast path。支持约束仍逐项核验，递归支持仍经过同一资格检查。signature 直接追加 snapshot 编码，projection restore 减少重建与分配；binding/summary 仅调整 reserve。

评分、任务搜索、deadline manager、candidate plan、legacy priority、parser、question preflight 的文件哈希与 1.6.6 相同。搜索预算、排序、安全余量和 complete projection gating 按原政策执行。新增机制限于局部异常 journal、纯查询复用和发布验收。
