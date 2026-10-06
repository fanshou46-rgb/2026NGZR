#include "rdfw.hpp"
#include <cassert>
#include <iostream>
using namespace _home;
namespace _home {struct ScoreSemanticsTestAccess {
    // An unstarted manager has elapsed=0: tests the exact policy boundary
    // without scheduler noise or adding a production clock abstraction.
    static void ExactBudget(RDFW& w,int ms) {w.deadline_manager=DeadlineManager(std::chrono::milliseconds(ms));}
    static bool Fits(RDFW& w,const CandidatePlan& p) {return w.CanStartPlan(p,"sensitivity-test");}
};}
int main(int argc,char** argv) {
    const int safety_margin_ms=200;
    assert(argc==2);auto w=std::make_shared<RDFW>();char name[]="deadline",path[]="-path";char* args[]={name,path,argv[1]};
    w->Init(3,args);w->stage=1;
    assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 cupboard) (size 1 big) (type 1 container) (at 1 1) (opened 1)"));
    assert(w->ParseInstruction("(:task (close X) (:cond (sort X cupboard)))"));
    unsigned checks=0;
    for(int budget: {0,1,50,99,100,199,299,300,301,5000}) {
        ScoreSemanticsTestAccess::ExactBudget(*w,budget);
        const auto before=w->DebugStateSnapshot();const auto p=w->PreviewCandidatePlan(0);
        assert(p.dry_run_succeeded && p.actions.size()==1 && p.remainingDuration().count()==100);
        assert(w->DebugStateSnapshot()==before);
        assert(ScoreSemanticsTestAccess::Fits(*w,p)==(budget>=300));
        assert(w->TestPlatformCalls()==0);++checks;
    }
    for(int duration: {0,1,100,420,999,3000}) {
        CandidatePlan p;p.dry_run_succeeded=true;
        CandidateAction a("Move",{2},ActionCategory::MOVE);a.estimated_duration=std::chrono::milliseconds(duration);p.actions.push_back(a);
        for(int delta=-2;delta<=2;++delta) {
            ScoreSemanticsTestAccess::ExactBudget(*w,duration+safety_margin_ms+delta);
            assert(ScoreSemanticsTestAccess::Fits(*w,p)==(delta>=0));++checks;
            p.dry_run_succeeded=false;assert(!ScoreSemanticsTestAccess::Fits(*w,p));++checks;p.dry_run_succeeded=true;
        }
    }
    DeadlineManager d(std::chrono::milliseconds(720));
    assert(d.canFinish(std::chrono::milliseconds(420),std::chrono::milliseconds(300)));
    assert(!d.canFinish(std::chrono::milliseconds(421),std::chrono::milliseconds(300)));
    assert(!d.canFinish(std::chrono::milliseconds(-1),std::chrono::milliseconds(300)));
    std::cout<<"DEADLINE checks="<<checks+3<<" exact_boundary=unchanged complete_projection=required\n";
}
