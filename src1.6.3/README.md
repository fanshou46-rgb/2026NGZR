# src1.6.3

基于 `src1.6.2` 的独立版本。保留 1.6.2 的评分语义与资格账本，将确定下界/可能上界与 1.6.1 的决策优先级分开；只有严格区间支配才允许因评分硬淘汰。统一按平台 5000 ms 上限管理时间，修复不完整投影被当作零耗时计划的尾部门控。默认仍为 off；guarded 仍只支持原 Stage 1 范围。没有概率、贝叶斯或学习。

- [修复与验证说明](docs/RELEASE_1.6.3.md)
- [逐题、重复和性能证据](test-results/validation-20260927/REPORT.md)
- 最终配对入口：`tests/run_interval_validation.py`
- `docs/AUDIT.md` 和 `docs/RELEASE_1.6.2.md` 是继承的基线审计记录。

在 Linux/WSL 中构建本地测试：

```sh
mkdir -p /tmp/rdfw-163-tests
cd /tmp/rdfw-163-tests
cmake /path/to/src1.6.3/tests -DCMAKE_BUILD_TYPE=Debug -DOFFICIAL_SDK=/home/yifan/env-release-2026
cmake --build . -- -j4
ctest --output-on-failure
```

省略 `OFFICIAL_SDK` 运行 10 组本地测试；提供 SDK 增加包含 16 个案例的官方语义测试，合计 11 组。SDK 资源复制到独立构建目录，不修改安装目录。

官方复跑：

```sh
python3 tests/run_interval_validation.py --output /tmp/rdfw-163-new-full --full --repeats 1
python3 tests/run_interval_validation.py --output /tmp/rdfw-163-new-target --repeats 5
python3 tests/run_interval_validation.py --output /tmp/rdfw-163-new-off --quick --group-mode off --repeats 1
```

默认定向 06 IT/NT、29 IT；`--full` 覆盖基线 86 对，`--quick` 覆盖 14 对默认路径。重复轮交替执行两版；`--binaries` 可复用两个已核对哈希的构建。`RDFW_STAGE_TIMING=1` 开启固定计数器的阶段计时，仅在 Plan 结束汇总输出；默认关闭。`--diagnostics off` 可测诊断关闭路径，`tests/build_diagnostic_baseline.py` 创建只增加计时的 1.6.2 副本供性能对照。
