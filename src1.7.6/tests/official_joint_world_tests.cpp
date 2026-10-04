#include "joint_world.hpp"
#include "evaluate.h"
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <regex>
#include <cctype>
using namespace _home;
static bool sdkAction(Evaluate& sdk,const JointAction& a) {
    switch(a.kind) {
    case JointActionKind::MOVE:return sdk.EvaluateMove(a.a);
    case JointActionKind::PICKUP:return sdk.EvaluatePickUp(a.a);
    case JointActionKind::PUTDOWN:return sdk.EvaluatePutDown(a.a);
    case JointActionKind::TOPLATE:return sdk.EvaluateToPlate(a.a);
    case JointActionKind::FROMPLATE:return sdk.EvaluateFromPlate(a.a);
    case JointActionKind::OPEN:return sdk.EvaluateOpen(a.a);
    case JointActionKind::CLOSE:return sdk.EvaluateClose(a.a);
    case JointActionKind::PUTIN:return sdk.EvaluatePutIn(a.a,a.b);
    case JointActionKind::TAKEOUT:return sdk.EvaluateTakeOut(a.a,a.b);
    default:assert(false);return false;
    }
}
static std::string domain(const JointWorld& w) {
    std::ostringstream s;s<<"(:domain (at 0 "<<w.robot<<") (hold "<<w.hand<<") (plate "<<w.plate<<") ";
    for(const auto& item:w.objects) {
        const auto& o=item.second;auto id=item.first;
        s<<"(sort "<<id<<' '<<(o.container?"cupboard":o.small?"cup":"table")<<") (size "<<id<<' '<<(o.small?"small":"big")<<") ";
        if(id==5)s<<"(color 5 red) ";
        if(o.at>=0)s<<"(at "<<id<<' '<<o.at<<") ";
        for(unsigned parent:o.inside)s<<"(inside "<<id<<' '<<parent<<") ";
        if(o.container)s<<"(type "<<id<<" container) ("<<(o.opened?"opened":"closed")<<' '<<id<<") ";
    }
    return s.str()+")";
}
static void compareState(const JointWorld& expected) {
    std::ifstream f("vstate.lp");assert(f.good());
    std::string s((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
    s.erase(std::remove_if(s.begin(),s.end(),[](unsigned char c){return std::isspace(c);}),s.end());
    auto atom=[&](const std::string& name){return s.find("h("+name+",0)")!=std::string::npos;};
    assert(atom("at(0,"+std::to_string(expected.robot)+")"));
    assert(atom("hold("+std::to_string(expected.hand)+")"));
    assert(atom("plate("+std::to_string(expected.plate)+")"));
    for(const auto& item:expected.objects) {
        const auto id=item.first;const auto& o=item.second;
        for(int loc:expected.locations) {
            bool actual=atom("at("+std::to_string(id)+","+std::to_string(loc)+")");
            // Initial vstate may omit static hold/plate closure; the SDK's
            // action model derives it from the same robot location.
            actual=actual || ((expected.hand==id || expected.plate==id) && loc==expected.robot);
            assert(actual==expected.atLocation(id,loc));
        }
        for(const auto& other:expected.objects) if(other.second.container)
            assert(atom("inside("+std::to_string(id)+","+std::to_string(other.first)+")")==bool(o.inside.count(other.first)));
        if(o.container)assert(atom(std::string(o.opened?"opened(":"closed(")+std::to_string(id)+")"));
    }
}
static void policyRun(JointWorld actual,int test) {
    actual.locations.insert(0);actual.robot=0;actual.objects[5].at=(test%2)?2:1;
    auto left=actual,right=actual;left.objects[5].at=1;right.objects[5].at=2;
    left.freezeSdkReplyDomain();right.freezeSdkReplyDomain();
    JointBelief belief({{left,.5},{right,.5}});
    AskObservationModel model({{'a',0},{'a',1},{'a',2},{'i',2}},.6,.3,.1,0);
    std::vector<JointAction> actions={{JointActionKind::MOVE,1},{JointActionKind::MOVE,2},{JointActionKind::ASK,5}};
    auto plan=JointPolicySearch::solve(belief,actions,model,
        [](const JointWorld& w){return w.atLocation(5,w.robot)?40.:0.;},2,
        std::chrono::milliseconds(1000),4096,std::chrono::milliseconds(1000));
    assert(plan.support_complete && plan.search_complete);
    assert(!plan.policy->stop && plan.policy->action.kind==JointActionKind::ASK);
    // The same prior and policy are constructed before the SDK receives truth.
    Evaluate sdk;std::string name="joint-policy-"+std::to_string(test);
    sdk.newteam(name.c_str(),test>=8);
    std::string env=domain(actual),task="(:ins (:task (goto X) (:cond (sort X table) (color X red))))";
    assert(sdk.init_et(env.c_str(),env.size()));assert(sdk.init_it(task.c_str(),task.size()));
    // Deliberately exercise wrong and unknown feedback, not only lucky truthful
    // samples. Initial entries retain duplicates: at(0), at(1), at(1),
    // at(2), at(target), inside(2). The fourth entry is at(2).
    unsigned seed=1;
    if(test>=8) {
        for(;seed<10000;++seed) {
            std::srand(seed);int branch=std::rand()%10;
            if(test==9 && branch==9)break;
            if(test==8 && branch>=6 && branch<=8 && std::rand()%6==3)break;
        }
        assert(seed<10000);
    }
    std::srand(seed);
    std::string answer=sdk.EvaluateAskLoc(5);
    if(test==8)assert(answer=="at(5,2)");
    if(test==9)assert(answer=="not_known");
    JointObservation observation;observation.kind=JointObservation::Kind::ANSWER;
    std::smatch match;
    if(std::regex_match(answer,match,std::regex("(at|inside)\\(5,([0-9]+)\\)")))
        observation.reply={match[1]=="at"?'a':'i',std::stoi(match[2])};
    else assert(answer=="not_known");
    assert(belief.observe({JointActionKind::ASK,5},observation,model,1));
    auto found=plan.policy->children.find(observation);assert(found!=plan.policy->children.end());
    const auto& next=*found->second;assert(!next.stop && next.action.kind==JointActionKind::MOVE);
    // Even a truthful reply leaves both hypotheses possible under the noisy model.
    assert(belief.support().size()==2);
    JointObservation feedback;feedback.success=sdkAction(sdk,next.action);assert(feedback.success);
    assert(belief.observe(next.action,feedback,model,2));
    actual=JointDynamics::step(actual,next.action).world;compareState(actual);
    const int expected=(actual.atLocation(5,actual.robot)?40:0)-6;
    const int score=sdk.EndEvaluation(5.0);assert(score==expected);
    std::ofstream trace(name+".txt");
    trace<<"answer="<<answer<<"\nmove="<<next.action.a<<"\nscore="<<score
         <<"\nposterior-first="<<belief.support()[0].weight<<"\n";
    std::cerr<<name<<" answer="<<answer<<" move="<<next.action.a<<" SDK="<<score<<'\n';
}
int main(int argc,char** argv) {
    assert(argc==2);int test=std::atoi(argv[1]);
    JointWorld w;w.robot=1;w.locations={1,2};
    w.objects={{1,{false,false,1}},{2,{false,true,1,0,false}},
               {3,{true,false,-1,2}},{4,{true,false,2}},{5,{false,false,2}}};
    if(test>=6 && test<=9) {policyRun(w,test);return 0;}
    using K=JointActionKind;
    std::vector<JointAction> actions;
    if(test==0)actions={{K::SENSE},{K::OPEN,2},{K::SENSE},{K::TAKEOUT,3,2},{K::MOVE,2},{K::SENSE},{K::TOPLATE,3},{K::SENSE},{K::FROMPLATE,3},{K::PUTDOWN,3}};
    else if(test==1) {w.hand=3;w.objects[3].inside.clear();w.plate=4;actions={{K::SENSE},{K::MOVE,2},{K::SENSE},{K::TOPLATE,3},{K::FROMPLATE,4},{K::OPEN,2}};}
    else if(test==2) {w.objects[3].at=1;actions={{K::SENSE},{K::PICKUP,3},{K::SENSE},{K::PUTDOWN,3},{K::SENSE}};}
    else if(test==3)actions={{K::TAKEOUT,3,2},{K::OPEN,2},{K::TAKEOUT,3,2},{K::CLOSE,2},{K::PUTDOWN,3},{K::CLOSE,2},{K::CLOSE,2}};
    else if(test==4)actions={{K::MOVE,1},{K::CLOSE,2},{K::OPEN,2},{K::OPEN,2},{K::MOVE,2},{K::OPEN,2},{K::SENSE}};
    else if(test==5) {w.hand=3;w.objects[3].inside.clear();w.objects[3].at=1;w.objects[2].opened=true;actions={{K::PUTIN,3,2},{K::SENSE},{K::CLOSE,2},{K::SENSE},{K::OPEN,2},{K::SENSE},{K::TAKEOUT,3,2}};}
    else if(test==10) {w.objects[3].at=1;w.objects[2].opened=true;w.objects[6]={false,true,2,0,true};
        actions={{K::PICKUP,3},{K::MOVE,2},{K::PUTIN,3,6},{K::SENSE},{K::TAKEOUT,3,6},{K::PUTDOWN,3},{K::MOVE,1},{K::OPEN,2},{K::TAKEOUT,3,2},{K::SENSE}};}
    else if(test==11) {w.plate=3;w.objects[2].opened=true;
        actions={{K::SENSE},{K::TAKEOUT,3,2},{K::MOVE,2},{K::PUTDOWN,3},{K::PICKUP,3},{K::FROMPLATE,3},{K::PUTDOWN,3},{K::SENSE}};}
    else assert(false);
    Evaluate sdk;std::string name="joint-"+std::to_string(test);sdk.newteam(name.c_str());
    std::string env=domain(w),task="(:ins (:task (goto X) (:cond (sort X table) (color X red))))";
    assert(sdk.init_et(env.c_str(),env.size()));assert(sdk.init_it(task.c_str(),task.size()));
    int cost=0;
    for(std::size_t n=0;n<actions.size();++n) {
        const auto& a=actions[n];auto next=JointDynamics::step(w,a);cost+=a.cost();
        if(a.kind==K::SENSE) {
            std::vector<unsigned> ids;sdk.EvaluateSense(ids);
            std::set<unsigned> actual(ids.begin(),ids.end());
            if(actual!=next.observation.ids) {std::cerr<<name<<" step "<<n<<" sense mismatch\n";return 1;}
        } else {
            bool actual=sdkAction(sdk,a);
            if(actual!=next.observation.success) {std::cerr<<name<<" step "<<n<<" feedback mismatch\n";return 1;}
        }
        w=std::move(next.world);
        compareState(w);
        // Preserve every intermediate state, including failed-action unchanged
        // states, so a matching final score cannot hide a transition error.
        std::ifstream input("vstate.lp");
        std::ofstream output(name+"-step-"+std::to_string(n)+".lp");output<<input.rdbuf();
    }
    int expected=(w.atLocation(5,w.robot)?40:0)-cost;
    int actual=sdk.EndEvaluation(5.0);
    std::cerr<<name<<" expected="<<expected<<" SDK="<<actual<<'\n';assert(expected==actual);
    for(const char* file:{"vstate.lp","vanswer.txt","vaction.lp"}) {
        std::ifstream input(file);std::ofstream output(name+"."+file);output<<input.rdbuf();
    }
}
