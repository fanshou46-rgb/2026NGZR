#include "rdfw.hpp"
#include "stage_timing.hpp"
#include <chrono>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <new>
using namespace _home;
static unsigned long long allocations=0;
void* operator new(std::size_t n) { ++allocations;if(void* p=std::malloc(n?n:1))return p;throw std::bad_alloc(); }
void* operator new[](std::size_t n) {return ::operator new(n);}
void operator delete(void* p) noexcept {std::free(p);}
void operator delete[](void* p) noexcept {std::free(p);}
namespace _home {struct ScoreSemanticsTestAccess {
    static CandidatePlan Projection(RDFW& w) {return w.BuildTaskGroupPlan({0});}
};}
static Instruction T(const char* name,std::shared_ptr<Object> x,std::shared_ptr<Object> y=nullptr) {
    Instruction t;t.behave=name;t.X={x};if(y){t.Y={y};t.isUseY=true;}return t;
}
int main(int argc,char** argv) {
    assert(argc==3);const unsigned size=std::atoi(argv[2]);
    StageTiming::get().enabled=false;DebugLogSuppressed()=true;std::cout.setstate(std::ios_base::failbit);
    auto w=std::make_shared<RDFW>();char name[]="profile",path[]="-path";char* args[]={name,path,argv[1]};
    w->Init(3,args);w->stage=2;
    std::string env="(at 0 1) (hold 0) (plate 0) (sort 1 human) (size 1 big) (at 1 1)";
    for(unsigned id=2;id<=size;++id) env+=" (sort "+std::to_string(id)+" table) (size "+std::to_string(id)+" big) (at "+std::to_string(id)+" 1)";
    assert(w->ParseEnv(env));w->human=std::dynamic_pointer_cast<BigObject>(w->objects[1]);
    for(unsigned id=1;id<=size;++id) w->ApplyStateValue(StateField::LOCATION,id,1,true,EvidenceSource::SENSE);
    for(unsigned id=2;id<=size;++id) w->notnot_infoConstrains.push_back(T("near",w->objects[id],w->objects[1]));
    w->constraint_eligible.assign(size-1,true);w->constraint_uncertain.assign(size-1,false);
    // Long support list plus depth-8 chain; direct benchmark fixtures only.
    for(unsigned id=2;id<=size;++id) {
        auto& p=w->locationProvenance[id];
        for(unsigned k=0;k<size-1;++k)p.supporting_constraints.push_back(k);
        if(id<=9) w->DependOn(StateField::LOCATION,id,StateField::LOCATION,id-1);
        w->tasks.push_back(T("goto",w->objects[id]));
    }
    const auto before=w->DebugStateSnapshot();
    unsigned long long checksum=0;
    const unsigned iterations[]={100000,2000,80};
    for(unsigned phase=0;phase<3;++phase) {
        unsigned long long sum=0;const auto count=allocations;
        const auto start=std::chrono::steady_clock::now();
        for(unsigned k=0;k<iterations[phase];++k) {
            if(phase==0)sum+=w->FactLocation(2+k%(size-1))==1;
            else if(phase==1)sum+=w->GetTerminalSummary().satisfied_goals;
            else {const auto p=ScoreSemanticsTestAccess::Projection(*w);sum+=p.actions.size()+p.dry_run_succeeded;}
        }
        const auto elapsed=std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-start).count();
        const auto allocated=allocations-count;
        std::cout.clear();std::cout<<"PROFILE {\"size\":"<<size<<",\"phase\":"<<phase<<",\"calls\":"<<iterations[phase]<<",\"nanos\":"<<elapsed<<",\"allocations\":"<<allocated<<",\"checksum\":"<<sum<<"}\n";
        std::cout.setstate(std::ios_base::failbit);checksum+=sum;
        assert(w->DebugStateSnapshot()==before);
    }
    std::cout.clear();return checksum?0:1;
}
