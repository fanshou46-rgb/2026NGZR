# 1.6.7.1-200ms

从 `src1.6.7-200ms` 独立派生的生命周期强化候选。原 `src1.6.7-200ms` 和基于 300ms 的 `src1.6.7.1` 均不修改。

产品代码沿用 `src1.6.7.1` 已验证的 H1 退出/初始化保护，但规划安全余量保持为 200ms。`tests/audit_derivation.py` 逐字节检查派生关系，结果与完整源码差异见 `docs/DERIVATION.json` 和 `docs/source.diff`。只有三个顶层产品文件不同于原 200ms：`CMakeLists.txt`、`rdfw.cpp`、`rdfw.hpp`；版本日志标明 200ms 派生版本。

代码目标是避免 SDK 结束规划时 `Fini` 与仍在运行的 `Plan` 交错清理内部状态，并给 `isMultiGotoMode` 明确初值。它不调整任务顺序、必要感知、约束选择或其他规划算法。综合 200 题的对照记录在 `test-results/comprehensive200-20261006/`；评价以原 200ms 为配对基线，300ms 历史结果单独列出。
