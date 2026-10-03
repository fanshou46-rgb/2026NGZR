# 11类证据索引

主分类互斥；次要机制与目标级细分分别列出。日志行号是保留原件中的实际行号，客户端摘录已去ANSI，仅为了阅读。

## qualification-too-strict

主分类 12 pair，目标净损失 408，基础分损失 14736；目标级独有ID 408，40分目标损失 16320。

旧版初始 MustChooseOne 绕过 eligible=false，先 Move4/PickUp11，AskLoc5 经两次 not_known 后得到真实 at(5,6)，随后 Move6+Sense 确认沙发并逐物完成重复目标。新版先 GOTO桌子3；其他 puton 因资格不通过，Probe 的地点4被未知约束安全拒绝，在约4.8秒余量时停止。

旧版34个独有目标由实际放物和官方评分确认；原错误沙发位置4已被 AskLoc/Sense 纠正后才送达6。旧版官方0/2约束，新版2/2；这是执行约束交换后的实际高收益，不属于全约束安全 recoverable，也不是错误目标信息碰巧得分的 legacy-lucky。重复34项集中于7个对象放物，不等于34次独立物理成功。

[完整代表pair](pair-evidence/c019-it-r1.md)

### baseline

[r1-c019-it-baseline:L241](evidence/r1-c019-it-baseline/client.log#L241)
```text
[LOG]:[3B][Candidate] phase=main-loop rank=1 task_index=0 behave=puton legacy_choice=true eligible=false complete=true actions=4 duration_ms=420 action_cost=9 score_before=0 score_after=1351 marginal_score=1351 utility=1351 gained_goals=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33] lost_goals=[] broken_constraints=[0,1] preserved_constraints=[]
```

[r1-c019-it-baseline:L456](evidence/r1-c019-it-baseline/client.log#L456)
```text
[LOG]:[3B][Candidate] phase=must-choose-one rank=1 task_index=0 behave=puton legacy_choice=false eligible=false complete=true actions=4 duration_ms=420 action_cost=9 score_before=0 score_after=1351 marginal_score=1351 utility=1351 gained_goals=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33] lost_goals=[] broken_constraints=[0,1] preserved_constraints=[]
```

[r1-c019-it-baseline:L459](evidence/r1-c019-it-baseline/client.log#L459)
```text
[LOG]:[3B][Candidate] phase=must-choose-one rank=2 task_index=1 behave=puton legacy_choice=false eligible=false complete=true actions=4 duration_ms=420 action_cost=9 score_before=0 score_after=1351 marginal_score=1351 utility=1351 gained_goals=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33] lost_goals=[] broken_constraints=[0,1] preserved_constraints=[]
```

[r1-c019-it-baseline:L684](evidence/r1-c019-it-baseline/client.log#L684)
```text
[LOG]:[3B][Candidate] phase=must-choose-one-post-check rank=1 task_index=0 behave=puton legacy_choice=true eligible=false complete=true actions=4 duration_ms=420 action_cost=9 score_before=0 score_after=1351 marginal_score=1351 utility=1351 gained_goals=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33] lost_goals=[] broken_constraints=[0,1] preserved_constraints=[]
```

[r1-c019-it-baseline:L786](evidence/r1-c019-it-baseline/client.log#L786)
```text
[LOG]:[3B][Candidate] phase=must-choose-one-post-check rank=35 task_index=34 behave=goto legacy_choice=false eligible=true complete=true actions=2 duration_ms=220 action_cost=5 score_before=0 score_after=35 marginal_score=35 utility=35 gained_goals=[34] lost_goals=[] broken_constraints=[] preserved_constraints=[0,1]
```

[r1-c019-it-baseline:L788](evidence/r1-c019-it-baseline/client.log#L788)
```text
[LOG]:[TradeoffDecision] phase=must-choose-one-post-check task=0 decision=execute priority=1351 incumbent_priority=35 lower=1351 upper=1391 group=1
```

[r1-c019-it-baseline:L1415](evidence/r1-c019-it-baseline/client.log#L1415)
```text
[LOG]:[3A][final] goals=35/35 (unknown=0), constraints=0/2 (unknown=0), base_score=1303, action_cost=97, elapsed=3308ms, remaining=1692ms
```

### current

[r1-c019-it-current:L345](evidence/r1-c019-it-current/client.log#L345)
```text
[LOG]:[Scheduler] filtered task=0 stable_id=0 marginal=1351 reason=ineligible
```

[r1-c019-it-current:L347](evidence/r1-c019-it-current/client.log#L347)
```text
[LOG]:[Scheduler] filtered task=1 stable_id=1 marginal=1351 reason=ineligible
```

[r1-c019-it-current:L604](evidence/r1-c019-it-current/client.log#L604)
```text
[LOG]:[Scheduler] filtered task=32 stable_id=32 marginal=1311 reason=ineligible
```

[r1-c019-it-current:L606](evidence/r1-c019-it-current/client.log#L606)
```text
[LOG]:[Scheduler] filtered task=33 stable_id=33 marginal=1311 reason=ineligible
```

[r1-c019-it-current:L614](evidence/r1-c019-it-current/client.log#L614)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"blocked_task","world_revision":2,"total_probes":0,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"task=0,stable_id=0,filter=risk_eligibility","closed_reason":""}
```

[r1-c019-it-current:L616](evidence/r1-c019-it-current/client.log#L616)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"blocking_fact","world_revision":2,"total_probes":0,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"task=0,stable_id=0,filter=risk_eligibility,fact=LOCATION:6,reason=unverified","closed_reason":""}
```

[r1-c019-it-current:L882](evidence/r1-c019-it-current/client.log#L882)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"blocking_fact","world_revision":2,"total_probes":0,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"task=33,stable_id=33,filter=risk_eligibility,fact=INSIDE:12,reason=unverified","closed_reason":""}
```

## probe-coverage-gap

主分类 4 pair，目标净损失 28，基础分损失 1044；目标级独有ID 24，40分目标损失 960。

旧版先黑罐17的 puton，新版先绿色杯12的 puton。旧版在错误 outside14@6 上 PickUp14 失败后 AskLoc14 得到真实 inside(14,6)，随后 TakeOut14 6/PutDown14 成功，满足六个重复黑杯目标。新版 Probe 只 Move+Sense，看到地点6没有14形成冲突，无法发现 inside；重复相关上下文拒绝后停止。另一个红杯 putin29 因 pickup11已完成而出现 gain1/loss1的排序后果。

无约束；黑杯恢复在得到真实 inside反馈后执行，失败触发的纠错不是依赖错误信息碰巧达成目标。六重复目标由一次实际取出并放到沙发完成。红杯goal29的旧版成功由正确初始位置8与 PutIn10 6 true确认。

[完整代表pair](pair-evidence/c033-it-r1.md)

### baseline

[r1-c033-it-baseline:L2826](evidence/r1-c033-it-baseline/client.log#L2826)
```text
[LOG]:[3A][final] goals=36/45 (unknown=9), constraints=0/0 (unknown=0), base_score=1348, action_cost=92, elapsed=3255ms, remaining=1745ms
```

[r1-c033-it-baseline:L2828](evidence/r1-c033-it-baseline/client.log#L2828)
```text
[LOG]:[3A][final] completed_goals=[0:puton,1:puton,2:puton,3:puton,4:puton,5:puton,6:putin,7:puton,8:puton,9:puton,10:puton,11:puton,12:puton,13:puton,23:puton,24:puton,25:puton,26:puton,27:puton,28:puton,29:puton,30:puton,31:puton,32:puton,33:puton,34:puton,35:pickup,36:goto,37:goto,38:goto,39:goto,40:goto,41:goto,42:goto,43:goto,44:goto], satisfied_constraints=[]
```

### current

[r1-c033-it-current:L416](evidence/r1-c033-it-current/client.log#L416)
```text
[LOG]:[GuardedDecision] outcome=greedy reason=unsupported_or_time stage=2 deferred_goto=true
```

[r1-c033-it-current:L624](evidence/r1-c033-it-current/client.log#L624)
```text
[LOG]:[GuardedDecision] outcome=greedy reason=unsupported_or_time stage=2 deferred_goto=true
```

[r1-c033-it-current:L2303](evidence/r1-c033-it-current/client.log#L2303)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"blocking_fact","world_revision":23,"total_probes":1,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"task=6,stable_id=16,filter=risk_eligibility,fact=LOCATION:14,reason=conflict","closed_reason":""}
```

[r1-c033-it-current:L2309](evidence/r1-c033-it-current/client.log#L2309)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"blocking_fact","world_revision":23,"total_probes":1,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"task=7,stable_id=17,filter=risk_eligibility,fact=LOCATION:14,reason=conflict","closed_reason":""}
```

[r1-c033-it-current:L2397](evidence/r1-c033-it-current/client.log#L2397)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"candidate","world_revision":23,"total_probes":1,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"duplicate_related_revision","closed_reason":"","signature":"sense_at:6","kind":"MoveSense","target_location":6,"eligible":false,"cost":5,"duration_ms":220,"fact_count":4,"potential_goal_value":600,"stable_id":16,"constraint_result":"constraint_safe","facts":[{"field":"LOCATION","id":14,"task":6,"stable_task_id":16,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":14,"task":6,"stable_task_id":16,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":14,"task":7,"stable_task_id":17,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":14,"task":7,"stable_task_id":17,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":14,"task":8,"stable_task_id":18,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":14,"task":8,"stable_task_id":18,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":14,"task":9,"stable_task_id":19,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":14,"task":9,"stable_task_id":19,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":14,"task":10,"stable_task_id":20,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":14,"task":10,"stable_task_id":20,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":14,"task":11,"stable_task_id":21,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":14,"task":11,"stable_task_id":21,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":18,"task":26,"stable_task_id":36,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":18,"task":26,"stable_task_id":36,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":18,"task":27,"stable_task_id":37,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":18,"task":27,"stable_task_id":37,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":18,"task":28,"stable_task_id":38,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":18,"task":28,"stable_task_id":38,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":18,"task":29,"stable_task_id":39,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":18,"task":29,"stable_task_id":39,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":18,"task":30,"stable_task_id":40,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":18,"task":30,"stable_task_id":40,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":18,"task":31,"stable_task_id":41,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":18,"task":31,"stable_task_id":41,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":18,"task":32,"stable_task_id":42,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":18,"task":32,"stable_task_id":42,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":18,"task":33,"stable_task_id":43,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":18,"task":33,"stable_task_id":43,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":18,"task":34,"stable_task_id":44,"reason":"conflict","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":18,"task":34,"stable_task_id":44,"reason":"unverified","location_hints":[{"location":6,"source":"object_location:claim_source=1"}]}]}
```

[r1-c033-it-current:L2548](evidence/r1-c033-it-current/client.log#L2548)
```text
[LOG]:[GuardedDecision] outcome=greedy reason=unsupported_or_time stage=2 deferred_goto=false
```

[r1-c033-it-current:L2655](evidence/r1-c033-it-current/client.log#L2655)
```text
[LOG]:[GuardedDecision] outcome=greedy reason=unsupported_or_time stage=2 deferred_goto=false
```

## no-location-clue

主分类 0 pair，目标净损失 0，基础分损失 0；目标级独有ID 0，40分目标损失 0。

本筛选集合没有该类主因，不能提供正例代表。

[c011](pair-evidence/c011-it-r1.md)未知白杯21影响双方give；旧独有goal5为已知地点的GOTO，主因是三次上限。

## constraint-gate-strict

主分类 4 pair，目标净损失 16，基础分损失 284；目标级独有ID 16，40分目标损失 640。

首次实动作分叉在共同完成白杯后：旧版先 PickUp 17，新版先 PickUp 13；两版最后均完成六个杯子目标。目标损失发生在后续书本任务：旧版在 check-phase 允许组合收益放行，进入地点3并完成四个书本目标；新版 requires_verified_group 过滤这些任务，Stage 2 guarded 不支持，Probe 的移动又被 constraint_safety_unknown 拒绝，在有余时停止。

旧版官方约束3/5，新版5/5；进入书桌和白瓶所在地3使两个约束失去信用。四个书本目标实际成功，但这不是全约束安全的恢复。错误椅子地点8触发的书本发现发生在共同前缀，随后已得到 Sense，不能把旧版独有的四个目标归为 legacy-lucky。

[完整代表pair](pair-evidence/c003-it-r1.md)

### baseline

[r1-c003-it-baseline:L1504](evidence/r1-c003-it-baseline/client.log#L1504)
```text
[LOG]:[TradeoffDecision] phase=check-phase task=1 decision=execute score=270 incumbent=255 group=2
```

[r1-c003-it-baseline:L1870](evidence/r1-c003-it-baseline/client.log#L1870)
```text
[LOG]:[3A][final] goals=10/18 (unknown=6), constraints=0/5 (unknown=3), base_score=266, action_cost=134, elapsed=4693ms, remaining=307ms
```

[r1-c003-it-baseline:L1872](evidence/r1-c003-it-baseline/client.log#L1872)
```text
[LOG]:[3A][final] completed_goals=[1:puton,2:puton,3:puton,4:puton,9:puton,13:puton,14:puton,15:puton,16:puton,17:puton], satisfied_constraints=[]
```

### current

[r1-c003-it-current:L242](evidence/r1-c003-it-current/client.log#L242)
```text
[LOG]:[TradeoffDecision] phase=greedy-filter task=6 decision=defer reason=requires_verified_group
```

[r1-c003-it-current:L260](evidence/r1-c003-it-current/client.log#L260)
```text
[LOG]:[TradeoffDecision] phase=greedy-filter task=7 decision=defer reason=requires_verified_group
```

[r1-c003-it-current:L530](evidence/r1-c003-it-current/client.log#L530)
```text
[LOG]:[GuardedDecision] outcome=greedy reason=unsupported_or_time stage=2 deferred_goto=false
```

[r1-c003-it-current:L896](evidence/r1-c003-it-current/client.log#L896)
```text
[LOG]:[GuardedDecision] outcome=greedy reason=unsupported_or_time stage=2 deferred_goto=false
```

[r1-c003-it-current:L1786](evidence/r1-c003-it-current/client.log#L1786)
```text
[LOG]:[GuardedDecision] outcome=greedy reason=unsupported_or_time stage=2 deferred_goto=false
```

[r1-c003-it-current:L1909](evidence/r1-c003-it-current/client.log#L1909)
```text
[LOG]:[TradeoffDecision] phase=greedy-filter task=16 decision=defer reason=requires_verified_group
```

[r1-c003-it-current:L1915](evidence/r1-c003-it-current/client.log#L1915)
```text
[LOG]:[TradeoffDecision] phase=greedy-filter task=17 decision=defer reason=requires_verified_group
```

## legacy-lucky

主分类 0 pair，目标净损失 0，基础分损失 0；目标级独有ID 0，40分目标损失 0。

本筛选集合没有该类主因，不能提供正例代表。

错误信息与真实成功必须分开。参见[c011：错误AskLoc未产生成绩差集](pair-evidence/c011-it-r1.md)、[c003：共同前缀中的错误线索发现](pair-evidence/c003-it-r1.md)、[c033：纠正inside之后的成功](pair-evidence/c033-it-r1.md)。

## ordering-cascade

主分类 12 pair，目标净损失 24，基础分损失 868；目标级独有ID 28，40分目标损失 1120。

旧版先完成白书 puton 再依次放物，最后 pickup 红罐18；新版第一轮选择边际34的 pickup18，随后放物需要暂时放下18，gain=1/loss=1，单任务边际为负且部分资格变为 false。五次 Probe 增加信息，仍无法消除该目标交换结构；Stage 2 没有任务组执行，最终只保留 pickup18。

旧版五目标全部由官方评分确认，禁止开冰箱的约束1/1仍有信用，获胜放物动作反馈均 true。旧版目标没有依赖本题错误的白杯/遥控器信息。安全恢复路径已在旧版观察到，但未测试新版的修改方案。

[完整代表pair](pair-evidence/c007-it-r1.md)

### baseline

[r1-c007-it-baseline:L111](evidence/r1-c007-it-baseline/client.log#L111)
```text
[LOG]:[TradeoffDecision] phase=main-loop task=0 decision=execute reason=legacy_priority lower=27 upper=167
```

[r1-c007-it-baseline:L324](evidence/r1-c007-it-baseline/client.log#L324)
```text
[LOG]:[3A][final] goals=5/5 (unknown=0), constraints=0/1 (unknown=1), base_score=144, action_cost=56, elapsed=1883ms, remaining=3117ms
```

[r1-c007-it-baseline:L326](evidence/r1-c007-it-baseline/client.log#L326)
```text
[LOG]:[3A][final] completed_goals=[0:puton,1:putin,2:puton,3:putin,4:pickup], satisfied_constraints=[]
```

### current

[r1-c007-it-current:L164](evidence/r1-c007-it-current/client.log#L164)
```text
[LOG]:[Scheduler] greedy task=4 marginal=34 remaining_ms=5000 group_attempt=true
```

[r1-c007-it-current:L166](evidence/r1-c007-it-current/client.log#L166)
```text
[LOG]:[GuardedDecision] outcome=greedy reason=unsupported_or_time stage=2 deferred_goto=false
```

[r1-c007-it-current:L186](evidence/r1-c007-it-current/client.log#L186)
```text
[LOG]:[3B][Candidate] phase=greedy-round rank=1 task_index=2 behave=puton legacy_choice=false eligible=false complete=true actions=5 duration_ms=520 action_cost=11 score_before=34 score_after=23 marginal_score=-11 utility=-11 gained_goals=[2] lost_goals=[4] broken_constraints=[] preserved_constraints=[0]
```

[r1-c007-it-current:L189](evidence/r1-c007-it-current/client.log#L189)
```text
[LOG]:[3B][Candidate] phase=greedy-round rank=2 task_index=1 behave=putin legacy_choice=false eligible=false complete=true actions=5 duration_ms=540 action_cost=14 score_before=34 score_after=20 marginal_score=-14 utility=-14 gained_goals=[1] lost_goals=[4] broken_constraints=[] preserved_constraints=[0]
```

[r1-c007-it-current:L207](evidence/r1-c007-it-current/client.log#L207)
```text
[LOG]:[GuardedDecision] outcome=greedy reason=unsupported_or_time stage=2 deferred_goto=false
```

[r1-c007-it-current:L536](evidence/r1-c007-it-current/client.log#L536)
```text
[LOG]:[GuardedDecision] outcome=greedy reason=unsupported_or_time stage=2 deferred_goto=false
```

[r1-c007-it-current:L584](evidence/r1-c007-it-current/client.log#L584)
```text
[LOG]:[3B][Candidate] phase=greedy-round rank=3 task_index=2 behave=puton legacy_choice=false eligible=false complete=true actions=5 duration_ms=540 action_cost=14 score_before=9 score_after=-5 marginal_score=-14 utility=-14 gained_goals=[2] lost_goals=[4] broken_constraints=[] preserved_constraints=[0]
```

## group-search-gap

主分类 8 pair，目标净损失 12，基础分损失 288；目标级独有ID 12，40分目标损失 480。

共同 PutDown10 后，旧版 Move45/PickUp29/Move44/PutDown29，再末尾 GOTO12；新版先 GOTO12，随后黑书 puton 将暂时失去 GOTO，单任务净边际非正。Stage 2 guarded 不支持，Probe 无法证明移动安全或投影含额外物理动作；新版放弃黑书。这里需要绑定 puton29 后返回12的组合才能保留两目标。

旧版官方20/20约束都有信用，黑书地点45与书桌44均来自正确原始信息，PickUp29/PutDown29均 true。丢失 goal4 属于安全可恢复路径；内部约束0/20 unknown=19 与官方信用20/20的差异单列。

[完整代表pair](pair-evidence/c015-it-r1.md)

### baseline

[r1-c015-it-baseline:L288](evidence/r1-c015-it-baseline/client.log#L288)
```text
[LOG]:[TradeoffDecision] phase=main-loop task=2 decision=execute reason=legacy_priority lower=25 upper=545
```

[r1-c015-it-baseline:L485](evidence/r1-c015-it-baseline/client.log#L485)
```text
[LOG]:[TradeoffDecision] phase=terminal-recovery task=3 decision=execute reason=legacy_priority lower=60 upper=540
```

[r1-c015-it-baseline:L533](evidence/r1-c015-it-baseline/client.log#L533)
```text
[LOG]:[3A][final] goals=2/4 (unknown=1), constraints=0/20 (unknown=19), base_score=60, action_cost=20, elapsed=777ms, remaining=4223ms
```

[r1-c015-it-baseline:L535](evidence/r1-c015-it-baseline/client.log#L535)
```text
[LOG]:[3A][final] completed_goals=[2:puton,3:goto], satisfied_constraints=[]
```

### current

[r1-c015-it-current:L269](evidence/r1-c015-it-current/client.log#L269)
```text
[LOG]:[Scheduler] greedy task=3 marginal=35 remaining_ms=4903 group_attempt=true
```

[r1-c015-it-current:L324](evidence/r1-c015-it-current/client.log#L324)
```text
[LOG]:[Scheduler] filtered task=2 stable_id=3 marginal=-13 reason=nonpositive_single
```

[r1-c015-it-current:L346](evidence/r1-c015-it-current/client.log#L346)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"blocked_task","world_revision":3,"total_probes":0,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"task=2,stable_id=3,filter=nonpositive_single","closed_reason":""}
```

[r1-c015-it-current:L350](evidence/r1-c015-it-current/client.log#L350)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"blocking_fact","world_revision":3,"total_probes":0,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"task=2,stable_id=3,filter=nonpositive_single,fact=INSIDE:29,reason=unverified","closed_reason":""}
```

[r1-c015-it-current:L352](evidence/r1-c015-it-current/client.log#L352)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"blocking_fact","world_revision":3,"total_probes":0,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"task=2,stable_id=3,filter=nonpositive_single,fact=LOCATION:31,reason=unverified","closed_reason":""}
```

[r1-c015-it-current:L354](evidence/r1-c015-it-current/client.log#L354)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"candidate","world_revision":3,"total_probes":0,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"constraint_safety_unknown","closed_reason":"","signature":"sense_at:45","kind":"MoveSense","target_location":45,"eligible":false,"cost":5,"duration_ms":220,"fact_count":2,"potential_goal_value":40,"stable_id":3,"constraint_result":"constraint_safety_unknown","facts":[{"field":"LOCATION","id":29,"task":2,"stable_task_id":3,"reason":"unverified","location_hints":[{"location":45,"source":"object_location:claim_source=1"}]},{"field":"INSIDE","id":29,"task":2,"stable_task_id":3,"reason":"unverified","location_hints":[{"location":45,"source":"object_location:claim_source=1"}]}]}
```

[r1-c015-it-current:L356](evidence/r1-c015-it-current/client.log#L356)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"candidate","world_revision":3,"total_probes":0,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"extra_physical_actions","closed_reason":"","signature":"sense_at:2","kind":"MoveSense","target_location":2,"eligible":false,"cost":5,"duration_ms":220,"fact_count":1,"potential_goal_value":80,"stable_id":1,"constraint_result":"constraint_safe","facts":[{"field":"LOCATION","id":2,"task":0,"stable_task_id":1,"reason":"unverified","location_hints":[{"location":2,"source":"object_location:claim_source=1"}]},{"field":"LOCATION","id":2,"task":1,"stable_task_id":2,"reason":"unverified","location_hints":[{"location":2,"source":"object_location:claim_source=1"}]}]}
```

## retry-bound

主分类 4 pair，目标净损失 4，基础分损失 112；目标级独有ID 4，40分目标损失 160。

第一动作旧版 Move14、新版 Move10。新版先执行 GOTO couch10，探索离开后反复重做；GOTO task4 三次均 success=true、attempts=1/2/3。随后 pickup16 与最后到地点1的 Probe 使 GOTO 不满足；任务尝试上限使其不再进入候选，最终比旧版少官方 goal5。旧版最后 Move10+Sense 保留 GOTO。

无约束；旧版独有 goal5 是末尾有意 Move10 达成，实际成功且可定位。旧版 AskLoc19 得到 inside(19,5) 与 XML 的 inside(19,12) 不符，TakeOut19 5/PutDown19 都失败；这个错误分支没有产生旧版独有目标。白杯21缺位置线索影响双方未完成的 give，而不是本次净损失。

[完整代表pair](pair-evidence/c011-it-r1.md)

### baseline

[r1-c011-it-baseline:L435](evidence/r1-c011-it-baseline/client.log#L435)
```text
[LOG]:[TradeoffDecision] phase=terminal-recovery task=4 decision=execute reason=legacy_priority lower=67 upper=147
```

[r1-c011-it-baseline:L467](evidence/r1-c011-it-baseline/client.log#L467)
```text
[LOG]:[3A][final] goals=3/5 (unknown=2), constraints=0/0 (unknown=0), base_score=67, action_cost=53, elapsed=2057ms, remaining=2943ms
```

[r1-c011-it-baseline:L469](evidence/r1-c011-it-baseline/client.log#L469)
```text
[LOG]:[3A][final] completed_goals=[2:takeout,3:pickup,4:goto], satisfied_constraints=[]
```

### current

[r1-c011-it-current:L163](evidence/r1-c011-it-current/client.log#L163)
```text
[LOG]:[Scheduler] result task=4 stable_id=4 success=true revision=2 attempts=1
```

[r1-c011-it-current:L374](evidence/r1-c011-it-current/client.log#L374)
```text
[LOG]:[Scheduler] result task=4 stable_id=4 success=true revision=7 attempts=2
```

[r1-c011-it-current:L508](evidence/r1-c011-it-current/client.log#L508)
```text
[LOG]:[Scheduler] result task=4 stable_id=4 success=true revision=11 attempts=3
```

[r1-c011-it-current:L663](evidence/r1-c011-it-current/client.log#L663)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"blocked_task","world_revision":15,"total_probes":3,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"task=4,stable_id=4,filter=task_retry_bound","closed_reason":""}
```

[r1-c011-it-current:L715](evidence/r1-c011-it-current/client.log#L715)
```text
[LOG]:[Probe] {"schema":"probe.v1","event":"blocked_task","world_revision":17,"total_probes":4,"consecutive_no_progress":0,"policy":[8,2,2],"reason":"task=4,stable_id=4,filter=task_retry_bound","closed_reason":""}
```

[r1-c011-it-current:L729](evidence/r1-c011-it-current/client.log#L729)
```text
[LOG]:[3A][final] goals=2/5 (unknown=1), constraints=0/0 (unknown=0), base_score=39, action_cost=41, elapsed=1628ms, remaining=3372ms
```

[r1-c011-it-current:L731](evidence/r1-c011-it-current/client.log#L731)
```text
[LOG]:[3A][final] completed_goals=[2:takeout,3:pickup], satisfied_constraints=[]
```

## deadline

主分类 0 pair，目标净损失 0，基础分损失 0；目标级独有ID 0，40分目标损失 0。

本筛选集合没有该类主因，不能提供正例代表。

[c003](pair-evidence/c003-it-r1.md)新版停止时仍有余时且约束gate/Probe明确拒绝；每pair末轮remaining在完整日志中。

## terminal/score-disagreement

主分类 0 pair，目标净损失 0，基础分损失 0；目标级独有ID 0，40分目标损失 0。

本筛选集合没有该类主因，不能提供正例代表。

[c015](pair-evidence/c015-it-r1.md)内部C=0/20、unknown=19，但官方C=20/20。pairs.csv的canonical_old/new字段保留内部指标，正式损失按vanswer重算。

## other

主分类 0 pair，目标净损失 0，基础分损失 0；目标级独有ID 0，40分目标损失 0。

本筛选集合没有该类主因，不能提供正例代表。

