#include "episode_router.hpp"
#include <cassert>
#include <iostream>
using namespace _home;
int main() {
    SdkEpisodeModel m;
    m.goals={SdkPredicate{"give",{{3,1}}},SdkPredicate{"putin",{{4,2}}},SdkPredicate{"close",{{2,0}}},
        SdkPredicate{"pickup",{{5,0}}},SdkPredicate{"goto",{{1,0}}}};
    SdkEpisode initial;auto& w=initial.world;w.robot=1;w.locations={1,2};
    w.objects[1]=JointObject(false,false,2);w.objects[2]=JointObject(false,true,1);
    w.objects[3]=JointObject(true,false,1);w.objects[4]=JointObject(true,false,1);w.objects[5]=JointObject(true,false,2);
    w.freezeSdkReplyDomain();assert(m.reward(initial).goals_lower==1);
    AskObservationModel ask({{'a',1},{'a',2},{'i',2}});
    for(unsigned repeat=0;repeat<50;++repeat) {
        auto proposals=EpisodeRouter::propose(EpisodeBelief({{initial,1}}),m,4096,std::chrono::milliseconds(1000));
        assert(!proposals.routes.empty() && !proposals.work_cut && !proposals.wall_cut);
        bool complete=false,perceived=false;
        for(const auto& route:proposals.routes) {
            auto state=initial;
            for(const auto& action:route) {
                auto step=JointDynamics::step(state.world,action);
                assert(step.observation.kind!=JointObservation::Kind::FEEDBACK || step.observation.success);
                if(action.kind==JointActionKind::SENSE)perceived=true;
                state=m.next(state,action,step.world,step.observation.success);
            }
            if(m.reward(state).goals_lower==5)complete=true;
        }
        assert(complete && perceived);
        const auto plan=EpisodeRouteSearch::solve(EpisodeBelief({{initial,1}}),m,proposals.routes,{},ask,
            std::chrono::milliseconds(5000),16384,std::chrono::milliseconds(1000));
        assert(!plan.policy->stop && plan.value.lower>140);
        // The selected policy restores the initially closed goal after PutIn,
        // and acquires the terminal held object after empty-hand operations.
        auto policy=plan.policy;auto state=initial;
        while(!policy->stop) {
            auto step=JointDynamics::step(state.world,policy->action);
            state=m.next(state,policy->action,step.world,step.observation.success);
            policy=policy->children.at(step.observation);
        }
        assert(m.reward(state).goals_lower==5);
    }
    // A small fixed budget must offer routes for both public position
    // hypotheses before spending it on variants of only the first world.
    SdkEpisode a;a.world.robot=0;a.world.locations={0,1,2};
    a.world.objects[3]=JointObject(true,false,1);a.world.freezeSdkReplyDomain();
    auto b=a;b.world.objects[3].at=2;b.world.initial_reply_counts.clear();b.world.freezeSdkReplyDomain();
    SdkEpisodeModel locate;locate.goals={SdkPredicate{"pickup",{{3,0}}}};
    for(unsigned repeat=0;repeat<50;++repeat) {
        const auto batch=EpisodeRouter::propose(EpisodeBelief({{a,.5},{b,.5}}),locate,12,std::chrono::milliseconds(1000));
        bool left=false,right=false;
        for(const auto& route:batch.routes)if(!route.empty() && route.front().kind==JointActionKind::MOVE) {
            left|=route.front().a==1;right|=route.front().a==2;
        }
        assert(left && right && batch.transitions==12 && batch.work_cut);
    }
    SdkEpisode delivery;delivery.world.robot=1;delivery.world.locations={1,2};
    delivery.world.objects[2]=JointObject(false,false,2);
    delivery.world.objects[3]=JointObject(true,false,1);delivery.world.objects[4]=JointObject(true,false,1);
    delivery.world.freezeSdkReplyDomain();
    SdkEpisodeModel two;two.goals={SdkPredicate{"puton",{{3,2}}},SdkPredicate{"puton",{{4,2}}}};
    for(unsigned repeat=0;repeat<50;++repeat) {
        const auto batch=EpisodeRouter::propose(EpisodeBelief({{delivery,1}}),two,4096,std::chrono::milliseconds(1000));
        auto chosen=EpisodeRouteSearch::solve(EpisodeBelief({{delivery,1}}),two,batch.routes,{},ask,
            std::chrono::milliseconds(5000),16384,std::chrono::milliseconds(1000));
        assert(chosen.value.lower==63 && !chosen.policy->stop); // two goals, 17 fees
        auto state=delivery;auto policy=chosen.policy;unsigned moves=0;
        while(!policy->stop) {
            moves+=policy->action.kind==JointActionKind::MOVE;
            const auto step=JointDynamics::step(state.world,policy->action);
            assert(step.observation.kind!=JointObservation::Kind::FEEDBACK || step.observation.success);
            state=two.next(state,policy->action,step.world,step.observation.success);policy=policy->children.at(step.observation);
        }
        assert(moves==1 && !state.world.hand && !state.world.plate && two.reward(state).goals_lower==2);
        // A permanent tray constraint must retain a serial delivery alternative.
        auto protected_model=two;protected_model.constraints={{SdkPredicate{"plate",{{3,0}}},false},
            {SdkPredicate{"plate",{{4,0}}},false}};
        state=delivery;state.credits={true,true};
        auto protected_plan=EpisodeRouteSearch::solve(EpisodeBelief({{state,1}}),protected_model,batch.routes,{},ask,
            std::chrono::milliseconds(5000),16384,std::chrono::milliseconds(1000));
        assert(protected_plan.value.lower==97); // 80 + 40 - 23; no tray violation
    }
    std::cout<<"complete task routes, hypothesis coverage, restoration, required sensing and 50 repeats passed\n";
}
