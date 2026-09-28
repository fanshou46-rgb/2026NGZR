/*
 * File: rdfw.cpp
 * Author : ShiQiao Chen(陈世侨)
 * Affiliation: WuHan University of Technology
 */
 #include <numeric>
 #include <unordered_map>
 #include <set>
 #include <map>
# include <cstring>
# include <iostream>
# include <regex>
# include "rdfw.hpp"
# include "parser.hpp"
using namespace _home;
using namespace std;

void split_string(vector<string> &out, const string &str_source, char mark);
ostream &operator<<(ostream &os, shared_ptr<Object> obj);
ostream &operator<<(ostream &os, shared_ptr<SyntaxNode> sn);
ostream &operator<<(ostream &os, const Instruction &instr);


/**
 * Load the team name.
 */
RDFW::RDFW() : Plug("RDFW") {

}

std::chrono::milliseconds RDFW::EstimateTaskTime(const Instruction& task) const
{
    if (terminal_checker.evaluateTask(*this, task) == TerminalStatus::SATISFIED)
        return std::chrono::milliseconds(0);

    // The existing planner executes actions directly and does not expose an action
    // list.  These deterministic estimates intentionally stay coarse and local.
    int estimate_ms = 150; // dispatch and feedback overhead
    if (task.behave == "goto" || task.behave == "move") estimate_ms += 650;
    else if (task.behave == "pickup") estimate_ms += 1100;
    else if (task.behave == "putdown") estimate_ms += 500;
    else if (task.behave == "open" || task.behave == "close") estimate_ms += 850;
    else if (task.behave == "putin" || task.behave == "takeout") estimate_ms += 1550;
    else if (task.behave == "puton" || task.behave == "give") estimate_ms += 1350;
    else estimate_ms += 1500;

    if (stage == 2) estimate_ms += 250; // bounded Ask/Sense allowance
    if (task.X.size() > 1) estimate_ms += static_cast<int>(task.X.size() - 1) * 350;
    return std::chrono::milliseconds(estimate_ms);
}

std::chrono::milliseconds RDFW::EstimateMultiGotoTime() const
{
    std::size_t enabled_goto = 0;
    for (const auto& task : tasks)
        if (task.isEnable && !task.hasMissingObjects && task.behave == "goto")
            ++enabled_goto;
    // Aggregation is incremental: the stop gate is re-applied before every
    // relocation candidate, so this is the next bounded chunk rather than the
    // whole remaining batch.
    return enabled_goto == 0
        ? std::chrono::milliseconds(0)
        : std::chrono::milliseconds(1000);
}

bool RDFW::HasExecutableCandidate(bool include_goto) const
{
    for (const auto& task : tasks) {
        if (!task.isEnable || task.hasMissingObjects || task.risk >= 2) continue;
        if (!include_goto && task.behave == "goto") continue;
        if (deadline_manager.canFinish(EstimateTaskTime(task), plan_safety_margin))
            return true;
    }
    return false;
}

void RDFW::LogProgressSnapshot(const char* phase) const
{
    const ScoreSnapshot score = score_evaluator.snapshot(*this, terminal_checker);
    const TerminalSummary terminal = terminal_checker.evaluateAll(*this);
    std::ostringstream completed_goal_ids;
    std::ostringstream satisfied_constraint_ids;
    bool first_goal = true;
    bool first_constraint = true;
    for (std::size_t i = 0; i < terminal.goals.size(); ++i) {
        if (terminal.goals[i] != TerminalStatus::SATISFIED) continue;
        if (!first_goal) completed_goal_ids << ',';
        completed_goal_ids << i << ':' << tasks[i].behave;
        first_goal = false;
    }
    for (std::size_t i = 0; i < terminal.constraints.size(); ++i) {
        if (terminal.constraints[i] != TerminalStatus::SATISFIED) continue;
        if (!first_constraint) satisfied_constraint_ids << ',';
        satisfied_constraint_ids << i;
        first_constraint = false;
    }
    LOG(CYAN_BLUE "[3A][%s] goals=%zu/%zu (unknown=%zu), constraints=%zu/%zu "
                  "(unknown=%zu), base_score=%d, action_cost=%d, "
                  "elapsed=%lldms, remaining=%lldms\n" RESET,
        phase,
        score.completed_goals, score.total_goals, score.unknown_goals,
        score.satisfied_constraints, score.total_constraints,
        score.unknown_constraints, score.deterministic_base_score,
        score.action_cost,
        static_cast<long long>(deadline_manager.elapsed().count()),
        static_cast<long long>(deadline_manager.remaining().count()));
    LOG(CYAN_BLUE "[3A][%s] completed_goals=[%s], satisfied_constraints=[%s]\n" RESET,
        phase, completed_goal_ids.str().c_str(), satisfied_constraint_ids.str().c_str());
}

bool RDFW::StopGate(const char* phase, bool include_goto)
{
    LogProgressSnapshot(phase);
    const TerminalSummary terminal = terminal_checker.evaluateAll(*this);
    if (terminal.allGoalsSatisfied()) {
        LOG(GREEN "[3A][StopGate] all goals are SATISFIED; normal stop before %s\n" RESET,
            phase);
        normal_stop_requested = true;
        return true;
    }
    if (deadline_manager.deadlineReached()) {
        LOG(YELLOW "[3A][StopGate] deadline reached; normal stop before %s\n" RESET,
            phase);
        normal_stop_requested = true;
        return true;
    }
    if (!HasExecutableCandidate(include_goto)) {
        const bool no_global_candidate = include_goto || !HasExecutableCandidate(true);
        LOG(YELLOW "[3A][StopGate] no executable candidate%s before %s\n" RESET,
            no_global_candidate ? "" : " in this phase", phase);
        if (no_global_candidate) normal_stop_requested = true;
        return true;
    }
    return false;
}

bool RDFW::CanStartPlan(const Instruction& task, const char* phase) const
{
    const std::chrono::milliseconds estimate = EstimateTaskTime(task);
    if (deadline_manager.canFinish(estimate, plan_safety_margin)) return true;
    LOG(YELLOW "[3A][StopGate] skip %s plan in %s: estimate=%lldms, "
               "safety=%lldms, remaining=%lldms\n" RESET,
        task.behave.c_str(), phase,
        static_cast<long long>(estimate.count()),
        static_cast<long long>(plan_safety_margin.count()),
        static_cast<long long>(deadline_manager.remaining().count()));
    return false;
}

/**
 * @brief 初始化动态数组
 * @param max_size 数组的最大大小，默认为100
 */
void RDFW::InitializeDynamicArrays(int max_size) {
    cout << "#(RDFW): Initializing dynamic arrays with size " << max_size << endl;

    // 初始化一维数组 - 使用reserve优化内存分配
    goto_cons.clear();
    goto_cons.reserve(max_size);
    goto_cons.resize(max_size, 0);

    putdown1_cons.clear();
    putdown1_cons.reserve(max_size);
    putdown1_cons.resize(max_size, 0);

    open_cons.clear();
    open_cons.reserve(max_size);
    open_cons.resize(max_size, 0);

    close_cons.clear();
    close_cons.reserve(max_size);
    close_cons.resize(max_size, 0);

    pickup_cons.clear();
    pickup_cons.reserve(max_size);
    pickup_cons.resize(max_size, 0);

    givehuman_cons.clear();
    givehuman_cons.reserve(max_size);
    givehuman_cons.resize(max_size, 0);

    fromplate_cons.clear();
    fromplate_cons.reserve(max_size);
    fromplate_cons.resize(max_size, 0);

    toplate_cons.clear();
    toplate_cons.reserve(max_size);
    toplate_cons.resize(max_size, 0);

    rightlocation.clear();
    rightlocation.reserve(max_size);
    rightlocation.resize(max_size, false);

    objectLocationVerified.assign(max_size, false);
    objectLocationInferredByMustNear.assign(max_size, false);
    objectInsideVerified.assign(max_size, false);
    containerStateVerified.assign(max_size, false);

    // 初始化二维数组 - 优化内存分配
    putin_cons.clear();
    putin_cons.reserve(max_size);
    for (int i = 0; i < max_size; i++) {
        putin_cons.emplace_back(max_size, 0);
    }

    takeout_cons.clear();
    takeout_cons.reserve(max_size);
    for (int i = 0; i < max_size; i++) {
        takeout_cons.emplace_back(max_size, 0);
    }

    putdown_cons.clear();
    putdown_cons.reserve(max_size);
    for (int i = 0; i < max_size; i++) {
        putdown_cons.emplace_back(max_size, 0);
    }

    move_cons.clear();
    move_cons.reserve(max_size);
    for (int i = 0; i < max_size; i++) {
        move_cons.emplace_back(max_size, 0);
    }

    mustnear_cons.clear();
    mustnear_cons.reserve(max_size);
    for (int i = 0; i < max_size; i++) {
        mustnear_cons.emplace_back(max_size, 0);
    }

    cout << "#(RDFW): Dynamic arrays initialization completed" << endl;
}


/**
 * @brief Initialization Function
 * @param argc:     argument count
 * @param argv:     argument value
 * Tasks:
 * 1. Parse Arguments and set options --> LOG
 * 2.
 */
void RDFW::Init(int argc, char **argv) // 改
{
    string path = "../example/words.txt";   // loading word dictionary
    if (argc > 1)
    {
        // Task 1: Parse Arguments and set options --> LOG
        bool optionFound = false; // 记录是否找到匹配的选项

        for (int i = 1; i < argc; i++)
        {
            LOG("%s", argv[i]);

            const std::string arg(argv[i]);
            const std::string nextArg(i + 1 < argc ? argv[i + 1] : "");

            // Change Option
            enum Options
            {
                NLP,
                ERR,
                ASK_2,
                PATH,
                STAGE
            };

            int option = -1;
            if (arg == "-nlp"){
                option = NLP;
                optionFound = true;
            } else if (arg == "-err") {
                option = ERR;
                optionFound = true;
            } else if (arg == "-ask_2"){
                option = ASK_2;
                optionFound = true;
            } else if (arg == "-path") {
                option = PATH;
                optionFound = true;
            } else if (arg == "-stage") {
                option = STAGE;
                optionFound = true;
            }

            // Set Option Value (Option value is in the next arg.)
            switch (option)
            {
                case NLP:
                    isNaturalParse = stoi(nextArg); // Extract next arg's value (e.g.  -nlp 0)
                    i++;
                    break;
                case ERR:
                    isErrorCorrection = stoi(nextArg);
                    i++;
                    break;
                case ASK_2:
                    isAskTwice = stoi(nextArg);
                    i++;
                    break;
                case PATH:
                    path = nextArg;
                    i++;
                    break;
                case STAGE:
                {
                    int temp = stoi(nextArg);
                    if(temp==1) stage=1;
                    if(temp==2) stage=2;
                    i++;
                }
                break;
            }
        }

        if (!optionFound)
        {
            LOG("notfound"); // 处理未匹配的选项
            // 可以输出错误信息或执行其他操作
        }
    }
    LOG("nlp %d, err %d", isNaturalParse, isErrorCorrection);

    objects.push_back(shared_from_this());  // 向物品中添加当前对象

    if (isErrorCorrection)
        posCorrectFlag.push_back(false);
    else
        posCorrectFlag.push_back(true);

    // 初始化动态数组
    InitializeDynamicArrays(100);  // 设置为100以支持更大的位置索引

    // 初始化位置感知记录数组，为所有可能的位置预留空间
    posSensedFlag.resize(100, false);  // 为100个位置预留空间，全部标记为未感知

    // 初始化位置感知物体记录数组
    locationSensedObjects.resize(100);  // 为100个位置预留空间

    nlp_parser = new parser();
    nlp_parser->words_map_initialize(path);
}


void RDFW::Plan() // 改
{
    deadline_manager.reset(deadline_manager.timeLimit());
    score_evaluator.reset();
    normal_stop_requested = false;

    // ==================== 测试开始前的状态验证 ====================
    cout << "#(RDFW): Starting new test - verifying clean state" << endl;

    // 验证关键状态变量是否已重置
    SetSolvedTaskNum(0);
    task_index = 0;
    err_times = 0;
    isPass = false;
    isKeepConstrain = false;
    isMultiGotoMode = false;
    isAutoConstrain = false;

    // 验证机器人状态
    location = UNKNOWN;
    hold = nullptr;
    hold_id = 0;

    // 验证感知状态
    for (size_t i = 0; i < posSensedFlag.size(); i++) {
        posSensedFlag[i] = false;
    }
    fill(objectLocationVerified.begin(), objectLocationVerified.end(), false);
    fill(objectLocationInferredByMustNear.begin(), objectLocationInferredByMustNear.end(), false);
    fill(objectInsideVerified.begin(), objectInsideVerified.end(), false);
    fill(containerStateVerified.begin(), containerStateVerified.end(), false);

    // 验证位置感知物体记录
    for (auto& loc_info : locationSensedObjects) {
        loc_info.object_ids.clear();
        loc_info.container_id = 0;
        loc_info.has_container = false;
    }

    // 验证约束查找表
    lock_by_mustnear.clear();
    mustNearComponent.clear();

    // 验证并查集状态
    memset(uf_parent, -1, sizeof(uf_parent));
    memset(uf_size, 0, sizeof(uf_size));
    memset(uf_groupLoc, -1, sizeof(uf_groupLoc));

    // 验证动态数组状态
    fill(goto_cons.begin(), goto_cons.end(), 0);
    fill(putdown1_cons.begin(), putdown1_cons.end(), 0);
    fill(open_cons.begin(), open_cons.end(), 0);
    fill(close_cons.begin(), close_cons.end(), 0);
    fill(pickup_cons.begin(), pickup_cons.end(), 0);
    fill(givehuman_cons.begin(), givehuman_cons.end(), 0);
    fill(fromplate_cons.begin(), fromplate_cons.end(), 0);
    fill(toplate_cons.begin(), toplate_cons.end(), 0);
    fill(rightlocation.begin(), rightlocation.end(), false);

    // 验证二维数组状态
    for (auto& row : putin_cons) fill(row.begin(), row.end(), 0);
    for (auto& row : takeout_cons) fill(row.begin(), row.end(), 0);
    for (auto& row : putdown_cons) fill(row.begin(), row.end(), 0);
    for (auto& row : move_cons) fill(row.begin(), row.end(), 0);
    for (auto& row : mustnear_cons) fill(row.begin(), row.end(), 0);

    // 验证解析器状态
    if (nlp_parser) {
        parser::clear_static_state();
    }

    cout << "#(RDFW): Pre-test state verification completed" << endl;

    // print test name
    printf(GREEN "%s\n" RESET, GetTestName().c_str());


    cout <<  "--------------------------------------------" << endl;
    cout << "Ready to Parse Env Infos." << endl;

    string env_str = GetEnvDes();

    // Try to Parse Env, write to Object, SmallObject
    if (ParseEnv(env_str) == false) {
        cout<<"ParseEnv Failed! Skipping this test."<<endl;
        cout<<"# Test skipped due to environment parsing failure"<<endl;
        return;  // Exit Plan() gracefully, allowing Fini() to be called
    } else {
        cout << endl << "ParseEnv finished" << endl;
    }

    cout <<  "--------------------------------------------" << endl;
    cout << "Ready to Parse Tasks and Cons." << endl;

    const string task_str = GetTaskDes();

    if(task_str[0]=='(')  {  // check IT or NT
        isNaturalParse=0;
    } else {
        isNaturalParse=1;
    }

    // parse natrual language
    if (isNaturalParse) {
        ParseNaturalLanguage(task_str);
    } else {
        if (ParseInstruction(task_str) == false) {
            cout << "Parse Natural Language Failed. Skipping this test." << endl;
            cout << "# Test skipped due to instruction parsing failure" << endl;
            return;  // Exit Plan() gracefully, allowing Fini() to be called
        }
    }

    // Parse Info Complements
    for (const auto &v : infos){
        ParseInfo(v);
    }


    if(stage == 2){
        PrintEnv();
    // ==================== 约束纠错与补全 ====================
    // 在解析完成后、位置推断前进行约束纠错
    ApplyOpenCloseCorrection();
    ApplyMustInConstraintCorrection();
    ApplyMustNearConstraintCorrection();

    }
    // Find Human Infomation from Objects
    human = nullptr;
    for (const auto &obj : objects) {
        if (obj->sort == "human") {
            human = ObjectPtrCast<BigObject>(obj);
            break;
        }
    }

    // print environment, instructions,
    PrintEnv();
    PrintInstruction();
    cout<<"Parse Tasks, Cons and Infos finished."<<endl;
    cout <<  "--------------------------------------------" << endl;



    /*=======================约束条件规划===================*/

    cout << "Ready to Cons  plan" << endl;
    Cons_plan();
    FilterConstraintsByTaskConflicts();
    cout<<"cons_plan finished"<<endl;
    cout <<  "--------------------------------------------" << endl;

    /*=======================任务优化===================*/
    tasks = TaskOptimization();
    cout<<"taskoptimization finished"<<endl;
    cout <<  "--------------------------------------------" << endl;

    /*=======================任务执行===================*/
    if (false)
    {
        cout << "2222222" << endl;
        cout << "2222222" << endl;
    }
    else
    {
        const size_t tasksSize = tasks.size();
        const bool performErrorCorrection = isErrorCorrection;//是否开启纠错模式
        cout << tasksSize << endl;

        // 检查并延迟多goto任务
        bool defer_multi_goto = CheckAndDeferMultiGoto();

        // 设置多goto模式标志
        //isMultiGotoMode = defer_multi_goto;

         // 执行主任务循环
         ExecuteMainTaskLoop(defer_multi_goto);

        /*============== mustchooseone and goto ==============*/
        // 只在“剩余启用的 goto < 2”时才调用 MustChooseOne，避免抢跑 goto
        if (!normal_stop_requested && solved_task_num == 0) {
            size_t remain_goto = 0;
            for (auto &t : tasks) if (t.isEnable && t.behave == "goto") ++remain_goto;
            if (remain_goto < 2) {
                MustChooseOne();
            } else {
                LOG(YELLOW "[Defer] skip MustChooseOne because multi-goto remain=%zu\n" RESET, remain_goto);
            }
        }

    }
    /*============== 检查阶段 ==============*/
    //检查一遍
    cout<<"-----check check check-----"<<endl;

    // 执行检查阶段
    if (!normal_stop_requested)
        ExecuteCheckPhase(CheckAndDeferMultiGoto());

    /*============== Multi-GOTO聚合 ==============*/
    // 执行Multi-GOTO聚合
    if (!normal_stop_requested) {
        PrintEnv();
        ExecuteMultiGotoAggregation();
    }

    /*============== 结果输出 ==============*/
    cout << endl
         << "Sovled Task Num:" << solved_task_num << "    " << "Expect Num:" << tasks.size() << endl;
    LogProgressSnapshot("final");
}

/*============== 主任务循环 ==============*/
void RDFW::ExecuteMainTaskLoop(bool defer_multi_goto)
{
    /*if(stage==2)
    {
        SenseCurrentLocationOnly();
    }*/

    // ============== 统计puton任务中出现多次的大物体 ==============
    map<unsigned int, int> bigObjectTaskCount;  // 大物体ID -> 任务数量
    map<unsigned int, vector<unsigned int>> bigObjectTaskIndices;  // 大物体ID -> 任务索引列表

    for (size_t i = 0; i < tasks.size(); ++i) {
        if (tasks[i].isEnable && tasks[i].behave == "puton" &&
            !tasks[i].Y.empty() && tasks[i].Y[0] != nullptr) {
            unsigned int bigObjectId = tasks[i].Y[0]->id;
            bigObjectTaskCount[bigObjectId]++;
            bigObjectTaskIndices[bigObjectId].push_back(i);
        }
    }

    // 标记出现多次的大物体
    for (const auto& pair : bigObjectTaskCount) {
        if (pair.second >= 2) {
            unsigned int bigObjectId = pair.first;
            int taskCount = pair.second;
            LOG(GREEN "[MultiPuton] Big object %d (sort: %s) appears in %d puton tasks" RESET,
                bigObjectId, objects[bigObjectId]->sort.c_str(), taskCount);

            // 标记这些任务为多puton任务
            for (unsigned int taskIdx : bigObjectTaskIndices[bigObjectId]) {
                tasks[taskIdx].isMultiPuton = true;  // 假设Instruction类有这个成员
                LOG(YELLOW "[MultiPuton] Marked task %d as multi-puton for object %d" RESET,
                    taskIdx, bigObjectId);
            }
        }
    }
    // ============== 多puton统计结束 ==============

    const size_t tasksSize = tasks.size();
    for (task_index = 0; task_index < tasksSize; ++task_index)
    {
        // 跳过包含不存在物体的任务
        if (tasks[task_index].hasMissingObjects) {
            continue;
        }

        // 延后多 GOTO：本轮不做，留给末尾聚合
        if (defer_multi_goto && tasks[task_index].behave == "goto") {
            continue;
        }

        if (StopGate("main-loop", false)) return;
        if (!CanStartPlan(tasks[task_index], "main-loop")) continue;

        isPass = false;
         /*============== 风险预判 ================*/
        if(CalculateTaskRisk(tasks[task_index])>=2) {     //先行判断
            cout<<tasks[task_index].behave<<" "<<"的风险系数是："<<tasks[task_index].risk<<endl;
            stringstream ss;
            ss << tasks[task_index];
            LOG(GREEN "too many cons\n %s" RESET, ss.str().c_str());
            continue;
        }

        /*============== 任务执行 ================*/

        // —— 零动作预验证：仅 stage2 且当前判定为“已满足”的任务才触发
        bool zero_ok = ZeroActionPreCheck(tasks[task_index]);
        if (zero_ok) {
            stringstream ss; ss << tasks[task_index];
            LOG(GREEN "Task done (zero-action prevalidated)\n %s" RESET, ss.str().c_str());
            SetSolvedTaskNum(solved_task_num + 1);
            tasks[task_index].isEnable = false;
            AfterSolveTask(tasks[task_index]);
        } else if (SolveTask(tasks[task_index])) {
            stringstream ss; ss << tasks[task_index];
            LOG(GREEN "Task done\n %s" RESET, ss.str().c_str());
            SetSolvedTaskNum(solved_task_num + 1);
            tasks[task_index].isEnable = false;
            AfterSolveTask(tasks[task_index]);
        } else {
            stringstream ss; ss << tasks[task_index];
            LOG(GREEN "Task not done\n %s" RESET, ss.str().c_str());
            tasks[task_index].isEnable=0;
            tasks[task_index].isfalse=1;
        }
    }
}


