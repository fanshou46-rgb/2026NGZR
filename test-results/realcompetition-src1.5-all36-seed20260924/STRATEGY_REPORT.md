# src1.5 realcompetition 36 题执行策略报告

## 总体策略

src1.5 沿用主任务顺序与风险门槛，以 CandidatePlan 做无副作用 dry-run，计算目标/约束增减、动作成本、边际 utility 与预计时长。StopGate/Deadline 只允许能在预算内完整结束的候选；多目标 goto 使用 hub 汇聚，最后再移动到目标位置。1.5 新增的 DecisionFeedback 为记录层，不改变选择规则。

本轮共选择 **259** 个候选，成功 **225**、失败 **34**；服务端失败动作 **54** 个；预测误差非零的候选 **45** 个。

候选类型计数：`multi-goto-puton=132, puton=68, goto=14, pickup=12, multi-goto-final-move=11, putin=10, takeout=6, give=5, putdown=1`。

选择原因计数：`multi_goto_hub_relocation=132, legacy_main_loop_task_order=75, legacy_check_phase_task_order=20, terminal_recovery_positive_marginal_score=14, multi_goto_hub_final_move=11, legacy_must_choose_one_risk=7`。

## 关键发现

- 全套 792 个动作中，AskLoc 85 次、Sense 51 次，实际操作/移动 656 次；Move 304 次，是出现次数最多的动作。
- 8 题最终触发 Deadline 门槛：01、11、19、20、21、28、29、30。这些题在剩余预算不足以完整执行下一候选时停止。
- 23 题出现 StopGate 收束：04、05、06、07、08、13、14、15、16、17、18、22、23、24、25、26、27、31、32、33、34、35、36。StopGate 包含无完整候选、低收益回收结束或已完成可执行目标等正常终止情形。
- 服务端失败动作共 54 次，分布为 04(9)、05(9)、06(1)、09(2)、11(1)、13(11)、14(6)、15(2)、16(5)、17(1)、34(1)、35(3)、36(3)；其中 04/05 各 9 次来自损坏题面，不能作为正常策略质量样本。
- 45 个候选的 prediction/actual 误差非零，分布为 04(5)、05(5)、06(5)、07(2)、08(1)、11(2)、13(4)、14(4)、15(2)、16(2)、17(1)、22(1)、23(1)、24(1)、34(2)、35(4)、36(3)。这表明 1.5 的反馈记录已经捕获感知/动作失败后的偏差，但当前版本尚未用误差在线调整选择策略。

## 逐题策略摘要

