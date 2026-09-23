# Illegal fault-model 题集

这 20 题是故意违反出题规范的负向题，不得混入正式比赛题库。文件名、目录名、
XML 顶部注释和 `manifest.csv` 均标记 `illegal`。题集包含 10 道 Stage 1 和
10 道 Stage 2，运行入口为 `src1.3.3B/tests/run_illegal_fault_model.py`。

Stage 1 聚焦 duplicate、malformed constraint 与确定性 WorldState 不变量；
Stage 2 增加语义别名/对称关系去重，以及 B 版明确未覆盖的 duplicate info、
初始已破坏 constraint、冲突 env 字段和平台侧 malformed XML。

所有可加载题均同时提供 IT 与 NL；本轮只运行 IT，以便针对客户端可见的
instruction stream 做稳定 A/B。NL 文本仅保证平台文档完整性，不作为 IT/NL
离线等价校验样本。

正式运行结论见 [REPORT.md](REPORT.md)，便于机器处理的逐题结果见
[results-summary.csv](results-summary.csv)。
