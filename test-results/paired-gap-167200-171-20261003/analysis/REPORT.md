# src1.6.7-200ms → src1.7.1 直接配对与 Stage 2 gap 诊断

原71输入、IT/NT、两轮的284对直接比较已经完成。Stage 2 中 G_old > G_new 的 44 对来自 11 个输入，目标净损失 492、基础分损失 17332。
其中 24 对属于“旧版实际成功且全约束安全”的 recoverable gap，净损失 60 个目标、2132 基础分；另外 20 对是旧版实际成功的约束交换。依赖错误信息碰巧得到旧版独有目标的 legacy-lucky 为 0 对。

## 比较口径与冻结

- 比较臂直接为 src1.6.7-200ms 与冻结的 src1.7.1；两版重新完整编译并链接原官方 SDK，没有拼接前两次发布的成绩作为本次结果。
- 71输入沿用 src1.7 原始 input-audit 的 ID、stage、SHA256。旧路径移动到 HistoryVersion 时，只接受字节哈希相同的文件。33道原比赛题、37道原 release fixtures、1道原 unified fixture；原先排除的02/04/05维持排除。
- 每输入 × IT/NT × 两轮，seed=20260924、5000ms；串行交替 AB/BA；StageTiming=0，正常默认策略。每一次 cserver 日志均核对种子标记。固定 seed 不保证分叉后观察值一致，动作不同会改变随机数消费。
- 运行前后核对两版源码与全部题源哈希，final-audit 通过。scheduler、Probe、canonical、mutation、score、题源均保持字节一致；仅新增独立分析目录。
- G/C 使用官方 vanswer 的 value(id,40/20)，K 从 server.log 单流动作重算，基础分 B=40G+20I(G>0)C−K。官方分含时间奖励并封顶1000，raw_score 单独保留。内部 canonical 终态另列，不替代官方指标。
- 先按实际动作及反馈对齐共同前缀，再追踪资格、排序、Probe、任务尝试次数、实际成功动作至旧独有官方目标。记录第一次动作分叉与后续决定损失的分叉，二者可以不同。
- 两轮是同一 seed 的重复，所有数值按配对运行计数；重复题目中的目标也按官方 ID 计数。它们不构成独立随机样本，重复目标数不等于独立物理动作数。

## 全量结果

|范围|对数|G 旧→新|C 旧→新|K 旧→新|基础分 旧→新|官方分 旧→新|G提高/相等/下降|
|---|---:|---:|---:|---:|---:|---:|---:|
|all|284|2564→2082|968→1002|10528→9088|111392→94232|121482→110600|6/234/44|
|stage1|120|356→356|68→68|1216→984|14384→14616|25458→25806|0/120/0|
|stage2|164|2208→1726|900→934|9312→8104|97008→79616|96024→84794|6/114/44|
|it|142|1286→1046|482→498|5294→4582|55786→47218|60806→55372|4/116/22|
|nt|142|1278→1036|486→504|5234→4506|55606→47014|60676→55228|2/118/22|

失败/超时：旧 0/0，新 0/0。逐 pair CSV 保留全284对，筛选 CSV 保留全部负向 Stage 2 对。

## 互斥的 pair 主分类

每个负向 pair 只有一个主分类，基础分只计入主分类；次要机制是诊断标签，不能相加。类别名表示本次差异的机制，其中 qualification-too-strict / constraint-gate-strict 并不自动意味着可以安全放宽。

|主分类|pair|输入|目标净损失|目标分损失|约束分损失|成本项|基础分净损失|安全可恢复pair|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|qualification-too-strict|12|3|408|16320|-480|-1104|14736|0|
|probe-coverage-gap|4|1|28|1120|0|-76|1044|4|
|no-location-clue|0|0|0|0|0|0|0|0|
|constraint-gate-strict|4|1|16|640|-160|-196|284|0|
|legacy-lucky|0|0|0|0|0|0|0|0|
|ordering-cascade|12|3|24|960|0|-92|868|12|
|group-search-gap|8|2|12|480|-80|-112|288|4|
|retry-bound|4|1|4|160|0|-48|112|4|
|deadline|0|0|0|0|0|0|0|0|
|terminal/score-disagreement|0|0|0|0|0|0|0|0|
|other|0|0|0|0|0|0|0|0|

