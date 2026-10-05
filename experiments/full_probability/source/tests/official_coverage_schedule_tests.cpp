#include "rdfw.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
using namespace _home;
int main(int argc,char** argv) {
    assert(argc==3);const unsigned test=std::atoi(argv[2]);assert(test<=1);
    const std::string public_env="(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 2) "
        "(sort 3 cup) (size 3 small) (color 3 blue) (at 3 1) "
        "(sort 4 cup) (size 4 small) (color 4 red)";
    const std::string truth="(:domain "+public_env+" (at 4 "+(test==0?"2":"9")+"))";
    const std::string tasks="(:task (puton X Y) (:cond (sort X cup) (color X blue) (sort Y human))) "
        "(:task (pickup X) (:cond (sort X cup) (color X red)))";
    Evaluate sdk;std::string name="coverage-schedule-"+std::to_string(test);sdk.newteam(name.c_str(),false);
    const std::string ins="(:ins "+tasks+")";
    assert(sdk.init_et(truth.c_str(),truth.size()) && sdk.init_it(ins.c_str(),ins.size()));
    auto w=std::make_shared<RDFW>();char program[]="coverage-schedule",path[]="-path";char* args[]={program,path,argv[1]};
    w->Init(3,args);w->stage=2;w->SetTestInput(public_env,tasks);unsigned calls=0,queries=0,necessary=0;int paid=0;
    w->SetSenseCallback([&](std::vector<unsigned>& ids){++calls;++paid;sdk.EvaluateSense(ids);});
    w->SetAskCallback([&](unsigned id) {
        assert(id==4);++calls;++queries;paid+=2;
        const auto& permit=w->ActionReceipts().back().permit;
        if(permit.selection_reason=="necessary_public_missing_location_coverage") {
            ++necessary;
            // Case 0 is on the already profitable delivery route; required
            // perception can locate it without an up-front coverage command.
            assert(test==1);
        } else assert(permit.selection_reason=="full_joint_public_feedback_policy");
        assert(w->ExplicitAt(4)==UNKNOWN);return sdk.EvaluateAskLoc(id);
    });
    w->SetActionCallback([&]() {
        const auto& p=w->ActionReceipts().back().permit;const auto& a=p.arguments;++calls;paid+=p.cost;bool ok=false;
        if(p.action=="Move")ok=sdk.EvaluateMove(a[0]);
        else if(p.action=="PickUp")ok=sdk.EvaluatePickUp(a[0]);
        else if(p.action=="PutDown")ok=sdk.EvaluatePutDown(a[0]);
        else if(p.action=="ToPlate")ok=sdk.EvaluateToPlate(a[0]);
        else if(p.action=="FromPlate")ok=sdk.EvaluateFromPlate(a[0]);else assert(false);
        assert(ok);w->SetActionResults({ok});
    });
    setenv("RDFW_FULL_MODEL","full",1);w->Plan();unsetenv("RDFW_FULL_MODEL");
    assert(sdk.EndEvaluation(5.0)==80-paid && w->FactValue(StateField::HOLD)==4);
    assert(w->GetScoreSnapshot().action_cost==paid && w->ActionReceipts().size()==calls && queries<=3);
    if(test==0)assert(necessary==0);
    for(const auto& r:w->ActionReceipts())assert(r.sent && r.state_committed && r.permit.policy>0 && r.permit.kind!=PermitKind::LEGACY_UNQUALIFIED);
    std::cout<<"SDK deferred coverage case="<<test<<" calls="<<calls<<" queries="<<queries<<" necessary="<<necessary<<" fees="<<paid<<" goals=2 base="<<80-paid<<" passed\n";
}
