# src1.6.3 官方配对及性能证据

WSL2 Ubuntu-18.04 / g++ 7.5.0 / 原官方 SDK。固定外部种子 20260927，原题未修改；平台上限 5000 ms。基础分不含时间奖励，耗时为真实墙钟。

|题组 / 题|模式|Stage|1.6.2 基础分|1.6.3 基础分|1.6.3 确定下界|动作相同|
|---|---|---:|---:|---:|---:|---|
|decision / 01-stop-before-conflicting-pickup|it|1|68|68|68|是|
|decision / 01-stop-before-conflicting-pickup|nt|1|68|68|68|是|
|decision / 02-pickup-route-and-capacity|it|1|34|34|34|是|
|decision / 02-pickup-route-and-capacity|nt|1|34|34|34|是|
|decision / 04-reorder-container-and-pickup|it|1|106|106|106|是|
|decision / 04-reorder-container-and-pickup|nt|1|106|106|106|是|
|combinatorial_gain / 01-two-rooms-four-goals|it|1|144|144|144|是|
|combinatorial_gain / 01-two-rooms-four-goals|nt|1|144|144|144|是|
|combinatorial_gain / 02-two-rooms-five-goals|it|1|178|178|178|是|
|combinatorial_gain / 02-two-rooms-five-goals|nt|1|178|178|178|是|
|combinatorial_gain / 03-two-rooms-six-goals|it|1|220|220|220|是|
|combinatorial_gain / 03-two-rooms-six-goals|nt|1|220|220|220|是|
|combinatorial_gain / 04-three-rooms-six-goals|it|1|216|216|216|是|
|combinatorial_gain / 04-three-rooms-six-goals|nt|1|216|216|216|是|
|constraint_tradeoff_challenge_2026 / C01|it|1|58|58|58|是|
|constraint_tradeoff_challenge_2026 / C01|nt|1|58|58|58|是|
|constraint_tradeoff_challenge_2026 / C02|it|1|98|98|98|是|
|constraint_tradeoff_challenge_2026 / C02|nt|1|98|98|98|是|
|constraint_tradeoff_challenge_2026 / C03|it|1|100|100|100|是|
|constraint_tradeoff_challenge_2026 / C03|nt|1|100|100|100|是|
|constraint_tradeoff_challenge_2026 / C04|it|1|52|52|52|是|
|constraint_tradeoff_challenge_2026 / C04|nt|1|52|52|52|是|
|constraint_tradeoff_challenge_2026 / C05|it|2|99|99|99|是|
|constraint_tradeoff_challenge_2026 / C05|nt|2|99|99|99|是|
|constraint_tradeoff_challenge_2026 / C06|it|1|96|96|96|是|
|constraint_tradeoff_challenge_2026 / C06|nt|1|96|96|96|是|
|constraint_tradeoff_challenge_2026 / C07|it|1|98|98|98|是|
|constraint_tradeoff_challenge_2026 / C07|nt|1|98|98|98|是|
|constraint_tradeoff_challenge_2026 / C08|it|1|100|100|100|是|
|constraint_tradeoff_challenge_2026 / C08|nt|1|100|100|100|是|
|constraint_tradeoff_challenge_2026 / C09|it|2|87|87|87|是|
|constraint_tradeoff_challenge_2026 / C09|nt|2|87|87|87|是|
|constraint_tradeoff_challenge_2026 / C10|it|1|140|140|140|是|
|constraint_tradeoff_challenge_2026 / C10|nt|1|140|140|140|是|
|constraint_tradeoff_challenge_2026 / N01|it|1|100|100|100|是|
|constraint_tradeoff_challenge_2026 / N01|nt|1|100|100|100|是|
|constraint_tradeoff_challenge_2026 / N02|it|1|100|100|100|是|
|constraint_tradeoff_challenge_2026 / N02|nt|1|100|100|100|是|
|constraint_tradeoff_challenge_2026 / N03|it|2|99|99|59|是|
|constraint_tradeoff_challenge_2026 / N03|nt|2|99|99|59|是|
|constraint_tradeoff_challenge_2026 / N04|it|1|100|100|100|是|
|constraint_tradeoff_challenge_2026 / N04|nt|1|100|100|100|是|
|constraint_tradeoff_challenge_2026 / N05|it|1|80|80|80|是|
|constraint_tradeoff_challenge_2026 / N05|nt|1|80|80|80|是|
|constraint_tradeoff_challenge_2026 / N06|it|2|80|80|0|是|
|constraint_tradeoff_challenge_2026 / N06|nt|2|80|80|0|是|
|constraint_tradeoff_challenge_2026 / N07|it|1|80|80|80|是|
|constraint_tradeoff_challenge_2026 / N07|nt|1|80|80|80|是|
|constraint_tradeoff_challenge_2026 / N08|it|2|79|79|79|是|
|constraint_tradeoff_challenge_2026 / N08|nt|2|79|79|79|是|
|constraint_tradeoff_challenge_2026 / N09|it|2|99|99|59|是|
|constraint_tradeoff_challenge_2026 / N09|nt|2|99|99|59|是|
|constraint_tradeoff_challenge_2026 / N10|it|1|80|80|80|是|
|constraint_tradeoff_challenge_2026 / N10|nt|1|80|80|80|是|
|constraint_tradeoff_challenge_2026 / P01|it|1|148|148|148|是|
|constraint_tradeoff_challenge_2026 / P01|nt|1|148|148|148|是|
|constraint_tradeoff_challenge_2026 / P02|it|1|148|148|148|是|
|constraint_tradeoff_challenge_2026 / P02|nt|1|148|148|148|是|
|constraint_tradeoff_challenge_2026 / P03|it|1|184|184|184|是|
|constraint_tradeoff_challenge_2026 / P03|nt|1|184|184|184|是|
|constraint_tradeoff_challenge_2026 / P04|it|1|220|220|220|是|
|constraint_tradeoff_challenge_2026 / P04|nt|1|220|220|220|是|
|constraint_tradeoff_challenge_2026 / P05|it|1|104|104|104|是|
|constraint_tradeoff_challenge_2026 / P05|nt|1|104|104|104|是|
|constraint_tradeoff_challenge_2026 / P06|it|1|232|232|232|是|
|constraint_tradeoff_challenge_2026 / P06|nt|1|232|232|232|是|
|constraint_tradeoff_challenge_2026 / P07|it|1|102|102|102|是|
|constraint_tradeoff_challenge_2026 / P07|nt|1|102|102|102|是|
|constraint_tradeoff_challenge_2026 / P08|it|1|190|190|190|是|
|constraint_tradeoff_challenge_2026 / P08|nt|1|190|190|190|是|
|constraint_tradeoff_challenge_2026 / P09|it|2|144|144|144|是|
|constraint_tradeoff_challenge_2026 / P09|nt|2|144|144|144|是|
|constraint_tradeoff_challenge_2026 / P10|it|2|191|191|191|是|
|constraint_tradeoff_challenge_2026 / P10|nt|2|191|191|191|是|
|realcompetiton_2024 / 01|it|2|421|421|421|是|
|realcompetiton_2024 / 01|nt|2|381|381|381|是|
|realcompetiton_2024 / 03|it|2|334|334|34|是|
|realcompetiton_2024 / 03|nt|2|334|334|34|是|
|realcompetiton_2024 / 06|it|2|259|330|270|否|
|realcompetiton_2024 / 06|nt|2|259|330|270|否|
|realcompetiton_2024 / 15|it|2|87|87|47|是|
|realcompetiton_2024 / 15|nt|2|87|87|47|是|
|realcompetiton_2024 / 28|it|2|816|816|816|是|
|realcompetiton_2024 / 28|nt|2|748|816|816|否|
|realcompetiton_2024 / 29|it|2|856|856|856|是|
|realcompetiton_2024 / 29|nt|2|856|856|856|是|

