# 约束换目标测试题

这组题检验：牺牲一条原本满足的约束后，新增目标的得分能否超过约束损失与动作成本；若不能，机器人应停手。题目同时覆盖 Stage 1 和 Stage 2。计分比较使用确定性的基础分：`40 × 完成目标数 + 20 × 满足约束数（至少完成一个目标时）− 动作成本`。完整官方得分还包含时间因素，因此另用 SDK 实际得分与不动作对照比较。

| 文件 | 阶段 | 设计意图 | 期望决策 |
| --- | --- | --- | --- |
| `01-one-goal-loss.xml` | 1 | 红书已在托盘上，取书与去柜子目标已满足；把书放入柜子会损失取书目标及关柜约束 | 不动作；基础分保持 100 |
| `02-two-goal-profit.xml` | 1 | 为把书和杯子放入柜子，允许损失关柜约束 | 执行；净收益为正 |
| `03-four-goal-reordered.xml` | 1 | 四个物品放入柜子，目标顺序反转 | 执行；检验组合收益不依赖固定顺序 |
| `04-stage2-two-goal.xml` | 2 | 同类双目标，但开启缺失／错误／回答环境标志 | 在感知后执行有利交换 |
| `05-near-shared-goals.xml` | 1 | 书离开桌子，损失“靠近桌子”约束，同时满足放置与多个位置目标 | 执行；检查单动作带来的共享收益 |
| `06-inside-shared-goals.xml` | 1 | 书离开柜子，损失“在柜中”约束，同时完成交付与位置目标 | 执行；检查另一类约束与共享收益 |

测试脚本另包含仓库原有的 `题目/liuyifan1.0/05.xml` 作为四目标基线，显示为 `07-existing-four-goal`。每题均在 IT／NT 两种语言模式下运行，并与 SDK 自带的不动作客户端 `bin/example` 成对比较；期限为 5 秒。

运行示例（在可运行 SDK 的 Linux／WSL 中）：

```bash
python3 src1.5/tests/run_constraint_tradeoff.py \
  --sdk /path/to/env-release-2026 \
  --output /tmp/constraint-tradeoff-run
```

`--sdk` 必须指向已能在当前 Linux 系统运行的 SDK 目录。修改前的结果见[基线报告](../../test-results/constraint-tradeoff-src1.5-20260924-final/REPORT.md)，修改后的结果见[约束收益规划报告](../../test-results/constraint-tradeoff-src1.5-20260924-implemented/REPORT.md)。
