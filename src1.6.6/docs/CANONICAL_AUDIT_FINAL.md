# Canonical state 最终语义审计

逐行访问索引为 [DIRECT_ACCESS_AFTER.md](DIRECT_ACCESS_AFTER.md)，修改前索引及先行复核为 [DIRECT_ACCESS_BEFORE.md](DIRECT_ACCESS_BEFORE.md) 和 [CANONICAL_AUDIT_REVIEW.md](CANONICAL_AUDIT_REVIEW.md)。索引按函数定义和函数体范围追踪访问；一个函数可能混合三类访问，索引中的 `safe/modify` 是初筛，不是发布时尚未修复的问题清单。下面按实际调用上下文复核事实边界。

| 文件 / 路径 | 剩余字段 / 查询 | 分类 | 最终判断 |
|---|---|---|---|
| terminal_checker.cpp / 默认 evaluateTask、evaluateConstraint、evaluateAll | FactLocation / FactInside / FactContainerState / FactValue / IsStoredFact | B | 事实值和资格来自同一查询。UNKNOWN 不因 bool 转换成为 closed，不因旧 location 相等成为已完成。|
| terminal_checker.cpp / evaluatePlanningHypothesis | 旧 location / inside / isOpen / hold / plate | A | 仅供 Plan 初始奖励探测；独立入口明确表示假设，不写 terminal summary、ledger 或事实资格。替代原临时 stage=1，保留原规划政策。|
| legacy_priority.cpp / 默认评估及 hypothesis=true | canonical；显式分支中的旧字段 | B / A | 默认使用 canonical；true 仅用于 ShouldStartConstraintTrade 的 conservativeScore 假设探测。旧 putdown/puton/on 谓词、fallback 优先级及禁止动作轨迹口径保留。|
| rdfw.cpp / SolveTask_*、HoldSmallObject | TaskFactSatisfied、canonical storage / inside / location | B | 零动作完成、同地 Give、相反 putin/takeout、已持有、已开关容器均不能由旧字段独立证明。返回成功平台动作结果仍合法。|
| rdfw.cpp / task solver 中路线、容量、选动作 | 旧位置、inside、开关、hold/plate | A | 为 Move/Open/TakeOut/PickUp 选择可执行尝试，允许使用候选值；不授予 terminal credit。|
| rdfw.cpp / Goto 的 sensed-container 路径 | canonical inside + 实际 Sense | B / C | 内容位置推导记录 inside 和容器位置两个依赖，不把“曾经 inside”独立当成当前位置事实。|
| rdfw.cpp / GetSmallObjectStatus、GetBigObjectStatus | Ask 候选和 canonical 已知值 | A / B / C | 选择 Ask 返回值仍是规划政策；保护已知事实的比较用 resolved 值；弱冲突保留候选，resolved UNKNOWN。|
| rdfw.cpp / must-near | candidate_votes、locks、inferred 标记；FactLocation | A / B / C | 候选投票和路线锁定保留；direct_votes 和事实 anchor 用 canonical。inferred 标记只排除派生 anchor，不能授予事实资格。|
| rdfw.cpp / SenseCurrentLocationOnly、sense、ConfirmContainerLocation | 感知输入、旧候选枚举、canonical 容器/inside | C / A / B | 两条管线共享事实资格；内容位置有依赖。旧预期位置用于反驳，开关 UNKNOWN 不构成确定开放或关闭的证明。|
| rdfw.cpp / Cons_plan、risk、IsKeepingGoing、MultiGoto、FilterConstraints | location / inside / isOpen / hold / plate | A | 路线、风险、冲突启发式，不回答当前世界任务已满足。保留原候选顺序、搜索及任务调度。|
| rdfw.cpp / DryRunActionSucceeds、DryRunSenseIds、shadow AskLoc | 旧字段 | A | 对完整投影的条件性预测；与真实执行共享 mutation。隐藏观察预测能力及 complete projection gating 保持原边界。|
| rdfw.cpp、canonical_state.cpp / ApplyStateValue、Mark*、Set*、parse、actions | 旧字段、Source/Verified、provenance | C | 普通值写入、证据元数据、依赖、槽位转换收敛到少量包装；内部短暂 staging 不在中途调用 terminal。Robot setter 仅由 RDFW wrapper 完成元数据同步。|
| rdfw.cpp / ParseEnv inside、ParseInfo on/near/inside、must-in、容器内容传播 | FactLocation / FactInside；未知时的旧候选 | B / C / A | 来源已知就复制 canonical 值；缓存成员必须与 canonical inside 相符才传播事实。候选位置只在来源 UNKNOWN 时作为弱假设。新测试 29..32 及 before probes 10..13。|
| rdfw.cpp / Isinside | inside 候选 | A | 仅用于选取关系/动作；原 solver 的完成判断已移至 canonical。|
| rdfw.cpp / Source/Verified 直接访问 | 并行数组 | C / D | 初始化、容量、mutation 镜像及保存/恢复；Is*Verified 兼容接口委托 ResolvedState。镜像不缓存当前依赖资格，失效依赖可保留 raw verified，但 query 拒绝。|
| rdfw.cpp / CaptureCandidateEvidence | provenance source + canonical present | B / D | CandidatePlan 输出来源与当前资格，并记录 hold/plate；不从旧 Verified 数组授予证据强度。|
| rdfw.cpp / BuildTaskGroupPlan、PlanStateSignature | 旧字段及全量有界 metadata | D | 保存/恢复 provenance、revision、依赖、支持列表、兼容数组。签名覆盖 canonical 元数据；debug 投影快照仅按测试开关采集。|
| canonical_state.cpp / DebugState*；PrintEnv、ToString；测试 fixture | 全部状态 | D | 主动检测人工不一致、比较 real/shadow/restore；正式比赛不进行全量检查。|
| binding、Condition、question_preflight | id / sort / color / type | 静态绑定 | 当前 binding 无动态 location/inside 过滤。失效 derived 对象可作为候选绑定，但它的任务状态必须由 TerminalChecker 返回 UNKNOWN；测试 14 明确覆盖。|
| task_group_search、score_evaluator、guarded decision | TerminalSummary、CandidatePlan evidence | B | 经 canonical terminal/投影摘要消费事实；无新增旧字段直接事实入口。strict interval dominance、deadline 和完整投影门控不变。|

Stage 1 的 ASP `at` 和物理 inside 传播位置是两个既有表达。`ScoreFactLocation` 保留官方 `at` 口径，同时先检查 canonical location 是否有效；resolved UNKNOWN 不能从 `score_locations` 获得事实资格。这不是给旧对象位置新增评分权威。

真实动作成功是证据输入，dry-run 成功是在原完整投影条件下的预测输入；两者共享更新与恢复逻辑，但本版没有赋予 dry-run 预测隐藏世界的能力。Sense 的正负观察缓存仍是实际观察证据，具有原有位置失效机制。

审计结论：当前产品的默认终态、约束谓词、零动作完成、事实 anchor 和 CandidatePlan 资格没有发现未经说明的 `direct field → world truth` 路径。公共对象字段和 provenance 仍能被外部调用方直接改写，debug 能检测部分不一致；封装权限、内部 staging 的异常安全以及独立 on 事实模型属于 release hardening 或后续状态能力，不在此版重写范围内。
