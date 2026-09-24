# liuyifan1.0 原型题设计

首批共6道。依据2025规则编写；每题包含完整env、instr和nl，Stage 1四题、Stage 2两题。

## 合规与计分边界

对象ID连续，robot=0、唯一human=1；所有小物体有颜色且以sort+color唯一绑定；所有大物体种类唯一且真实位置不重合；指令无重复、无两个小物体同句；goto小物体初始均在外部。所有约束在真实初态成立。第二阶段错误仅作用于允许的at/inside和容器开关字段。

04的NT仅在物体名、颜色词中加入#和混合大小写；其空格、句号和动作词保持合法。extra的microwave关闭信息有独立info句补充。

每个参考方案的基础分均≥200；按40×目标数+20×约束数+100计算的保守总分上界均≤1000。参考动作已经官方运行验证，所以理论可达分数落在规则要求区间内。参考方案不宣称动作最优。

IT/NT实际解析、对象绑定与纠错后快照通过等价比较；只规范化in/inside别名和give的literal-human/显式human绑定表示。

## 原型明细

### 01 自由终态汇聚

- 文件：[01.xml](01.xml)，Stage 1，7目标、0约束。
- 测试意图：六个不同小物体 goto 与 table goto；搬到 table 后停留，同时完成七个终态目标。
- 参考策略：保留桌边红书、蓝杯，将白瓶、绿罐、黄遥控器、黑书搬到桌边，最终停在位置2。
- 参考基础分232；保守总分上界380。

|对象ID|物体|真实初始状态|
|---:|---|---|
|0|robot|位置2，手爪和盘子均为空|
|1| human|位置1|
|2| table|位置2|
|3| chair|位置3|
|4| sofa|位置4|
|5|red book|位置2|
|6|blue cup|位置2|
|7|white bottle|位置3|
|8|green can|位置3|
|9|yellow remotecontrol|位置4|
|10|black book|位置4|

|类别|IT|NT|
|---|---|---|
|task|`(:task (goto X) (:cond (sort X book) (color X red)))`|Go to the red book.|
|task|`(:task (goto X) (:cond (sort X cup) (color X blue)))`|Go to the blue cup.|
|task|`(:task (goto X) (:cond (sort X bottle) (color X white)))`|Go to the white bottle.|
|task|`(:task (goto X) (:cond (sort X can) (color X green)))`|Go to the green can.|
|task|`(:task (goto X) (:cond (sort X remotecontrol) (color X yellow)))`|Go to the yellow remotecontrol.|
|task|`(:task (goto X) (:cond (sort X book) (color X black)))`|Go to the black book.|
|task|`(:task (goto X) (:cond (sort X table)))`|Go to the table.|

参考动作：[reference-plans/01.txt](reference-plans/01.txt)。

### 02 搬运与到达共享终态

- 文件：[02.xml](02.xml)，Stage 1，9目标、0约束。
- 测试意图：四个 puton、四个小物体 goto、一个 table goto；同一布局满足九个不同目标。
- 参考策略：四件物体全部放到桌边，最终停在桌边；后续 goto 不应再移动已完成的物体。
- 参考基础分312；保守总分上界460。

|对象ID|物体|真实初始状态|
|---:|---|---|
|0|robot|位置2，手爪和盘子均为空|
|1| human|位置1|
|2| table|位置2|
|3| chair|位置3|
|4| sofa|位置4|
|5|red book|位置3|
|6|blue cup|位置3|
|7|white bottle|位置4|
|8|green can|位置4|

|类别|IT|NT|
|---|---|---|
|task|`(:task (goto X) (:cond (sort X book) (color X red)))`|Go to the red book.|
|task|`(:task (puton X Y) (:cond (sort X book) (color X red) (sort Y table)))`|Put the red book on the table.|
|task|`(:task (goto X) (:cond (sort X cup) (color X blue)))`|Go to the blue cup.|
|task|`(:task (puton X Y) (:cond (sort X cup) (color X blue) (sort Y table)))`|Put the blue cup on the table.|
|task|`(:task (goto X) (:cond (sort X bottle) (color X white)))`|Go to the white bottle.|
|task|`(:task (puton X Y) (:cond (sort X bottle) (color X white) (sort Y table)))`|Put the white bottle on the table.|
|task|`(:task (goto X) (:cond (sort X can) (color X green)))`|Go to the green can.|
|task|`(:task (puton X Y) (:cond (sort X can) (color X green) (sort Y table)))`|Put the green can on the table.|
|task|`(:task (goto X) (:cond (sort X table)))`|Go to the table.|

