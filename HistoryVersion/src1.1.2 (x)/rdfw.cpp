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
    
    // 初始化任务查找表 - 优化内存分配
    takeout.clear();
    takeout.reserve(max_size);
    for (int i = 0; i < max_size; i++) {
        takeout.emplace_back(max_size, false);
    }
    
    putin.clear();
    putin.reserve(max_size);
    for (int i = 0; i < max_size; i++) {
        putin.emplace_back(max_size, false);
    }
    
    close.clear();
    close.reserve(max_size);
    close.resize(max_size, false);
    
    open.clear();
    open.reserve(max_size);
    open.resize(max_size, false);
    
    pickup.clear();
    pickup.reserve(max_size);
    pickup.resize(max_size, false);
    
    putdown.clear();
    putdown.reserve(max_size);
    putdown.resize(max_size, false);
    
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
            if (arg == "-budget_ms" || arg == "-reserve_ms") {
                if (nextArg.empty()) throw std::invalid_argument("missing budget option value");
                size_t used = 0;
                long value = std::stol(nextArg, &used);
                if (used != nextArg.size() || value < 0)
                    throw std::invalid_argument("invalid budget option value");
                if (arg == "-budget_ms") budget_ms = value;
                else reserve_ms = value;
                ++i;
                continue;
            }

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
    if (budget_ms > 0 && reserve_ms >= budget_ms) reserve_ms = budget_ms / 5;
    budget.configure(budget_ms, reserve_ms);
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


void RDFW::CheckBudget() { budget.check(); }

bool RDFW::CanStartTask() {
    CheckBudget();
    return budget.phase() == TimeBudget::Phase::Normal;
}

void RDFW::BeforeAction(const char* action) {
    CheckBudget();
    ++action_counts[action];
}

void RDFW::EmitMetrics() const {
    std::cout << "RDFW_METRICS {\"elapsed_ms\":" << budget.elapsed_ms()
              << ",\"budget_ms\":" << budget.limit_ms()
              << ",\"exit_reason\":\"" << (budget_stopped ? "budget" : "completed")
              << "\",\"completed_during_execution\":" << solved_task_num
              << ",\"actions\":{";
    bool first = true;
    for (const auto& item : action_counts) {
        if (!first) std::cout << ",";
        std::cout << "\"" << item.first << "\":" << item.second;
        first = false;
    }
    std::cout << "}}" << std::endl;
}

void RDFW::Plan() {
    budget.reset();
    budget_stopped = false;
    action_counts.clear();
    try {
        PlanWithinBudget();
    } catch (const BudgetExceeded&) {
        budget_stopped = true;
        // Return normally so the official SDK sends Fini and grades current state.
    }
    EmitMetrics();
}

