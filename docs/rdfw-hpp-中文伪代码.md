# `rdfw.hpp` 中文伪代码

> 对应源码：`src/iron/rdfw.hpp`
>
> 本文不是可编译代码，而是按原头文件的结构改写成中文伪代码。成员名和方法名保留，方便回到 C++ 源码搜索。头文件中只有声明的方法，本文只解释其接口意图；具体算法仍以 `src/iron/rdfw.cpp` 为准。

## 1. 整体结构

```text
官方接口 Plug
      │
      ├──────────────┐
      │              │
基础对象 Object      │
      │              │
      ├─ SmallObject │
      │              │
      ├─ BigObject   │
      │    └─ Container
      │
      └─ Robot ──────┴─ RDFW
                         ├─ 保存环境、任务、约束和感知结果
                         ├─ 解析题目
                         ├─ 规划、排序并执行任务
                         └─ 调用官方原子动作

SyntaxNode  表示解析树节点
Condition   表示物体筛选条件
Instruction 表示任务、信息或约束
```

`RDFW` 同时继承：

- `Plug`：获得官方平台 API；
- `Robot`：让工作区本身也保存机器人的位置、手持物和托盘状态；
- `enable_shared_from_this<RDFW>`：允许从当前对象安全取得 `shared_ptr<RDFW>`。

## 2. 全局约定和前置声明

```text
常量 UNKNOWN = -1       // 状态未知，例如未知位置、未知容器
常量 NONE    = 0        // 明确表示“没有”，例如手中没有物体

提前声明 parser

命名空间 _home:
    提前声明 Instruction
    提前声明 Object、SmallObject、BigObject、Container、Robot
    提前声明 SyntaxNode、Condition
    提前声明 RDFW
```

## 3. 对象模型

### 3.1 `Object`：所有场景对象的基类

```text
类 Object:
    公有数据:
        location: 整数 = UNKNOWN    // 所在位置
        id: 整数                     // 对象 ID
        is_keep: 整数 = 0            // 维护该对象相关强约束的优先程度
        unable_site: 整数 = -1       // 暂不明确；记录一个不可用位置
        sort: 字符串 = ""            // 对象类别

    构造 Object(对象ID, 类别="", 位置=UNKNOWN):
        sort     ← 类别
        location ← 位置
        id       ← 对象ID

    默认构造 Object():
        具体实现见 rdfw.cpp

    虚方法 ToString():
        返回 "id、location、sort" 的文本

    析构 Object()
```

### 3.2 `SmallObject`：可拿取的小物体

```text
类 SmallObject 继承 Object:
    公有数据:
        color: 字符串 = ""           // 颜色
        inside: 整数 = UNKNOWN       // 所在容器的对象 ID
        on: 整数 = UNKNOWN           // 所在大物体的对象 ID

    构造 SmallObject(对象ID, 位置=UNKNOWN, 类别="", 颜色=""):
        调用 Object(...)
        color ← 颜色

    构造 SmallObject(普通对象指针):
        复制普通对象的基类部分

    覆盖 ToString():
        返回 基类信息 + color + inside + on
```

### 3.3 `BigObject`：大物体

```text
类 BigObject 继承 Object:
    构造 BigObject(对象ID, 位置=UNKNOWN, 类别=""):
        调用 Object(...)

    构造 BigObject(普通对象指针):
        复制普通对象的基类部分
```

### 3.4 `Container`：能够容纳小物体的大物体

```text
类 Container 继承 BigObject:
    公有数据:
        smallObjectsInside: 小物体指针列表
        isOpen: 整数 = 0             // 0=关闭，1=打开，UNKNOWN=未知

    构造 Container(对象ID, 位置=UNKNOWN, 是否打开=true, 类别=""):
        初始化 BigObject
        isOpen ← 是否打开

    构造 Container(普通对象指针):
        从该对象初始化 BigObject
        isOpen ← UNKNOWN

    构造 Container(大物体指针):
        复制该大物体
        isOpen ← UNKNOWN

    方法 DeleteObjectInside(目标小物体):
        遍历 smallObjectsInside:
            如果当前小物体.id == 目标.id:
                从列表删除当前元素

    覆盖 ToString():
        输出自身的大物体信息
        逐个输出内部小物体的信息
```

### 3.5 `Robot`：机器人自身状态

