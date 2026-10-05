#include "sdk_episode.hpp"
#include "evaluate.h"
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <regex>
using namespace _home;
int main() {
    SdkEpisode initial;auto& w=initial.world;w.robot=1;w.locations={1,2};
    w.objects[1]=JointObject(false,false,1);w.objects[2]=JointObject(false,true,1);
    w.objects[3]=JointObject(true,false,1,2);w.objects[4]=JointObject(false,false,2);
    w.objects[5]=JointObject(true,false,-1,2);w.objects[6]=JointObject(false,true,2);
    w.freezeSdkReplyDomain();
    assert(w.initial_reply_counts.at({'a',1})==4 && w.initial_reply_counts.at({'a',2})==2);
    assert(w.initial_reply_counts.at({'i',2})==1 && w.initial_reply_counts.at({'i',6})==1);
    AskObservationModel ask({{'a',1},{'a',2},{'i',2},{'i',6}},.6,.3,.1,0);
    SdkEpisodeModel model;model.goals={SdkPredicate{"pickup",{{3,0}}}};
    EpisodeBelief belief({{initial,1}});
    double one=0,two=0,inside=0,unknown=0,empty=0;
    for(const auto& b:belief.branches(model,{JointActionKind::ASK,4},ask)) {
        const auto r=b.observation.reply;
        if(r==LocationHypothesis('a',1))one=b.probability;
        if(r==LocationHypothesis('a',2))two=b.probability;
        if(r==LocationHypothesis('i',2))inside=b.probability;
        if(r==LocationHypothesis('i',6))empty=b.probability;
        if(r==LocationHypothesis('?',-1))unknown=b.probability;
    }
    assert(std::abs(one-.15)<1e-9 && std::abs(two-.675)<1e-9 &&
        std::abs(inside-.0375)<1e-9 && std::abs(unknown-.1)<1e-9 && std::abs(empty-.0375)<1e-9);
    Evaluate sdk;sdk.newteam("noise-pool",true);
    const std::string env="(:domain (hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) (closed 2) "
        "(sort 3 cup) (size 3 small) (color 3 red) (at 3 1) (inside 3 2) "
        "(sort 4 table) (size 4 big) (at 4 2) (sort 5 bottle) (size 5 small) (color 5 blue) (inside 5 2) "
        "(sort 6 closet) (size 6 big) (type 6 container) (at 6 2) (closed 6))";
    const std::string ins="(:ins (:task (pickup X) (:cond (sort X cup) (color X red))))";
    assert(sdk.init_et(env.c_str(),env.size()) && sdk.init_it(ins.c_str(),ins.size()));
    // Exercise each of the eight actual SDK random-pool indices once. This is
    // semantic enumeration, not a statistical calibration of candidate scores.
    for(unsigned index=0;index<8;++index) {
        unsigned seed=1;
        for(;seed<100000;++seed) {
            std::srand(seed);const auto branch=std::rand()%10;
            if(branch>=6 && branch<=8 && unsigned(std::rand()%8)==index)break;
        }
        assert(seed<100000);std::srand(seed);const auto raw=sdk.EvaluateAskLoc(4);
        const auto expected=index<4?"at(4,1)":index<6?"at(4,2)":index==6?"inside(4,2)":"inside(4,6)";
        assert(raw==expected);
        JointObservation o;o.kind=JointObservation::Kind::ANSWER;
        o.reply=index<4?LocationHypothesis('a',1):index<6?LocationHypothesis('a',2):LocationHypothesis('i',index==6?2:6);
        assert(belief.observe(model,{JointActionKind::ASK,4},o,ask,index+1)==EpisodeUpdate::APPLIED);
    }
    assert(sdk.EndEvaluation(5.0)==-16 && belief.support().front().episode.paid==16);
    std::cout<<"SDK wrong-answer pool: container declarations, empty container present, inside edge count irrelevant, eight indices checked\n";
}
