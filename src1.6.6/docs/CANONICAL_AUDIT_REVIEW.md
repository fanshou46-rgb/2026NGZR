# 1.6.5 audit review (completed before product edits)

逐行索引见 DIRECT_ACCESS_BEFORE.md / json（含测试与声明）。同一个函数常混合 A/B/C；下表是语义复核，不能按字段名机械替换。

| 文件 / 函数 | 字段 | 类别 | 安全性 / 修改决定 |
|---|---|---|---|
| terminal_checker.cpp / evaluatePair, known helpers, scoreLocation | location/inside/isOpen/hold/plate/Source/Verified | B | 不安全：资格和值来自不同存储；统一读取 canonical value。Stage 1 ASP at 评分口径必须保留。|
| rdfw.cpp / Is*Verified | Verified + dependency | B | 不安全：未检查 resolved UNKNOWN/heuristic；改为 canonical adapter。|
| rdfw.cpp / SolveTask_Give | location/hold/plate | B | 不安全：同地直接完成绕过验证；canonical 同地、inside、storage。|
| rdfw.cpp / SolveTask_TakeOut | inside | B | 不安全：相反任务及 VerifyObjectRelation 分支把未验证的“非 inside”判完成。|
| rdfw.cpp / SolveTask_PickUp, PutDown, HoldSmallObject | hold/plate/inside | B + A | 完成/已持有判断需 canonical；发起动作、容量和路线仍允许假设。|
| rdfw.cpp / SolveTask_Goto/Open/Close/Putin/PutOn | location/inside/isOpen | B + A | 提前完成必须同一次 canonical query 取得值；导航/选动作仍为 A。goto Sense 的 inside 推导必须记录两个依赖。|
| rdfw.cpp / TakeOutLogic | isOpen/inside/location | A + B + C | 选 Open/TakeOut 为 A；“开放容器不存在物体”证明必须查询 canonical open。|
| rdfw.cpp / GetSmallObjectStatus/GetBigObjectStatus | location/inside/Verified | A + B + C | Ask 候选为 A；保护已验证事实的比较必须用 resolved value；写入收敛。|
| rdfw.cpp / RefreshMustNearConstraintState | Verified/inferred/location | A + B + C | candidate_votes/locks 是路线假设；direct_votes 和 anchored 是事实资格，应 canonical；原 1.6.4 手工只写 Verified 的 fixture 需迁移 setup。|
| rdfw.cpp / sense | location/inside | C + B | 容器内容位置传播缺少容器 location 与 inside revision 依赖。|
| rdfw.cpp / SenseCurrentLocationOnly | isOpen/inside/hold/plate/location | A + B + C | 感知输入直接事实；隐藏容器判断只能由 canonical closed/open 证明；未知容器保守处理。原位置枚举是待反驳假设。|
| rdfw.cpp / ConfirmContainerLocation | inside/location | B + C | 内容列表是缓存；强度由 canonical inside、container location 决定，保留依赖。|
| rdfw.cpp / ApplyMustInConstraintCorrection | inside/location | C | not-inside 清除字段漏写 metadata；修复清除。约束补全保留同一政策、记录资格依赖。|
| rdfw.cpp / SetHold/SetPlate, Robot setters | hold/plate/inside/location | C | Robot setter 只写字段，RDFW wrapper 漏更新物体 metadata；wrapper 同步。|
| rdfw.cpp / ParseEnvSentence/ParseEnv/ParseInfo, actions | 核心字段 + metadata | C | 用最小值写入 API 收敛；初始化/关系转换不能留不一致 metadata。|
| rdfw.cpp / MarkUnresolved | metadata/Verified/Source | C | 旧资格数组残留；同步降级但保留 hypothesis。|
| rdfw.cpp / DependenciesCurrentDepth | dependency/support | B | 依赖仅检查 revision/value，未要求支持本身是 fact；增加支持事实资格及边界。|
| rdfw.cpp / Fini | hold/plate provenance | C | metadata 未重置，跨题可残留；补重置。|
| rdfw.cpp / BuildTaskGroupPlan, PlanStateSignature | 全部状态 | D | 保存恢复已有 provenance；signature 漏 canonical metadata，加入有界序列化，debug 快照核对。|
| rdfw.cpp / CaptureCandidateEvidence | Source/Verified | B + D | 输出来源由 provenance，verified 由 canonical；补 hold/plate。|
| rdfw.cpp / Cons_plan, CalculateTaskRisk/StepRisk, IsKeepingGoing, MultiGoto, FilterConstraints | location/inside/hold/plate/isOpen | A | 路线、风险、任务冲突启发式；不授予终态分，保留政策。|
| rdfw.cpp / SearchConditionObject; Condition; question_preflight | id/sort/color/type | binding | 静态属性绑定，无动态位置条件；失效 derived 不参与事实绑定，不引入动态筛选。|
| legacy_priority.cpp | 同上字段 | A (+ qualification B) | 优先级策略、putdown/puton 旧谓词口径保留；其资格和值适配 canonical，不改 fallback 算法。|
| task_group_search / score_evaluator / deadline / candidate_plan | terminal summaries | B | 已委托 TerminalChecker；无需新 truth access，不改排序/搜索/区间/截止。|
| header constructors/ToString/PrintEnv/tests/replay/parse_snapshot | 旧字段 | C / D | 构造默认不是事实；序列化、人工故障 fixture、debug 不参与真实事实判定。|

限定：Source/Verified 是 resolved metadata 的兼容镜像，并非“当前依赖有效”的缓存；过期依赖可以保留旧值及 raw verified=true，但 canonical 拒绝。冲突历史可以保留，后来的 Sense/成功动作可确定新时刻事实，不能因历史相异永久拒绝直接观察。
