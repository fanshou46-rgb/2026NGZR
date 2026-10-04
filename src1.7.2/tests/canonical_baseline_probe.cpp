// Same assertions compiled against unchanged 1.6.5 and current 1.6.6.
// Baseline failures are the minimal before/after semantic bug evidence.
#include "rdfw.hpp"
#include <cassert>
#include <cstdlib>
using namespace _home;
namespace _home { struct ScoreSemanticsTestAccess {
    static void Sense(RDFW& w){w.sense(2);}
    static bool Move(RDFW& w){return w.Move(5);}
}; }
static Instruction T(const char* name,std::shared_ptr<Object> x,std::shared_ptr<Object> y=nullptr){
    Instruction t;t.behave=name;t.X={x};if(y){t.Y={y};t.isUseY=true;}return t;
}
int main(int argc,char** argv){
    assert(argc==3);int test=std::atoi(argv[2]);auto w=std::make_shared<RDFW>();
    char name[]="baseline-probe",path[]="-path";char* args[]={name,path,argv[1]};w->Init(3,args);w->stage=2;
    assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 5) (closed 2) "
        "(sort 3 cup) (size 3 small) (at 3 1)"));
    auto c=std::dynamic_pointer_cast<Container>(w->objects[2]);auto s=std::dynamic_pointer_cast<SmallObject>(w->objects[3]);
    w->human=std::dynamic_pointer_cast<BigObject>(w->objects[1]);
    if(test==0){
        w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);w->MarkUnresolved(StateField::LOCATION,2);
        assert(!w->IsLocationVerified(2));
    } else if(test==1){
        w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);c->location=1;
        assert(TerminalChecker().evaluateTask(*w,T("goto",c))!=TerminalStatus::SATISFIED);
    } else if(test==2){
        w->SetActionResults({false,false,false,false});
        assert(!w->SolveTask_Give(3));assert(w->TestPlatformCalls()>0);
    } else if(test==3){
        w->tasks={T("putin",s,c)};assert(!w->SolveTask_TakeOut(3,2));
    } else if(test==4){
        w->SetHold(s);assert(w->ResolvedState(StateField::INSIDE,3).present);
        assert(w->ResolvedState(StateField::LOCATION,3).present);
    } else if(test==5){
        w->notnot_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection();
        w->not_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection();
        assert(!w->IsInsideVerified(3));
    } else if(test==6){
        w->notnot_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection();
        c->location=5;w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);
        w->SetSenseResult({2});ScoreSemanticsTestAccess::Sense(*w);
        w->constraint_uncertain={true};assert(!w->ResolvedState(StateField::LOCATION,3).present);
    } else if(test==7){
        w->SetHold(s);w->Fini();assert(!w->ResolvedState(StateField::HOLD,0).present);
    } else if(test==8){
        w->SetHold(s,EvidenceSource::INITIAL);assert(ScoreSemanticsTestAccess::Move(*w));
        assert(!w->ResolvedState(StateField::LOCATION,3).present);
    } else if(test==9){
        w->MarkDirectLocationEvidence(2,true,EvidenceSource::CONSTRAINT_HEURISTIC);
        assert(!w->ResolvedState(StateField::LOCATION,2).present);
    } else if(test==10){
        w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);c->location=1;
        w->notnot_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection();
        assert(w->ResolvedState(StateField::LOCATION,3).value==5);
    } else if(test==11){
        w->stage=1;w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);c->location=1;
        w->ParseInfo(T("on",s,c));assert(w->ResolvedState(StateField::LOCATION,3).value==5);
    } else if(test==12){
        s->inside=NONE;w->SetInsideEvidence(3,true,EvidenceSource::SENSE);
        s->inside=2;c->smallObjectsInside.push_back(s);
        w->SetSenseResult({2});ScoreSemanticsTestAccess::Sense(*w);
        assert(!w->ResolvedState(StateField::LOCATION,3).present);
    } else if(test==13){
        s->inside=1;w->SetInsideEvidence(3,true,EvidenceSource::SENSE);
        assert(!w->ResolvedState(StateField::INSIDE,3).present);
    } else assert(false);
}
