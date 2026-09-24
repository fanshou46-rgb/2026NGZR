# liuyifan1.0

6道2025规则原型题，附WSL2 Ubuntu 18.04官方平台测试结果。当前求解器：src1.3.3-fixed。

- [分数报告](SCORE_REPORT.md)：主测试、随机种子复测、逐次分数与原始证据。
- [执行策略报告](STRATEGY_REPORT.md)：真实动作序列、收益取舍、04失分原因、05内部估分偏差。
- [题目设计](DESIGN.md)：环境、IT/NT、参考策略与合规说明。
- [scores.csv](scores.csv)：26次官方运行的结构化结果。
- [test.list](test.list)：仅列出本批6道题。

|题号|题型|阶段|
|---|---|---|
|[01](01.xml)|自由终态汇聚|1|
|[02](02.xml)|搬运与到达共享终态|1|
|[03](03.xml)|must-near 纠错与缺失补全|2|
|[04](04.xml)|容器状态纠错与合法语言扰动|2|
|[05](05.xml)|牺牲一个约束解锁四个目标|1|
|[06](06.xml)|放弃低收益目标保住三个约束|1|

## 复现

从仓库根目录，在WSL2 Ubuntu-18.04中运行：

```bash
python3 题目/liuyifan1.0/tools/check.py
python3 题目/liuyifan1.0/tools/run.py --output test-results/liuyifan1.0-rerun-001
```

输出目录必须尚不存在。run.py重新编译求解器、验证IT/NT解析并执行26次官方运行；官方平台使用端口7932，脚本在运行前检查占用。报告生成器report.py绑定本次-final证据目录。

test.list同时含两个阶段，竞赛客户端按每题对应stage运行；本批runner会自动选择。正式按阶段提交时，应分别使用Stage 1的01/02/05/06与Stage 2的03/04。

参考客户端只用于作者可行解验收，依据reference-plans执行固定动作；原版求解器测试不读取这些动作，也没有加入题号特判。
