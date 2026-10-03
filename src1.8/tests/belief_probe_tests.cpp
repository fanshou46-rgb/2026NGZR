#include "rdfw.hpp"
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <condition_variable>
#include <thread>
using namespace _home;
namespace _home { struct BeliefProbeTestAccess {
    static std::vector<ProbeCandidate> probes(RDFW& w) {return w.GenerateProbeCandidates(w.EvaluateShadowCandidates("test",true,-1));}
    static void execute(RDFW& w,const ProbeCandidate& p) {w.ExecuteProbe(p);}
    static bool answer(RDFW& w,unsigned id,const std::string& s) {return w.AcceptProbeAnswer(id,s);}
    static LocationBelief& belief(RDFW& w,unsigned id) {return w.BeliefFor(id);}
    static void budget(RDFW& w,int ms) {w.deadline_manager=DeadlineManager(std::chrono::milliseconds(ms));}
    static void cost(RDFW& w,int value) {w.probe_cost_spent=value;}
    static void qualify(RDFW& w,ProbeCandidate& p) {w.QualifyProbe(p);}
    static std::size_t attempts(RDFW& w) {return w.task_attempts[0];}
    static bool shutdown(RDFW& w) {return w.planner_shutdown_requested.load();}
}; }
using A=BeliefProbeTestAccess;
static ProbeCandidate find(RDFW& w,ProbeKind kind,unsigned object=3) {
    for(auto p:A::probes(w)) if(p.kind==kind && (kind!=ProbeKind::ASK_LOCATION || p.target_object==object)) return p;
    assert(false); return {};
}
int main(int argc,char** argv) {
    assert(argc==3); const int test=std::atoi(argv[2]);
    LocationBelief b; b.initialize({{'a',1},{'a',2},{'i',2}},{'a',1});
    if(test==0) {
        const auto before=b.distribution(); assert(!b.answer({'?',-1})); assert(b.distribution()==before);
        assert(b.answer({'a',2})); const auto once=b.distribution();
        assert(!b.answer({'a',2}) && b.distribution()==once);
        double total=0; for(auto h:once) total+=h.second;
        assert(std::abs(total-1)<1e-9 && b.probability({'a',2})<1 && b.probability({'?',-1})>0);
        return 0;
    }
    auto owner=std::make_shared<RDFW>(); RDFW& w=*owner; char n[]="belief",option[]="-path"; char* args[]={n,option,argv[1]};w.Init(3,args);w.stage=2;
    assert(w.ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 2) (closed 2) "
        "(sort 3 book) (size 3 small) (at 3 2) (sort 4 table) (size 4 big) (at 4 4) "
        "(sort 5 cup) (size 5 small) (at 5 4)"));
    assert(w.ParseInstruction("(:task (pickup X) (:cond (sort X book) (id X 3)))")); w.Cons_plan();
    if(test==1 || test==2 || test==3) {
        if(test==2) {w.ApplyStateValue(StateField::LOCATION,3,2,true,EvidenceSource::SENSE);w.ApplyStateValue(StateField::INSIDE,3,0,true,EvidenceSource::SENSE); assert(!A::answer(w,3,"at(3,4)")); assert(w.FactLocation(3)==2 && w.FactInside(3)==0); return 0;}
        auto p=find(w,ProbeKind::ASK_LOCATION); w.SetAskResult(test==3?"not_known":"at(3,4)");
        const auto before=w.DebugStateSnapshot(); A::execute(w,p);
        assert(w.TestPlatformCalls()==1 && w.ProbeFeedback().size()==1);
        if(test==2) assert(w.FactLocation(3)==2 && w.FactInside(3)==0);
        else assert(w.FactLocation(3)==UNKNOWN && w.FactInside(3)==UNKNOWN);
        if(test==3) assert(w.DebugStateSnapshot()==before && !w.ProbeFeedback()[0].related_new_evidence);
        if(test==1) {
            assert(w.objects[3]->location==4 && A::belief(w,3).probability({'a',4})>0);
            auto again=find(w,ProbeKind::ASK_LOCATION); assert(!again.eligible && again.rejection=="answer_requires_verification");
            auto distribution=A::belief(w,3).distribution(); auto canonical=w.DebugStateSnapshot();
            w.PreviewGreedyContinuation(0,false);
            assert(A::belief(w,3).distribution()==distribution && w.DebugStateSnapshot()==canonical && w.TestPlatformCalls()==1);
        }
    } else if(test>=4 && test<=7) {
        w.SetHold(nullptr); w.SetPlate(nullptr);
        w.ApplyStateValue(StateField::LOCATION,2,2,true,EvidenceSource::SENSE);
        w.ApplyStateValue(StateField::CONTAINER_STATE,2,0,true,EvidenceSource::SENSE);
        assert(A::answer(w,3,"inside(3,2)")); assert(w.FactInside(3)==UNKNOWN);
        if(test==5) {
            Instruction c; c.behave="closed";c.X={w.objects[2]};w.notnot_infoConstrains.push_back(c);
        }
        auto p=find(w,ProbeKind::OPEN_AND_SENSE);
        if(test==5) {assert(!p.eligible);return 0;}
        assert(p.eligible && p.actions.size()==3);
        w.SetSenseResult({2,3});
        if(test==6) w.SetActionResults({true,false});
        if(test==7) w.SetActionCallback([&](){A::budget(w,399);});
        A::execute(w,p);
        if(test==4) {assert(w.TestPlatformCalls()==3 && w.FactContainerState(2)==1 && w.FactLocation(3)==2); assert(w.FactInside(3)==UNKNOWN);}
        if(test==6) {assert(w.TestPlatformCalls()==2 && !w.ProbeFeedback()[0].sense_attempted && w.FactContainerState(2)==0);}
        if(test==7) assert(w.TestPlatformCalls()==1 && !w.ProbeFeedback()[0].sense_attempted);
    } else if(test==8) {
        auto p=find(w,ProbeKind::ASK_LOCATION);A::cost(w,31);A::qualify(w,p);
        assert(!p.eligible && p.rejection=="probe_cost_bound");A::execute(w,p);assert(w.TestPlatformCalls()==0);
    } else if(test==9) {
        A::budget(w,350);auto p=find(w,ProbeKind::ASK_LOCATION);assert(!p.eligible && p.rejection=="continuation_deadline");
        A::execute(w,p);assert(w.TestPlatformCalls()==0);
    } else if(test==10) {
        w.ApplyStateValue(StateField::LOCATION,3,1,true,EvidenceSource::SENSE);
        w.ApplyStateValue(StateField::INSIDE,3,0,true,EvidenceSource::SENSE);
        w.ExecuteMainTaskLoop(false);assert(w.GetTerminalSummary().allGoalsSatisfied());
        assert(A::attempts(w)==0);
    } else if(test==11) {
        w.tasks[0].risk=2;
        auto unknown=w.PreviewTaskGroupPlan({0}); assert(!unknown.eligible);
        w.ApplyStateValue(StateField::LOCATION,3,1,true,EvidenceSource::SENSE);
        w.ApplyStateValue(StateField::INSIDE,3,0,true,EvidenceSource::SENSE);
        auto known=w.PreviewTaskGroupPlan({0}); assert(known.eligible && known.dry_run_succeeded);
    } else if(test==12) {
        w.ApplyStateValue(StateField::LOCATION,3,1,true,EvidenceSource::SENSE);
        w.ApplyStateValue(StateField::INSIDE,3,0,true,EvidenceSource::SENSE);
        w.SetHold(std::dynamic_pointer_cast<SmallObject>(w.objects[3]));
        assert(w.ParseInstruction("(:task (puton X Y) (:cond (id X 3) (id Y 4)))"));
        const auto ps=A::probes(w); assert(!ps.empty());
        for(const auto& p:ps) assert(p.kind!=ProbeKind::ASK_LOCATION);
    } else if(test==13) {
        w.SetAskResult("not_known");
        const auto state=w.DebugStateSnapshot();
        for(int i=0;i<3;++i) {
            auto p=find(w,ProbeKind::ASK_LOCATION); assert(p.eligible); A::execute(w,p);
        }
        auto p=find(w,ProbeKind::ASK_LOCATION); assert(!p.eligible && p.rejection=="same_probe_bound");
        assert(w.TestPlatformCalls()==3 && w.ProbeFeedback().size()==3 && w.DebugStateSnapshot()==state);
    } else if(test==14 || test==15) {
        w.SetHold(nullptr);w.SetPlate(nullptr);
        w.ApplyStateValue(StateField::LOCATION,2,2,true,EvidenceSource::SENSE);
        const auto task=w.tasks[0];w.tasks.assign(5,task);
        Instruction c;c.behave="goto";c.X={w.objects[2]};
        w.not_taskConstrains.assign(test==14?1:3,c);
        bool found=false;
        for(const auto& p:A::probes(w)) if(p.kind==ProbeKind::MOVE_AND_SENSE && p.target_location==2) {
            found=true;
            if(test==14) assert(p.eligible && p.constraint_result=="bounded_score_trade" && p.constraint_risks.size()==1 && p.expected_gain>0);
            else assert(!p.eligible && p.constraint_risks.size()==3);
        }
        assert(found && w.TestPlatformCalls()==0);
    } else if(test==16) {
        assert(w.ParseInstruction("(:task (pickup X) (:cond (id X 5)))")); w.Cons_plan();
        A::belief(w,5).answer({'a',4});
        const auto ps=A::probes(w);std::size_t first=ps.size(),second=ps.size();
        for(std::size_t i=0;i<ps.size();++i) if(ps[i].kind==ProbeKind::MOVE_AND_SENSE) {
            if(ps[i].target_location==2) first=i;
            if(ps[i].target_location==4) second=i;
        }
        assert(first<second && second<ps.size());
        assert(ps[second].expected_gain>ps[first].expected_gain);
        assert(w.TestPlatformCalls()==0);
    } else if(test==17) {
        auto live_owner=std::make_shared<RDFW>(); RDFW& live=*live_owner;
        live.Init(3,args);live.stage=1;
        live.SetTestInput("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
            "(sort 2 book) (size 2 small) (at 2 2) (sort 3 table) (size 3 big) (at 3 3)",
            "(:task (puton X Y) (:cond (id X 2) (id Y 3)))");
        std::mutex gate;std::condition_variable event;bool in_call=false,release=false;
        live.SetActionCallback([&](){std::unique_lock<std::mutex> lock(gate);in_call=true;event.notify_all();event.wait(lock,[&](){return release;});});
        std::thread planner([&](){live.Plan();});
        {std::unique_lock<std::mutex> lock(gate);assert(event.wait_for(lock,std::chrono::seconds(3),[&](){return in_call;}));}
        std::thread cleanup([&](){live.Fini();});
        const auto end=std::chrono::steady_clock::now()+std::chrono::seconds(2);
        while(!A::shutdown(live) && std::chrono::steady_clock::now()<end) std::this_thread::yield();
        assert(A::shutdown(live) && !live.objects.empty() && !live.tasks.empty());
        {std::lock_guard<std::mutex> lock(gate);release=true;}event.notify_all();
        planner.join();cleanup.join();
        assert(live.objects.size()==1 && live.objects[0].get()==static_cast<Object*>(&live) && live.tasks.empty() && live.TestPlatformCalls()==1);
        live.SetActionCallback({}); live.Plan();assert(live.TestPlatformCalls()>1); live.Fini();
    } else assert(false);
}
