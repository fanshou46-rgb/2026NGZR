# 四版本复核工具

本轮结果见 [REPORT.md](../../validation/review-20261004/REPORT.md)，逐版审计见 [AUDIT](../../docs/AUDIT_1.7.2_1.7.4.md)。

`generate_questions.py` 生成 24 道题，不读取机器人结果。题目已经冻结；已有目标目录时拒绝覆盖。清单的设计种子、运行种子、题目哈希、参考动作和预先指定的分组均可检查。

在已经构建好官方 Linux SDK 的 WSL/Linux 环境中，从仓库根目录执行：

```sh
python3 tools/review_172_174/run_review.py \
  --sdk /absolute/path/to/env-release-2026 \
  --out validation/a-new-review-output
```

输出目录必须是新的。工具默认重新构建四个版本，再运行 48 次参考验证及 384 次串行对照；不会依赖仓库中未提交的旧二进制。`--reuse-build-root` 可指定含 `src1.7.1` 至 `src1.7.4` 子目录的构建缓存，每个子目录必须含 `build.json` 和 `example`，全部生产源码/词典与二进制哈希必须匹配。

`reference_client.cpp` 只用于验证题目可行和官方得分。参赛机器人不会读取参考动作。参考动作不保证最优；完整任务、颜色条件和英文句子都在题目 XML 中。

`semantic_counterexamples.cpp` 用真实 SDK 成败反馈检查当前 RDFW 的事实判断；`../review_joint_multi_inside.cpp` 检查 SDK 与联合模型的关系保存差异。它们成功退出表示**成功复现已知错误**，不能当成产品正确性通过。生产修复应另建下一版本，并把相应断言改成正确性要求。

已执行的 384 次对照使用改日志标签之前的已验证历史二进制，精确核心源码和执行工具快照位于证据 ZIP 内。当前脚本在对照结束后补了默认全新构建、可选构建缓存和缺失评分保护；历史记录不改写。当前版本的日志标签和比较脚本默认基线已经修正，不把这些标签改动计为性能收益。

本轮汇总与归档入口是 `../summarize_review_172_174.py` 和 `../package_review_172_174.py`。它们针对本轮固定输出目录，用于检查全部格数、种子、缺失与配对、执行边界、ZIP CRC 和逐文件 SHA。原始缺失/崩溃保留，不填零、不挑选重跑。
