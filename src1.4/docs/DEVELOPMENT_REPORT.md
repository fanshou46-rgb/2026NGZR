# src1.4 开发报告

基于 `src1.3.3-fixed`。本轮只处理全过程约束记账、goto 的 keep 风险和这两项所需的初始约束证据。没有修改题目，也没有引入概率模型或任务组调度。

## 根因与修改

1. `TerminalChecker` 原来只返回当前谓词真假；`ScoreEvaluator` 直接把终态满足的约束计分。05 的 Open 使 must-closed 中途失效，Close 后却被重新计入。现在 `RDFW::constraint_eligible` 按 `not_info`、`notnot_info`、`not_task` 的固定顺序存放资格；每次成功原子动作和感知更新后检查，首次确认违反即永久置为 false。`TerminalSummary` 同时暴露当前真假和资格；计分只计当前满足且仍有资格的状态约束，以及未触发的禁止动作约束。题目开始时初始化，dry-run 快照并恢复，真实执行保留到本题结束。
2. 04 的 must-inside 修正只更新了红书的 `inside`，未更新其已验证证据，导致终态计分为 UNKNOWN。must-closed 推断也未提供关门任务的已验证证据。初始约束在官方题目中保证成立，因此修正这两类初态事实时同步记录证据。04 因此识别 cupboard 已关闭，省去赴柜和失败的 Close。
3. `CalculateTaskRisk` 和另一处任务风险检查把目标对象的 `is_keep` 加给 goto。goto/move 的目标对象没有被修改，现不继承该 keep 惩罚；原有位置风险和搬运物体的移动风险仍在。CandidatePlan 另以整个 dry-run 的资格变化检查实际副作用：若会新破坏至少两个仍可计分的约束，候选仍被风险门槛阻止。Open、PickUp、PutIn 等物理动作继续使用原有风险检查。

主要修改：`rdfw.cpp/.hpp`、`terminal_checker.cpp/.hpp`、`score_evaluator.cpp`、`candidate_plan.cpp`、`tests/three_a_tests.cpp`，以及 CMake 测试选项描述。

## 回归

2026 SDK、Ubuntu 18.04、5000 ms；01～06 各跑 IT/NT 一次，12 次均有效。表内为 IT，NT 的目标数、约束数、动作成本和基础分相同。动作成本按官方动作流计算；前值来自原版正式记录，后值来自本版官方运行。每题后值的内部基础分与官方基础分相同。

|题|目标 前→后|约束 前→后|动作成本 前→后|内部基础分 前→后|官方基础分 前→后|
|---|---|---|---:|---:|---:|
|01|7/7→7/7|0/0→0/0|48→48|232→232|232→232|
|02|9/9→9/9|0/0→0/0|48→48|312→312|312→312|
|03|7/7→7/7|2/2→2/2|25→25|295→295|295→295|
|04|5/6→6/6|1/2→2/2|47→40|173→240|193→240|
|05|6/6→6/6|1/1→0/1|20→20|240→220|220→220|
|06|5/6→5/6|3/3→3/3|20→20|240→240|240→240|

04 的实际动作以 `Close(4)` 结束，机器人处于 microwave 所在位置，goto 目标成立；没有再发生 `Move(3)`、`Close(3)` 失败和随后的 Sense。通用单测另验证 `is_keep=2` 的目标容器仍允许 goto 候选执行 Move。05 的候选日志在首次 putin dry-run 中报告 `broken_constraints=[0]`；真实运行 Open(2) 后即失去该约束资格，最终 Close(2) 只恢复当前关闭事实，内部仍计 0/1。

01/02/03/06 的 IT 与 NT 官方动作和反馈序列均与修改前逐项一致。

编译通过；`three_a_tests`、`input_safety_tests`、`legal_preservation_tests`、`question_preflight_tests` 均通过。完整逐次结果在 `../../test-results/liuyifan1.0-src1.4-final-20260924/comparison.csv`，04/05 的 `client.log`、`server.log` 保留于对应题目目录。

## 尚存事项

六题没有内部基础分与官方基础分差异。03 仍比作者参考方案多一次 Sense、少 1 基础分；06 仍按预期放弃高风险 give 目标。本轮未扩展验证更大题库或概率、Bayesian 路线。