目标分损失=40(G_old−G_new)，约束分损失=20(C_old−C_new)，成本项=K_new−K_old；成本项可为负。三项严格相加等于基础分净损失。所有分类基础分相加=17332，与筛选集合一致。

## 逐目标分类

goal-gaps.csv 每行一个旧版独有官方目标 ID。每个目标记录 ASP 条件、类别、旧版持续满足起始事件和动作反馈，以及新版是否曾经满足。目标分类只归因40分目标项，探索成本与约束信用不任意摊到单个目标。
36.xml 的 pair 主类为 probe-coverage-gap，但其六个黑杯重复目标属于 Probe 覆盖缺口，红杯 putin 的一个目标属于 ordering-cascade。因此目标级分类与 pair 主分类的目标数分布不同。

|目标级类别|旧独有目标ID计数|目标分损失|
|---|---:|---:|
|qualification-too-strict|408|16320|
|probe-coverage-gap|24|960|
|constraint-gate-strict|16|640|
|ordering-cascade|28|1120|
|group-search-gap|12|480|
|retry-bound|4|160|

## 每个输入的行为链

|输入|主类|每pair G 旧→新|每pair基础分损失|安全性|代表性证据|
|---|---|---:|---:|---|---|
|c003 06.xml|constraint-gate-strict|10→6|71|successful-constraint-trade|[c003-it-r1](pair-evidence/c003-it-r1.md)|
|c007 10.xml|ordering-cascade|5→1|135|recoverable-safe-observed|[c007-it-r1](pair-evidence/c007-it-r1.md)|
|c011 14.xml|retry-bound|3→2|28|recoverable-safe-observed|[c011-it-r1](pair-evidence/c011-it-r1.md)|
|c015 18.xml|group-search-gap|2→1|27|recoverable-safe-observed|[c015-it-r1](pair-evidence/c015-it-r1.md)|
|c019 22.xml|qualification-too-strict|35→1|1228|successful-constraint-trade|[c019-it-r1](pair-evidence/c019-it-r1.md)|
|c020 23.xml|qualification-too-strict|35→1|1228|successful-constraint-trade|[c020-it-r1](pair-evidence/c020-it-r1.md)|
|c021 24.xml|qualification-too-strict|35→1|1228|successful-constraint-trade|[c021-it-r1](pair-evidence/c021-it-r1.md)|
|c031 34.xml|ordering-cascade|39→38|37|recoverable-safe-observed|[c031-it-r1](pair-evidence/c031-it-r1.md)|
|c032 35.xml|ordering-cascade|39→38|45|recoverable-safe-observed|[c032-it-r1](pair-evidence/c032-it-r1.md)|
|c033 36.xml|probe-coverage-gap|36→29|261|recoverable-safe-observed|[c033-it-r1](pair-evidence/c033-it-r1.md)|
|c069 P09.xml|group-search-gap|4→2|45|successful-constraint-trade|[c069-it-r1](pair-evidence/c069-it-r1.md)|

全部IT/NT与两轮的逐pair链条均在 pair-evidence/ 中；pair-traces.json 保留精确日志行号、动作序号、官方目标差集与评分结果。

### c003 / 06.xml

首次实动作分叉在共同完成白杯后：旧版先 PickUp 17，新版先 PickUp 13；两版最后均完成六个杯子目标。目标损失发生在后续书本任务：旧版在 check-phase 允许组合收益放行，进入地点3并完成四个书本目标；新版 requires_verified_group 过滤这些任务，Stage 2 guarded 不支持，Probe 的移动又被 constraint_safety_unknown 拒绝，在有余时停止。

旧版官方约束3/5，新版5/5；进入书桌和白瓶所在地3使两个约束失去信用。四个书本目标实际成功，但这不是全约束安全的恢复。错误椅子地点8触发的书本发现发生在共同前缀，随后已得到 Sense，不能把旧版独有的四个目标归为 legacy-lucky。