/*============== 检查阶段 ==============*/
void RDFW::ExecuteCheckPhase(bool defer_multi_goto)
{
    for(task_index = 0; task_index < tasks.size(); ++task_index){
        // 跳过包含不存在物体的任务
        if (tasks[task_index].hasMissingObjects) {
            continue;
        }

        // 延后多 GOTO：检查一遍也不做，留给末尾聚合
        if (defer_multi_goto && tasks[task_index].isEnable && tasks[task_index].behave == "goto") {
            continue;
        }
        if(tasks[task_index].isEnable&&CalculateTaskRisk(tasks[task_index])<2){
            if (StopGate("check-phase", false)) return;
            if (!CanStartPlan(tasks[task_index], "check-phase")) continue;
            bool zero_ok = ZeroActionPreCheck(tasks[task_index]);
            if (zero_ok) {
                stringstream ss; ss << tasks[task_index];
                LOG(GREEN "Task done (zero-action prevalidated)\n %s" RESET, ss.str().c_str());
                SetSolvedTaskNum(solved_task_num + 1);
                tasks[task_index].isEnable = false;
                AfterSolveTask(tasks[task_index]);
            } else if (SolveTask(tasks[task_index])) {
                stringstream ss; ss << tasks[task_index];
                LOG(GREEN "Task done\n %s" RESET, ss.str().c_str());
                SetSolvedTaskNum(solved_task_num + 1);
                tasks[task_index].isEnable = false;
                AfterSolveTask(tasks[task_index]);
            }
        }
    }
}





/**====================== 约束条件规划 =========================== */


void RDFW::Cons_plan(){
    int x;
    for(auto cons:not_infoConstrains){
        // 跳过包含不存在物体的约束
        if (cons.hasMissingObjects) {
            continue;
        }

        if(cons.behave=="on") {
            if(cons.X[0]->location!=cons.Y[0]->location) putdown_cons[cons.X[0]->id][cons.Y[0]->location]++;
            else if(cons.X[0]->id==plate_id||cons.X[0]->id==hold_id) putdown_cons[cons.X[0]->id][cons.Y[0]->location]++;
        }
        else if(cons.behave=="inside"||cons.behave=="in") {
             auto small=dynamic_pointer_cast<SmallObject>(cons.X[0]);
            if(small->inside!=cons.Y[0]->id) putin_cons[cons.X[0]->id][cons.Y[0]->id]++;
        }
        else if(cons.behave == "near"||cons.behave == "nextto") {
            if(cons.Y[0]->location!=cons.X[0]->location) //如果约束没有触犯
            {
            if(cons.Y[0]->location!=UNKNOWN) move_cons[cons.X[0]->id][cons.Y[0]->location]++;
            if(cons.X[0]->location!=UNKNOWN) move_cons[cons.Y[0]->id][cons.X[0]->location]++;
            }
        }
        else if(cons.behave == "plate") toplate_cons[cons.X[0]->id]++;
        else if(cons.behave == "opened") {
            auto cont=dynamic_pointer_cast<Container>(cons.X[0]);
            if(cont->isOpen!=1) open_cons[cons.X[0]->id]++;
        }
        else if(cons.behave == "closed")
        {
            auto cont=dynamic_pointer_cast<Container>(cons.X[0]);
            if(cont->isOpen==1) close_cons[cons.X[0]->id]++;
        }
    }
    for(auto cons:notnot_infoConstrains){
        // 跳过包含不存在物体的约束
        if (cons.hasMissingObjects) {
            continue;
        }

            if(cons.behave=="on"&&cons.X[0]->location==cons.Y[0]->location) {
                auto small=dynamic_pointer_cast<SmallObject>(cons.X[0]);
               if(small->inside!=cons.Y[0]->id) cons.X[0]->is_keep++;
            }
            else if((cons.behave=="near" || cons.behave=="nextto") && !cons.Y.empty()){
                // 关系图已由 BuildMustNearRelations 对称构建；这里仅维护当前
                // 已满足关系的 keep 权重，且覆盖 every 产生的 X × Y。
                for (const auto& x_obj : cons.X) {
                    if (!x_obj) continue;
                    for (const auto& y_obj : cons.Y) {
                        if (!y_obj || x_obj->id == y_obj->id) continue;
                        if (x_obj->location != UNKNOWN && x_obj->location == y_obj->location) {
                            x_obj->is_keep++;
                            y_obj->is_keep++;
                        }
                    }
                }
            }
            else if(cons.behave=="plate"&& plate_id==cons.X[0]->id)fromplate_cons[cons.X[0]->id]++;
            else if(cons.behave=="inside"||cons.behave=="in")
            {
            auto small=dynamic_pointer_cast<SmallObject>(cons.X[0]);
            if(small->inside==cons.Y[0]->id)  takeout_cons[cons.X[0]->id][cons.Y[0]->id]++;
            }
           else if(cons.behave=="closed") {
             auto cont=dynamic_pointer_cast<Container>(cons.X[0]);
            if(cont->isOpen!=1) open_cons[cons.X[0]->id]++;
           }
           else if(cons.behave=="opened") {
            auto cont=dynamic_pointer_cast<Container>(cons.X[0]);
            if(cont->isOpen!=1) close_cons[cons.X[0]->id]++;
           }
    }
    for(auto cons:not_taskConstrains){
        // 跳过包含不存在物体的约束
        if (cons.hasMissingObjects) {
            continue;
        }

        //这里不用判断一开始是否触犯约束
         if(cons.behave=="takeout") takeout_cons[cons.X[0]->id][cons.Y[0]->id]++;
         else if(cons.behave=="putin") putin_cons[cons.X[0]->id][cons.Y[0]->id]++;
         else if(cons.behave=="puton") putdown_cons[cons.X[0]->id][cons.Y[0]->location]++;
         else if(cons.behave=="goto") goto_cons[cons.X[0]->location]++;
         else if(cons.behave=="open") open_cons[cons.X[0]->id]++;
         else if(cons.behave=="close") close_cons[cons.X[0]->id]++;
         else if(cons.behave=="pickup") pickup_cons[cons.X[0]->id]++;
         else if(cons.behave=="give") givehuman_cons[cons.X[0]->id]++;
         else if(cons.behave == "putdown") putdown1_cons[cons.X[0]->id]++ ;
    }
    if(hold_id>0) {
        x=hold_id;
     if(objects[x]->is_keep>putdown1_cons[x]+putdown_cons[x][location]+fromplate_cons[x]){
        cout<<"the hold object must putdown here!"<<endl;
         PutDown(x);
     }
     }
    if(plate_id>0)
    {
        x=plate_id;
     if(objects[x]->is_keep>putdown1_cons[x]+putdown_cons[x][location]+fromplate_cons[x]){
        cout<<"the plate object must putdown here!"<<endl;
        if(hold_id>0) PutDown(hold_id);
        FromPlate(x);
         PutDown(x);
     }
    }

}


void RDFW::FilterConstraintsByTaskConflicts() {
    // 只计算goto_cons和open_cons与多少任务冲突，超过4个则舍弃这个约束
    // 定义一个需要舍弃的gotocons数组
    int discard_gotoconsloc[100] = {0};
    int discard_gotoconsloc_count[100] = {0};
    int sum_conflict_count=0;
    int max_effect=0;
    int max_effect_loc=0;
    int i=0;//计数
    // 1. 处理goto_cons
    for (int loc = 0; loc < (int)goto_cons.size(); ++loc) {
        if (goto_cons[loc] > 0) {
            int conflict_count = 0;
            for (const auto& task : tasks) {
                // 判断任务是否会与goto约束冲突
                if (task.isEnable) {
                    if ((task.behave == "goto" && task.X.size() > 0 && task.X[0]->location == loc) ||
                        (task.behave == "putin" && task.Y.size() > 0 && task.Y[0]->location == loc) ||
                        (task.behave == "putin" && task.X.size() > 0 && task.X[0]->location == loc)||
                        (task.behave == "puton" && task.Y.size() > 0 && task.Y[0]->location == loc)||
                        (task.behave == "puton" && task.X.size() > 0 && task.X[0]->location == loc)||
                        (task.behave == "open" && task.X.size() > 0 && task.X[0]->location == loc)||
                        (task.behave == "close" && task.X.size() > 0 && task.X[0]->location == loc)||
                        (task.behave == "pickup" && task.X.size() > 0 && task.X[0]->location == loc)||
                        (task.behave == "give" && task.X.size() > 0 && task.X[0]->location == loc)||
                        (task.behave == "give" && task.Y.size() > 0 && task.Y[0]->location == loc)||
                        (task.behave == "takeout" && task.Y.size() > 0 && task.Y[0]->location == loc)) {
                        conflict_count++;
                        cout << "[FilterConstraintsByTaskConflicts] Conflict found between goto_cons at location " << loc << " and task " << task.behave << " at location " << task.X[0]->location << endl;
                    }
                }
            }
            if (conflict_count - goto_cons[loc] > 2) {
                discard_gotoconsloc[i] = loc;
                discard_gotoconsloc_count[i] = conflict_count;
                sum_conflict_count+=conflict_count;
                if (conflict_count - goto_cons[loc] > max_effect) {
                    max_effect = conflict_count - goto_cons[loc];
                    max_effect_loc = loc;
                }
                cout << "[FilterConstraintsByTaskConflicts] Conflict found between goto_cons at location " << loc << " with conflict count " << conflict_count << endl;
                i++;
            }
        }
    }


    if(sum_conflict_count>30) {
        goto_cons[max_effect_loc] = 0;
        cout << "[FilterConstraintsByTaskConflicts] Discarded goto_cons at location " << max_effect_loc << " due to " << max_effect << " conflicts." << endl;
    }
    else{
        while(i>=0){
            goto_cons[discard_gotoconsloc[i]] = 0;
            cout << "[FilterConstraintsByTaskConflicts] Discarded goto_cons at location " << discard_gotoconsloc[i] << " due to " << discard_gotoconsloc_count[i] << " conflicts." << endl;
            i--;
        }
    }

    // 2. 处理open_cons，逻辑同goto_cons
    int discard_openconsid[100] = {0};
    int discard_openconsid_count[100] = {0};
    int sum_conflict_count_open=0;
    int max_effect_open=0;
    int max_effect_id=0;
    int j=0;
    for (int id = 0; id < (int)open_cons.size(); ++id) {
        if (open_cons[id] > 0) {
            int conflict_count = 0;
            for (const auto& task : tasks) {
                // 判断任务是否会与open约束冲突
                // 这里假设冲突定义为：任务涉及该id，且是open/putin/takeout/puton/pickup/give等
                if (task.isEnable) {
                    if ((task.behave == "open" && task.X.size() > 0 && task.X[0]->id == id) ||
                        (task.behave == "putin" && task.Y.size() > 0 && task.Y[0]->id == id) ||
                        (task.behave == "putin" && task.X.size() > 0 && task.X[0]->id == id)||
                        (task.behave == "takeout" && task.Y.size() > 0 && task.Y[0]->id == id)||
                        (task.behave == "puton" && task.Y.size() > 0 && task.Y[0]->id == id)||
                        (task.behave == "pickup" && task.X.size() > 0 && task.X[0]->id == id)||
                        (task.behave == "give" && task.X.size() > 0 && task.X[0]->id == id)
                    ) {
                        conflict_count++;
                    }
                }
            }
            if (conflict_count - open_cons[id] > 2) {
                discard_openconsid[j] = id;
                discard_openconsid_count[j] = conflict_count;
                sum_conflict_count_open += conflict_count;
                if (conflict_count > max_effect_open) {
                    max_effect_open = conflict_count;
                    max_effect_id = id;
                }
                cout << "[FilterConstraintsByTaskConflicts] Conflict found between open_cons for id " << id << " with conflict count " << conflict_count << endl;
                j++;
            }
        }
    }

    if(sum_conflict_count_open>30) {
        open_cons[max_effect_id] = 0;
        cout << "[FilterConstraintsByTaskConflicts] Discarded open_cons for id " << max_effect_id << " due to " << max_effect_open << " conflicts." << endl;
    }
    else{
        for(int k = 0; k < j; k++){
            open_cons[discard_openconsid[k]] = 0;
            cout << "[FilterConstraintsByTaskConflicts] Discarded open_cons for id " << discard_openconsid[k] << " due to " << discard_openconsid_count[k] << " conflicts." << endl;
        }
    }



}


/**====================== 任务优化 =========================== */

//任务优化函数
vector<Instruction> RDFW::TaskOptimization()
{
    auto taskEvaluate = [](const string &behave) -> int
    {
        if (behave == "putin" || behave == "puton" || behave == "give")
            return 0;
        else if (behave == "takeout" ||behave == "putdown")
            return 1;
        else if (behave == "open" || behave == "close")
            return 2;
        else if ( behave == "pickup")
            return 3;
        else if (behave == "goto")
            return 4;
        else
            return 5;
    };
    /*
    auto TaskEquel =[](Instruction task1,Instruction task2) ->bool{
          if(task1.behave==task2.behave&&task1.behave!="pickup"&&task1.behave!="goto")
                if(task1.conditionX.sort==task2.conditionX.sort)
                    return true;
        if(task1.behave==task2.behave){
                if(task1.behave=="pickup"||task1.behave=="goto")
                return true;
            }

          return false;
    }*/
    // Sort tasks based on behavior evaluation and container grouping for takeout tasks
    std::sort(tasks.begin(), tasks.end(), [&](const Instruction &a, const Instruction &b)
              {
                  int priority_a = taskEvaluate(a.behave);
                  int priority_b = taskEvaluate(b.behave);

                  // If different task types, sort by priority
                  if (priority_a != priority_b) {
                      return priority_a < priority_b;
                  }

                  // If both are takeout tasks, group by container (Y[0]->id)
                  if (a.behave == "takeout" && b.behave == "takeout") {
                      if (!a.Y.empty() && !b.Y.empty()) {
                          return a.Y[0]->id < b.Y[0]->id;
                      }
                  }

                  // For other cases, maintain original order (stable sort)
                  return false;
              });


    vector<Instruction> optimizedTasks;
    optimizedTasks.reserve(tasks.size());

    bool hasGoto = false;
    for(int i=0;i<tasks.size();i++){
        // 跳过包含不存在物体的任务
        if (tasks[i].hasMissingObjects) {
            continue;
        }

        optimizedTasks.push_back(tasks[i]);
      }

return optimizedTasks;
}

bool RDFW::HasRequestedTask(const string &behave, unsigned int object_id,
                            unsigned int target_id) const
{
    for (const auto &task : tasks) {
        // 与原索引一致：不按 isEnable/isfalse 过滤，只匹配 X[0]/Y[0]。
        // 扩展到全部候选对象会改变冲突策略，不属于本次结构简化。
        if (task.hasMissingObjects || task.behave != behave ||
            task.X.empty() || !task.X[0] || task.X[0]->id != object_id) {
            continue;
        }
        if (target_id != NONE &&
            (task.Y.empty() || !task.Y[0] || task.Y[0]->id != target_id)) {
            continue;
        }
        return true;
    }
    return false;
}




/**====================== 任务执行 =========================== */

/*========1)风险预判 ===============*/

//计算任务风险
int RDFW::CalculateTaskRisk(Instruction &t){
    t.risk=0;
   if(t.behave=="takeout")
   {
     auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
    if(small->inside!=t.Y[0]->id) return 0;//如果任务满足
       EnsureLocationCapacity(t.Y[0]->location);
     t.risk+=takeout_cons[t.X[0]->id][t.Y[0]->id]+goto_cons[t.Y[0]->location];
     t.risk+=open_cons[t.Y[0]->id];
    }

     else if(t.behave=="putin") {
         auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
          if(small->inside==t.Y[0]->id) return 0;
         EnsureLocationCapacity(t.Y[0]->location);

            t.risk+=putin_cons[t.X[0]->id][t.Y[0]->id]+open_cons[t.Y[0]->id]+move_cons[t.X[0]->id][t.Y[0]->location];
            if(t.X[0]->location!=t.Y[0]->location) t.risk+=goto_cons[t.Y[0]->location];
            CalculateStepRisk(t);

      }
      else if(t.behave=="puton") {
          EnsureLocationCapacity(t.Y[0]->location);

          t.risk+= putdown_cons[t.X[0]->id][t.Y[0]->location]+move_cons[t.X[0]->id][t.Y[0]->location]+putdown1_cons[t.X[0]->id];
        if(t.X[0]->location!=t.Y[0]->location) t.risk+=goto_cons[t.Y[0]->location];
        CalculateStepRisk(t);
      }
      else if (t.behave == "goto") {
          int loc = t.X[0]->location;
          t.risk += goto_cons[loc];
           // 调试日志，明确 t.risk 的组成
          std::cout << "[DBG] goto risk@loc=" << loc
                    << " bool=" << goto_cons[loc]
                   << std::endl;
      }

      else if(t.behave=="open") t.risk+=open_cons[t.X[0]->id]+goto_cons[t.X[0]->location];
      else if(t.behave=="close") t.risk+=close_cons[t.X[0]->id]+goto_cons[t.X[0]->location];
      else if(t.behave=="pickup") {
         CalculateStepRisk(t);
      }
      else if(t.behave=="give") {
         CalculateStepRisk(t);
         t.risk+=givehuman_cons[t.X[0]->id]+move_cons[t.X[0]->id][human->location]+putdown1_cons[t.X[0]->id];
         if(t.X[0]->location!=human->location) t.risk+=goto_cons[human->location];
         auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
      }
      else if(t.behave == "putdown")t.risk+=putdown1_cons[t.X[0]->id];
    //  t.risk+=t.X[0]->is_keep;
    int keep_penalty = t.X[0]->is_keep;
    // 特例：仅对 pickup，且与 near/next-to 的“对端对象”仍在同一位置时，
    // 视为 pickup 不破坏 near/next-to —— 不计入这部分 keep 惩罚。
    if (t.behave == "pickup") {
        int near_keep = 0;
        for (const auto &cons : notnot_infoConstrains) {
            if (cons.behave == "near") { // 你的“next to”在解析里等同于 near
                const auto aId = t.X[0]->id;
                bool a_is_X = (cons.X.size() > 0 && cons.X[0]->id == aId);
                bool a_is_Y = (cons.Y.size() > 0 && cons.Y[0]->id == aId);
                if (!(a_is_X || a_is_Y)) continue;

                // 找到与 t.X[0] 成 near 关系的“另一端对象”
                shared_ptr<Object> other =
                    a_is_X ? (cons.Y.size() ? cons.Y[0] : nullptr)
                           : (cons.X.size() ? cons.X[0] : nullptr);

                // 如果二者当前确实在同一位置，则“原地 pickup”不会破坏 near
                if (other && other->location == t.X[0]->location && t.X[0]->location != UNKNOWN) {
                    near_keep++;
                }
            }
        }
        // 只剔除 near/next-to 导致的 keep 惩罚，其它类型的 keep 仍然有效
        if (near_keep > 0) {
            keep_penalty = std::max(0, keep_penalty - near_keep);
        }
    }
    t.risk += keep_penalty;
      return t.risk;
}


