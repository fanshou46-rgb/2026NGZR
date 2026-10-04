#include "rdfw.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
using namespace _home;
namespace _home { struct ScoreSemanticsTestAccess {
    static bool drop(RDFW& w) { return w.PutDown(3); }
    static bool verify(RDFW& w) { return w.ConfirmOutsidePlacement(3); }
    static bool take(RDFW& w) { return w.TakeOut(3,2); }
    static void sense(RDFW& w) { w.SenseCurrentLocationOnly(true); }
}; }
int main(int argc,char** argv) {
    assert(argc==3);int test=std::atoi(argv[2]);
    const std::string common="(at 0 1) (sort 1 table) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) (opened 2) "
        "(sort 3 cup) (size 3 small) (inside 3 2) "
        "(sort 4 book) (size 4 small) (at 4 1)";
    const std::string truth="(:domain (hold 0) (plate "+std::to_string(test==1?3:test==2?4:0)+") "+common+")";
    const std::string task="(:ins (:task (puton X Y) (:cond (sort X cup) (sort Y table))))";
    Evaluate sdk;std::string name="placement-recovery-"+std::to_string(test);sdk.newteam(name.c_str());
    assert(sdk.init_et(truth.c_str(),truth.size()));assert(sdk.init_it(task.c_str(),task.size()));
    auto w=std::make_shared<RDFW>();char nameArg[]="placement",path[]="-path";char* args[]={nameArg,path,argv[1]};
    w->Init(3,args);w->stage=2;
    // Identical weak input for empty tray, tray=A, and tray=another object.
    assert(w->ParseEnv("(hold 0) (plate 0) "+common));assert(w->ParseInstruction(task));
    bool ok=sdk.EvaluateTakeOut(3,2);assert(ok);w->SetActionResults({ok});assert(ScoreSemanticsTestAccess::take(*w));
    ok=sdk.EvaluatePutDown(3);assert(ok);w->SetActionResults({ok});assert(ScoreSemanticsTestAccess::drop(*w));
    assert(!w->IsNotStoredFact(3));
    // Only the SDK's public success/failure sequence reaches the agent.
    std::vector<bool> feedback;ok=sdk.EvaluatePickUp(3);feedback.push_back(ok);
    if(!ok) {ok=sdk.EvaluateFromPlate(3);feedback.push_back(ok);assert(ok);}
    ok=sdk.EvaluatePutDown(3);feedback.push_back(ok);assert(ok);
    w->SetActionResults(feedback);assert(ScoreSemanticsTestAccess::verify(*w));
    assert(w->IsNotStoredFact(3));
    std::vector<unsigned> ids;sdk.EvaluateSense(ids);w->SetSenseResult(ids);ScoreSemanticsTestAccess::sense(*w);
    assert(w->GetTerminalSummary().goals[0]==TerminalStatus::SATISFIED);
    const int cost=4+int(feedback.size())*2+1;
    assert(sdk.EndEvaluation(5.0)==40-cost);
    assert(w->FactValue(StateField::PLATE)==(test==1?NONE:UNKNOWN));
    std::cout<<name<<" SDK and canonical placement agree; cost="<<cost<<'\n';
}
