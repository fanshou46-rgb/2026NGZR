# 部分可观测规划的 GitHub 参考

检索日期：2026-10-03。以下是设计参考；当前 src1.8 没有引入这些项目的运行时依赖或复制其代码。

| 项目 | 已核对的实现 | 对当前仓库的启发 | 接入顺序 |
|---|---|---|---|
| [h2r/pomdp-py](https://github.com/h2r/pomdp-py) | [Tiger 的带噪观测模型](https://github.com/h2r/pomdp-py/blob/main/pomdp_py/problems/tiger/tiger_problem.py)、[有限深度 value_function](https://github.com/h2r/pomdp-py/blob/main/pomdp_py/algorithms/value_function.py) | 单独定义 `P(answer|world, action)`；对可能回答分支加权计算后续价值。错误答案改变 belief，不能直接改变已验证事实。 | 先把 AskLoc、Sense、动作反馈的模型与估值接口分开；再在小场景离线核对两步分支的正确性。 |
| [AdaCompNUS/despot](https://github.com/AdaCompNUS/despot) | README 的 C++ API、黑盒模拟接口与 [Tiger 示例](https://github.com/AdaCompNUS/despot/blob/master/examples/cpp_models/tiger/src/tiger.cpp) | 用有限采样场景评估信息动作后的不同结果，考虑计划复杂度及执行成本。语言与本仓库接近，适合后续实验。 | 先做独立离线实验；真实 SDK 调用不能用作搜索采样，需构建无副作用的世界模型。 |
| [JuliaPOMDP/BasicPOMCP.jl](https://github.com/JuliaPOMDP/BasicPOMCP.jl) | README 的 `max_time`、`max_depth`、`tree_queries` 与 belief update 说明 | 搜索预算必须明确；选择动作的搜索器与更新 belief 的模块可以独立。每次真正观测后再规划。 | 借鉴预算、深度与回退规则。当前不需要增加 Julia 部署依赖。 |

## 本轮采用与后续实验

本轮采用：belief 与 canonical 分离，显式观测噪声假设，单次探测后重规划，单题次数/成本/时间预算，完整投影与实际反馈的隔离。

下轮优先实验：对 AskLoc 的 `at / inside / not_known / invalid` 分支，分别估计下一步最优可执行计划，按观测概率加权；比较“现在执行”“现在询问”“移动观察”“停止”的净收益。当前 `expected_gain` 是排序启发式，不能当作上述完整分支计算或已校准概率。

再下一步：把实际动作造成的状态迁移、封闭容器的可见性以及询问答案域写入独立生成模型，然后比较小规模场景搜索与现有 greedy。先证明固定预算下目标数、基础分与稳定性改善，再扩大搜索规模。

验收要包含错误但格式合法的回答、回答重复、未知回答、容器遮挡、动作失败及耗时不足；按多种随机种子保留完整结果，不能只展示正收益题。

## 不确定性与评分约束

本轮的 Move+Sense 可以在风险额度内交换记分约束，但不能把预计收益当作事实确认或物理许可。信息估计、目标机会估计和成本分别记录；目标机会最多覆盖三个对象绑定组。一次真实观测后的下一次决策仍从 canonical 和当前约束账本重新计算。

BasicPOMCP 的 belief update 说明特别提醒：决策树中的模拟样本不能直接充当可靠的观测更新。这与本仓库的边界一致：shadow Sense 是用假设生成的预测，不能写入真实 belief 或 confirmed facts。

## 概率模型的下一轮实施顺序

1. 定义独立 ObservationModel，分别描述 AskLoc 的带噪回答、Sense 的局部可见性及动作成功/失败反馈。本地回答域与 SDK 实际域之间的缺口用显式未知质量表示；封闭容器看不见不能标注为不存在。
2. 建立小规模、无副作用的假设世界和两步回答分支。每个分支更新模拟 belief，调用现有候选评估器计算后续可执行价值，比较停止/直接执行/询问/观察的期望净收益。不得调用真实 SDK 采样，不得把模拟状态写入真实 canonical。
3. 从真实反馈采集带来源的样本。只有后来被真实 Sense 或动作确认的答案才有可用真值标签；尚未验证的回答不标为正确，选择性可验证样本的偏差要单独报告。分别拟合回答可靠性、可见性和动作耗时，并在独立题目/种子上检查概率校准及期限违约。
4. 再引入有限场景搜索。固定总搜索预算、场景数和深度，叶子用现有可执行普通规划估值；失败、预算耗尽或无足够证据时回退。按完整目标、历史约束、动作成本、时间及退化率验收，不能只比较平均总分。

本轮没有实现以上完整模型；已提供可供下一轮替换的 belief/信息估值接口、真实反馈日志和对照基线。
