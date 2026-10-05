#include "episode_proposal.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
using namespace _home;
int main() {
    JointWorld w;w.robot=1;w.locations={1,2};w.objects[2]=JointObject(false,true,1,0,true);
    w.objects[3]=JointObject(true,false,1);
    w.objects[4]=JointObject(false,false,2); // SDK loc(2) has an initial AT witness
    PublicPriorFactor at;at.field=PriorField::EXPLICIT_AT;at.object=3;at.values={{1,.2},{2,.3},{-1,.5}};
    PublicPriorFactor inside;inside.field=PriorField::INSIDE_EDGE;inside.object=3;inside.parent=2;inside.values={{0,.5},{1,.5}};
    JointObservation first;first.kind=JointObservation::Kind::VISIBLE;first.ids={2,3};
    JointObservation last=first;last.ids={3,4};
    JointObservation ok;ok.success=true;
    std::vector<EpisodeEvidence> history={{1,{JointActionKind::SENSE},first},
        {2,{JointActionKind::MOVE,2},ok},{3,{JointActionKind::SENSE},last}};
    SdkEpisodeModel model;model.goals={SdkPredicate{"pickup",{{3,0}}}};
    AskObservationModel ask({{'a',1},{'a',2},{'i',2}});
    for(unsigned repeat=0;repeat<50;++repeat) {
        auto proposal=EpisodeProposal::generate(w,{at,inside},history,0,32,7,262144,std::chrono::milliseconds(1000));
        assert(proposal.complete && proposal.scenes.size()==32);
        double mass=0;
        for(const auto& s:proposal.scenes) {
            assert(s.episode.paid==0 && s.episode.world.robot==1);
            assert(s.episode.world.objects.at(3).at==2 && s.episode.world.objects.at(3).inside.count(2));
            assert(s.episode.world.initial_reply_counts.at({'a',2})==2); // regenerated actual AT-entry domain
            mass+=s.weight;
        }
        assert(std::abs(mass-.15)<1e-9); // exact block prior/q correction
        assert(proposal.block_cache_hits==31 && proposal.checks<=18);
        auto bounded=EpisodeProposal::generate(w,{at,inside},history,0,32,7,18,std::chrono::milliseconds(1000));
        assert(bounded.complete && bounded.scenes.size()==32 && bounded.checks==proposal.checks);
        SdkEpisode initial;initial.world=w;
        EpisodeReplay replay(EpisodeBelief({{initial,1}}));
        assert(replay.observe(model,history[0].action,first,ask,1)==EpisodeUpdate::APPLIED);
        assert(replay.observe(model,history[1].action,ok,ask,2)==EpisodeUpdate::APPLIED);
        assert(replay.observe(model,history[2].action,last,ask,3)==EpisodeUpdate::SUPPORT_MISS);
        auto repaired=replay.repair(model,ask,proposal.scenes,4096,std::chrono::milliseconds(1000));
        assert(repaired.installed && replay.belief().support().front().episode.paid==6);
        assert(replay.belief().support().front().episode.world.robot==2);
        auto cut=EpisodeProposal::generate(w,{at,inside},history,0,32,7,1,std::chrono::milliseconds(1000));
        assert(!cut.complete && cut.work_cut && cut.scenes.empty());
    }
    // Stored co-location is an alternative to explicit at. Public visibility
    // must not collapse this to a single location claim.
    auto stored=w;stored.hand=3;stored.objects[3].at=2;
    auto storage=EpisodeProposal::generate(stored,{at,inside},{{1,{JointActionKind::SENSE},first}},0,32,9,4096,std::chrono::milliseconds(1000));
    assert(storage.complete && !storage.scenes.empty());bool alternative=false;
    for(const auto& s:storage.scenes)alternative|=s.episode.world.objects.at(3).at!=1;
    assert(alternative);
    PublicPriorFactor hand;hand.field=PriorField::HAND;hand.values={{0,.5},{3,.5}};
    auto mixed=EpisodeProposal::generate(w,{at,inside,hand},{{1,{JointActionKind::SENSE},first}},0,32,7,1000,std::chrono::milliseconds(1000));
    assert(mixed.complete && mixed.scenes.size()==32 && mixed.block_cache_hits==30);
    double mixed_mass=0;bool empty=false,held=false;
    for(const auto& s:mixed.scenes) {
        mixed_mass+=s.weight;empty|=s.episode.world.hand==0;held|=s.episode.world.hand==3;
        if(!s.episode.world.hand)assert(s.episode.world.objects.at(3).at==1 || s.episode.world.objects.at(3).inside.count(2));
    }
    assert(empty && held && std::abs(mixed_mass-.8)<1e-9); // .5*.6+.5*1
    bool rejected=false;
    try{EpisodeProposal::generate(w,{at},{{0,{JointActionKind::SENSE},first}},0,1,0,100,std::chrono::milliseconds(1000));}
    catch(const std::invalid_argument&){rejected=true;}assert(rejected);
    std::cout<<"public block conditioning, importance mass, replayed fees, storage alternatives and 50 repeats passed\n";
}