|题号|最终目标/约束|候选（执行顺序，连续项压缩）|动作构成|Stop/Deadline|
|---:|---:|---|---|---|
|01|10/0|puton → give → multi-goto-puton×9|askloc×2, move×14, pickup×8, putdown×9, sense×1|Deadline|
|02|—|—|—|正常收束|
|03|1/15|pickup|move×1, pickup×1|正常收束|
|04|—|give → putin → puton×2 → takeout|askloc×10, fromplate×1, move×6, pickup×2|StopGate|
|05|—|give → putin → puton×2 → takeout|askloc×10, fromplate×1, move×6, pickup×2|StopGate|
|06|5/0|puton×5|askloc×7, move×11, pickup×6, putdown×5, sense×3|StopGate|
|07|22/0|multi-goto-puton×7 → multi-goto-final-move → goto|askloc×3, move×16, pickup×7, putdown×7, sense×3|StopGate|
|08|16/0|puton×2 → multi-goto-puton×2|askloc×3, move×4, pickup×2, putdown×2, sense×2|StopGate|
|09|3/23|puton → takeout → pickup → takeout → multi-goto-final-move → goto|fromplate×1, move×6, open×1, pickup×2, putdown×4, sense×4, takeout×2|正常收束|
|10|5/1|puton → putin → puton → putin → pickup|move×9, pickup×4, putdown×2, putin×2, sense×2, takeout×1|正常收束|
|11|9/7|multi-goto-puton×9|askloc×3, move×14, pickup×9, putdown×8, sense×2|Deadline|
|12|5/0|give → putin → puton×2 → takeout|fromplate×1, move×6, open×2, pickup×4, putdown×4, putin×1, sense×3, takeout×1|正常收束|
|13|1/23|pickup×5 → multi-goto-puton → multi-goto-final-move → goto|askloc×10, move×5, pickup×6, putdown×1|StopGate|
|14|3/0|puton → give → takeout → pickup → puton → multi-goto-final-move → goto|askloc×6, move×9, open×1, pickup×1, putdown×4, sense×4, takeout×6|StopGate|
|15|3/0|putin → puton×2 → putin|askloc×4, move×5, pickup×3, putdown×3, sense×2, takeout×1|StopGate|
|16|1/0|puton×2 → putdown|askloc×4, move×5, pickup×2, putdown×3|StopGate|
|17|1/21|puton|fromplate×1, move×1, pickup×1, putdown×4, sense×1|StopGate|
|18|2/20|puton×2 → multi-goto-final-move → goto|askloc×2, move×3, pickup×1, putdown×2, sense×2|StopGate|
|19|15/0|multi-goto-puton×15|move×15, pickup×9, putdown×9|Deadline|
|20|18/0|multi-goto-puton×18|move×15, pickup×8, putdown×8, sense×1|Deadline|
|21|18/2|multi-goto-puton×18|move×15, pickup×9, putdown×9|Deadline|
|22|35/0|puton×7 → multi-goto-final-move → goto|askloc×3, move×15, pickup×7, putdown×7, sense×3|StopGate|
|23|35/0|puton×7 → multi-goto-final-move → goto|askloc×3, move×15, pickup×7, putdown×7, sense×3|StopGate|
|24|35/0|puton×7 → multi-goto-final-move → goto|askloc×3, move×15, pickup×7, putdown×7, sense×3|StopGate|
|25|20/10|multi-goto-final-move → goto|move×1, sense×1|StopGate|
|26|20/10|multi-goto-final-move → goto|move×1, sense×1|StopGate|
|27|20/10|multi-goto-final-move → goto|move×1, sense×1|StopGate|
|28|15/0|multi-goto-puton×15|move×15, pickup×9, putdown×9|Deadline|
|29|17/0|multi-goto-puton×17|move×15, pickup×9, putdown×9|Deadline|
|30|21/0|multi-goto-puton×21|move×15, pickup×9, putdown×9|Deadline|
|31|1/23|pickup → goto|fromplate×1, move×2, pickup×1, putdown×3, sense×1|StopGate|
|32|1/23|pickup → goto|fromplate×1, move×2, pickup×1, putdown×3, sense×1|StopGate|
|33|1/23|pickup → goto|fromplate×1, move×2, pickup×1, putdown×3, sense×1|StopGate|
|34|36/0|puton×2 → putin → puton×5|askloc×3, move×13, open×1, pickup×5, putdown×6, putin×1, sense×2, takeout×3|StopGate|
|35|30/0|puton×2 → putin → puton×5|askloc×5, move×13, open×1, pickup×6, putdown×5, putin×1, sense×2, takeout×2|StopGate|
|36|29/0|puton×2 → putin → puton×5|askloc×4, move×13, open×1, pickup×7, putdown×5, putin×1, sense×2, takeout×2|StopGate|

## 逐题完整动作序列

