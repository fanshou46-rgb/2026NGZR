#include "joint_world.hpp"
#include <cassert>
#include <cmath>
#include <cstdlib>
using namespace _home;
static bool close(double a,double b) {return std::abs(a-b)<1e-8;}
static JointWorld base() {
    JointWorld w;w.robot=1;w.locations={1,2};
    w.objects={{1,{false,false,1}},{2,{false,true,1,0,false}},
               {3,{true,false,-1,2}},{4,{true,false,2}},{5,{false,false,2}}};
    return w;
}
static JointStep act(JointWorld w,JointActionKind a,unsigned x=0,unsigned y=0) {
    return JointDynamics::step(w,{a,x,y});
}
static JointWorld target(int at) {
    auto w=base();w.locations.insert(0);w.robot=0;w.objects[5].at=at;return w;
}
int main(int argc,char** argv) {
    assert(argc==2);const int test=std::atoi(argv[1]);
    auto w=base();AskObservationModel model({{'a',1},{'a',2}},.6,.3,.1,0);
    if(test==0) {
        assert(w.visible()==std::set<unsigned>({1,2}));
        w.hand=4;assert(w.visible().count(4));w.hand=0;w.plate=4;assert(w.visible().count(4));
        w.plate=0;w.objects[2].opened=true;assert(w.visible().count(3));
        w.objects[2].opened=false;w.objects[3].at=1;assert(w.visible().count(3));
    } else if(test==1) {
        w.hand=4;assert(!act(w,JointActionKind::OPEN,2).observation.success);
        w.hand=0;auto next=act(w,JointActionKind::OPEN,2);assert(next.observation.success && next.world.objects[2].opened);
        assert(!act(next.world,JointActionKind::OPEN,2).observation.success);
        assert(act(next.world,JointActionKind::CLOSE,2).observation.success);
    } else if(test==2) {
        w.objects[2].opened=true;assert(!act(w,JointActionKind::PICKUP,3).observation.success);
        auto next=act(w,JointActionKind::TAKEOUT,3,2);assert(next.observation.success);
        assert(next.world.hand==3 && next.world.objects[3].inside==0 && next.world.atLocation(3,1));
        auto moved=act(next.world,JointActionKind::MOVE,2);assert(moved.world.atLocation(3,2));
    } else if(test==3) {
        w.hand=3;w.objects[3].inside=0;auto next=act(w,JointActionKind::TOPLATE,3);
        assert(next.observation.success && next.world.plate==3 && next.world.hand==0);
        assert(!act(next.world,JointActionKind::PICKUP,3).observation.success);
        auto back=act(next.world,JointActionKind::FROMPLATE,3);assert(back.world.hand==3 && back.world.plate==0);
        assert(act(back.world,JointActionKind::PUTDOWN,3).world.hand==0);
    } else if(test==4) {
        auto next=act(w,JointActionKind::MOVE,1);assert(!next.observation.success && next.world.robot==1);
        assert(JointAction(JointActionKind::MOVE,1).cost()==4);
        assert(!act(w,JointActionKind::MOVE,99).observation.success);
        assert(!act(w,JointActionKind::PUTDOWN,3).observation.success);
    } else if(test==5) {
        w.objects[3].at=1;auto next=act(w,JointActionKind::PICKUP,3);
        assert(next.observation.success && next.world.objects[3].inside==2);
        assert(next.world.truthfulReplies(3).size()==2);
    } else if(test==6) {
        w.hand=2;bool failed=false;try{w.validate();}catch(const std::invalid_argument&){failed=true;}assert(failed);
        bool bad=false;try{JointBelief b({{base(),-1}});}catch(const std::invalid_argument&){bad=true;}assert(bad);
    } else if(test==7) {
        auto opened=w;opened.objects[2].opened=true;
        JointBelief belief({{w,.5},{opened,.5}});
        JointObservation o;o.kind=JointObservation::Kind::VISIBLE;o.ids={1,2};
        assert(belief.observe({JointActionKind::SENSE},o,model,1));
        assert(belief.support().size()==1 && !belief.support()[0].world.objects.at(2).opened);
        assert(!belief.observe({JointActionKind::SENSE},o,model,1));
        assert(belief.observe({JointActionKind::SENSE},o,model,2));
        assert(close(belief.support()[0].weight,1));
    } else if(test==8) {
        auto occupied=w;occupied.hand=4;auto already_open=w;already_open.objects[2].opened=true;
        JointBelief belief({{w,.2},{occupied,.3},{already_open,.5}});
        JointObservation failed;failed.success=false;
        assert(belief.observe({JointActionKind::OPEN,2},failed,model));
        assert(belief.support().size()==2);
        assert(close(belief.support()[0].weight,.375) && close(belief.support()[1].weight,.625));
        assert(belief.support()[0].world.hand==4); // Failure does not mean merely "door open".
    } else if(test==9) {
        JointBelief belief({{target(1),.5},{target(2),.5}});
        auto branches=belief.branches({JointActionKind::ASK,5},model);double sum=0;
        for(const auto& branch:branches) {
            sum+=branch.probability;
            if(branch.observation.reply==LocationHypothesis('a',1)) {
                assert(close(branch.probability,.45));assert(close(branch.posterior.support()[0].weight,5.0/6));
            }
        }
        assert(close(sum,1));
        JointObservation impossible;impossible.kind=JointObservation::Kind::VISIBLE;impossible.ids={999};
        assert(!belief.observe({JointActionKind::SENSE},impossible,model,2));
        assert(belief.support().size()==2 && close(belief.support()[0].weight,.5));
    } else if(test==10) {
        JointBelief belief({{w,.7}},.3);
        auto plan=JointPolicySearch::solve(belief,{},model,[](const JointWorld&){return 0.;},3,std::chrono::milliseconds(100));
        assert(!plan.support_complete && plan.reason=="residual_support" && plan.policy->stop);
        bool failed=false;try{belief.branches({JointActionKind::SENSE},model);}catch(const std::logic_error&){failed=true;}assert(failed);
    } else if(test==11) {
        w.objects[3].at=1;JointBelief belief({{w,1}});
        auto p=JointPolicySearch::solve(belief,{{JointActionKind::ASK,3}},model,[](const JointWorld&){return 0.;},2,std::chrono::milliseconds(100));
        assert(!p.support_complete && p.reason=="unmodeled_answer_order" && p.policy->stop);
    } else if(test>=12 && test<=15) {
        JointBelief belief({{target(1),.5},{target(2),.5}});
        std::vector<JointAction> actions={{JointActionKind::MOVE,1,0,10},{JointActionKind::MOVE,2,0,10}};
        if(test!=13)actions.emplace_back(JointActionKind::ASK,5,0,10);
        auto value=[](const JointWorld& s){return s.atLocation(5,s.robot)?40.:0.;};
        if(test==14) {auto known=target(1);known.robot=1;belief=JointBelief({{known,1}});}
        auto p=JointPolicySearch::solve(belief,actions,model,value,2,
            std::chrono::milliseconds(test==15?0:100),4096,std::chrono::milliseconds(1000));
        assert(p.search_complete && p.support_complete);
        if(test==12) {
            assert(!p.policy->stop && p.policy->action.kind==JointActionKind::ASK && close(p.value,26));
            for(const auto& child:p.policy->children)if(child.first.reply.first=='a')
                assert(child.second->action.a==unsigned(child.first.reply.second));
        }
        if(test==13)assert(close(p.value,16)); // An oracle would claim 36 by choosing per true world.
        if(test==14)assert(p.policy->stop && close(p.value,40)); // Confirmation is not a new goal.
        if(test==15)assert(p.policy->stop && close(p.value,0));
    } else if(test==16) {
        auto a=w,b=w;a.objects[3]={true,false,1};a.objects[5].at=2;
        b.objects[3]={true,false,2};b.objects[5].at=1;
        JointBelief belief({{a,.5},{b,.5}});
        auto value=[](const JointWorld& s){return !s.hand && !s.plate && s.objects.at(3).at==s.objects.at(5).at?40.:0.;};
        std::vector<JointAction> actions={{JointActionKind::SENSE,0,0,1},{JointActionKind::PICKUP,3,0,1},
            {JointActionKind::MOVE,1,0,1},{JointActionKind::MOVE,2,0,1},{JointActionKind::PUTDOWN,3,0,1}};
        auto p=JointPolicySearch::solve(belief,actions,model,value,5,std::chrono::milliseconds(100),100000,std::chrono::milliseconds(2000));
        assert(p.support_complete && p.search_complete && p.value>=29-1e-8 && p.value<=30+1e-8);
    } else if(test==17) {
        JointBelief belief({{target(1),.5},{target(2),.5}});
        auto p=JointPolicySearch::solve(belief,{{JointActionKind::MOVE,1}},model,
            [](const JointWorld& s){return s.atLocation(5,s.robot)?40.:0.;},8,std::chrono::milliseconds(100),0);
        assert(!p.search_complete && p.policy->stop && close(p.value,0));
    } else if(test==18) {
        JointBelief belief({{w,1}});auto value=[](const JointWorld&){return 0.;};
        bool bad=false;
        try{JointPolicySearch::solve(belief,{},model,value,33,std::chrono::milliseconds(100));}
        catch(const std::invalid_argument&){bad=true;}assert(bad);
        bad=false;try{JointPolicySearch::solve(belief,{{JointActionKind::SENSE,0,0,-2}},model,value,1,std::chrono::milliseconds(100));}
        catch(const std::invalid_argument&){bad=true;}assert(bad);
        bad=false;w.locations.insert(-1);try{w.validate();}catch(const std::invalid_argument&){bad=true;}assert(bad);
    } else if(test==19) {
        JointBelief belief({{w,.2},{w,.3}},.5);assert(close(belief.residualMass(),.5));
        bool bad=false;try{JointBelief empty({});}catch(const std::invalid_argument&){bad=true;}assert(bad);
        bad=false;try{act(base(),static_cast<JointActionKind>(100));}catch(const std::invalid_argument&){bad=true;}assert(bad);
    } else if(test==20) {
        auto weighted=model.reweighted({{{'a',1},4},{{'a',2},1},{{'i',2},1}},0);
        assert(close(weighted.likelihood({'a',1},{'a',1}),.8));
        assert(close(weighted.likelihood({'a',1},{'a',2}),.2));
        for(auto truth:std::set<LocationHypothesis>{{'a',1},{'a',2},{'?',-1}}) {
            double sum=0;for(auto reply:weighted.observations())sum+=weighted.likelihood(reply,truth);assert(close(sum,1));
        }
    } else if(test==21) {
        auto weighted=model.reweighted({{{'a',1},4},{{'a',2},1}},.2);
        const auto before=weighted.randomDistribution();
        assert(weighted.withReply({'a',1}).randomDistribution()==before);
        auto expanded=weighted.withReply({'a',3});
        assert(close(expanded.randomDistribution().at({'a',1}),before.at({'a',1})));
        assert(close(expanded.randomDistribution().at({'a',3}),.1));
        assert(close(expanded.randomDistribution().at({'*',-2}),.1));
        bool bad=false;try{model.reweighted({{{'a',1},-1}},.1);}catch(const std::invalid_argument&){bad=true;}assert(bad);
    } else if(test==22) {
        auto left=target(1),right=target(2);left.freezeSdkReplyDomain();right.freezeSdkReplyDomain();
        auto frozen=left.initial_reply_counts;auto moved=act(left,JointActionKind::MOVE,1).world;
        assert(moved.initial_reply_counts==frozen);
        JointBelief belief({{left,.5},{right,.5}});
        for(const auto& branch:belief.branches({JointActionKind::ASK,5},model))
            if(branch.observation.reply==LocationHypothesis('a',1)) {
                assert(close(branch.probability,.425));assert(close(branch.posterior.support()[0].weight,15.0/17));
            }
    } else assert(false);
}
