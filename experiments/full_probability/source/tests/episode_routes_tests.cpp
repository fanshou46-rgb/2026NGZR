#include "episode_routes.hpp"
#include <cassert>
#include <iostream>
using namespace _home;
int main() {
    AskObservationModel ask({{'a',0},{'a',1},{'a',2}},.6,.3,.1,0);
    SdkEpisodeModel model;model.goals={SdkPredicate{"puton",{{3,2}}}};
    SdkEpisode e;e.world.robot=1;e.world.locations={0,1,2};
    e.world.objects[2]=JointObject(false,false,2);e.world.objects[3]=JointObject(true,false,1);
    e.world.freezeSdkReplyDomain();
    const EpisodeRoute delivery={{JointActionKind::PICKUP,3},{JointActionKind::MOVE,2},{JointActionKind::PUTDOWN,3}};
    for(unsigned repeat=0;repeat<50;++repeat) {
        auto plan=EpisodeRouteSearch::solve(EpisodeBelief({{e,1}}),model,{delivery},{},ask,std::chrono::milliseconds(2000),4096,std::chrono::milliseconds(1000));
        assert(!plan.policy->stop && plan.policy->action.kind==JointActionKind::PICKUP);
        assert(plan.value.lower==32 && plan.value.upper==32 && plan.transitions==3);
        auto policy=plan.policy;unsigned depth=0;
        while(!policy->stop){assert(policy->children.size()==1);policy=policy->children.begin()->second;++depth;}
        assert(depth==3); // negative paid prefixes retain the complete delivery
    }
    auto other=e;other.world.robot=1;other.world.hand=0;other.world.plate=3;
    auto conditional=EpisodeRouteSearch::solve(EpisodeBelief({{e,.5},{other,.5}}),model,{delivery},{},ask,std::chrono::milliseconds(2000),4096,std::chrono::milliseconds(1000));
    assert(!conditional.policy->stop && conditional.policy->children.size()==2);
    JointObservation failed;failed.success=false;
    assert(conditional.policy->children.at(failed)->stop);
    assert(conditional.value.lower==15); // .5*32 + .5*(-2), no success oracle
    SdkEpisode left=e;left.world.robot=0;left.world.objects[3].at=1;
    SdkEpisode right=left;right.world.objects[3].at=2;
    left.world.freezeSdkReplyDomain();right.world.freezeSdkReplyDomain();
    model.goals={SdkPredicate{"pickup",{{3,0}}}};
    auto information=EpisodeRouteSearch::solve(EpisodeBelief({{left,.5},{right,.5}}),model,
        {{{JointActionKind::MOVE,1},{JointActionKind::PICKUP,3}},{{JointActionKind::MOVE,2},{JointActionKind::PICKUP,3}}},
        {{JointActionKind::ASK,3}},ask,std::chrono::milliseconds(2000),4096,std::chrono::milliseconds(1000));
    assert(!information.policy->stop && information.policy->action.kind==JointActionKind::ASK);
    assert(information.policy->children.size()>=3 && information.value.lower>14);
    auto cut=EpisodeRouteSearch::solve(EpisodeBelief({{left,.5},{right,.5}}),model,
        {{{JointActionKind::MOVE,1},{JointActionKind::PICKUP,3}}},{{JointActionKind::ASK,3}},ask,
        std::chrono::milliseconds(2000),2,std::chrono::milliseconds(1000));
    assert(cut.work_cut && cut.policy->stop && cut.value.lower==0);
    auto mandatory=EpisodeRouteSearch::solve(EpisodeBelief({{left,1}}),model,
        {{{JointActionKind::MOVE,1},{JointActionKind::SENSE},{JointActionKind::PICKUP,3}}},{},ask,
        std::chrono::milliseconds(2000),4096,std::chrono::milliseconds(1000));
    assert(!mandatory.policy->stop);
    auto after_move=mandatory.policy->children.begin()->second;
    assert(!after_move->stop && after_move->action.kind==JointActionKind::SENSE);
    std::cout<<"whole-belief routes, conditional paid failures, Ask routing and 50 repeats passed\n";
}
