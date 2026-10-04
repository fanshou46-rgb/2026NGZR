# src1.7.4 联合场景模型开发中

最新独立复核发现生产柜内关系与联合状态表示仍有错误；24 道新题的 96 对比较中，相对 1.7.3 基础分 -1227、G -41。完整范围与全部退化见 [新题报告](../validation/review-20261004/REPORT.md)，版本新增与后续修复见 [逐版审计](../docs/AUDIT_1.7.2_1.7.4.md)。本轮重命名后普通/官方检查 287/287；下文内存检查是此前记录，未把反例复现计作产品通过。

从 src1.7.3（9c600988）独立复制，旧版保留。本轮新增独立隐藏世界、联合 belief、观察/动作反馈分支，以及有界的反馈策略树。开发范围、证据与接入要求见 [JOINT_MODEL.md](docs/JOINT_MODEL.md)。

从接收题目到停止的每一步决策见 [ROBOT_FLOW_1.7.4.md](docs/ROBOT_FLOW_1.7.4.md)。

生产询问噪声已修正重复地点权重并固定初始域；事实层与终态检查已修正 Sense 不能证明“不在手持/托盘”的误判，并分别记录动作对两个槽位的排除证据。新增联合搜索尚未接入真实 Probe 的选择/授权，不宣称完整模型验收。继承文档属于各自原版本。

普通测试含官方 SDK 对照 287/287 通过；ASan/UBSan 和泄漏检查 269/269 通过。相对 src1.7.3 新增 23 个联合模型测试、3 个噪声集成用例、12 个事实判定用例，以及 17 组 SDK 场景，按每一步比较反馈、可见 ID、完整 at/inside/slot/door 状态和最终基础分。历史题配对与全部开发退化见 `test-results/validation-20261004/REPORT.md`。

```sh
cmake -Hsrc1.7.4/tests -B/tmp/rdfw174-unit -DCMAKE_BUILD_TYPE=Release -DOFFICIAL_SDK=/tmp/env-release-2026-search
cmake --build /tmp/rdfw174-unit -- -j3
(cd /tmp/rdfw174-unit && ctest --output-on-failure)
bash src1.7.4/tests/sanitize_probe.sh /tmp/rdfw174-sanitizer-nopie
```
