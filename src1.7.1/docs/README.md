# src1.7.1

本版本在 src1.7 的 Stage 2 停滞分支加入有界 Probe。设计和构建/复跑入口见
[PROBE_LAYER.md](PROBE_LAYER.md)，canonical / mutation 审计见 [PROBE_AUDIT.md](PROBE_AUDIT.md)，
本次发布结果见 [RELEASE_1.7.1.md](RELEASE_1.7.1.md)。

[UNIFIED_SCHEDULER.md](UNIFIED_SCHEDULER.md) 保留继承调度说明并标注新入口；
[RELEASE_1.7.md](RELEASE_1.7.md) 和下文保留历史资料，不代表本次验收结果。

## 历史基线：src1.6.7-200ms

基于独立保留的 src1.6.7。产品文件仅 rdfw.hpp 一行差异：
`std::chrono::milliseconds plan_safety_margin{300}` 改为 `{200}`。
DeadlineManager 的 5000 ms 总期限、Multi-GOTO 的 100 ms 尾部预留、动作估时、
搜索 CPU 预算、评分和任务排序均保持原值。CMake 项目版本号与日志标记保留基线值，
本版本通过目录名、源码哈希和二进制哈希辨识。

本版本的复跑入口：

```sh
python3 "/path/to/src1.6.7-200ms/tests/run_deadline_ab.py" \
  --output /tmp/rdfw-deadline-ab-new --rounds 3
```

需要 WSL2 Ubuntu-18.04、g++ 7.5.0 和官方 SDK `/home/yifan/env-release-2026`。
输出目录必须全新；脚本不删除文件。两版分别编译，使用同一题目、固定种子 20260924、
5000 ms 平台时限和相同 planner mode，串行交替 AB/BA 运行，关闭 StageTiming。

主实验覆盖 33 道可原样评分的 realcompetiton_2024 比赛题和 37 道既有 release fixtures，
默认 off 模式、IT/NT、3 轮，共 420 对；7 道 decision/combinatorial fixtures
另以 guarded 模式运行 3 轮，共 42 对。02 原题 XML 无法建立，04/05 原题官方评分失败，
按已有验收记录排除；不修改题源。

`tests/deadline_sensitivity_tests.cpp` 仅更新测试预期为 200 ms，并增加 299/300/301 ms
的精确门控边界。直接调用 DeadlineManager 的显式 300 ms API 测试保留，验证类本身未改。
其余本地测试继承基线并全部执行。

本次结果和原始证据见 `../test-results/deadline-ab-20260928/REPORT.md`。
官方总分按平台分数封顶 1000 后汇总，原始分数另存；目标数取官方 ASP 终态。
超时、失败和未评分运行均保留并计入分母。同种子重复用于观察墙钟波动，
不能视作独立随机场景。

本目录其他报告和测试工具继承 src1.6.7，保留历史记录；它们描述的是 300 ms 基线，
不作为 200 ms 版本的验收结论。200 ms 验收以本入口和本次配对报告为准。
