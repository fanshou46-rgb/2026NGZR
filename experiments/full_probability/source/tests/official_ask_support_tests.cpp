#include "episode_prior.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <regex>
using namespace _home;
int main(int argc,char** argv) {
    assert(argc==2);int test=std::atoi(argv[1]);assert(test>=0&&test<4);
    SdkEpisode initial;auto& w=initial.world;w.robot=1;w.locations={1,2};
    w.objects[1]=JointObject(false,false,1);w.objects[2]=JointObject(false,true,1);
    w.objects[3]=JointObject(true,false,-1);w.objects[4]=JointObject(false,false,2);
    if(test>=2){w.objects[3].at=1;w.objects[3].inside.insert(2);}
    w.freezeSdkReplyDomain();
    SdkEpisodeModel model;model.goals={SdkPredicate{"pickup",{{3,0}}}};
    auto ask=AskObservationModel({{'a',1},{'a',2},{'i',2}},test%2?.6:1,test%2?.3:0,test%2?.1:0,0).withPersistentAnswerOrderPrior();
    auto prior=EpisodePrior::generate(w,{},0,32,7,true);
    EpisodeBelief belief(std::move(prior.scenes));
    Evaluate sdk;std::string name="ask-support-"+std::to_string(test);sdk.newteam(name.c_str(),test%2);
    const std::string env="(:domain (hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) (closed 2) "
        "(sort 3 cup) (size 3 small) "+std::string(test>=2?"(at 3 1) (inside 3 2) ":"")+
        "(sort 4 table) (size 4 big) (at 4 2))";
    const std::string ins="(:ins (:task (pickup X) (:cond (sort X cup))))";
    assert(sdk.init_et(env.c_str(),env.size()) && sdk.init_it(ins.c_str(),ins.size()));
    for(unsigned event=1;event<=5;++event) {
        std::srand(2026100403+event);auto raw=sdk.EvaluateAskLoc(3);
        JointObservation observation;observation.kind=JointObservation::Kind::ANSWER;
        if(test<2){assert(raw.empty());observation.reply={'!',-1};}
        else if(raw!="not_known") {
            std::smatch match;assert(std::regex_match(raw,match,std::regex("(at|inside)\\(3,([0-9]+)\\)")));
            observation.reply={match[1]=="at"?'a':'i',std::stoi(match[2])};
        }
        assert(belief.observe(model,{JointActionKind::ASK,3},observation,ask,event)==EpisodeUpdate::APPLIED);
        assert(belief.support().front().episode.paid==int(event)*2);
    }
    assert(sdk.EndEvaluation(5.0)==-10);
    std::cout<<"official blank/nonunique Ask feedback supported; selector prior is explicit and uncalibrated\n";
}
