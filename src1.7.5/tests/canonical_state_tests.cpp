#include "rdfw.hpp"
#include "stage_timing.hpp"
#include <cassert>
#include <cstdlib>
#include <iostream>
using namespace _home;
namespace _home {
struct ScoreSemanticsTestAccess {
    static bool Action(RDFW& w,int action) {
        switch(action) {
        case 0:return w.Open(2); case 1:return w.TakeOut(3,2);
        case 2:return w.ToPlate(3); case 3:return w.Move(5);
        case 4:return w.FromPlate(3); case 5:return w.PutDown(3);
        case 6:return w.PickUp(3); case 7:return w.Move(1);
        case 8:return w.PutIn(3,2); case 9:return w.Close(2);
        }
        return false;
    }
    static void Shadow(RDFW& w,bool enable) { w.shadow_dry_run=enable; }
    static void Sense(RDFW& w) { w.sense(2); }
    static bool NotStored(RDFW& w,unsigned id) { return w.IsNotStoredFact(id); }
    static void ForceSense(RDFW& w) { w.SenseCurrentLocationOnly(true); }
};
}
static Instruction Task(const char* behave,std::shared_ptr<Object> x,std::shared_ptr<Object> y=nullptr) {
    Instruction t;t.behave=behave;t.X={x};if(y){t.Y={y};t.isUseY=true;}return t;
}
static std::shared_ptr<RDFW> World(char* words,int stage=2) {
    auto w=std::make_shared<RDFW>();char name[]="canonical",path[]="-path";char* args[]={name,path,words};
    w->Init(3,args);w->stage=stage;
    assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) (closed 2) "
        "(sort 3 cup) (size 3 small) (inside 3 2) (sort 4 table) (size 4 big) (at 4 5)"));
    w->human=std::dynamic_pointer_cast<BigObject>(w->objects[1]);return w;
}
int main(int argc,char** argv) {
    assert(argc==3);int test=std::atoi(argv[2]);auto w=World(argv[1]);
    auto s=std::dynamic_pointer_cast<SmallObject>(w->objects[3]);
    auto c=std::dynamic_pointer_cast<Container>(w->objects[2]);
    const auto fact=[&](StateField f,unsigned id,int value,EvidenceSource source=EvidenceSource::SENSE) {w->ApplyStateValue(f,id,value,true,source);};
    if(test==0) {
        fact(StateField::LOCATION,2,1);w->MarkUnresolved(StateField::LOCATION,2);
        w->objectLocationVerified[2]=true; // deliberate stale compatibility
        assert(c->location==1 && w->FactLocation(2)==UNKNOWN && !w->IsLocationVerified(2));
    } else if(test==1 || test==2 || test==14) {
        fact(StateField::LOCATION,2,1);w->objects[4]->location=UNKNOWN;
        w->notnot_infoConstrains.push_back(Task("near",c,w->objects[4]));w->ApplyMustNearConstraintCorrection();
        assert(w->FactLocation(4)==1);w->constraint_eligible={test!=2};w->constraint_uncertain={test!=2};
        if(test==1)fact(StateField::LOCATION,2,5);
        assert(w->objects[4]->location==1 && w->FactLocation(4)==UNKNOWN);
        if(test==14) {
            Instruction binding;binding.behave="goto";binding.conditionX.sort="table";binding.SearchConditionObject(w);
            assert(binding.X.size()==1 && binding.X[0]==w->objects[4]);
            assert(TerminalChecker().evaluateTask(*w,binding)==TerminalStatus::UNKNOWN);
        }
    } else if(test==3 || test==12) {
        w->tasks={Task("goto",c)};assert(c->location==w->location);
        auto before=w->DebugStateSnapshot();assert(!w->ZeroActionPreCheck(w->tasks[0]));
        assert(w->GetTerminalSummary().goals[0]==TerminalStatus::UNKNOWN);
        assert(w->DebugStateSnapshot()==before);
        if(test==12) { fact(StateField::LOCATION,2,5);c->location=1;
            assert(w->GetTerminalSummary().goals[0]==TerminalStatus::UNSATISFIED); }
    } else if(test==4) {
        fact(StateField::LOCATION,2,5);fact(StateField::INSIDE,3,NONE);fact(StateField::CONTAINER_STATE,2,1);
        assert(c->location==5 && s->inside==NONE && c->isOpen==1);
        assert(w->FactLocation(2)==5 && w->FactInside(3)==NONE && w->FactContainerState(2)==1);
        assert(w->DebugStateConsistency().empty());
    } else if(test==5) {
        fact(StateField::LOCATION,2,5);c->location=1;
        assert(w->FactLocation(2)==5);w->objectLocationVerified[2]=false;
        assert(w->FactLocation(2)==5);assert(!w->DebugStateConsistency().empty());
    } else if(test==6) {
        w->SetHold(s);assert(w->FactValue(StateField::HOLD)==3 && w->FactInside(3)==NONE && w->FactLocation(3)==1);
        w->SetPlate(s);assert(w->FactValue(StateField::PLATE)==3 && w->FactValue(StateField::HOLD)==3);
        assert(w->plate==s && w->hold==s && w->DebugStateConsistency().empty());
    } else if(test==7) {
        c->isOpen=1;w->containerStateVerified[2]=true;
        w->MarkUnresolved(StateField::CONTAINER_STATE,2);w->tasks={Task("open",c),Task("close",c)};
        assert(w->FactContainerState(2)==UNKNOWN);
        for(auto status:w->GetTerminalSummary().goals)assert(status==TerminalStatus::UNKNOWN);
    } else if(test==8) {
        w->ApplyStateValue(StateField::LOCATION,2,5,false,EvidenceSource::ASK_ANSWER);
        assert(c->location==5 && w->HasContradictoryEvidence(StateField::LOCATION,2));
        assert(w->FactLocation(2)==UNKNOWN);
        fact(StateField::LOCATION,2,5);assert(w->FactLocation(2)==5); // new observation resolves current truth
    } else if(test==9) {
        auto real=World(argv[1],1), projected=World(argv[1],1);
        ScoreSemanticsTestAccess::Shadow(*projected,true);
        for(int a=0;a<=9;++a) {
            assert(ScoreSemanticsTestAccess::Action(*real,a));assert(ScoreSemanticsTestAccess::Action(*projected,a));
            assert(real->DebugStateSnapshot()==projected->DebugStateSnapshot());
            assert(real->DebugStateConsistency().empty());assert(projected->DebugStateConsistency().empty());
        }
        assert(projected->TestPlatformCalls()==0);
    } else if(test==10 || test==11) {
        fact(StateField::LOCATION,2,1);w->objects[4]->location=UNKNOWN;
        w->notnot_infoConstrains.push_back(Task("near",c,w->objects[4]));w->ApplyMustNearConstraintCorrection();
        w->constraint_eligible={true};w->constraint_uncertain={false};
        w->tasks={Task("open",c)};w->debug_capture_projection=true;
        const auto before=w->DebugStateSnapshot();auto plan=w->PreviewTaskGroupPlan({0});
        assert(w->DebugStateSnapshot()==before && plan.dry_run_succeeded && !plan.debug_projected_state.empty());
        assert(w->SolveTask(w->tasks[0]));assert(w->DebugStateSnapshot()==plan.debug_projected_state);
    } else if(test==13) {
        w->SetPlate(s,EvidenceSource::INITIAL);w->tasks={Task("pickup",s)};
        assert(!w->SolveTask_PickUp(3) || w->TestPlatformCalls()>0);
        assert(w->TestPlatformCalls()>0); // weak initial storage cannot zero-action complete
    } else if(test==15) {
        fact(StateField::LOCATION,2,1);c->location=5;
        assert(!w->DebugStateConsistency().empty());
        w->ApplyStateValue(StateField::LOCATION,2,1,true,EvidenceSource::SENSE);
        assert(w->DebugStateConsistency().empty());
    } else if(test==16) {
        s->location=1;s->inside=NONE;w->tasks={Task("give",s)};w->SetActionResults({false,false,false,false});
        assert(!w->SolveTask_Give(3));assert(w->TestPlatformCalls()>0);
    } else if(test==17) {
        s->inside=NONE;w->tasks={Task("putin",s,c)};
        assert(!w->SolveTask_TakeOut(3,2)); // opposite-task shortcut must have a fact
    } else if(test==18) {
        w->notnot_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection();
        fact(StateField::LOCATION,2,5);w->SetSenseResult({2});ScoreSemanticsTestAccess::Sense(*w);
        assert(w->FactLocation(3)==1 && w->Provenance(StateField::LOCATION,3).dependency_count==2);
        w->constraint_uncertain={true};assert(w->FactLocation(3)==UNKNOWN);
    } else if(test==19) {
        w->notnot_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection();
        w->not_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection();
        assert(s->inside==UNKNOWN && w->FactInside(3)==UNKNOWN && !w->IsInsideVerified(3));
    } else if(test==20) {
        w->SetHold(s);w->Fini();assert(!w->ResolvedState(StateField::HOLD,0).present);
        assert(!w->ResolvedState(StateField::PLATE,0).present);
    } else if(test==21) {
        fact(StateField::LOCATION,2,1);w->DependOn(StateField::LOCATION,2,StateField::INSIDE,3);
        assert(!w->ResolvedState(StateField::LOCATION,2).present); // weak support revision matches, but is not fact
    } else if(test==22) {
        w->ApplyStateValue(StateField::LOCATION,2,1,true,EvidenceSource::CONSTRAINT_HEURISTIC);
        assert(!w->ResolvedState(StateField::LOCATION,2).present);
    } else if(test==23) {
        fact(StateField::LOCATION,2,1);auto snapshot=w->DebugStateSnapshot();
        for(int i=0;i<1000;++i)assert(w->FactLocation(2)==1);
        assert(w->DebugStateSnapshot()==snapshot);
    } else if(test==24) {
        fact(StateField::INSIDE,3,2,EvidenceSource::CONSTRAINT_DERIVED);
        w->SetConstraintSupport(StateField::INSIDE,3,0);assert(w->FactInside(3)==UNKNOWN); // removed support
    } else if(test==25) {
        w->SetHold(s,EvidenceSource::INITIAL);
        assert(ScoreSemanticsTestAccess::Action(*w,3));
        assert(s->location==5 && w->FactLocation(3)==UNKNOWN);
        assert(w->FactValue(StateField::HOLD)==UNKNOWN);
    } else if(test==26) {
        fact(StateField::CONTAINER_STATE,2,2);assert(w->FactContainerState(2)==UNKNOWN);
        w->SetHold(s);w->plateProvenance=w->holdProvenance;w->plate_id=3;w->plate=s;
        assert(w->FactValue(StateField::HOLD)==3 && w->FactValue(StateField::PLATE)==3);
        // SDK permits both slots to refer to the same small object.
        assert(!w->DebugStateConsistency().empty());
    } else if(test==27) {
        fact(StateField::CONTAINER_STATE,2,2);fact(StateField::LOCATION,3,1);
        w->DependOn(StateField::LOCATION,3,StateField::CONTAINER_STATE,2);
        assert(w->FactLocation(3)==UNKNOWN); // matching revision of an invalid state is no support
    } else if(test==28) {
        w->stage=1;fact(StateField::LOCATION,2,1);w->MarkUnresolved(StateField::LOCATION,2);
        assert(w->score_locations[2]==1 && w->ScoreFactLocation(2)==UNKNOWN);
        w->tasks={Task("goto",c)};
        assert(w->GetTerminalSummary().goals[0]!=TerminalStatus::SATISFIED);
    } else if(test==29) {
        fact(StateField::LOCATION,2,5);c->location=1;
        w->notnot_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection();
        assert(w->FactLocation(3)==5 && s->location==5);
        assert(w->FactInside(3)==2);
    } else if(test==30) {
        w->stage=1;fact(StateField::LOCATION,2,5);c->location=1;
        w->ParseInfo(Task("on",s,c));assert(w->FactLocation(3)==5);
        w->ParseInfo(Task("near",s,c));assert(w->FactLocation(3)==5);
        w->ParseInfo(Task("inside",s,c));assert(w->FactLocation(3)==5);
    } else if(test==31) {
        fact(StateField::INSIDE,3,NONE);s->inside=2;c->smallObjectsInside.push_back(s);
        fact(StateField::LOCATION,2,5);w->SetSenseResult({2});
        ScoreSemanticsTestAccess::Sense(*w);
        assert(w->FactLocation(3)==UNKNOWN); // cache membership cannot prove inside
    } else if(test==32) {
        fact(StateField::INSIDE,3,1); // human is not a container
        assert(w->FactInside(3)==UNKNOWN && !w->DebugStateConsistency().empty());
    } else if(test==33) {
        w->ApplyStateValue(StateField::LOCATION,2,5,false,EvidenceSource::INITIAL);
        w->SetSenseResult({1,3});ScoreSemanticsTestAccess::ForceSense(*w);
        assert(w->FactInside(3)==UNKNOWN && w->FactLocation(3)==1);
        assert(w->FactValue(StateField::HOLD)==UNKNOWN && w->FactValue(StateField::PLATE)==UNKNOWN);
        assert(!ScoreSemanticsTestAccess::NotStored(*w,3));
        assert(!w->TaskFactSatisfied("putdown",3));
        assert(!w->TaskFactSatisfied("give",3,1));
        w->tasks={Task("putdown",s),Task("give",s)};
        for(auto status:w->GetTerminalSummary().goals) assert(status==TerminalStatus::UNKNOWN);
    } else if(test==34 || test==35) {
        fact(StateField::INSIDE,3,test==34?2:NONE,
             test==34?EvidenceSource::CONSTRAINT_DERIVED:EvidenceSource::ACTION_SUCCESS);
        fact(StateField::LOCATION,3,1);
        assert(!ScoreSemanticsTestAccess::NotStored(*w,3));
    } else if(test==36 || test==37 || test==38) {
        fact(StateField::LOCATION,1,1);
        // PickUp feedback excludes this item from the tray; PutDown then
        // excludes it from the hand without claiming the whole tray empty.
        assert(ScoreSemanticsTestAccess::Action(*w,6));
        assert(w->FactValue(StateField::PLATE)==UNKNOWN);
        assert(!ScoreSemanticsTestAccess::NotStored(*w,3));
        assert(ScoreSemanticsTestAccess::Action(*w,5));
        assert(ScoreSemanticsTestAccess::NotStored(*w,3));
        assert(w->TaskFactSatisfied("give",3,1));
        w->tasks={Task("putdown",s),Task("give",s)};
        for(auto status:w->GetTerminalSummary().goals) assert(status==TerminalStatus::SATISFIED);
        if(test==36) {
            w->SetSenseResult({1,2,3});ScoreSemanticsTestAccess::ForceSense(*w);
            assert(ScoreSemanticsTestAccess::NotStored(*w,3));
            assert(w->Provenance(StateField::INSIDE,3).storage_exclusion==3);
        } else if(test==37) {
            assert(ScoreSemanticsTestAccess::Action(*w,6));
            w->MarkUnresolved(StateField::HOLD,0);
            assert(!ScoreSemanticsTestAccess::NotStored(*w,3));
        } else {
            w->MarkUnresolved(StateField::INSIDE,3);
            w->MarkUnresolved(StateField::HOLD,0);
            assert(!ScoreSemanticsTestAccess::NotStored(*w,3));
        }
    } else if(test==39) {
        w->SetHold(s);assert(ScoreSemanticsTestAccess::Action(*w,5));
        // PutDown alone says nothing about an unknown tray. A generic setter
        // does not manufacture the PickUp precondition proof.
        assert(!ScoreSemanticsTestAccess::NotStored(*w,3));
    } else if(test==40) {
        w->SetPlate(s);assert(ScoreSemanticsTestAccess::Action(*w,4));
        assert(ScoreSemanticsTestAccess::Action(*w,5));
        assert(ScoreSemanticsTestAccess::NotStored(*w,3));
    } else if(test==41) {
        assert(ScoreSemanticsTestAccess::Action(*w,6));
        auto before=w->DebugStateSnapshot();w->SetActionResults({false});
        assert(!ScoreSemanticsTestAccess::Action(*w,5));
        assert(w->DebugStateSnapshot()==before && !ScoreSemanticsTestAccess::NotStored(*w,3));
    } else if(test==42) {
        w->SetPlate(nullptr);assert(ScoreSemanticsTestAccess::Action(*w,6));
        w->tasks={Task("putdown",s)};w->debug_capture_projection=true;
        auto before=w->DebugStateSnapshot();auto plan=w->PreviewTaskGroupPlan({0});
        assert(plan.dry_run_succeeded && w->DebugStateSnapshot()==before);
        assert(ScoreSemanticsTestAccess::Action(*w,5));
        assert(w->DebugStateSnapshot()==plan.debug_projected_state);
    } else if(test==43 || test==44) {
        fact(StateField::LOCATION,2,1);fact(StateField::CONTAINER_STATE,2,1);
        assert(ScoreSemanticsTestAccess::Action(*w,test==43?1:6));
        assert(ScoreSemanticsTestAccess::Action(*w,8));
        assert(w->FactValue(StateField::PLATE)==UNKNOWN && w->FactInside(3)==2);
        assert(ScoreSemanticsTestAccess::NotStored(*w,3)==(test==44));
        w->tasks={Task("pickup",s)};
        assert(w->GetTerminalSummary().goals[0]==(test==44?TerminalStatus::UNSATISFIED:TerminalStatus::UNKNOWN));
    } else assert(false);
    std::cout<<"canonical case "<<test<<" passed\n";
}
