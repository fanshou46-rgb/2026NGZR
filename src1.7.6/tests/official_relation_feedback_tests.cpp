#include "rdfw.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
using namespace _home;
namespace _home { struct ScoreSemanticsTestAccess {
    static std::size_t revision(const RDFW& w) {return w.world_revision;}
    static bool act(RDFW& w,int a) {
        switch(a) {case 0:return w.PickUp(3);case 1:return w.PutDown(3);
        case 2:return w.ToPlate(3);case 3:return w.FromPlate(3);
        case 4:return w.TakeOut(3,2);case 5:return w.PutIn(3,2);case 6:return w.Open(2);}
        return false;
    }
}; }
int main(int argc,char** argv) {
    assert(argc==3);const int test=std::atoi(argv[2]);
    const std::string common="(at 0 1) (sort 1 table) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) "
        "(sort 3 cup) (size 3 small) (at 3 1) "
        "(sort 4 closet) (size 4 big) (type 4 container) (at 4 1) (opened 4) "
        "(sort 5 book) (size 5 small) (at 5 1)";
    const std::string door=test==3 || test==4?"(closed 2) ":"(opened 2) ";
    const std::string edges=test<=2?"(inside 3 2) (inside 3 4) ":"";
    const std::string slots=test==2?"(hold 0) (plate 3) ":
        test==4?"(hold 0) (plate 5) ":test==5?"(hold 5) (plate 3) ":
        "(hold 0) (plate 0) ";
    const std::string truth="(:domain "+slots+common+door+edges+")";
    const std::string tasks=test<=1?
        "(:ins (:task (takeout X Y) (:cond (sort X cup) (sort Y cupboard))) "
        "(:task (putin X Y) (:cond (sort X cup) (sort Y closet))))":test==2?
        "(:ins (:task (takeout X Y) (:cond (sort X cup) (sort Y cupboard))))":
        "(:ins (:task (putdown X) (:cond (sort X cup))))";
    Evaluate sdk;const std::string name="relation-feedback-"+std::to_string(test);
    sdk.newteam(name.c_str());assert(sdk.init_et(truth.c_str(),truth.size()));
    assert(sdk.init_it(tasks.c_str(),tasks.size()));
    auto w=std::make_shared<RDFW>();char program[]="relation",path[]="-path";
    char* args[]={program,path,argv[1]};w->Init(3,args);w->stage=test<=1?1:2;
    // Stage 2 receives the same weak slot description for differing truths.
    std::string input_common=common;
    if(test==1) input_common.erase(input_common.find("(type 4 container) "),19);
    assert(w->ParseEnv((test<=1?slots:"(hold 0) (plate 0) ")+input_common+door+edges+(test==1?"(type 4 container) ":"")));
    assert(w->ParseInstruction(tasks));int cost=0;
    const auto act=[&](int a) {
        const bool ok=a==0?sdk.EvaluatePickUp(3):a==1?sdk.EvaluatePutDown(3):
            a==2?sdk.EvaluateToPlate(3):a==3?sdk.EvaluateFromPlate(3):
            a==4?sdk.EvaluateTakeOut(3,2):a==5?sdk.EvaluatePutIn(3,2):sdk.EvaluateOpen(2);
        w->SetActionResults({ok});assert(ScoreSemanticsTestAccess::act(*w,a)==ok);
        cost+=2;return ok;
    };
    int expected_goals=0;
    if(test<=1) {
        assert(w->InsideRelation(3,2)==1 && w->InsideRelation(3,4)==1);
        w->debug_capture_projection=true;const auto before=w->DebugStateSnapshot();
        const auto plan=w->PreviewCandidatePlan(0);
        assert(plan.dry_run_succeeded && w->DebugStateSnapshot()==before);
        assert(act(0) && act(2) && act(3) && act(1));
        assert(w->InsideRelation(3,2)==1 && w->InsideRelation(3,4)==1);
        assert(!w->TaskFactSatisfied("takeout",3,2));
        assert(act(4));
        assert(w->InsideRelation(3,2)==0 && w->InsideRelation(3,4)==1);
        expected_goals=2;
        if(test==1) {
            assert(act(5));assert(w->InsideRelation(3,2)==1 && w->InsideRelation(3,4)==1);
            expected_goals=1;
        }
    } else if(test==2) {
        assert(act(3) && act(1));
        assert(w->InsideRelation(3,2)==UNKNOWN);
        assert(w->GetTerminalSummary().goals[0]==TerminalStatus::UNKNOWN);
        assert(act(4));assert(w->InsideRelation(3,2)==0);
        assert(w->InsideRelation(3,4)==UNKNOWN); // unrelated weak edge stays weak
        expected_goals=1;
    } else if(test==3 || test==4) {
        assert(act(6));assert(w->FactValue(StateField::HOLD)==NONE);
        const auto revision=ScoreSemanticsTestAccess::revision(*w);assert(!act(3));
        assert(w->IsNotStoredFact(3) && w->FactValue(StateField::PLATE)==UNKNOWN);
        assert(ScoreSemanticsTestAccess::revision(*w)>revision);const auto learned=ScoreSemanticsTestAccess::revision(*w);
        assert(!act(3) && ScoreSemanticsTestAccess::revision(*w)==learned);
        expected_goals=1;
    } else {
        assert(w->FactValue(StateField::HOLD)==UNKNOWN);const auto before=w->DebugStateSnapshot();
        assert(!act(3));assert(w->DebugStateSnapshot()==before && !w->IsNotStoredFact(3));
        expected_goals=0;
    }
    assert(sdk.EndEvaluation(5.0)==40*expected_goals-cost);
    const auto terminal=w->GetTerminalSummary();
    assert(terminal.satisfied_goals==static_cast<unsigned>(expected_goals));
    std::cout<<name<<" SDK/canonical G="<<expected_goals<<" K="<<cost<<" agree\n";
}