//计算步骤风险------计算获取物体的约束值
int RDFW:: CalculateStepRisk(Instruction &t){
    if (t.X.empty() || !t.X[0]) return 0;
    if(t.X[0]->location!=location && t.X[0]->location >= 0) {
        EnsureLocationCapacity(t.X[0]->location);
        t.risk+=goto_cons[t.X[0]->location];
    }
    auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
    if (!small) return 0;
    if(small->inside!=UNKNOWN&&small->inside!=NONE)t.risk+=open_cons[small->inside]+takeout_cons[small->id][small->inside];
    else if(small->inside==NONE) t.risk+=pickup_cons[small->id];
    return 1;
}

// ==== helpers for capacity & existence ====
inline void RDFW::EnsureLocationCapacity(int loc) {
    if (loc < 0) return;

    // 扩展位置相关的动态数组
    if (loc >= (int)posCorrectFlag.size()) posCorrectFlag.resize(loc + 1, true); // 位置维度
    if (loc >= (int)posSensedFlag.size()) posSensedFlag.resize(loc + 1, false);
    if (loc >= (int)locationSensedObjects.size()) locationSensedObjects.resize(loc + 1);

    // 扩展约束数组
    if (loc >= (int)goto_cons.size()) goto_cons.resize(loc + 1, 0);
    if (loc >= (int)putdown1_cons.size()) putdown1_cons.resize(loc + 1, 0);
    if (loc >= (int)open_cons.size()) open_cons.resize(loc + 1, 0);
    if (loc >= (int)close_cons.size()) close_cons.resize(loc + 1, 0);
    if (loc >= (int)pickup_cons.size()) pickup_cons.resize(loc + 1, 0);
    if (loc >= (int)givehuman_cons.size()) givehuman_cons.resize(loc + 1, 0);
    if (loc >= (int)fromplate_cons.size()) fromplate_cons.resize(loc + 1, 0);
    if (loc >= (int)toplate_cons.size()) toplate_cons.resize(loc + 1, 0);
    if (loc >= (int)rightlocation.size()) rightlocation.resize(loc + 1, false);

    // 扩展二维约束数组
    if (loc >= (int)putin_cons.size()) putin_cons.resize(loc + 1, vector<int>(putin_cons.empty() ? 0 : putin_cons[0].size(), 0));
    if (loc >= (int)takeout_cons.size()) takeout_cons.resize(loc + 1, vector<int>(takeout_cons.empty() ? 0 : takeout_cons[0].size(), 0));
    if (loc >= (int)putdown_cons.size()) putdown_cons.resize(loc + 1, vector<int>(putdown_cons.empty() ? 0 : putdown_cons[0].size(), 0));
    if (loc >= (int)move_cons.size()) move_cons.resize(loc + 1, vector<int>(move_cons.empty() ? 0 : move_cons[0].size(), 0));
    // mustnear_cons 的两个维度都是对象 id，不能用位置 loc 扩容。

}

inline void RDFW::EnsureObjectExists(unsigned id, bool prefer_small) {
    if (id >= objects.size()) {
        size_t last = objects.size();
        objects.resize(id + 1);
        for (size_t i = last; i < objects.size(); ++i) {
            objects[i] = std::make_shared<Object>((unsigned)i);
        }
    }
    if (prefer_small) {
        if (!std::dynamic_pointer_cast<SmallObject>(objects[id])) {
            objects[id] = std::make_shared<SmallObject>(objects[id]); // 基于已有 Object 包装
            smallObjects.push_back(std::dynamic_pointer_cast<SmallObject>(objects[id]));
        }
    }
    const size_t object_count = objects.size();
    if (mustnear_cons.size() < object_count) mustnear_cons.resize(object_count);
    for (auto& row : mustnear_cons) {
        if (row.size() < object_count) row.resize(object_count, 0);
    }
    if (mustNearComponent.size() < object_count)
        mustNearComponent.resize(object_count, UNKNOWN);
    if (lock_by_mustnear.size() < object_count)
        lock_by_mustnear.resize(object_count, false);
    EnsureEvidenceCapacity(id);
}

void RDFW::EnsureEvidenceCapacity(unsigned int id) {
    const size_t required = static_cast<size_t>(id) + 1;
    if (objectLocationVerified.size() < required)
        objectLocationVerified.resize(required, false);
    if (objectLocationInferredByMustNear.size() < required)
        objectLocationInferredByMustNear.resize(required, false);
    if (objectInsideVerified.size() < required)
        objectInsideVerified.resize(required, false);
    if (containerStateVerified.size() < required)
        containerStateVerified.resize(required, false);
}

void RDFW::MarkDirectLocationEvidence(unsigned int id, bool verified) {
    EnsureEvidenceCapacity(id);
    objectLocationVerified[id] = verified;
    objectLocationInferredByMustNear[id] = false;
}

void RDFW::InvalidateSenseAtLocation(int loc) {
    if (loc < 0) return;
    EnsureLocationCapacity(loc);
    posSensedFlag[loc] = false;
    locationSensedObjects[loc].object_ids.clear();
    locationSensedObjects[loc].container_id = NONE;
    locationSensedObjects[loc].has_container = false;
}

bool RDFW::IsLocationVerified(unsigned int id) const {
    return id < objectLocationVerified.size() && objectLocationVerified[id];
}

bool RDFW::IsInsideVerified(unsigned int id) const {
    return id < objectInsideVerified.size() && objectInsideVerified[id];
}

bool RDFW::IsContainerStateVerified(unsigned int id) const {
    return id < containerStateVerified.size() && containerStateVerified[id];
}


/*========2)任务顺序执行 ===============*/

/*======a)做任务（边执行边判断）==========*/


//执行任务----主要是看有没有任务对象，服务stage2
bool RDFW::SolveTask(const Instruction &task) // 改
{
    bool success = false;//是否成功执行

    if (task.behave == "puton" || task.behave == "putin" || task.behave == "takeout")
    {
        if (task.X.empty() || task.Y.empty())
        {
            LogInstructionError(task);
            return false;
        }
        for (const auto &a : task.X)
        {
            cout<<task.behave<<" "<<a->sort<<"的风险系数是："<<task.risk<<endl;
            success = DoBehavious(task.behave, a->id, task.Y[0]->id);
            if (!success)
                break;
        }
    }
    else if (task.X.empty())
    {
        LogInstructionError(task);
        success = false;
    }
    else
    {
        for (const auto &a : task.X)
        {
            cout<<task.behave<<" "<<a->sort<<"的风险系数是："<<task.risk<<endl;
            success = DoBehavious(task.behave,a->id);
            if (!success)
                break;
        }
    }
    return success;
}

//执行行为---一个对象
bool RDFW::DoBehavious(const string &behavious, unsigned int x)
{
    if (behavious == "move" || behavious == "Move" || behavious == "Goto" || behavious == "goto")
        return SolveTask_Goto(x);
    else if (behavious == "pickup" || behavious == "PickUp")
        return SolveTask_PickUp(x);
    else if (behavious == "close" || behavious == "Close")
    {
        return SolveTask_Close(x);
    }

    else if (behavious == "open" || behavious == "Open")
    {
        return SolveTask_Open(x);
    }
    else if (behavious == "putdown" || behavious == "PutDown")
        return SolveTask_PutDown(x);
    else if (behavious == "give" || behavious == "Give")
        return SolveTask_Give(x);
    else
    {
           LOG("error task error task error task");
           return false;
    }
}

//执行行为---两个对象
bool RDFW::DoBehavious(const string &behavious, unsigned int a, unsigned int b) //dobehavious函数
{
    if (behavious == "putin" || behavious == "PutIn")
    {
        return SolveTask_Putin(a,b);
    }

    else if (behavious == "takeout" || behavious == "TakeOut")
    {
       return SolveTask_TakeOut(a,b);
    }

    else if (behavious == "puton" || behavious == "PutOn")
    {
        return SolveTask_PutOn(a,b);
    }
    else
    {
        LOG("error task error task error task");
        return false;
    }
}

//拿起物体的逻辑
bool RDFW::HoldSmallObject(unsigned int a)
{
    int t = 0;
    auto target_small = ObjectPtrCast<SmallObject>(objects[a]);
    ///这是stage1的逻辑
     if(stage==1)
    {
      if (plate_id == a)
        {
        if (hold_id != NONE && !PutDown(hold_id)) return false;
        return FromPlate(a);
        }
       else if(hold_id==a) return true;
    if (hold_id != NONE && !PutDown(hold_id)) return false;
    if(location!=target_small->location && !Move(target_small->location)) return false;
    if(target_small->inside==NONE) return PickUp(a);
    else if(target_small->inside!=UNKNOWN)//说明小物体在容器里面
    {
       auto target_cont = ObjectPtrCast<Container>(objects[target_small->inside]);
       if(!target_cont->isOpen && !Open(target_cont->id)) return false;
       return  TakeOut(a,target_cont->id);
    }
    return false;
    }
    //这是stage2的逻辑
    if (hold_id == static_cast<int>(a)) {
        if (IsInsideVerified(a)) return true;
        // 初始 hold 事实可能是错的。用一次可观察动作建立本地事实；失败则清除猜测。
        if (PutDown(a)) return HoldSmallObject(a);
        SetHold(nullptr);
    }
    if (plate_id == static_cast<int>(a) && !IsInsideVerified(a)) {
        if (FromPlate(a)) return true;
        SetPlate(nullptr);
    }
    if (hold_id != a)
    {
        if (hold_id != NONE && !PutDown(hold_id)) return false; //如果拿着物体，先放下
        if (plate_id == a)
        {
        return FromPlate(a);
        }

        while (1)
        {
            t++;
            if (target_small->location != UNKNOWN)
            {
                if (location != target_small->location)
                    if(Move(target_small->location)!=1)
                    {
                        if (t >= 2)  return 0;
                        GetSmallObjectStatus(a);
                        if(!IsKeepingGoing(task_index)) return 0;
                        continue;
                    }
            //Airong:Move后感知，位置可能重新标记为UNKNOWN
                if(target_small->location == UNKNOWN ){
                    if (t >= 2)  return 0;
                    GetSmallObjectStatus(a);
                    if(!IsKeepingGoing(task_index)) return 0;
                    continue;
                }


                 if (target_small->inside == NONE||target_small->inside == UNKNOWN) //这里我想了想，可能不会有UNKOWN的情况
                {

                     if (target_small->location == location && PickUp(a)) return 1;

                     // 先保证容量（这是“语句”，必须放在 if 条件外执行）
                     EnsureLocationCapacity(location);

                     // 然后再按条件判断
                     if ( posSensedFlag[location]
                          && target_small->location == location
                          && HasContainerAtLocation(location)
                          && [&]{
                                 unsigned int cont_id = GetContainerAtLocation(location);
                                 if (cont_id > 0) {
                                     auto cont = ObjectPtrCast<Container>(objects[cont_id]);
                                     return (cont && cont->isOpen);
                                 }
                                 return false;
                             }() )
                     {
                         if (TakeOut(a, GetContainerAtLocation(location))) return 1;
                         if (t >= 2) return 0;
                     }
                     else {
                         if (plate_id == UNKNOWN && FromPlate(a)) return 1;
                         target_small->location = UNKNOWN;
                         if (t >= 2) return 0;
                         GetSmallObjectStatus(a);
                         if (!IsKeepingGoing(task_index)) return 0;
                         continue;
                     }


                }


                else
                {
                    int initial_cont_id=target_small->inside;
                    TakeOutResult result = TakeOutLogic(a,target_small->inside);
                    if(result == TakeOutResult::Success) return true;
                    else
                    {

                        if(result == TakeOutResult::NeedObjectLocation)  {if (t >= 2)  return 0;GetSmallObjectStatus(a);}
                        else if(result == TakeOutResult::NeedContainerLocation) {if (t >= 2)  return 0;GetBigObjectStatus(target_small->inside);}
                        else if(result == TakeOutResult::VerifyObjectRelation)
                        {
                            if (t >= 2)  return 0;
                            GetSmallObjectStatus(a);
                            if(Isinside(a,initial_cont_id))//a就在一开始容器里面
                            {
                                    if(Open(initial_cont_id)) return TakeOut(a,initial_cont_id); //认为骗我是关的
                                    else  GetBigObjectStatus(initial_cont_id);//open失败，本身不可能是open的，直接问容器
                            }
                            else
                            {
                                //小物体不在容器里了
                            }
                        }
                        if(!IsKeepingGoing(task_index)) return 0;
                        continue;
                    }

                }
            }
            else{
                  if (t >= 2)  return 0;
                GetSmallObjectStatus(a);
                if(!IsKeepingGoing(task_index)) return 0;
                continue;
            }

        }
    }
    return 1;
}

// 从容器拿出物体的逻辑。显式结果类型避免数字返回码在调用处被误解。
RDFW::TakeOutResult RDFW::TakeOutLogic(unsigned int small,unsigned int cont){
    auto target_cont = ObjectPtrCast<Container>(objects[cont]);
    if (!target_cont) return TakeOutResult::NeedContainerLocation;
    auto verified_absent_from_open_container = [&]() -> bool {
        if (!target_cont->isOpen || !IsContainerStateVerified(cont)) return false;
        SenseCurrentLocationOnly(true);
        const bool absent = HasObjectAtLocation(location, cont) &&
                            !HasObjectAtLocation(location, small);
        if (absent && small < objects.size()) {
            auto small_object = dynamic_pointer_cast<SmallObject>(objects[small]);
            if (small_object && small_object->inside == static_cast<int>(cont)) {
                target_cont->DeleteObjectInside(small_object);
                small_object->inside = UNKNOWN;
                EnsureEvidenceCapacity(small);
                objectInsideVerified[small] = false;
            }
        }
        return absent;
    };
    //Airong:
    if(target_cont->location==UNKNOWN)return TakeOutResult::NeedContainerLocation;

    if(!target_cont->isOpen)
    {
     if(Open(cont))
        if(!TakeOut(small,cont)) {
            if (verified_absent_from_open_container()) return TakeOutResult::Success;
            return TakeOutResult::NeedObjectLocation;
        }
        else return TakeOutResult::Success;
    else
    {
      if(sense(cont))
      {
        target_cont->isOpen = true;
        EnsureEvidenceCapacity(cont);
        containerStateVerified[cont] = true;
        if(!TakeOut(small,cont)) {
            if (verified_absent_from_open_container()) return TakeOutResult::Success;
            return TakeOutResult::NeedObjectLocation;
        }
        else return TakeOutResult::Success;
      }
      else return TakeOutResult::NeedContainerLocation;
    }
    }
    else //不需要打开容器
    {
         if(!TakeOut(small,cont))
         {
            if (verified_absent_from_open_container()) return TakeOutResult::Success;
            return TakeOutResult::VerifyObjectRelation;
         }
         else return TakeOutResult::Success;
    }
}


/*===============
  solve task流程
  ==============*/

//pickup任务
bool RDFW::SolveTask_PickUp(unsigned int a)
{
    if(HasRequestedTask("putdown", a)){
        if(hold_id==a||plate_id==a) return true;
        else {
            cout<<"there is putdown task,no need to do this!"<<endl;
            return false;
        }
    }
    if(hold_id==a ||plate_id==a) return true;
    else return HoldSmallObject(a);
}

bool RDFW::SolveTask_PutDown(unsigned int a)
{
    if(HasRequestedTask("pickup", a)){
        if(hold_id!=a&&plate_id!=a) return true;
        else {
            cout<<"there is pickup task,no need to do this!"<<endl;
            return false;
        }
    }
    if(hold_id==a){
        if(putdown_cons[a][location]) {
            int safe_location = findrightlocation(a);
            if (safe_location == UNKNOWN || !Move(safe_location)) return false;
        }
        return PutDown(a);
    }
    else if(plate_id==a){
        if(hold_id>0) {
            if (!PutDown(hold_id)) return false;
            if(putdown_cons[a][location]) {
                int safe_location = findrightlocation(a);
                if (safe_location == UNKNOWN || !Move(safe_location)) return false;
            }
        }
        if (!FromPlate(a)) return false;
        if(putdown_cons[a][location]) {
            int safe_location = findrightlocation(a);
            if (safe_location == UNKNOWN || !Move(safe_location)) return false;
        }
       return PutDown(a);
    }
    else {
        auto small = dynamic_pointer_cast<SmallObject>(objects[a]);
        if (!small) return false;
        if (stage == 1 && small->inside == NONE) return true;
        if (stage == 2 && IsInsideVerified(a) && IsLocationVerified(a) && small->inside == NONE)
            return true;
        if (!HoldSmallObject(a)) return false;
        if (location < 0) return false;
        EnsureLocationCapacity(location);
        if (putdown_cons[a][location]) {
            int safe_location = findrightlocation(a);
            if (safe_location == UNKNOWN || !Move(safe_location)) return false;
        }
        return PutDown(a);
    }
}

//goto任务
bool RDFW::SolveTask_Goto(unsigned int a)
{
    if(stage==1)
    {
        if(location==objects[a]->location){
        return true;
    }
    else return Move(objects[a]->location);
    }

    //stage2的情况
    if(location==objects[a]->location && IsLocationVerified(a)) return true;
    const bool is_small = dynamic_pointer_cast<SmallObject>(objects[a]) != nullptr;
    if(objects[a]->location==UNKNOWN)
    {
        if(dynamic_pointer_cast<SmallObject>(objects[a]) != nullptr)
        {
               GetSmallObjectStatus(a);
               if(!IsKeepingGoing(task_index)) return 0;
        }
        else
        {
        GetBigObjectStatus(a);
        if(!IsKeepingGoing(task_index)) return 0;
        }
    }
    int t=0;
    while(1)
    {
        t++;
    if(location==objects[a]->location) {
        SenseCurrentLocationOnly(true);
        if (HasObjectAtLocation(location, a)) return true;
        auto small = dynamic_pointer_cast<SmallObject>(objects[a]);
        if (small && small->inside > 0 && HasObjectAtLocation(location, small->inside)) {
            MarkDirectLocationEvidence(a, true);
            return true;
        }
    }
    else if(!Move(objects[a]->location))
    {
          if(t>=2) return false;
          if(is_small) {GetSmallObjectStatus(a);if(!IsKeepingGoing(task_index)) return 0;}
          else {GetBigObjectStatus(a);if(!IsKeepingGoing(task_index)) return 0;}
    }
    else {
        SenseCurrentLocationOnly(true);
        if (HasObjectAtLocation(location, a)) return true;
        auto small = dynamic_pointer_cast<SmallObject>(objects[a]);
        if (small && small->inside > 0 && HasObjectAtLocation(location, small->inside)) {
            MarkDirectLocationEvidence(a, true);
            return true;
        }
        if(t>=2) return false;
        if(is_small) GetSmallObjectStatus(a); else GetBigObjectStatus(a);
    }
    }
    return false;
}

//open任务
bool RDFW::SolveTask_Open(unsigned int a)
{
    auto cnt=dynamic_pointer_cast<Container>(objects[a]);
    if(HasRequestedTask("close", a)){
        if(cnt->isOpen && (stage == 1 || IsContainerStateVerified(a))) return true;
        else {
            cout<<"there is close task,no need to do this!"<<endl;
            return false;
        }
    }
    if(cnt->isOpen && (stage == 1 || IsContainerStateVerified(a))) return true;
    if(hold_id!=NONE && !PutDown(hold_id)) return false;
    if(stage==1)
    {
        if (location != objects[a]->location && !Move(objects[a]->location)) return false;
        return Open(a);
    }

    //这是stage2
    if(objects[a]->location==UNKNOWN)
    {
        GetBigObjectStatus(a);
        if(!IsKeepingGoing(task_index)) return 0;
    }
     int t=0;
    while(1)
    {
        t++;
    if (location != objects[a]->location)
        if(!Move(objects[a]->location))
        {
            if(t>=2) return false;
            GetBigObjectStatus(a);
             if(!IsKeepingGoing(task_index)) return 0;
        }
    if(!Open(a))
    {
       if (sense(a)) {
            cnt->isOpen = true;
            EnsureEvidenceCapacity(a);
            containerStateVerified[a] = true;
            MarkDirectLocationEvidence(a, true);
            return true;
       }
       if(t>=2) return false;
            GetBigObjectStatus(a);
             if(!IsKeepingGoing(task_index)) return 0;
    }
    else return true;
    }
    return false;
}

