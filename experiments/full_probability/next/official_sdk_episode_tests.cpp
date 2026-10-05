#include "sdk_episode.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <regex>
#include <sstream>
using namespace _home;
static SdkPredicate task(const char* verb,unsigned x,unsigned y=0) {SdkPredicate p;p.verb=verb;p.bindings={{x,y}};return p;}
static std::string domain(const JointWorld& w) {
    std::ostringstream s;s<<"(:domain (hold "<<w.hand<<") (plate "<<w.plate<<") (at 0 "<<w.robot<<") ";
    for(const auto& pair:w.objects) {
        const auto& o=pair.second;unsigned id=pair.first;
        s<<"(sort "<<id<<' '<<(id==1?"human":o.container?"cupboard":o.small?"cup":"table")<<") (size "<<id<<' '<<(o.small?"small":"big")<<") ";
        if(id==3)s<<"(color 3 red) ";
        if(o.at>=0)s<<"(at "<<id<<' '<<o.at<<") ";
        for(unsigned parent:o.inside)s<<"(inside "<<id<<' '<<parent<<") ";
        if(o.container)s<<"(type "<<id<<" container) ("<<(o.opened?"opened":"closed")<<' '<<id<<") ";
    }
    return s.str()+")";
}
int main(int argc,char** argv) {
    assert(argc==2);int test=std::atoi(argv[1]);assert(test>=0&&test<8);
    SdkEpisode left,right;left.world.robot=1;left.world.locations={0,1,2};
    left.world.objects={{1,JointObject(false,false,1)},{2,JointObject(false,true,1)},{3,JointObject(true,false,1)},{4,JointObject(false,false,2)}};
    right=left;SdkEpisodeModel m;std::string ins;
    std::vector<JointAction> actions;
    if(test<2) {
        right.world.plate=3;m.goals={task("pickup",3)};
        m.constraints={{task("closed",2),true},{task("near",3,1),true}};
        ins="(:task (pickup X) (:cond (sort X cup) (color X red))) (:cons_notnot (:info (closed X) (:cond (sort X cupboard)))) (:cons_notnot (:info (near X Y) (:cond (sort X cup) (color X red) (sort Y human))))";
        actions={{JointActionKind::PICKUP,3}};
    } else if(test<4) {
        right.world.objects[2].opened=true;m.goals={task("open",2)};m.constraints={{task("closed",2),true}};
        ins="(:task (open X) (:cond (sort X cupboard))) (:cons_notnot (:info (closed X) (:cond (sort X cupboard))))";
        actions={{JointActionKind::OPEN,2}};
    } else {
        left.world.robot=right.world.robot=0;right.world.objects[3].at=2;
        // Goto accepts any object; a small target avoids an extra static table
        // binding, and does not supply its true location to the decision code.
        m.goals={task("goto",3)};
        ins="(:task (goto X) (:cond (sort X cup) (color X red)))";
        actions={{JointActionKind::ASK,3},{JointActionKind::MOVE,1},{JointActionKind::MOVE,2}};
    }
    left.credits=right.credits=std::vector<bool>(m.constraints.size(),true);
    left.world.freezeSdkReplyDomain();right.world.freezeSdkReplyDomain();
    EpisodeBelief belief({{left,.5},{right,.5}});
    AskObservationModel ask({{'a',0},{'a',1},{'a',2},{'i',2}});
    auto plan=EpisodePolicySearch::solve(belief,m,actions,ask,test<4?1:2,
        std::chrono::milliseconds(1000),4096,std::chrono::milliseconds(1000));
    assert(plan.support_complete && !plan.policy->stop);
    if(test>=4)assert(plan.policy->action.kind==JointActionKind::ASK);
    auto actual=test%2?right:left;
    // Actual SDK truth is supplied only after the prior and policy are frozen.
    Evaluate sdk;std::string name="episode-"+std::to_string(test);sdk.newteam(name.c_str(),test>=6);
    auto env=domain(actual.world);auto instructions="(:ins "+ins+")";
    assert(sdk.init_et(env.c_str(),env.size()));assert(sdk.init_it(instructions.c_str(),instructions.size()));
    std::srand(2026100403+test);
    auto policy=plan.policy;unsigned receipt=0;
    while(!policy->stop) {
        auto a=policy->action;JointObservation feedback;
        if(a.kind==JointActionKind::ASK) {
            feedback.kind=JointObservation::Kind::ANSWER;auto raw=sdk.EvaluateAskLoc(a.a);std::smatch match;
            if(std::regex_match(raw,match,std::regex("(at|inside)\\([0-9]+,([0-9]+)\\)")))feedback.reply={match[1]=="at"?'a':'i',std::stoi(match[2])};
            else assert(raw=="not_known");
            actual=m.next(actual,a,actual.world,false);
        } else {
            if(a.kind==JointActionKind::PICKUP)feedback.success=sdk.EvaluatePickUp(a.a);
            else if(a.kind==JointActionKind::OPEN)feedback.success=sdk.EvaluateOpen(a.a);
            else if(a.kind==JointActionKind::MOVE)feedback.success=sdk.EvaluateMove(a.a);
            else assert(false);
            auto predicted=JointDynamics::step(actual.world,a);assert(predicted.observation.success==feedback.success);
            actual=m.next(actual,a,predicted.world,feedback.success);
        }
        assert(belief.observe(m,a,feedback,ask,++receipt)==EpisodeUpdate::APPLIED);
        auto child=policy->children.find(feedback);assert(child!=policy->children.end());policy=child->second;
    }
    auto predicted=m.reward(actual);int score=sdk.EndEvaluation(5.0);
    assert(score>=predicted.lower && score<=predicted.upper);
    std::cout<<name<<" SDK="<<score<<" model="<<predicted.lower<<":"<<predicted.upper<<" receipts="<<receipt<<"\n";
}
