# liuyifan1.0 分数报告

日期：2026-09-24。6道原型题，原版 src1.3.3-fixed 完成20次正式求解测试；另有6次作者参考方案的官方运行。26次均取得有效官方评分，0次平台硬超时、0次客户端崩溃。

## 测试口径

- WSL2 发行版 Ubuntu-18.04，系统 Ubuntu 18.04.2 LTS，g++ 7.5.0。
- 官方 SDK：`/home/yifan/env-release-2026`；cserver、libasp、libframe及求解器源码哈希见[构建记录](../../test-results/liuyifan1.0-20260924-final/build-fixed/build.json)。
- 出题依据是仓库中的2025规则及出题指南；执行评分使用现有2026 SDK，5000 ms。该测试结果不冒称为2025平台实测。
- 01、02、05、06为Stage 1；03、04为Stage 2。所有题均测IT和NT。Stage 2再使用20260924、20260925两个固定种子各测IT/NT。
- 原版求解器保持不变；[前后源码哈希核验](../../test-results/liuyifan1.0-20260924-final/source-unchanged.json)通过。固定种子仅用于测试端srand插桩；无种子的原生运行完整保留。
- 分数、目标数和约束数来自官方server及ASP answer-set；基础分=40×完成目标+20×计分约束−动作成本。效率分采用官方总分减基础分，避免规则文字与平台公式差异。
- 参考客户端执行公开的作者动作序列，用于证明可行解和比较动作成本；它掌握题目真值、没有在线搜索开销，所得分数不是最优解证明，也不计入求解器成绩。

## 主测试：未固定随机种子

|题|主题|阶段|IT分|NT分|完成目标/总目标|维护约束/总约束|动作数|基础分|参考基础分|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
|[01](01.xml)|自由终态汇聚|1|292|294|7/7|0/0|16|232|232|
|[02](02.xml)|搬运与到达共享终态|1|374|374|9/9|0/0|16|312|312|
|[03](03.xml)|must-near 纠错与缺失补全|2|373|373|7/7|2/2|9|295|296|
|[04](04.xml)|容器状态纠错与合法语言扰动|2|253|253|5/6|2/2|18|193|236|
|[05](05.xml)|牺牲一个约束解锁四个目标|1|296|296|6/6|0/1|10|220|220|
|[06](06.xml)|放弃低收益目标保住三个约束|1|324|322|5/6|3/3|7|240|240|

**IT合计：1912分；NT合计：1912分；两个子项目合计：3824分。** 这只是6道原型的测试合计。所有分数均低于1000，因此raw与封顶后的official字段相同。

06有意放弃give目标，维护三个约束；05有意牺牲must-closed约束。两者都符合题目的收益取舍设计。04少完成的goto目标属于实际失分。

## 第二阶段复测

|题|模式|自然运行|种子20260924|种子20260925|动作轨迹|
|---|---|---:|---:|---:|---|
|03|IT|373|373|373|完全一致|
|03|NT|373|373|373|完全一致|
|04|IT|253|251|253|完全一致|
|04|NT|253|251|253|完全一致|

这两题各6次运行的动作、反馈、目标数、约束数均一致。04的251–253分变化来自耗时奖励；其基础分恒为193。所有当前测试轨迹均没有AskLoc，故种子复测证明本题执行稳定，不覆盖错误询问回答分支。

## 逐次完整记录

