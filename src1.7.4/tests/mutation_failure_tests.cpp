// Identical observable tests compile against 1.6.6 for before probes.
#include "rdfw.hpp"
#include <cassert>
#include <cstdlib>
#include <new>
#include <iostream>
using namespace _home;
static long allocation_budget=-1;
void* operator new(std::size_t n) {
    if(allocation_budget==0) throw std::bad_alloc();
    if(allocation_budget>0) --allocation_budget;
    if(void* p=std::malloc(n?n:1)) return p;
    throw std::bad_alloc();
}
void* operator new[](std::size_t n) { return ::operator new(n); }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
static Instruction T(const char* name,std::shared_ptr<Object> x,std::shared_ptr<Object> y=nullptr) {
    Instruction t; t.behave=name; t.X={x}; if(y) {t.Y={y};t.isUseY=true;} return t;
}
namespace _home { struct ScoreSemanticsTestAccess {
    static bool Action(RDFW& w,int a) {
        switch(a) {case 0:return w.Open(2);case 1:return w.TakeOut(3,2);case 2:return w.ToPlate(3);
        case 3:return w.Move(5);case 4:return w.FromPlate(3);case 5:return w.PutDown(3);
        case 6:return w.PickUp(3);case 7:return w.PutIn(3,2);case 8:return w.Close(2);}
        return false;
    }
    static void Sense(RDFW& w) {w.SenseCurrentLocationOnly(true);}
    static void Shadow(RDFW& w) {w.shadow_dry_run=true;}
    static void Projection(RDFW& w) {w.BuildTaskGroupPlan({0,1});}
}; }
static std::shared_ptr<RDFW> World(char* words) {
    auto w=std::make_shared<RDFW>();char name[]="hardening",path[]="-path";char* args[]={name,path,words};
    w->Init(3,args); w->stage=1;
    assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) (closed 2) "
        "(sort 3 cup) (size 3 small) (inside 3 2) "
        "(sort 4 cupboard) (size 4 big) (type 4 container) (at 4 1) (closed 4)"));
    w->human=std::dynamic_pointer_cast<BigObject>(w->objects[1]);
    return w;
}
int main(int argc,char** argv) {
    assert(argc==3);const int test=std::atoi(argv[2]);
    if(test==3) {
        auto w=World(argv[1]);auto before=w->DebugStateSnapshot();
        auto foreign=std::make_shared<SmallObject>(3,1,"cup");
        w->SetHold(foreign);assert(w->DebugStateSnapshot()==before);
        w->SetPlate(foreign);assert(w->DebugStateSnapshot()==before);
        std::cout<<"foreign storage identity rejected\n";return 0;
    }
    if(test>=5 && test<=13) {
        // Failed platform returns never alter world facts; action bookkeeping is
        // intentionally outside the world-fact contract.
        auto w=World(argv[1]);w->SetActionResults({false});auto before=w->DebugStateSnapshot();
        assert(!ScoreSemanticsTestAccess::Action(*w,test-5));assert(w->DebugStateSnapshot()==before);return 0;
    }
    unsigned failures=0, completed=0;
    const int limit=(test==4 || test==14)?1400:test>=19?500:120;
    for(int fail_after=0;fail_after<=limit;++fail_after) {
        auto w=World(argv[1]);auto small=std::dynamic_pointer_cast<SmallObject>(w->objects[3]);
        if(test==1) w->notnot_infoConstrains={T("near",w->objects[2],w->objects[4])};
        if(test==4) {w->tasks={T("open",w->objects[2]),T("takeout",small,w->objects[2])};}
        if(test==14) {w->stage=2;w->SetSenseResult({2,3});}
        const auto before=w->DebugStateSnapshot();bool thrown=false;
        allocation_budget=fail_after;
        try {
            if(test==0) w->ApplyStateValue(StateField::INSIDE,3,4,true,EvidenceSource::SENSE);
            else if(test==1) w->MarkDirectLocationEvidence(2,true,EvidenceSource::CONSTRAINT_DERIVED);
            else if(test==2) w->ParseInfo(T("inside",small,w->objects[4]));
            else if(test==4) ScoreSemanticsTestAccess::Projection(*w);
            else if(test==14) ScoreSemanticsTestAccess::Sense(*w);
            else if(test==15) w->SetHold(small);
            else if(test==16) w->SetPlate(small);
            else if(test==17) {w->notnot_infoConstrains={T("inside",small,w->objects[4])};w->ApplyMustInConstraintCorrection();}
            else if(test==18) {w->ApplyStateValue(StateField::LOCATION,2,5,true,EvidenceSource::SENSE);}
            else if(test>=19 && test<=27) ScoreSemanticsTestAccess::Action(*w,test-19);
            else assert(false);
        } catch(const std::bad_alloc&) {thrown=true;}
        // Keep allocations disabled throughout stack unwinding. Reset only after
        // the mutation/projection guards have restored their snapshots.
        allocation_budget=-1;
        if(thrown) {
            ++failures;
            if(test>=19 && w->TestPlatformCalls()>0) {
                assert(w->FactLocation(0)==UNKNOWN);
                assert(w->FactValue(StateField::HOLD)==UNKNOWN && w->FactValue(StateField::PLATE)==UNKNOWN);
                assert(!w->IsNotStoredFact(3));
            } else assert(w->DebugStateSnapshot()==before);
        }
        else {++completed;if(test==4) assert(w->DebugStateSnapshot()==before);}
        assert(w->DebugStateConsistency().empty());
    }
    assert(failures && completed);
    std::cout<<"fault-sweep case="<<test<<" rollback="<<failures<<" completed="<<completed<<"\n";
}
