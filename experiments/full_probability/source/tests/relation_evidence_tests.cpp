#include "rdfw.hpp"
#include <cassert>
#include <cstdlib>
using namespace _home;
namespace _home { struct ScoreSemanticsTestAccess {
    static bool ask(RDFW& w) {return w.GetSmallObjectStatus(3);}
}; }
int main(int argc,char**argv) {
    assert(argc==3);const int test=std::atoi(argv[2]);auto w=std::make_shared<RDFW>();
    char n[]="relations",p[]="-path";char* args[]={n,p,argv[1]};w->Init(3,args);w->stage=2;
    assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) (opened 2) "
        "(sort 3 cup) (size 3 small) (inside 3 2) "
        "(sort 4 closet) (size 4 big) (type 4 container) (at 4 1) (opened 4)"));
    if(test==2) {
        Instruction c;c.behave="inside";c.X={w->objects[3]};c.Y={w->objects[2]};c.isUseY=true;
        w->notnot_infoConstrains={c};w->ApplyMustInConstraintCorrection();
        assert(w->InsideRelation(3,2)==1);
        w->SetInsideRelation(3,4,1,false,EvidenceSource::ASK_ANSWER);
        assert(w->InsideRelation(3,2)==1 && w->InsideRelation(3,4)==UNKNOWN);
        w->constraint_eligible={false};assert(w->InsideRelation(3,2)==UNKNOWN);
    } else {
        const int truth=test==0?1:0;
        w->SetInsideRelation(3,2,truth,true,EvidenceSource::ACTION_SUCCESS);
        if(test!=3) w->SetInsideRelation(3,4,1,false,EvidenceSource::ASK_ANSWER);
        assert(w->InsideRelation(3,2)==truth);
        w->SetAskResult(test==3?"inside(3,2)":"at(3,5)");
        assert(ScoreSemanticsTestAccess::ask(*w)==(test!=3));
        assert(w->InsideRelation(3,2)==truth && w->InsideRelation(3,4)==UNKNOWN);
    }
    assert(w->DebugStateConsistency().empty());
}