参考动作：[reference-plans/02.txt](reference-plans/02.txt)。

### 03 must-near 纠错与缺失补全

- 文件：[03.xml](03.xml)，Stage 2，7目标、2约束。
- 测试意图：红书位置错误、蓝杯位置缺失；两个真实成立的 must-near 以 table 为可靠锚点。
- 参考策略：约束推断红书和蓝杯均在桌边并保留原位，只搬白瓶、绿罐到桌边。
- 参考基础分296；保守总分上界420。

|对象ID|物体|真实初始状态|
|---:|---|---|
|0|robot|位置2，手爪和盘子均为空|
|1| human|位置1|
|2| table|位置2|
|3| chair|位置3|
|4| sofa|位置4|
|5|red book|位置2|
|6|blue cup|位置2|
|7|white bottle|位置3|
|8|green can|位置3|

|类别|IT|NT|
|---|---|---|
|must|`(:cons_notnot (:info (near X Y) (:cond (sort X book) (color X red) (sort Y table))))`|The red book must be near the table.|
|must|`(:cons_notnot (:info (near X Y) (:cond (sort X cup) (color X blue) (sort Y table))))`|The blue cup must be near the table.|
|task|`(:task (goto X) (:cond (sort X book) (color X red)))`|Go to the red book.|
|task|`(:task (goto X) (:cond (sort X cup) (color X blue)))`|Go to the blue cup.|
|task|`(:task (puton X Y) (:cond (sort X bottle) (color X white) (sort Y table)))`|Put the white bottle on the table.|
|task|`(:task (goto X) (:cond (sort X bottle) (color X white)))`|Go to the white bottle.|
|task|`(:task (puton X Y) (:cond (sort X can) (color X green) (sort Y table)))`|Put the green can on the table.|
|task|`(:task (goto X) (:cond (sort X can) (color X green)))`|Go to the green can.|
|task|`(:task (goto X) (:cond (sort X table)))`|Go to the table.|

参考动作：[reference-plans/03.txt](reference-plans/03.txt)。

### 04 容器状态纠错与合法语言扰动

- 文件：[04.xml](04.xml)，Stage 2，6目标、2约束。
- 测试意图：错误红书位置、错误 cupboard 开关状态；extra 用 info 补充 microwave 关闭状态；NT只扰动物体名和颜色词。
- 参考策略：用 must-inside、must-closed 修正 cupboard 信息，保持红书和柜门不动；将蓝杯、白瓶、绿罐放入 microwave 并关门。
- 参考基础分236；保守总分上界380。

|对象ID|物体|真实初始状态|
|---:|---|---|
|0|robot|位置2，手爪和盘子均为空|
|1| human|位置1|
|2| table|位置2|
|3| cupboard|位置3，关闭|
|4| microwave|位置4，关闭|
|5|red book|inside 3|
|6|blue cup|位置2|
|7|white bottle|位置2|
|8|green can|位置2|

|类别|IT|NT|
|---|---|---|
|info|`(:info (closed X) (:cond (sort X microwave)))`|The M#icrowave is closed.|
|must|`(:cons_notnot (:info (inside X Y) (:cond (sort X book) (color X red) (sort Y cupboard) (type Y container))))`|The R#ed B#ook must be in the C#upboard.|
|must|`(:cons_notnot (:info (closed X) (:cond (sort X cupboard))))`|The C#upboard must be closed.|
|task|`(:task (putin X Y) (:cond (sort X cup) (color X blue) (sort Y microwave) (type Y container)))`|Put the B#lue C#up in the M#icrowave.|
|task|`(:task (putin X Y) (:cond (sort X bottle) (color X white) (sort Y microwave) (type Y container)))`|Put the W#hite B#ottle in the M#icrowave.|
|task|`(:task (putin X Y) (:cond (sort X can) (color X green) (sort Y microwave) (type Y container)))`|Put the G#reen C#an in the M#icrowave.|
|task|`(:task (close X) (:cond (sort X microwave) (type X container)))`|Close the M#icrowave.|
|task|`(:task (goto X) (:cond (sort X microwave)))`|Go to the M#icrowave.|
|task|`(:task (close X) (:cond (sort X cupboard) (type X container)))`|Close the C#upboard.|

参考动作：[reference-plans/04.txt](reference-plans/04.txt)。