//close任务
bool RDFW::SolveTask_Close(unsigned int a)
{
    auto cnt=dynamic_pointer_cast<Container>(objects[a]);
    if(HasRequestedTask("open", a))
    {
        if(!cnt->isOpen && (stage == 1 || IsContainerStateVerified(a))) return true;
        else {
            cout<<"there is open task,no need to do this!"<<endl;
            return false;
        }
    }
    if(!cnt->isOpen && (stage == 1 || IsContainerStateVerified(a))) return true;
    if(hold_id!=NONE && !PutDown(hold_id)) return false;
    if(stage==1)
    {
    if (location != objects[a]->location && !Move(objects[a]->location)) return false;
    return Close(a);
    }

   //这是stage2

   if(objects[a]->location==UNKNOWN)
    {
        GetBigObjectStatus(a);
        if(!IsKeepingGoing(task_index)) return 0;
    }
     int t=0;
    while(1)
    {
        t++;
    if (location != objects[a]->location)
        if(!Move(objects[a]->location))
        {
            if(t>=2) return false;
            GetBigObjectStatus(a);
             if(!IsKeepingGoing(task_index)) return 0;
        }
    if(!Close(a))
    {
       if (sense(a)) {
            cnt->isOpen = false;
            EnsureEvidenceCapacity(a);
            containerStateVerified[a] = true;
            MarkDirectLocationEvidence(a, true);
            return true;
       }
       if(t>=2) return false;
            GetBigObjectStatus(a);
             if(!IsKeepingGoing(task_index)) return 0;
    }
    else return true;
    }
    return false;
}

//give任务
bool RDFW::SolveTask_Give(unsigned int a)
  {
        if (human != nullptr){
            if(human->location==UNKNOWN)
             {
        GetBigObjectStatus(human->id);
        if(!IsKeepingGoing(task_index)) return 0;
        }
            if(objects[a]->location==human->location && plate_id!=a && hold_id!=a) return true;
            else return SolveTask_PutOn(a, human->id);
            }
        else
            LOG_ERROR("There are not human in Scene");

    return false;
}


//putin任务
bool RDFW::SolveTask_Putin(unsigned int a, unsigned int b)
{
    if(HasRequestedTask("takeout", a, b))
    {
        if(Isinside(a,b) && (stage == 1 || IsInsideVerified(a))) return true;
               else
               {
            cout<<"there is takeout task,no need to do this!"<<endl;
            return false;
               }
    }
    if(Isinside(a,b) && (stage == 1 || IsInsideVerified(a))) return true;
    auto target_cont = ObjectPtrCast<Container>(objects[b]);
    if(stage==1)
    {
        //优化了一下规划，如果目标物体和容器在一起，先打开再picku
        if(objects[a]->location==objects[b]->location)
        {
        if (location != target_cont->location && !Move(target_cont->location)) return false;
        if (target_cont->isOpen != 1 && !Open(b)) return false;
        if (!HoldSmallObject(a)) return false;
        return PutIn(a,b);
        }
        else
        {
        if(!HoldSmallObject(a)) return false;
        if (location != target_cont->location && !Move(target_cont->location)) return false;
        if (target_cont->isOpen != 1)
        {
        if (!PutDown(a)) return false;
        if (!Open(b)) return false;
        if (!PickUp(a)) return false;
        }
        return PutIn(a,b);
        }
       return false;
    }
    //stage2的情况
  //open如果false可能的情况有两种：1.容器本身就是开着的，他骗我没开 2.b容器就不在这个位置
  //putin a b 如果false的情况有两种： 1.容器是关着的，骗我是开着的，我没有打开 2.b容器就不在这个位置上
    if(objects[b]->location==UNKNOWN)
    {
        GetBigObjectStatus(b);
        if(!IsKeepingGoing(task_index)) return 0;
    }
    if(!HoldSmallObject(a)) return false;

    int try_times=0;
    while(1)
    {
      try_times++;
    if (location != target_cont->location)
        if(!Move(target_cont->location))
        {
            if(try_times>=2) return false;
            GetBigObjectStatus(b);
            if(!IsKeepingGoing(task_index)) return false;
            continue;
        }

    if (!target_cont->isOpen)
    {
        if (!PutDown(a)) return false;
        if(Open(b))
        {
             if (!PickUp(a)) return false;
             return PutIn(a,b);
        }
        else
        {
            if(sense(b)) {
                target_cont->isOpen = true;
                EnsureEvidenceCapacity(b);
                containerStateVerified[b] = true;
                if (!PickUp(a)) return false;
                return PutIn(a,b);
            }
            else
            {
            if(try_times>=2) return false;
            if (!PickUp(a)) return false;
            GetBigObjectStatus(b);
            if(!IsKeepingGoing(task_index)) return false;
            continue;
            }
        }

    }
    else
    {
    if(!PutIn(a, b))
    {
        if (!PutDown(a)) return false;
       if(Open(b)){
           if (!PickUp(a)) return false;
           return PutIn(a,b);
       }
       else
       {
        if(try_times>=2) return false;
        if (!PickUp(a)) return false;
        GetBigObjectStatus(b);
        if(!IsKeepingGoing(task_index)) return false;
        continue;
        }
    //    if(sense(b))
    //    {
    //     PutDown(hold_id);
    //     Open(b);
    //     PickUp(a);
    //     return PutIn(a,b);
    //    }
    //    else
    //    {
    //      if(try_times>=2) return false;
    //      GetBigObjectStatus(b);
    //      if(!IsKeepingGoing(task_index)) return false;
    //      continue;
    //    }
    }
    else return true;
    }
    }
}


//takeout任务
bool RDFW::SolveTask_TakeOut(unsigned int a, unsigned int b)
{
    if(HasRequestedTask("putin", a, b)){
         if(Isinside(a,b)==0) return true;
        else {
            cout<<"there is putin task,no need to do this!"<<endl;
            return false;
        }
    }
    auto small = ObjectPtrCast<SmallObject>(objects[a]);


    auto target_cont = ObjectPtrCast<Container>(objects[b]);
    // Stage 2 location facts and AskLoc replies may be misleading. A known
    // "at" reply therefore does not prove that the object is outside this
    // container; verify by trying the target container instead. Stage 1 has
    // reliable state and can keep the zero-cost shortcut.
    if (stage == 1 && small->inside != target_cont->id && small->inside != UNKNOWN)
    {
         return true;
    }


    if(stage==1)
    {
        if (hold!= nullptr && !PutDown(hold->id)) return false;
        if (location != target_cont->location && !Move(target_cont->location)) return false;
        if (target_cont->isOpen != 1 && !Open(target_cont->id)) return false;
        return TakeOut(a, target_cont->id);
    }
   ///这是stage2的逻辑 //对于takeout任务，inside未知，location未知，先去容器尝试takeout；或者先询问小物体，再判断任务是否已经完成
    if(target_cont->location==UNKNOWN){GetBigObjectStatus(b);if(!IsKeepingGoing(task_index)) return false;}
    if (hold!= nullptr && !PutDown(hold->id)) return false;
    int t = 0;
    while(1)
    {
        t++;
    if (location != target_cont->location)
        if(!Move(target_cont->location))
        {
        if (t >= 2)  return 0;
        GetBigObjectStatus(b);
        if(!IsKeepingGoing(task_index)) return false;
        continue;
        }
    TakeOutResult result = TakeOutLogic(a,b);
    if(result == TakeOutResult::Success) return true;
    else if(result == TakeOutResult::NeedContainerLocation) {if (t >= 2)  return 0;GetBigObjectStatus(b);}
    else if(result == TakeOutResult::NeedObjectLocation) {
        if (t >= 2) return false;
        GetSmallObjectStatus(a);
        if (!Isinside(a,b) && IsInsideVerified(a)) return true;
    }
    else if(result == TakeOutResult::VerifyObjectRelation)
    {
    if (t >= 2)  return 0;
    GetSmallObjectStatus(a);
    if(Isinside(a,b))//a就在一开始容器里面
    {
     if(Open(b)) return TakeOut(a,b); //认为骗我是关的
     else  GetBigObjectStatus(b);//open失败，本身不可能是open的，直接问容器
    }
    else
    {
    return true; //小物体不在容器里了
    }
    }
    if(!IsKeepingGoing(task_index)) return false;continue;
    }
}


//puton任务
bool RDFW::SolveTask_PutOn(unsigned int a, unsigned int b)
{
    //10.27
    auto small=dynamic_pointer_cast<SmallObject>(objects[a]);
    if(small && small->inside==NONE && small->location==objects[b]->location &&
       plate_id!=a && hold_id!=a &&
       (stage == 1 || (IsInsideVerified(a) && IsLocationVerified(a) && IsLocationVerified(b))))
        return true;
    //
    if(objects[b]->location==UNKNOWN)
    {
        GetBigObjectStatus(b);
         if(!IsKeepingGoing(task_index)) return false;
    }
    if (!HoldSmallObject(a)) return false;
    int t=0;
    while(1)
    {
        t++;
        if (location != objects[b]->location)
        {
            if(!Move(objects[b]->location))
            {
            if (t >= 3)  return 0;
            GetBigObjectStatus(b);
            if(!IsKeepingGoing(task_index)) return false;
            continue;
            }
        }
        if (stage == 2 && (!IsLocationVerified(b) || objects[b]->location != location)) {
            SenseCurrentLocationOnly(true);
            if(!HasObjectAtLocation(location, b)) {
                if (t >= 3) return false;
                GetBigObjectStatus(b);
                if(!IsKeepingGoing(task_index)) return false;
                continue;
            }
        }
        return PutDown(a);
    }
    return true;
}



/*============== b)mustchooseone ==============*/

//必须要做一个任务
void RDFW::MustChooseOne(void){
    if (StopGate("must-choose-one", true)) return;
    if(stage==1){
        cout<<"stage=1"<<endl;
        int flag=0;
         for(int i=0;i<tasks.size();i++){
                   if(tasks[i].risk<tasks[flag].risk){
                    flag=i;
                   }
               }
               task_index=flag;
               if (!CanStartPlan(tasks[task_index], "must-choose-one")) return;
               cout<<"Must Choose one:"<<tasks[flag].behave<<endl;
               if (SolveTask(tasks[task_index]))
                {
                    stringstream ss;
                    ss << tasks[task_index];
                    LOG(GREEN "Task done\n %s" RESET, ss.str().c_str());
                    SetSolvedTaskNum(solved_task_num + 1);
                    tasks[task_index].isEnable = false;
                    AfterSolveTask(tasks[task_index]);
                }
    }
    if(stage==2){
        cout<<"stage=2"<<endl;
        // —— 新增：若剩余启用的 goto ≥ 2，则不要在这里做选择（留给 Final-GOTO）
        size_t remain_goto = 0;
        for (auto &t : tasks) if (t.isEnable && t.behave == "goto") ++remain_goto;
        if (remain_goto >= 2) {
            LOG(YELLOW "[Defer] MustChooseOne returns early due to multi-goto=%zu\n" RESET, remain_goto);
            return;
        }
          int t=0;
        while(solved_task_num==0){
        int flag=0;

        t++;
        if (StopGate("must-choose-one", true)) return;
        for(int i=0;i<tasks.size();i++){
            // 跳过包含不存在物体的任务
            if (tasks[i].hasMissingObjects) {
                continue;
            }

                   if((tasks[i].ask_times==0?(double)tasks[i].risk/2:(tasks[i].is_cheat?1000:tasks[i].risk))
                        <(tasks[flag].ask_times==0?(double)tasks[flag].risk/2:(tasks[flag].is_cheat?1000:tasks[flag].risk))){
                    flag=i;
                   }
               }
                task_index=flag;
               if (!CanStartPlan(tasks[task_index], "must-choose-one")) return;
               cout<<"Must Choose one:"<<tasks[flag].behave<<endl;
               if(t>3){
                SolveTask(tasks[flag]);
                break;
               }
               if(tasks[flag].risk>=4){   //怀疑是否有陷阱
             if(tasks[flag].behave!="open"||tasks[flag].behave!="close") {
                 if (!tasks[flag].X.empty()) {
                     GetSmallObjectStatus(tasks[flag].X[0]->id);
                 }
             }
                if(IsKeepingGoing(flag)!=1) continue;
               }
               if(tasks[flag].isfalse) {
                if (!tasks[flag].X.empty()) {
                    GetSmallObjectStatus(tasks[flag].X[0]->id);
                }
                if(IsKeepingGoing(flag)!=1) continue;
               }

            // ===【新增】零动作预验证：先试；失败(含 fake)立刻回落到 SolveTask ===
            bool zero_ok = ZeroActionPreCheck(tasks[task_index]);
            if (zero_ok) {
                std::stringstream ss; ss << tasks[task_index];
                LOG(GREEN "Task done (zero-action prevalidated)\n %s" RESET, ss.str().c_str());
                SetSolvedTaskNum(solved_task_num + 1);
                tasks[task_index].isEnable = false;
                AfterSolveTask(tasks[task_index]);
                break;
            }

            if (SolveTask(tasks[task_index]))
                {
                    stringstream ss;
                    ss << tasks[task_index];
                    LOG(GREEN "Task done\n %s" RESET, ss.str().c_str());
                    SetSolvedTaskNum(solved_task_num + 1);
                    tasks[task_index].isEnable = false;
                    AfterSolveTask(tasks[task_index]);
                    break;
                }
        }
    }
}




/**============== 附：goto任务处理============== */

//检查是否有多goto任务
bool RDFW::CheckAndDeferMultiGoto()
{
    size_t goto_count_enabled = 0;
    for (auto &t : tasks) if (t.behave == "goto") ++goto_count_enabled;
    const bool defer_multi_goto = (goto_count_enabled >= 2);
    if (defer_multi_goto)
        LOG(YELLOW "[Defer] multi-goto detected: %zu tasks; skip in main loop, handle at final aggregation\n" RESET, goto_count_enabled);
    return defer_multi_goto;
}