```text
类 Robot 继承 Object:
    公有数据:
        hold: 小物体指针             // 机械手中的物体
        plate: 小物体指针            // 托盘上的物体
        hold_id: 整数 = NONE
        plate_id: 整数 = UNKNOWN

    构造 Robot(对象ID, 位置=UNKNOWN):
        调用 Object(对象ID, "robot", 位置)

    默认构造 Robot():
        调用 Robot(0)

    方法 SetHold(新物体):
        hold ← 新物体
        如果新物体存在:
            新物体.location ← 机器人.location
            hold_id ← 新物体.id
            新物体.inside ← NONE
        否则:
            hold_id ← NONE

    方法 SetPlate(新物体):
        plate ← 新物体
        如果新物体存在:
            新物体.location ← 机器人.location
            plate_id ← 新物体.id
            新物体.inside ← NONE
        否则:
            plate_id ← NONE

    覆盖 ToString():
        返回机器人基本信息
             + 手中物体信息（若存在）
             + 托盘物体信息（若存在）
```

### 3.6 安全的对象指针转换

```text
模板函数 ObjectPtrCast<目标类型>(Object指针):
    p ← 尝试执行运行时动态类型转换
    如果 p 为空:
        记录对象 ID 和类别
        输出调用栈
        抛出 "Abort"
    返回 p
```

## 4. 解析和条件结构

### 4.1 `SyntaxNode`：语法树节点

```text
结构 SyntaxNode:
    value: 字符串
    sons: 子 SyntaxNode 指针列表
```

### 4.2 `Condition`：对象筛选条件

```text
结构 Condition:
    sort: 字符串 = ""               // 要求的类别
    color: 字符串 = ""              // 要求的颜色

    方法 ToString():
        返回 "(Sort:类别,Color:颜色)"

    方法 IsObjectSatisfy(目标对象) -> 布尔值:
        判断对象是否符合类别和颜色条件
        具体实现见 rdfw.cpp
```

## 5. `Instruction`：统一表示任务、信息和约束

```text
类 Instruction:
    公有数据:
        behave: 字符串               // 动作/关系，例如 goto、putin、inside
        conditionX: Condition        // X 的筛选条件
        conditionY: Condition        // Y 的筛选条件

        X: 对象指针列表              // 条件 X 匹配到的对象
        Y: 对象指针列表              // 条件 Y 匹配到的对象

        risk: 整数 = 0               // 风险值
        repeat_times: 整数 = 1       // 同类指令重复次数
        is_cheat: 整数 = 0           // 欺骗/纠错相关标记
        ask_times: 整数 = 0          // 已询问次数
        isUseY: 布尔值 = false       // 指令是否需要 Y
        isEnable: 布尔值 = true      // 指令当前是否仍启用
        isfalse: 布尔值 = false      // 指令是否已失败
        isMultiPuton: 布尔值 = false // 是否属于同一大物体上的多个 puton 任务
        hasMissingObjects: 布尔值 = false
                                      // 是否引用了环境中不存在的对象
        conflictnum: 整数 = 0        // 冲突任务类别编号

    默认构造 Instruction()

    构造 Instruction(语法树节点, RDFW工作区):
        根据解析树和当前环境构造指令
        具体实现见 rdfw.cpp

    方法 SearchConditionObject(RDFW工作区, 是否匹配全部=false):
        在工作区对象中搜索满足 conditionX/conditionY 的对象
        将结果写入 X/Y

    方法 IsInstructionInvoke(动作名, 对象x, 对象y=null) -> 布尔值:
        判断一次状态变化/动作是否会触发或满足本指令

    方法 ToString():
        返回 behave、conditionX、conditionY 的文本
```

## 6. `RDFW`：整个规划工作区

### 6.1 初始化和官方入口

```text
类 RDFW 继承 Plug、Robot、enable_shared_from_this<RDFW>:

    构造 RDFW()

    方法 Init(argc, argv):
        解析启动选项
        初始化对象、解析器、动态数组和感知记录

    方法 InitializeDynamicArrays(最大大小=100):
        初始化约束矩阵和任务查找表

    覆盖方法 Plan():
        执行一次题目的完整规划流程
```

`Plan()` 在当前 `rdfw.cpp` 中的高层流程可以概括为：

```text
过程 Plan:
    重置上一题遗留的运行状态
    读取并解析环境描述
    读取任务描述

    如果任务描述以 "(" 开头:
        按形式化指令解析
    否则:
        按自然语言解析

    应用补充信息 infos

    如果 stage == 2:
        修正 open/close 约束
        修正 must-in 约束
        修正 must-near 约束

    从 objects 中找到 human
    生成各类约束查找表
    过滤与任务冲突的约束
    优化任务顺序
    延迟需要聚合的多个 goto
    执行主任务循环

    如果尚未完成任务且剩余 goto 少于 2:
        执行 MustChooseOne

    执行检查阶段
    聚合执行多个 goto
    输出完成任务数
```

