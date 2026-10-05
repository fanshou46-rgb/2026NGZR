#include "episode_routes.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
using namespace _home;
namespace {
double future(const std::shared_ptr<EpisodePolicy>& policy,const EpisodeLatencyModel& time) {
    if(policy->stop)return 0;
    double ms=0;
    for(const auto& branch:policy->children)
        ms+=policy->probabilities.at(branch.first)*(time.estimate(policy->action,branch.first).median_ms+future(branch.second,time));
    return ms;
}
}
int main() {
    auto time=EpisodeLatencyModel::development();
    assert(time.action[static_cast<unsigned>(JointActionKind::ASK)].count==124);
    assert(time.action[static_cast<unsigned>(JointActionKind::SENSE)].count==323);
    assert(time.failed[static_cast<unsigned>(JointActionKind::MOVE)].count==6);
    assert(time.failed[static_cast<unsigned>(JointActionKind::PICKUP)].count==0); // fallback, not fabricated failures
    SdkEpisode e;e.world.robot=1;e.world.locations={1,2};e.world.objects[3]=JointObject(true,false,1);e.world.freezeSdkReplyDomain();e.paid=17;
    SdkEpisodeModel m;m.goals={SdkPredicate{"pickup",{{3,0}}}};
    const AskObservationModel ask({{'a',1},{'a',2}},.6,.3,.1,0);
    const EpisodeRoute pickup={{JointActionKind::PICKUP,3}};
    auto invalid=time;invalid.action[static_cast<unsigned>(JointActionKind::SENSE)].median_ms=-1;
    bool rejected=false;
    try{EpisodeRouteSearch::solve(EpisodeBelief({{e,1}}),m,{pickup},{},ask,std::chrono::milliseconds(5000),1000,std::chrono::milliseconds(1000),true,&invalid);}
    catch(const std::invalid_argument&){rejected=true;}
    assert(rejected);
    auto timedSolve=[&](const EpisodeBelief& b,const std::vector<EpisodeRoute>& routes,const std::vector<JointAction>& info,std::chrono::milliseconds left) {
        auto p=EpisodeRouteSearch::solve(b,m,routes,info,ask,left,1000000,std::chrono::milliseconds(1000),true,&time);
        assert(!p.wall_cut && !p.work_cut);
        const auto ms=future(p.policy,time);
        assert(std::abs(ms-p.predicted_sdk_ms)<1e-9);
        assert(std::abs(p.value.lower-.02*ms-p.proxy_lower)<1e-9);
        assert(std::abs(p.value.upper-.02*ms-p.proxy_upper)<1e-9);
        return p;
    };
    auto solve=[&](const EpisodeBelief& b,const std::vector<EpisodeRoute>& routes,const std::vector<JointAction>& info) {
        return timedSolve(b,routes,info,std::chrono::milliseconds(5000));
    };
    for(unsigned repeat=0;repeat<50;++repeat) {
        auto p=solve(EpisodeBelief({{e,1}}),{pickup},{});
        assert(!p.policy->stop && p.value.lower==21); // 40 - 17 previous - 2 current
        assert(std::abs(p.predicted_sdk_ms-111.235163)<1e-9); // previous time is not charged
        auto fail=e;fail.world.objects[4]=JointObject(true,false,2);fail.world.hand=4;
        auto split=solve(EpisodeBelief({{e,.5},{fail,.5}}),{pickup},{});
        assert(!split.policy->stop && split.value.lower==1); // .5*21 + .5*(-19)
        JointObservation failed;failed.success=false;
        assert(split.policy->children.at(failed)->stop);
        assert(std::abs(split.predicted_sdk_ms-111.235163)<1e-9); // false pays time and fee once
    }
    // Benefit is still allowed when its full expected tail beats Stop.
    auto restoration=e;restoration.world.hand=3;
    SdkEpisodeModel delivery;delivery.goals={SdkPredicate{"puton",{{3,4}}}};
    restoration.world.objects[4]=JointObject(false,false,2);restoration.world.freezeSdkReplyDomain();
    restoration.world.initial_reply_counts[{'a',2}]=1;
    EpisodeRoute drop={{JointActionKind::MOVE,2},{JointActionKind::SENSE},{JointActionKind::PUTDOWN,3}};
    auto restored=EpisodeRouteSearch::solve(EpisodeBelief({{restoration,1}}),delivery,{drop},{},ask,
        std::chrono::milliseconds(5000),1000000,std::chrono::milliseconds(1000),true,&time);
    assert(!restored.policy->stop && restored.value.lower==16 && !restored.policy->children.begin()->second->stop);
    assert(restored.policy->children.begin()->second->action.kind==JointActionKind::SENSE);
    assert(std::abs(future(restored.policy,time)-restored.predicted_sdk_ms)<1e-9);
    // A positive base gain alone cannot justify an excessively slow full tail.
    EpisodeRoute long_route;
    for(unsigned i=0;i<12;++i)long_route.push_back({JointActionKind::SENSE});
    long_route.push_back({JointActionKind::PICKUP,3});auto clean=e;clean.paid=0;
    auto base=EpisodeRouteSearch::solve(EpisodeBelief({{clean,1}}),m,{long_route},{},ask,
        std::chrono::milliseconds(5000),1000000,std::chrono::milliseconds(1000),true);
    assert(!base.policy->stop && base.value.lower==26);
    auto priced=solve(EpisodeBelief({{clean,1}}),{long_route},{});
    assert(priced.policy->stop && priced.predicted_sdk_ms==0 && priced.proxy_lower==0);
    auto useful=solve(EpisodeBelief({{clean,1}}),{long_route,pickup},{});
    assert(!useful.policy->stop && useful.policy->action.kind==JointActionKind::PICKUP && useful.value.lower==38);
    auto short_time=timedSolve(EpisodeBelief({{clean,1}}),{pickup},{},std::chrono::milliseconds(100));
    assert(short_time.policy->stop); // empirical reserve, actual deadline still enforced separately
    auto other=clean;other.world.objects[3].at=2;other.world.initial_reply_counts[{'a',2}]=1;
    const auto uncertain=EpisodeBelief({{clean,.5},{other,.5}});
    solve(uncertain,{{{JointActionKind::PICKUP,3}},{{JointActionKind::MOVE,2},{JointActionKind::PICKUP,3}}},{{JointActionKind::ASK,3},{JointActionKind::SENSE}});
    std::cout<<"50 repeats: SDK time/base/proxy distinct, paid prefix and false charged once, positive restoration and necessary Sense retained, full information tails checked\n";
}
