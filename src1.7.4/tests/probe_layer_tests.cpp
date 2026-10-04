#include "rdfw.hpp"
#include <cassert>
#include <cstdlib>
#include <memory>
using namespace _home;
namespace _home { struct ProbeLayerTestAccess {
    static std::vector<CandidatePlan> Tasks(RDFW& w) { return w.EvaluateShadowCandidates("unit",true,static_cast<std::size_t>(-1)); }
    static bool HasBest(RDFW& w,const std::vector<CandidatePlan>& tasks) { return w.SelectGreedyCandidate(tasks)!=nullptr; }
    static std::vector<ProbeCandidate> Probes(RDFW& w) { return w.GenerateProbeCandidates(Tasks(w)); }
    static void Qualify(RDFW& w,ProbeCandidate& p) { w.QualifyProbe(p); }
    static void Execute(RDFW& w,const ProbeCandidate& p) { w.ExecuteProbe(p); }
    static void Replan(RDFW& w) { auto c=Tasks(w); w.FinalizeProbeReplan(c,w.SelectGreedyCandidate(c)); }
    static void NoTaskReplan(RDFW& w) { w.FinalizeProbeReplan({},nullptr); }
    static void Budget(RDFW& w,int ms) { w.deadline_manager=DeadlineManager(std::chrono::milliseconds(ms)); }
    static ProbeHistory& History(RDFW& w,const std::string& key) { return w.probe_history[key]; }
    static void Revise(RDFW& w) { ++w.world_revision; }
    static void Invalidate(RDFW& w,int loc) { w.InvalidateSenseAtLocation(loc); }
    static std::size_t Steps(RDFW& w) { return w.scheduler_steps; }
    static std::string Closed(RDFW& w) { return w.probe_closed_reason; }
    static void Close(RDFW& w) { w.probe_closed_reason="total_probe_bound"; }
    static void Shadow(RDFW& w,bool value) { w.shadow_dry_run=value; }
    static void FailTask(RDFW& w,std::size_t id) {
        w.failed_task_revision.assign(w.tasks.size(),RDFW::NO_FAILED_REVISION);
        w.failed_task_revision[id]=w.world_revision; w.task_attempts.assign(w.tasks.size(),0);
    }
    static ProbeCandidate Manual(RDFW& w,int loc,unsigned id=3) {
        ProbeCandidate p; p.target_location=loc; p.signature="sense_at:"+std::to_string(loc);
        p.world_revision=w.world_revision; p.state_before=w.PlanStateSignature();
        BlockingFact f; f.object_id=id; f.field=StateField::LOCATION; f.location_hints[loc]="fixture_specific_hint"; p.facts.push_back(f); p.task_indices={0};
        p.kind=loc==w.FactLocation(0)?ProbeKind::SENSE_CURRENT_LOCATION_ONLY:ProbeKind::MOVE_AND_SENSE;
        if (p.kind==ProbeKind::MOVE_AND_SENSE) p.actions.emplace_back("Move",std::vector<unsigned>{unsigned(loc)},ActionCategory::MOVE);
        p.actions.emplace_back("Sense",std::vector<unsigned>(),ActionCategory::OBSERVATION);
        for (const auto& a:p.actions) {p.action_cost+=a.cost;p.estimated_duration+=a.estimated_duration;}
        p.fact_context=w.ProbeFactContext(p); w.QualifyProbe(p); return p;
    }
}; }
using A=ProbeLayerTestAccess;
const char* env="(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
    "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 2) (closed 2) "
    "(sort 3 book) (size 3 small) (at 3 2) (sort 4 book) (size 4 small) (at 4 4)";
