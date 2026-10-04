// Reproduces a remaining defect; this is NOT a correctness-passing test.
#include "rdfw.hpp"
#include <cassert>
#include <iostream>
using namespace _home;
int main(int argc,char**argv) {
    assert(argc==2);
    auto w=std::make_shared<RDFW>();
    char n[]="goto_projection",p[]="-path";char*args[]={n,p,argv[1]};
    w->Init(3,args);w->stage=1;
    assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) "
        "(sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 table) (size 2 big) (at 2 2) "
        "(sort 4 cupboard) (size 4 big) (type 4 container) (at 4 1) (closed 4) "
        "(sort 3 cup) (size 3 small) (at 3 2) (inside 3 4)"));
    w->stage=2; // all input relations qualified first; isolate projection only
    Instruction delivered;delivered.behave="puton";delivered.X={w->objects[3]};
    delivered.Y={w->objects[2]};delivered.isUseY=true;
    Instruction go;go.behave="goto";go.X={w->objects[2]};
    w->tasks={delivered,go};
    TerminalChecker checker;
    assert(checker.evaluateTask(*w,w->tasks[0])==TerminalStatus::SATISFIED);
    const std::string before=w->DebugStateSnapshot();
    const CandidatePlan plan=w->PreviewTaskGroupPlan({1});
    std::cout<<"dry_run="<<plan.dry_run_succeeded<<" utility="<<plan.marginal_score
             <<" gained="<<plan.gained_goals.size()<<" lost="<<plan.lost_goals.size()<<"\n";
    for(const auto&a:plan.actions) std::cout<<a.name<<"\n";
    assert(w->DebugStateSnapshot()==before);
    assert(plan.dry_run_succeeded && plan.gained_goals==std::vector<std::size_t>{1});
    assert(plan.lost_goals==std::vector<std::size_t>{0} && plan.marginal_score==-5);
    std::cout<<"REMAINING_DEFECT_REPRODUCED: virtual Sense loses delivered cup while returning\n";
}
