#include "episode_replay.hpp"
#include <cassert>
#include <iostream>
#include <stdexcept>
using namespace _home;
namespace {
JointWorld world(bool open) {
    JointWorld w;w.robot=1;w.locations={1,2};w.objects[2]=JointObject(false,true,1,0,open);
    w.objects[3]=JointObject(true,false,1);w.freezeSdkReplyDomain();w.validate();return w;
}
JointObservation feedback(bool ok) {JointObservation o;o.success=ok;return o;}
SdkEpisode initialEpisode(const JointWorld& w) {SdkEpisode e;e.world=w;e.credits={true};return e;}
}
int main() {
    AskObservationModel ask({{'a',1},{'a',2}},.6,.3,.1,0);
    SdkEpisodeModel model;model.goals={SdkPredicate{"pickup",{{3,0}}}};
    model.constraints={SdkConstraint{SdkPredicate{"close",{{2,0}}},true}};
    for(unsigned repeat=0;repeat<50;++repeat) {
        const auto closed=world(false),opened=world(true);
        WeightedEpisode initial{initialEpisode(closed),1};
        EpisodeReplay replay(EpisodeBelief({initial}));
        assert(replay.observe(model,{JointActionKind::OPEN,2},feedback(true),ask,1)==EpisodeUpdate::APPLIED);
        assert(replay.observe(model,{JointActionKind::CLOSE,2},feedback(true),ask,2)==EpisodeUpdate::APPLIED);
        assert(!replay.belief().support()[0].episode.credits[0]); // close cannot restore history
        // The modeled PickUp succeeds. Actual false is a support miss, paid once.
        assert(replay.observe(model,{JointActionKind::PICKUP,3},feedback(false),ask,3)==EpisodeUpdate::SUPPORT_MISS);
        assert(!replay.belief().modelValid() && replay.belief().support()[0].episode.paid==6);
        assert(replay.observe(model,{JointActionKind::PICKUP,3},feedback(false),ask,3)==EpisodeUpdate::DUPLICATE);
        auto hidden=closed;hidden.plate=3; // public false explained by independent tray storage
        const std::vector<WeightedEpisode> candidates={initial,{initialEpisode(hidden),1}};
        auto cut=replay.repair(model,ask,candidates,1,std::chrono::milliseconds(1000));
        assert(!cut.installed && cut.work_cut && !replay.belief().modelValid());
        auto repaired=replay.repair(model,ask,candidates,32,std::chrono::milliseconds(1000));
        assert(repaired.installed && replay.belief().modelValid());
        const auto& e=replay.belief().support().front().episode;
        assert(e.paid==6 && e.world.plate==3 && !e.credits[0]);
        assert(model.reward(e).lower==34); // goal fulfilled by tray, history still damaged
        assert(replay.observe(model,{JointActionKind::PICKUP,3},feedback(false),ask,3)==EpisodeUpdate::DUPLICATE);
        assert(replay.belief().support()[0].episode.paid==6 && replay.evidence().size()==3);
        bool invalid=false;
        try{replay.observe(model,{JointActionKind::PICKUP,3},feedback(true),ask,3);}catch(const std::invalid_argument&){invalid=true;}
        assert(invalid);
        invalid=false;
        try{replay.observe(model,{JointActionKind::PICKUP,3},feedback(false),ask,2);}catch(const std::invalid_argument&){invalid=true;}
        assert(invalid);
        EpisodeReplay noise(EpisodeBelief({initial,{initialEpisode(opened),1}}));
        JointObservation seen;seen.kind=JointObservation::Kind::VISIBLE;seen.ids={2,3};
        // Same visibility for both worlds; repair preserves uncertainty rather
        // than introducing a strong door claim.
        assert(noise.observe(model,{JointActionKind::SENSE},seen,ask,1)==EpisodeUpdate::APPLIED);
        assert(noise.repair(model,ask,{initial,{initialEpisode(opened),1}},8,std::chrono::milliseconds(1000)).installed);
        assert(noise.belief().support().size()==2 && noise.belief().support()[0].weight==.5);
    }
    std::cout<<"episode history replay, support repair and 50 deterministic repeats passed\n";
}
