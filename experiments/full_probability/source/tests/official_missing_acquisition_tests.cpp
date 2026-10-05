#include "rdfw.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
using namespace _home;
int main(int argc,char** argv) {
    assert(argc==3);const unsigned test=std::atoi(argv[2]);assert(test<=5);
    const bool container_case=test==2 || test==5;
    const std::string slots=test==3?"(hold 3) (plate 0) ":"(hold 0) (plate 0) ";
    const std::string public_env=slots+"(at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (closed 2) (at 2 "+
        (container_case?"9":"1")+") (sort 3 cup) (size 3 small) (color 3 red) "+
        (test==5?"(inside 3 2)":"");
    // Only the SDK receives truth. Plan receives the public omission above.
    const std::string real="(:domain "+public_env+
        (test==2?" (inside 3 2)":test==5 || test==3?"":" (at 3 9)")+")";
    const std::string task=std::string("(:task (")+(test==4?"putdown":"pickup")+
        " X) (:cond (sort X cup) (color X red)))";
    Evaluate sdk;std::string name="missing-acquisition-"+std::to_string(test);sdk.newteam(name.c_str(),test==1);
    const std::string ins="(:ins "+task+")";
    assert(sdk.init_et(real.c_str(),real.size()) && sdk.init_it(ins.c_str(),ins.size()));
    auto w=std::make_shared<RDFW>();char program[]="missing-acquisition",path[]="-path";char* args[]={program,path,argv[1]};
    w->Init(3,args);w->stage=test==3?1:2;w->SetTestInput(public_env,task);
    unsigned calls=0,queries=0,coverage_queries=0;int paid=0;
    w->SetSenseCallback([&](std::vector<unsigned>& ids){++calls;++paid;sdk.EvaluateSense(ids);});
    w->SetAskCallback([&](unsigned id) {
        assert(test!=3 && test!=4);++calls;++queries;paid+=2;
        const auto& permit=w->ActionReceipts().back().permit;
        coverage_queries+=permit.selection_reason=="necessary_public_missing_location_coverage";
        if(test<=2) {
            assert(id==3 && w->ExplicitAt(3)==UNKNOWN);
            // An ordinary profitable information query may now precede the
            // deferred necessary-coverage fallback. Both remain weak clues.
            assert(permit.selection_reason=="necessary_public_missing_location_coverage" ||
                permit.selection_reason=="full_joint_public_feedback_policy");
        } else assert(permit.selection_reason!="necessary_public_missing_location_coverage");
        if(test==1) {
            unsigned seed=1;
            for(;seed<100000;++seed) {
                std::srand(seed);const int branch=std::rand()%10;
                if(queries==1) {if(branch>=6 && branch<=8 && std::rand()%5==0)break;}
                else if(branch<6)break;
            }
            assert(seed<100000);std::srand(seed);
        }
        const auto answer=sdk.EvaluateAskLoc(id);
        if(test<=2)assert(answer==(test==1 && queries==1?"at(3,1)":test==2?"inside(3,2)":"at(3,9)"));
        return answer;
    });
    w->SetActionCallback([&]() {
        const auto& p=w->ActionReceipts().back().permit;const auto& a=p.arguments;
        ++calls;paid+=p.cost;bool ok=false;
        if(p.action=="Move") {
            assert(a[0]==9);
            // Weak query answers must not acquire canonical AT authority.
            if(test<=2)assert(w->ExplicitAt(3)==UNKNOWN);
            ok=sdk.EvaluateMove(a[0]);
        } else if(p.action=="Open")ok=sdk.EvaluateOpen(a[0]);
        else if(p.action=="PickUp")ok=sdk.EvaluatePickUp(a[0]);
        else if(p.action=="TakeOut")ok=sdk.EvaluateTakeOut(a[0],a[1]);
        else if(p.action=="PutDown")ok=sdk.EvaluatePutDown(a[0]);
        else if(p.action=="FromPlate")ok=sdk.EvaluateFromPlate(a[0]);
        else if(p.action=="ToPlate")ok=sdk.EvaluateToPlate(a[0]);else assert(false);
        assert(ok);w->SetActionResults({ok});
    });
    setenv("RDFW_FULL_MODEL","full",1);w->Plan();unsetenv("RDFW_FULL_MODEL");
    assert(sdk.EndEvaluation(5.0)==40-paid); // actual goal, all actual fees
    assert(w->GetScoreSnapshot().action_cost==paid && w->ActionReceipts().size()==calls);
    if(test==0 || test==1)assert(queries==(test==1?2:1) && w->FactValue(StateField::HOLD)==3);
    // Necessary fallback is used only after ordinary Stop; a positive-value
    // ordinary query can cover the same missing location first.
    if(test==2)assert(coverage_queries<=1 && queries>=1 && queries<=3 && w->FactValue(StateField::HOLD)==3 && w->InsideRelation(3,2)==0);
    if(test==3 || test==4)assert(queries==0 && calls==1 && paid==1);
    if(test==5)for(const auto& r:w->ActionReceipts())assert(r.permit.selection_reason!="necessary_public_missing_location_coverage");
    for(const auto& r:w->ActionReceipts())assert(r.sent && r.state_committed && r.permit.policy>0 && r.permit.kind!=PermitKind::LEGACY_UNQUALIFIED);
    std::cout<<"SDK missing acquisition case="<<test<<" calls="<<calls<<" queries="<<queries<<" fees="<<paid<<" goal=1 passed\n";
}
