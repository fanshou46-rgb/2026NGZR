#include "rdfw.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
using namespace _home;
int main(int argc,char** argv) {
    assert(argc==2);
    const std::string env="(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 2) "
        "(sort 2 table) (size 2 big) (at 2 2) (sort 3 cup) (size 3 small) (color 3 red) (at 3 1) "
        "(sort 4 bottle) (size 4 small) (color 4 blue) (at 4 1)";
    const std::string tasks="(:task (puton X Y) (:cond (sort X cup) (color X red) (sort Y table))) "
        "(:task (puton X Y) (:cond (sort X bottle) (color X blue) (sort Y table)))";
    Evaluate sdk;sdk.newteam("transport-policy",false);
    const std::string domain="(:domain "+env+")",ins="(:ins "+tasks+")";
    assert(sdk.init_et(domain.c_str(),domain.size()) && sdk.init_it(ins.c_str(),ins.size()));
    auto w=std::make_shared<RDFW>();char program[]="transport",path[]="-path";char* args[]={program,path,argv[1]};
    w->Init(3,args);w->stage=1;w->SetTestInput(env,tasks);unsigned calls=0,moves=0;int paid=0;
    w->SetSenseCallback([&](std::vector<unsigned>& ids){++calls;++paid;sdk.EvaluateSense(ids);});
    w->SetAskCallback([&](unsigned){assert(false);return std::string();});
    w->SetActionCallback([&](){
        const auto& p=w->ActionReceipts().back().permit;const auto& a=p.arguments;
        ++calls;paid+=p.cost;bool ok=false;
        if(p.action=="Move"){++moves;ok=sdk.EvaluateMove(a[0]);}
        else if(p.action=="PickUp")ok=sdk.EvaluatePickUp(a[0]);
        else if(p.action=="PutDown")ok=sdk.EvaluatePutDown(a[0]);
        else if(p.action=="ToPlate")ok=sdk.EvaluateToPlate(a[0]);
        else if(p.action=="FromPlate")ok=sdk.EvaluateFromPlate(a[0]);else assert(false);
        assert(ok);w->SetActionResults({ok});
    });
    setenv("RDFW_FULL_MODEL","full",1);w->Plan();unsetenv("RDFW_FULL_MODEL");
    const auto score=sdk.EndEvaluation(5.0);
    assert(score==62 && paid==18 && calls==9 && moves==1); // includes necessary initial Sense
    assert(w->ActionReceipts().size()==calls && w->TestPlatformCalls()==calls);
    for(const auto& r:w->ActionReceipts())assert(r.sent && r.state_committed && r.permit.policy>0 &&
        r.permit.kind!=PermitKind::LEGACY_UNQUALIFIED && r.sdk_ns>=0);
    assert(w->GetScoreSnapshot().action_cost==paid);
    std::cout<<"SDK transport: two delivered goals, one Move, nine policy receipts, 18 fees, base 62\n";
}
