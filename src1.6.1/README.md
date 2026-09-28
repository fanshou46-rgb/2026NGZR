# src1.6.1

这是独立的 1.6.1 源码目录，包含规划器、词典、测试、设计记录和本轮验收结果。原 1.6 保留在相邻的 `src1.6`。

- [版本说明](docs/RELEASE.md)
- [决策实现计划](docs/DECISION_IMPLEMENTATION_PLAN.md)
- [官方配对报告](test-results/src1.6.1-guarded-20260926/REPORT.md)
- [多目标组合收益题与实测结果](test-results/combinatorial-gain-20260927/REPORT.md)
- [旁路阶段报告](test-results/user-stage60-shadow-20260925/REPORT.md)
- [目录拆分复核](test-results/SEPARATION_VALIDATION.md)

默认使用原策略；设置 `RDFW_TASK_GROUP_MODE=guarded` 后，才在受支持的 Stage 1 场景尝试 1.6.1 任务组决策。

官方配对是在目录拆分前完成的，因此 `results.json` 保留当时的输入路径；每一道题的原始内容已收录在报告的 `official-inputs.zip` 中。
