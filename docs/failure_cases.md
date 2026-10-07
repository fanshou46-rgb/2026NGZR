# 典型失败记录

日期：2026-10-07。保留七组代表案例，每个问题类别1～2组。案例与完整来源哈希见 [机器可读索引](../logs/representative_failures/INDEX.json)。服务端原始动作、客户端决策、原始评分及关键官方ASP终态均按原字节保存。

| 案例 | 版本／题目／模式／种子 | 现象及结论 |
|---|---|---|
| [提前停止](../logs/representative_failures/early-stop-A01-02/CASE.json) | 1.7.7 对 1.6.7-200ms；A01-02-s1，Stage1 IT，2026100403 | 候选G3/C30/K14/B706/F792，尚余4366ms；基线继续运输和闭合。组合搜索不完整后停止是具体修复入口。 |
| [SDK截止](../logs/representative_failures/sdk-deadline-j04b/CASE.json) | 1.7.7 对200ms基线；j04b，Stage2 IT，2026100403 | 1.7.7触发5000ms SDK截止，仍有有效评分。保留截止标志；这条记录属于1.7.7。 |
| [内部高报与恢复失败](../logs/representative_failures/recovery-h03a/CASE.json) | 1.7.5／1.7.6；h03a，Stage2 IT，2026100401 | 1.7.5内部G6而SDK G5；1.7.6修正关系后探索丢掉goto，SDK G4。完整收益遗漏、未知门恢复和投影缺陷有原始证据。 |
| [事实语义](../logs/representative_failures/independent-inside-semantics/CASE.json) | 1.7.4及独立联合内核；直接SDK反例 | 显式at和inside共存、双父关系被模型错误清除或丢失。直接语义检查使用明确动作，题目种子不适用。 |
| [模型预算](../logs/representative_failures/model-budget-f29/CASE.json) | f29；A04-01-s2，Stage2 IT，首种子重复 | 模型累计269.904959ms超过250ms目标。模型预算与比赛200ms规划余量分开记录。 |
| [重复分叉](../logs/representative_failures/repeat-divergence-f29/CASE.json) | f29；A01-01-s2，Stage2 NT，2026100403 | 相同种子首轮／重复轮G6→7、K74→86。保留两次原始路径和首次分叉审计；重复用于稳定性检查。 |
| [sanitizer未完成](../logs/representative_failures/sanitizer-incomplete-competition/CASE.json) | 1.6.7.1-200ms；连续专项检查 | 不同用例10秒超时，input_safety检查未完成。普通测试及SDK结果另列，内存检查状态保持未完成。 |

每个CASE.json包含版本配对、模式、阶段、种子、原始commands、评分、文件来源与SHA256。无任务种子的直接语义与专项测试标为不适用。未找到的碰撞／定位物理问题不建立虚构案例。

## 完整证据

比赛综合200题的完整EVIDENCE.zip继续保留在比赛目录；原始SDK对照与研发检查的已有证据包保留在原位置。补充归档为 [INDEX.zip](../logs/evidence_archives/INDEX.zip) 和同目录分卷，校验收据为 [receipt.json](../logs/evidence_archives/receipt.json)。

补充归档按SHA256内容块去重，文件索引记录原路径、精确字节、模式和修改时间。已有结果汇总、逐题CSV/JSON、题库及复算工具继续保留；被移出的完整旧版本也保留在Git和补充归档中。

例如恢复特定配对至新目录：

```powershell
python tools/workspace_archive.py restore --prefix validation/review177-100-20261004/runs/new-A01-02-s1-it-r1-177 --destination D:/RoboCupEvidenceReview
```

恢复到原工作区时省略destination。目录已有不同内容时工具停止，防止覆盖新实验。比赛证据的原格式可用本版 `tests/package_comprehensive_evidence.py` 查看和校验。
