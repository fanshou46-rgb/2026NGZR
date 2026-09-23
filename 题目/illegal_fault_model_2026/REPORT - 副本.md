# 20 道非法题：src1.3.3A / src1.3.3B 对照报告

日期：2026-09-23。运行环境：Ubuntu 18.04、g++ 7.5.0、官方 2026 SDK
`/home/yifan/env-release-2026`，IT 模式，单题平台限时 5000 ms。

## 结论

- 题集含 10 道 Stage 1、10 道 Stage 2；19 题可由平台加载，1 题故意破坏
  XML 并在客户端启动前被拒绝。A/B 对 19 题都正常退出，无硬超时或客户端崩溃。
- 9 个 duplicate 样本全部被 B 的语义 key 命中：6 个 task、3 个 constraint。
  去重发生在 risk、multi-goto、TerminalChecker 和 ScoreEvaluator 之前。
- 两个 duplicate constraint 样本给出最直接的 P0 证据：A 的重复权重把 risk
  推到 2 并放弃任务；B 保留一个权重、risk=1，成功执行任务。Stage 1 得分
  `98→134`，Stage 2 得分 `98→130`。
- 两个 malformed constraint 样本中，A 都吞掉后缀；B 都恢复了后续 task，
  Stage 2 还恢复了后续合法 constraint。由于题源指令本身不合法，官方 evaluator
  没有建立可计分目标，两版均为 0 分；动作差异证明客户端恢复路径生效。
- 四个 Stage 1 WorldState 关键错误——多个 human、human 编号错误、同位置多个
  大物体、对象缺运行时类型——在 A 中继续规划并各执行一次 Move；B 在任何平台
  动作前停止。得分 `132→98` 是安全停止的预期代价，不是合法题回归。
- B 仍未覆盖 ID 断号、duplicate info、初始已破坏 constraint、冲突 env 字段；
  malformed XML 只能由平台或离线 linter 拦截。这些题明确给出下一版边界。

## 题集设计

题目存放在本目录，所有文件通过目录、文件名、XML 注释和清单四重标记
`illegal`。除故意损坏 XML 的 `illegal-s2-10` 外，其余 19 题都是 well-formed XML。
修订后的题目只在待测 fault 上偏离要求；指令条件使用官方 grader 接受的
`sort/color/type`，避免客户端扩展 `(id X n)` 抢先导致 evaluator 失败。

| 类别 | 题号 | 验证目的 |
|---|---|---|
| duplicate task / goto | S1-01、03、04；S2-01、04、05 | 精确/语义去重、multi-goto、duplicate 与 conflict 边界 |
| duplicate constraint | S1-02；S2-02、03 | 风险阈值、条件重排、对称 near 关系 |
| malformed constraint | S1-05、S2-06 | 坏 wrapper 隔离和后缀恢复 |
| 关键 WorldState | S1-07～10 | human、编号、位置碰撞、运行时类型 |
| 已知客户端缺口 | S1-06；S2-07～09 | ID 连续、info 重复、初始 constraint、env 冲突字段 |
| 平台侧错误 | S2-10 | malformed XML 在 `Plan()` 前拒绝 |

完整定义和预期边界见 [manifest.csv](manifest.csv)。

## 逐题分数与动作

分数为官方平台输出，`Δ=B−A`。动作数包含 Move、物理、人机交互和观察动作。

| 题号 | fault | A分 | B分 | Δ | A动作 | B动作 | 主要执行差异 |
|---|---|---:|---:|---:|---:|---:|---|
| S1-01 | duplicate pickup | 174 | 174 | 0 | 1 | 1 | B `2→1` task；均 `PickUp(2)` |
| S1-02 | duplicate cons_not pickup | 98 | 134 | +36 | 0 | 1 | A risk=2 跳过；B risk=1，`PickUp(2)` |
| S1-03 | duplicate goto | 172 | 172 | 0 | 1 | 1 | A 走 multi-goto；B 普通 goto；均 `Move(2)` |
| S1-04 | duplicate open + close conflict | 178 | 178 | 0 | 0 | 0 | B task `3→2`，open/close 均保留 |
| S1-05 | malformed constraint | 0 | 0 | 0 | 0 | 1 | B 恢复并尝试 `Close(3)`；A 丢后缀 |
| S1-06 | sparse ID | 132 | 132 | 0 | 1 | 1 | A/B 均容忍 ID 2 占位槽；`Move(3)` |
| S1-07 | multiple human | 132 | 98 | −34 | 1 | 0 | A `Move(3)`；B 报 2 个 human 后停止 |
| S1-08 | human≠ID 1 | 132 | 98 | −34 | 1 | 0 | A `Move(1)`；B 报 human 编号错误后停止 |
| S1-09 | big-location collision | 132 | 98 | −34 | 1 | 0 | A `Move(2)`；B 报 location 2 冲突后停止 |
| S1-10 | missing size/type | 132 | 98 | −34 | 1 | 0 | A `Move(2)`；B 拒绝 task 并停止整题 |
| S2-01 | reordered duplicate pickup | 174 | 174 | 0 | 1 | 1 | B `2→1` task；均 `PickUp(2)` |
| S2-02 | reordered duplicate inside cons | 98 | 130 | +32 | 0 | 2 | A risk=2；B risk=1，`PickUp→PutIn` |
| S2-03 | symmetric duplicate near | 119 | 121 | +2 | 4 | 4 | 动作完全相同；B constraint `2→1`；2 分为耗时波动 |
| S2-04 | duplicate goto | 172 | 169 | −3 | 1 | 2 | A multi-goto 跳过 Sense；B 普通 `Move→Sense` |
| S2-05 | duplicate open + close conflict | 138 | 138 | 0 | 0 | 0 | B task `3→2`，open/close 均保留 |
| S2-06 | malformed constraint | 0 | 0 | 0 | 0 | 3 | B 恢复 pickup/not-open，尝试 `PickUp→AskLoc×2` |
| S2-07 | duplicate info | 114 | 110 | −4 | 6 | 7 | 两版都保留重复 info；AskLoc 随机结果不同 |
| S2-08 | initially broken constraint | 155 | 155 | 0 | 1 | 1 | 两版都未拒绝；均 `Sense` |
| S2-09 | conflicting at facts | 129 | 129 | 0 | 2 | 2 | 两版都 last-write-wins；均 `Move(3)→Sense` |
| S2-10 | malformed XML | 0 | 0 | 0 | 0 | 0 | 平台报 `Error reading end tag`，客户端未收到题目 |