std::shared_ptr<RDFW> world(const char* words,int stage=2) {
    auto w=std::make_shared<RDFW>(); char n[]="probe",p[]="-path"; char* args[]={n,p,const_cast<char*>(words)};
    w->Init(3,args); w->stage=stage; assert(w->ParseEnv(env));
    assert(w->ParseInstruction("(:task (pickup X) (:cond (sort X book) (id X 3)))"));
    w->Cons_plan(); return w;
}
Instruction unary(const char* verb,std::shared_ptr<Object> x) { Instruction t; t.behave=verb; t.X={x}; return t; }
ProbeCandidate at(RDFW& w,int loc) { auto ps=A::Probes(w); for (auto p:ps) if (p.target_location==loc) return p; assert(false); return {}; }
void reliable(RDFW& w,unsigned id,int loc,int inside=0) {
    w.ApplyStateValue(StateField::LOCATION,id,loc,true,EvidenceSource::SENSE);
    if (dynamic_cast<SmallObject*>(w.objects[id].get())) w.ApplyStateValue(StateField::INSIDE,id,inside,true,EvidenceSource::SENSE);
}
int main(int argc,char** argv) {
    assert(argc==3); int test=std::atoi(argv[2]); auto w=world(argv[1]);
    if (test==0 || test==29) {
        reliable(*w,3,1); w->SetHold(nullptr); w->SetPlate(nullptr);
        if (test==29) A::Close(*w);
        w->ExecuteMainTaskLoop(false); assert(w->ProbeFeedback().empty()); assert(w->TestPlatformCalls()==1);
    } else if (test==1) {
        w=world(argv[1],1); w->ExecuteMainTaskLoop(false); assert(w->ProbeFeedback().empty());
    } else if (test==2 || test==28) {
        if (test==28) { auto p=at(*w,2); w->SetSenseResult({2,3}); A::Execute(*w,p); }
        const auto state=w->DebugStateSnapshot(); auto count=w->ProbeFeedback().size(); auto calls=w->TestPlatformCalls();
        w->PreviewGreedyContinuation(0,false); assert(w->DebugStateSnapshot()==state); assert(w->ProbeFeedback().size()==count); assert(w->TestPlatformCalls()==calls);
    } else if (test==3 || test==5 || test==22) {
        w->ApplyStateValue(StateField::LOCATION,3,1,false,EvidenceSource::INITIAL); w->SetSenseResult({1,3});
        if (test==22) {
            // First collect real Sense evidence, then the unchanged complete scheduler restores execution.
            auto p=at(*w,1); A::Execute(*w,p); A::Replan(*w);
            assert(!w->ProbeFeedback()[0].restored_tasks.empty());
            w->ExecuteMainTaskLoop(false); assert(!w->ProbeFeedback()[0].completed_tasks.empty());
        }
        else { auto p=at(*w,1); assert(p.kind==ProbeKind::SENSE_CURRENT_LOCATION_ONLY && p.eligible && p.actions.size()==1);
            if (test==5) { A::Execute(*w,p); assert(w->FactLocation(3)==1 && w->FactInside(3)==0); assert(w->ProbeFeedback()[0].related_new_evidence); } }
    } else if (test==4 || test==6 || test==23 || test==24 || test==25) {
        auto before=w->DebugStateSnapshot(); auto p=at(*w,2); assert(p.eligible && p.actions.size()==2 && w->TestPlatformCalls()==0); assert(w->DebugStateSnapshot()==before);
        if (test==6) w->SetActionResults({false});
        if (test==23) w->SetActionCallback([&](){A::Budget(*w,299);});
        if (test==24) w->SetThrowAction(true);
        if (test==25) w->SetThrowSense(true);
        w->SetSenseResult({2,3}); A::Execute(*w,p);
        const auto& r=w->ProbeFeedback()[0];
        if (test==4) assert(w->TestPlatformCalls()==2 && w->FactLocation(3)==2 && r.related_new_evidence);
        if (test==6) assert(w->TestPlatformCalls()==1 && r.move_failed && !r.sense_attempted && w->DebugStateSnapshot()==before);
        if (test==23) assert(w->TestPlatformCalls()==1 && !r.failure.empty() && w->FactLocation(0)==2);
        if (test==24) assert(w->TestPlatformCalls()==1 && !r.failure.empty() && w->FactLocation(0)==UNKNOWN);
        if (test==25) assert(w->TestPlatformCalls()==2 && !r.failure.empty() && w->FactLocation(3)==UNKNOWN);
    } else if (test==7) {
        A::Budget(*w,419); auto p=at(*w,2); assert(!p.eligible && p.rejection=="deadline");
        A::Budget(*w,420); p=at(*w,2); assert(!p.eligible && p.rejection=="continuation_deadline");
        A::Budget(*w,900); p=at(*w,2); assert(p.eligible);
        w->ApplyStateValue(StateField::LOCATION,3,1,false,EvidenceSource::INITIAL); A::Budget(*w,299); p=at(*w,1); assert(!p.eligible && p.rejection=="deadline");
    } else if (test==8) {
        reliable(*w,4,1); w->SetHold(std::dynamic_pointer_cast<SmallObject>(w->objects[4])); w->move_cons[4][2]=1;
        auto p=at(*w,2); assert(!p.eligible && p.rejection=="extra_physical_actions"); assert(w->TestPlatformCalls()==0);
    } else if (test==9 || test==10 || test==11 || test==12 || test==13 || test==27) {
        if (test==9) { reliable(*w,1,1); w->notnot_infoConstrains.push_back(unary("goto",w->objects[1])); }
        if (test==10) w->notnot_infoConstrains.push_back(unary("goto",w->objects[1]));
        if (test==11) w->notnot_infoConstrains.push_back(unary("closed",w->objects[2]));
        if (test==12 || test==13 || test==27) {
            reliable(*w,1,1); reliable(*w,4,1); auto c=unary("near",w->objects[4]); c.Y={w->objects[1]};
            if (test==12) w->SetHold(std::dynamic_pointer_cast<SmallObject>(w->objects[4]));
            else w->ApplyStateValue(StateField::INSIDE,4,UNKNOWN,false,EvidenceSource::UNKNOWN);
            if (test==27) { c.X={w->objects[3]}; c.conditionX.sort="book"; }
            w->notnot_infoConstrains.push_back(c);
        }
        auto p=at(*w,2);
        if (test==11) assert(p.eligible && p.constraint_result=="constraint_safe");
        else assert(!p.eligible && p.constraint_result==(test==9 || test==12?"constraint_known_loss":"constraint_safety_unknown"));
    } else if (test==14) {
        for (int stage:{1,2}) { w->stage=stage; auto state=w->DebugStateSnapshot(); auto tasks=w->tasks; w->MustChooseOne(); assert(w->TestPlatformCalls()==0 && w->DebugStateSnapshot()==state); assert(w->tasks[0].isEnable==tasks[0].isEnable && w->tasks[0].ask_times==tasks[0].ask_times); }
    } else if (test>=15 && test<=18) {
        auto p=at(*w,2); auto& h=A::History(*w,p.signature); h.attempts=1; h.context_after=p.fact_context; h.world_revision=p.world_revision;
        if (test==15) { A::Revise(*w); A::Qualify(*w,p); assert(p.rejection=="duplicate_related_revision"); }
        else { h.context_after="different"; A::Revise(*w);
            if (test==16) { A::Qualify(*w,p); assert(p.rejection=="previous_probe_no_information"); }
            if (test==17) {
                h.related_new_evidence=true;
                for (const auto& f:p.facts) h.fact_contexts_after[{f.field,f.object_id}]="different_fact_context";
                A::Qualify(*w,p); assert(p.eligible);
            }
            if (test==18) { h.attempts=2; h.related_new_evidence=true; A::Qualify(*w,p); assert(p.rejection=="same_probe_bound"); }
        }
    } else if (test==19) {
        for (int loc=1; loc<=8; ++loc) {
            w->ApplyStateValue(StateField::LOCATION,0,loc,true,EvidenceSource::ACTION_SUCCESS);
            w->ApplyStateValue(StateField::LOCATION,3,loc,false,EvidenceSource::INITIAL);
            A::Invalidate(*w,loc); w->SetSenseResult({3}); auto p=A::Manual(*w,loc); assert(p.eligible); A::Execute(*w,p); A::NoTaskReplan(*w);
        }
        assert(w->ProbeFeedback().size()==8 && A::Steps(*w)==0 && A::Closed(*w)=="total_probe_bound");
    } else if (test==20) {
        w->ApplyStateValue(StateField::LOCATION,3,1,false,EvidenceSource::INITIAL); w->SetSenseResult({3});
        auto p=at(*w,1); A::Execute(*w,p); A::NoTaskReplan(*w);
        w->ApplyStateValue(StateField::LOCATION,3,1,false,EvidenceSource::ASK_ANSWER); A::Revise(*w); A::Invalidate(*w,1);
        p=at(*w,1); assert(p.eligible); A::Execute(*w,p); assert(A::Closed(*w).empty());
        auto retry=A::Manual(*w,1); assert(!retry.eligible && retry.rejection=="same_probe_bound");
        auto other=A::Manual(*w,4,4); assert(other.eligible);
    } else if (test==21) {
        // A container hides the absent target: neither empty observation nor robot movement is progress.
        w->ApplyStateValue(StateField::LOCATION,4,5,false,EvidenceSource::INITIAL);
        for (int loc:{1,4}) {
            w->ApplyStateValue(StateField::LOCATION,0,loc,true,EvidenceSource::ACTION_SUCCESS);
            w->SetSenseResult({2}); auto p=A::Manual(*w,loc,4); assert(p.eligible); A::Execute(*w,p); A::NoTaskReplan(*w);
        }
        assert(A::Closed(*w).empty()); for (const auto& r:w->ProbeFeedback()) assert(!r.related_new_evidence);
    } else if (test==26) {
        w->tasks.push_back(unary("pickup",w->objects[4])); w->ApplyStateValue(StateField::LOCATION,4,2,false,EvidenceSource::INITIAL);
        auto p=at(*w,2); assert(p.task_indices.size()==2 && p.potential_goal_value==80);
    } else if (test==30) {
        auto p=at(*w,2); w->stage=1; A::Execute(*w,p); w->stage=2; A::Shadow(*w,true); A::Execute(*w,p); A::Shadow(*w,false);
        assert(w->ProbeFeedback().empty() && w->TestPlatformCalls()==0);
    } else if (test==31) {
        reliable(*w,2,2); w->ApplyStateValue(StateField::CONTAINER_STATE,2,1,true,EvidenceSource::SENSE);
        w->ApplyStateValue(StateField::INSIDE,3,2,false,EvidenceSource::INITIAL);
        auto p=at(*w,2); for (const auto& f:p.facts) assert(f.field!=StateField::INSIDE);
        w->SetSenseResult({2,3}); A::Execute(*w,p); assert(w->FactInside(3)==UNKNOWN);
    } else if (test==32) {
        w->tasks={unary("goto",w->objects[2]),unary("goto",w->objects[4])};
        w->ExecuteMainTaskLoop(true); assert(w->ProbeFeedback().empty() && w->TestPlatformCalls()==0);
    } else if (test==33) {
        w->ApplyStateValue(StateField::LOCATION,3,4,false,EvidenceSource::ASK_ANSWER);
        reliable(*w,3,2,UNKNOWN); const auto ps=A::Probes(*w);
        for (const auto& p:ps) for (const auto& f:p.facts) if (f.object_id==3) {
            assert(f.location_hints.count(4)==0 && f.location_hints.count(2)==1);
        }
    } else if (test==36) {
        reliable(*w,1,1);
        w->tasks={unary("goto",w->objects[1]),unary("goto",w->objects[3]),unary("goto",w->objects[4])};
        const auto candidates=A::Tasks(*w); assert(!A::HasBest(*w,candidates));
        const auto state=w->DebugStateSnapshot();
        const auto tail=w->PreviewGreedyContinuation(0,true);
        assert(tail.eligible && tail.dry_run_succeeded && tail.marginal_score>0);
        assert(w->DebugStateSnapshot()==state && w->TestPlatformCalls()==0);
        w->ExecuteMainTaskLoop(true);
        assert(w->ProbeFeedback().empty() && w->TestPlatformCalls()==0);
    } else if (test==35) {
        auto p=at(*w,2); w->SetSenseResult({2,3}); A::Execute(*w,p); A::NoTaskReplan(*w);
        A::Revise(*w); A::Invalidate(*w,2);
        // A different blocked object or a smaller fact set cannot reopen this observation identity.
        auto other=A::Manual(*w,2,4);
        assert(!other.eligible && other.rejection=="duplicate_related_revision");
        other=A::Manual(*w,2,3);
        assert(!other.eligible && other.rejection=="duplicate_related_revision");
    } else if (test==34) {
        w->tasks={unary("putdown",w->objects[3]),unary("pickup",w->objects[4])};
        w->ApplyStateValue(StateField::LOCATION,3,1,false,EvidenceSource::INITIAL);
        A::FailTask(*w,1); w->SetSenseResult({3});
        w->ExecuteMainTaskLoop(false);
        assert(w->ProbeFeedback().size()==1);
        const auto& r=w->ProbeFeedback()[0];
        assert(r.related_new_evidence && !r.restored_tasks.empty() && !r.completed_tasks.empty());
        assert(w->GetTerminalSummary().allGoalsSatisfied());
    } else assert(false);
}