//执行多goto任务
void RDFW::ExecuteMultiGotoAggregation()
{
    // =========================
    // [FINAL] Multi-GOTO 聚合（低风险 hub + 候选筛选 + 上限 10 + 最终停留）
    // =========================

    LogProgressSnapshot("multi-goto");
    const TerminalSummary terminal = terminal_checker.evaluateAll(*this);
    if (terminal.allGoalsSatisfied() || deadline_manager.deadlineReached()) {
        normal_stop_requested = true;
        LOG(GREEN "[3A][StopGate] multi-goto not started: terminal/deadline condition\n" RESET);
        return;
    }
    const std::chrono::milliseconds estimate = EstimateMultiGotoTime();
    if (!deadline_manager.canFinish(estimate, plan_safety_margin)) {
        normal_stop_requested = true;
        LOG(YELLOW "[3A][StopGate] multi-goto not started: estimate=%lldms, "
                   "safety=%lldms, remaining=%lldms\n" RESET,
            static_cast<long long>(estimate.count()),
            static_cast<long long>(plan_safety_margin.count()),
            static_cast<long long>(deadline_manager.remaining().count()));
        return;
    }

    // 确保多goto模式标志已设置，跳过Sense操作
    isMultiGotoMode = true;
    LOG(GREEN "[MultiGoto] Executing multi-goto aggregation - skipping Sense operations\n" RESET);

    // 1) 收集启用中的 goto 任务对应的小物体
    // 分类收集 goto 任务中的大物体和小物体
    std::vector<unsigned> small_cand_ids;
    std::vector<unsigned> big_cand_ids;

    std::vector<unsigned> small_cand_ids_disable;
    small_cand_ids.reserve(32);
    big_cand_ids.reserve(32);
    for (auto &t : tasks) {
        if(t.behave == "goto"){
            if(t.isEnable){
                for (auto &x : t.X) {
                    if (std::dynamic_pointer_cast<SmallObject>(x))
                        small_cand_ids.push_back(x->id);
                    else if (std::dynamic_pointer_cast<BigObject>(x))
                        big_cand_ids.push_back(x->id);}
                }else{
                    for (auto &x : t.X) {
                        if (std::dynamic_pointer_cast<SmallObject>(x))
                            small_cand_ids_disable.push_back(x->id);
                    }
                }
            }
        }


    // 删掉small_cand_ids_disable中goto约束大于2的小物体
    small_cand_ids_disable.erase(
        std::remove_if(
            small_cand_ids_disable.begin(),
            small_cand_ids_disable.end(),
            [&](unsigned id) {
                int loc = (objects[id] ? objects[id]->location : UNKNOWN);
                int risk = (loc != UNKNOWN && loc >= 0) ? goto_cons[loc] : 99;
                return risk > 2;
            }
        ),
        small_cand_ids_disable.end()
    );


    /*不需要去重，不能有重复的任务---比赛规则
    // 去重
    std::sort(small_cand_ids.begin(), small_cand_ids.end());
    small_cand_ids.erase(std::unique(small_cand_ids.begin(), small_cand_ids.end()), small_cand_ids.end());
    std::sort(big_cand_ids.begin(), big_cand_ids.end());
    big_cand_ids.erase(std::unique(big_cand_ids.begin(), big_cand_ids.end()), big_cand_ids.end());
    // 计算每个小物体：去到其位置 + 拿起小物体 + 移动小物体违反的约束值（不考虑能否移动到 hub）
    // 如果小物体有 near 约束（即 near_cons[id] > 0），则视为不能移动，风险值设为极大
    */


    // 得到约束值小于2的小物体
    struct SmallGotoPickupInfo {
        unsigned id;
        int goto_risk = 0;      // 去到小物体位置的约束
        int pickup_risk = 0;    // 拿起小物体的约束
        int mustnear_risk = 0;  // mustnear 约束
        int total_risk = 0;     // 总约束
        bool can_move = true;   // 是否能移动
    };
    std::vector<SmallGotoPickupInfo> small_goto_infos;
    std::vector<unsigned> small_lowrisk_ids; // 约束值小于2的小物体id
    // 小物体：计算 goto/pickup/mustnear
    for (auto id : small_cand_ids) {
        SmallGotoPickupInfo info;
        info.id = id;
        // 2. 去到小物体当前位置
        int loc = (objects[id] ? objects[id]->location : UNKNOWN);
        info.goto_risk = (loc != UNKNOWN && loc >= 0) ? goto_cons[loc] : 99;
        // 3. 拿起小物体的约束
        info.pickup_risk = pickup_cons[id];
        // 4. mustnear 约束（第二维同样是对象 id，不是位置）
        int mustnear_sum = 0;
        for (int i = 0; i < (int)mustnear_cons[id].size(); ++i) mustnear_sum += mustnear_cons[id][i];
        info.mustnear_risk = mustnear_sum;
        // 5. 总约束
        info.total_risk = info.goto_risk + info.pickup_risk + info.mustnear_risk;
        info.can_move = (info.total_risk < 2);
        LOG(GREEN "[MultiGoto] Object[%u]: goto_risk=%d, pickup_risk=%d, mustnear_risk=%d, total_risk=%d, can_move=%s\n" RESET,
            id, info.goto_risk, info.pickup_risk, info.mustnear_risk, info.total_risk, info.can_move ? "true" : "false");
        if (info.total_risk < 3) {
            small_lowrisk_ids.push_back(id);
        }
        small_goto_infos.push_back(info);
    }
    // 大物体：仅统计 goto 约束值
    struct BigGotoInfo {
        unsigned id;
        int goto_risk = 0;
    };
    std::vector<BigGotoInfo> big_goto_infos;
    for (auto id : big_cand_ids) {
        BigGotoInfo info;
        info.id = id;
        int loc = (objects[id] ? objects[id]->location : UNKNOWN);
        info.goto_risk = (loc != UNKNOWN && loc >= 0) ? goto_cons[loc] : 99;
        LOG(GREEN "[MultiGoto] BigObject[%u]: goto_risk=%d\n" RESET, id, info.goto_risk);
        big_goto_infos.push_back(info);
    }


    LOG(GREEN "[MultiGoto] small_cand_id_disable: ");
    for(auto id : small_cand_ids_disable){
        LOG(GREEN "%u ", id);
    }
    LOG(GREEN "\n" RESET);
    LOG(GREEN "[MultiGoto] small_cand_ids: ");
    for(auto id : small_cand_ids){
        LOG(GREEN "%u ", id);
    }
    LOG(GREEN "\n" RESET);
    LOG(GREEN "[MultiGoto] big_cand_ids: ");
    for(auto id : big_cand_ids){
        LOG(GREEN "%u ", id);
    }
    LOG(GREEN "\n" RESET);
    LOG(GREEN "[MultiGoto] small_cand_ids.size()=%zu, big_cand_ids.size()=%zu\n" RESET,
        small_cand_ids.size(), big_cand_ids.size());
    LOG(GREEN "[MultiGoto] small_lowrisk_ids.size()=%zu\n" RESET, small_lowrisk_ids.size());

    if(small_lowrisk_ids.size()>0 || big_cand_ids.size()>0){
        LOG(GREEN "[MultiGoto] Entering main aggregation logic\n" RESET);

    // 只收集有物体的位置，避免遍历所有空位置
    std::set<int> occupied_locations;

    // 收集所有小物体和大物体的位置
    for (auto id : small_lowrisk_ids) {
        if (id < objects.size() && objects[id]) {
            int loc = objects[id]->location;
            if (loc >= 0 && loc < (int)rightlocation.size()) {
                occupied_locations.insert(loc);
            }
        }
    }
    for (auto id : big_cand_ids) {
        if (id < objects.size() && objects[id]) {
            int loc = objects[id]->location;
            if (loc >= 0 && loc < (int)rightlocation.size()) {
                occupied_locations.insert(loc);
            }
        }
    }
    for (auto id : small_cand_ids_disable) {
        if (id < objects.size() && objects[id]) {
            int loc = objects[id]->location;
            if (loc >= 0 && loc < (int)rightlocation.size()) {
                occupied_locations.insert(loc);
            }
        }
    }

    // 转换为vector，只包含有物体的位置
    std::vector<int> valid_locations(occupied_locations.begin(), occupied_locations.end());

    LOG(GREEN "[MultiGoto] Performance optimization: Only checking %zu occupied locations instead of %zu total locations\n" RESET,
        valid_locations.size(), rightlocation.size());

    // 记录每个位置的约束统计
    struct LocationRiskInfo {
        int loc;
        int goto_risk;
        std::vector<int> move_cons_risks;     // 对每个小物体
        std::vector<int> putdown_cons_risks;  // 对每个小物体
        int total_risk;
    };
    std::vector<LocationRiskInfo> location_risks;

    for (int loc : valid_locations) {
        LocationRiskInfo info;
        info.loc = loc;
        info.goto_risk = goto_cons[loc];
        info.move_cons_risks.reserve(small_lowrisk_ids.size());
        info.putdown_cons_risks.reserve(small_lowrisk_ids.size());
        int sum_risk = info.goto_risk;
        for (auto id : small_lowrisk_ids) {
            int move_risk = move_cons[id][loc];
            int putdown_risk = putdown_cons[id][loc];
            info.move_cons_risks.push_back(move_risk);
            info.putdown_cons_risks.push_back(putdown_risk);
            sum_risk += move_risk + putdown_risk;
        }
        info.total_risk = sum_risk;
        location_risks.push_back(info);
    }

    // 1. 选出约束值小于3且可达的位置
    std::vector<int> low_risk_locs;
    int min_risk = 1000000;
    for (const auto& info : location_risks) {
        // 检查位置是否可达（在rightlocation中且不是UNKNOWN）
        if (info.loc >= 0 && info.loc < (int)rightlocation.size() && rightlocation[info.loc]) {
            if (info.total_risk < 3) {
                low_risk_locs.push_back(info.loc);
            }
            if (info.total_risk < min_risk) {
                min_risk = info.total_risk;
            }
        }
    }

    // 统计选出来的小物体在每个位置的数量（只统计有物体的位置）
    std::map<int, int> location_smallobjloc_counts;
    // 合并两个vector
    std::vector<unsigned int> combined_ids = small_lowrisk_ids;
    combined_ids.insert(combined_ids.end(), small_cand_ids_disable.begin(), small_cand_ids_disable.end());

    for (auto id : combined_ids) {
        if (id < objects.size() && objects[id]) {
            int loc = objects[id]->location;
            if (loc >= 0 && loc < (int)rightlocation.size()) {
                location_smallobjloc_counts[loc]++;
            }
        }
    }

    int chosen_loc = -1;

    // 优先选择大物体中约束值最小且小于2的位置，若没有，选择约束值最小的位置
    int best_big_risk = 1000000;
    int best_big_loc = -1;

    // 直接使用小物体聚集数量大于2且数量最多的位置作为 chosen_loc

    int most_smallobj_loc = -1;
    int most_smallobj_count = 0;


    for (const auto& pair : location_smallobjloc_counts) {
        int loc = pair.first;
        int count = pair.second;
        if (count >= 2) {
            cout << "[MultiGoto] location " << loc << " has " << count << " small objects" << endl;
            // 找到对应的location_risks信息
            int total_risk = 99; // 默认高风险
            for (const auto& risk_info : location_risks) {
                if (risk_info.loc == loc) {
                    total_risk = risk_info.total_risk;
                    break;
                }
            }
            if (count > most_smallobj_count && (count - total_risk) > 2) {
                // 检查位置可达
                if (loc >= 0 && loc < (int)rightlocation.size()) {
                    most_smallobj_count = count;
                    most_smallobj_loc = loc;
                    cout << "[MultiGoto] most_smallobj_loc " << most_smallobj_loc << endl;
                }
            }
        }
    }


    if (most_smallobj_loc != -1) {
        chosen_loc = most_smallobj_loc;
        rightlocation[chosen_loc] = true;
        LOG(YELLOW "[MultiGoto] smallobj_loc is found: %d\n" RESET, most_smallobj_loc);
    }
    else{
        LOG(YELLOW "[MultiGoto] smallobj_loc is not found: %d\n" RESET, most_smallobj_loc);
    }


    // 1. 在 big_cand_ids 中找约束值最小且小于2的位置

    if(chosen_loc == -1){
    for (auto big_id : big_cand_ids) {
        if (objects[big_id]) {
            int loc = objects[big_id]->location;
            // 确保位置可达
            if (loc >= 0 && loc < (int)rightlocation.size() && rightlocation[loc]) {
                for (const auto& info : location_risks) {
                    if (info.loc == loc && info.total_risk < 2) {
                        if (info.total_risk < best_big_risk) {
                            best_big_risk = info.total_risk;
                            best_big_loc = loc;}
                            }
                        }
                    }
                }
            }
        }


    if (best_big_loc != -1 ) {
        chosen_loc = best_big_loc;
    }
    else if(chosen_loc == -1){
        LOG(YELLOW "[MultiGoto] bigobj_loc is not found: %d\n" RESET, best_big_loc);
        // 没有满足条件的大物体位置，选择所有可达位置中约束值最小的位置
        int best_risk = 1000000;
        for (const auto& info : location_risks) {
            // 确保位置可达
            if (info.loc >= 0 && info.loc < (int)rightlocation.size() && rightlocation[info.loc]) {
                if (info.total_risk < best_risk) {
                    best_risk = info.total_risk;
                    chosen_loc = info.loc;
                }
            }
        }
        LOG(YELLOW "[MultiGoto] No optimal location found, using first available: %d\n" RESET, chosen_loc);
    }

    // 如果仍然没有选择到位置，选择第一个可达的位置
    if (chosen_loc == -1) {
        for (int loc = 0; loc < (int)rightlocation.size(); ++loc) {
            if (rightlocation[loc]) {
                chosen_loc = loc;
                LOG(YELLOW "[MultiGoto] No optimal location found, using first available: %d\n" RESET, loc);
                break;
            }
        }
    }


    // 验证选择的位置是否可达
    if (chosen_loc == -1 || !rightlocation[chosen_loc]) {
        LOG(RED "[MultiGoto] ERROR: No valid location found! chosen_loc=%d, rightlocation[%d]=%d\n" RESET,
            chosen_loc, chosen_loc, chosen_loc >= 0 && chosen_loc < (int)rightlocation.size() ? rightlocation[chosen_loc] : -1);
        // 选择机器人当前位置作为备选
        chosen_loc = location;
        LOG(YELLOW "[MultiGoto] Using current location as fallback: %d\n" RESET, chosen_loc);
    }

    LOG(GREEN "Final-GOTO: choose hub=%d\n" RESET,chosen_loc);

        // 4) 两层过滤得到最终搬运集合 move_set
        std::vector<unsigned> move_set;
        move_set.reserve(small_lowrisk_ids.size());

        // 使用 small_lowrisk_ids 作为搬运集合
        for (auto id : small_lowrisk_ids) {
            // 重新定义lambda函数，因为作用域问题
            auto ViolationsIfGoto = [&](unsigned id) -> int {
                if (id >= objects.size() || !objects[id]) return 99;
                int loc = objects[id]->location;
                if (loc == UNKNOWN || loc < 0) return 99;
                return goto_cons[loc];
            };
            auto SafeForIdAt = [&](unsigned id, int h) -> bool {
                if (h < 0) return false;
                return putdown_cons[id][h] == 0 && move_cons[id][h] == 0;
            };
            if (ViolationsIfGoto(id) < 2 && SafeForIdAt(id, chosen_loc)) {
                move_set.push_back(id);
            }
        }

        // 没有可搬的，就至少停在 chosen_loc
        if (move_set.empty()) {
            if (location != chosen_loc &&
                deadline_manager.canFinish(std::chrono::milliseconds(300),
                                           plan_safety_margin)) {
                Move(chosen_loc);
            }
        } else {
            auto in_set = [&](unsigned x){
                return std::find(move_set.begin(), move_set.end(), x) != move_set.end();
            };

            // 护栏：hold/plate 不在集合且跨区会触发 move 约束时，先就地处理
            if (hold_id > 0 && !in_set(hold_id) && move_cons[hold_id][chosen_loc]) {
                PutDown(hold_id);
            }
            if (plate_id > 0 && !in_set(plate_id) && move_cons[plate_id][chosen_loc]) {
                if (hold_id > 0) PutDown(hold_id);
                FromPlate(plate_id);
                PutDown(plate_id);
            }

            // 若 hold/plate 在集合里，优先处理
            auto promote_front = [&](unsigned x){
                auto it = std::find(move_set.begin(), move_set.end(), x);
                if (it != move_set.end()) std::rotate(move_set.begin(), it, it + 1);
            };
            if (hold_id  > 0) promote_front(hold_id);
            if (plate_id > 0) promote_front(plate_id);

            // 已在 chosen_loc 的优先，其余按 id 升序
            std::stable_sort(move_set.begin(), move_set.end(), [&](unsigned a, unsigned b){
                auto sa = std::dynamic_pointer_cast<SmallObject>(objects[a]);
                auto sb = std::dynamic_pointer_cast<SmallObject>(objects[b]);
                int da = (sa && sa->location == chosen_loc) ? 0 : 1;
                int db = (sb && sb->location == chosen_loc) ? 0 : 1;
                return (da != db) ? (da < db) : (a < b);
            });

            // 实际搬运 ≤ 10 件
            const int MULTI_GOTO_LIMIT = 500;
            int moved = 0;
            int try_times = 0;
            for (unsigned id : move_set) {
                if (moved >= MULTI_GOTO_LIMIT) break;
                if (!deadline_manager.canFinish(std::chrono::milliseconds(1000),
                                                plan_safety_margin)) {
                    LOG(YELLOW "[3A][StopGate] stop multi-goto candidates: "
                               "estimate=1000ms, remaining=%lldms\n" RESET,
                        static_cast<long long>(deadline_manager.remaining().count()));
                    break;
                }
                // 直接调用 SolveTask_PutOn ，把小物体移动到 hub
                if (SolveTask_PutOn(id, chosen_loc)) {
                    ++moved;
                    LOG(GREEN "Final-GOTO: moved obj[%u] to hub=%d (%d/%d) (via SolveTask_PutOn)\n" RESET,
                        id, chosen_loc, moved, MULTI_GOTO_LIMIT);
                }
            }

            // 收尾：最终停在 chosen_loc
            if (location != chosen_loc &&
                deadline_manager.canFinish(std::chrono::milliseconds(300),
                                           plan_safety_margin)) {
                Move(chosen_loc);
            }
            LOG(GREEN "Final-GOTO: aggregation done, stay at hub=%d\n" RESET, chosen_loc);

            // 关闭剩余 goto，避免后续检查阶段拉走
            for (auto &t : tasks) {
                if (t.isEnable && t.behave == "goto") t.isEnable = false;
            }
        }
    } else {
        LOG(YELLOW "[MultiGoto] Skipping aggregation: small_lowrisk_ids.size()=%zu, big_cand_ids.size()=%zu\n" RESET,
            small_lowrisk_ids.size(), big_cand_ids.size());
    }
    // =========================
    // [FINAL] Multi-GOTO 聚合结束
    // =========================
    LOG(GREEN "[MultiGoto] ExecuteMultiGotoAggregation finished\n" RESET);
}



// === Zero-Action Precheck helpers (stage2 only) ===

// 判定当前知识下，该任务是否“无需执行器动作即可满足”
bool RDFW::IsZeroActionSatisfy(const Instruction& t) const
{
    return stage == 2 &&
           terminal_checker.evaluateTask(*this, t) == TerminalStatus::SATISFIED;
}

// 零动作检查必须是纯检查：不得 Ask、Sense、Move 或改变场景。
bool RDFW::ZeroActionPreCheck(Instruction& t)
{
    if (stage != 2) return false;
    if (IsZeroActionSatisfy(t)) {
        stringstream ss; ss << t;
        LOG(GREEN "[Zero-Action] validated as done\n %s" RESET, ss.str().c_str());
        return true;
    }
    return false;
}
// === Zero-Action Precheck helpers (stage2 only) ===




/**============== b)状态判断函数============== */
//小物体、大物体、询问、Sense、inside判断、IsKeepingGoing、IsObjectSatisfy、IsInstructionInvoke、SearchConditionObject


namespace {
bool ParseAskLocationReply(const string& reply, unsigned int expected_id,
                           string& relation, unsigned int& target)
{
    static const regex pattern(
        "^\\s*(at|inside)\\s*\\(\\s*([0-9]+)\\s*,\\s*([0-9]+)\\s*\\)\\s*$");
    smatch match;
    if (!regex_match(reply, match, pattern) || match.size() != 4) return false;
    try {
        const unsigned long reply_id = stoul(match[2].str());
        const unsigned long reply_target = stoul(match[3].str());
        if (reply_id != expected_id) return false;
        relation = match[1].str();
        target = static_cast<unsigned int>(reply_target);
        return true;
    } catch (const exception&) {
        return false;
    }
}
}

// 获取小物体状态。AskLoc 只用于提出待验证的位置假设，因此遇到第一个
// 格式正确的回答即可继续；最多额外重试一次 not_known/非法回答。
bool RDFW::GetSmallObjectStatus(unsigned int a)
{
    if (isPass || a == 0 || a >= objects.size() || !objects[a]) return false;
    auto small = dynamic_pointer_cast<SmallObject>(objects[a]);
    if (!small) return false;

    const int max_attempts = 2;
    string chosen_relation;
    unsigned int chosen_target = 0;
    bool chosen = false;

    for (int attempt = 0; attempt < max_attempts; ++attempt) {
        const string reply = AskLoc(a);
        string relation;
        unsigned int target = 0;
        if (!ParseAskLocationReply(reply, a, relation, target)) continue;
        if (relation == "inside") {
            if (target == 0 || target >= objects.size() || !objects[target] ||
                !dynamic_pointer_cast<Container>(objects[target])) continue;
        } else if (target < posSensedFlag.size() && posSensedFlag[target] &&
                   !HasObjectAtLocation(static_cast<int>(target), a)) {
            continue;
        }
        chosen_relation = relation;
        chosen_target = target;
        chosen = true;
        break;
    }
    if (!chosen) {
        LOG(YELLOW "AskLoc(%u) produced no usable bounded reply\n" RESET, a);
        return false;
    }

    if (small->inside > 0 && static_cast<size_t>(small->inside) < objects.size()) {
        auto old_cont = dynamic_pointer_cast<Container>(objects[small->inside]);
        if (old_cont) old_cont->DeleteObjectInside(small);
    }

    if (chosen_relation == "inside") {
        auto cont = dynamic_pointer_cast<Container>(objects[chosen_target]);
        if (!cont) return false;
        if (cont->location == UNKNOWN) GetBigObjectStatus(cont->id);
        small->location = cont->location;
        small->inside = cont->id;
        bool already_listed = false;
        for (const auto& item : cont->smallObjectsInside) {
            if (item && item->id == small->id) { already_listed = true; break; }
        }
        if (!already_listed) cont->smallObjectsInside.push_back(small);
    } else {
        EnsureLocationCapacity(static_cast<int>(chosen_target));
        small->location = static_cast<int>(chosen_target);
        small->inside = NONE;
    }

    MarkDirectLocationEvidence(a, false);
    objectInsideVerified[a] = false;
    if (small->location >= 0) {
        EnsureLocationCapacity(small->location);
        posCorrectFlag[small->location] = false;
    }
    RefreshMustNearConstraintState(false);
    return true;
}

// 获取大物体状态。只接受格式正确且对象 ID 匹配的 at 回答。
bool RDFW::GetBigObjectStatus(unsigned int a)
{
    if (isPass || a == 0 || a >= objects.size() || !objects[a]) return false;
    const int max_attempts = 2;
    unsigned int chosen_location = 0;
    bool chosen = false;

    for (int attempt = 0; attempt < max_attempts; ++attempt) {
        const string reply = AskLoc(a);
        string relation;
        unsigned int target = 0;
        if (!ParseAskLocationReply(reply, a, relation, target) || relation != "at") continue;
        if (target < posSensedFlag.size() && posSensedFlag[target] &&
            !HasObjectAtLocation(static_cast<int>(target), a)) continue;
        chosen_location = target;
        chosen = true;
        break;
    }
    if (!chosen) {
        LOG(YELLOW "AskLoc(%u) produced no usable bounded location reply\n" RESET, a);
        return false;
    }

    EnsureLocationCapacity(static_cast<int>(chosen_location));
    objects[a]->location = static_cast<int>(chosen_location);
    if (auto cont = dynamic_pointer_cast<Container>(objects[a])) {
        for (const auto& item : cont->smallObjectsInside) {
            if (item) item->location = cont->location;
        }
    }
    MarkDirectLocationEvidence(a, false);
    posCorrectFlag[chosen_location] = false;
    RefreshMustNearConstraintState(false);
    return true;
}

// 单次询问。重试与一致性判断由调用方控制，保证每条调用链都有明确上限。
std::string RDFW::AskLoc(unsigned int a)
{
    if (isPass || a == 0 || a >= objects.size() || !objects[a]) return "";
    score_evaluator.recordAction(ActionCategory::HUMAN_INTERACTION);
    const string str = Plug::AskLoc(a);
    if (task_index >= 0 && static_cast<size_t>(task_index) < tasks.size())
        tasks[task_index].ask_times++;
    LOG("AskLoc(%d)", a);
    if (str.empty())
        LOG_ERROR("AskLoc returned empty string for object (%d,%s)", a, objects[a]->sort.c_str());
    return str;
}

//感知位置---只能判断是否有这个物体，容器中的物体感知不到
void RDFW::Sense()
{
    if(stage==1 || isPass) return;
    // Sense 只观察当前位置，不应把 location 当作对象 ID，也不应隐式开关门。
    SenseCurrentLocationOnly(true);
}