[本输入代表性日志链](pair-evidence/c003-it-r1.md)

### c007 / 10.xml

旧版先完成白书 puton 再依次放物，最后 pickup 红罐18；新版第一轮选择边际34的 pickup18，随后放物需要暂时放下18，gain=1/loss=1，单任务边际为负且部分资格变为 false。五次 Probe 增加信息，仍无法消除该目标交换结构；Stage 2 没有任务组执行，最终只保留 pickup18。

旧版五目标全部由官方评分确认，禁止开冰箱的约束1/1仍有信用，获胜放物动作反馈均 true。旧版目标没有依赖本题错误的白杯/遥控器信息。安全恢复路径已在旧版观察到，但未测试新版的修改方案。

[本输入代表性日志链](pair-evidence/c007-it-r1.md)

### c011 / 14.xml

第一动作旧版 Move14、新版 Move10。新版先执行 GOTO couch10，探索离开后反复重做；GOTO task4 三次均 success=true、attempts=1/2/3。随后 pickup16 与最后到地点1的 Probe 使 GOTO 不满足；任务尝试上限使其不再进入候选，最终比旧版少官方 goal5。旧版最后 Move10+Sense 保留 GOTO。

无约束；旧版独有 goal5 是末尾有意 Move10 达成，实际成功且可定位。旧版 AskLoc19 得到 inside(19,5) 与 XML 的 inside(19,12) 不符，TakeOut19 5/PutDown19 都失败；这个错误分支没有产生旧版独有目标。白杯21缺位置线索影响双方未完成的 give，而不是本次净损失。

[本输入代表性日志链](pair-evidence/c011-it-r1.md)

### c015 / 18.xml

共同 PutDown10 后，旧版 Move45/PickUp29/Move44/PutDown29，再末尾 GOTO12；新版先 GOTO12，随后黑书 puton 将暂时失去 GOTO，单任务净边际非正。Stage 2 guarded 不支持，Probe 无法证明移动安全或投影含额外物理动作；新版放弃黑书。这里需要绑定 puton29 后返回12的组合才能保留两目标。

旧版官方20/20约束都有信用，黑书地点45与书桌44均来自正确原始信息，PickUp29/PutDown29均 true。丢失 goal4 属于安全可恢复路径；内部约束0/20 unknown=19 与官方信用20/20的差异单列。

[本输入代表性日志链](pair-evidence/c015-it-r1.md)

### c019 / 22.xml

旧版初始 MustChooseOne 绕过 eligible=false，先 Move4/PickUp11，AskLoc5 经两次 not_known 后得到真实 at(5,6)，随后 Move6+Sense 确认沙发并逐物完成重复目标。新版先 GOTO桌子3；其他 puton 因资格不通过，Probe 的地点4被未知约束安全拒绝，在约4.8秒余量时停止。

旧版34个独有目标由实际放物和官方评分确认；原错误沙发位置4已被 AskLoc/Sense 纠正后才送达6。旧版官方0/2约束，新版2/2；这是执行约束交换后的实际高收益，不属于全约束安全 recoverable，也不是错误目标信息碰巧得分的 legacy-lucky。重复34项集中于7个对象放物，不等于34次独立物理成功。

[本输入代表性日志链](pair-evidence/c019-it-r1.md)

### c020 / 23.xml

旧版初始 MustChooseOne 绕过 eligible=false，先 Move4/PickUp11，AskLoc5 经两次 not_known 后得到真实 at(5,6)，随后 Move6+Sense 确认沙发并逐物完成重复目标。新版先 GOTO桌子3；其他 puton 因资格不通过，Probe 的地点4被未知约束安全拒绝，在约4.8秒余量时停止。

旧版34个独有目标由实际放物和官方评分确认；原错误沙发位置4已被 AskLoc/Sense 纠正后才送达6。旧版官方0/2约束，新版2/2；这是执行约束交换后的实际高收益，不属于全约束安全 recoverable，也不是错误目标信息碰巧得分的 legacy-lucky。重复34项集中于7个对象放物，不等于34次独立物理成功。

