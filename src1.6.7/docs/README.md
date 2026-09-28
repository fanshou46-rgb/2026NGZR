# src1.6.7 State Model Closure / Release Hardening

基线为已验证、独立保留的 src1.6.6。本版说明见 [mutation closure](MUTATION_CLOSURE.md)、[逐行 direct-access 索引](DIRECT_ACCESS_AFTER.md) 和 [发布报告](RELEASE_1.6.7.md)。

统一 gate 在 WSL Ubuntu-18.04 / g++ 7.5 / CMake 3.10 执行。SDK 只读；output 必须为全新目录；官方服务器独占端口、全部串行。自动执行 CTest、ASan+UBSan、基线 before probes、AB/BA 微基准、73 个 exact deadline assertions、118 对官方 regression、6 对独立 StageTiming、36 对宽覆盖 self-pair controls，以及 source/build/SDK/problem hash 审计和原始证据归档。

```sh
python3 /path/to/src1.6.7/tests/run_closure_gate.py \
  --output /tmp/rdfw-167-new-gate \
  --baseline /tmp/rdfw-166-final/build-release/example \
  --seed-library /tmp/rdfw-165-official/seed_rng.so
```

baseline 必须匹配 src1.6.6 的已验证 executable SHA-256。gate 固定官方 5000 ms 与 seed 20260924，performance instrumentation 与正式 regression 分开。若出现动作/基础分差异，`difference-classification.json` 标为 REVIEW_REQUIRED，依据 first-divergence logs、deadline gate 和 self-pair controls 填写 `docs/DIFFERENCE_REVIEW.json`，再运行归档脚本；原始 pair 保留。

```sh
python3 /path/to/src1.6.7/tests/audit_mutation_closure.py
python3 /path/to/src1.6.7/tests/archive_closure_gate.py /tmp/rdfw-167-new-gate
```

126 个 CTest 含官方评分语义，125 个 ASan+UBSan tests 不链接未插桩的外部 libasp。源码、二进制、SDK 完整文件树、题源和构建命令在 `test-results/validation-20260928` 中可核对。`official-raw-evidence.zip` 与 `local-raw-evidence.zip` 保留完整日志/JSON/answer sets，发布二进制同时归档。

tests 下继承的一次性开发脚本与旧版本 release 工具作为历史源码保留；本版验收入口是 run_closure_gate.py / audit_mutation_closure.py / archive_closure_gate.py。implement_hardening.py、finish_hardening.py、optimize_terminal.py 是开发记录，完成版本不重复运行。全程采用新目录和逐文件写入，不进行批量删除。
