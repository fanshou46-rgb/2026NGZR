# src1.7.1：Stage 2 有界 Probe

本版从 `src1.7` 建立独立源码目录。Probe 只在真实 Stage 2 主循环没有可执行的合格正收益单任务、也没有原 Multi-GOTO 合格正收益尾部时启用。Stage 1 沿用 1.7 的生产流程；启动 Sense 仍属于原兼容观测。

Probe 先分析未完成任务的 canonical blocking facts，再用已有带来源的具体地点线索生成当前位置 Sense 或单地点 Move + Sense。候选与普通 CandidatePlan 分离；正常 greedy 的资格、排序、完整投影、约束交换、基础分和执行后整轮重规划均沿用原实现。

移动投影只能展开一个 Move，执行后最多一个 Sense。有关约束安全未知或确定损失均拒绝；原动作包装器负责 observation / action evidence、provenance、canonical resolution、ledger 和异常恢复。Probe 不写事实、补造 verified state 或执行普通不合格任务。

总次数 8、同观察地点 2、连续无进展 2，任一上限触发后本题 Probe 层锁定关闭。机器人移动、成本和单纯 world_revision 增长不算信息进展。执行结束立即完整重规划；正常任务计数和执行上限不受 Probe 影响。MustChooseOne 保留为只读分析优先提示和日志包装器，没有生产执行权。

普通及官方 SDK 语义检查 183/183，ASan/UBSan 182/182，包含 37 项 Probe 专项覆盖。正式配对使用原 71 输入与 comprehensive 全部 200 输入，两轮 IT/NT、种子 20260924、5000 ms、串行 AB/BA、StageTiming 关闭；20 道非法输入独立汇总，不纳入正常成绩。完整结果、全部退化及每次原始证据见 [发布验证报告](../test-results/validation-20261003/REPORT.md)。

最终 1084 对中，480 对正常 Stage 1 的动作序列与基础分完全一致、零 Probe。Stage 2 基础分 338032→346328，目标数 2685→2925，约束计分相同，两版正常运行均无失败、超时或评分缺失。原 71 输入的 126 对提前停止运行有 36 对恢复正常候选（28.57%），其中 32 对随后完成恢复任务；综合正常题没有恢复。116 次 Probe 中 108 次获得相关新信息、8 次无信息。36 对运行因探索成本降低基础分，另有时间奖励退化，任一指标下降的 60 对全部保留。

- [Probe 设计与构建/复跑入口](PROBE_LAYER.md)
- [canonical / mutation / 生产执行权审计](PROBE_AUDIT.md)
- [全部退化配对](../test-results/validation-20261003/REGRESSIONS.md)
- [最终配对 CSV](../test-results/validation-20261003/analysis-final/pairs.csv)
- [最终原始日志归档](../test-results/validation-20261003/raw-evidence.zip)

修复前完整比较、源码快照、早期冒烟、种子路径校验中止及 sanitizer 启动失败均单独保留。未修题、删除文件、修改旧版或选择性替换不利结果。