### 05 牺牲一个约束解锁四个目标

- 文件：[05.xml](05.xml)，Stage 1，6目标、1约束。
- 测试意图：must-closed 与四个 putin 冲突；柜门重新关闭仍不能挽回全过程约束分。
- 参考策略：打开 cupboard，依次放入四件物体，再关门；牺牲20约束分，新增160目标分，参考动作成本20。
- 参考基础分220；保守总分上界360。

|对象ID|物体|真实初始状态|
|---:|---|---|
|0|robot|位置2，手爪和盘子均为空|
|1| human|位置1|
|2| cupboard|位置2，关闭|
|3| table|位置3|
|4|red book|位置2|
|5|blue cup|位置2|
|6|white bottle|位置2|
|7|green can|位置2|

|类别|IT|NT|
|---|---|---|
|must|`(:cons_notnot (:info (closed X) (:cond (sort X cupboard))))`|The cupboard must be closed.|
|task|`(:task (putin X Y) (:cond (sort X book) (color X red) (sort Y cupboard) (type Y container)))`|Put the red book in the cupboard.|
|task|`(:task (putin X Y) (:cond (sort X cup) (color X blue) (sort Y cupboard) (type Y container)))`|Put the blue cup in the cupboard.|
|task|`(:task (putin X Y) (:cond (sort X bottle) (color X white) (sort Y cupboard) (type Y container)))`|Put the white bottle in the cupboard.|
|task|`(:task (putin X Y) (:cond (sort X can) (color X green) (sort Y cupboard) (type Y container)))`|Put the green can in the cupboard.|
|task|`(:task (close X) (:cond (sort X cupboard) (type X container)))`|Close the cupboard.|
|task|`(:task (goto X) (:cond (sort X cupboard)))`|Go to the cupboard.|

参考动作：[reference-plans/05.txt](reference-plans/05.txt)。

### 06 放弃低收益目标保住三个约束

- 文件：[06.xml](06.xml)，Stage 1，6目标、3约束。
- 测试意图：交付红杯将破坏 must-closed、must-inside、must-not-near human 三个不同约束；完成另外五个兼容目标更有利。
- 参考策略：不取红杯、不打开 cupboard；只搬蓝书、白瓶到桌边，完成五个目标并维护三个约束。
- 参考基础分240；保守总分上界400。

|对象ID|物体|真实初始状态|
|---:|---|---|
|0|robot|位置4，手爪和盘子均为空|
|1| human|位置1|
|2| table|位置2|
|3| cupboard|位置3，关闭|
|4| chair|位置4|
|5|red cup|inside 3|
|6|blue book|位置4|
|7|white bottle|位置4|

|类别|IT|NT|
|---|---|---|
|must|`(:cons_notnot (:info (closed X) (:cond (sort X cupboard))))`|The cupboard must be closed.|
|must|`(:cons_notnot (:info (inside X Y) (:cond (sort X cup) (color X red) (sort Y cupboard) (type Y container))))`|The red cup must be in the cupboard.|
|must_not|`(:cons_not (:info (near X Y) (:cond (sort X cup) (color X red) (sort Y human))))`|The red cup must not be near the human.|
|task|`(:task (give human X) (:cond (sort X cup) (color X red)))`|Give the red cup to me.|
|task|`(:task (puton X Y) (:cond (sort X book) (color X blue) (sort Y table)))`|Put the blue book on the table.|
|task|`(:task (goto X) (:cond (sort X book) (color X blue)))`|Go to the blue book.|
|task|`(:task (puton X Y) (:cond (sort X bottle) (color X white) (sort Y table)))`|Put the white bottle on the table.|
|task|`(:task (goto X) (:cond (sort X bottle) (color X white)))`|Go to the white bottle.|
|task|`(:task (goto X) (:cond (sort X table)))`|Go to the table.|

参考动作：[reference-plans/06.txt](reference-plans/06.txt)。

## 设计验收修订

初稿06使用“红杯在cupboard内部且必须near cupboard”。官方平台并不自动把inside投影为near，参考运行只计两个约束。最终06已将第三约束改为“红杯必须不near human”，重新通过静态检查和官方参考运行。初稿证据单独保留在test-results/liuyifan1.0-20260924；正式统计只采用带-final的目录。

规则来源：[2025赛事规则](../../docs/rules/rules-2025.pdf)、[2025出题指南](../../docs/rules/question-guide-2025.pdf)。