### 6.2 环境对象

```text
human: BigObject 指针
    // 场景中的人

objects: Object 指针列表
    // 场景中全部对象；通常使用对象 ID 作为下标

smallObjects: SmallObject 指针列表
    // 场景中全部小物体
```

### 6.3 指令分类

```text
tasks: Instruction 列表
    // 需要完成的任务

infos: Instruction 列表
    // 补充环境信息

not_infoConstrains: Instruction 列表
    // 禁止某种状态成立的信息约束

not_taskConstrains: Instruction 列表
    // 禁止执行某种任务/动作的约束

notnot_infoConstrains: Instruction 列表
    // 必须保持成立的信息约束
```

### 6.4 执行模式和状态

```text
stage = 2                       // 比赛阶段：1 或 2
task_index = 0                  // 当前任务下标
err_times = 0                   // 当前错误次数
task_limit = 4                  // 自动约束模式使用的已完成任务阈值

isKeepConstrain = false         // 是否进入维护约束状态
isAutoConstrain = false         // 是否依据完成数自动切换约束维护
isAskTwice = false              // 纠错时是否询问到两次结果一致
isErrorCorrection = false       // 是否启用纠错
isNaturalParse = false          // 是否解析自然语言
isPass = false                  // 是否放弃/跳过当前任务
```

### 6.5 约束查找表

这些数组以对象 ID、位置 ID 或两个 ID 的组合为索引，值通常表示对应限制的计数或是否存在。

```text
goto_cons[位置]
    // 禁止 goto 某位置

putin_cons[小物体][容器]
    // 禁止形成 inside，或禁止执行 putin

takeout_cons[小物体][容器]
    // 必须保持 inside，或禁止执行 takeout

putdown_cons[小物体][位置]
    // 禁止形成 on，或禁止相关 puton/putdown

putdown1_cons[对象]
    // putdown、手持、托盘相关限制

move_cons[对象][位置]
    // near 等关系引出的移动限制

open_cons[容器]
    // opened/closed 信息和 open 任务限制

close_cons[容器]
    // closed/opened 信息和 close 任务限制

pickup_cons[小物体]
    // 托盘状态或 pickup 任务限制

givehuman_cons[对象]
    // give 任务限制

fromplate_cons[小物体]
    // 从托盘取下的限制

toplate_cons[小物体]
    // 放上托盘的限制

mustnear_cons[对象A][对象B]
    // 必须保持 near 的对象关系

rightlocation[位置]
    // 位置是否已确认正确
```

### 6.6 must-near 纠错状态

```text
lock_by_mustnear: 布尔列表
    // must-near 成组以后，标记哪些对象的位置被锁定

uf_parent[256]: 整数数组
uf_size[256]: 整数数组
uf_groupLoc[256]: 整数数组
    // 用并查集维护 must-near 等价组及其位置；UNKNOWN 表示组位置未知

sense_cb(对象ID, 位置) -> 布尔值
    // 可由外部绑定的感知回调

enable_near_correction = true
    // 是否启用 near 纠错总开关

enable_must_lock = true
    // 是否锁定 must-near 组中所有成员的位置

hold_mustnear = false
plate_mustnear = false
    // 手持物/托盘物是否受到 must-near 关系影响
```

### 6.7 任务快速查找表

```text
takeout[小物体][容器] -> Instruction 指针
putin[小物体][容器]   -> Instruction 指针
close[容器]           -> Instruction 指针
open[容器]            -> Instruction 指针
pickup[小物体]        -> Instruction 指针
putdown[小物体]       -> Instruction 指针
```

这些表不拥有任务本身，只指向 `tasks` 中的相关任务，目的是快速判断一个动作与哪些任务有关。

### 6.8 解析器和感知记录

```text
nlp_parser: parser 指针
errorlist: 字符串列表
posCorrectFlag: 布尔列表
    // 各位置/对象的位置正确性标记

posSensedFlag: 布尔列表
    // 各位置是否已感知，防止重复 Sense

isMultiGotoMode: 布尔值
    // 是否处于多 goto 模式，用于决定是否跳过某些 Sense

结构 LocationSensedInfo:
    object_ids: 无符号整数列表
        // 在该位置感知到的小物体 ID
    container_id: 无符号整数
        // 在该位置感知到的容器 ID
    has_container: 布尔值
        // 该位置是否有容器

locationSensedObjects: LocationSensedInfo 列表
    // 每个位置一条感知记录
```

