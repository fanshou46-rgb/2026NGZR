#include "rdfw.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
using namespace _home;
int main(int argc,char** argv) {
    assert(argc==3);const unsigned test=std::atoi(argv[2]);assert(test<=1);
    const std::string env="(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 3) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (closed 2) (at 2 1) "
        "(sort 3 cup) (size 3 small) (color 3 red) (at 3 1) "
        "(sort 4 bottle) (size 4 small) (color 4 blue) (at 4 2) "
        "(sort 5 table) (size 5 big) (at 5 2) (sort 6 desk) (size 6 big) (at 6 3) "
        "(sort 7 book) (size 7 small) (color 7 yellow) (at 7 1) "
        "(sort 8 can) (size 8 small) (color 8 black) (at 8 1) "
        "(sort 9 can) (size 9 small) (color 9 white) (at 9 3)";
    std::string tasks="(:task (putin X Y) (:cond (sort X book) (color X yellow) (sort Y cupboard) (type Y container))) "
        "(:task (putin X Y) (:cond (sort X can) (color X black) (sort Y cupboard) (type Y container))) "
        "(:task (puton X Y) (:cond (sort X bottle) (color X blue) (sort Y desk))) "
        "(:task (puton X Y) (:cond (sort X cup) (color X red) (sort Y table))) "
        "(:task (close X) (:cond (sort X cupboard) (type X container))) "
        "(:task (pickup X) (:cond (sort X can) (color X white))) "
        "(:task (goto X) (:cond (sort X human)))";
    if(test==0)tasks+=" (:cons_not (:info (inside X Y) (:cond (sort X book) (color X yellow) (sort Y cupboard) (type Y container)))) "
        "(:cons_not (:task (pickup X) (:cond (sort X book) (color X yellow)))) "
        "(:cons_not (:info (inside X Y) (:cond (sort X can) (color X black) (sort Y cupboard) (type Y container)))) "
        "(:cons_not (:task (pickup X) (:cond (sort X can) (color X black))))";
    Evaluate sdk;std::string name="subset-policy-"+std::to_string(test);sdk.newteam(name.c_str(),false);
    const std::string domain="(:domain "+env+")",ins="(:ins "+tasks+")";
    assert(sdk.init_et(domain.c_str(),domain.size()) && sdk.init_it(ins.c_str(),ins.size()));
    auto w=std::make_shared<RDFW>();char program[]="subset-policy",path[]="-path";char* args[]={program,path,argv[1]};
    w->Init(3,args);w->stage=1;w->SetTestInput(env,tasks);unsigned calls=0,moves=0;int paid=0;
    w->SetSenseCallback([&](std::vector<unsigned>& ids){++calls;++paid;sdk.EvaluateSense(ids);});
    w->SetAskCallback([&](unsigned){assert(false);return std::string();});
    w->SetActionCallback([&]() {
        const auto& p=w->ActionReceipts().back().permit;const auto& a=p.arguments;
        ++calls;paid+=p.cost;bool ok=false;
        if(test==0)assert(!(p.action=="PickUp" && (a[0]==7 || a[0]==8)) && p.action!="PutIn");
        if(p.action=="Move"){++moves;ok=sdk.EvaluateMove(a[0]);}
        else if(p.action=="PickUp")ok=sdk.EvaluatePickUp(a[0]);
        else if(p.action=="PutDown")ok=sdk.EvaluatePutDown(a[0]);
        else if(p.action=="ToPlate")ok=sdk.EvaluateToPlate(a[0]);
        else if(p.action=="FromPlate")ok=sdk.EvaluateFromPlate(a[0]);
        else if(p.action=="Open")ok=sdk.EvaluateOpen(a[0]);
        else if(p.action=="Close")ok=sdk.EvaluateClose(a[0]);
        else if(p.action=="PutIn")ok=sdk.EvaluatePutIn(a[0],a[1]);else assert(false);
        assert(ok);w->SetActionResults({ok});
    });
    setenv("RDFW_FULL_MODEL","full",1);w->Plan();unsetenv("RDFW_FULL_MODEL");
    // Protected: 5 goals + 4 never violated constraints. Unprotected: 7 goals.
    // Both expressions equal 280; action trace rules exclude the damaged-goal
    // alternative in case 0. Goal truth is verified by the actual SDK score.
    assert(sdk.EndEvaluation(5.0)==280-paid);
    if(test==0)assert(paid==21 && calls==10 && moves==2);
    assert(w->ActionReceipts().size()==calls && w->TestPlatformCalls()==calls && w->GetScoreSnapshot().action_cost==paid);
    for(const auto& r:w->ActionReceipts())assert(r.sent && r.state_committed && r.permit.policy>0 && r.permit.kind!=PermitKind::LEGACY_UNQUALIFIED);
    std::cout<<"SDK subset counterfactual="<<test<<" calls="<<calls<<" moves="<<moves<<" fees="<<paid<<" goals="<<(test==0?5:7)<<" base="<<280-paid<<" passed\n";
}
