#include "rdfw.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
using namespace _home;
int main(int argc,char** argv) {
    assert(argc==3);const unsigned test=std::atoi(argv[2]);assert(test<=1);
    const std::string public_env="(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (closed 2) "
        "(sort 3 cup) (size 3 small) (color 3 red) (at 3 1)";
    // Site 9 is absent from the entire PUBLIC description. No author location
    // enters Plan; it becomes available only through the selected SDK query.
    const std::string real="(:domain "+public_env+" (at 2 9))";
    const std::string task="(:task (goto X) (:cond (sort X cupboard) (type X container)))";
    Evaluate sdk;std::string name="missing-location-"+std::to_string(test);sdk.newteam(name.c_str(),test==1);
    const std::string ins="(:ins "+task+")";
    assert(sdk.init_et(real.c_str(),real.size()) && sdk.init_it(ins.c_str(),ins.size()));
    auto w=std::make_shared<RDFW>();char program[]="missing-location",path[]="-path";char* args[]={program,path,argv[1]};
    w->Init(3,args);w->stage=2;w->SetTestInput(public_env,task);
    unsigned calls=0,queries=0;int paid=0;
    w->SetSenseCallback([&](std::vector<unsigned>& ids){++calls;++paid;sdk.EvaluateSense(ids);});
    w->SetAskCallback([&](unsigned id) {
        assert(id==2 && w->FactLocation(2)==UNKNOWN);++calls;++queries;paid+=2;
        if(test==1) {
            unsigned seed=1;
            for(;seed<100000;++seed) {
                std::srand(seed);const int branch=std::rand()%10;
                if(queries==1) {
                    // The initial random pool has four AT entries and one
                    // container. Index 0 is the robot's site, already excluded
                    // for this big object by the first actual Sense.
                    if(branch>=6 && branch<=8 && std::rand()%5==0)break;
                } else if(branch<6)break;
            }
            assert(seed<100000);std::srand(seed);
        }
        const auto answer=sdk.EvaluateAskLoc(id);
        assert(answer==(test==1 && queries==1?"at(2,1)":"at(2,9)"));return answer;
    });
    w->SetActionCallback([&]() {
        const auto& p=w->ActionReceipts().back().permit;
        assert(p.action=="Move" && p.arguments==std::vector<unsigned>{9});
        assert(w->FactLocation(2)==UNKNOWN && !w->IsAbsentFromSensedLocation(2,9));
        ++calls;paid+=p.cost;w->SetActionResults({sdk.EvaluateMove(9)});
    });
    setenv("RDFW_FULL_MODEL","full",1);w->Plan();unsetenv("RDFW_FULL_MODEL");
    assert(queries==(test==1?2:1) && calls==(test==1?5:4));
    assert(paid==(test==1?10:8) && sdk.EndEvaluation(5.0)==40-paid);
    assert(w->FactLocation(2)==9 && w->ExplicitAt(2)==9); // confirmed only after final Sense
    assert(w->GetScoreSnapshot().action_cost==paid && w->ActionReceipts().size()==calls);
    for(const auto& receipt:w->ActionReceipts()) {
        assert(receipt.sent && receipt.state_committed && receipt.status==ExecutionStatus::COMMITTED);
        assert(receipt.permit.policy>0 && receipt.permit.kind!=PermitKind::LEGACY_UNQUALIFIED);
    }
    assert(w->ActionReceipts().front().permit.action=="Sense");
    assert(w->ActionReceipts()[calls-2].permit.action=="Move");
    assert(w->ActionReceipts().back().permit.action=="Sense");
    std::cout<<"missing initial big AT, actual SDK query outside public map, noisy contradicted clue, paid history and final Sense proof passed\n";
}
