# src1.6.6

独立基线为已验证的 src1.6.5。事实查询统一经 `StateProvenance → ResolutionEligible → DependenciesCurrent → ResolvedState`；旧字段保留为规划假设、兼容视图和缓存。

- [发布报告](RELEASE_1.6.6.md)
- [修改前语义审计](CANONICAL_AUDIT_REVIEW.md)
- [修改前逐行索引](DIRECT_ACCESS_BEFORE.md) / [修改后逐行索引](DIRECT_ACCESS_AFTER.md)
- [最终语义审计](CANONICAL_AUDIT_FINAL.md)
- [验证汇总](../test-results/validation-20260928/summary.json) / [哈希审计](../test-results/validation-20260928/audit.json)

以下命令在 WSL/Linux 执行；将 `/path/to/src1.6.6` 换为实际路径。构建目录独立，SDK 只读。

```sh
mkdir -p /tmp/rdfw-166-unit-reproduce
cd /tmp/rdfw-166-unit-reproduce
cmake /path/to/src1.6.6/tests -DCMAKE_BUILD_TYPE=Release -DOFFICIAL_SDK=/home/yifan/env-release-2026
cmake --build . -- -j3
ctest --output-on-failure
```

共 97 个 CTest：原十组测试、20 个 state invariant、19 个 state layer、官方评分语义、33 个 canonical 用例和 14 个修复回归。sanitize 使用独立目录，不链接未插桩 SDK，共 96 个：

```sh
mkdir -p /tmp/rdfw-166-asan-reproduce
cd /tmp/rdfw-166-asan-reproduce
cmake /path/to/src1.6.6/tests -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS='-fsanitize=address,undefined -fno-omit-frame-pointer -fno-pie' \
  -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=address,undefined -no-pie'
cmake --build . -- -j3
ASAN_OPTIONS=detect_leaks=1 UBSAN_OPTIONS=halt_on_error=1 ctest --output-on-failure
```

官方 86 + 18 + 14 对与六对独立性能采样串行运行，固定种子 20260924，5000 ms 期限：

```sh
python3 /path/to/src1.6.6/tests/run_release_matrix.py \
  --output /tmp/rdfw-166-reproduce \
  --baseline /tmp/rdfw-165-closure/build-release/example \
  --seed-library /tmp/rdfw-165-official/seed_rng.so
```

output 必须是全新目录；使用已核对源码哈希的 1.6.5 基线二进制。官方服务器端口独占，不能同时启动其他回放。`package_state_release.py` 归档结果，`audit_state_release.py` 检查源码、基线、SDK、题源、二进制及 LF 词表；实际参数见发布报告。

修复前最小证据入口为 `tests/canonical_baseline_probe`，直接编译未修改的 src1.6.5。该入口 14 个断言预期失败；当前版本同一测试源码的 14 个断言全部通过。原始日志见验证目录的 `baseline-probe-*`。

`canonical_audit.py src1.6.6` 可更新修改后索引。`implement_convergence.py`、`converge_terminal.py`、`converge_mutations.py`、`converge_priority.py`、`priority_hypothesis_view.py`、`migrate_canonical_fixtures.py` 是一次性开发记录，不是验收入口，不应对完成版本重复执行。继承的旧报告/工具保留作历史记录，可能固定旧版本；当前验收使用本页入口。