|执行者|题|模式|种子|官方分|基础分|效率分|动作成本|用时s|证据|
|---|---|---|---|---:|---:|---:|---:|---:|---|
|reference|01|IT|natural|294|232|62|48|1.875|[server](../../test-results/liuyifan1.0-20260924-final/reference-natural-01-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/reference-natural-01-it/trace.json)|
|reference|02|IT|natural|374|312|62|48|1.847|[server](../../test-results/liuyifan1.0-20260924-final/reference-natural-02-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/reference-natural-02-it/trace.json)|
|reference|03|IT|natural|376|296|80|24|0.915|[server](../../test-results/liuyifan1.0-20260924-final/reference-natural-03-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/reference-natural-03-it/trace.json)|
|reference|04|IT|natural|302|236|66|44|1.648|[server](../../test-results/liuyifan1.0-20260924-final/reference-natural-04-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/reference-natural-04-it/trace.json)|
|reference|05|IT|natural|296|220|76|20|1.109|[server](../../test-results/liuyifan1.0-20260924-final/reference-natural-05-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/reference-natural-05-it/trace.json)|
|reference|06|IT|natural|322|240|82|20|0.820|[server](../../test-results/liuyifan1.0-20260924-final/reference-natural-06-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/reference-natural-06-it/trace.json)|
|fixed|01|IT|natural|292|232|60|48|1.902|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-01-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-01-it/trace.json)|
|fixed|01|NT|natural|294|232|62|48|1.873|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-01-nt/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-01-nt/trace.json)|
|fixed|02|IT|natural|374|312|62|48|1.830|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-02-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-02-it/trace.json)|
|fixed|02|NT|natural|374|312|62|48|1.835|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-02-nt/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-02-nt/trace.json)|
|fixed|03|IT|natural|373|295|78|25|1.043|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-03-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-03-it/trace.json)|
|fixed|03|NT|natural|373|295|78|25|1.078|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-03-nt/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-03-nt/trace.json)|
|fixed|04|IT|natural|253|193|60|47|1.995|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-04-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-04-it/trace.json)|
|fixed|04|NT|natural|253|193|60|47|1.965|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-04-nt/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-04-nt/trace.json)|
|fixed|05|IT|natural|296|220|76|20|1.128|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-05-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-05-it/trace.json)|
|fixed|05|NT|natural|296|220|76|20|1.151|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-05-nt/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-05-nt/trace.json)|
|fixed|06|IT|natural|324|240|84|20|0.793|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-06-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-06-it/trace.json)|
|fixed|06|NT|natural|322|240|82|20|0.813|[server](../../test-results/liuyifan1.0-20260924-final/fixed-natural-06-nt/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-natural-06-nt/trace.json)|
|fixed|03|IT|20260924|373|295|78|25|1.052|[server](../../test-results/liuyifan1.0-20260924-final/fixed-20260924-03-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-20260924-03-it/trace.json)|
|fixed|03|NT|20260924|373|295|78|25|1.058|[server](../../test-results/liuyifan1.0-20260924-final/fixed-20260924-03-nt/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-20260924-03-nt/trace.json)|
|fixed|04|IT|20260924|251|193|58|47|2.005|[server](../../test-results/liuyifan1.0-20260924-final/fixed-20260924-04-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-20260924-04-it/trace.json)|
|fixed|04|NT|20260924|251|193|58|47|2.001|[server](../../test-results/liuyifan1.0-20260924-final/fixed-20260924-04-nt/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-20260924-04-nt/trace.json)|
|fixed|03|IT|20260925|373|295|78|25|1.096|[server](../../test-results/liuyifan1.0-20260924-final/fixed-20260925-03-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-20260925-03-it/trace.json)|
|fixed|03|NT|20260925|373|295|78|25|1.032|[server](../../test-results/liuyifan1.0-20260924-final/fixed-20260925-03-nt/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-20260925-03-nt/trace.json)|
|fixed|04|IT|20260925|253|193|60|47|1.985|[server](../../test-results/liuyifan1.0-20260924-final/fixed-20260925-04-it/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-20260925-04-it/trace.json)|
|fixed|04|NT|20260925|253|193|60|47|1.980|[server](../../test-results/liuyifan1.0-20260924-final/fixed-20260925-04-nt/server.log) / [trace](../../test-results/liuyifan1.0-20260924-final/fixed-20260925-04-nt/trace.json)|

## 结论

01、02、05、06的基础分与作者参考方案相同；03多一次Sense，基础分少1；04基础分少43，构成为少一个goto目标40分、动作净成本多3分。六题基础分合计1492，参考方案为1536，相差44分。

题库适合继续作为小规模原型与回归集。04应在修复求解器后再考虑作为优势题推广。

机器可读结果：[scores.csv](scores.csv)。设计说明：[DESIGN.md](DESIGN.md)。执行分析：[STRATEGY_REPORT.md](STRATEGY_REPORT.md)。
