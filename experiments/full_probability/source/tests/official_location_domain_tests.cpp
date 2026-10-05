#include "sdk_episode.hpp"
#include "episode_conditioner.hpp"
#include "episode_proposal.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
using namespace _home;
int main(int argc,char** argv) {
    assert(argc==2);const int test=std::atoi(argv[1]);assert(test==0 || test==1);
    SdkEpisode a,b;a.world.robot=1;a.world.locations={1,2,9};
    a.world.objects[1]=JointObject(false,false,1);a.world.objects[2]=JointObject(false,false,9);
    a.world.objects[3]=JointObject(true,false,2);b=a;b.world.objects[2].at=2;
    a.world.freezeSdkReplyDomain();b.world.freezeSdkReplyDomain();
    assert(a.world.legalLocation(9) && !b.world.legalLocation(9));
    SdkEpisodeModel model;model.goals={SdkPredicate{"goto",{{2,0}}}};
    AskObservationModel ask({{'a',1},{'a',2},{'a',9}},.6,.3,.1,0);
    EpisodeBelief belief({{a,.5},{b,.5}});
    const auto branches=belief.branches(model,{JointActionKind::MOVE,9},ask);
    assert(branches.size()==2 && branches[0].probability==.5 && branches[1].probability==.5);
    Evaluate sdk;std::string name="location-domain-"+std::to_string(test);sdk.newteam(name.c_str(),false);
    const std::string env="(:domain (hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 table) (size 2 big) (at 2 "+std::string(test?"9":"2")+") "
        "(sort 3 cup) (size 3 small) (color 3 red) (at 3 2))";
    const std::string ins="(:ins (:task (goto X) (:cond (sort X table))))";
    assert(sdk.init_et(env.c_str(),env.size()) && sdk.init_it(ins.c_str(),ins.size()));
    auto actual=test?a:b;unsigned event=0;
    for(unsigned destination:{9,2,1}) {
        const JointAction action{JointActionKind::MOVE,destination};
        const auto step=JointDynamics::step(actual.world,action);JointObservation outcome;
        outcome.success=sdk.EvaluateMove(destination);
        assert(outcome.success==step.observation.success);
        actual=model.next(actual,action,step.world,outcome.success);
        assert(belief.observe(model,action,outcome,ask,++event)==EpisodeUpdate::APPLIED);
        assert(actual.world.legalLocation(1)); // the initial robot-only loc persists after moving
    }
    assert(sdk.EndEvaluation(5.0)==-12 && model.reward(actual).lower==-12);
    // A failed noncurrent Move can condition the initial map without claiming
    // an object position. Final full replay checks local AT witnesses too.
    auto base=b.world;base.initial_reply_counts.clear();base.objects[2].at=9;
    PublicPriorFactor at;at.field=PriorField::EXPLICIT_AT;at.object=2;at.values={{9,.5},{2,.5}};
    JointObservation failed;failed.success=false;
    const std::vector<EpisodeEvidence> history={{1,{JointActionKind::MOVE,9},failed}};
    auto conditioned=EpisodeConditioner::initial(base,{at},history);
    assert(conditioned.consistent && conditioned.retained_prior_mass==.5);
    assert(conditioned.factors[0].values.size()==1 && conditioned.factors[0].values[0].value==2);
    auto proposal=EpisodeProposal::generate(base,conditioned.factors,history,0,8,7,4096,std::chrono::milliseconds(1000));
    assert(proposal.complete && !proposal.scenes.empty());
    EpisodeReplay replay(EpisodeBelief({{a,1}}));
    assert(replay.observe(model,{JointActionKind::MOVE,9},failed,ask,1)==EpisodeUpdate::SUPPORT_MISS);
    assert(replay.repair(model,ask,proposal.scenes,4096,std::chrono::milliseconds(1000)).installed);
    assert(replay.belief().support().front().episode.paid==4);
    std::cout<<"SDK static loc domain, candidate-only loc failure, paid feedback branches and initial-map replay passed\n";
}