[本输入代表性日志链](pair-evidence/c020-it-r1.md)

### c021 / 24.xml

旧版初始 MustChooseOne 绕过 eligible=false，先 Move4/PickUp11，AskLoc5 经两次 not_known 后得到真实 at(5,6)，随后 Move6+Sense 确认沙发并逐物完成重复目标。新版先 GOTO桌子3；其他 puton 因资格不通过，Probe 的地点4被未知约束安全拒绝，在约4.8秒余量时停止。

旧版34个独有目标由实际放物和官方评分确认；原错误沙发位置4已被 AskLoc/Sense 纠正后才送达6。旧版官方0/2约束，新版2/2；这是执行约束交换后的实际高收益，不属于全约束安全 recoverable，也不是错误目标信息碰巧得分的 legacy-lucky。重复34项集中于7个对象放物，不等于34次独立物理成功。

[本输入代表性日志链](pair-evidence/c021-it-r1.md)

### c031 / 34.xml

旧版先 Move6 尝试黄色罐17，纠错后取黄色杯15；新版先 Move8/PickUp18。后续旧版在手空时 PickUp10/PutIn10 6，保留红杯目标28；新版优先完成其他重复 puton 和 pickup蓝杯11。末尾虽 Probe 到8看到红杯10，持有11使 putin10 6暂时失去pickup目标，非正单任务过滤且Stage 2无任务组执行。

无约束。独有goal28由正确的 at(10,8) 及 PickUp10/PutIn10 6 true 证实，未依赖本题关于罐17的错误 outside 信息。旧版罐17的失败与 AskLoc not_known 不构成 lucky 目标成功。

[本输入代表性日志链](pair-evidence/c031-it-r1.md)

### c032 / 35.xml

旧版先 Move6 尝试黄色罐17，纠错后取黄色杯15；新版先 Move8/PickUp18。后续旧版在手空时 PickUp10/PutIn10 6，保留红杯目标28；新版优先完成其他重复 puton 和 pickup蓝杯11。末尾虽 Probe 到8看到红杯10，持有11使 putin10 6暂时失去pickup目标，非正单任务过滤且Stage 2无任务组执行。

无约束。独有goal28由正确的 at(10,8) 及 PickUp10/PutIn10 6 true 证实，未依赖本题关于罐17的错误 outside 信息。旧版罐17的失败与 AskLoc not_known 不构成 lucky 目标成功。

[本输入代表性日志链](pair-evidence/c032-it-r1.md)

### c033 / 36.xml

旧版先黑罐17的 puton，新版先绿色杯12的 puton。旧版在错误 outside14@6 上 PickUp14 失败后 AskLoc14 得到真实 inside(14,6)，随后 TakeOut14 6/PutDown14 成功，满足六个重复黑杯目标。新版 Probe 只 Move+Sense，看到地点6没有14形成冲突，无法发现 inside；重复相关上下文拒绝后停止。另一个红杯 putin29 因 pickup11已完成而出现 gain1/loss1的排序后果。

无约束；黑杯恢复在得到真实 inside反馈后执行，失败触发的纠错不是依赖错误信息碰巧达成目标。六重复目标由一次实际取出并放到沙发完成。红杯goal29的旧版成功由正确初始位置8与 PutIn10 6 true确认。

[本输入代表性日志链](pair-evidence/c033-it-r1.md)

### c069 / P09.xml

旧版首先 PickUp5，经 putdown/open/putin 连续执行两物放入任务，最后 Close2；gate 日志明确用 group=2放行首任务。新版两物 putin 都 requires_verified_group，Stage 2 guarded不支持；一次 Sense后信息已完整，仍无可执行单任务，保留初始close与goto目标，少goal2/3。

旧版 putin2/3实际成功，基础分144超过新版99，但官方约束信用0/1对1/1；Open2导致历史约束损失，末尾Close2不恢复信用。应归为高收益约束交换，不是全约束安全recoverable。