感知记录的只读访问接口：

```text
GetLocationSensedInfo(位置) -> 该位置的完整感知记录
HasObjectAtLocation(位置, 对象ID) -> 是否感知到指定对象
HasContainerAtLocation(位置) -> 是否感知到容器
GetObjectsAtLocation(位置) -> 该位置的小物体 ID 列表
GetContainerAtLocation(位置) -> 该位置的容器 ID
CountObjectsAtLocation(位置) -> 该位置的对象数量
```

## 7. `RDFW` 方法按职责分组

以下方法在头文件中只有接口声明。

### 7.1 解析

```text
ParseEnv(环境描述) -> 是否成功
    // 解析完整环境

ParseEnvSentence(单句) -> 是否成功
    // 解析一条环境陈述

ParseInstruction(任务描述) -> 是否成功
    // 解析形式化指令

ParseNaturalLanguage(原文)
    // 解析完整自然语言任务

ParseNaturalLanguageSentence(单句) -> 是否成功
    // 解析一条自然语言任务

ParseInfo(补充信息指令)
    // 把 info 写入环境状态

ExtractValue(任务描述, 起始标签, 结束标签) -> 字符串
    // 从指定标签范围提取值

ExtractInstructions(语法树节点列表)
    // 从语法树生成并分类 Instruction
```

### 7.2 收尾、内存和调试输出

```text
Fini()
    // 一次运行结束后的收尾

OptimizeMemoryUsage()
    // 优化容器容量或释放暂时不用的内存

LogInstructionError(任务)
    // 记录指令错误

PrintInstruction()
    // 输出全部指令

PrintEnv()
    // 输出当前环境模型

InferUnknownLocations()
    // 根据已知关系推断未知位置
```

### 7.3 约束规划和任务优化

```text
Cons_plan()
    // 把约束指令转换为各类约束查找表

FilterConstraintsByTaskConflicts()
    // 移除或停用与任务定义冲突的约束

UpdateTaskList(动作, 对象x, 对象y=null)
    // 动作改变环境后，更新受影响任务的状态

TaskOptimization() -> 优化后的 Instruction 列表
    // 计算风险、依赖或顺序，返回新的任务序列
```

### 7.4 任务分派和求解

```text
SolveTask(任务) -> 是否成功
    // 按 behave 把任务分派到具体求解器

DoBehavious(动作, x) -> 是否成功
DoBehavious(动作, x, y) -> 是否成功
    // 执行一元或二元行为

HoldSmallObject(小物体ID) -> 是否成功
    // 确保目标小物体进入机械手

SolveTask_PickUp(a)       -> 是否成功
SolveTask_PutDown(a)      -> 是否成功
SolveTask_Goto(a)         -> 是否成功
SolveTask_Open(a)         -> 是否成功
SolveTask_Close(a)        -> 是否成功
SolveTask_Give(a)         -> 是否成功
SolveTask_Putin(a, b)     -> 是否成功
SolveTask_TakeOut(a, b)   -> 是否成功
SolveTask_PutOn(a, b)     -> 是否成功
    // 各类任务的高层求解器

CalculateTaskRisk(任务) -> 整数
    // 估计整个任务风险

CalculateStepRisk(任务) -> 整数
    // 估计下一步动作风险

TakeOutLogic(小物体ID, 容器ID) -> 整数
    // 处理 takeout 的状态和逻辑分支
```

### 7.5 任务选择和循环

```text
MustChooseOne()
    // 在互斥/多选任务中强制选择一个

CheckAndDeferMultiGoto() -> 是否存在被延迟的多 goto
    // 检测多个 goto，并把它们留到聚合阶段

ExecuteMultiGotoAggregation()
    // 聚合执行延迟的 goto

AfterSolveTask(任务)
    // 成功执行任务后的统一状态更新

ExecuteMainTaskLoop(是否延迟多goto)
    // 首轮遍历并执行任务

ExecuteCheckPhase(是否延迟多goto)
    // 再检查一轮尚未完成的任务
```

### 7.6 询问、感知和状态检查

```text
AskLoc(对象ID) -> 字符串
    // 通过官方接口询问对象位置/状态

Sense()
    // 执行官方感知

SenseAndUpdateEnvironment()
    // 感知并把结果同步到内部环境模型

SenseCurrentLocationOnly()
    // 只感知机器人当前位置

Isinside(a, b) -> 布尔值
    // 判断对象 a 是否在容器 b 内

IsKeepingGoing(任务下标) -> 布尔值
    // 判断是否继续执行指定任务

sense(对象ID) -> 布尔值
    // 针对指定对象执行/验证感知

findrightlocation(对象ID) -> 整数
    // 找到或确认对象的正确位置
```

