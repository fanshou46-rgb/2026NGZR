# 原 200ms 与 1.6.7.1-200ms：综合 200 题证据

2026-10-06 正式对照：200 题 × IT/NT × 两版 = 400 组、800 次官方 SDK 运行。180 道正常题形成 360 组，20 道刻意非法题形成 40 组。默认策略、5000ms、种子 20260928、一轮、串行 AB/BA 交替；预试 3 题、6 组、12 次单独保存，不并入成绩。

正常题 G 2020→2020、C 11084→11084、K 14800→14800、基础分 287680→287680，360 组动作序列全部一致。正式分 311040→311054（+14）、平台秒数 613.963→613.484（−0.479）；43 组分数升、44 组降、273 组相同，87 组差异全是时间奖励。两版 0 SDK 截止、0 外部超时、0 运行失败、0 评分缺失。非法题两版动作与状态一致，各 4 `failed`、36 `ok`；12 组 G/C 无官方 ASP 答案，单独标为缺失。

独立审计重新读取 800 次服务器动作、官方 ASP 答案和原始分，保存字段 0 处不一致。运行器结束时验证源码、题目、SDK、二进制未变，全部种子确认。原 200ms 的退出清理与构造初值反例分别退出 42、43；候选普通 Release 134/134。O2 sanitizer 的首轮 8 项生命周期检查通过，但完整套件在 `input_safety_tests` 高 CPU 后停止，后续连续专项运行也有不稳定超时；这项检查不记为通过。详见 [发布说明](../../docs/RELEASE_1.6.7.1-200ms.md)。

可直接核对的文件：

- [SUMMARY.json](SUMMARY.json)：正常、非法、Stage 1、Stage 2 汇总，包括缺失、失败、超时及逐组变化数。
- [PAIRS.csv](PAIRS.csv) 和 [results.jsonl](results.jsonl)：400 组原始配对字段与每次运行目录。
- [REGRESSIONS.json](REGRESSIONS.json)、[BEHAVIOR_DIFFERENCES.json](BEHAVIOR_DIFFERENCES.json)、[difference-classification.json](difference-classification.json)：逐组退化、行为差异与时间奖励分类；行为差异为空。
- [input-audit.json](input-audit.json)、[build-audit.json](build-audit.json)、[final-audit.json](final-audit.json)：源码、题目、SDK、工具、种子、编译器及二进制冻结。
- [git-byte-audit.json](git-byte-audit.json)：两版共 50 个产品文件的实测字节与 Git 暂存字节核对；仅 CRLF/LF 换行不同，标准化后无语义差异。正式运行使用的原始字节保存在证据包。
- [independent-log-audit.json](independent-log-audit.json)：800 次日志/ASP/评分重算及原文件哈希，0 处差异。
- [HISTORICAL_300.json](HISTORICAL_300.json)：与上一轮 300ms 测试按题目/模式/种子对齐；跨轮时间分仅作参考。
- [checks](checks)：普通测试、基线反例、O2 sanitizer 构建及未完成/补充运行原日志。

[EVIDENCE.zip](EVIDENCE.zip) 保存正式/预试全部原始运行目录、两版临时源码副本、编译日志和可执行文件及检查日志。ZIP 中 `MANIFEST.json` 以 SHA256 将 17139 个原逻辑文件映射至 4346 个去重内容块；逻辑原字节总量 2105286891，压缩包 22166996 字节。[EVIDENCE.receipt.json](EVIDENCE.receipt.json) 记录归档 SHA256 和逐项 CRC/SHA256 验证。检查构建中间对象未归档；官方对照的两版生产二进制和构建输入均归档。

300ms 历史结果：原版 G2020/B287680/F311080，H1 G2020/B287680/F311078；本轮 200ms 的 +14 与历史 300ms 的 −2 都只涉及时间奖励，没有解题行为变化。两个运行时间窗口的分数差不能解释为 200ms/300ms 余量的稳定因果效果。