[本输入代表性日志链](pair-evidence/c069-it-r1.md)

## recoverable 与 legacy lucky 的证据标准

recoverable-safe-observed 要求旧版独有目标由真实世界终态和成功动作支持，并且旧版所有官方约束保有信用。含错误初始信息、动作失败或 AskLoc 错误响应本身不使结果成为 lucky；要检查获胜目标是否在正确证据下实际完成，以及错误线索是否决定了它的成功。
本次安全可恢复集合为10、14、18、34、35、36.xml，共24对；约束交换集合为06、22、23、24.xml和P09，共20对。
36.xml 是纠错后的安全恢复：PickUp14 false → AskLoc14 inside(14,6)（与题源真值一致）→ TakeOut14 6 true → PutDown14 true。错误outside信息触发了纠错，成功依靠正确inside反馈与实际动作；应归入Probe能力覆盖差异。
22–24.xml 是实际成功的约束交换：沙发位置从错误4被AskLoc/Sense纠正到真实6后才放物；旧版0/2约束信用，所以不能列入安全恢复，也不能据“使用了错误初始线索”归成legacy-lucky。
14.xml 的旧版 AskLoc19 inside(19,5) 与真实inside(19,12)不符，随后TakeOut19 5和PutDown19失败；这个错误信息分支没有产生本次旧独有的GOTO目标。06.xml通过错误椅子线索到8后发现书本，是两版共同前缀，不能解释旧独有差集。
本次负向差集中没有验证到 legacy-lucky。该结论只覆盖这71题、这个seed的获胜目标链；已有错误信息分支照样保存在原始证据中。安全可恢复是对已观察旧版路径的诊断，尚未执行任何新版修复的反事实验证。

## 未占主分类的类别与边界证据

- no-location-clue：14.xml中白杯21缺地点线索，影响双方没有完成的give；它不属于旧版独有目标差集，故没有把它误计入目标损失。
- deadline：所有负向pair均有明确非deadline停止机制。06.xml旧版尾部接近预算，但新版在明显余时停止且有requires_verified_group/constraint_rejected证据；不能将其归为deadline。
- terminal/score-disagreement：多对内部约束终态与官方信用不同，例如18.xml内部C=0/20、unknown=19，官方两版都是20/20。这会影响保守资格/Probe安全证明，作为次要证据保存；官方重算的G差异不是客户端计数差异造成。
- other：已筛选负向pair均有审阅过的主机制，没有未归类残差。没有运行的类别不提供虚构代表日志；其边界证据见[CATEGORY_EVIDENCE.md](CATEGORY_EVIDENCE.md)。

## 完整性与复核

核验284个唯一pair、568次运行、71个输入的完整IT/NT×两轮网格。每次官方G/C、动作K和基础分从原始日志重算，并与运行结果逐一相等；492个旧独有目标的轻量动作重放与官方终态一致。
两轮动作/G/基础分不一致的臂数：0。所有原始运行、输入、官方ASP、两版二进制、编译命令及seed interposer保存在raw-evidence.zip，原件未删除。

## 交付文件

- [pairs.csv](pairs.csv)：全部284对；[gaps.csv](gaps.csv)：全部负向Stage 2对。
- [goal-gaps.csv](goal-gaps.csv)：逐目标类别与成功动作；[category-summary.csv](category-summary.csv)：11类完整汇总，包括0计数。
- [CATEGORY_EVIDENCE.md](CATEGORY_EVIDENCE.md)：每类代表日志与边界证据；[pair-traces.json](pair-traces.json)：完整机器可读追踪。
- [analysis-validation.json](analysis-validation.json)、[repeat-audit.json](repeat-audit.json)、[source-receipt.json](source-receipt.json)：网格、重算、重复与来源核验。
- [原始证据归档](../raw-evidence.zip)、[运行冻结核验](../raw-metadata/final-audit.json)、[输入与源码审计](../raw-metadata/input-audit.json)。
- 分析与复跑入口：run_direct_pairs.py / analyze_direct_pairs.py / case_review.json / write_report.py。复跑必须选用新的输出目录。
