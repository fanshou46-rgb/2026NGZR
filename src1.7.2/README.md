# src1.7.2 位置概率与有界 Probe

对应历史 1.8，从 1.7.1 增加每个物体的位置概率、带噪询问、受限开柜观察、有限约束代价交换，以及规划线程退出同步。询问是弱线索，概率参数尚未校准。

本轮逐版复核和未修复问题见 [审计说明](../docs/AUDIT_1.7.2_1.7.4.md)，24 道独立新题的完整对照见 [新题报告](../validation/review-20261004/REPORT.md)。历史发布记录见 [RELEASE_1.7.2.md](docs/RELEASE_1.7.2.md)，实现与机器人流程见 [IMPLEMENTATION.md](docs/IMPLEMENTATION.md) 和 [ROBOT_FLOW.md](docs/ROBOT_FLOW.md)。不同轮次的分数不能直接相加。

使用已有官方 Linux SDK，从仓库根目录在 WSL/Linux 构建；输出目录应是新的：

```sh
cmake -Hsrc1.7.2/tests -B/tmp/rdfw172-unit -DCMAKE_BUILD_TYPE=Release -DOFFICIAL_SDK=/tmp/env-release-2026-search
cmake --build /tmp/rdfw172-unit -- -j2
(cd /tmp/rdfw172-unit && ctest --output-on-failure)
```

完整四版新题复跑入口见 [review 工具说明](../tools/review_172_174/README.md)。
