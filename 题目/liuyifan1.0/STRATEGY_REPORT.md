# liuyifan1.0 执行策略报告

五道题达到作者参考方案的目标完成数和约束保持数；04稳定少完成一个终态goto目标。05同时验证了当前内部约束估分会把已破坏的约束重新计入。以下分析以自然运行IT日志为主，各题IT/NT动作及回复一致。

## 01 自由终态汇聚

程序选择位置2的table为汇聚点，保留原地红书、蓝杯，把位置3的白瓶、绿罐和位置4的黄遥控器、黑书依次搬来。最终七个goto同时成立。16动作、成本48，与参考方案一致。这道题直接验证现有MultiGoto聚合能力。

## 02 搬运与到达共享终态

程序先做四个puton，把全部小物体搬到table，最后的四个小物体goto和table goto随布局一起成立。九个目标全部完成，16动作、成本48。它没有在完成搬运后再逐个无效访问原位置。

## 03 must-near纠错与缺失补全

初始红书被错报在位置4，蓝杯位置缺失。初始must-near投票在位置2/4之间出现平票，日志明确记录“不传播”；代码没有立即从约束得出可靠位置。搬运白瓶回table时执行一次Sense，实际读到红书、蓝杯及table，再完成绿罐搬运，七目标、两约束全部获得官方计分。

实际优势是冲突证据下保持谨慎、用一次感知恢复正确状态并共享该结果。相对参考多1次Sense、少1基础分；本题不能作为“初始零感知纠错成功”的证据。

## 04 容器纠错后的终态丢失

六次官方运行均完成5/6目标、保持2/2约束，18动作、成本47、基础分193。缺失的是goto microwave。

执行链：先将蓝杯、白瓶、绿罐放入microwave并关闭；随后Move(3)，对真实已经关闭的cupboard执行Close(3)，平台返回false，再Sense确认柜子。机器人最终停在cupboard处，而microwave位于位置4。

源码与日志对应的原因：

- `ApplyOpenCloseCorrection`依据must-closed设置了cupboard的isOpen=false，但没有建立对应已验证证据；`SolveTask_Close`在Stage 2仍选择实际验证，产生离开终点和失败动作。
- `AfterSolveTask(close microwave)`给microwave的is_keep增加2；`CalculateTaskRisk(goto microwave)`把同一keep值加到goto风险，尽管移动机器人不需要移动microwave。该候选因此eligible=false。
- 最终候选日志显示goto计划完整、预计220ms、边际收益+35，却因eligible=false被StopGate拒绝。当时仍剩约2700ms，失分不是硬超时造成的。

与参考的基础分差为43：目标少40，动作净成本多3。参考计划预先空手开microwave；当前程序在首件物体已拿起时额外使用盘子暂存，随后又去cupboard。因此成本差不能简单等同于末尾三步的7分。

修复优先级：先拆分“物体不可移动”与“机器人可到达”的风险；再统一约束推导证据与零动作完成判定；最后根据真实终态重新激活仍有收益的goto。04保留原题作为回归用例。

## 05 牺牲一个约束的收益取舍

旧启发式检测到open_cons与四个putin冲突，放弃该限制，执行Open→四组PickUp/PutIn→Close。官方完成6/6目标、计0/1约束，10动作、成本20、基础分220。选择与参考相同。

这里同时出现估分缺陷：客户端最终日志显示constraints=1/1、base_score=240；官方为0/1和220。它把重新关闭的柜门视为恢复了约束，但全过程must-closed已经在Open时永久失去计分资格。当前题目选对了策略，内部评分仍高估20分。将shadow收益排序投入实际选任务前，应先接入不可逆的约束破坏记录。

## 06 放弃低收益目标

give红杯的风险被计算为3，程序跳过该目标，只将蓝书、白瓶放到table，随后三个goto全部满足。官方完成5/6目标、保持3/3约束，7动作、成本20、基础分240，与参考相同。

交付红杯需要打开cupboard、把红杯取出并送到human，从而破坏must-closed、must-inside、must-not-near human三个不同约束。新增40目标分不足以弥补60约束分及动作成本；放弃该目标是本题的预期策略。

## 逐题真实动作

