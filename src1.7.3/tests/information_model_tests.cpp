#include "rdfw.hpp"
#include <cassert>
#include <cmath>
#include <cstdlib>
using namespace _home;
namespace _home { struct InformationModelTestAccess {
    static CandidatePlan project(RDFW& w,unsigned id,LocationHypothesis h,std::size_t task) {return w.ProjectVerification(id,h,task);}
    static void evaluate(RDFW& w,ProbeCandidate& p) {w.EvaluateAskBranches(p);}
    static LocationBelief& belief(RDFW& w,unsigned id) {return w.BeliefFor(id);}
    static void ask(RDFW& w,unsigned id) {auto saved=w.task_index;w.task_index=-1;w.AskLoc(id);w.task_index=saved;}
    static void sense(RDFW& w) {w.SenseCurrentLocationOnly(true);}
    static void spent(RDFW& w,int cost) {w.probe_cost_spent=cost;}
}; }
using A=InformationModelTestAccess;
static bool close(double a,double b) {return std::abs(a-b)<1e-9;}
int main(int argc,char** argv) {
    assert(argc==3);const int test=std::atoi(argv[2]);
    AskObservationModel model({{'a',1},{'a',2}},.6,.3,.1,0);
    LocationBelief belief;belief.initialize({{'a',1},{'a',2}},{'?',-1});
    if(test==0) {
        for(auto world:std::set<LocationHypothesis>{{'a',1},{'a',2},{'?',-1}}) {
            double sum=0;for(auto o:model.observations())sum+=model.likelihood(o,world);
            assert(close(sum,1));
        }
        assert(close(model.likelihood({'a',1},{'a',1}),.75));
        assert(close(model.likelihood({'a',1},{'a',2}),.15));return 0;
    }
    if(test==1) {
        double sum=0;for(auto o:model.observations())sum+=belief.observationProbability(o,model);assert(close(sum,1));
        auto next=belief.posterior({'a',1},model);
        assert(close(next.probability({'a',1}),5.0/7));
        assert(close(next.probability({'a',2}),1.0/7));
        assert(close(next.probability({'?',-1}),1.0/7));
        assert(belief.posterior({'?',-1},model).distribution()==belief.distribution());return 0;
    }
    if(test==2) {
        assert(belief.observe({'a',1},model,11));auto first=belief.distribution();
        assert(!belief.observe({'a',1},model,11) && belief.distribution()==first);
        assert(belief.observe({'a',1},model,12) && belief.probability({'a',1})>first.at({'a',1}));return 0;
    }
    VerificationRoute a;a.hypothesis={'a',1};a.success_value=40;a.failure_value=-5;a.worst_duration=std::chrono::milliseconds(400);a.feasible=true;
    auto b=a;b.hypothesis={'a',2};
    if(test==3) {
        auto value=InformationPlanner::ask(belief,model,{a,b},2,std::chrono::milliseconds(1000));
        double p=0;for(auto branch:value.branches)p+=branch.probability;assert(close(p,1));
        // Independently enumerate joint P(world,reply); one route per reply, no oracle.
        double total=0;
        for(auto branch:value.branches) for(auto world:belief.distribution())
            total+=world.second*model.likelihood(branch.observation,world.first)*
                (branch.selected_route.first=='?'?0:world.first==branch.selected_route?40:-5);
        assert(close(total,value.after_answer_value));assert(close(value.direct_value,10));
        assert(value.net_value>0 && value.after_answer_value<40);return 0;
    }
    if(test==4) {
        belief.confirm({'a',1});auto value=InformationPlanner::ask(belief,model,{a,b},2,std::chrono::milliseconds(1000));
        assert(close(value.net_value,-2));return 0; // known world: asking cannot improve the route
    }
    if(test==5) {
        auto value=InformationPlanner::ask(belief,model,{a,b},2,std::chrono::milliseconds(450),std::chrono::milliseconds(100));
        assert(close(value.after_answer_value,0) && close(value.net_value,-12));return 0;
    }
    if(test==6) {
        AskObservationModel no_information({{'a',1},{'a',2}},0,.9,.1,0);
        auto value=InformationPlanner::ask(belief,no_information,{a,b},2,std::chrono::milliseconds(1000));
        assert(close(value.net_value,-2));return 0;
    }
    if(test==12) {
        a.requires_new_answer=true;b.requires_new_answer=true;
        auto value=InformationPlanner::ask(belief,model,{a,b},2,std::chrono::milliseconds(1000));
        assert(close(value.direct_value,0));
        for(auto branch:value.branches) if(branch.observation.first=='?' || branch.observation.first=='*')
            assert(branch.selected_route.first=='?' && close(branch.value,0));
        assert(value.net_value>0);return 0;
    }
    if(test==14) {
        LocationBelief big;big.initialize({{'a',1}},{'?',-1});
        AskObservationModel noisy({{'a',1},{'i',2}},.6,.3,.1,0);
        a.requires_new_answer=true;
        auto value=InformationPlanner::ask(big,noisy,{a},2,std::chrono::milliseconds(1000));
        for(auto branch:value.branches) if(branch.observation.first=='i')
            assert(branch.selected_route.first=='?' && close(branch.value,0));
        return 0;
    }
    if(test>=19 && test<=22) {
        LocationBelief v;v.initialize({{'a',1},{'a',2},{'i',7}},{'?',-1});
        std::map<int,std::pair<int,int>> containers{{7,{1,test==19?0:test==20?1:-1}}};
        assert(v.filterVisibility(1,test==22,containers));
        assert(close(v.probability({'a',test==22?2:1}),0));
        if(test==20) assert(close(v.probability({'i',7}),0));
        else assert(v.probability({'i',7})>0);
        auto after=v.distribution();assert(!v.filterVisibility(1,test==22,containers));
        assert(after==v.distribution());return 0;
    }
    auto owner=std::make_shared<RDFW>();auto& w=*owner;char name[]="info",option[]="-path";char* args[]={name,option,argv[1]};w.Init(3,args);w.stage=2;
    assert(w.ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 2) (closed 2) "
        "(sort 3 book) (size 3 small) (at 3 2) (sort 4 table) (size 4 big) (at 4 4)"));
    assert(w.ParseInstruction("(:task (pickup X) (:cond (id X 3)))"));w.Cons_plan();
    if(test==29 || test==30) {
        ProbeCandidate p;p.kind=ProbeKind::ASK_LOCATION;p.target_object=3;p.task_indices={0};
        p.action_cost=2;p.estimated_duration=std::chrono::milliseconds(100);p.potential_goal_value=40;p.eligible=true;
        if(test==29) {
            A::evaluate(w,p);bool feasible=false;for(const auto& route:p.verification_routes) feasible|=route.feasible;
            assert(feasible);p.verification_routes.clear();p.eligible=true;
        }
        A::spent(w,30);auto state=w.DebugStateSnapshot();A::evaluate(w,p);
        for(const auto& route:p.verification_routes) assert(!route.feasible);
        assert(!p.eligible && p.expected_gain<=0 && w.DebugStateSnapshot()==state && w.TestPlatformCalls()==0);
        assert(p.answer_cache_hit==(test==29));return 0;
    }
    if(test>=25 && test<=28) {
        w.tasks.clear();assert(w.ParseInstruction("(:task (puton X Y) (:cond (id X 3) (id Y 4)))"));
        w.tasks.assign(30,w.tasks.front());
        for(auto& task:w.tasks) task.risk=2; // large-question binding gate, as in c019/c020/c021
        if(test!=26) {
            w.ApplyStateValue(StateField::LOCATION,3,2,true,EvidenceSource::ACTION_SUCCESS);
            if(test!=28) w.ApplyStateValue(StateField::INSIDE,3,NONE,true,EvidenceSource::ACTION_SUCCESS);
        }
        auto state=w.DebugStateSnapshot();auto plan=test==27?w.PreviewTaskGroupPlan({0}):A::project(w,4,{'a',4},0);
        assert(w.TestPlatformCalls()==0 && state==w.DebugStateSnapshot());
        if(test==25) {
            assert(plan.dry_run_succeeded && plan.eligible);
            assert(w.FactLocation(4)==UNKNOWN); // scenario eligibility is not real action authorization
            ProbeCandidate p;p.kind=ProbeKind::ASK_LOCATION;p.target_object=4;p.task_indices={0};
            p.action_cost=2;p.estimated_duration=std::chrono::milliseconds(100);p.potential_goal_value=1200;p.eligible=true;
            A::evaluate(w,p);bool found=false;
            for(const auto& route:p.verification_routes) found|=route.hypothesis==LocationHypothesis{'a',4} && route.feasible;
            assert(found);
        } else assert(!plan.eligible); // other unknown inputs or real execution retain their gate
        assert(w.TestPlatformCalls()==0 && state==w.DebugStateSnapshot());return 0;
    }
    if(test>=15 && test<=18) {
        w.ApplyStateValue(StateField::LOCATION,2,1,true,EvidenceSource::SENSE);
        if(test!=16) w.ApplyStateValue(StateField::CONTAINER_STATE,2,1,true,EvidenceSource::ACTION_SUCCESS);
        w.ApplyStateValue(StateField::LOCATION,3,1,false,EvidenceSource::INITIAL);
        w.ApplyStateValue(StateField::INSIDE,3,NONE,test>=17,
            test>=17?EvidenceSource::ACTION_SUCCESS:EvidenceSource::INITIAL);
        if(test==18) w.ApplyStateValue(StateField::INSIDE,3,2,true,EvidenceSource::ACTION_SUCCESS);
        w.SetSenseResult({2,3});A::sense(w);
        assert(w.FactLocation(3)==1 && w.TestPlatformCalls()==1);
        if(test<=16) {
            assert(w.FactInside(3)==UNKNOWN && !w.IsInsideVerified(3));
            auto dist=A::belief(w,3).distribution();
            assert(dist.size()>1 && A::belief(w,3).probability({'a',1})<1);
        } else assert(w.FactInside(3)==(test==18?2:NONE) && w.IsInsideVerified(3));
        return 0;
    }
    if(test==7) {
        auto dist=A::belief(w,3).distribution();auto state=w.DebugStateSnapshot();
        auto plan=A::project(w,3,{'a',4},0);
        assert(plan.dry_run_succeeded && plan.marginal_score>0);
        assert(plan.actions.size()==3 && plan.actions[0].name=="Move" && plan.actions[1].name=="Sense" && plan.actions[2].name=="PickUp");
        assert(w.TestPlatformCalls()==0 && w.DebugStateSnapshot()==state && A::belief(w,3).distribution()==dist);
        assert(w.FactLocation(3)==UNKNOWN && w.FactInside(3)==UNKNOWN);return 0;
    }
    if(test==8) {
        w.ApplyStateValue(StateField::LOCATION,2,2,true,EvidenceSource::SENSE);
        w.ApplyStateValue(StateField::CONTAINER_STATE,2,0,true,EvidenceSource::SENSE);w.SetHold(nullptr);w.SetPlate(nullptr);
        auto state=w.DebugStateSnapshot();auto plan=A::project(w,3,{'i',2},0);
        assert(plan.dry_run_succeeded && plan.marginal_score>0);
        assert(plan.actions.size()==4 && plan.actions[1].name=="Open" && plan.actions[2].name=="Sense" && plan.actions[3].name=="TakeOut");
        assert(w.TestPlatformCalls()==0 && w.DebugStateSnapshot()==state && w.FactInside(3)==UNKNOWN);return 0;
    }
    if(test==9) {
        auto state=w.DebugStateSnapshot();auto plan=A::project(w,3,{'i',2},0);
        assert(!plan.dry_run_succeeded && w.DebugStateSnapshot()==state && w.TestPlatformCalls()==0);return 0;
    }
    if(test==10) {
        A::belief(w,3).answer({'a',4});w.ApplyStateValue(StateField::LOCATION,3,1,true,EvidenceSource::ACTION_SUCCESS);
        w.ApplyStateValue(StateField::INSIDE,3,0,true,EvidenceSource::ACTION_SUCCESS);
        assert(close(A::belief(w,3).probability({'a',1}),1));return 0;
    }
    if(test==11) {
        ProbeCandidate p;p.kind=ProbeKind::ASK_LOCATION;p.target_object=3;p.task_indices={0};
        p.action_cost=2;p.estimated_duration=std::chrono::milliseconds(100);p.potential_goal_value=40;p.eligible=true;
        auto state=w.DebugStateSnapshot();A::evaluate(w,p);
        assert(p.answer_branches_evaluated && !p.verification_routes.empty());
        for(const auto& route:p.verification_routes) assert(route.failure_value<=0 && route.success_value<=40);
        assert(std::isfinite(p.expected_gain) && p.expected_gain<=38 && w.TestPlatformCalls()==0 && w.DebugStateSnapshot()==state);
        double sum=0;for(auto branch:p.answer_value.branches)sum+=branch.probability;
        assert(close(sum,1));return 0;
    }
    if(test==13) {
        ProbeCandidate p;p.kind=ProbeKind::ASK_LOCATION;p.target_object=3;p.task_indices={0};
        p.action_cost=2;p.estimated_duration=std::chrono::milliseconds(100);p.potential_goal_value=40;p.eligible=true;
        A::evaluate(w,p);assert(!p.answer_cache_hit);
        auto next=p;next.verification_routes.clear();A::evaluate(w,next);
        assert(next.answer_cache_hit && next.verification_routes.size()==p.verification_routes.size());
        assert(close(next.expected_gain,p.expected_gain));
        w.SetAskResult("not_known");A::ask(w,3);
        auto unknown=p;unknown.verification_routes.clear();A::evaluate(w,unknown);
        assert(unknown.answer_cache_hit && close(unknown.expected_gain,p.expected_gain));
        w.ApplyStateValue(StateField::LOCATION,3,1,true,EvidenceSource::SENSE);
        w.ApplyStateValue(StateField::INSIDE,3,0,true,EvidenceSource::SENSE);
        auto changed=p;changed.verification_routes.clear();A::evaluate(w,changed);
        assert(!changed.answer_cache_hit && changed.expected_gain<=0);return 0;
    }
    if(test==23 || test==24) {
        w.ApplyStateValue(StateField::LOCATION,2,1,true,EvidenceSource::SENSE);
        w.ApplyStateValue(StateField::CONTAINER_STATE,2,test==23?0:1,true,EvidenceSource::ACTION_SUCCESS);
        auto& prior=A::belief(w,3);assert(prior.probability({'a',1})>0 && prior.probability({'i',2})>0);
        w.SetSenseResult({2});A::sense(w);
        auto& after=A::belief(w,3);assert(close(after.probability({'a',1}),0));
        if(test==23) assert(after.probability({'i',2})>0);
        else assert(close(after.probability({'i',2}),0));
        assert(w.TestPlatformCalls()==1 && w.FactInside(3)==UNKNOWN);return 0;
    }
    assert(false);
}
