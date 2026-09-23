# src1.3.3B 验证与旧题行为变化

日期：2026-09-22。基线为当前 `src1.3.3A`；A 目录未修改。

## 验证结果

- Ubuntu 18.04 / g++ 7.5.0 / C++11 下重新构建，三组测试全部通过：
  `input_safety_tests`、`three_a_tests`、`question_preflight_tests`。
- ASan + UBSan（`-fsanitize=address,undefined`、链接 `-no-pie`）三组测试
  连续两轮通过，无 sanitizer 报告。该 WSL 工具链的默认 PIE sanitizer 进程曾
  在启动时 SIGSEGV、无业务栈输出；最终验证使用上述 non-PIE 配置。
- 官方 `/home/yifan/env-release-2026`，Stage 2 / IT，5000 ms，原始 01–36 XML。
  A 与最终 B 均为 35 题正常完成、0 平台硬超时；02 均在平台解析阶段失败。
- B 的 35 份 Preflight 日志均为 `world_errors=0`、`rejected=0`。
  04 的坏指令仍在继承的解析阶段隔离，不是新增 WorldState 拦截。
- 最终运行的全部 `.cpp` SHA-256 与交付源码逐一核对一致。
  Candidate、TerminalChecker、ScoreEvaluator、DeadlineManager、NL parser
  源码与 A 相同；求解策略没有重写。

原始产物（Git 忽略）：

- A 及开发轮 B：`test-results/src1.3.3B-build/official-all36/`。
- 最终 B：`test-results/src1.3.3B-build/official-final-b/`。
- 各目录含 `results.json`、逐题 client/server 日志、原始官方 evaluator 输出、
  构建命令及源文件/SDK hash。最终结论采用第二个目录的 B 结果。

可重跑：

```sh
python3 src1.3.3B/tests/run_official_compare.py \
  --sdk /home/yifan/env-release-2026 \
  --output /tmp/rdfw-preflight-official-new-run
```

输出目录必须尚不存在。可用 `--cases 16 17 25` 缩小题集，或
`--versions src1.3.3B` 只跑 B。复用仓库既有隔离 runner，SDK、题源均不改写。

## 19 道 duplicate 旧题：确定发生的语义变化

以下数值来自最终 B 的真实入口日志，而不是 XML 行数统计。
箭头表示去重前后向量长度；task 16 题、constraint 7 题，合并共 19 题。

| 2024 题号 | task raw → unique | constraint raw → unique | 去掉的 task / constraint 副本 |
|---|---:|---:|---:|
| 01 | 19 → 18 | 0 → 0 | 1 / 0 |
| 16 | 3 → 3 | 21 → 14 | 0 / 7 |
| 17 | 3 → 3 | 21 → 14 | 0 / 7 |
| 18 | 4 → 4 | 20 → 16 | 0 / 4 |
| 19 | 34 → 18 | 1 → 1 | 16 / 0 |
| 20 | 33 → 18 | 1 → 1 | 15 / 0 |
| 21 | 36 → 18 | 2 → 1 | 18 / 1 |
| 22–24（每题） | 35 → 8 | 2 → 2 | 27 / 0 |
| 25–27（每题） | 36 → 3 | 10 → 1 | 33 / 9 |
| 28 | 34 → 18 | 1 → 1 | 16 / 0 |
| 29 | 35 → 18 | 0 → 0 | 17 / 0 |
| 30 | 38 → 18 | 0 → 0 | 20 / 0 |
| 34–36（每题） | 45 → 9 | 0 → 0 | 36 / 0 |

预期变化是：同一个语义目标/约束只计一次。重复项不再增加风险表权重、
task-conflict 计数、multi-goto 聚合权重、multi-puton 数量、Terminal 条目和
ScoreEvaluator 分母/收益。仍然存在的多个**不同** goto/puton 会正常进入聚合。

本轮动作观察：

- 01、18、28、29：虽然规范化列表变化，实际动作名/参数流与 A 一致。
- 20、21、30、34–36：第一条 Move 的目的地就发生变化；22–24 第一条
  PickUp 的对象变化。它们的重复 goto 目标数/权重被改为唯一对象口径，
  这是旧聚合逻辑消费规范化输入后的预期变化。
- 25–27：动作数均为 **13 → 9**，共同前缀之后不再沿重复 puton 再尝试一次，
  转入剩余 goto；本轮官方封顶分仍均为 1000。
- 19：A 的动作流是 B 的严格前缀，动作数 33 → 37；规范化减少候选处理量，
  既有时间门控下本轮多执行了一组动作。耗时收益不保证每轮相同。
- 16/17：约束数明确减少，动作流也不同；16 的首次差异为
  `AskLoc(9): at(9,22) → at(9,11)`，不能把整段动作差异都归于去重。

这些题本身违反当前“不重复 task/constraint”的出题要求。
新版本不为旧题恢复副本权重，也不以“保持旧题所有动作/分数不变”为验收标准。
任何变化仍须结合重复 key、实际观测和源码路径解释，不能仅凭题号豁免缺陷。

## 普通题与分数解释

无 duplicate 且能运行的 16 题为 03–15、31–33。
其中 03–05、09–12、31–33 共 10 题的动作名/参数流完全一致。
其余 6 题首次分叉都在同一个 AskLoc 请求的回答：

| 题号 | 请求 | A 返回 | B 返回 |
|---|---|---|---|
| 06 | AskLoc(5) | at(5,6) | not_known |
| 07 | AskLoc(5) | at(5,6) | not_known |
| 08 | AskLoc(8) | not_known | at(8,6) |
| 13 | AskLoc(5) | at(5,2) | not_known |
| 14 | AskLoc(19) | at(19,8) | inside(19,12) |
| 15 | AskLoc(19) | at(19,2) | at(19,12) |

单轮官方分合计 **20226 → 20160**。其中 35 题 **1000 → 710**，同时存在
重复目标归一化后的聚合目的地变化和随机平台观测。本版验收依据是唯一目标/
约束口径、合法 conflict 保留及入口安全；这轮随机 Stage 2 对照不是固定证据流
的策略优劣实验。旧 evaluator 仍按题源重复条目计分，客户端的 unique goal /
constraint snapshot 与它不再一一对应，不能把两种分数当作同一量比较。

## 覆盖边界

客户端最小负向测试覆盖了用户指定的五类：duplicate task、duplicate constraint、
duplicate goto、duplicate vs conflict、malformed constraint。增加的 WorldState
检查和入口顺序也有断言。测试未新增 XML/mis/err/extra/IT-NL 离线校验或概率模型。
完整规范化和恢复边界见 [PREFLIGHT.md](PREFLIGHT.md)。
