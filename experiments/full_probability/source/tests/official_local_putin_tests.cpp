#include "rdfw.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
using namespace _home;
int main(int argc,char** argv) {
    assert(argc==3);const unsigned test=std::atoi(argv[2]);assert(test<=1);
    const std::string env="(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) (closed 2) "
        "(sort 3 cup) (size 3 small) (color 3 red) (inside 3 4) "
        "(sort 4 closet) (size 4 big) (type 4 container) (at 4 1) (opened 4)";
    const std::string task="(:task (putin X Y) (:cond (sort X cup) (sort Y cupboard)))"+
        std::string(test==1?" (:cons_not (:info (inside X Y) (:cond (sort X cup) (sort Y closet))))":"");
    Evaluate sdk;std::string name="local-putin-"+std::to_string(test);sdk.newteam(name.c_str(),false);
    const std::string real="(:domain "+env+")",ins="(:ins "+task+")";
    assert(sdk.init_et(real.c_str(),real.size()) && sdk.init_it(ins.c_str(),ins.size()));
    auto w=std::make_shared<RDFW>();char program[]="local-putin",path[]="-path";char* args[]={program,path,argv[1]};
    w->Init(3,args);w->stage=1;w->SetTestInput(env,task);
    unsigned calls=0;int paid=0;
    w->SetSenseCallback([&](std::vector<unsigned>& ids){++calls;++paid;sdk.EvaluateSense(ids);});
    w->SetAskCallback([&](unsigned){assert(false);return std::string();});
    w->SetActionCallback([&]() {
        const auto& p=w->ActionReceipts().back().permit;const auto& a=p.arguments;
        ++calls;paid+=p.cost;bool ok=false;
        if(p.action=="Open")ok=sdk.EvaluateOpen(a[0]);
        else if(p.action=="TakeOut")ok=sdk.EvaluateTakeOut(a[0],a[1]);
        else if(p.action=="PutIn")ok=sdk.EvaluatePutIn(a[0],a[1]);
        else if(p.action=="PickUp")ok=sdk.EvaluatePickUp(a[0]);
        else if(p.action=="PutDown")ok=sdk.EvaluatePutDown(a[0]);
        else if(p.action=="ToPlate")ok=sdk.EvaluateToPlate(a[0]);
        else if(p.action=="FromPlate")ok=sdk.EvaluateFromPlate(a[0]);else assert(false);
        assert(ok);w->SetActionResults({ok});
    });
    setenv("RDFW_FULL_MODEL","full",1);w->Plan();unsetenv("RDFW_FULL_MODEL");
    const int score=sdk.EndEvaluation(5.0);
    assert(paid==(test==1?12:8) && score==(test==1?48:32));
    assert(calls==(test==1?7:5) && w->ActionReceipts().size()==calls && w->GetScoreSnapshot().action_cost==paid);
    // The first physical action changes with the public permanent constraint.
    // Open-first saves two fees without it; TakeOut-first keeps its credit.
    assert(w->ActionReceipts()[1].permit.action==(test==1?"TakeOut":"Open"));
    assert(w->InsideRelation(3,2)==1 && w->InsideRelation(3,4)==0);
    for(const auto& receipt:w->ActionReceipts())assert(receipt.sent && receipt.state_committed && receipt.permit.policy>0);
    std::cout<<"SDK local PutIn opening order, two saved physical calls and irreversible constraint counterfactual passed\n";
}