void RDFW::PlanWithinBudget() // 改
{   
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
        posSensedFlag[LocationId(i)] = false;
    }
    fill(objectLocationVerified.begin(), objectLocationVerified.end(), false);
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
    
    // 验证任务查找表状态
    for (auto& row : takeout) fill(row.begin(), row.end(), false);
    for (auto& row : putin) fill(row.begin(), row.end(), false);
    fill(close.begin(), close.end(), false);
    fill(open.begin(), open.end(), false);
    fill(pickup.begin(), pickup.end(), false);
    fill(putdown.begin(), putdown.end(), false);
    
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
    CheckBudget();
    Cons_plan();
    FilterConstraintsByTaskConflicts();
    cout<<"cons_plan finished"<<endl;
    cout <<  "--------------------------------------------" << endl;

    /*=======================任务优化===================*/
    CheckBudget();
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
        if (solved_task_num == 0) {
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
    ExecuteCheckPhase(CheckAndDeferMultiGoto());

    /*============== Multi-GOTO聚合 ==============*/
    // 执行Multi-GOTO聚合
    PrintEnv();
    ExecuteMultiGotoAggregation();

    /*============== 结果输出 ==============*/
    cout << endl
         << "Sovled Task Num:" << solved_task_num << "    " << "Expect Num:" << tasks.size() << endl;
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
                bigObjectId, objects[ObjectId(bigObjectId)]->sort.c_str(), taskCount);
            
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
        if (!CanStartTask()) break;
        // 跳过包含不存在物体的任务
        if (tasks[task_index].hasMissingObjects) {
            continue;
        }
        
        // 延后多 GOTO：本轮不做，留给末尾聚合
        if (defer_multi_goto && tasks[task_index].behave == "goto") {
            continue;
        }
        
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
        if (!CanStartTask()) break;
        // 跳过包含不存在物体的任务
        if (tasks[task_index].hasMissingObjects) {
            continue;
        }
        
        // 延后多 GOTO：检查一遍也不做，留给末尾聚合
        if (defer_multi_goto && tasks[task_index].isEnable && tasks[task_index].behave == "goto") {
            continue;
        }
        if(tasks[task_index].isEnable&&CalculateTaskRisk(tasks[task_index])<2){
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
        
        if(cons.behave=="on" && cons.Y[0]->location >= 0) {
            if(cons.X[0]->location!=cons.Y[0]->location) putdown_cons[ObjectId(cons.X[0]->id)][LocationId(cons.Y[0]->location)]++;
            else if(cons.X[0]->id==plate_id||cons.X[0]->id==hold_id) putdown_cons[ObjectId(cons.X[0]->id)][LocationId(cons.Y[0]->location)]++;
        }
        else if(cons.behave=="inside"||cons.behave=="in") {
             auto small=dynamic_pointer_cast<SmallObject>(cons.X[0]);
            if(small->inside!=cons.Y[0]->id) putin_cons[ObjectId(cons.X[0]->id)][ObjectId(cons.Y[0]->id)]++;
        }
        else if(cons.behave == "near"||cons.behave == "nextto") {
            if(cons.Y[0]->location!=cons.X[0]->location) //如果约束没有触犯
            {
            if(cons.Y[0]->location!=UNKNOWN) move_cons[ObjectId(cons.X[0]->id)][LocationId(cons.Y[0]->location)]++;
            if(cons.X[0]->location!=UNKNOWN) move_cons[ObjectId(cons.Y[0]->id)][LocationId(cons.X[0]->location)]++;
            }
        } 
        else if(cons.behave == "plate") toplate_cons[ObjectId(cons.X[0]->id)]++; 
        else if(cons.behave == "opened") {
            auto cont=dynamic_pointer_cast<Container>(cons.X[0]);
            if(cont->isOpen!=1) open_cons[ObjectId(cons.X[0]->id)]++;  
        }
        else if(cons.behave == "closed")
        {   
            auto cont=dynamic_pointer_cast<Container>(cons.X[0]);
            if(cont->isOpen==1) close_cons[ObjectId(cons.X[0]->id)]++; 
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
               mustnear_cons[ObjectId(cons.X[0]->id)][ObjectId(cons.Y[0]->id)]++;
            }
            else if(cons.behave=="near"&&cons.Y.size()>0&&cons.X[0]->location==cons.Y[0]->location){
                 cons.X[0]->is_keep++;
                  cons.Y[0]->is_keep++;
                  mustnear_cons[ObjectId(cons.X[0]->id)][ObjectId(cons.Y[0]->id)]++;
            }
            else if(cons.behave=="plate"&& plate_id==cons.X[0]->id)fromplate_cons[ObjectId(cons.X[0]->id)]++;
            else if(cons.behave=="inside"||cons.behave=="in")
            {
            auto small=dynamic_pointer_cast<SmallObject>(cons.X[0]);
            if(small->inside==cons.Y[0]->id)  takeout_cons[ObjectId(cons.X[0]->id)][ObjectId(cons.Y[0]->id)]++;
            } 
           else if(cons.behave=="closed") {
             auto cont=dynamic_pointer_cast<Container>(cons.X[0]);
            if(cont->isOpen!=1) open_cons[ObjectId(cons.X[0]->id)]++;
           }
           else if(cons.behave=="opened") {
            auto cont=dynamic_pointer_cast<Container>(cons.X[0]);
            if(cont->isOpen!=1) close_cons[ObjectId(cons.X[0]->id)]++;
           }
    }
    for(auto cons:not_taskConstrains){
        // 跳过包含不存在物体的约束
        if (cons.hasMissingObjects) {
            continue;
        }
        
        //这里不用判断一开始是否触犯约束
         if(cons.behave=="takeout") takeout_cons[ObjectId(cons.X[0]->id)][ObjectId(cons.Y[0]->id)]++;
         else if(cons.behave=="putin") putin_cons[ObjectId(cons.X[0]->id)][ObjectId(cons.Y[0]->id)]++;
         else if(cons.behave=="puton" && cons.Y[0]->location >= 0) putdown_cons[ObjectId(cons.X[0]->id)][LocationId(cons.Y[0]->location)]++;
         else if(cons.behave=="goto" && cons.X[0]->location >= 0) goto_cons[LocationId(cons.X[0]->location)]++;
         else if(cons.behave=="open") open_cons[ObjectId(cons.X[0]->id)]++;
         else if(cons.behave=="close") close_cons[ObjectId(cons.X[0]->id)]++;
         else if(cons.behave=="pickup") pickup_cons[ObjectId(cons.X[0]->id)]++;
         else if(cons.behave=="give") givehuman_cons[ObjectId(cons.X[0]->id)]++;
         else if(cons.behave == "putdown") putdown1_cons[ObjectId(cons.X[0]->id)]++ ;
    }
    if(hold_id>0) {
        x=hold_id;
     if(objects[ObjectId(x)]->is_keep>putdown1_cons[ObjectId(x)]+putdown_cons[ObjectId(x)][LocationId(location)]+fromplate_cons[ObjectId(x)]){
        cout<<"the hold object must putdown here!"<<endl;
         PutDown(ObjectId(x));
     }
     }
    if(plate_id>0) 
    {
        x=plate_id;
     if(objects[ObjectId(x)]->is_keep>putdown1_cons[ObjectId(x)]+putdown_cons[ObjectId(x)][LocationId(location)]+fromplate_cons[ObjectId(x)]){
        cout<<"the plate object must putdown here!"<<endl;
        if(hold_id>0) PutDown(ObjectId(hold_id));
        FromPlate(ObjectId(x));
         PutDown(ObjectId(x));
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
        if (goto_cons[LocationId(loc)] > 0) {
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
            if (conflict_count - goto_cons[LocationId(loc)] > 2) {
                discard_gotoconsloc[i] = loc;
                discard_gotoconsloc_count[i] = conflict_count;
                sum_conflict_count+=conflict_count;
                if (conflict_count - goto_cons[LocationId(loc)] > max_effect) {
                    max_effect = conflict_count - goto_cons[LocationId(loc)];
                    max_effect_loc = loc;
                }
                cout << "[FilterConstraintsByTaskConflicts] Conflict found between goto_cons at location " << loc << " with conflict count " << conflict_count << endl;
                i++;
            }
        }
    }

    
    if(sum_conflict_count>30) {
        goto_cons[LocationId(max_effect_loc)] = 0;
        cout << "[FilterConstraintsByTaskConflicts] Discarded goto_cons at location " << max_effect_loc << " due to " << max_effect << " conflicts." << endl;
    }
    else{
        while(i>=0){
            goto_cons[LocationId(discard_gotoconsloc[i])] = 0;
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
        if (open_cons[ObjectId(id)] > 0) {
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
            if (conflict_count - open_cons[ObjectId(id)] > 2) {
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
        open_cons[ObjectId(max_effect_id)] = 0;
        cout << "[FilterConstraintsByTaskConflicts] Discarded open_cons for id " << max_effect_id << " due to " << max_effect_open << " conflicts." << endl;
    }
    else{
        for(int k = 0; k < j; k++){
            open_cons[ObjectId(discard_openconsid[k])] = 0;
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
        
        if(tasks[i].behave=="putin"){
             putin[ObjectId(tasks[i].X[0]->id)][ObjectId(tasks[i].Y[0]->id)]=true;
        }
        else if(tasks[i].behave=="takeout"){
             takeout[ObjectId(tasks[i].X[0]->id)][ObjectId(tasks[i].Y[0]->id)]=true;
        }
        else if(tasks[i].behave=="open"){
             open[ObjectId(tasks[i].X[0]->id)]=true;
        }
        else if(tasks[i].behave=="close"){
             close[ObjectId(tasks[i].X[0]->id)]=true;
        }
        else if(tasks[i].behave=="pickup"){
             pickup[ObjectId(tasks[i].X[0]->id)]=true;
        }
        else if(tasks[i].behave=="putdown"){
             putdown[ObjectId(tasks[i].X[0]->id)]=true;
        }
        optimizedTasks.push_back(tasks[i]);
      }

return optimizedTasks;
}




/**====================== 任务执行 =========================== */

/*========1)风险预判 ===============*/

//计算任务风险
int RDFW::CalculateTaskRisk(Instruction &t){
    t.risk=0;
    if (t.X.empty() || !t.X[0] || t.hasMissingObjects) return t.risk = 1000;
    if ((t.behave == "putin" || t.behave == "puton" || t.behave == "takeout") &&
        (t.Y.empty() || !t.Y[0])) return t.risk = 1000;
    if (t.behave == "give" && !human) return t.risk = 1000;
    auto at_risk = [&](int loc) {
        if (loc < 0) return 0;
        EnsureLocationCapacity(loc);
        return goto_cons[LocationId(loc)];
    };
    auto pair_risk = [&](const ObjectLocationTable& table, int id, int loc) {
        if (loc < 0) return 0;
        EnsureLocationCapacity(loc);
        return table[ObjectId(id)][LocationId(loc)];
    };
   if(t.behave=="takeout")
   {
     auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
    if(small->inside!=t.Y[0]->id) return 0;//如果任务满足
       EnsureLocationCapacity(t.Y[0]->location);
     t.risk+=takeout_cons[ObjectId(t.X[0]->id)][ObjectId(t.Y[0]->id)]+at_risk(t.Y[0]->location);
     t.risk+=open_cons[ObjectId(t.Y[0]->id)];
    }

     else if(t.behave=="putin") {
         auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
          if(small->inside==t.Y[0]->id) return 0;
         EnsureLocationCapacity(t.Y[0]->location);

            t.risk+=putin_cons[ObjectId(t.X[0]->id)][ObjectId(t.Y[0]->id)]+open_cons[ObjectId(t.Y[0]->id)]+pair_risk(move_cons, t.X[0]->id, t.Y[0]->location);
            if(t.X[0]->location!=t.Y[0]->location) t.risk+=at_risk(t.Y[0]->location);
            CalculateStepRisk(t);

      }
      else if(t.behave=="puton") {
          EnsureLocationCapacity(t.Y[0]->location);

          t.risk+= pair_risk(putdown_cons, t.X[0]->id, t.Y[0]->location)+pair_risk(move_cons, t.X[0]->id, t.Y[0]->location)+putdown1_cons[ObjectId(t.X[0]->id)];
        if(t.X[0]->location!=t.Y[0]->location) t.risk+=at_risk(t.Y[0]->location);
        CalculateStepRisk(t);
      }
      else if (t.behave == "goto") {
          int loc = t.X[0]->location;
          t.risk += at_risk(loc);
           // 调试日志，明确 t.risk 的组成
          std::cout << "[DBG] goto risk@loc=" << loc
                    << " bool=" << at_risk(loc)
                   << std::endl;
      }

      else if(t.behave=="open") t.risk+=open_cons[ObjectId(t.X[0]->id)]+at_risk(t.X[0]->location);
      else if(t.behave=="close") t.risk+=close_cons[ObjectId(t.X[0]->id)]+at_risk(t.X[0]->location);
      else if(t.behave=="pickup") {
         CalculateStepRisk(t);
      }
      else if(t.behave=="give") {
         CalculateStepRisk(t);
         t.risk+=givehuman_cons[ObjectId(t.X[0]->id)]+pair_risk(move_cons, t.X[0]->id, human->location)+putdown1_cons[ObjectId(t.X[0]->id)];
         if(t.X[0]->location!=human->location) t.risk+=at_risk(human->location);
         auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
      }
      else if(t.behave == "putdown")t.risk+=putdown1_cons[ObjectId(t.X[0]->id)];
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
        t.risk+=goto_cons[LocationId(t.X[0]->location)];
    }
    auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
    if (!small) return 0;
    if(small->inside!=UNKNOWN&&small->inside!=NONE)t.risk+=open_cons[ObjectId(small->inside)]+takeout_cons[ObjectId(small->id)][ObjectId(small->inside)];
    else if(small->inside==NONE) t.risk+=pickup_cons[ObjectId(small->id)];
    return 1;
}

// ==== helpers for capacity & existence ====
inline void RDFW::EnsureLocationCapacity(int loc) {
    if (loc < 0) return;
    const size_t count = static_cast<size_t>(loc) + 1;
    if (posCorrectFlag.size() < count) posCorrectFlag.resize(count, false);
    if (posSensedFlag.size() < count) posSensedFlag.resize(count, false);
    if (locationSensedObjects.size() < count) locationSensedObjects.resize(count);
    if (goto_cons.size() < count) goto_cons.resize(count, 0);
    if (rightlocation.size() < count) rightlocation.resize(count, false);
    // Location is the COLUMN of these tables. Never expand object rows here.
    for (auto& row : putdown_cons) if (row.size() < count) row.resize(count, 0);
    for (auto& row : move_cons) if (row.size() < count) row.resize(count, 0);
}

void RDFW::EnsureObjectCapacity(ObjectId id) {
    if (id.value() < 0) throw std::out_of_range("negative object id");
    const size_t count = static_cast<size_t>(id.value()) + 1;
    for (auto* table : {&putdown1_cons, &open_cons, &close_cons, &pickup_cons,
                       &givehuman_cons, &fromplate_cons, &toplate_cons})
        if (table->size() < count) table->resize(count, 0);
    for (auto* table : {&putin_cons, &takeout_cons, &mustnear_cons}) {
        if (table->size() < count) table->resize(count);
        for (auto& row : *table) if (row.size() < table->size()) row.resize(table->size(), 0);
    }
    for (auto* table : {&putdown_cons, &move_cons}) {
        if (table->size() < count) table->resize(count);
        for (auto& row : *table) if (row.size() < rightlocation.size()) row.resize(rightlocation.size(), 0);
    }
    for (auto* table : {&putin, &takeout}) {
        if (table->size() < count) table->resize(count);
        for (auto& row : *table) if (row.size() < table->size()) row.resize(table->size(), false);
    }
    for (auto* table : {&open, &close, &pickup, &putdown})
        if (table->size() < count) table->resize(count, false);
    EnsureEvidenceCapacity(id.value());
}

inline void RDFW::EnsureObjectExists(unsigned id, bool prefer_small) {
    if (id >= objects.size()) {
        size_t last = objects.size();
        objects.resize(id + 1);
        for (size_t i = last; i < objects.size(); ++i) {
            objects[ObjectId(i)] = std::make_shared<Object>((unsigned)i);
        }
    }
    if (prefer_small) {
        if (!std::dynamic_pointer_cast<SmallObject>(objects[ObjectId(id)])) {
            objects[ObjectId(id)] = std::make_shared<SmallObject>(objects[ObjectId(id)]); // 基于已有 Object 包装
            smallObjects.push_back(std::dynamic_pointer_cast<SmallObject>(objects[ObjectId(id)]));
        }
    }
    EnsureObjectCapacity(ObjectId(id));
}

void RDFW::EnsureEvidenceCapacity(unsigned int id) {
    const size_t required = static_cast<size_t>(id) + 1;
    if (objectLocationVerified.size() < required)
        objectLocationVerified.resize(required, false);
    if (objectInsideVerified.size() < required)
        objectInsideVerified.resize(required, false);
    if (containerStateVerified.size() < required)
        containerStateVerified.resize(required, false);
}

void RDFW::InvalidateSenseAtLocation(int loc) {
    if (loc < 0) return;
    EnsureLocationCapacity(loc);
    posSensedFlag[LocationId(loc)] = false;
    locationSensedObjects[LocationId(loc)].object_ids.clear();
    locationSensedObjects[LocationId(loc)].container_id = NONE;
    locationSensedObjects[LocationId(loc)].has_container = false;
}

bool RDFW::IsLocationVerified(unsigned int id) const {
    return id < objectLocationVerified.size() && objectLocationVerified[ObjectId(id)];
}

bool RDFW::IsInsideVerified(unsigned int id) const {
    return id < objectInsideVerified.size() && objectInsideVerified[ObjectId(id)];
}

bool RDFW::IsContainerStateVerified(unsigned int id) const {
    return id < containerStateVerified.size() && containerStateVerified[ObjectId(id)];
}


/*========2)任务顺序执行 ===============*/

/*======a)做任务（边执行边判断）==========*/


//执行任务----主要是看有没有任务对象，服务stage2
bool RDFW::SolveTask(const Instruction &task) // 改
{
    if (!CanStartTask()) return false;
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
    auto target_small = ObjectPtrCast<SmallObject>(objects[ObjectId(a)]);
    ///这是stage1的逻辑
     if(stage==1)
    {
      if (plate_id == a)
        {
        if (hold_id != NONE && !PutDown(ObjectId(hold_id))) return false;
        return FromPlate(ObjectId(a));
        }
       else if(hold_id==a) return true;
    if (hold_id != NONE && !PutDown(ObjectId(hold_id))) return false;
    if(location!=target_small->location && !Move(LocationId(target_small->location))) return false;
    if(target_small->inside==NONE) return PickUp(ObjectId(a));
    else if(target_small->inside!=UNKNOWN)//说明小物体在容器里面
    {
       auto target_cont = ObjectPtrCast<Container>(objects[ObjectId(target_small->inside)]);
       if(!target_cont->isOpen && !Open(ObjectId(target_cont->id))) return false;
       return  TakeOut(ObjectId(a),ObjectId(target_cont->id));
    }
    return false;
    }
    //这是stage2的逻辑
    if (hold_id == static_cast<int>(a)) {
        if (IsInsideVerified(a)) return true;
        // 初始 hold 事实可能是错的。用一次可观察动作建立本地事实；失败则清除猜测。
        if (PutDown(ObjectId(a))) return HoldSmallObject(a);
        SetHold(nullptr);
    }
    if (plate_id == static_cast<int>(a) && !IsInsideVerified(a)) {
        if (FromPlate(ObjectId(a))) return true;
        SetPlate(nullptr);
    }
    if (hold_id != a)
    {
        if (hold_id != NONE && !PutDown(ObjectId(hold_id))) return false; //如果拿着物体，先放下
        if (plate_id == a)
        {
        return FromPlate(ObjectId(a));
        }

        while (1)
        {
            CheckBudget();
            t++;
            if (target_small->location != UNKNOWN)
            {
                if (location != target_small->location)
                    if(Move(LocationId(target_small->location))!=1)
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
                    
                     if (target_small->location == location && PickUp(ObjectId(a))) return 1;

                     // 先保证容量（这是“语句”，必须放在 if 条件外执行）
                     EnsureLocationCapacity(location);

                     // 然后再按条件判断
                     if ( posSensedFlag[LocationId(location)]
                          && target_small->location == location
                          && HasContainerAtLocation(location)
                          && [&]{
                                 unsigned int cont_id = GetContainerAtLocation(location);
                                 if (cont_id > 0) {
                                     auto cont = ObjectPtrCast<Container>(objects[ObjectId(cont_id)]);
                                     return (cont && cont->isOpen);
                                 }
                                 return false;
                             }() )
                     {
                         if (TakeOut(ObjectId(a),ObjectId( GetContainerAtLocation(location)))) return 1;
                         if (t >= 2) return 0;
                     }
                     else {
                         if (plate_id == UNKNOWN && FromPlate(ObjectId(a))) return 1;
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
                                    if(Open(ObjectId(initial_cont_id))) return TakeOut(ObjectId(a),ObjectId(initial_cont_id)); //认为骗我是关的
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
    auto target_cont = ObjectPtrCast<Container>(objects[ObjectId(cont)]);
    if (!target_cont) return TakeOutResult::NeedContainerLocation;
    auto verified_absent_from_open_container = [&]() -> bool {
        if (!target_cont->isOpen || !IsContainerStateVerified(cont)) return false;
        SenseCurrentLocationOnly(true);
        const bool absent = HasObjectAtLocation(location, cont) &&
                            !HasObjectAtLocation(location, small);
        if (absent && small < objects.size()) {
            auto small_object = dynamic_pointer_cast<SmallObject>(objects[ObjectId(small)]);
            if (small_object && small_object->inside == static_cast<int>(cont)) {
                target_cont->DeleteObjectInside(small_object);
                small_object->inside = UNKNOWN;
                EnsureEvidenceCapacity(small);
                objectInsideVerified[ObjectId(small)] = false;
            }
        }
        return absent;
    };
    //Airong:
    if(target_cont->location==UNKNOWN)return TakeOutResult::NeedContainerLocation;

    if(!target_cont->isOpen)
    {
     if(Open(ObjectId(cont)))
        if(!TakeOut(ObjectId(small),ObjectId(cont))) {
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
        containerStateVerified[ObjectId(cont)] = true;
        if(!TakeOut(ObjectId(small),ObjectId(cont))) {
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
         if(!TakeOut(ObjectId(small),ObjectId(cont)))
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
    if(putdown[ObjectId(a)] != false){
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
    if(pickup[ObjectId(a)] != false){
        if(hold_id!=a&&plate_id!=a) return true;
        else {
            cout<<"there is pickup task,no need to do this!"<<endl;
            return false;
        }
    }
    if(hold_id==a){
        if(putdown_cons[ObjectId(a)][LocationId(location)]) {
            int safe_location = findrightlocation(a);
            if (safe_location == UNKNOWN || !Move(LocationId(safe_location))) return false;
        }
        return PutDown(ObjectId(a));
    }
    else if(plate_id==a){
        if(hold_id>0) {
            if (!PutDown(ObjectId(hold_id))) return false;
            if(putdown_cons[ObjectId(a)][LocationId(location)]) {
                int safe_location = findrightlocation(a);
                if (safe_location == UNKNOWN || !Move(LocationId(safe_location))) return false;
            }
        }
        if (!FromPlate(ObjectId(a))) return false;
        if(putdown_cons[ObjectId(a)][LocationId(location)]) {
            int safe_location = findrightlocation(a);
            if (safe_location == UNKNOWN || !Move(LocationId(safe_location))) return false;
        }
       return PutDown(ObjectId(a));
    }
    else {
        auto small = dynamic_pointer_cast<SmallObject>(objects[ObjectId(a)]);
        if (!small) return false;
        if (stage == 1 && small->inside == NONE) return true;
        if (stage == 2 && IsInsideVerified(a) && IsLocationVerified(a) && small->inside == NONE)
            return true;
        if (!HoldSmallObject(a)) return false;
        if (location < 0) return false;
        EnsureLocationCapacity(location);
        if (putdown_cons[ObjectId(a)][LocationId(location)]) {
            int safe_location = findrightlocation(a);
            if (safe_location == UNKNOWN || !Move(LocationId(safe_location))) return false;
        }
        return PutDown(ObjectId(a));
    }
}

//goto任务
bool RDFW::SolveTask_Goto(unsigned int a)
{
    if(stage==1)
    {
        if(location==objects[ObjectId(a)]->location){
        return true;
    }
    else return Move(LocationId(objects[ObjectId(a)]->location));
    }

    //stage2的情况
    if(location==objects[ObjectId(a)]->location && IsLocationVerified(a)) return true;
    const bool is_small = dynamic_pointer_cast<SmallObject>(objects[ObjectId(a)]) != nullptr;
    if(objects[ObjectId(a)]->location==UNKNOWN)
    {
        if(dynamic_pointer_cast<SmallObject>(objects[ObjectId(a)]) != nullptr)
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
            CheckBudget();
        t++;
    if(location==objects[ObjectId(a)]->location) {
        SenseCurrentLocationOnly(true);
        if (HasObjectAtLocation(location, a)) return true;
        auto small = dynamic_pointer_cast<SmallObject>(objects[ObjectId(a)]);
        if (small && small->inside > 0 && HasObjectAtLocation(location, small->inside)) {
            EnsureEvidenceCapacity(a);
            objectLocationVerified[ObjectId(a)] = true;
            return true;
        }
    }
    else if(!Move(LocationId(objects[ObjectId(a)]->location)))
    {
          if(t>=2) return false;
          if(is_small) {GetSmallObjectStatus(a);if(!IsKeepingGoing(task_index)) return 0;}
          else {GetBigObjectStatus(a);if(!IsKeepingGoing(task_index)) return 0;}
    }
    else {
        SenseCurrentLocationOnly(true);
        if (HasObjectAtLocation(location, a)) return true;
        auto small = dynamic_pointer_cast<SmallObject>(objects[ObjectId(a)]);
        if (small && small->inside > 0 && HasObjectAtLocation(location, small->inside)) {
            EnsureEvidenceCapacity(a);
            objectLocationVerified[ObjectId(a)] = true;
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
    auto cnt=dynamic_pointer_cast<Container>(objects[ObjectId(a)]);
    if(close[ObjectId(a)] != false){
        if(cnt->isOpen && (stage == 1 || IsContainerStateVerified(a))) return true;
        else {
            cout<<"there is close task,no need to do this!"<<endl;
            return false;
        }
    }
    if(cnt->isOpen && (stage == 1 || IsContainerStateVerified(a))) return true;
    if(hold_id!=NONE && !PutDown(ObjectId(hold_id))) return false;
    if(stage==1)
    {
        if (location != objects[ObjectId(a)]->location && !Move(LocationId(objects[ObjectId(a)]->location))) return false;
        return Open(ObjectId(a));
    }

    //这是stage2
    if(objects[ObjectId(a)]->location==UNKNOWN)
    {
        GetBigObjectStatus(a);
        if(!IsKeepingGoing(task_index)) return 0;
    }
     int t=0;
    while(1)
    {
            CheckBudget();
        t++;
    if (location != objects[ObjectId(a)]->location)
        if(!Move(LocationId(objects[ObjectId(a)]->location)))
        {
            if(t>=2) return false;
            GetBigObjectStatus(a);
             if(!IsKeepingGoing(task_index)) return 0;
        }
    if(!Open(ObjectId(a)))
    {
       if (sense(a)) {
            cnt->isOpen = true;
            EnsureEvidenceCapacity(a);
            containerStateVerified[ObjectId(a)] = true;
            objectLocationVerified[ObjectId(a)] = true;
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
    auto cnt=dynamic_pointer_cast<Container>(objects[ObjectId(a)]);
    if(open[ObjectId(a)] != false)
    {
        if(!cnt->isOpen && (stage == 1 || IsContainerStateVerified(a))) return true;
        else {
            cout<<"there is open task,no need to do this!"<<endl;
            return false;
        }
    }
    if(!cnt->isOpen && (stage == 1 || IsContainerStateVerified(a))) return true;
    if(hold_id!=NONE && !PutDown(ObjectId(hold_id))) return false;
    if(stage==1)
    {
    if (location != objects[ObjectId(a)]->location && !Move(LocationId(objects[ObjectId(a)]->location))) return false;
    return Close(ObjectId(a));
    }

   //这是stage2

   if(objects[ObjectId(a)]->location==UNKNOWN)
    {
        GetBigObjectStatus(a);
        if(!IsKeepingGoing(task_index)) return 0;
    }
     int t=0;
    while(1)
    {
            CheckBudget();
        t++;
    if (location != objects[ObjectId(a)]->location)
        if(!Move(LocationId(objects[ObjectId(a)]->location)))
        {
            if(t>=2) return false;
            GetBigObjectStatus(a);
             if(!IsKeepingGoing(task_index)) return 0;
        }
    if(!Close(ObjectId(a)))
    {
       if (sense(a)) {
            cnt->isOpen = false;
            EnsureEvidenceCapacity(a);
            containerStateVerified[ObjectId(a)] = true;
            objectLocationVerified[ObjectId(a)] = true;
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
            if(objects[ObjectId(a)]->location==human->location && plate_id!=a && hold_id!=a) return true;
            else return SolveTask_PutOn(a, human->id);
            }
        else
            LOG_ERROR("There are not human in Scene");

    return false;
}


//putin任务
bool RDFW::SolveTask_Putin(unsigned int a, unsigned int b)
{
    if(takeout[ObjectId(a)][ObjectId(b)] != false)
    {
        if(Isinside(a,b) && (stage == 1 || IsInsideVerified(a))) return true;
               else
               {
            cout<<"there is takeout task,no need to do this!"<<endl;
            return false;
               }
    }
    if(Isinside(a,b) && (stage == 1 || IsInsideVerified(a))) return true;
    auto target_cont = ObjectPtrCast<Container>(objects[ObjectId(b)]);
    if(stage==1)
    {
        //优化了一下规划，如果目标物体和容器在一起，先打开再picku
        if(objects[ObjectId(a)]->location==objects[ObjectId(b)]->location)
        {
        if (location != target_cont->location && !Move(LocationId(target_cont->location))) return false;
        if (target_cont->isOpen != 1 && !Open(ObjectId(b))) return false;
        if (!HoldSmallObject(a)) return false;
        return PutIn(ObjectId(a),ObjectId(b));
        }
        else
        {
        if(!HoldSmallObject(a)) return false;
        if (location != target_cont->location && !Move(LocationId(target_cont->location))) return false;
        if (target_cont->isOpen != 1)
        {
        if (!PutDown(ObjectId(a))) return false;
        if (!Open(ObjectId(b))) return false;
        if (!PickUp(ObjectId(a))) return false;
        }
        return PutIn(ObjectId(a),ObjectId(b));
        }
       return false;
    }
    //stage2的情况
  //open如果false可能的情况有两种：1.容器本身就是开着的，他骗我没开 2.b容器就不在这个位置
  //putin a b 如果false的情况有两种： 1.容器是关着的，骗我是开着的，我没有打开 2.b容器就不在这个位置上
    if(objects[ObjectId(b)]->location==UNKNOWN)
    {
        GetBigObjectStatus(b);
        if(!IsKeepingGoing(task_index)) return 0;
    }
    if(!HoldSmallObject(a)) return false;
    
    int try_times=0;
    while(1)
    {
            CheckBudget();
      try_times++;
    if (location != target_cont->location)
        if(!Move(LocationId(target_cont->location)))
        {
            if(try_times>=2) return false;
            GetBigObjectStatus(b);
            if(!IsKeepingGoing(task_index)) return false;
            continue;
        }

    if (!target_cont->isOpen)
    {
        if (!PutDown(ObjectId(a))) return false;
        if(Open(ObjectId(b)))
        {
             if (!PickUp(ObjectId(a))) return false;
             return PutIn(ObjectId(a),ObjectId(b));
        }
        else
        {
            if(sense(b)) {
                target_cont->isOpen = true;
                EnsureEvidenceCapacity(b);
                containerStateVerified[ObjectId(b)] = true;
                if (!PickUp(ObjectId(a))) return false;
                return PutIn(ObjectId(a),ObjectId(b));
            }
            else
            {
            if(try_times>=2) return false;
            if (!PickUp(ObjectId(a))) return false;
            GetBigObjectStatus(b);
            if(!IsKeepingGoing(task_index)) return false;
            continue;
            }
        }

    }
    else
    {
    if(!PutIn(ObjectId(a),ObjectId( b)))
    {
        if (!PutDown(ObjectId(a))) return false;
       if(Open(ObjectId(b))){
           if (!PickUp(ObjectId(a))) return false;
           return PutIn(ObjectId(a),ObjectId(b));
       }
       else
       {
        if(try_times>=2) return false;
        if (!PickUp(ObjectId(a))) return false;
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
    if(putin[ObjectId(a)][ObjectId(b)] != false){
         if(Isinside(a,b)==0) return true;
        else {
            cout<<"there is putin task,no need to do this!"<<endl;
            return false;
        }
    }
    auto small = ObjectPtrCast<SmallObject>(objects[ObjectId(a)]);


    auto target_cont = ObjectPtrCast<Container>(objects[ObjectId(b)]);
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
        if (hold!= nullptr && !PutDown(ObjectId(hold->id))) return false;
        if (location != target_cont->location && !Move(LocationId(target_cont->location))) return false;
        if (target_cont->isOpen != 1 && !Open(ObjectId(target_cont->id))) return false;
        return TakeOut(ObjectId(a),ObjectId( target_cont->id));
    }
   ///这是stage2的逻辑 //对于takeout任务，inside未知，location未知，先去容器尝试takeout；或者先询问小物体，再判断任务是否已经完成
    if(target_cont->location==UNKNOWN){GetBigObjectStatus(b);if(!IsKeepingGoing(task_index)) return false;}
    if (hold!= nullptr && !PutDown(ObjectId(hold->id))) return false;
    int t = 0;
    while(1)
    {
            CheckBudget();
        t++;
    if (location != target_cont->location)
        if(!Move(LocationId(target_cont->location)))
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
     if(Open(ObjectId(b))) return TakeOut(ObjectId(a),ObjectId(b)); //认为骗我是关的
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
    auto small=dynamic_pointer_cast<SmallObject>(objects[ObjectId(a)]);
    if(small && small->inside==NONE && small->location==objects[ObjectId(b)]->location &&
       plate_id!=a && hold_id!=a &&
       (stage == 1 || (IsInsideVerified(a) && IsLocationVerified(a) && IsLocationVerified(b))))
        return true;
    //
    if(objects[ObjectId(b)]->location==UNKNOWN)
    {
        GetBigObjectStatus(b);
         if(!IsKeepingGoing(task_index)) return false;
    }
    if (!HoldSmallObject(a)) return false;
    int t=0;
    while(1)
    {
            CheckBudget();
        t++;
        if (location != objects[ObjectId(b)]->location)
        {
            if(!Move(LocationId(objects[ObjectId(b)]->location)))
            {
            if (t >= 3)  return 0;
            GetBigObjectStatus(b);
            if(!IsKeepingGoing(task_index)) return false;
            continue;
            }
        }
        if (stage == 2 && (!IsLocationVerified(b) || objects[ObjectId(b)]->location != location)) {
            SenseCurrentLocationOnly(true);
            if(!HasObjectAtLocation(location, b)) {
                if (t >= 3) return false;
                GetBigObjectStatus(b);
                if(!IsKeepingGoing(task_index)) return false;
                continue;
            }
        }
        return PutDown(ObjectId(a));
    }
    return true;
}



/*============== b)mustchooseone ==============*/

//必须要做一个任务
void RDFW::MustChooseOne(void){
    if(stage==1){
        cout<<"stage=1"<<endl;
        int flag=0;
         for(int i=0;i<tasks.size();i++){
                   if(tasks[i].risk<tasks[flag].risk){
                    flag=i;
                   }
               }
               task_index=flag;
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
        if (!CanStartTask()) return;
        int flag=0;
    
        t++;
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
    if (!CanStartTask()) return;
    // =========================
    // [FINAL] Multi-GOTO 聚合（低风险 hub + 候选筛选 + 上限 10 + 最终停留）
    // =========================
    
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
                int loc = (objects[ObjectId(id)] ? objects[ObjectId(id)]->location : UNKNOWN);
                int risk = (loc != UNKNOWN && loc >= 0) ? goto_cons[LocationId(loc)] : 99;
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
        int loc = (objects[ObjectId(id)] ? objects[ObjectId(id)]->location : UNKNOWN);
        info.goto_risk = (loc != UNKNOWN && loc >= 0) ? goto_cons[LocationId(loc)] : 99;
        // 3. 拿起小物体的约束
        info.pickup_risk = pickup_cons[ObjectId(id)];
        // 4. mustnear 约束（统计所有位置的 mustnear_cons[ObjectId(id)][ObjectId(*)] 之和）
        int mustnear_sum = 0;
        for (int i = 0; i < (int)mustnear_cons[ObjectId(id)].size(); ++i) mustnear_sum += mustnear_cons[ObjectId(id)][ObjectId(i)];
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
        int loc = (objects[ObjectId(id)] ? objects[ObjectId(id)]->location : UNKNOWN);
        info.goto_risk = (loc != UNKNOWN && loc >= 0) ? goto_cons[LocationId(loc)] : 99;
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
        if (id < objects.size() && objects[ObjectId(id)]) {
            int loc = objects[ObjectId(id)]->location;
            if (loc >= 0 && loc < (int)rightlocation.size()) {
                occupied_locations.insert(loc);
            }
        }
    }
    for (auto id : big_cand_ids) {
        if (id < objects.size() && objects[ObjectId(id)]) {
            int loc = objects[ObjectId(id)]->location;
            if (loc >= 0 && loc < (int)rightlocation.size()) {
                occupied_locations.insert(loc);
            }
        }
    }
    for (auto id : small_cand_ids_disable) {
        if (id < objects.size() && objects[ObjectId(id)]) {
            int loc = objects[ObjectId(id)]->location;
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
        info.goto_risk = goto_cons[LocationId(loc)];
        info.move_cons_risks.reserve(small_lowrisk_ids.size());
        info.putdown_cons_risks.reserve(small_lowrisk_ids.size());
        int sum_risk = info.goto_risk;
        for (auto id : small_lowrisk_ids) {
            int move_risk = move_cons[ObjectId(id)][LocationId(loc)];
            int putdown_risk = putdown_cons[ObjectId(id)][LocationId(loc)];
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
        if (info.loc >= 0 && info.loc < (int)rightlocation.size() && rightlocation[LocationId(info.loc)]) {
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
        if (id < objects.size() && objects[ObjectId(id)]) {
            int loc = objects[ObjectId(id)]->location;
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
        rightlocation[LocationId(chosen_loc)] = true;
        LOG(YELLOW "[MultiGoto] smallobj_loc is found: %d\n" RESET, most_smallobj_loc);
    }
    else{
        LOG(YELLOW "[MultiGoto] smallobj_loc is not found: %d\n" RESET, most_smallobj_loc);
    }


    // 1. 在 big_cand_ids 中找约束值最小且小于2的位置

    if(chosen_loc == -1){
    for (auto big_id : big_cand_ids) {
        if (objects[ObjectId(big_id)]) {
            int loc = objects[ObjectId(big_id)]->location;
            // 确保位置可达
            if (loc >= 0 && loc < (int)rightlocation.size() && rightlocation[LocationId(loc)]) {
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
            if (info.loc >= 0 && info.loc < (int)rightlocation.size() && rightlocation[LocationId(info.loc)]) {
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
            if (rightlocation[LocationId(loc)]) {
                chosen_loc = loc;
                LOG(YELLOW "[MultiGoto] No optimal location found, using first available: %d\n" RESET, loc);
                break;
            }
        }
    }
    

    // 验证选择的位置是否可达
    if (chosen_loc == -1 || !rightlocation[LocationId(chosen_loc)]) {
        LOG(RED "[MultiGoto] ERROR: No valid location found! chosen_loc=%d, rightlocation[LocationId(%d)]=%d\n" RESET, 
            chosen_loc, chosen_loc, chosen_loc >= 0 && chosen_loc < (int)rightlocation.size() ? rightlocation[LocationId(chosen_loc)] : -1);
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
                if (id >= objects.size() || !objects[ObjectId(id)]) return 99;
                int loc = objects[ObjectId(id)]->location;
                if (loc == UNKNOWN || loc < 0) return 99;
                return goto_cons[LocationId(loc)];
            };
            auto SafeForIdAt = [&](unsigned id, int h) -> bool {
                if (h < 0) return false;
                return putdown_cons[ObjectId(id)][LocationId(h)] == 0 && move_cons[ObjectId(id)][LocationId(h)] == 0;
            };
            if (ViolationsIfGoto(id) < 2 && SafeForIdAt(id, chosen_loc)) {
                move_set.push_back(id);
            }
        }

        // 没有可搬的，就至少停在 chosen_loc
        if (move_set.empty()) {
            if (location != chosen_loc) Move(LocationId(chosen_loc));
        } else {
            auto in_set = [&](unsigned x){
                return std::find(move_set.begin(), move_set.end(), x) != move_set.end();
            };

            // 护栏：hold/plate 不在集合且跨区会触发 move 约束时，先就地处理
            if (hold_id > 0 && !in_set(hold_id) && move_cons[ObjectId(hold_id)][LocationId(chosen_loc)]) {
                PutDown(ObjectId(hold_id));
            }
            if (plate_id > 0 && !in_set(plate_id) && move_cons[ObjectId(plate_id)][LocationId(chosen_loc)]) {
                if (hold_id > 0) PutDown(ObjectId(hold_id));
                FromPlate(ObjectId(plate_id));
                PutDown(ObjectId(plate_id));
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
                auto sa = std::dynamic_pointer_cast<SmallObject>(objects[ObjectId(a)]);
                auto sb = std::dynamic_pointer_cast<SmallObject>(objects[ObjectId(b)]);
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
                // 直接调用 SolveTask_PutOn ，把小物体移动到 hub
                if (SolveTask_PutOn(id, chosen_loc)) {
                    ++moved;
                    LOG(GREEN "Final-GOTO: moved obj[%u] to hub=%d (%d/%d) (via SolveTask_PutOn)\n" RESET,
                        id, chosen_loc, moved, MULTI_GOTO_LIMIT);
                }
            }

            // 收尾：最终停在 chosen_loc
            if (location != chosen_loc) Move(LocationId(chosen_loc));
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
    if (stage != 2) return false;
    if (!t.isEnable || t.X.empty()) return false;

    const std::string& bh = t.behave;
    auto X0 = t.X[0];
    shared_ptr<Object> Y0 = (t.Y.empty() ? nullptr : t.Y[0]);
    if (!X0) return false;

    if (bh == "open") {
        if (!Y0 && X0) Y0 = X0;
        auto c = std::dynamic_pointer_cast<Container>(Y0);
        return c && IsContainerStateVerified(c->id) && c->isOpen;
    }
    if (bh == "close") {
        if (!Y0 && X0) Y0 = X0;
        auto c = std::dynamic_pointer_cast<Container>(Y0);
        return c && IsContainerStateVerified(c->id) && !c->isOpen;
    }
    if (bh == "goto") {
        return X0->location != UNKNOWN && IsLocationVerified(X0->id) && location == X0->location;
    }
    if (bh == "pickup") {
        return IsInsideVerified(X0->id) && (hold_id == X0->id || plate_id == X0->id);
    }
    if (bh == "putdown") {
        if (hold_id == X0->id || plate_id == X0->id) return false;  // 还拿着/在盘上 -> 未完成
        auto s = std::dynamic_pointer_cast<SmallObject>(X0);
        return s && IsInsideVerified(s->id) && IsLocationVerified(s->id) && s->inside == NONE;
    }
    if (bh == "putin") {
        if (!X0 || !Y0) return false;
        auto s = std::dynamic_pointer_cast<SmallObject>(X0);
        auto c = std::dynamic_pointer_cast<Container>(Y0);
        return s && c && IsInsideVerified(s->id) && s->inside == c->id;
    }
    if (bh == "takeout") {
        if (!Y0) return false;
        auto s = std::dynamic_pointer_cast<SmallObject>(X0);
        return s && IsInsideVerified(s->id) && s->inside != static_cast<int>(Y0->id);
    }
    if (bh == "puton") {
        if (!X0 || !Y0) return false;
        auto s = std::dynamic_pointer_cast<SmallObject>(X0);
        if (!s) return false;
        if (hold_id == s->id || plate_id == s->id) return false; // 手/盘上，不算“已在台面”
        return IsInsideVerified(s->id) && IsLocationVerified(s->id) &&
               IsLocationVerified(Y0->id) && s->inside == NONE &&
               Y0->location != UNKNOWN && s->location == Y0->location;
    }

    return false;
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
    if (isPass || a == 0 || a >= objects.size() || !objects[ObjectId(a)]) return false;
    auto small = dynamic_pointer_cast<SmallObject>(objects[ObjectId(a)]);
    if (!small) return false;

    const int max_attempts = 2;
    string chosen_relation;
    unsigned int chosen_target = 0;
    bool chosen = false;

    for (int attempt = 0; attempt < max_attempts; ++attempt) {
        const string reply = AskLoc(ObjectId(a));
        string relation;
        unsigned int target = 0;
        if (!ParseAskLocationReply(reply, a, relation, target)) continue;
        if (relation == "inside") {
            if (target == 0 || target >= objects.size() || !objects[ObjectId(target)] ||
                !dynamic_pointer_cast<Container>(objects[ObjectId(target)])) continue;
        } else if (target < posSensedFlag.size() && posSensedFlag[LocationId(target)] &&
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
        auto old_cont = dynamic_pointer_cast<Container>(objects[ObjectId(small->inside)]);
        if (old_cont) old_cont->DeleteObjectInside(small);
    }

    if (chosen_relation == "inside") {
        auto cont = dynamic_pointer_cast<Container>(objects[ObjectId(chosen_target)]);
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

    EnsureEvidenceCapacity(a);
    objectLocationVerified[ObjectId(a)] = false;
    objectInsideVerified[ObjectId(a)] = false;
    if (small->location >= 0) {
        EnsureLocationCapacity(small->location);
        posCorrectFlag[LocationId(small->location)] = false;
    }
    return true;
}

// 获取大物体状态。只接受格式正确且对象 ID 匹配的 at 回答。
bool RDFW::GetBigObjectStatus(unsigned int a)
{
    if (isPass || a == 0 || a >= objects.size() || !objects[ObjectId(a)]) return false;
    const int max_attempts = 2;
    unsigned int chosen_location = 0;
    bool chosen = false;

    for (int attempt = 0; attempt < max_attempts; ++attempt) {
        const string reply = AskLoc(ObjectId(a));
        string relation;
        unsigned int target = 0;
        if (!ParseAskLocationReply(reply, a, relation, target) || relation != "at") continue;
        if (target < posSensedFlag.size() && posSensedFlag[LocationId(target)] &&
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
    objects[ObjectId(a)]->location = static_cast<int>(chosen_location);
    if (auto cont = dynamic_pointer_cast<Container>(objects[ObjectId(a)])) {
        for (const auto& item : cont->smallObjectsInside) {
            if (item) item->location = cont->location;
        }
    }
    EnsureEvidenceCapacity(a);
    objectLocationVerified[ObjectId(a)] = false;
    posCorrectFlag[LocationId(chosen_location)] = false;
    return true;
}

// 单次询问。重试与一致性判断由调用方控制，保证每条调用链都有明确上限。
std::string RDFW::AskLoc(ObjectId target)
{
    const int a = target.value();
    if (!CanStartTask() || isPass || a == 0 || a >= objects.size() || !objects[ObjectId(a)]) return "";
    BeforeAction("AskLoc");
    const string str = Plug::AskLoc(a);
    if (task_index >= 0 && static_cast<size_t>(task_index) < tasks.size())
        tasks[task_index].ask_times++;
    LOG("AskLoc(%d)", a);
    if (str.empty())
        LOG_ERROR("AskLoc returned empty string for object (%d,%s)", a, objects[ObjectId(a)]->sort.c_str());
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
    
    if (!force && posSensedFlag[LocationId(curr_loc)]) {
        LOG(YELLOW "[SenseCurrentLocationOnly] Location %d already sensed, skipping to avoid redundancy\n" RESET, curr_loc);
        return;
    }

    // 感知当前位置的物体
    vector<unsigned int> sensed_ids;
    BeforeAction("Sense");
    Plug::Sense(sensed_ids);

    // 标记当前位置已感知
    if (curr_loc >= posSensedFlag.size()) {
        posSensedFlag.resize(curr_loc + 1, false);
        locationSensedObjects.resize(curr_loc + 1);  // 同时扩展物体记录数组
    }
    posSensedFlag[LocationId(curr_loc)] = true;
    
    // 清空当前位置的感知记录，准备记录新的感知结果
    locationSensedObjects[LocationId(curr_loc)].object_ids.clear();
    locationSensedObjects[LocationId(curr_loc)].container_id = 0;
    locationSensedObjects[LocationId(curr_loc)].has_container = false;
    
    LOG(GREEN "[SenseCurrentLocationOnly] Location %d marked as sensed\n" RESET, curr_loc);

    // 遍历感知到的物体，更新其位置
    for (auto id : sensed_ids) {
        if (id > 0 && id < objects.size() && objects[ObjectId(id)] != nullptr) {
            objects[ObjectId(id)]->location = curr_loc;
            EnsureEvidenceCapacity(id);
            objectLocationVerified[ObjectId(id)] = true;
            
            // 记录感知到的物体ID
            locationSensedObjects[LocationId(curr_loc)].object_ids.push_back(id);
            
            auto cont = std::dynamic_pointer_cast<Container>(objects[ObjectId(id)]);
            if (cont) {
                // 记录容器ID和标记有容器（一个位置只能有一个大物体）
                locationSensedObjects[LocationId(curr_loc)].container_id = id;
                locationSensedObjects[LocationId(curr_loc)].has_container = true;
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
        if (id == 0 || id >= objects.size() || !objects[ObjectId(id)]) continue;
        auto small = dynamic_pointer_cast<SmallObject>(objects[ObjectId(id)]);
        if (!small || static_cast<int>(id) == hold_id || static_cast<int>(id) == plate_id) continue;
        EnsureEvidenceCapacity(id);

        bool visible_container_is_open = false;
        if (sensed_container_id > 0 && sensed_container_id < objects.size()) {
            auto visible_container = dynamic_pointer_cast<Container>(objects[ObjectId(sensed_container_id)]);
            visible_container_is_open = visible_container && visible_container->isOpen;
        }

        const bool relation_is_ambiguous =
            small->inside == static_cast<int>(sensed_container_id) && visible_container_is_open;
        if (relation_is_ambiguous) {
            objectInsideVerified[ObjectId(id)] = false;
            continue;
        }

        if (small->inside > 0 && static_cast<size_t>(small->inside) < objects.size()) {
            auto old_container = dynamic_pointer_cast<Container>(objects[ObjectId(small->inside)]);
            if (old_container) old_container->DeleteObjectInside(small);
        }
        small->inside = NONE;
        objectInsideVerified[ObjectId(id)] = true;
    }
    
    // 检查原本应该在这个位置但没被感知到的物体
    // 1. 标记已感知到的物体（包括容器内的物体）
    std::vector<bool> sensed(objects.size(), false);
    for (auto id2 : locationSensedObjects[LocationId(curr_loc)].object_ids) {
        if (id2 > 0 && id2 < objects.size() && objects[ObjectId(id2)] != nullptr) {
            sensed[id2] = true;
        }
    }
    
    // 2.检查这个容器是否开着
    bool container_is_open = false;
    if (sensed_container_id > 0 && sensed_container_id < objects.size() && objects[ObjectId(sensed_container_id)] != nullptr) {
        auto cont = std::dynamic_pointer_cast<Container>(objects[ObjectId(sensed_container_id)]);
        if (cont) {
            container_is_open = cont->isOpen;
        }
    }

    // 直接按照位置找，找到标记为在这个位置的所谓物体id
    std::vector<unsigned int> ids_at_curr_loc;
    for (unsigned int i = 1; i < objects.size(); ++i) {
        if (!objects[ObjectId(i)]) continue;
        if (static_cast<int>(i) == hold_id || static_cast<int>(i) == plate_id) continue;
        if (objects[ObjectId(i)]->location == curr_loc) {
            ids_at_curr_loc.push_back(i);
        }
    }

    if(sensed_container_id == NONE || container_is_open == true){
        for (auto id : ids_at_curr_loc) {
            if (!sensed[id]) {
                objects[ObjectId(id)]->location = UNKNOWN;
                EnsureEvidenceCapacity(id);
                objectLocationVerified[ObjectId(id)] = false;
                LOG(YELLOW "[SenseCurrentLocationOnly] Object id=%u expected at %d but not sensed, set location UNKNOWN\n" RESET, id, curr_loc);
            }
        }
    }
    else{
        for (auto id : ids_at_curr_loc) {
            bool in_container = false;
            // 检查是否是小物体且在容器内
            auto small = std::dynamic_pointer_cast<SmallObject>(objects[ObjectId(id)]);
            if (small && small->inside == sensed_container_id) {
                in_container = true;
            }
            
            if (!sensed[id] && !in_container) {
                objects[ObjectId(id)]->location = UNKNOWN;
                EnsureEvidenceCapacity(id);
                objectLocationVerified[ObjectId(id)] = false;
                LOG(YELLOW "[SenseCurrentLocationOnly] Object id=%u expected at %d but not sensed, set location UNKNOWN\n" RESET, id, curr_loc);
            }
        }
    }
}
// 位置感知物体记录访问函数实现
const RDFW::LocationSensedInfo& RDFW::GetLocationSensedInfo(int location) const {
    static RDFW::LocationSensedInfo empty_info;  // 返回空结构体作为默认值
    if (location >= 0 && location < locationSensedObjects.size()) {
        return locationSensedObjects[LocationId(location)];
    }
    return empty_info;
}

bool RDFW::HasObjectAtLocation(int location, unsigned int object_id) const {
    if (location >= 0 && location < locationSensedObjects.size()) {
        const auto& info = locationSensedObjects[LocationId(location)];
        for (auto id : info.object_ids) {
            if (id == object_id) return true;
        }
    }
    return false;
}

bool RDFW::HasContainerAtLocation(int location) const {
    if (location >= 0 && location < locationSensedObjects.size()) {
        return locationSensedObjects[LocationId(location)].has_container;
    }
    return false;
}

vector<unsigned int> RDFW::GetObjectsAtLocation(int location) const {
    if (location >= 0 && location < locationSensedObjects.size()) {
        return locationSensedObjects[LocationId(location)].object_ids;
    }
    return vector<unsigned int>();
}

unsigned int RDFW::GetContainerAtLocation(int location) const {
    if (location >= 0 && location < locationSensedObjects.size()) {
        return locationSensedObjects[LocationId(location)].container_id;
    }
    return 0;
}


//感知大物体是否在当前位置
bool RDFW::sense(unsigned int t) //返回值表示t对应的大物体是否在当前位置
{

    vector<unsigned int> A_;

    BeforeAction("Sense");
    Plug::Sense(A_);
    LOG("Sense");
    int flagg = 0;
    // 用“感知到的对象 id”安全地更新
    for (auto id : A_) {
        if (t == id) flagg = 1;
        if (id < objects.size() && objects[ObjectId(id)]) {
            if (objects[ObjectId(id)]->location != location) {
                objects[ObjectId(id)]->location = location;
                if (auto cont = std::dynamic_pointer_cast<Container>(objects[ObjectId(id)])) {
                    for (auto &sp : cont->smallObjectsInside) {
                        if (sp) sp->location = location;
                    }
                }
                // 小物体分支无需强制改 inside，这里保持原有逻辑不动
            }
            EnsureEvidenceCapacity(id);
            objectLocationVerified[ObjectId(id)] = true;
        }
    }
    return flagg;


}

//查找合适的位置
int RDFW::findrightlocation(unsigned int a)
{
    if (a >= move_cons.size() || a >= putdown_cons.size()) return UNKNOWN;
    for(int i=0;i<(int)rightlocation.size();i++){
        if (!rightlocation[LocationId(i)]) continue;
        if (i >= (int)move_cons[ObjectId(a)].size() || i >= (int)putdown_cons[ObjectId(a)].size()) continue;
        if (i >= (int)goto_cons.size()) continue;
        if (goto_cons[LocationId(i)] == 0 && move_cons[ObjectId(a)][LocationId(i)] == 0 && putdown_cons[ObjectId(a)][LocationId(i)] == 0)
            return i;
    }
	return UNKNOWN;
}

//判断小物体是否在容器里面
bool RDFW::Isinside(unsigned int a, unsigned int b){
    auto small = ObjectPtrCast<SmallObject>(objects[ObjectId(a)]);
    if(small->inside==objects[ObjectId(b)]->id) return true;
    else return false;
}


//判断任务是否继续---跟违反的约束有关
bool RDFW::IsKeepingGoing(unsigned int index){
    CheckBudget();
    if (index >= tasks.size() || tasks[index].X.empty() || !tasks[index].X[0]) return false;
    auto &t=tasks[index];
    t.risk=0;
      if(t.behave=="takeout")
      {
        auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
        if(small->inside==t.Y[0]->id){ //如果任务没有满足
            const int target_location = t.Y[0]->location;
            if (target_location >= 0) EnsureLocationCapacity(target_location);
        t.risk+=takeout_cons[ObjectId(t.X[0]->id)][ObjectId(t.Y[0]->id)];
        if (target_location >= 0) t.risk+=goto_cons[LocationId(target_location)];
        t.risk+=open_cons[ObjectId(t.Y[0]->id)];
            }
            }

        else if(t.behave=="putin") {
            auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
             if(small->inside!=t.Y[0]->id) //如果任务没有满足
             {
                const int target_location = t.Y[0]->location;
                if (target_location >= 0) EnsureLocationCapacity(target_location);
               t.risk+=putin_cons[ObjectId(t.X[0]->id)][ObjectId(t.Y[0]->id)]+open_cons[ObjectId(t.Y[0]->id)];
               if (target_location >= 0) {
                   t.risk+=move_cons[ObjectId(t.X[0]->id)][LocationId(target_location)];
                   if(t.X[0]->location!=target_location) t.risk+=goto_cons[LocationId(target_location)];
               }
               CalculateStepRisk(t);
              }
         }
         else if(t.behave=="puton") {
             const int target_location = t.Y[0]->location;
             if (target_location >= 0) EnsureLocationCapacity(target_location);
             t.risk+=putdown1_cons[ObjectId(t.X[0]->id)];
             if (target_location >= 0) {
                 t.risk+= putdown_cons[ObjectId(t.X[0]->id)][LocationId(target_location)]+move_cons[ObjectId(t.X[0]->id)][LocationId(target_location)];
                 if(t.X[0]->location!=target_location) t.risk+=goto_cons[LocationId(target_location)];
             }
           CalculateStepRisk(t);
         }
         else if(t.behave=="goto" && t.X[0]->location >= 0) t.risk+=goto_cons[LocationId(t.X[0]->location)];
         else if(t.behave=="open") {
             t.risk+=open_cons[ObjectId(t.X[0]->id)];
             if (t.X[0]->location >= 0) t.risk+=goto_cons[LocationId(t.X[0]->location)];
         }
         else if(t.behave=="close") {
             t.risk+=close_cons[ObjectId(t.X[0]->id)];
             if (t.X[0]->location >= 0) t.risk+=goto_cons[LocationId(t.X[0]->location)];
         }
         else if(t.behave=="pickup") {
            CalculateStepRisk(t);
         }
         else if(t.behave=="give") {
            CalculateStepRisk(t);
            t.risk+=givehuman_cons[ObjectId(t.X[0]->id)]+putdown1_cons[ObjectId(t.X[0]->id)];
            if (human && human->location >= 0) {
                t.risk+=move_cons[ObjectId(t.X[0]->id)][LocationId(human->location)];
                if(t.X[0]->location!=human->location) t.risk+=goto_cons[LocationId(human->location)];
            }
            auto small=dynamic_pointer_cast<SmallObject>(t.X[0]);
         }
         else if(t.behave == "putdown")t.risk+=putdown1_cons[ObjectId(t.X[0]->id)];
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
bool RDFW::TakeOut(ObjectId small_id, ObjectId container_id)
{
    const int a = small_id.value();
    const int b = container_id.value();
    auto small = ObjectPtrCast<SmallObject>(objects[ObjectId(a)]);
    auto cont = ObjectPtrCast<Container>(objects[ObjectId(b)]);
    LOG("TakeOut(%d,%s)(%d,%s)", a, small->sort.c_str(), b, cont->sort.c_str());
    BeforeAction("TakeOut");
    if (Plug::TakeOut(a, b))
    {
        small->inside = NONE;
        small->location = location;
        cont->DeleteObjectInside(small);
        cont->isOpen=1;
        SetHold(small);
        EnsureEvidenceCapacity(a);
        EnsureEvidenceCapacity(b);
        objectLocationVerified[ObjectId(a)] = true;
        objectInsideVerified[ObjectId(a)] = true;
        objectLocationVerified[ObjectId(b)] = true;
        containerStateVerified[ObjectId(b)] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("takeout", objects[ObjectId(a)], objects[ObjectId(b)]);
        takeout_cons[ObjectId(a)][ObjectId(b)]=0;
        return 1;
    }
    return 0;
}

bool RDFW::PutIn(ObjectId small_id, ObjectId container_id)
{
    const int a = small_id.value();
    const int b = container_id.value();
    auto cont = ObjectPtrCast<Container>(objects[ObjectId(b)]);
    auto small = ObjectPtrCast<SmallObject>(objects[ObjectId(a)]);
    if (!cont || !small) return 0; // 直接早退，避免 LOG 解引用空指针
    LOG("PutIn(%d,%s)(%d,%s)", a,small->sort.c_str() , b, cont->sort.c_str());
    BeforeAction("PutIn");
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
        objectLocationVerified[ObjectId(a)] = true;
        objectInsideVerified[ObjectId(a)] = true;
        objectLocationVerified[ObjectId(b)] = true;
        containerStateVerified[ObjectId(b)] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("putin", objects[ObjectId(a)], objects[ObjectId(b)]);
        putin_cons[ObjectId(a)][ObjectId(b)]=0;
        open_cons[ObjectId(b)]=0;
        return 1;
    }
    return 0;
}
bool RDFW::Close(ObjectId target)
{
    const int a = target.value();
    shared_ptr<Container> container = ObjectPtrCast<Container>(objects[ObjectId(a)]);
    if (!container) return 0;
    LOG("(%d,%s) has closed", a, container->sort.c_str());
    BeforeAction("Close");
    if (Plug::Close(a))
    {
        container->isOpen = false;
        EnsureEvidenceCapacity(a);
        objectLocationVerified[ObjectId(a)] = true;
        containerStateVerified[ObjectId(a)] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("close", objects[ObjectId(a)]);
        objects[ObjectId(a)]->is_keep=0;
        close_cons[ObjectId(a)]=0;
        return 1;
    }
    return 0;
}
bool RDFW::Open(ObjectId target)
{
    const int a = target.value();
    shared_ptr<Container> container = ObjectPtrCast<Container>(objects[ObjectId(a)]);
    if (!container) return 0;
    LOG("Open(%d,%s)", a, container->sort.c_str());
    BeforeAction("Open");
    if (Plug::Open(a))
    {
        container->isOpen = true;
        EnsureEvidenceCapacity(a);
        objectLocationVerified[ObjectId(a)] = true;
        containerStateVerified[ObjectId(a)] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("open", objects[ObjectId(a)]);
        open_cons[ObjectId(a)]=0;
        objects[ObjectId(a)]->is_keep=0;
        return 1;
    }
    return 0;
}
bool RDFW::FromPlate(ObjectId target)
{
    const int a = target.value();   
    LOG("FromPlate(%d,%s)", a, objects[ObjectId(a)]->sort.c_str());
    BeforeAction("FromPlate");
    if (Plug::FromPlate(a))
    {
        SetHold(plate);
        SetPlate(nullptr);
        EnsureEvidenceCapacity(a);
        objectLocationVerified[ObjectId(a)] = true;
        objectInsideVerified[ObjectId(a)] = true;
        InvalidateSenseAtLocation(location);
        return 1;
    }
    fromplate_cons[ObjectId(a)]=0;
    return 0;
}
bool RDFW::ToPlate(ObjectId target)
{
    const int a = target.value();
    LOG("ToPlate(%d,%s)", a, objects[ObjectId(a)]->sort.c_str());
    BeforeAction("ToPlate");
    if (Plug::ToPlate(a))
    {
        SetPlate(hold);
        SetHold(nullptr);
        EnsureEvidenceCapacity(a);
        objectLocationVerified[ObjectId(a)] = true;
        objectInsideVerified[ObjectId(a)] = true;
        InvalidateSenseAtLocation(location);
        toplate_cons[ObjectId(a)]=0;
        return 1;
    }
    return 0;
}

bool RDFW::PutDown(ObjectId target)
{
    const int a = target.value();
    LOG("PutDown(%d,%s)", a, objects[ObjectId(a)]->sort.c_str());
    BeforeAction("PutDown");
    if (Plug::PutDown(a))
    {
        SetHold(nullptr);
        auto small = dynamic_pointer_cast<SmallObject>(objects[ObjectId(a)]);
        if (small) {
            small->location = location;
            small->inside = NONE;
        }
        EnsureEvidenceCapacity(a);
        objectLocationVerified[ObjectId(a)] = true;
        objectInsideVerified[ObjectId(a)] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("putdown", objects[ObjectId(a)]);
        putdown1_cons[ObjectId(a)]=0;
        EnsureLocationCapacity(location);
        putdown_cons[ObjectId(a)][LocationId(location)]=0;
        return 1;
    }
    return 0;
}
bool RDFW::PickUp(ObjectId target)
{
    const int a = target.value();
    auto small = ObjectPtrCast<SmallObject>(objects[ObjectId(a)]);
    if (!small) return 0;
    LOG("PickUp(%d,%s)", small->id, small->sort.c_str());
    BeforeAction("PickUp");
    if (Plug::PickUp(a))
    {
        SetHold(small);
        small->location = location;
        small->inside = NONE;
        EnsureEvidenceCapacity(a);
        objectLocationVerified[ObjectId(a)] = true;
        objectInsideVerified[ObjectId(a)] = true;
        InvalidateSenseAtLocation(location);
        UpdateTaskList("pickup", objects[ObjectId(a)]);
        pickup_cons[ObjectId(a)]=0;
        return 1;
    }
    return 0;
}


bool RDFW::Move(LocationId target)
{
    const int a = target.value();
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
        return (id > 0 && id < objects.size() && objects[ObjectId(id)] != nullptr);
    };
    auto hit_move_cons = [&](unsigned id, unsigned loc)->bool {
        if (!safe_idx(id)) return false;
        if ((int)loc < 0 || (int)loc >= (int)rightlocation.size()) return false;
        // 检查二维数组边界
        if (id >= move_cons.size() || loc >= move_cons[ObjectId(id)].size()) return false;
        return move_cons[ObjectId(id)][LocationId(loc)] != 0;
    };

    // 4) 跨区前的"自清理"：手持/托盘若会触发 move 约束，先放下/取下
    if (hold_id > 0 && hit_move_cons(hold_id, a)) {
        if (!has_taskX0 || tasks[task_index].X[0]->id != hold_id) {
            PutDown(ObjectId(hold_id));
        }
    }
    if (plate_id > 0 && hit_move_cons(plate_id, a)) {
        if (hold_id > 0) PutDown(ObjectId(hold_id));
        FromPlate(ObjectId(plate_id));
        if (hold_id > 0) PutDown(ObjectId(hold_id));
    }

    // 5) 真正移动
    const int previous_location = location;
    BeforeAction("Move");
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
        EnsureEvidenceCapacity(hold_id);
        objectLocationVerified[ObjectId(hold_id)] = true;
    }
    if (plate_id > 0) {
        EnsureEvidenceCapacity(plate_id);
        objectLocationVerified[ObjectId(plate_id)] = true;
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
    goto_cons[LocationId(a)] = 0;                          // a 边界在上面已保证
    if (hold_id > 0 && safe_idx(hold_id)) {
        move_cons[ObjectId(hold_id)][LocationId(a)] = 0;
        objects[ObjectId(hold_id)]->is_keep = 0;
    }

    // 正确地把“当前任务的目标对象”传给 UpdateTaskList
    if (has_taskX0) {
        UpdateTaskList("goto", tasks[task_index].X[0]);  // ✅ 用任务里的那个对象
    }
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
         bool is_corr = (i >= 0 && i < (int)posCorrectFlag.size()) ? (posCorrectFlag[LocationId(i)] == true) : true;
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
            EnsureObjectCapacity(ObjectId(lastSize - 1));
        }

        auto &obj = objects[ObjectId(index)];

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
            if (L >= 0) rightlocation[LocationId(L)] = 1;
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
        SetHold(ObjectPtrCast<SmallObject>(objects[ObjectId(hold_id)]));
        EnsureEvidenceCapacity(hold_id);
        objectLocationVerified[ObjectId(hold_id)] = true;
        objectInsideVerified[ObjectId(hold_id)] = true;
    }
    if (plate_id > 0)
    {
        SetPlate(ObjectPtrCast<SmallObject>(objects[ObjectId(plate_id)]));
        EnsureEvidenceCapacity(plate_id);
        objectLocationVerified[ObjectId(plate_id)] = true;
        objectInsideVerified[ObjectId(plate_id)] = true;
    }

    for (const auto &s : smallObjects)
    {
        if (s == plate || s == hold)
            continue;
        if (s->inside != UNKNOWN && s->inside != NONE)
        {
            auto p = dynamic_pointer_cast<Container>(objects[ObjectId(s->inside)]);
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
    if(task.behave=="pickup") for(int i=0;i<(int)pickup_cons.size();i++) pickup_cons[ObjectId(i)]+=2;
    else if(task.behave=="putdown") pickup_cons[ObjectId(task.X[0]->id)]+=2;
    else if(task.behave=="takeout") putin_cons[ObjectId(task.X[0]->id)][ObjectId(task.Y[0]->id)]+=2;
    else if(task.behave=="putin") takeout_cons[ObjectId(task.X[0]->id)][ObjectId(task.Y[0]->id)]+=2;
//这里要删除
//    else if(task.behave=="goto") for(int i=0;i<50;i++) goto_cons[LocationId(i)]+=2;
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
    objectInsideVerified.clear();
    containerStateVerified.clear();
    errorlist.clear();
    lock_by_mustnear.clear();
    
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
    objectInsideVerified.shrink_to_fit();
    containerStateVerified.shrink_to_fit();
    errorlist.shrink_to_fit();
    lock_by_mustnear.shrink_to_fit();
    
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
    
    // 清理任务查找表
    for (auto& row : takeout) fill(row.begin(), row.end(), false);
    for (auto& row : putin) fill(row.begin(), row.end(), false);
    fill(close.begin(), close.end(), false);
    fill(open.begin(), open.end(), false);
    fill(pickup.begin(), pickup.end(), false);
    fill(putdown.begin(), putdown.end(), false);
    
    // ==================== 感知状态完全重置 ====================
    posSensedFlag.resize(100, false);
    objectLocationVerified.resize(100, false);
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
    objectInsideVerified.shrink_to_fit();
    containerStateVerified.shrink_to_fit();
    errorlist.shrink_to_fit();
    lock_by_mustnear.shrink_to_fit();
    
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
    
    // 优化任务查找表内存
    for (auto& row : takeout) row.shrink_to_fit();
    for (auto& row : putin) row.shrink_to_fit();
    close.shrink_to_fit();
    open.shrink_to_fit();
    pickup.shrink_to_fit();
    putdown.shrink_to_fit();
    
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
 void RDFW::ApplyMustNearConstraintCorrection(){

    const int numObjs = static_cast<int>(objects.size());

     if (!enable_near_correction) {
         LOG(YELLOW "[MustNear] disabled\n" RESET);
         return;
     }

     if (numObjs == 0) {
         LOG(YELLOW "[MustNear] no objects\n" RESET);
         return;
     }
 
     // 并查集：局部化，避免类里再放 uf_parent/size 等成员
     std::vector<int> parent(numObjs), sz(numObjs, 1);
     std::iota(parent.begin(), parent.end(), 0);
 
     auto find = [&](int x) {
         while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
         return x;
     };
     auto unite = [&](int a, int b) {
         a = find(a); b = find(b);
         if (a == b) return;
         if (sz[a] < sz[b]) std::swap(a, b);
         parent[b] = a; sz[a] += sz[b];
     };
 
     // 1) 收集 must near 约束并合并等价类
     for (const auto &cons : notnot_infoConstrains) {
         CheckBudget();
        if ((cons.behave == "near"||cons.behave == "on"||cons.behave == "nextto") && !cons.X.empty() && !cons.Y.empty()) {
            if(cons.X[0]->id==hold_id) hold_mustnear = true;
            if(cons.X[0]->id==plate_id) plate_mustnear = true;
            if(cons.Y[0]->id==hold_id) hold_mustnear = true;
            if(cons.Y[0]->id==plate_id) plate_mustnear = true;
            if(cons.X[0]->location!=cons.Y[0]->location){
            // INSERT_YOUR_CODE
            // 分别统计cons.X[0]和cons.Y[0]的near/notnear情况
            // cons.X[0] 在它自己位置上的物体统计
            int x_near_status = 0; // 0=无, 1=有near, 2=有notnear
            int y_near_status = 0;
            int xloc = cons.X[0]->location;
            int yloc = cons.Y[0]->location;

            // 如果有对象在 xloc, 判断是否有near或notnear关系
            for (const auto& obj : objects) {
                if (!obj) continue;
                if (obj->id == cons.X[0]->id) continue;
                if (obj->location == xloc) {
                    // 判断 cons.X[0] 与 obj 的 near/notnear 关系
                    // 检查 notnot_infoConstrains
                    for (const auto& c2 : notnot_infoConstrains) {
                        if (
                            (c2.behave == "near" || c2.behave == "on"||c2.behave == "nextto") &&
                            !c2.X.empty() && !c2.Y.empty() &&
                            (
                                (c2.X[0]->id == cons.X[0]->id && c2.Y[0]->id == obj->id) ||
                                (c2.Y[0]->id == cons.X[0]->id && c2.X[0]->id == obj->id)
                            )
                        ) {
                            x_near_status = 1;
                            break;
                        }
                    }
                    // 检查 not_infoConstrains
                    for (const auto& c2 : not_infoConstrains) {
                        if (
                            (c2.behave == "near" || c2.behave == "on"||c2.behave == "nextto") &&
                            !c2.X.empty() && !c2.Y.empty() &&
                            (
                                (c2.X[0]->id == cons.X[0]->id && c2.Y[0]->id == obj->id) ||
                                (c2.Y[0]->id == cons.X[0]->id && c2.X[0]->id == obj->id)
                            )
                        ) {
                            x_near_status = 2;
                            break;
                        }
                    }
                    if (x_near_status) break;
                }
            }
            // 如果有对象在 yloc, 判断是否有near或notnear关系
            for (const auto& obj : objects) {
                if (!obj) continue;
                if (obj->id == cons.Y[0]->id) continue;
                if (obj->location == yloc) {
                    // 判断 cons.Y[0] 与 obj 的 near/notnear 关系
                    // 检查 notnot_infoConstrains
                    for (const auto& c2 : notnot_infoConstrains) {
                        if (
                            (c2.behave == "near" || c2.behave == "on"||c2.behave == "nextto") &&
                            !c2.X.empty() && !c2.Y.empty() &&
                            (
                                (c2.X[0]->id == cons.Y[0]->id && c2.Y[0]->id == obj->id) ||
                                (c2.Y[0]->id == cons.Y[0]->id && c2.X[0]->id == obj->id)
                            )
                        ) {
                            y_near_status = 1;
                            break;
                        }
                    }
                    // 检查 not_infoConstrains
                    for (const auto& c2 : not_infoConstrains) {
                        if (
                            (c2.behave == "near" || c2.behave == "on"||c2.behave == "nextto") &&
                            !c2.X.empty() && !c2.Y.empty() &&
                            (
                                (c2.X[0]->id == cons.Y[0]->id && c2.Y[0]->id == obj->id) ||
                                (c2.Y[0]->id == cons.Y[0]->id && c2.X[0]->id == obj->id)
                            )
                        ) {
                            y_near_status = 2;
                            break;
                        }
                    }
                    if (y_near_status) break;
                }
            }
            // 统计完成，如需将结果用于后续逻辑或输出可在后面使用 x_near_status, y_near_status
            if(x_near_status==2&&y_near_status!=2){
                cons.X[0]->location = cons.Y[0]->location;
                LOG(GREEN "[MustNear] set obj %d location to %d\n" RESET, cons.X[0]->id, cons.Y[0]->location);
            }
            else if(x_near_status!=2&&y_near_status==2){
                cons.Y[0]->location = cons.X[0]->location;
                LOG(GREEN "[MustNear] set obj %d location to %d\n" RESET, cons.Y[0]->id, cons.X[0]->location);
            }
             unite(cons.X[0]->id, cons.Y[0]->id);
             LOG(GREEN "[MustNear] union %u ~ %u\n" RESET, cons.X[0]->id, cons.Y[0]->id);
         }
     }
    }
     // 2) 按“已知位置”给每个组投票（root -> loc->count）
     std::unordered_map<int, std::unordered_map<int,int>> vote;
     vote.reserve(numObjs);
     for (int i = 0; i < numObjs; ++i) {
         if (!objects[ObjectId(i)]) continue;
         const int loc = objects[ObjectId(i)]->location;
         if (loc == UNKNOWN) continue;
         vote[find(i)][loc]++;   // root 组对 loc 投票 +1
     }
 
     // 3) 选出每个组的“多数位置”；若无人投票则保持 UNKNOWN
     std::vector<int> groupChosen(numObjs, UNKNOWN);
     for (auto &kv : vote) {
         const int root = kv.first;
         int bestLoc = UNKNOWN, bestCnt = -1;
         for (auto &lc : kv.second) {
             if (lc.second > bestCnt || (lc.second == bestCnt && lc.first < bestLoc)) {
                 bestCnt = lc.second;
                 bestLoc = lc.first; // 少数服从多数；平票取更小的 loc
             }
         }
         groupChosen[root] = bestLoc;
     }
 
     // 4)（可选）上锁：把一个组内的所有对象位置改到"多数位置"，并打锁位标记
     lock_by_mustnear.assign(numObjs, false);
     if (enable_must_lock) {
         for (int i = 0; i < numObjs; ++i) {
             const int root = find(i);
             const int loc  = groupChosen[root];
             if (loc == UNKNOWN) continue;  // 该组没有确定位置，跳过
             if (!objects[ObjectId(i)]) continue;
             objects[ObjectId(i)]->location   = loc;
             lock_by_mustnear[i]    = true;
             LOG(GREEN "[MustNear] lock obj[%d] @ %d\n" RESET, i, loc);
         }
     }
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
            if (objects[ObjectId(x)]) {
                if (auto sm = std::dynamic_pointer_cast<SmallObject>(objects[ObjectId(x)])) {
                    cout<<"sm->inside: "<<sm->inside<<endl;
                    // 移除在原容器中的记录
                    if (sm->inside != UNKNOWN && sm->inside != y) {
                        if (sm->inside >= 0 && sm->inside < numObjs) {
                            if (auto old_cont = std::dynamic_pointer_cast<Container>(objects[ObjectId(sm->inside)])) {
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
                    if (objects[ObjectId(y)]) {
                        if (auto cont = std::dynamic_pointer_cast<Container>(objects[ObjectId(y)])) {
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
            if (objects[ObjectId(x)] && objects[ObjectId(y)]) {
                int y_loc = objects[ObjectId(y)]->location;
                if (y_loc != UNKNOWN) {
                    objects[ObjectId(x)]->location = y_loc;
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
        auto smObj = std::dynamic_pointer_cast<SmallObject>(objects[ObjectId(x)]);
        if (!smObj) continue;
        // 如果x当前就在y里，需要移除
        if (smObj->inside == y) {
            // 修改smallObject的inside信息
            smObj->inside = UNKNOWN;
            int old_loc = smObj->location;
            smObj->location = UNKNOWN;
            // 同时尝试从container的smallObjectsInside中移除
            auto cont = std::dynamic_pointer_cast<Container>(objects[ObjectId(y)]);
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
