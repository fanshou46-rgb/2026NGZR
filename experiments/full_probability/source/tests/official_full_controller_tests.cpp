#include "rdfw.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
using namespace _home;
int main(int argc,char** argv) {
    assert(argc==3);const unsigned test=unsigned(std::atoi(argv[2]));
    const bool carry=test==4 || test==5,inside=test==3 || test==6;
    const std::string common="(at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) "
        "(sort 3 cup) (size 3 small) "+std::string(inside?"(inside 3 2) ":"(at 3 1) ")+
        "(sort 4 book) (size 4 small) (at 4 "+std::string(carry?"2":"1")+") ";
    const std::string public_env=std::string(carry?"(hold 3) ":"(hold 0) ")+"(plate 0) (closed 2) "+common;
    const std::string real="(:domain "+std::string(test==2?"(hold 4) ":test==4?"(hold 3) ":"(hold 0) ")+
        (test==1?"(plate 3) ":"(plate 0) ")+(test==3?"(opened 2) ":"(closed 2) ")+common+")";
    const std::string task=carry?"(:task (goto X) (:cond (sort X book))) (:cons_notnot (:info (near X Y) (:cond (sort X cup) (sort Y human))))":
        inside?"(:task (takeout X Y) (:cond (sort X cup) (sort Y cupboard)))":
        "(:task (pickup X) (:cond (sort X cup)))";
    Evaluate sdk;std::string name="full-controller-"+std::to_string(test);sdk.newteam(name.c_str());
    const std::string ins="(:ins "+task+")";
    assert(sdk.init_et(real.c_str(),real.size()));assert(sdk.init_it(ins.c_str(),ins.size()));
    auto w=std::make_shared<RDFW>();char program[]="full-controller",path[]="-path";char* args[]={program,path,argv[1]};
    w->Init(3,args);w->stage=2;w->SetTestInput(public_env,task);
    // Only the public description enters Plan. The real SDK is called solely
    // at the already selected dispatch boundary, returning public feedback.
    unsigned sdk_calls=0;int paid=0;
    w->SetSenseCallback([&](std::vector<unsigned>& ids){
        ++sdk_calls;++paid;sdk.EvaluateSense(ids);
        if(carry)w->move_cons[3][2]=1; // public near constraint's legacy cleanup trigger
    });
    w->SetAskCallback([&](unsigned id){++sdk_calls;paid+=2;return sdk.EvaluateAskLoc(id);});
    w->SetActionCallback([&]() {
        const auto& p=w->ActionReceipts().back().permit;const auto& a=p.arguments;bool ok=false;
        ++sdk_calls;paid+=p.cost;
        if(p.action=="Move")ok=sdk.EvaluateMove(a[0]);
        else if(p.action=="PickUp")ok=sdk.EvaluatePickUp(a[0]);
        else if(p.action=="PutDown")ok=sdk.EvaluatePutDown(a[0]);
        else if(p.action=="ToPlate")ok=sdk.EvaluateToPlate(a[0]);
        else if(p.action=="FromPlate")ok=sdk.EvaluateFromPlate(a[0]);
        else if(p.action=="Open")ok=sdk.EvaluateOpen(a[0]);
        else if(p.action=="Close")ok=sdk.EvaluateClose(a[0]);
        else if(p.action=="TakeOut")ok=sdk.EvaluateTakeOut(a[0],a[1]);
        else if(p.action=="PutIn")ok=sdk.EvaluatePutIn(a[0],a[1]);else assert(false);
        w->SetActionResults({ok});
    });
    setenv("RDFW_FULL_MODEL","full",1);w->Plan();unsetenv("RDFW_FULL_MODEL");
    const int score=sdk.EndEvaluation(5.0);
    std::cout<<"case="<<test<<" SDK="<<score<<" cost="<<paid<<" calls="<<sdk_calls<<"\n";
    assert(score==40+(test==5?20:0)-paid);
    if(carry) {
        // The full controller's selected Move must not call legacy implicit
        // PutDown. Its permanent near loss is priced in the selected policy.
        assert(w->ActionReceipts().size()==3 && paid==6 && score==(test==4?34:54));
        assert(w->ActionReceipts()[1].permit.action=="Move");
        assert(w->ActionReceipts()[2].permit.action=="Sense");
        assert(w->ExplicitAt(3)==UNKNOWN); // weak carried-item hint did not prove independent at
    }
    if(test==6) {
        assert(paid==6 && score==34 && w->ActionReceipts().size()==4);
        assert(w->ActionReceipts()[1].permit.action=="Open");
        assert(w->ActionReceipts()[2].permit.action=="Sense");
        assert(w->ActionReceipts()[3].permit.action=="TakeOut");
    }
    assert(sdk_calls>1 && w->ActionReceipts().size()==sdk_calls && w->TestPlatformCalls()==sdk_calls);
    assert(w->GetScoreSnapshot().action_cost==paid);
    unsigned modeled=0;
    for(const auto& r:w->ActionReceipts()) {
        assert(r.sent && r.state_committed && r.status==ExecutionStatus::COMMITTED);
        assert(r.sdk_ns>=0);
        assert(r.permit.kind!=PermitKind::LEGACY_UNQUALIFIED && r.permit.policy>0);
        if(r.permit.kind==PermitKind::MODELED_PROBE){assert(r.permit.branches_complete);++modeled;}
    }
    assert(modeled>0);
}
