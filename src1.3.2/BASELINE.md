# src1.3.2 版本说明

本目录完整继承 `src1.3.1`，实现 Stage 3B 第一阶段的“确定性任务组边际收益
评估”，不引入概率模型，不以 utility 改写原 planner 的选择：

- planner 通过同一 `SolveTask` 调用链在 dry-run 模式产生完整 `CandidatePlan`，原子动作
  只更新临时 World State；评估后恢复对象、机器人、任务、约束表、证据位与评分器状态；
- `CandidatePlanEvaluator` 复用 `TerminalChecker` 与 `ScoreEvaluator`，输出 gained/lost
  goals、broken/preserved constraints、action cost、`marginal_score = score_after -
  score_before`，并令第一阶段 `utility = marginal_score`；
- `[3B][Candidate]` 以 shadow mode 输出所有候选的 utility 与排序，同时用
  `legacy_choice` 标记原选择，排序不参与调度；
- `DeadlineManager` 只接收 CandidatePlan 的完整剩余动作耗时，不再用按任务类型写死的
  单步 estimate；执行中的计划持续输出 remaining-utility，但不因 `utility <= 0` 退出；
- multi-goto 的每个完整 relocation 也封装为 candidate，并修复既定 hub 位置号被误当成
  `SolveTask_PutOn` 对象 ID 的参数错配；hub 搜索和 World State 语义不变；
- 重点回归 11、13、16、19、21、22–24、28–30、34–36 共 14 题全部正常结束、
  无平台硬超时；19/21/28/29/30 均在最终兑现分数前保留完整 relocation。

## src1.3.1 / Stage 3A 基础设施

`src1.3.1` 新增 3A“确定性终态检查与时间预算”基础设施，不改写原有任务求解器和
动作策略：

- `TerminalChecker` 只读解释当前 World State，对每个 goal/constraint 返回
  `SATISFIED / UNSATISFIED / UNKNOWN`，不读取 `isEnable`、已执行次数或 plan；
- Stage 2 中只有动作或感知建立的证据才允许确定判定，未验证的初始描述保持
  `UNKNOWN`；禁止动作类约束属于轨迹事实，不能由终态反推，保守返回 `UNKNOWN`；
- `ScoreEvaluator` 按 2026 规则计算确定性基础分 snapshot：目标 40 分、约束
  20 分（至少完成一个目标）、Move 扣 4 分、交互/其他物理动作扣 2 分、观察扣
  1 分；每次动作尝试无论成功与否都计成本，暂不包含效率分和概率模型；
- `DeadlineManager` 提供 `elapsed / remaining / deadlineReached / canFinish`，默认
  预算 4700ms、安全余量 300ms；它不持有执行器，也不从计时线程发动作；
- 主循环、复查、兜底任务和 multi-goto 前均有 stop gate。全部目标完成、没有可执行
  候选或候选估时超出余量时，均由主执行线程正常退出或跳过并尝试后续候选；
- `[3A]` 日志输出确定完成的目标/约束、基础分、动作成本和 elapsed/remaining。

## 上游 scr1.3 说明

本目录以 `scr1.2` 为代码基线，修复 must-near 的关系构建、证据传播与运行时状态刷新。

- must-near/nextto 关系按对象 ID 对称构建，并覆盖多对象条件的 `X × Y`；
- `on` 不再误建为 must-near，位置 ID 也不再参与 must-near 对象矩阵扩容；
- 直接位置证据与 must-near 推导证据分开记录，冲突或 Sense 反证不会被强制覆盖；
- 感知、询问及原子动作改变位置后统一刷新 must-near 组件状态。

以下内容记录本项目最初导入的上游历史基线，仅用于追溯；其中哈希不是 scr1.3 当前文件哈希。

## Iron 临时基线

本目录由 2025 国赛 Stage2 候选包原样导入，尚未得到上届队员对“正式提交版本”的确认。

- 来源：`archive/legacy-2025/代码/stage2国赛/example(15).zip`
- ZIP SHA256：`dd1cad8aafe9f4bae4016236ece608f6436b964e08af97a4f2a180e8dccd8785`
- 导入日期：2026-08-25
- 预期 Git 标签：`legacy-stage2-2025`

在取得可运行、可计分的基线前，不应直接重写策略或大规模拆分 `rdfw.cpp`。任何与该目录的差异都必须能够通过 Git 和逐题回归解释。

## 文件哈希

```text
9ad5afc9d40e6e92341b7e38e1b8699f10e56ffad18cd41a2bc1fe7abf5df936  CMakeLists.txt
746b17d5c62ae2d3d8f1e300a849f1d019458eb11641cd48ecbc9bad113e1fc9  debuglog.hpp
adcf1e3b5e63d3f0d3bd798b5a5952227d8c6bef279215f32a03cefa22b9c187  main.cpp
ee0bf43aafa2be02c02362ee16f32bf3c8ad949fb3fcc4f7f646901b480e5936  parser.cpp
b6efd33040703d51483d6d303be9d1decde72f492275d1abe78ddbd2fd449887  parser.hpp
9d1d41367ff16871647fcc6bd95aa114fea197da5c3cd22435a611f6d39483e3  rdfw.cpp
5c29620a3b0846807c4edf5a6a9f5c53313c171e9440a7be1c61b7175c533397  rdfw.hpp
66f951c478092c11bf1e29894401401a55c0f26cfc4cf038acfeb1d6a8515a41  words.txt
```
