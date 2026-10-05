#include "episode_prior.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
using namespace _home;
int main() {
    JointWorld world;world.robot=1;world.locations={1,2};world.objects[2]=JointObject(false,true,1);
    world.objects[3]=JointObject(true,false,1,2);
    auto ask=AskObservationModel({{'a',1},{'a',2},{'i',2}},1,0,0,0).withPersistentAnswerOrderPrior();
    SdkEpisodeModel model;model.goals={SdkPredicate{"pickup",{{3,0}}}};
    for(unsigned repeat=0;repeat<50;++repeat) {
        auto sampled=EpisodePrior::generate(world,{},0,32,0,true);
        assert(!sampled.exact && sampled.scenes.size()==32);
        SdkEpisode at_scene,inside_scene;bool at=false,inside=false;
        for(const auto& s:sampled.scenes) {
            const auto answer=s.episode.world.selectedTruthfulReply(3);
            auto moved=JointDynamics::step(s.episode.world,{JointActionKind::MOVE,2});
            assert(moved.world.selectedTruthfulReply(3)==answer); // ranking stays fixed
            if(answer.first=='a'){at_scene=s.episode;at=true;}
            if(answer.first=='i'){inside_scene=s.episode;inside=true;}
        }
        assert(at && inside);
        auto unique=at_scene;unique.world.objects[3].inside.clear();
        EpisodeBelief belief({{unique,.5},{at_scene,.25},{inside_scene,.25}});
        JointObservation observation;observation.kind=JointObservation::Kind::ANSWER;observation.reply={'a',1};
        assert(belief.observe(model,{JointActionKind::ASK,3},observation,ask,1)==EpisodeUpdate::APPLIED);
        assert(belief.support().size()==2 && std::abs(belief.support()[0].weight-2.0/3)<1e-9);
        assert(belief.observe(model,{JointActionKind::ASK,3},observation,ask,2)==EpisodeUpdate::APPLIED);
        assert(belief.support().size()==2 && std::abs(belief.support()[0].weight-2.0/3)<1e-9);
        assert(belief.support()[0].episode.paid==4); // repeated truth is not a new selector draw
    }
    std::cout<<"persistent answer order, correct repeated Bayes weights and 50 repeats passed\n";
}
