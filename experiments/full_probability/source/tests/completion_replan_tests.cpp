#include "rdfw.hpp"
#include <cassert>
#include <memory>
#include <sstream>
using namespace _home;
int main(int argc,char** argv) {
    assert(argc==2);auto w=std::make_shared<RDFW>();
    char name[]="completion_replan",path[]="-path";char* args[]={name,path,argv[1]};w->Init(3,args);
    w->stage=1;
    std::ostringstream env,ins;env<<"(hold 0) (plate 0) (at 0 0) (sort 1 human) (size 1 big) (at 1 0) ";
    for(unsigned id=2;id<=8;++id) {
        env<<"(sort "<<id<<" cupboard) (size "<<id<<" big) (type "<<id<<" container) (at "<<id<<' '<<id-1<<") (closed "<<id<<") ";
        ins<<"(:task (open X) (:cond (id X "<<id<<"))) ";
    }
    w->SetTestInput(env.str(),ins.str());
    // All seven actions in one projected route exceed this horizon. Real stub
    // calls finish immediately, so a validated partial group leaves time for
    // a second decision. Completing one group is not proof all goals are done.
    const_cast<DeadlineManager&>(w->GetDeadlineManager()).reset(std::chrono::milliseconds(1600));
    w->Plan();
    assert(w->GetTerminalSummary().allGoalsSatisfied());
    assert(w->GetTerminalSummary().satisfied_goals==7);
    assert(w->DecisionFeedback().size()>=2 && w->TestPlatformCalls()==14);
    assert(w->GetScoreSnapshot().deterministic_base_score==238);
    assert(w->ActionReceipts().size()==14);
}
