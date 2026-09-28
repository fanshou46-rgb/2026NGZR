# Question Preflight 契约

## 入口与处置

`Plan → ParseEnv → ParseInstruction / ParseNaturalLanguage → RunQuestionPreflight`
先建立唯一 task/constraint 列表，再执行 `ParseInfo → Stage 2 corrections →
Cons_plan → FilterConstraintsByTaskConflicts → TaskOptimization → execution`。
前后所有 risk、multi-goto/multi-puton、Candidate、TerminalChecker、ScoreEvaluator
共享同一份列表，不各自实现不同的去重口径。

| 检查 | 处置 | 实现 |
|---|---|---|
| 重复 task、禁止动作、禁止状态、必须状态 | 同类别内按 key 稳定保留第一条，删除其余副本 | `question_preflight.cpp` |
| schema 不合法或绑定到无 sort/运行时类型的稀疏占位对象 | 仅移除当前指令，计入 rejected | `RunQuestionPreflight` |
| robot 不是对象 0，或初始位置不可用 | 整题在任何规划/平台动作前正常返回 | `RunQuestionPreflight` / `Plan` |
| 对象表 ID/指针注册不一致；实际对象缺少 sort 或 small/big 运行时类型；位置越界 | 同上 | 同上 |
| human 不唯一、不是 ID 1、不是非容器大物体 | 同上 | 同上 |
| Stage 1 多个大物体占同一已知位置 | 同上 | 同上 |
| Stage 2 未知位置、未知容器状态、描述中的位置碰撞 | 保留，交给现有询问/感知/纠错链 | 同上 |
| 括号损坏的 constraint | 隔离坏 wrapper，在后续已知 marker 恢复 | `ParseInstruction` |
| 括号平衡但结构非法的 constraint（含多个 child、错误 child kind、嵌套 wrapper） | 整个 wrapper 丢弃，子 task 不执行 | `ParseInstruction` / `ExtractInstructions` |

`preflightReport()` 返回本次调用的 raw / unique / duplicates / rejected 和 world errors。
raw 统计已进入解析向量的指令数；解析阶段已经拒绝的 form 仍由
`discardedInstructionCount()` 记录。重复副本单独计数，不伪装为 schema 错误。
预检重复调用对列表幂等；`Plan` 开始和 `Fini` 都重置报告，避免跨题污染。

## Duplicate 与 conflict 的边界

key 为 `kind:predicate:X[sorted unique IDs]:Y[sorted unique IDs]`。
键构造仅接受 schema 已验证的注册对象，不使用位置或源文本作身份。
`in` 归一为 `inside`，`nextto` 归一为 `near`；near 的两个完整集合按对称关系排序。
实际指令保留首条表达和执行元数据，未改写谓词或重写求解策略。

以下保持独立：

- `open(3)` 与 `close(3)`；`puton(2,4)` 与 `puton(2,1)`。
- task `open(3)`、禁止 task `open(3)`、禁止 info `opened(3)`、必须 info `opened(3)`。
- must opened 与 must closed；not closed 与 must opened 不做逻辑化简。
- `goto(2)` 与 `goto(5)`，即使对象 2 与 5 同位置。
- 一个 `every/all` 的集合目标与某个单对象目标；只去除完全相同的集合关系，
  不拆开集合计分、不合并部分重叠集合。

这些 conflict 在预检后完整交给既有策略。原来的约束筛选、风险阈值、动作重试
仍可能决定执行或放弃某项；这属于既有求解行为。

## malformed constraint 的恢复边界

合法 wrapper 只拥有一个直接 task/info child。损坏括号流中，扫描器消费该首个
payload，后续已知指令 marker 用作恢复点；坏 wrapper 与已消费的 payload 一起
丢弃。非法嵌套/未知 child 的内部 marker 不升格为顶层任务。

对整体括号平衡的输入采取保守隔离：结构非法的 constraint 整体拒绝。若缺失
右括号又由其他多余右括号抵消，纯文本不能唯一判断原边界，本版不会猜测其
内部 task 是独立目标。此类形式可能丢失被吞入 wrapper 的后续指令，但不执行
闭合非法 wrapper 的内部任务。XML、IT/NL 对齐及题源分区校验不在本版范围。

## 验证

本地独立构建使用 stub，不连接平台：

```sh
# 从仓库根目录执行；适配 Ubuntu 18.04 自带 CMake 3.10。
repo="$PWD"
build_dir=$(mktemp -d /tmp/rdfw-preflight.XXXXXX)
cd "$build_dir"
cmake "$repo/src1.3.3B/tests" -DCMAKE_BUILD_TYPE=Debug
make -j2
ctest --output-on-failure
```

`question_preflight_tests.cpp` 覆盖：duplicate task/puton、constraint 风险 2→1、
Terminal/Score 80→40 与 60 分断言、duplicate goto 不再触发 multi-goto、同位置
不同 ID、合法 conflict、谓词 alias/near 对称、集合顺序与集合/单对象区别、NL
共用入口、missing inner/outer bracket、非法/嵌套/多 child constraint、末尾坏 form、
Stage 2 unknown、Stage 1 碰撞、human/注册/类型错误、稀疏占位隔离、跨题清理。
通过 stub `SetTestInput` 直接调用 `Plan()`，确认真实入口的时序和 unsafe world 的
零平台调用；不是只测独立 key 函数。

保留并运行 A 的 `input_safety_tests` 和 `three_a_tests`。可给测试构建额外传入
`-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -DCMAKE_EXE_LINKER_FLAGS=-no-pie`
执行 ASan/UBSan。生产 SDK 构建使用目录根 `CMakeLists.txt`；自定义编译脚本需
把 `question_preflight.cpp` 加入源码列表。

## 明确留待后续

本版是小型入口 gate，不是完整题源合法性判定器。保留 A 对字段冲突的既有
处理，不新增完整 taxonomy、所有必填字段、条件匹配歧义或初始 constraint 真值
验证。XML / mis / err / extra / IT-NL 离线校验、概率扩展与求解策略重写均未实现。