## 06 / 29 重复回归

|题|模式|轮|1.6.2 基础分|1.6.3 基础分|1.6.3 目标/约束/成本|
|---|---|---:|---:|---:|---|
|06|it|1|259|330|10/3/130|
|06|nt|1|259|330|10/3/130|
|29|it|1|856|856|25/0/144|
|06|it|2|259|330|10/3/130|
|06|nt|2|259|330|10/3/130|
|29|it|2|856|856|25/0/144|
|06|it|3|259|330|10/3/130|
|06|nt|3|259|330|10/3/130|
|29|it|3|856|856|25/0/144|
|06|it|4|259|330|10/3/130|
|06|nt|4|259|330|10/3/130|
|29|it|4|856|856|25/0/144|
|06|it|5|259|330|10/3/130|
|06|nt|5|259|330|10/3/130|
|29|it|5|856|856|25/0/144|

## 29 阶段耗时（5 轮中位数）

汇总阶段耗时含嵌套调用，不能相加；计时本身有额外开销。platform 为同步 SDK 调用墙钟，tail 包含它。

|阶段|1.6.2 us|1.6.3 us|
|---|---:|---:|
|terminal|8675|5233|
|binding|7114|4331|
|ledger|1948|94|
|projection|7653|6066|
|candidates|3303|3166|
|tradeoff|0|0|
|guarded|2|0|
|platform|4735697|4731002|
|tail|4749659|4740916|

详细行为差异：behavior-differences.json。完整统计：summary.json。原始日志、ASP 终态、构建命令和输入哈希见各 evidence.zip。

reproduce 是最初 1.6.1/1.6.2 的复现；profile 是统一 5000 ms 前的开发诊断对照，包含未交付原型的退化结果，不计入最终验收。最终验收仅使用 full、off、target、diagnostics_off。
