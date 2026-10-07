# 工作区整理与恢复

日期：2026-10-07。整理范围为 `upstream-main-20260928`。根目录 `current/docs/logs` 是指向该工作区的 Windows Junction；其他三个 Git 工作区及其未提交内容保留。

## 保存与清理规则

先固定比赛 tag 和25个产品文件哈希，再扫描完整长路径清单、保存其他工作区未提交文件哈希、建立内容去重归档和典型失败索引。CRC、全部内容块、每个逻辑文件SHA256及删除前实物文件核对均通过后，才实施稀疏检出和残留目录清理。

清理清单见 [before.json](../logs/workspace_cleanup_20261007/before.json) 的 `targets`。其中逐项给出绝对路径、字节数、受Git管理的文件数、归档和恢复命令。完整目录/文件前20名也在同一文件，嵌套目录累计值存在重叠，不能相加。

保留比赛版本、原200ms基线、题库、历史测试入口、已有证据包、原路径的汇总/逐题统计、实验 `source/next/drafts` 及未提交草稿。历史构建目录中的源码副本连同产物一起归档，保证独有实现可恢复。共享 `.git` 和LFS对象保留。

新归档位于 `logs/evidence_archives/`。`INDEX.zip` 中的 `MANIFEST.json` 将每个原路径映射到文件SHA256、长度、8MiB以内内容块及所在分卷。分卷上限约40MiB，便于Git传输。校验见 [receipt.json](../logs/evidence_archives/receipt.json)。已有比赛证据和78个原始研发证据包已分别校验CRC，原格式继续保留。

归档读取使用8线程、有界批次；写入和校验保持确定顺序。归档中只使用完整校验的分卷。

## 本地稀疏检出

Git非cone模式仅对这个工作区生效：包括根目录全部文件，排除清单中的旧1.7+版本和庞大展开日志目录。`git ls-files` 仍记录所有旧文件，`git status` 中不会出现批量删除；云端普通完整检出也继续包含Git保存的历史版本。

当前规则的实际位置：

```powershell
git rev-parse --git-path info/sparse-checkout
git config --worktree --get core.sparseCheckout
```

恢复某版Git源码时，打开上面输出的规则文件，删除对应 `!/src1.7.7/` 行，然后：

```powershell
git sparse-checkout reapply
```

这样恢复Git保存的文件和当前仓库换行配置。完整回到普通检出可执行 `git sparse-checkout disable`；它会重新占用空间，但不会恢复从未进入Git的旧日志。

## 精确原字节与日志恢复

归档工具使用Python3.9+；当前Windows解释器为 `C:\Users\20723\miniconda3\python.exe`。从主工作区运行：

```powershell
python tools/workspace_archive.py verify
python tools/workspace_archive.py restore --prefix src1.7.7 --destination D:/RoboCupEvidenceReview
python tools/workspace_archive.py restore --prefix validation/review177-100-20261004/runs/new-A01-02-s1-it-r1-177
```

第一条检查所有分卷、内容块与逻辑文件；第二条在独立目录恢复完整旧版；第三条在原工作区恢复单条日志。恢复工具预先检查整个前缀，遇到已有不同内容就停止，保护新实验。Git换行转换后的文件与原始归档字节可能不同，此时选用新destination检查原始字节。

历史工具依赖 `src1.7.7/tests` 等旧路径时，先恢复对应Git目录。当前比赛构建和四模式冒烟使用保留的独立入口 `tools/competition_smoke.py`，运行说明见 [比赛快照](competition_version.md)。

## 验证和占用结果

所有占用数字采用文件逻辑字节，跳过Junction以避免重复计数；统计已计入新增归档和Git对象。

| 范围 | 清理前 GiB | 清理后 GiB |
|---|---:|---:|
| 整个2026robocup目录 | 25.253 | 10.693 |
| 主工作区 | 18.422 | 2.972 |

全目录释放 **14.560 GiB**。清理331个目标目录，原1.7+目录已从磁盘移出；174735个文件的16.418GiB原始内容保存为931.92MiB补充归档（28个数据分卷加INDEX）。

验证结果：所有归档CRC、74750个内容块及174735个逻辑文件SHA256通过；删除前每个原文件SHA256一致，目标集合无新增文件。恢复167个1.7.7文件和4个完整失败记录文件成功；Git旧版本38个产品文件在换行统一后逐字节一致。比赛25个产品文件、交付ZIP和比赛证据包原字节保持一致，其他工作区状态及未提交文件哈希一致。四项官方SDK冒烟与52个官方源/模型哈希核对通过。

详细记录：[占用排名](../logs/workspace_cleanup_20261007/disk_ranking.md)、[清理清单](../logs/workspace_cleanup_20261007/cleanup_targets.csv)、[实际执行](../logs/workspace_cleanup_20261007/applied.json)、[清理后核对](../logs/workspace_cleanup_20261007/after.json)、[恢复测试](../logs/workspace_cleanup_20261007/restoration-audit.json)。

未处理项：四个未提交实验草稿、现有发布ZIP、其他工作区、共享Git/LFS继续保留。D盘 `D:/RoboCupEvidenceReview/workspace-verification-20261007` 为恢复测试副本；自动审批审查拒绝其递归删除，返回原因为 `blocked by policy`，因此保留。连续sanitizer检查状态仍为未完成。详见 [skipped-items.json](../logs/workspace_cleanup_20261007/skipped-items.json)。
