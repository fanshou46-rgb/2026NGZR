# 仓库结构

```text
2026NGZR/
├── 2026工作日志/          # 2026 年各轮版本迭代与变更记录
├── 定时器/                # 比赛定时器相关文件
├── 题目/                  # 赛题、测试数据与题目图片
├── docs/                  # 规则、代码说明与总结文档
├── robocup2025工作日志/   # 2025 年历史工作记录
├── scr1.1/                # scr 1.1 版本代码
├── scr1.1.2/              # scr 1.1.2 版本代码
├── scr1.2/                # scr 1.2 版本代码、测试、工具与产物
├── scr1.3/                # scr 1.3：must-near 关系、证据传播与状态更新修复
├── src1.3.1/              # src 1.3.1：确定性终态检查、基础分与时间预算基础设施
├── src1.3.2/              # src 1.3.2：Stage 3B 确定性候选计划边际收益 shadow 评估
├── src1.3.3A/             # src 1.3.3A：输入、Instruction Schema 与索引安全层
├── src1.3.3-fixed/        # 1.3.3-fixed：保留合法题语义的容错修复与逐题验收
├── src1.5/                # src 1.5：候选决策反馈记录
└── src1.6/                # src 1.6：约束收益决策与 Stage 2 未知事实校验
```

最新开发版本：`src1.9/`，在独立观测模型中按回答更新概率、选择验证路线，
并修正真实可见性过滤和未来绑定资格。流程见
`src1.9/docs/ROBOT_FLOW_1.9.md`，模型与 GitHub 参考见
`src1.9/docs/PROBABILITY_MODEL.md`；复核报告见
`src1.9/test-results/validation-20261004/REPORT.md`。
最终 56 对开发对照基础分合计 +323、目标 +8，仍有 14 对基础分下降，
模型尚未覆盖完整联合隐藏状态及校准，不建议直接替换比赛版本。

上一实验基线：`src1.8/`，在 `src1.7.1` 上加入独立位置 belief、带噪询问、
受限开柜观察和有界记分约束交换，并扩展已验证输入下的 Stage 2 规划。
询问只提供弱线索，真实事实仍由感知/动作证据确认。完整流程见
`src1.8/docs/ROBOT_FLOW.md`，实现与 GitHub 参考见 `src1.8/docs/IMPLEMENTATION.md`
和 `src1.8/docs/GITHUB_INSPIRATION.md`；实测收益、退化、超时与范围见
`src1.8/docs/RELEASE_1.8.md`。概率参数尚未校准，本版本用于可复跑的开发对照。

Probe 基线版本：`src1.7.1/`，在 `src1.7` 的真实 Stage 2 停滞分支加入有界 Probe，
保留正常 greedy、Stage 1、canonical authority、约束交换、基础分及 deadline 参数。
设计、构建与复跑入口见 `src1.7.1/docs/PROBE_LAYER.md`，本次验证见
`src1.7.1/docs/RELEASE_1.7.1.md`；完整收益、退化和非法输入结果分别保留。

基线版本：`src1.7/`，正常启动使用 greedy + 内部 guarded 的统一决策流程，
不需要策略模式配置。实现说明见 `src1.7/docs/UNIFIED_SCHEDULER.md`，
验证与完整退化记录见 `src1.7/test-results/validation-20261002/REPORT.md`。
该版本保留用于开发回归；是否用于比赛应先阅读报告中的 Stage 2 退化结论。

此前策略实验：`src1.6.7-200ms/` 基于 `src1.6.7/`，仅将普通计划的
deadline 安全余量从 300 ms 调整为 200 ms；配对重复测试见
`src1.6.7-200ms/test-results/deadline-ab-20260928/REPORT.md`。

# 提交要求

1. 每修改一次代码，都必须进行一次新的版本迭代并单独提交。
2. 不直接更改已有版本的代码；以当前版本为基础创建新的版本目录，在新版本中完成修改。
3. 每轮版本迭代都必须同步在 `2026工作日志/工作日志.md` 中记录本轮更改，至少写明日期、版本号、更改内容和验证结果。
4. 代码与对应的工作日志必须放在同一次提交中，确保提交记录与版本迭代一一对应。
5. 提交信息使用 `版本号: 更改摘要` 的格式，例如：`scr1.3: 优化路径规划`。
