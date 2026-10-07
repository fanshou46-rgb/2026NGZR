# 比赛快照：1.6.7.1-200ms

冻结日期：2026-10-07。比赛代码位于 `src1.6.7.1-200ms/`，根目录 `current` 是指向它的 Windows Junction。Git 命令在 `upstream-main-20260928` 工作区执行。

| 项目 | 固定值 |
|---|---|
| 附注 tag | `competition-1.6.7.1-200ms` |
| tag 对应提交 | `4336a368ffe531a33902b93256d6b26e528ed2e2` |
| 规划安全余量 | 200ms |
| SDK 总期限 | 5000ms |
| 默认策略 | 保持原版默认；清除 `RDFW_TASK_GROUP_MODE` 实验覆盖 |
| 产品文件 | 25 个；逐文件 SHA256 见 [competition_snapshot.json](competition_snapshot.json) |
| 交付 ZIP | 工作区根目录 `src1.6.7.1-200ms.zip`，保持原字节 |
| ZIP SHA256 | `7361b56c2f9557e5a1825cecd4137389a0339cf1e426a62776b7192b27eb8d49` |
| 完整比赛证据 SHA256 | `9365a96f74470adde61b9a97d122234b624e212f28b8eb3b3827fba3bb6a8f46` |

## 已验证行为

本版从原 200ms 版移入 H1 生命周期退出保护，并将 `isMultiGotoMode` 初始化为 false。任务排序、必要感知、约束交换及评分逻辑保持原版。

2026-10-06 综合 200 题对照：正常题 360 对动作完全一致，G=2020、C=11084、K=14800、B=287680；正式分 311040→311054，差异属于单轮时间奖励波动。普通 Release 检查 134/134 通过。完整记录见 [发布报告](../src1.6.7.1-200ms/docs/RELEASE_1.6.7.1-200ms.md)。

2026-10-07 使用真实官方 SDK 重新编译，Stage 1/2 各 IT/NT 四项冒烟通过；25 个产品文件及 52 个 SDK 源/模型文件前后哈希一致。结果见 [本次验证](../logs/competition_smoke_20261007/SUMMARY.json)。这些冒烟检查验证构建与运行入口，分数不作为新性能对照。

连续 O2 ASan/UBSan/泄漏检查仍未完成：输入安全检查曾长时间高 CPU，后续连续 CTest 出现不同用例的 10 秒超时。原始日志、单项成功与未完成记录一起保存于比赛证据和失败索引。

## 环境与构建运行

已实测环境：WSL `Ubuntu-18.04`，g++ 7.5.0，Python 3.6+，C++11，Boost thread/system/chrono/date_time/regex，pthread/dl。兼容官方 SDK 为 `/tmp/env-release-2026-search`；Windows 保留官方安装材料于上级 `env-release-2026/`。实际 SDK 源、模型及编译参数哈希见本次冒烟 SUMMARY。

在 PowerShell 从现有工作区重新构建并运行四项检查（输出目录必须是新名称）：

```powershell
wsl -d Ubuntu-18.04 -- bash -lc 'cd /mnt/c/Users/20723/Desktop/2026robocup/upstream-main-20260928 && python3 tools/competition_smoke.py --sdk /tmp/env-release-2026-search --output logs/competition_smoke_rerun'
```

工具复制产品文件到 WSL 原生临时构建目录，执行完整 `g++` 编译/链接命令，保存 `build.log`、二进制哈希、SDK 哈希、种子和客户端/服务端日志。SDK 保持原样，运行词表单独转为 LF。编译结果的原生路径记录在 SUMMARY 的 `native_build`；本次为 `/tmp/competition-1671-200-8s6lmyfo/example`。

实际服务器和客户端完整参数见四个结果 JSON 中的 `commands`。客户端参数分别为 `-stage 1/2 -nlp 0/1 -err 0/1 -ask_2 0/1 -path <临时LF词表>`，服务端为对应 `-mode it/nt -test 1 -to 5000`。服务器工作目录必须隔离，以容纳评分器写入的 ASP 状态；使用已保留的 `HistoryVersion/src1.1.2 (x)/tools/baseline.py` 运行入口。

## 冻结与后续开发

tag 固定产品快照，整理文档的新提交不会移动 tag。后续算法开发从独立实验分支开始，产品改动写入实验目录；使用本文件中的快照哈希校验比赛目录。`current` Junction 共享原目录，因此在其中编辑也会修改比赛工作副本。

所有旧分支与提交保留。需要 1.7+ 源码时，按 [开发历史](development_1.7plus.md) 恢复原路径或创建独立工作区。归档和清理范围见 [工作区整理](workspace_cleanup.md)。
