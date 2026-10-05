# 1.6.7 → 1.6.7.1 综合 200 题证据

正式协议：原版 300ms 基线，默认/default，5000ms，种子 20260928，一轮，IT/NT，串行 AB/BA。200 题、400 组、800 次官方 SDK 运行；其中正常题 360 组，非法题 40 组。

正常题目标 2020→2020、约束信用 11084→11084、动作成本 14800→14800、基础分 287680→287680、正式分 311080→311078、平台秒数 612.753→613.464。全部动作序列一致，SDK 截止/外部超时/运行失败/评分缺失均为 0。45 组正式分增加、46 组下降、269 组相同；91 组差异均只有时间奖励。

结论：专项清理交错与构造默认值反例证明退出/初始化保护增强；本轮正常题行为兼容，未证明解题能力或稳定提分。完整实现、分组成绩、测试范围和 SDK 阻塞边界见 [发布报告](../../docs/RELEASE_1.6.7.1.md)。

## 可直接查看的结果

- [SUMMARY.json](SUMMARY.json)：正常/非法/Stage 1/Stage 2 汇总，缺失与失败分别计数。
- [PAIRS.csv](PAIRS.csv)、[results.jsonl](results.jsonl)：完整首轮配对与逐运行状态；output 字段是本轮 Linux 原运行路径。
- [REGRESSIONS.json](REGRESSIONS.json)：所有目标/基础分/正式分下降；时间奖励下降也保留。
- [BEHAVIOR_DIFFERENCES.json](BEHAVIOR_DIFFERENCES.json)：行为/G/C/K/B 差异，本轮为空。
- [difference-classification.json](difference-classification.json)：每组行为/时间奖励/非法题分类。
- [independent-log-audit.json](independent-log-audit.json)：800 次原始动作、官方答案与成绩重算，0 差异，附原始文件 SHA256。
- [input-audit.json](input-audit.json)、[build-audit.json](build-audit.json)、[final-audit.json](final-audit.json)：两版源码、题目、SDK、工具、编译器、二进制冻结和结束核对。
- [git-byte-audit.json](git-byte-audit.json)：两版共 50 个生产文件的暂存字节与实测副本核对，均只有 CRLF/LF 差异，标准化换行后逐字节一致。实测原字节保存在证据包，Git 检出哈希不等于该原字节哈希。Windows 绝对路径 worktree 应使用原生 Windows Python/Git 执行 tests/audit_staged_source.py；WSL Git 不能解析本工作树的 Windows .git 指针。

## 原始证据包

[EVIDENCE.zip](EVIDENCE.zip) 使用按内容去重格式，入口 MANIFEST.json 的 files 保存原逻辑路径、SHA256、字节数和文件 mode；实际字节位于 blobs/<sha256>。相同资源只存一次，原逻辑文件没有删减。

- full/：800 次正式运行的 server/client 日志、官方 ASP 输入与输出、测试 XML、每次结果、SDK 运行资源，两版源码副本/二进制/构建命令和日志。
- pilot/：修复构造标志之前草稿的 12 次预试及独立核对；与正式运行分开。
- checks/：普通、Debug/O2 内存检查、初始失败、最终通过、原版失败退出码 42/43、配置/构建/CTest 日志。中间构建对象省略。

[EVIDENCE.receipt.json](EVIDENCE.receipt.json) 记录归档哈希、大小、逻辑文件数和 CRC/SHA256 验证。恢复某个文件时，从 MANIFEST.json 查其 sha256，读取对应 blob 写入原逻辑路径，再按 mode 设置权限；example、iclingo 等可执行文件需要恢复执行权限。

普通最终 134/134，通过日志 checks/ctest-unit-v2.log；O2 ASan/UBSan/泄漏最终 133/133，通过日志 checks/ctest-asan-o2.log。原版反例 checks/before-probes-final.json；初次错误 fixture 与 Debug 失败日志也在包内。单轮固定种子的已见题回归及测试 stub 反例分别用于行为兼容与内部生命周期验证，不代替新题泛化或 SDK 网络中断验证。

原生产二进制 SHA256：858ea96c5c4631b987675813cd36e8d2b77c57246ee90ce544c3299cf57b737a。

新版生产二进制 SHA256：5b3f5b40bf163cff759bdc89e6d2b2ad5062209b71948693e50482a6c9c54078。