// 只感知当前位置的物体，并更新其感知位置
void RDFW::SenseCurrentLocationOnly(bool force)
{
    unsigned int sensed_container_id = NONE;
    // 获取当前位置
    int curr_loc = location;
    if (curr_loc < 0) return;

    // 检查位置是否已经感知过，避免重复感知
    if (curr_loc >= posSensedFlag.size()) {
        posSensedFlag.resize(curr_loc + 1, false);
        locationSensedObjects.resize(curr_loc + 1);  // 同时扩展物体记录数组
    }

    if (!force && posSensedFlag[curr_loc]) {
        LOG(YELLOW "[SenseCurrentLocationOnly] Location %d already sensed, skipping to avoid redundancy\n" RESET, curr_loc);
        return;
    }

    // 感知当前位置的物体
    vector<unsigned int> sensed_ids;
    score_evaluator.recordAction(ActionCategory::OBSERVATION);
    Plug::Sense(sensed_ids);

    // 标记当前位置已感知
    if (curr_loc >= posSensedFlag.size()) {
        posSensedFlag.resize(curr_loc + 1, false);
        locationSensedObjects.resize(curr_loc + 1);  // 同时扩展物体记录数组
    }
    posSensedFlag[curr_loc] = true;

    // 清空当前位置的感知记录，准备记录新的感知结果
    locationSensedObjects[curr_loc].object_ids.clear();
    locationSensedObjects[curr_loc].container_id = 0;
    locationSensedObjects[curr_loc].has_container = false;

    LOG(GREEN "[SenseCurrentLocationOnly] Location %d marked as sensed\n" RESET, curr_loc);

    // 遍历感知到的物体，更新其位置
    for (auto id : sensed_ids) {
        if (id > 0 && id < objects.size() && objects[id] != nullptr) {
            objects[id]->location = curr_loc;
            MarkDirectLocationEvidence(id, true);
            if (objects[id]->unable_site == curr_loc) objects[id]->unable_site = UNKNOWN;

            // 记录感知到的物体ID
            locationSensedObjects[curr_loc].object_ids.push_back(id);

            auto cont = std::dynamic_pointer_cast<Container>(objects[id]);
            if (cont) {
                // 记录容器ID和标记有容器（一个位置只能有一个大物体）
                locationSensedObjects[curr_loc].container_id = id;
                locationSensedObjects[curr_loc].has_container = true;
                sensed_container_id = id;
                LOG("[SenseCurrentLocationOnly] Container %d detected at location %d", id, curr_loc);
            } else {
                LOG("[SenseCurrentLocationOnly] Object %d detected at location %d", id, curr_loc);
            }
        }
    }

    // 让位置证据与 inside 关系保持一致。开放容器与其内容同时可见时，
    // 单次 Sense 无法区分“在容器内”和“在容器旁”，因此只清理能够
    // 确定矛盾的旧关系，不把歧义状态升级为已验证。
    for (auto id : sensed_ids) {
        if (id == 0 || id >= objects.size() || !objects[id]) continue;
        auto small = dynamic_pointer_cast<SmallObject>(objects[id]);
        if (!small || static_cast<int>(id) == hold_id || static_cast<int>(id) == plate_id) continue;
        EnsureEvidenceCapacity(id);

        bool visible_container_is_open = false;
        if (sensed_container_id > 0 && sensed_container_id < objects.size()) {
            auto visible_container = dynamic_pointer_cast<Container>(objects[sensed_container_id]);
            visible_container_is_open = visible_container && visible_container->isOpen;
        }

        const bool relation_is_ambiguous =
            small->inside == static_cast<int>(sensed_container_id) && visible_container_is_open;
        if (relation_is_ambiguous) {
            objectInsideVerified[id] = false;
            continue;
        }

        if (small->inside > 0 && static_cast<size_t>(small->inside) < objects.size()) {
            auto old_container = dynamic_pointer_cast<Container>(objects[small->inside]);
            if (old_container) old_container->DeleteObjectInside(small);
        }
        small->inside = NONE;
        objectInsideVerified[id] = true;
    }

    // 检查原本应该在这个位置但没被感知到的物体
    // 1. 标记已感知到的物体（包括容器内的物体）
    std::vector<bool> sensed(objects.size(), false);
    for (auto id2 : locationSensedObjects[curr_loc].object_ids) {
        if (id2 > 0 && id2 < objects.size() && objects[id2] != nullptr) {
            sensed[id2] = true;
        }
    }

    // 2.检查这个容器是否开着
    bool container_is_open = false;
    if (sensed_container_id > 0 && sensed_container_id < objects.size() && objects[sensed_container_id] != nullptr) {
        auto cont = std::dynamic_pointer_cast<Container>(objects[sensed_container_id]);
        if (cont) {
            container_is_open = cont->isOpen;
        }
    }

    // 直接按照位置找，找到标记为在这个位置的所谓物体id
    std::vector<unsigned int> ids_at_curr_loc;
    for (unsigned int i = 1; i < objects.size(); ++i) {
        if (!objects[i]) continue;
        if (static_cast<int>(i) == hold_id || static_cast<int>(i) == plate_id) continue;
        if (objects[i]->location == curr_loc) {
            ids_at_curr_loc.push_back(i);
        }
    }

    if(sensed_container_id == NONE || container_is_open == true){
        for (auto id : ids_at_curr_loc) {
            if (!sensed[id]) {
                objects[id]->location = UNKNOWN;
                MarkDirectLocationEvidence(id, false);
                objects[id]->unable_site = curr_loc;
                LOG(YELLOW "[SenseCurrentLocationOnly] Object id=%u expected at %d but not sensed, set location UNKNOWN\n" RESET, id, curr_loc);
            }
        }
    }
    else{
        for (auto id : ids_at_curr_loc) {
            bool in_container = false;
            // 检查是否是小物体且在容器内
            auto small = std::dynamic_pointer_cast<SmallObject>(objects[id]);
            if (small && small->inside == sensed_container_id) {
                in_container = true;
            }

            if (!sensed[id] && !in_container) {
                objects[id]->location = UNKNOWN;
                MarkDirectLocationEvidence(id, false);
                objects[id]->unable_site = curr_loc;
                LOG(YELLOW "[SenseCurrentLocationOnly] Object id=%u expected at %d but not sensed, set location UNKNOWN\n" RESET, id, curr_loc);
            }
        }
    }
    RefreshMustNearConstraintState(true);
}
// 位置感知物体记录访问函数实现
const RDFW::LocationSensedInfo& RDFW::GetLocationSensedInfo(int location) const {
    static RDFW::LocationSensedInfo empty_info;  // 返回空结构体作为默认值
    if (location >= 0 && location < locationSensedObjects.size()) {
        return locationSensedObjects[location];
    }
    return empty_info;
}

bool RDFW::HasObjectAtLocation(int location, unsigned int object_id) const {
    if (location >= 0 && location < locationSensedObjects.size()) {
        const auto& info = locationSensedObjects[location];
        for (auto id : info.object_ids) {
            if (id == object_id) return true;
        }
    }
    return false;
}

bool RDFW::HasContainerAtLocation(int location) const {
    if (location >= 0 && location < locationSensedObjects.size()) {
        return locationSensedObjects[location].has_container;
    }
    return false;
}

vector<unsigned int> RDFW::GetObjectsAtLocation(int location) const {
    if (location >= 0 && location < locationSensedObjects.size()) {
        return locationSensedObjects[location].object_ids;
    }
    return vector<unsigned int>();
}

unsigned int RDFW::GetContainerAtLocation(int location) const {
    if (location >= 0 && location < locationSensedObjects.size()) {
        return locationSensedObjects[location].container_id;
    }
    return 0;
}


//感知大物体是否在当前位置
bool RDFW::sense(unsigned int t) //返回值表示t对应的大物体是否在当前位置
{

    vector<unsigned int> A_;

    score_evaluator.recordAction(ActionCategory::OBSERVATION);
    Plug::Sense(A_);
    LOG("Sense");
    int flagg = 0;
    // 用“感知到的对象 id”安全地更新
    for (auto id : A_) {
        if (t == id) flagg = 1;
        if (id < objects.size() && objects[id]) {
            if (objects[id]->location != location) {
                objects[id]->location = location;
                if (auto cont = std::dynamic_pointer_cast<Container>(objects[id])) {
                    for (auto &sp : cont->smallObjectsInside) {
                        if (sp) sp->location = location;
                    }
                }
                // 小物体分支无需强制改 inside，这里保持原有逻辑不动
            }
            MarkDirectLocationEvidence(id, true);
            if (objects[id]->unable_site == location) objects[id]->unable_site = UNKNOWN;
        }
    }
    RefreshMustNearConstraintState(true);
    return flagg;


}

//查找合适的位置
int RDFW::findrightlocation(unsigned int a)
{
    if (a >= move_cons.size() || a >= putdown_cons.size()) return UNKNOWN;
    for(int i=0;i<(int)rightlocation.size();i++){
        if (!rightlocation[i]) continue;
        if (i >= (int)move_cons[a].size() || i >= (int)putdown_cons[a].size()) continue;
        if (i >= (int)goto_cons.size()) continue;
        if (goto_cons[i] == 0 && move_cons[a][i] == 0 && putdown_cons[a][i] == 0)
            return i;
    }
	return UNKNOWN;
}

//判断小物体是否在容器里面
bool RDFW::Isinside(unsigned int a, unsigned int b){
    auto small = ObjectPtrCast<SmallObject>(objects[a]);
    if(small->inside==objects[b]->id) return true;
    else return false;
}


//判断任务是否继续---跟违反的约束有关
bool RDFW::IsKeepingGoing(unsigned int index){
    if (index >= tasks.size() || tasks[index].X.empty() || !tasks[index].X[0]) return false;
    auto &t=tasks[index];
    t.risk=0;
      if(t.behave=="takeout")
      {
        auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
        if(small->inside==t.Y[0]->id){ //如果任务没有满足
            const int target_location = t.Y[0]->location;
            if (target_location >= 0) EnsureLocationCapacity(target_location);
        t.risk+=takeout_cons[t.X[0]->id][t.Y[0]->id];
        if (target_location >= 0) t.risk+=goto_cons[target_location];
        t.risk+=open_cons[t.Y[0]->id];
            }
            }

        else if(t.behave=="putin") {
            auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
             if(small->inside!=t.Y[0]->id) //如果任务没有满足
             {
                const int target_location = t.Y[0]->location;
                if (target_location >= 0) EnsureLocationCapacity(target_location);
               t.risk+=putin_cons[t.X[0]->id][t.Y[0]->id]+open_cons[t.Y[0]->id];
               if (target_location >= 0) {
                   t.risk+=move_cons[t.X[0]->id][target_location];
                   if(t.X[0]->location!=target_location) t.risk+=goto_cons[target_location];
               }
               CalculateStepRisk(t);
              }
         }
         else if(t.behave=="puton") {
             const int target_location = t.Y[0]->location;
             if (target_location >= 0) EnsureLocationCapacity(target_location);
             t.risk+=putdown1_cons[t.X[0]->id];
             if (target_location >= 0) {
                 t.risk+= putdown_cons[t.X[0]->id][target_location]+move_cons[t.X[0]->id][target_location];
                 if(t.X[0]->location!=target_location) t.risk+=goto_cons[target_location];
             }
           CalculateStepRisk(t);
         }
         else if(t.behave=="goto" && t.X[0]->location >= 0) t.risk+=goto_cons[t.X[0]->location];
         else if(t.behave=="open") {
             t.risk+=open_cons[t.X[0]->id];
             if (t.X[0]->location >= 0) t.risk+=goto_cons[t.X[0]->location];
         }
         else if(t.behave=="close") {
             t.risk+=close_cons[t.X[0]->id];
             if (t.X[0]->location >= 0) t.risk+=goto_cons[t.X[0]->location];
         }
         else if(t.behave=="pickup") {
            CalculateStepRisk(t);
         }
         else if(t.behave=="give") {
            CalculateStepRisk(t);
            t.risk+=givehuman_cons[t.X[0]->id]+putdown1_cons[t.X[0]->id];
            if (human && human->location >= 0) {
                t.risk+=move_cons[t.X[0]->id][human->location];
                if(t.X[0]->location!=human->location) t.risk+=goto_cons[human->location];
            }
            auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
         }
         else if(t.behave == "putdown")t.risk+=putdown1_cons[t.X[0]->id];
         t.risk+=t.X[0]->is_keep;
         if(t.risk>=2)
         {
            cout<<"cheating task!!"<<endl;
            cout<<"real cons num is "<<t.risk<<endl;
            t.is_cheat=0;
            return false;
         }
         else return true;
}

//判断物体是否满足条件
bool Condition::IsObjectSatisfy(const shared_ptr<Object> &target) const
 {
     if (!target || sort == "")
         return false;
     if (sort != target->sort)
         return false;
     if (color != "") // target maybe point to SmallObject
     {
         auto tem = dynamic_pointer_cast<SmallObject>(target); // Convert type safely
         if (tem && tem->color != color)
             return false;
     }
     return true;
 }

 //判断任务是否可执行
 bool Instruction::IsInstructionInvoke(const string &behave, const shared_ptr<Object> &x, const shared_ptr<Object> &y)
 {
     if (isEnable && behave == this->behave && conditionX.IsObjectSatisfy(x) && (y == nullptr || conditionY.IsObjectSatisfy(y)))
         return true;
     return false;
 }

//搜索条件物体
 void Instruction::SearchConditionObject(const shared_ptr<RDFW> &rdfw, bool is_every)
 {
     for (auto v : rdfw->objects)
     {
         if (conditionX.IsObjectSatisfy(v))
         {
             if (is_every == true || X.size() == 0)
                 X.push_back(v);
         }
         if (isUseY && conditionY.IsObjectSatisfy(v))
         {
             if (is_every == true || Y.size() == 0)
                 Y.push_back(v);
         }
     }

     // 验证是否找到了必要的物体
     if (X.empty()) {
         LOG_ERROR("Instruction Error: No object found matching conditionX (sort=%s, color=%s)",
                   conditionX.sort.c_str(), conditionX.color.c_str());
         hasMissingObjects = true;  // 标记包含不存在的物体
     }
     if (isUseY && Y.empty()) {
         LOG_ERROR("Instruction Error: No object found matching conditionY (sort=%s, color=%s)",
                   conditionY.sort.c_str(), conditionY.color.c_str());
         hasMissingObjects = true;  // 标记包含不存在的物体
     }
 }


/**====================== 原子动作 =========================== */
bool RDFW::TakeOut(unsigned int a, unsigned int b)
{
    auto small = ObjectPtrCast<SmallObject>(objects[a]);
    auto cont = ObjectPtrCast<Container>(objects[b]);
    LOG("TakeOut(%d,%s)(%d,%s)", a, small->sort.c_str(), b, cont->sort.c_str());
    score_evaluator.recordAction(ActionCategory::PHYSICAL);
    if (Plug::TakeOut(a, b))
    {
        small->inside = NONE;
        small->location = location;
        cont->DeleteObjectInside(small);
        cont->isOpen=1;
        SetHold(small);
        EnsureEvidenceCapacity(a);
        EnsureEvidenceCapacity(b);
        MarkDirectLocationEvidence(a, true);
        objectInsideVerified[a] = true;
        MarkDirectLocationEvidence(b, true);
        containerStateVerified[b] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("takeout", objects[a], objects[b]);
        takeout_cons[a][b]=0;
        RefreshMustNearConstraintState(false);
        return 1;
    }
    return 0;
}

bool RDFW::PutIn(unsigned int a, unsigned int b)
{
    auto cont = ObjectPtrCast<Container>(objects[b]);
    auto small = ObjectPtrCast<SmallObject>(objects[a]);
    if (!cont || !small) return 0; // 直接早退，避免 LOG 解引用空指针
    LOG("PutIn(%d,%s)(%d,%s)", a,small->sort.c_str() , b, cont->sort.c_str());
    score_evaluator.recordAction(ActionCategory::PHYSICAL);
    if (Plug::PutIn(a, b))
    {

        small->inside = b;
        small->location = location;
        SetHold(nullptr);
        bool already_listed = false;
        for (const auto& item : cont->smallObjectsInside) {
            if (item && item->id == small->id) { already_listed = true; break; }
        }
        if (!already_listed) cont->smallObjectsInside.push_back(small);
        cont->isOpen=1;
        EnsureEvidenceCapacity(a);
        EnsureEvidenceCapacity(b);
        MarkDirectLocationEvidence(a, true);
        objectInsideVerified[a] = true;
        MarkDirectLocationEvidence(b, true);
        containerStateVerified[b] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("putin", objects[a], objects[b]);
        putin_cons[a][b]=0;
        open_cons[b]=0;
        RefreshMustNearConstraintState(false);
        return 1;
    }
    return 0;
}
bool RDFW::Close(unsigned int a)
{
    shared_ptr<Container> container = ObjectPtrCast<Container>(objects[a]);
    if (!container) return 0;
    LOG("(%d,%s) has closed", a, container->sort.c_str());
    score_evaluator.recordAction(ActionCategory::PHYSICAL);
    if (Plug::Close(a))
    {
        container->isOpen = false;
        MarkDirectLocationEvidence(a, true);
        containerStateVerified[a] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("close", objects[a]);
        objects[a]->is_keep=0;
        close_cons[a]=0;
        RefreshMustNearConstraintState(false);
        return 1;
    }
    return 0;
}
bool RDFW::Open(unsigned int a)
{
    shared_ptr<Container> container = ObjectPtrCast<Container>(objects[a]);
    if (!container) return 0;
    LOG("Open(%d,%s)", a, container->sort.c_str());
    score_evaluator.recordAction(ActionCategory::PHYSICAL);
    if (Plug::Open(a))
    {
        container->isOpen = true;
        MarkDirectLocationEvidence(a, true);
        containerStateVerified[a] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("open", objects[a]);
        open_cons[a]=0;
        objects[a]->is_keep=0;
        RefreshMustNearConstraintState(false);
        return 1;
    }
    return 0;
}
bool RDFW::FromPlate(unsigned int a)
{
    LOG("FromPlate(%d,%s)", a, objects[a]->sort.c_str());
    score_evaluator.recordAction(ActionCategory::PHYSICAL);
    if (Plug::FromPlate(a))
    {
        SetHold(plate);
        SetPlate(nullptr);
        MarkDirectLocationEvidence(a, true);
        objectInsideVerified[a] = true;
        InvalidateSenseAtLocation(location);
        RefreshMustNearConstraintState(false);
        return 1;
    }
    fromplate_cons[a]=0;
    return 0;
}
bool RDFW::ToPlate(unsigned int a)
{
    LOG("ToPlate(%d,%s)", a, objects[a]->sort.c_str());
    score_evaluator.recordAction(ActionCategory::PHYSICAL);
    if (Plug::ToPlate(a))
    {
        SetPlate(hold);
        SetHold(nullptr);
        MarkDirectLocationEvidence(a, true);
        objectInsideVerified[a] = true;
        InvalidateSenseAtLocation(location);
        toplate_cons[a]=0;
        RefreshMustNearConstraintState(false);
        return 1;
    }
    return 0;
}

bool RDFW::PutDown(unsigned int a)
{
    LOG("PutDown(%d,%s)", a, objects[a]->sort.c_str());
    score_evaluator.recordAction(ActionCategory::PHYSICAL);
    if (Plug::PutDown(a))
    {
        SetHold(nullptr);
        auto small = dynamic_pointer_cast<SmallObject>(objects[a]);
        if (small) {
            small->location = location;
            small->inside = NONE;
        }
        MarkDirectLocationEvidence(a, true);
        objectInsideVerified[a] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("putdown", objects[a]);
        putdown1_cons[a]=0;
        EnsureLocationCapacity(location);
        putdown_cons[a][location]=0;
        RefreshMustNearConstraintState(false);
        return 1;
    }
    return 0;
}
bool RDFW::PickUp(unsigned int a)
{
    auto small = ObjectPtrCast<SmallObject>(objects[a]);
    if (!small) return 0;
    LOG("PickUp(%d,%s)", small->id, small->sort.c_str());
    score_evaluator.recordAction(ActionCategory::PHYSICAL);
    if (Plug::PickUp(a))
    {
        SetHold(small);
        small->location = location;
        small->inside = NONE;
        MarkDirectLocationEvidence(a, true);
        objectInsideVerified[a] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("pickup", objects[a]);
        pickup_cons[a]=0;
        RefreshMustNearConstraintState(false);
        return 1;
    }
    return 0;
}


bool RDFW::Move(unsigned int a)
{
    LOG("Move(%d)", a);

    // 1) 位置边界检查（使用动态数组大小）
    if ((int)a == UNKNOWN || (int)a < 0) {
        LOG(RED "Move: invalid target loc=%d (UNKNOWN or negative)\n" RESET, (int)a);
        return 0;
    }

    // 2) 确保数组容量足够，动态扩展
    EnsureLocationCapacity(a);

    // 3) 当前任务 X[0] 是否存在（聚合阶段常常不存在）
    const bool has_taskX0 =
        (task_index < tasks.size() &&
         !tasks[task_index].X.empty() &&
         tasks[task_index].X[0] != nullptr);

    auto safe_idx = [&](unsigned id)->bool {
        return (id > 0 && id < objects.size() && objects[id] != nullptr);
    };
    auto hit_move_cons = [&](unsigned id, unsigned loc)->bool {
        if (!safe_idx(id)) return false;
        if ((int)loc < 0 || (int)loc >= (int)rightlocation.size()) return false;
        // 检查二维数组边界
        if (id >= move_cons.size() || loc >= move_cons[id].size()) return false;
        return move_cons[id][loc] != 0;
    };

    // 4) 跨区前的"自清理"：手持/托盘若会触发 move 约束，先放下/取下
    if (hold_id > 0 && hit_move_cons(hold_id, a)) {
        if (!has_taskX0 || tasks[task_index].X[0]->id != hold_id) {
            PutDown(hold_id);
        }
    }
    if (plate_id > 0 && hit_move_cons(plate_id, a)) {
        if (hold_id > 0) PutDown(hold_id);
        FromPlate(plate_id);
        if (hold_id > 0) PutDown(hold_id);
    }

    // 5) 真正移动
    const int previous_location = location;
    score_evaluator.recordAction(ActionCategory::MOVE);
    if (!Plug::Move(a)) {
        LOG(RED "Move: Plug::Move(%d) failed\n" RESET, (int)a);
        return 0;
    }

    // 6) 成功后的状态更新（全部带边界/判空）
    location = a;
    if (hold)  hold->location  = a;
    if (plate) plate->location = a;
    InvalidateSenseAtLocation(previous_location);
    InvalidateSenseAtLocation(static_cast<int>(a));
    if (hold_id > 0) {
        MarkDirectLocationEvidence(hold_id, true);
    }
    if (plate_id > 0) {
        MarkDirectLocationEvidence(plate_id, true);
    }

    /*
    // 6) 移动到新位置后立即进行感知，更新物体位置信息
    // 改进：每次移动后都进行感知，更新物体位置和状态信息
    // 在多goto任务模式下跳过Sense操作
    if (!isMultiGotoMode) {
        SenseCurrentLocationOnly();
    } else {

    }
    */
    EnsureLocationCapacity(a);
    goto_cons[a] = 0;                          // a 边界在上面已保证
    if (hold_id > 0 && safe_idx(hold_id)) {
        move_cons[hold_id][a] = 0;
        objects[hold_id]->is_keep = 0;
    }

    // 正确地把“当前任务的目标对象”传给 UpdateTaskList
    if (has_taskX0) {
        UpdateTaskList("goto", tasks[task_index].X[0]);  // ✅ 用任务里的那个对象
    }
    RefreshMustNearConstraintState(false);
    return 1;
}