### 7.7 约束纠错

```text
FindUF(x) -> 并查集根节点
UnionUF(a, b)
    // 合并 must-near 等价组

ApplyMustNearConstraintCorrection()
    // 根据 must-near 关系统一、修正并可选锁定组内位置

ApplyMustInConstraintCorrection()
    // 根据 must-in 关系修正 inside、容器成员表和位置

ApplyOpenCloseCorrection()
    // 修正 opened/closed 关系和容器开关状态
```

### 7.8 零动作预检查（仅 stage 2）

```text
IsZeroActionSatisfy(任务) -> 布尔值
    // 只检查当前环境是否已经满足任务，不执行动作

ZeroActionPreCheck(任务) -> 布尔值
    // 必要时先 Ask/Sense，再判断任务是否已经完成
    // 若已满足，可直接把任务计为完成，避免多余动作
```

## 8. 私有方法

### 8.1 状态获取和容量保护

```text
GetSmallObjectStatus(对象ID)
    // 询问并更新小物体状态

GetBigObjectStatus(对象ID)
    // 询问并更新大物体状态

EnsureLocationCapacity(位置)
    // 在访问前保证所有按位置索引的数组足够大

EnsureObjectExists(对象ID, 倾向创建小物体=false)
    // 在按 ID 访问前保证对象槽位存在
```

### 8.2 原子动作

这些方法是高层求解器最终调用的基础动作，并同步内部状态。

```text
Move(位置x)             -> 是否成功
PickUp(小物体a)         -> 是否成功
PutDown(小物体a)        -> 是否成功
ToPlate(小物体a)        -> 是否成功
FromPlate(小物体a)      -> 是否成功
Open(容器a)             -> 是否成功
Close(容器a)            -> 是否成功
PutIn(小物体a, 容器b)   -> 是否成功
TakeOut(小物体a, 容器b) -> 是否成功
```

### 8.3 内联运行状态方法

```text
方法 ErrTimesAdd():
    err_times ← err_times + 1
    如果 err_times > 2:
        isPass ← true

solved_task_num = 0

方法 SetSolvedTaskNum(数量):
    solved_task_num ← 数量

    如果 isAutoConstrain:
        如果 数量 > task_limit:
            isKeepConstrain ← true
        否则:
            isKeepConstrain ← false
```

## 9. 一次任务执行时的数据流

```text
题目文本
  │
  ├─ 环境描述 ──> ParseEnv ───────────────> objects / smallObjects / human
  │
  └─ 任务描述 ──> ParseInstruction 或 NLP ─> tasks / infos / 各类 constraints
                                                    │
                                                    v
                                          约束纠错与 Cons_plan
                                                    │
                                                    v
                                             TaskOptimization
                                                    │
                                                    v
                              ExecuteMainTaskLoop / ExecuteCheckPhase
                                                    │
                                                    v
                                          SolveTask_* 高层求解
                                                    │
                                                    v
                                      Move / PickUp / PutIn 等原子动作
                                                    │
                                                    v
                                 更新 Robot、Object、任务和感知记录
```

## 10. 阅读源码时应特别留意

1. `UNKNOWN` 和 `NONE` 含义不同：前者是“不知道”，后者是“确定没有”。
2. `objects` 多处默认“对象 ID 就是数组下标”，因此扩容和空槽检查很重要。
3. `SmallObject::inside` 保存的是容器对象 ID，不是位置 ID；`location` 才是位置。
4. `RDFW` 本身也是 `Robot` 和 `Object`，所以机器人状态直接存在工作区对象里。
5. `tasks`、`infos` 和三类 constraints 都使用 `Instruction`，区别主要来自存入哪个列表以及如何解释 `behave`。
6. 头文件中的 `SmallObject` 和 `BigObject` 构造函数调用基类时写成了 `Object(location, sort, id)`，但 `Object` 的参数顺序是 `(id, sort, location)`。本文没有擅自修正源码语义；这是值得单独核查的参数顺序问题。
7. 动态查找表默认按 100 初始化，而 must-near 并查集是固定长度 256；读取或修改对象容量逻辑时要同时检查这两套边界。
8. `DeleteObjectInside` 删除后仍继续递增下标；若列表里存在相邻重复项，可能跳过后一个重复项。
