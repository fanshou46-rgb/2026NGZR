# src1.3.3B 版本说明

本目录继承 `src1.3.3A`，增加解析后、规划前的 Question Preflight：

- IT / NL 共用入口，在 `ParseInfo`、Stage 2 correction、`Cons_plan` 和所有
  规划/终态评分消费者前，对 task 与三类 constraint 做稳定语义去重。
- key 包含类别/极性、规范化谓词、完整 X/Y 对象 ID 集合；支持条件重排、
  ID/描述绑定、`in/inside`、`near/nextto` 与 near 对称关系。同位置不同对象、
  不同目标、相反动作、不同极性和 every/all 的不同对象集合仍独立保留。
- 增加 malformed constraint 局部恢复；闭合但结构非法的 wrapper 整体隔离，
  不将其 child task 升格为可执行任务。
- 对 robot/human 身份、对象注册、稳定 sort/运行时类型与 Stage 1 大物体位置
  碰撞做少量关键预检；WorldState 不可信时在规划前正常退出。
- 保留 Stage 2 未知位置/开关状态，位置碰撞不据此判为非法；稀疏 ID 占位槽
  本身保留，引用占位槽的指令局部隔离。

现有求解策略、Candidate/TerminalChecker/ScoreEvaluator 算法和概率模型保持不变；
它们消费去重后的共同向量。版本契约与负向测试见 [PREFLIGHT.md](PREFLIGHT.md)，
旧 2024 题的去重清单与官方验证见 [VALIDATION.md](VALIDATION.md)。

## src1.3.3A 继承说明

本目录完整继承 `src1.3.2`，增加输入与索引安全层，不改 Candidate
排序、选择或执行策略：

- 所有环境整数使用完整 token 的有界解析；对象 ID 限制为 `1..255`，位置
  ID 限制为 `0..4095`，输入限制为 1 MiB，防止负数下标、超大/稀疏 ID
  导致越界或无界扩容；
- 环境事实按谓词校验精确字段数，先解析后建模；`inside` / `hold` / `plate`
  在 WorldState 建立后核对引用和实际类型。单个坏事实仅就地丢弃，只有无法
  建立安全 WorldState 时整题失败；
- IT 指令按独立 form 有界建树，一个 malformed task 可在下一个 marker 处恢复；
  NL 解析对空 token、空栈、空树和空节点返回局部错误；
- `Instruction Schema` 对 task / info / cons 校验行为种类、形参数量与
  `X/Y` 绑定、对象注册身份及运行时实际类型；已由实际对象明确的缺失
  类型标记为 `INFERRED`，可安全修复的绑定元数据标记为 `REPAIRED`；
- `ObjectPtrCast` 只抛出 `std::invalid_argument` / `std::runtime_error`，关键业务路径在
  访问 `objects[id]` 或二维约束表前校验对象、位置与行列边界；
- `objects[0]` 改为不拥有的 Robot 身份视图，NL 语法树在重新解析与销毁前
  显式断开父子 `shared_ptr` 环，避免长时运行或重复非法 NL 输入累积泄漏；
- 新增 `tests/input_safety_tests.cpp`，覆盖负/超大/稀疏 ID、缺字段、非法引用、
  空节点、错误对象类型、空 `X/Y`、错误参数量及 malformed task 恢复。

14 题 Stage 2 IT 重点集全部正常退出、0 平台硬超时，完整轮官方分合计
10012（`src1.3.2` 同集 9920）。随机回答导致的 13 题单轮波动复跑后回到基线
496 分。详见 `test-results/realcompetition-src133A-input-safety-20260922/report.md`。

## src1.3.2 / Stage 3B 说明

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