以下`×`表示平台返回false，完整反馈在trace.json中。

### 01 自由终态汇聚

Move(3) → PickUp(7) → Move(2) → PutDown(7) → Move(3) → PickUp(8) → Move(2) → PutDown(8) → Move(4) → PickUp(9) → Move(2) → PutDown(9) → Move(4) → PickUp(10) → Move(2) → PutDown(10)

[客户端决策日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-01-it/client.log) · [官方反馈日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-01-it/server.log) · [最终ASP评分](../../test-results/liuyifan1.0-20260924-final/fixed-natural-01-it/runtime/vanswer.txt)

### 02 搬运与到达共享终态

Move(3) → PickUp(5) → Move(2) → PutDown(5) → Move(3) → PickUp(6) → Move(2) → PutDown(6) → Move(4) → PickUp(7) → Move(2) → PutDown(7) → Move(4) → PickUp(8) → Move(2) → PutDown(8)

[客户端决策日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-02-it/client.log) · [官方反馈日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-02-it/server.log) · [最终ASP评分](../../test-results/liuyifan1.0-20260924-final/fixed-natural-02-it/runtime/vanswer.txt)

### 03 must-near 纠错与缺失补全

Move(3) → PickUp(7) → Move(2) → Sense() → PutDown(7) → Move(3) → PickUp(8) → Move(2) → PutDown(8)

[客户端决策日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-03-it/client.log) · [官方反馈日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-03-it/server.log) · [最终ASP评分](../../test-results/liuyifan1.0-20260924-final/fixed-natural-03-it/runtime/vanswer.txt)

### 04 容器状态纠错与合法语言扰动

PickUp(6) → Move(4) → PutDown(6) → Open(4) → PickUp(6) → PutIn(6,4) → Move(2) → PickUp(7) → Move(4) → PutIn(7,4) → Move(2) → PickUp(8) → Move(4) → PutIn(8,4) → Close(4) → Move(3) → Close(3)× → Sense()

[客户端决策日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-04-it/client.log) · [官方反馈日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-04-it/server.log) · [最终ASP评分](../../test-results/liuyifan1.0-20260924-final/fixed-natural-04-it/runtime/vanswer.txt)

### 05 牺牲一个约束解锁四个目标

Open(2) → PickUp(4) → PutIn(4,2) → PickUp(5) → PutIn(5,2) → PickUp(6) → PutIn(6,2) → PickUp(7) → PutIn(7,2) → Close(2)

[客户端决策日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-05-it/client.log) · [官方反馈日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-05-it/server.log) · [最终ASP评分](../../test-results/liuyifan1.0-20260924-final/fixed-natural-05-it/runtime/vanswer.txt)

### 06 放弃低收益目标保住三个约束

PickUp(6) → Move(2) → PutDown(6) → Move(4) → PickUp(7) → Move(2) → PutDown(7)

[客户端决策日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-06-it/client.log) · [官方反馈日志](../../test-results/liuyifan1.0-20260924-final/fixed-natural-06-it/server.log) · [最终ASP评分](../../test-results/liuyifan1.0-20260924-final/fixed-natural-06-it/runtime/vanswer.txt)

## 内部估分与官方基础分

|题|客户端最终目标数|客户端计入约束数|客户端基础分|官方基础分|解释|
|---|---:|---:|---:|---:|---|
|01|7|0|232|232|一致|
|02|9|0|312|312|一致|
|03|7|2|295|295|一致|
|04|5|1|173|193|must-inside仍为UNKNOWN，少计一个已维护约束20分|
|05|6|1|240|220|只看恢复后的关闭状态，多计已破坏约束20分|
|06|5|3|240|240|一致|

## 出题与开发建议

01/02可继续发展为终态规划题；03可扩展为有真实观测锚点的关系推理题；05/06可作为成对收益取舍回归。04优先用于修复终态回收和容器证据问题。当前测试没有执行AskLoc，也没有直接验证关闭容器搜索能力，后续应另设有信息线索的搜索原型。

建议修复顺序：goto误用keep风险 → 全过程约束记账 → 约束推导证据一致性 → 候选收益驱动任务组调度。本轮保持src1.3.3-fixed源码不变。
