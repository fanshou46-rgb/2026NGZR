#include "episode_router.hpp"
#include <cassert>
#include <iostream>
using namespace _home;
int main() {
    SdkEpisode initial;auto& w=initial.world;w.robot=1;w.locations={1,2,3};
    w.objects[1]=JointObject(false,false,3);w.objects[2]=JointObject(false,true,1);
    w.objects[3]=JointObject(true,false,1);w.objects[4]=JointObject(true,false,2);
    w.objects[5]=JointObject(false,false,2);w.objects[6]=JointObject(false,false,3);
    w.objects[7]=JointObject(true,false,1);w.objects[8]=JointObject(true,false,1);w.objects[9]=JointObject(true,false,3);
    w.freezeSdkReplyDomain();
    SdkEpisodeModel protected_model;
    protected_model.goals={SdkPredicate{"putin",{{7,2}}},SdkPredicate{"putin",{{8,2}}},
        SdkPredicate{"puton",{{4,6}}},SdkPredicate{"puton",{{3,5}}},SdkPredicate{"close",{{2,0}}},
        SdkPredicate{"pickup",{{9,0}}},SdkPredicate{"goto",{{1,0}}}};
    protected_model.constraints={{SdkPredicate{"inside",{{7,2}}},false},{SdkPredicate{"pickup",{{7,0}}},false},
        {SdkPredicate{"inside",{{8,2}}},false},{SdkPredicate{"pickup",{{8,0}}},false}};
    initial.credits={true,true,true,true};
    const AskObservationModel ask({{'a',1},{'a',2},{'a',3},{'i',2}});
    for(unsigned repeat=0;repeat<50;++repeat) {
        auto proposals=EpisodeRouter::propose(EpisodeBelief({{initial,1}}),protected_model,4096,std::chrono::milliseconds(1000));
        assert(!proposals.wall_cut && !proposals.work_cut);
        auto plan=EpisodeRouteSearch::solve(EpisodeBelief({{initial,1}}),protected_model,proposals.routes,{},ask,
            std::chrono::milliseconds(5000),16384,std::chrono::milliseconds(1000));
        auto state=initial;auto policy=plan.policy;unsigned moves=0;
        while(!policy->stop) {
            const auto action=policy->action;moves+=action.kind==JointActionKind::MOVE;
            assert(!(action.kind==JointActionKind::PICKUP && (action.a==7 || action.a==8)));
            auto next=JointDynamics::step(state.world,action);
            assert(next.observation.kind!=JointObservation::Kind::FEEDBACK || next.observation.success);
            state=protected_model.next(state,action,next.world,next.observation.success);
            policy=policy->children.at(next.observation);
        }
        const auto value=protected_model.reward(state);
        // Two deliveries in geographical order, one terminal pickup, two
        // initial/restored endpoints: 5*40 + 4*20 - 20 actual fees.
        assert(value.goals_lower==5 && value.credits==4 && state.paid==20 && moves==2 && plan.value.lower==260);
        auto unprotected=protected_model;unprotected.constraints.clear();auto free=initial;free.credits.clear();
        auto free_routes=EpisodeRouter::propose(EpisodeBelief({{free,1}}),unprotected,4096,std::chrono::milliseconds(1000));
        auto full=EpisodeRouteSearch::solve(EpisodeBelief({{free,1}}),unprotected,free_routes.routes,{},ask,
            std::chrono::milliseconds(5000),16384,std::chrono::milliseconds(1000));
        state=free;policy=full.policy;
        while(!policy->stop) {
            auto next=JointDynamics::step(state.world,policy->action);
            state=unprotected.next(state,policy->action,next.world,next.observation.success);
            policy=policy->children.at(next.observation);
        }
        assert(unprotected.reward(state).goals_lower==7); // no permanently disabled task
    }
    std::cout<<"50 repeats: two damaging tasks omitted together, ordered transport, fees20/base260, no-constraint full7 counterfactual passed\n";
}
