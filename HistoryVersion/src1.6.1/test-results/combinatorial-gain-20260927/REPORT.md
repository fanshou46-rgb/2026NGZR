# 1.6.1 多目标组合收益题

这四道 Stage 1 题专门检验任务执行顺序。每个目标都能独立完成；同一房间里的目标集中执行可以少走路。题目按原始顺序交替指向不同房间，因此 1.6 的顺序执行与 1.6.1 的分组决策有可测的分差。

题目位于 [`tests/fixtures/combinatorial_gain`](../../tests/fixtures/combinatorial_gain)，可直接作为官方 SDK 的 XML 输入；`<instr>` 和 `<nl>` 分别用于 IT、NT 模式。环境关闭误报、错误信息和问答，四题均无额外约束。

| 题目 | 目标及原顺序 | 可行任务顺序 | 1.6 移动次数 | 1.6.1 移动次数 | 基础分 1.6 → 1.6.1 | 全排列最优基础分 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [01 双房间四目标](../../tests/fixtures/combinatorial_gain/01-two-rooms-four-goals.xml) | 开 2、关 3、关 4、开 5；房间 2→3→2→3 | 24 | 4 | 2 | 136 → 144（+8） | 144 |
| [02 双房间五目标](../../tests/fixtures/combinatorial_gain/02-two-rooms-five-goals.xml) | 开 2、关 3、开 4、关 5、开 6；房间 2→3→2→3→2 | 120 | 5 | 3 | 170 → 178（+8） | 182 |
| [03 双房间六目标](../../tests/fixtures/combinatorial_gain/03-two-rooms-six-goals.xml) | 开 2、关 3、开 4、关 5、开 6、关 7；房间 2→3→2→3→2→3 | 720 | 6 | 2 | 204 → 220（+16） | 220 |
| [04 三房间六目标](../../tests/fixtures/combinatorial_gain/04-three-rooms-six-goals.xml) | 开 2、关 3、开 4、关 5、开 6、关 7；房间 2→3→4→2→3→4 | 720 | 6 | 3 | 204 → 216（+12） | 216 |

例如第 03 题，1.6 依次往返房间 2 和 3，执行 6 次移动；1.6.1 先处理房间 2 的三个目标，再处理房间 3 的三个目标，只需 2 次移动。每减少一次移动，基础分增加 4 分。第 02 题仍比穷举最优少 4 分，说明当前分组搜索在五目标题上还有改进空间。

## 官方配对结果

两版使用同一套官方 SDK、同一批 XML、同一随机种子 `20260924`。基线为 1.6；当前版为 1.6.1，开启 `RDFW_TASK_GROUP_MODE=guarded`。八组运行状态均为 `ok`，种子均得到服务端确认，所有目标均完成。

| 题目 | IT 官方分 1.6 → 1.6.1 | NT 官方分 1.6 → 1.6.1 | IT/NT 基础分提升 |
| --- | ---: | ---: | ---: |
| 01 | 198 → 212 | 202 → 212 | +8 / +8 |
| 02 | 214 → 232 | 216 → 236 | +8 / +8 |
| 03 | 234 → 272 | 226 → 270 | +16 / +16 |
| 04 | 242 → 264 | 240 → 266 | +12 / +12 |

官方分数含耗时奖励，同一道题两次运行的耗时会变化；基础分只按完成目标和动作成本计算，因此上表用基础分评估路线收益。第一次试跑和本报告的第二次运行，八组基础分与移动次数完全一致。上述题目是定向构造的回归题，用于验证 1.6.1 的适用场景；它们不代表原先 60 题的总体分数会同比上升。

[`results.json`](results.json) 保存每次运行的动作序列、基础分、官方分与决策日志；同目录保存完整客户端和服务端日志。[`oracle.json`](oracle.json) 保存全排列最优值，并校验了两版每条动作序列对应的基础分。生成脚本为 [`generate_combinatorial_gain.py`](../../tests/generate_combinatorial_gain.py)，独立穷举校验脚本为 [`oracle_combinatorial_gain.py`](../../tests/oracle_combinatorial_gain.py)。

复现时，在 WSL 内以仓库根目录为工作目录，先构建 1.6 与 1.6.1 的 `example`，再运行：

```sh
python3 src1.6.1/tests/generate_combinatorial_gain.py
python3 src1.6.1/tests/run_guarded_compare.py \
  --sdk "$SDK" --runner 'src1.1.2 (x)/tools/baseline.py' \
  --baseline "$V16_EXAMPLE" --current "$V161_EXAMPLE" \
  --words src1.6.1/words.txt --seed-library "$SEED_LIBRARY" \
  --seed 20260924 --modes it nt \
  --case-dir 1:src1.6.1/tests/fixtures/combinatorial_gain \
  --output "$RESULT_DIR"
python3 src1.6.1/tests/oracle_combinatorial_gain.py \
  --fixture-dir src1.6.1/tests/fixtures/combinatorial_gain \
  --results "$RESULT_DIR/results.json" --output "$RESULT_DIR/oracle.json"
```

本次基线程序 SHA-256 为 `7829402e7fb6d1043568f9997bab03b11c309d385216f368b29455c47f2ef03b`，1.6.1 程序为 `b95d8dfb0413fb703fb503c71120d0aa48d6193be78dc71271d45d78f3554ee2`，固定种子库为 `427d6227defa007f113c9e26dc46d3cda32aa1c0fd13fb8e7136c224bb6ea2b9`。