机器可读表见 [results-summary.csv](results-summary.csv)。

## 关键执行逻辑对照

### Duplicate task

B 的 Preflight 日志显示 task `raw=2 unique=1 duplicate=1`。S1/S2 pickup
最终都只执行一次；官方 grader 仍按非法题源的两个重复 goal 计分，所以官方分数
不随客户端内部目标数下降。S1-04/S2-05 中，两个 open 合并为一个，close 保留，
证明不同 predicate 的合法 conflict 没有被误删。

### Duplicate constraint

S1-02 与 S2-02 的 A 日志分别出现 `pickup/putin 风险系数是：2`，触发既有
`risk >= 2` 跳过。B 的约束向量均从 `2→1`，risk 降为 1，任务可执行。
这验证了去重结果确实进入真实 `Cons_plan` / `CalculateTaskRisk`，不是只改日志或
Terminal 计数。

S2-03 将 `near(cup,table)` 与交换 X/Y 的 `near(table,cup)` 识别为同一个对称
constraint。两版外部动作完全一致；B 的内部终态日志从 `constraints=2/2` 变为
`1/1`。官方 grader仍消费原始非法题，因此官方分差只有运行时取整造成的 2 分。

### Duplicate goto

S1-03/S2-04 中，A 都记录 `multi-goto detected: 2 tasks` 并进入聚合路径；B 去重后
按一个普通 goto 执行。Stage 1 的外部结果都是一次 Move。Stage 2 中，multi-goto
路径按旧策略跳过 Sense，普通 goto 会 Sense，因此 B 多一个观察动作并少 3 分。
这是 duplicate 修复后恢复单任务语义的预期行为。

### Malformed constraint

S1-05/S2-06 的坏 constraint 缺少右括号。A 对 constraint 不做 marker 恢复，吞掉
后续内容；B 在首个 payload 后以顶层 marker 恢复，分别保住 close task，以及
pickup task + not-open constraint。平台 evaluator 无法从原始 malformed 指令建立
合法评分问题，因此动作尝试不产生 goal 分；这不影响客户端恢复结论。

### WorldState gate

S1-07～10 中，B 的 `world_errors` 分别为：

- `human must be the non-container big object 1` + `world must have exactly one human`；
- `human must be the non-container big object 1`；
- `multiple big objects at Stage 1 location 2`；
- `object lacks stable sort/runtime type: 2`。

B 四题均零平台调用。A 每题执行一次 Move 并得到 132 分；B 的 98 分来自平台
在零动作快速结束时的效率项。非法题上减少分数换取不在不可信世界中行动，符合
Preflight 的安全停止契约。

## 已知缺口与解释边界

- S1-06：B 为安全处理稀疏 ID 而保留未引用占位槽，尚未实现官方“ID 连续”硬拒绝。
- S2-07：Preflight 只去重 task/constraint，按版本范围明确不去重 info；两版都把
  cup 两次加入 container 内容。A/B 后续动作差异始于 `AskLoc(3)` 随机返回
  `at(3,1)` 与 `at(3,2)`，不能归因于 B。
- S2-08：两版都没有在规划前验证 constraint 是否已由真实初态破坏。
- S2-09：两版都采用 env 增量解析和 last-write-wins，第二个 `at(2,3)` 覆盖
  `at(2,2)`。
- S2-10：错误发生在 SDK 向客户端提供 `GetEnvDes/GetTaskDes` 之前，客户端版本
  无法修复。

20 题官方分合计为 A `2381`、B `2308`（Stage 1 `1282→1182`，Stage 2
`1099→1126`）。这个 `−73` 由四次 WorldState 安全停止主导，不代表合法题性能；
非法题聚合分仅用于核对逐题结果完整性。判断 B 是否符合本版目标应看语义去重、
风险阈值、执行路径和安全停止，而不是最大化非法题得分。

## 可复现性

正式运行命令：

```sh
wsl -d Ubuntu-18.04 -- python3 src1.3.3B/tests/run_illegal_fault_model.py \
  --sdk /home/yifan/env-release-2026 \
  --output test-results/src1.3.3B-build/illegal-fault-model-final-20260923
```

输出目录包括 `results.json`、`comparison.json/csv`、逐题 client/server 日志、
官方 evaluator 中间文件，以及 A/B 构建命令和 SHA-256。目录由现有测试产物
`.gitignore` 排除；最终 B 构建记录中的全部 `.cpp` hash 已与交付源码逐一核对。
首轮含 `(id X n)` 的调试运行保存在相邻非 final 目录，不作为本报告数据源。
