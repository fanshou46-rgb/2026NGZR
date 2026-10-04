# 1.7.7 验证工具

当前证据位于 `validation/review177-20261004`，以完整报告、最终冻结清单和原始归档为准。`implement.py`、`repair_at.py`、`repair_probe.py` 是开发阶段的局部编辑记录，不能重放为最终源代码；最终实际编译的源码已独立保存并逐项核对。

- `run_review.py`：冻结并串行比较两版，共304次生产、16次参考；旧题/已见题用一个种子，新题及比赛样本用两个。运行依赖已构建的1.7.6/1.7.7客户端。
- `generate_holdout.py`：独立新结构生成器；当前题目已观察过结果，重新运行不产生新的留出集。
- `revise_preflight.py`：原作者预检失败的保留和统一缩短路径操作，当前已完成，不重复执行。
- `summarize_review.py`、`audit_probes.py`：核对完整官方评分、所有退化、Stage1及概率/执行日志。
- `collect_and_package.py`、`archive_inputs.py`、`verify_publication.py`：保留原始证据与精确执行字节，核对CRC/SHA和Git发布字节。
- `write_report.py`、`write_delivery.py`：根据最终结果写报告与工作日志，前者要求已完成实际轨迹分析；后者防止重复插入日志。

原始证据和源码不在运行过程中改写。较早作者预检仅运行10次（9次完整、1次超时）、0次规划器，单独归档；最终成绩不包含该预检。

## 在新副本重跑

使用独立的新仓库副本及相同官方SDK环境。历史输入/工具的Git换行与实际执行字节存在32项差异，先在该新副本还原 `checks/executed-input-tooling.zip` 的精确字节，勿覆盖正在工作的仓库。新副本若缺少忽略的编译产物，先用 `rebuild_review_dependencies.py --sdk <SDK目录>` 构建两个客户端，再运行 `run_review.py --sdk <SDK目录> --out validation/review177-20261004/raw/frozen-v1`。工具拒绝覆盖已有产物。

重建需要已配置的官方头文件/库和Linux编译器；生成的新二进制和墙钟成绩是新的实验，不能称为原结果逐字节复现。原二进制的哈希和构建配方保留于归档。当前本轮实际使用的是复用已验证的两版二进制；上述新副本重建辅助工具只提供入口，本轮没有另做一次新副本重建/304次重复实验。
