# src1.9 概率观测模型开发版

从 src1.8 独立复制，旧版本保留。当前实现带噪回答的 Bayes 更新、按回答选择后续路线、真实感知的可见性排除与验证路线缓存。完整开发记录与已知退化见 [PROBABILITY_MODEL.md](docs/PROBABILITY_MODEL.md)；从接收题目到结束的逐步决策见 [ROBOT_FLOW_1.9.md](docs/ROBOT_FLOW_1.9.md)。这份记录是本版本的状态入口，其他继承的历史文档保留各自版本语境。

本次普通测试 232/232、内存检查 231/231；最终 56 对平台对照基础分合计 +323、目标 +8，仍有 14 对基础分退化。完整证据见 [开发复核报告](test-results/validation-20261004/REPORT.md)。

本版本仍用于开发对照。目标之外的位置、柜门、手持/托盘未知状态尚未形成完整联合场景；不能把未完成的续规划估值当成已经证明没有探索收益。新增模型尚未完成全题、多种子校准。

## 复跑

WSL Ubuntu-18.04 / g++ 7.5，使用现有官方 SDK。以下为仓库根目录执行的示例，输出目录必须不存在；旧结果不会被替换。

```sh
cmake -Hsrc1.9/tests -B/tmp/rdfw19-unit -DCMAKE_BUILD_TYPE=Release -DOFFICIAL_SDK=/tmp/env-release-2026-search
cmake --build /tmp/rdfw19-unit -- -j3
(cd /tmp/rdfw19-unit && ctest --output-on-failure)
bash src1.9/tests/sanitize_probe.sh /tmp/rdfw19-asan
python3 src1.9/tests/run_probe_compare.py --output src1.9/test-results/development-example --sdk /tmp/env-release-2026-search --suite legacy --rounds 1 --seed 20260924
```

测试字典在临时输出中转换为 LF，不更改原字典。平台配对使用相同输入、5000 ms、默认策略、串行 IT/NT 及交替执行顺序，保存两版全部动作、评分、时间、超时和探测日志。`final-audit.json` 检查源码/SDK/输入未被测试修改；它不是模型性能验收。