- **01**（319 分）：PutDown 24 → AskLoc 25 → AskLoc 25 → PickUp 6 → Sense → PutDown 6 → Move 2 → PickUp 7 → Move 1 → PutDown 7 → Move 3 → PickUp 8 → Move 1 → PutDown 8 → Move 4 → PickUp 9 → Move 1 → PutDown 9 → Move 5 → PickUp 10 → Move 1 → PutDown 10 → Move 6 → PickUp 11 → Move 1 → PutDown 11 → Move 7 → PickUp 12 → Move 1 → PutDown 12 → Move 8 → PickUp 13 → Move 1 → PutDown 13
- **02**（0 分）：无动作
- **03**（426 分）：Move 8 → PickUp 12
- **04**（0 分）：FromPlate 10 → PickUp 10 → AskLoc 10 → AskLoc 10 → PickUp 16 → AskLoc 16 → AskLoc 16 → Move 5 → AskLoc 11 → AskLoc 11 → Move 5 → Move 2 → AskLoc 13 → AskLoc 13 → Move 2 → Move 6 → AskLoc 6 → AskLoc 6 → Move 6
- **05**（0 分）：FromPlate 10 → PickUp 10 → AskLoc 10 → AskLoc 10 → PickUp 16 → AskLoc 16 → AskLoc 16 → Move 5 → AskLoc 11 → AskLoc 11 → Move 5 → Move 2 → AskLoc 13 → AskLoc 13 → Move 2 → Move 6 → AskLoc 6 → AskLoc 6 → Move 6
- **06**（135 分）：Move 4 → PickUp 9 → Sense → AskLoc 5 → AskLoc 5 → AskLoc 5 → Move 6 → Sense → PutDown 9 → Move 3 → PickUp 23 → AskLoc 23 → Move 8 → PickUp 23 → Move 3 → Sense → PutDown 23 → AskLoc 22 → Move 8 → PickUp 22 → Move 3 → PutDown 22 → AskLoc 21 → Move 8 → PickUp 21 → Move 3 → PutDown 21 → AskLoc 20 → Move 8 → PickUp 20 → Move 3 → PutDown 20
- **07**（793 分）：Move 4 → PickUp 6 → Sense → AskLoc 5 → AskLoc 5 → AskLoc 5 → Move 6 → Sense → PutDown 6 → Move 4 → PickUp 7 → Move 6 → PutDown 7 → Move 4 → PickUp 8 → Move 6 → PutDown 8 → Move 4 → PickUp 9 → Move 6 → PutDown 9 → Move 4 → PickUp 10 → Move 6 → PutDown 10 → Move 4 → PickUp 11 → Move 6 → PutDown 11 → Move 4 → PickUp 12 → Move 6 → PutDown 12 → Move 4 → Move 6 → Sense
- **08**（676 分）：Move 4 → PickUp 6 → Sense → AskLoc 5 → AskLoc 5 → AskLoc 5 → Move 6 → Sense → PutDown 6 → Move 4 → PickUp 7 → Move 6 → PutDown 7
- **09**（582 分）：PutDown 9 → FromPlate 10 → PutDown 10 → Move 1 → PickUp 13 → Move 4 → Sense → PutDown 13 → Move 2 → Open 4 → TakeOut 11 4 → Sense → Move 6 → PickUp 12 → PutDown 12 → Move 2 → TakeOut 11 4 → Sense → Move 1 → Sense
- **10**（212 分）：Move 8 → TakeOut 12 8 → Move 5 → Sense → PutDown 12 → Move 2 → PickUp 13 → Move 8 → PutIn 13 8 → Move 5 → PickUp 11 → Move 4 → Sense → PutDown 11 → Move 2 → PickUp 15 → Move 9 → PutIn 15 9 → Move 5 → PickUp 18
- **11**（412 分）：Move 10 → PickUp 6 → AskLoc 6 → AskLoc 6 → PickUp 7 → Sense → AskLoc 20 → PutDown 7 → PickUp 14 → Move 2 → Sense → PutDown 14 → Move 15 → PickUp 2 → Move 2 → PutDown 2 → Move 5 → PickUp 3 → Move 2 → PutDown 3 → Move 13 → PickUp 4 → Move 2 → PutDown 4 → Move 8 → PickUp 9 → Move 2 → PutDown 9 → Move 7 → PickUp 10 → Move 2 → PutDown 10 → Move 7 → PickUp 11 → Move 2 → PutDown 11
- **12**（191 分）：FromPlate 10 → Sense → PutDown 10 → PickUp 16 → Move 7 → PutDown 16 → Open 7 → PickUp 16 → PutIn 16 7 → Move 5 → PickUp 11 → Move 4 → Sense → PutDown 11 → Move 2 → PickUp 13 → Move 5 → Sense → PutDown 13 → Move 6 → Open 6 → TakeOut 14 6
- **13**（496 分）：PutDown 3 → PickUp 5 → AskLoc 5 → AskLoc 5 → AskLoc 5 → PickUp 5 → AskLoc 5 → PickUp 5 → AskLoc 5 → PickUp 5 → AskLoc 5 → PickUp 5 → AskLoc 5 → PickUp 5 → Move 1 → AskLoc 4 → Move 1 → Move 1 → Move 1 → AskLoc 4 → AskLoc 4 → Move 1
- **14**（70 分）：Move 14 → TakeOut 19 14 → AskLoc 19 → AskLoc 19 → Open 14 → AskLoc 14 → TakeOut 19 14 → AskLoc 21 → Move 5 → TakeOut 21 5 → Sense → Move 1 → Sense → PutDown 21 → Move 5 → TakeOut 18 5 → PutDown 18 → AskLoc 16 → Move 3 → PickUp 16 → PutDown 16 → Move 14 → TakeOut 19 14 → AskLoc 19 → Move 12 → TakeOut 19 12 → Move 3 → Sense → PutDown 19 → Move 10 → Sense
- **15**（132 分）：PutDown 13 → AskLoc 11 → AskLoc 11 → AskLoc 19 → Move 2 → PickUp 19 → Sense → PutDown 19 → Move 15 → PickUp 15 → Move 20 → Sense → PutDown 15 → Move 3 → TakeOut 18 3 → AskLoc 18 → Move 2 → PickUp 18
- **16**（66 分）：PutDown 20 → PickUp 16 → Move 11 → AskLoc 9 → AskLoc 9 → Move 11 → AskLoc 9 → Move 11 → PutDown 16 → Move 11 → AskLoc 13 → Move 11 → PickUp 18 → PutDown 18
- **17**（521 分）：PutDown 20 → PickUp 13 → PutDown 13 → FromPlate 2 → PutDown 2 → Move 22 → Sense → PutDown 13
- **18**（530 分）：PutDown 10 → AskLoc 26 → AskLoc 26 → Move 45 → PickUp 29 → Move 44 → Sense → PutDown 29 → Move 12 → Sense
- **19**（522 分）：Move 7 → PickUp 10 → PutDown 10 → PickUp 11 → PutDown 11 → Move 15 → PickUp 2 → Move 7 → PutDown 2 → Move 14 → PickUp 3 → Move 7 → PutDown 3 → Move 13 → PickUp 4 → Move 7 → PutDown 4 → Move 12 → PickUp 5 → Move 7 → PutDown 5 → Move 11 → PickUp 6 → Move 7 → PutDown 6 → Move 10 → PickUp 7 → Move 7 → PutDown 7 → Move 9 → PickUp 8 → Move 7 → PutDown 8
- **20**（645 分）：Move 3 → PickUp 3 → Sense → PutDown 3 → Move 4 → PickUp 2 → Move 3 → PutDown 2 → Move 15 → PickUp 4 → Move 3 → PutDown 4 → Move 12 → PickUp 5 → Move 3 → PutDown 5 → Move 11 → PickUp 6 → Move 3 → PutDown 6 → Move 10 → PickUp 7 → Move 3 → PutDown 7 → Move 9 → PickUp 8 → Move 3 → PutDown 8 → Move 8 → PickUp 9 → Move 3 → PutDown 9
- **21**（678 分）：Move 9 → PickUp 8 → PutDown 8 → PickUp 13 → PutDown 13 → Move 15 → PickUp 2 → Move 9 → PutDown 2 → Move 14 → PickUp 3 → Move 9 → PutDown 3 → Move 13 → PickUp 4 → Move 9 → PutDown 4 → Move 12 → PickUp 5 → Move 9 → PutDown 5 → Move 11 → PickUp 6 → Move 9 → PutDown 6 → Move 10 → PickUp 7 → Move 9 → PutDown 7 → Move 8 → PickUp 9 → Move 9 → PutDown 9
- **22**（1000 分）：Move 4 → PickUp 11 → Sense → AskLoc 5 → AskLoc 5 → AskLoc 5 → Move 6 → Sense → PutDown 11 → Move 4 → PickUp 9 → Move 6 → PutDown 9 → Move 4 → PickUp 10 → Move 6 → PutDown 10 → Move 4 → PickUp 6 → Move 6 → PutDown 6 → Move 4 → PickUp 12 → Move 6 → PutDown 12 → Move 4 → PickUp 7 → Move 6 → PutDown 7 → Move 4 → PickUp 8 → Move 6 → PutDown 8 → Move 3 → Sense
- **23**（1000 分）：Move 4 → PickUp 11 → Sense → AskLoc 5 → AskLoc 5 → AskLoc 5 → Move 6 → Sense → PutDown 11 → Move 4 → PickUp 9 → Move 6 → PutDown 9 → Move 4 → PickUp 10 → Move 6 → PutDown 10 → Move 4 → PickUp 6 → Move 6 → PutDown 6 → Move 4 → PickUp 12 → Move 6 → PutDown 12 → Move 4 → PickUp 7 → Move 6 → PutDown 7 → Move 4 → PickUp 8 → Move 6 → PutDown 8 → Move 3 → Sense
- **24**（1000 分）：Move 4 → PickUp 11 → Sense → AskLoc 5 → AskLoc 5 → AskLoc 5 → Move 6 → Sense → PutDown 11 → Move 4 → PickUp 9 → Move 6 → PutDown 9 → Move 4 → PickUp 10 → Move 6 → PutDown 10 → Move 4 → PickUp 6 → Move 6 → PutDown 6 → Move 4 → PickUp 12 → Move 6 → PutDown 12 → Move 4 → PickUp 7 → Move 6 → PutDown 7 → Move 4 → PickUp 8 → Move 6 → PutDown 8 → Move 3 → Sense
- **25**（1000 分）：Move 10 → Sense
- **26**（1000 分）：Move 10 → Sense
- **27**（1000 分）：Move 10 → Sense
- **28**（522 分）：Move 7 → PickUp 10 → PutDown 10 → PickUp 11 → PutDown 11 → Move 15 → PickUp 2 → Move 7 → PutDown 2 → Move 14 → PickUp 3 → Move 7 → PutDown 3 → Move 13 → PickUp 4 → Move 7 → PutDown 4 → Move 12 → PickUp 5 → Move 7 → PutDown 5 → Move 11 → PickUp 6 → Move 7 → PutDown 6 → Move 10 → PickUp 7 → Move 7 → PutDown 7 → Move 9 → PickUp 8 → Move 7 → PutDown 8
- **29**（596 分）：Move 7 → PickUp 2 → PutDown 2 → PickUp 19 → PutDown 19 → Move 8 → PickUp 3 → Move 7 → PutDown 3 → Move 9 → PickUp 4 → Move 7 → PutDown 4 → Move 10 → PickUp 5 → Move 7 → PutDown 5 → Move 11 → PickUp 6 → Move 7 → PutDown 6 → Move 12 → PickUp 7 → Move 7 → PutDown 7 → Move 13 → PickUp 8 → Move 7 → PutDown 8 → Move 14 → PickUp 9 → Move 7 → PutDown 9
- **30**（756 分）：Move 10 → PickUp 7 → PutDown 7 → PickUp 14 → PutDown 14 → Move 4 → PickUp 2 → Move 10 → PutDown 2 → Move 3 → PickUp 3 → Move 10 → PutDown 3 → Move 15 → PickUp 4 → Move 10 → PutDown 4 → Move 12 → PickUp 5 → Move 10 → PutDown 5 → Move 11 → PickUp 6 → Move 10 → PutDown 6 → Move 9 → PickUp 8 → Move 10 → PutDown 8 → Move 8 → PickUp 9 → Move 10 → PutDown 9
- **31**（557 分）：PutDown 3 → FromPlate 2 → PutDown 2 → Move 2 → PickUp 5 → PutDown 5 → Move 1 → Sense
- **32**（557 分）：PutDown 3 → FromPlate 2 → PutDown 2 → Move 2 → PickUp 5 → PutDown 5 → Move 1 → Sense
- **33**（559 分）：PutDown 3 → FromPlate 2 → PutDown 2 → Move 2 → PickUp 5 → PutDown 5 → Move 1 → Sense
- **34**（1000 分）：Move 6 → PickUp 17 → AskLoc 17 → AskLoc 17 → Open 6 → TakeOut 15 6 → Move 2 → Sense → PutDown 15 → Move 8 → PickUp 10 → Move 6 → PutIn 10 6 → PickUp 12 → Move 4 → Sense → PutDown 12 → AskLoc 17 → Move 6 → TakeOut 17 6 → Move 2 → PutDown 17 → Move 8 → PickUp 18 → Move 2 → PutDown 18 → Move 7 → PickUp 13 → Move 2 → PutDown 13 → Move 6 → TakeOut 14 6 → Move 2 → PutDown 14
- **35**（1000 分）：Move 6 → PickUp 17 → AskLoc 17 → AskLoc 17 → Open 6 → TakeOut 15 6 → Move 9 → AskLoc 2 → Move 10 → Sense → PutDown 15 → Move 8 → PickUp 10 → Move 6 → PutIn 10 6 → PickUp 12 → Move 4 → Sense → PutDown 12 → AskLoc 17 → Move 1 → PickUp 17 → AskLoc 17 → Move 6 → TakeOut 17 6 → Move 10 → PutDown 17 → Move 8 → PickUp 18 → Move 10 → PutDown 18 → Move 7 → PickUp 13 → Move 10 → PutDown 13
- **36**（1000 分）：Move 8 → PickUp 17 → Move 2 → Sense → PutDown 17 → Move 6 → Open 6 → TakeOut 15 6 → Move 2 → PutDown 15 → Move 8 → PickUp 10 → Move 6 → PutIn 10 6 → PickUp 12 → Move 4 → Sense → PutDown 12 → Move 6 → PickUp 18 → AskLoc 18 → AskLoc 18 → AskLoc 18 → TakeOut 18 6 → Move 2 → PutDown 18 → Move 6 → PickUp 14 → AskLoc 14 → Move 1 → PickUp 14 → Move 7 → PickUp 13 → Move 2 → PutDown 13

## 结论

本报告描述的是固定种子下的一次官方平台实跑。Stage 2 的 AskLoc/Sense 回复具有随机性；更换种子后，部分题的询问分支、动作数与得分可能变化。DecisionFeedback 的 prediction/actual/error 已保存在各题 client.log 和 `results.json`，可用于后续定位具体候选误差。
