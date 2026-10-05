#include "sdk_episode.hpp"
#include <cassert>
#include <cmath>
using namespace _home;
static SdkEpisode episode() {
    SdkEpisode e;e.world.robot=1;e.world.locations={1,2};
    e.world.objects[1]=JointObject(false,false,1);
    e.world.objects[2]=JointObject(false,true,1,0,false);
    e.world.objects[3]=JointObject(true,false,1);
    return e;
}
static SdkPredicate task(const char* verb,unsigned x,unsigned y=0) {
    SdkPredicate p;p.verb=verb;p.bindings={{x,y}};return p;
}
int main() {
    SdkEpisodeModel m;m.goals={task("pickup",3)};
    m.constraints={{task("closed",2),true},{task("near",3,1),true}};
    auto e=episode();e.credits={true,true};
    assert(m.reward(e).lower==0); // credits require G>0
    auto pick=JointAction(JointActionKind::PICKUP,3);
    auto result=JointDynamics::step(e.world,pick);
    auto held=m.next(e,pick,result.world,result.observation.success);
    assert(m.reward(held).lower==78 && held.paid==2);
    auto move=JointAction(JointActionKind::MOVE,2);result=JointDynamics::step(held.world,move);
    auto away=m.next(held,move,result.world,result.observation.success);
    assert(!away.credits[1] && m.reward(away).lower==54);
    move.a=1;result=JointDynamics::step(away.world,move);
    auto restored=m.next(away,move,result.world,result.observation.success);
    assert(!restored.credits[1] && m.reward(restored).lower==50);
    // Observation and failed physical calls are paid, without initial/extra
    // constraint checks. The authoritative SDK ledger starts eligible.
    e.world.objects[2].opened=true;
    auto sense=JointAction(JointActionKind::SENSE);result=JointDynamics::step(e.world,sense);
    auto observed=m.next(e,sense,result.world,result.observation.success);
    assert(observed.credits[0] && observed.paid==1);
    auto open=JointAction(JointActionKind::OPEN,2);result=JointDynamics::step(e.world,open);
    auto failed=m.next(e,open,result.world,result.observation.success);
    assert(failed.credits[0] && failed.paid==2);
    e=episode();e.credits={true,true};
    auto tray=e;tray.world.plate=3;
    EpisodeBelief b({{e,.7},{tray,.3}});
    AskObservationModel ask({{'a',1},{'a',2},{'i',2}});
    for(unsigned repeat=0;repeat<50;++repeat) {
        auto plan=EpisodePolicySearch::solve(b,m,{pick},ask,1,std::chrono::milliseconds(1000),16,std::chrono::milliseconds(100));
        assert(!plan.policy->stop && plan.policy->children.size()==2 && plan.transitions==2);
        assert(std::abs(plan.value.lower-78)<1e-9);
    }
    // A failure updates joint tray belief from public feedback, without oracle
    // access to a hidden state ID or asserting anything in the canonical world.
    JointObservation no;no.success=false;
    assert(b.observe(m,pick,no,ask,1)==EpisodeUpdate::APPLIED);
    assert(b.support().size()==1 && b.support()[0].episode.world.plate==3);
    assert(b.support()[0].episode.paid==2);
    assert(b.observe(m,pick,no,ask,1)==EpisodeUpdate::DUPLICATE);
    assert(b.support()[0].episode.paid==2);
    JointObservation impossible;impossible.kind=JointObservation::Kind::VISIBLE;impossible.ids={99};
    assert(b.observe(m,sense,impossible,ask,2)==EpisodeUpdate::SUPPORT_MISS);
    assert(!b.modelValid() && b.support()[0].episode.paid==3);
    assert(b.observe(m,sense,impossible,ask,2)==EpisodeUpdate::DUPLICATE);
    bool rejected=false;try{b.branches(m,sense,ask);}catch(const std::logic_error&){rejected=true;}assert(rejected);
    // Static ambiguous SDK grounding is an interval, not a convenient target.
    m.goals={task("pickup",3)};m.goals[0].bindings.push_back({1,0});
    auto score=m.reward(held);assert(score.goals_lower==0 && score.goals_upper==1);
    assert(score.lower==-2 && score.upper==78);
    // Work expiry retains a complete incumbent. Every represented feedback
    // still has a stop child even when deeper optimization has no allowance.
    m.goals={task("pickup",3)};
    EpisodeBelief full({{e,1}});
    auto cut=EpisodePolicySearch::solve(full,m,{pick,sense},ask,3,std::chrono::milliseconds(1000),1,std::chrono::milliseconds(100));
    assert(cut.work_cut && cut.transitions==1 && !cut.policy->stop && cut.policy->children.size()==1);
}