/*====================== 解析环境 =========================== */


void RDFW::PrintEnv()
 {
 #ifdef __DEBUG__
     vector<vector<shared_ptr<Object>>> objPos;  // 2-dim shared_ptr vector
                                                 // Each position contains all objects_ptrs
     vector<shared_ptr<Object>> unknownPos;      // 1-dim shared_ptr vector

     // Check each object's position and put into objPos
     for (auto v : objects)
     {
         if (v->location == UNKNOWN)
         {
             unknownPos.push_back(v);
             continue;
         }
         if (v->location >= objPos.size())
             objPos.resize(v->location + 1); // expand objPos
         objPos[v->location].push_back(v);
     }
 //把“位置正确性”的调试打印改为“按位置维度”访问
    if ((int)posCorrectFlag.size() < (int)objPos.size()) {
        posCorrectFlag.resize(objPos.size(), true);  // 统一按“位置维度”
    }

     for (int i = 0; i < objPos.size(); i++)
     {
         // print: position and is_correct
         bool is_corr = (i >= 0 && i < (int)posCorrectFlag.size()) ? (posCorrectFlag[i] == true) : true;
         cout << "Pos " << (i < 10 ? " " : "") << i << ":" << (is_corr ? "(T)" : "(F)") << ":";

         // print objects info in this position
         for (auto v : objPos[i])
         {
             // print robot info (green) (hold, plate)
             if (v->sort == "robot")
                 cout << GREEN << "(" << v->sort << " hold:" << hold_id << " plate:" << plate_id << ")" << RESET;

             // print Big Object info (yellow) (id, sort)
             else if (dynamic_pointer_cast<BigObject>(v))
             {
                 auto p = dynamic_pointer_cast<BigObject>(v);
                 cout << YELLOW << "(" << p->id << " " << p->sort;
                 // check container
                 if (dynamic_pointer_cast<Container>(v))
                 {
                     auto p = dynamic_pointer_cast<Container>(v);
                     cout << " inside:[";
                     for (int c = 0; c < p->smallObjectsInside.size(); c++)
                         cout << (c == 0 ? "" : ",") << p->smallObjectsInside[c]->id;
                     cout << "] " << (p->isOpen ? "Open" : "Closed");
                 }
                 cout << ")" << RESET;
             }
             else
                 cout << "(" << v->id << " " << v->sort << ")";
         }
         cout << endl;
     }

     // print Unknown Position (id, sort)
     cout << "UnknownPos:" << endl;
     for (auto v : unknownPos)
     {
         cout << BLUE << "(" << v->id << " " << v->sort << ")" << RESET << " ";
     }

     cout << endl;
 #endif
 }


bool RDFW::ParseInstruction(const string &taskDis) // 改并且新增两个函数
{
    if (taskDis.empty())
    {
        LOG_ERROR("Instruction is null");
        return false;
    }

    shared_ptr<SyntaxNode> root = make_shared<SyntaxNode>();
    vector<shared_ptr<SyntaxNode>> leaf_path;
    shared_ptr<SyntaxNode> curr_leaf = root;
    leaf_path.push_back(curr_leaf);
    int tag1 = 0;

    for (int i = 0; i < taskDis.size(); i++)
    {
        if (taskDis[i] == '(')
        {
            const string value = ExtractValue(taskDis, tag1, i);
            curr_leaf->value += value;
            tag1 = i + 1;
            auto p = make_shared<SyntaxNode>();
            curr_leaf->sons.emplace_back(p);
            curr_leaf = p;
            leaf_path.push_back(curr_leaf);
        }
        else if (taskDis[i] == ')')
        {
            const string value = ExtractValue(taskDis, tag1, i);
            curr_leaf->value += value;
            tag1 = i + 1;
            curr_leaf = *(leaf_path.end() - 2);
            leaf_path.pop_back();
        }
    }
    ExtractInstructions(root->sons[0]->sons);
    return true;
}



string RDFW::ExtractValue(const string &taskDis, int tag1, int tag2)
{
    const string value = taskDis.substr(tag1, tag2 - tag1);
    return (value.back() == ' ' ? value.substr(0, value.size() - 1) : value);
}



void RDFW::ExtractInstructions(const vector<shared_ptr<SyntaxNode>> &nodes)
{
    // instructions.reserve(nodes.size());
    for (const auto &node : nodes)
    {
        string instructionType = node->value;

        if (instructionType == ":task")
        {
            tasks.emplace_back(Instruction(node, shared_from_this())); // 创建一个新的 Instruction 对象
        }
        else if (instructionType == ":cons_not")
        {
            for (auto y : node->sons)
            {
                if (y->value == ":info") not_infoConstrains.emplace_back(Instruction(node->sons[0], shared_from_this()));
                if (y->value == ":task")not_taskConstrains.emplace_back(Instruction(node->sons[0], shared_from_this()));
            }
        }
        else if (instructionType == ":cons_notnot")notnot_infoConstrains.emplace_back(Instruction(node->sons[0], shared_from_this())); // 创建一个新的 Instruction 对象
        else if (instructionType == ":info")infos.emplace_back(Instruction(node, shared_from_this()));

    }
}


////////////////////////////////////////////////////////////////////////////////////////////////////////
/**
 * @brief   Parse Natural Language
 * @param   src (const): All env strings in natural language
 * @returns None
 */
void RDFW::ParseNaturalLanguage(const string &src) //
{
    int lp = 0;
    for (int i = 0; i < src.size(); i++)
    {
        if (src[i] == '.')  // separated by sentence "."
        {
            string str = src.substr(lp, (i + 1) - lp);  // extract sentence (lp:start,  i:end)
            LOG(GREEN "%s" RESET, str.c_str()); // print sentence in log
            ParseNaturalLanguageSentence(str);  // parse sentence info
            lp = i + 2;
        }
    }
}


////////////////////////////////////////////////////////////////////////////////////////////////////////
/**
 * @brief   Parse Natural Language (Single Sentence)
 * @param   s (string): single sentence to parse
 * @return  if Parse successfully
 */
bool RDFW::ParseNaturalLanguageSentence(const string &s) // 改
{
    if (!nlp_parser->parse(s))  // Fail to parse
    {
        errorlist.push_back(s);
        return false;
    }

    auto tree = nlp_parser->root;
    vector<Instruction> *list_p = nullptr;
    bool is_task = true;

    switch (tree->sons.size())
    {
    case 1:
    {
        if (tree->sons[0]->token.type == VP)
        {
            if (nlp_parser->is_not)
                list_p = &not_taskConstrains;
            else
                list_p = &tasks;
        }
        break;
    }
    case 2:
    case 3:
    {
        is_task = false;

        // 定位指令类被
        if (nlp_parser->is_must)
        {
            if (nlp_parser->is_not)
                list_p = &not_infoConstrains;
            else
                list_p = &notnot_infoConstrains;
        }
        else
            list_p = &infos;
        break;
    }
    default:
        break;
    }

    if (list_p == nullptr)
    {
        LOG_ERROR("NLP Parse Error");
    }
    else
    {
        Instruction instr;
        // 捕获task或info, 封装进Instruction
        if (is_task)
            instr = nlp_parser->get_task_instruction();
        else
            instr = nlp_parser->get_info_instruction();

        // 添加至Instruction vector
        list_p->push_back(instr);
        list_p->back().SearchConditionObject(shared_from_this(), nlp_parser->is_every);
    }

    return true;
}



bool RDFW::ParseEnvSentence(const string &sentence) // 改
{
    int pos = 1;
    vector<string> tokenList;
    tokenList.reserve(3); // Reserve space for up to 3 tokens

    // Extract token
    for (int i = 1; i < sentence.size(); i++)
    {
        if (sentence[i] == ' ' || sentence[i] == ')')
        {
            tokenList.emplace_back(&sentence[pos], &sentence[i]);
            pos = i + 1;
        }
    }

    if (tokenList.size() != 2 && tokenList.size() != 3)
    {
        LOG_ERROR("Env Sentence (%s) error", sentence.c_str());
        return false;
    }

    const string &firstToken = tokenList[0];
    int index = stoi(tokenList[1]);
    int lastSize = objects.size();

    // set robot status
    if (firstToken == "hold")
    {
        this->hold_id = index;
    }
    else if (firstToken == "plate")
    {
        this->plate_id = index;
    }
    else
    {
        while (index >= lastSize)
        {
            objects.emplace_back(make_shared<Object>(lastSize++));
            posCorrectFlag.push_back(!isErrorCorrection);
        }

        auto &obj = objects[index];

        if (firstToken == "opened" || firstToken == "closed")
        {
            auto containerPtr = dynamic_pointer_cast<Container>(obj);
            if (containerPtr == nullptr)
            {
                containerPtr = make_shared<Container>(obj);
                obj = containerPtr;
            }
            containerPtr->isOpen = (firstToken == "opened");
        }
        else if (firstToken == "at")
        {
            int L = stoi(tokenList[2]);
            EnsureLocationCapacity(L);
            obj->location = L;
            rightlocation[L] = 1;
        }
        else if (firstToken == "sort")
        {
            obj->sort = tokenList[2];
        }
        else if (firstToken == "size")
        {
            if (tokenList[2] == "big")
            {
                if (dynamic_pointer_cast<BigObject>(obj) == nullptr)
                {
                    auto bigObjPtr = make_shared<BigObject>(obj);
                    obj = bigObjPtr;
                }
            }
            else if (tokenList[2] == "small")
            {
                if (dynamic_pointer_cast<SmallObject>(obj) == nullptr)
                {
                    auto smallObjPtr = make_shared<SmallObject>(obj);
                    smallObjects.push_back(smallObjPtr);
                    obj = smallObjPtr;
                }
            }
        }
        else if (firstToken == "color")
        {
            auto smallObjPtr = dynamic_pointer_cast<SmallObject>(obj);
            if (smallObjPtr == nullptr)
            {
                smallObjPtr = make_shared<SmallObject>(obj);
                smallObjects.push_back(smallObjPtr);
                obj = smallObjPtr;
            }
            smallObjPtr->color = tokenList[2];
        }
        else if (firstToken == "inside")
        {
            auto smallObjPtr = dynamic_pointer_cast<SmallObject>(obj);
            if (smallObjPtr == nullptr)
            {
                smallObjPtr = make_shared<SmallObject>(obj);
                smallObjects.push_back(smallObjPtr);
                obj = smallObjPtr;
            }
            smallObjPtr->inside = stoi(tokenList[2]);
        }
        else if (firstToken == "type" && tokenList[2] == "container")
        {
            if (dynamic_pointer_cast<Container>(obj) == nullptr)
            {
                auto containerPtr = make_shared<Container>(obj);
                obj = containerPtr;
            }
        }
    }

    return true;
}



bool RDFW::ParseEnv(const string &env) // 没改
{
    regex reg("\\(.*?\\)");
    cmatch m;
    auto pos = env.data() + 1;
    auto end = env.data() + env.size();

    // separate sentence and parse
    for (; regex_search(pos, end, m, reg); pos = m.suffix().first)
    {
        string str = m.str();
        if (ParseEnvSentence(str) == false)
        {
            LOG_ERROR("Parse Env Sentence ERROR\n %s", env.c_str());
            return false;
        }
    }

    // set robot status
    if (hold_id > 0)
    {
        SetHold(ObjectPtrCast<SmallObject>(objects[hold_id]));
        MarkDirectLocationEvidence(hold_id, stage == 1);
        objectInsideVerified[hold_id] = (stage == 1);
    }
    if (plate_id > 0)
    {
        SetPlate(ObjectPtrCast<SmallObject>(objects[plate_id]));
        MarkDirectLocationEvidence(plate_id, stage == 1);
        objectInsideVerified[plate_id] = (stage == 1);
    }

    for (const auto &s : smallObjects)
    {
        if (s == plate || s == hold)
            continue;
        if (s->inside != UNKNOWN && s->inside != NONE)
        {
            auto p = dynamic_pointer_cast<Container>(objects[s->inside]);
            if (p != nullptr)
            {
                p->smallObjectsInside.push_back(s);
                s->location = p->location;
            }
            else
            {
                s->location = UNKNOWN;
                s->inside = UNKNOWN;
            }
        }
        else if (s->location != UNKNOWN)
            s->inside = NONE;
    }

    return true;
}



void RDFW::ParseInfo(const Instruction &info) // 改
{
    // 跳过包含不存在物体的info
    if (info.hasMissingObjects) {
        return;
    }

    const string &behave = info.behave;

    if (behave == "on")
    {
        int thelocation = info.Y[0]->location;
        for (auto v : info.X)
        {
            v->location = thelocation;
            auto small=dynamic_pointer_cast<SmallObject>(v);
            if(small!=nullptr) {
                small->inside=NONE;
                small->on = info.Y[0]->id;
            }
        }
    }
    else if (behave == "near")
    {
        int yLocation = info.Y[0]->location;
        int xLocation = info.X[0]->location;

        if (yLocation != UNKNOWN)
        {
            for (auto v : info.X)
            {
            v->location = yLocation;
            auto small=dynamic_pointer_cast<SmallObject>(v);
            if(small!=nullptr) small->inside=NONE;
            }

        }
        else if (xLocation != UNKNOWN)
        {
            for (auto v : info.Y)
            {
            v->location = xLocation;
            auto small=dynamic_pointer_cast<SmallObject>(v);
            if(small!=nullptr) small->inside=NONE;
            }
        }
    }
    else if (behave == "plate")
    {
        if (plate == nullptr)
        {
            SetPlate(ObjectPtrCast<SmallObject>(info.X[0]));
        }
        else
        {
            LOG_ERROR("The plate already has a small object (%d %s)", plate->id, plate->sort.c_str());
        }
    }
    else if (behave == "inside" || behave == "in")
    {
        auto c = ObjectPtrCast<Container>(info.Y[0]);
        int cId = c->id;

        for (auto v : info.X)
        {
            auto p = ObjectPtrCast<SmallObject>(v);
            p->inside = cId;
            p->location=c->location;
            c->smallObjectsInside.push_back(p);
        }
    }
    else if (behave == "opened")
    {
        for (auto v : info.X)
        {
            auto p = ObjectPtrCast<Container>(v);
            p->isOpen = true;
        }
    }
    else if (behave == "closed")
    {
        for (auto v : info.X)
        {
            auto p = ObjectPtrCast<Container>(v);
            p->isOpen = false;
        }
    }
}






/*====================== 工具函数=========================== */
//UpdateTaskList、LogInstructionError、AfterSolveTask、PrintInstruction、


//更新任务列表
void RDFW::UpdateTaskList(const string& behave,
        const shared_ptr<Object>& x,
        const shared_ptr<Object>& y)
    {
    for (auto& t : tasks) {
    if (!t.isEnable) continue;

    if (behave == "goto") {
    // 仅当“同一物体”时才去重（严格按对象 id）
    if (t.behave == "goto" && t.X.size() > 0 && t.X[0] && x && (t.X[0]->id == x->id)) {
    t.isEnable = false;
    }
    // 注意：这里直接 continue，避免 goto 走到下面“通用等价”分支
    continue;
    }

    // 非 goto：保持你原有的等价判定（条件/对象等）
    if (t.IsInstructionInvoke(behave, x, y)) {
    t.isEnable = false;
    }
    }
}

//记录错误任务
void RDFW::LogInstructionError(const Instruction &task) // 新增
{
    stringstream ss;
    ss << task;
    LOG_ERROR("Instruction Error\n %s", ss.str().c_str());
}

//执行完任务后更新约束
void RDFW::AfterSolveTask(const Instruction &task){
    if(task.behave=="pickup") for(int i=0;i<(int)pickup_cons.size();i++) pickup_cons[i]+=2;
    else if(task.behave=="putdown") pickup_cons[task.X[0]->id]+=2;
    else if(task.behave=="takeout") putin_cons[task.X[0]->id][task.Y[0]->id]+=2;
    else if(task.behave=="putin") takeout_cons[task.X[0]->id][task.Y[0]->id]+=2;
//这里要删除
//    else if(task.behave=="goto") for(int i=0;i<50;i++) goto_cons[i]+=2;
    else task.X[0]->is_keep+=2;
}//我还是想把这个改一下

/**
 * @brief   Print Instruction Infomation
 * @param   None
 * @note    task, info, constrains are stored as "Instruction class",
 *          include bahave, conditionX, conditionY (if it has)
 */
 void RDFW::PrintInstruction()
 {
 #ifdef __DEBUG__
     // print tasks (Do)
     cout << "Task:\n";
     for (auto v : tasks) {
         cout << v;
     }

     // print infos
     cout << "\nInfo:\n";
     for (auto v : infos) {
         cout << v;
     }

     // print not_infos (constrains)
     cout << "\nNot_Info:\n";
     for (auto v : not_infoConstrains) {
         cout << v;
     }

     // print not_tasks (constrains)
     cout << "\nNot_Task:\n";
     for (auto v : not_taskConstrains)
         {
         cout << v;
     }

     // print notnot_infos (Must keep)
     cout << "\nNotNot_Info:\n";
     for (auto v : notnot_infoConstrains)
         {
         cout << v;
     }
 #endif
 }



 ////////////////////////////////////////////////////////////////////////////////////////////////////////
 /**
  * @brief   Print Environment Infomation
  * @param   None
  * @note    All Env Infomations are stored in objects, include id, sort, position...
  *          we define a 2D vector to store each objects' position and its info
  *
  */


void RDFW::Fini()
{
    cout << "#(RDFW): Fini - Comprehensive state cleanup for next test" << endl;

    // ==================== 机器人状态重置 ====================
    location = UNKNOWN;
    hold = nullptr;
    hold_id = 0;

    // ==================== 对象引用清理 ====================
    human = nullptr;
    plate = nullptr;
    plate_id = 0;
    task_index = 0;

    // ==================== 状态变量重置 ====================
    solved_task_num = 0;
    err_times = 0;
    isPass = false;
    isKeepConstrain = false;
    isMultiGotoMode = false;
    isAutoConstrain = false;
    isAskTwice = false;

    // ==================== 容器完全清理 ====================
    objects.clear();
    smallObjects.clear();
    tasks.clear();
    infos.clear();
    not_infoConstrains.clear();
    not_taskConstrains.clear();
    notnot_infoConstrains.clear();
    posCorrectFlag.clear();
    posSensedFlag.clear();
    objectLocationVerified.clear();
    objectLocationInferredByMustNear.clear();
    objectInsideVerified.clear();
    containerStateVerified.clear();
    errorlist.clear();
    lock_by_mustnear.clear();
    mustNearComponent.clear();

    // ==================== 内存优化清理 ====================
    // 强制释放vector内存
    objects.shrink_to_fit();
    smallObjects.shrink_to_fit();
    tasks.shrink_to_fit();
    infos.shrink_to_fit();
    not_infoConstrains.shrink_to_fit();
    not_taskConstrains.shrink_to_fit();
    notnot_infoConstrains.shrink_to_fit();
    posCorrectFlag.shrink_to_fit();
    posSensedFlag.shrink_to_fit();
    objectLocationVerified.shrink_to_fit();
    objectLocationInferredByMustNear.shrink_to_fit();
    objectInsideVerified.shrink_to_fit();
    containerStateVerified.shrink_to_fit();
    errorlist.shrink_to_fit();
    lock_by_mustnear.shrink_to_fit();
    mustNearComponent.shrink_to_fit();

    // ==================== 数组完全重置 ====================
    // 重置并查集数组
    memset(uf_parent, -1, sizeof(uf_parent));
    memset(uf_size, 0, sizeof(uf_size));
    memset(uf_groupLoc, -1, sizeof(uf_groupLoc));

    // 重置配置标志
    enable_near_correction = true;
    enable_must_lock = true;
    sense_cb = nullptr;

    // ==================== 动态数组深度清理 ====================
    // 清理一维数组
    fill(goto_cons.begin(), goto_cons.end(), 0);
    fill(putdown1_cons.begin(), putdown1_cons.end(), 0);
    fill(open_cons.begin(), open_cons.end(), 0);
    fill(close_cons.begin(), close_cons.end(), 0);
    fill(pickup_cons.begin(), pickup_cons.end(), 0);
    fill(givehuman_cons.begin(), givehuman_cons.end(), 0);
    fill(fromplate_cons.begin(), fromplate_cons.end(), 0);
    fill(toplate_cons.begin(), toplate_cons.end(), 0);
    fill(rightlocation.begin(), rightlocation.end(), false);

    // 清理二维数组
    for (auto& row : putin_cons) fill(row.begin(), row.end(), 0);
    for (auto& row : takeout_cons) fill(row.begin(), row.end(), 0);
    for (auto& row : putdown_cons) fill(row.begin(), row.end(), 0);
    for (auto& row : move_cons) fill(row.begin(), row.end(), 0);
    for (auto& row : mustnear_cons) fill(row.begin(), row.end(), 0);

    // ==================== 感知状态完全重置 ====================
    posSensedFlag.resize(100, false);
    objectLocationVerified.resize(100, false);
    objectLocationInferredByMustNear.resize(100, false);
    objectInsideVerified.resize(100, false);
    containerStateVerified.resize(100, false);
    locationSensedObjects.resize(100);

    // 深度清理位置感知数据
    for (auto& loc_info : locationSensedObjects) {
        loc_info.object_ids.clear();
        loc_info.object_ids.shrink_to_fit();
        loc_info.container_id = 0;
        loc_info.has_container = false;
    }

    // ==================== 解析器状态清理 ====================
    if (nlp_parser) {
        parser::clear_static_state();
    }

    // ==================== 重新初始化基础状态 ====================
    objects.push_back(shared_from_this());
    if (isErrorCorrection)
        posCorrectFlag.push_back(false);
    else
        posCorrectFlag.push_back(true);

    // ==================== 内存优化 ====================
    OptimizeMemoryUsage();

    cout << "#(RDFW): Comprehensive state cleanup completed - ready for next test" << endl;
}

