#include "rdfw.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <memory>
using namespace _home;
namespace _home {struct ScoreSemanticsTestAccess {
    static void run(RDFW& w,int test) {
        if(test==1)assert(w.Open(5));
        if(test==3)w.SolveTask_Close(2);else w.TakeOutLogic(3,2);
    }
};}
int main(int argc,char** argv) {
    assert(argc==4);const int test=std::atoi(argv[2]);bool before=std::string(argv[3])=="before";
    const bool actual_open=test==1 || test==2 || test==3 || test==4;
    const bool actually_empty=test==1 || test==4;
    std::string common="(plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) "
        "(sort 3 cup) (size 3 small) (inside 3 2) "
        "(sort 4 book) (size 4 small) (at 4 1) "
        "(sort 5 closet) (size 5 big) (type 5 container) (at 5 1) (closed 5) ";
    const std::string real=std::string("(hold ")+(actually_empty?"0":"4")+") "+common+(actual_open?"(opened 2)":"(closed 2)");
    const std::string public_input="(hold 0) "+common+(test==3?"(opened 2)":"(closed 2)");
    const std::string task=test==3?"(:task (close X) (:cond (sort X cupboard)))":
        "(:task (takeout X Y) (:cond (sort X cup) (sort Y cupboard)))";
    Evaluate sdk;std::string name="door-failure-"+std::to_string(test);sdk.newteam(name.c_str());
    std::string env="(:domain "+real+")",ins="(:ins "+task+")";
    assert(sdk.init_et(env.c_str(),env.size()));assert(sdk.init_it(ins.c_str(),ins.size()));
    auto w=std::make_shared<RDFW>();char name_arg[]="door-proof",path[]="-path";char* args[]={name_arg,path,argv[1]};
    w->Init(3,args);w->stage=2;assert(w->ParseEnv(public_input));assert(w->ParseInstruction(task));
    w->SetActionResults(test==1?std::vector<bool>{true,false,true}:
        test==4?std::vector<bool>{false,true}:std::vector<bool>{false,false});
    unsigned physical=0;
    w->SetActionCallback([&]() {
        bool result;
        if(test==1 && physical==0)result=sdk.EvaluateOpen(5);
        else if(test==3)result=sdk.EvaluateClose(2);
        else if((test==1 && physical==1) || (test!=1 && physical==0))result=sdk.EvaluateOpen(2);
        else result=sdk.EvaluateTakeOut(3,2);
        ++physical;
        const bool expected=(test==1 && physical==1) || (test==1 && physical==3) || (test==4 && physical==2);
        assert(result==expected);
        // Observations don't change physical state/ledger. Cache the real SDK
        // ID response for the immediate wrapper Sense after a false action.
        if(!result) {std::vector<unsigned> ids;sdk.EvaluateSense(ids);w->SetSenseResult(ids);}
    });
    ScoreSemanticsTestAccess::run(*w,test);
    const auto internal=w->GetScoreSnapshot();int official=sdk.EndEvaluation(5.0);
    std::cout<<"case="<<test<<" mode="<<(before?"before":"fixed")<<" SDK="<<official
        <<" internal="<<internal.deterministic_base_score<<":"<<internal.possible_base_score
        <<" door="<<w->FactContainerState(2)<<" inside="<<w->InsideRelation(3,2)
        <<" platform_calls="<<w->TestPlatformCalls()<<"\n";
    if(before && (test==0 || test==3))assert(internal.deterministic_base_score>official);
    else assert(internal.deterministic_base_score<=official && official<=internal.possible_base_score);
    if(!before && test!=1)assert(w->FactContainerState(2)==UNKNOWN);
    if(!before && test==0)assert(w->InsideRelation(3,2)==UNKNOWN);
    if(test==1)assert(w->FactContainerState(2)==1 && w->InsideRelation(3,2)==0);
}