void RDFW::OptimizeMemoryUsage() {
    cout << "#(RDFW): Optimizing memory usage..." << endl;

    // 强制释放所有vector的未使用内存
    objects.shrink_to_fit();
    smallObjects.shrink_to_fit();
    tasks.shrink_to_fit();
    infos.shrink_to_fit();
    not_infoConstrains.shrink_to_fit();
    not_taskConstrains.shrink_to_fit();
    notnot_infoConstrains.shrink_to_fit();
    posCorrectFlag.shrink_to_fit();
    posSensedFlag.shrink_to_fit();
    objectLocationVerified.shrink_to_fit();
    objectLocationInferredByMustNear.shrink_to_fit();
    objectInsideVerified.shrink_to_fit();
    containerStateVerified.shrink_to_fit();
    errorlist.shrink_to_fit();
    lock_by_mustnear.shrink_to_fit();
    mustNearComponent.shrink_to_fit();

    // 优化动态数组内存
    goto_cons.shrink_to_fit();
    putdown1_cons.shrink_to_fit();
    open_cons.shrink_to_fit();
    close_cons.shrink_to_fit();
    pickup_cons.shrink_to_fit();
    givehuman_cons.shrink_to_fit();
    fromplate_cons.shrink_to_fit();
    toplate_cons.shrink_to_fit();
    rightlocation.shrink_to_fit();

    // 优化二维数组内存
    for (auto& row : putin_cons) row.shrink_to_fit();
    for (auto& row : takeout_cons) row.shrink_to_fit();
    for (auto& row : putdown_cons) row.shrink_to_fit();
    for (auto& row : move_cons) row.shrink_to_fit();
    for (auto& row : mustnear_cons) row.shrink_to_fit();

    // 优化位置感知数据内存
    for (auto& loc_info : locationSensedObjects) {
        loc_info.object_ids.shrink_to_fit();
    }
    locationSensedObjects.shrink_to_fit();

    cout << "#(RDFW): Memory optimization completed" << endl;
}



 void split_string(vector<string> &out, const string &str_source, char mark)
 {
     int last = 0;
     for (int i = 0; i < str_source.size(); i++)
     {
         if (str_source[i] == mark)
         {
             out.push_back(str_source.substr(last, i - last));
             last = i + 1;
         }
     }
     if (last != str_source.size())
         out.push_back(str_source.substr(last, str_source.size() - 1));
 }





 Instruction::Instruction() {}

 Instruction::Instruction(const shared_ptr<SyntaxNode> &node, const shared_ptr<RDFW> &rdfw) // 改
 {
     vector<string> disc;
     split_string(disc, node->sons[0]->value, ' '); // node是ins下一层的小节点
     behave = disc[0];

    for (const auto &n : node->sons[1]->sons) // sons[1]是cond节点
    {
        vector<string> temp;
        split_string(temp, n->value, ' ');

        // 检查temp向量是否有足够的元素
        if (temp.size() < 3) {
            LOG_ERROR("Invalid condition format: %s", n->value.c_str());
            continue;
        }

        Condition *con = &conditionX;
        if (temp[1] == "Y")
        {
            isUseY = true;
            con = &conditionY;
        }
        if (temp[0] == "color")
        {
            con->color = temp[2];
        }
        else if (temp[0] == "sort")
        {
            con->sort = temp[2];
        }
    }

     SearchConditionObject(rdfw);
 }


 ostream &operator<<(ostream &os, const Instruction &instr)
 {
     os << instr.ToString();
     return os;
 }

 ostream &operator<<(ostream &os, shared_ptr<SyntaxNode> sn)
 {
     static int layer = 0;
     for (int i = 0; i < layer; i++)
         os << "-";
     os << sn->value << '|' << endl;
     layer++;
     for (int i = 0; i < sn->sons.size(); i++)
     {
         os << sn->sons[i];
     }
     layer--;
     return os;
 }

 ostream &operator<<(ostream &os, shared_ptr<Object> obj)
 {
     if (dynamic_pointer_cast<SmallObject>(obj) != nullptr)
     {
         os << "SmallObject " << dynamic_pointer_cast<SmallObject>(obj)->ToString();
     }
     else if (dynamic_pointer_cast<Robot>(obj) != nullptr)
     {
         os << "this " << dynamic_pointer_cast<Robot>(obj)->ToString();
     }
     else if (dynamic_pointer_cast<BigObject>(obj) != nullptr)
     {
         if (dynamic_pointer_cast<Container>(obj) != nullptr)
         {
             os << "Container " << dynamic_pointer_cast<Container>(obj)->ToString();
         }
         else
         {
             os << "BigObject  " << dynamic_pointer_cast<BigObject>(obj)->ToString();
         }
    }
    return os;
}

 /**
  * @brief Must Near 纠错与补全（极简版）
  * - 用并查集把 near 约束形成的对象连通分量合并
  * - 对每个分量按“已知位置”的多数票决定组位置
  * - 如果启用上锁，则把组内所有对象位置改为该“组位置”，并标记为锁定
  * 依赖成员：
  *   objects, notnot_infoConstrains, lock_by_mustnear, enable_near_correction, enable_must_lock, UNKNOWN
  */
void RDFW::BuildMustNearRelations() {
    const size_t object_count = objects.size();
    mustnear_cons.assign(object_count, vector<int>(object_count, 0));
    mustNearComponent.assign(object_count, UNKNOWN);
    lock_by_mustnear.assign(object_count, false);
    hold_mustnear = false;
    plate_mustnear = false;

    if (object_count == 0) return;

    vector<int> parent(object_count);
    vector<int> component_size(object_count, 1);
    std::iota(parent.begin(), parent.end(), 0);

    auto find_root = [&](int id) {
        while (parent[id] != id) {
            parent[id] = parent[parent[id]];
            id = parent[id];
        }
        return id;
    };
    auto unite = [&](int lhs, int rhs) {
        lhs = find_root(lhs);
        rhs = find_root(rhs);
        if (lhs == rhs) return;
        if (component_size[lhs] < component_size[rhs]) std::swap(lhs, rhs);
        parent[rhs] = lhs;
        component_size[lhs] += component_size[rhs];
    };

    for (const auto& cons : notnot_infoConstrains) {
        if (cons.hasMissingObjects ||
            (cons.behave != "near" && cons.behave != "nextto")) continue;

        // 自然语言中的 every 会让 X/Y 各包含多个对象；must-near 应覆盖
        // 两侧对象集合的笛卡尔积，而不是只读取 X[0]/Y[0]。
        for (const auto& x : cons.X) {
            if (!x || x->id <= 0 || static_cast<size_t>(x->id) >= object_count) continue;
            for (const auto& y : cons.Y) {
                if (!y || y->id <= 0 || static_cast<size_t>(y->id) >= object_count ||
                    x->id == y->id) continue;
                ++mustnear_cons[x->id][y->id];
                ++mustnear_cons[y->id][x->id];
                unite(x->id, y->id);
                LOG(GREEN "[MustNear] relation obj %d <-> obj %d\n" RESET,
                    x->id, y->id);
            }
        }
    }

    for (size_t id = 1; id < object_count; ++id) {
        bool has_relation = false;
        for (size_t other = 1; other < object_count; ++other) {
            if (mustnear_cons[id][other] > 0) {
                has_relation = true;
                break;
            }
        }
        if (has_relation) mustNearComponent[id] = find_root(static_cast<int>(id));
    }

    hold_mustnear = hold_id > 0 && static_cast<size_t>(hold_id) < mustNearComponent.size() &&
                    mustNearComponent[hold_id] != UNKNOWN;
    plate_mustnear = plate_id > 0 && static_cast<size_t>(plate_id) < mustNearComponent.size() &&
                     mustNearComponent[plate_id] != UNKNOWN;
}

void RDFW::RefreshMustNearConstraintState(bool propagate_evidence) {
    const size_t object_count = objects.size();
    if (mustNearComponent.size() != object_count) return;

    lock_by_mustnear.assign(object_count, false);
    unordered_map<int, vector<unsigned int>> groups;
    for (size_t id = 1; id < object_count; ++id) {
        if (mustNearComponent[id] != UNKNOWN && objects[id])
            groups[mustNearComponent[id]].push_back(static_cast<unsigned int>(id));
    }

    for (const auto& entry : groups) {
        const vector<unsigned int>& members = entry.second;
        map<int, int> direct_votes;
        map<int, int> candidate_votes;

        for (unsigned int id : members) {
            EnsureEvidenceCapacity(id);
            const int loc = objects[id]->location;
            if (loc == UNKNOWN) continue;
            if (objectLocationVerified[id] && !objectLocationInferredByMustNear[id])
                ++direct_votes[loc];
            if (!objectLocationInferredByMustNear[id]) ++candidate_votes[loc];
        }

        const map<int, int>& votes = direct_votes.empty() ? candidate_votes : direct_votes;
        int chosen_location = UNKNOWN;
        int best_count = 0;
        bool tied = false;
        for (const auto& vote : votes) {
            if (vote.second > best_count) {
                chosen_location = vote.first;
                best_count = vote.second;
                tied = false;
            } else if (vote.second == best_count) {
                tied = true;
            }
        }
        if (tied) chosen_location = UNKNOWN;

        bool conflicts_with_evidence = false;
        if (chosen_location != UNKNOWN) {
            for (unsigned int id : members) {
                // Sense 未发现对象形成明确的反证，不能再由 must-near 把它
                // 强行写回同一位置。
                if (objects[id]->unable_site == chosen_location) {
                    conflicts_with_evidence = true;
                    break;
                }
                if (objectLocationVerified[id] && !objectLocationInferredByMustNear[id] &&
                    objects[id]->location != UNKNOWN && objects[id]->location != chosen_location) {
                    conflicts_with_evidence = true;
                    break;
                }
            }
        }

        if (propagate_evidence && chosen_location != UNKNOWN && !conflicts_with_evidence) {
            for (unsigned int id : members) {
                if (objects[id]->location == chosen_location &&
                    objectLocationVerified[id] && !objectLocationInferredByMustNear[id]) continue;

                objects[id]->location = chosen_location;
                objectLocationVerified[id] = true;
                objectLocationInferredByMustNear[id] = true;

                // 容器位置变化时，只同步确定在该容器内的物体；不修改
                // SmallObject::inside/on，near 本身不代表包含或承载关系。
                auto container = dynamic_pointer_cast<Container>(objects[id]);
                if (container) {
                    for (const auto& item : container->smallObjectsInside) {
                        if (!item || item->inside != container->id) continue;
                        item->location = chosen_location;
                        EnsureEvidenceCapacity(item->id);
                        objectLocationVerified[item->id] = true;
                        objectLocationInferredByMustNear[item->id] = true;
                    }
                }
                LOG(GREEN "[MustNear] inferred obj %u at location %d\n" RESET,
                    id, chosen_location);
            }
        }

        int component_location = UNKNOWN;
        bool component_consistent = !conflicts_with_evidence;
        for (unsigned int id : members) {
            const int loc = objects[id]->location;
            if (loc == UNKNOWN) {
                component_consistent = false;
                break;
            }
            if (component_location == UNKNOWN) component_location = loc;
            else if (component_location != loc) {
                component_consistent = false;
                break;
            }
        }

        if (enable_must_lock && component_consistent && component_location != UNKNOWN) {
            for (unsigned int id : members) lock_by_mustnear[id] = true;
        } else if (chosen_location == UNKNOWN || conflicts_with_evidence) {
            LOG(YELLOW "[MustNear] component %d has conflicting/insufficient evidence; not propagated\n" RESET,
                entry.first);
        }
    }
}

void RDFW::ApplyMustNearConstraintCorrection() {
    if (!enable_near_correction) {
        LOG(YELLOW "[MustNear] disabled\n" RESET);
        return;
    }
    BuildMustNearRelations();
    RefreshMustNearConstraintState(true);
    LOG(GREEN "[MustNear] correction done.\n" RESET);
}


void RDFW::ApplyMustInConstraintCorrection() {
    const int numObjs = static_cast<int>(objects.size());
    if (numObjs <= 0) return;

    // 采集 mustin（或同义）约束：记录每个物体唯一的容器
    std::vector<int> obj_to_cont(numObjs, -1);
    for (const auto& cons : notnot_infoConstrains) {
        if (cons.behave == "inside"||cons.behave == "in" && !cons.X.empty() && !cons.Y.empty())
        {
            const int x = static_cast<int>(cons.X[0]->id);
            const int y = static_cast<int>(cons.Y[0]->id);
            if (x < 0 || x >= numObjs || y < 0 || y >= numObjs) continue;
            cout<<"x: "<<x<<" y: "<<y<<endl;

            obj_to_cont[x] = y;

            cout<<"obj_to_cont[x]: "<<obj_to_cont[x]<<endl;

            // 直接同步smallObject和container信息
            if (objects[x]) {
                if (auto sm = std::dynamic_pointer_cast<SmallObject>(objects[x])) {
                    cout<<"sm->inside: "<<sm->inside<<endl;
                    // 移除在原容器中的记录
                    if (sm->inside != UNKNOWN && sm->inside != y) {
                        if (sm->inside >= 0 && sm->inside < numObjs) {
                            if (auto old_cont = std::dynamic_pointer_cast<Container>(objects[sm->inside])) {
                                auto& vec = old_cont->smallObjectsInside;
                                vec.erase(std::remove_if(vec.begin(), vec.end(),
                                    [&](const std::shared_ptr<SmallObject>& ptr) {
                                        return ptr && ptr->id == sm->id;
                                    }), vec.end());
                            }
                        }
                    }
                    sm->inside = y;
                    // 添加到目标容器（避免重复）
                    if (objects[y]) {
                        if (auto cont = std::dynamic_pointer_cast<Container>(objects[y])) {
                            bool exists = false;
                            for (auto&& v : cont->smallObjectsInside) {
                                if (v && v->id == sm->id) { exists = true; break; }
                            }
                            if (!exists)
                                cont->smallObjectsInside.push_back(sm);
                        }
                    }
                }
            }
            // 同步位置（取容器已知位置为准，否则不强制）
            if (objects[x] && objects[y]) {
                int y_loc = objects[y]->location;
                if (y_loc != UNKNOWN) {
                    objects[x]->location = y_loc;
                    LOG(GREEN "[MustIn] (direct) set obj %d @ %d (in %d)\n" RESET, x, y_loc, y);
                }
            }
        }
    }

    // INSERT_YOUR_CODE
    // 处理 notinside 约束的纠错与补全
    // 遍历所有 notnot_infoConstrains，查找 behave == "notinside" 的约束
    for (const auto& cons : not_infoConstrains) {
        if (cons.behave != "inside"&&cons.behave != "in") continue;
        if (cons.X.empty() || cons.Y.empty()) continue;
        int x = static_cast<int>(cons.X[0]->id);   // smallObject id
        int y = static_cast<int>(cons.Y[0]->id);   // container id
        if (x < 0 || x >= numObjs || y < 0 || y >= numObjs) continue;
        // 防御性检查
        auto smObj = std::dynamic_pointer_cast<SmallObject>(objects[x]);
        if (!smObj) continue;
        // 如果x当前就在y里，需要移除
        if (smObj->inside == y) {
            // 修改smallObject的inside信息
            smObj->inside = UNKNOWN;
            int old_loc = smObj->location;
            smObj->location = UNKNOWN;
            // 同时尝试从container的smallObjectsInside中移除
            auto cont = std::dynamic_pointer_cast<Container>(objects[y]);
            if (cont) {
                auto& vec = cont->smallObjectsInside;
                vec.erase(std::remove_if(vec.begin(), vec.end(),
                    [&](const std::shared_ptr<SmallObject>& ptr){
                        return ptr && ptr->id == smObj->id;
                    }), vec.end());
            }
            LOG(GREEN "[NotInside] remove obj %d from container %d\n" RESET, x, y);
        }
        // 如果inside本来就不是y，例如 UNKNOWN 或其他容器，则无需操作
    }

    LOG(GREEN "[MustIn] correction done.\n" RESET);
}

// open和close的纠正和补全，只处理not_infoConstrains和notnot_infoConstrains

void RDFW::ApplyOpenCloseCorrection() {
    // 遍历所有容器，对opened/closed的约束进行处理
    for (const auto& obj : objects) {
        if (!obj) continue;
        auto cont = std::dynamic_pointer_cast<Container>(obj);
        if (!cont) continue;

        // 收集是否存在opened/closed的约束
        bool must_open = false;
        bool must_closed = false;
        bool cons_not_open = false;
        bool cons_not_closed = false;

        // notnot_infoConstrains：必须成立
        for (const auto& cons : notnot_infoConstrains) {
            if (cons.X.empty()) continue;
            if (cons.X[0]->id != obj->id) continue;
            if (cons.behave == "opened") must_open = true;
            else if (cons.behave == "closed") must_closed = true;
        }
        // not_infoConstrains：必须不成立
        for (const auto& cons : not_infoConstrains) {
            if (cons.X.empty()) continue;
            if (cons.X[0]->id != obj->id) continue;
            if (cons.behave == "opened") cons_not_open = true;
            else if (cons.behave == "closed") cons_not_closed = true;
        }

        // 优先满足冲突最小原则
        // 如果必须open且不能closed
        if (must_open && !cons_not_open && !must_closed) {
            if (!cont->isOpen) {
                cont->isOpen = true;
                LOG(GREEN "[AutoOpenClose] set container %d open (by notnot)\n" RESET, cont->id);
            }
        }
        // 如果必须closed且不能open
        else if (must_closed && !cons_not_closed && !must_open) {
            if (cont->isOpen) {
                cont->isOpen = false;
                LOG(GREEN "[AutoOpenClose] set container %d closed (by notnot)\n" RESET, cont->id);
            }
        }
        // 如果not要求not opened，则要关闭
        else if (cons_not_open && !must_open) {
            if (cont->isOpen) {
                cont->isOpen = false;
                LOG(GREEN "[AutoOpenClose] set container %d closed (by not constraint)\n" RESET, cont->id);
            }
        }
        // 如果not要求not closed，则要打开
        else if (cons_not_closed && !must_closed) {
            if (!cont->isOpen) {
                cont->isOpen = true;
                LOG(GREEN "[AutoOpenClose] set container %d open (by not constraint)\n" RESET, cont->id);
            }
        }
        // 冲突：有not和notnot都要求open/closed
        else if ((must_open && cons_not_open) || (must_closed && cons_not_closed) || (must_open && must_closed)) {
            // 默认优先closed
            cont->isOpen = false;
            LOG(YELLOW "[AutoOpenClose] conflict: container %d open/close constraints conflict, set to closed\n" RESET, cont->id);
        }
        // 无约束不处理
    }
}
