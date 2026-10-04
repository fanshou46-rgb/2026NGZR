#include "rdfw.hpp"
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
using namespace _home;
namespace _home {struct InformationModelTestAccess {
    static ProbabilityBounds forecast(RDFW&w,unsigned id,int loc){return w.VisibilityProbability(id,loc);}
    static void ids(RDFW&w,std::vector<unsigned>&ids){w.DryRunSenseIds(ids);}
    static bool act(RDFW&w,int a){return a==0?w.PickUp(3):a==1?w.PutIn(3,4):w.TakeOut(3,4);}
    static void ask(RDFW&w,ProbeCandidate&p){w.EvaluateAskBranches(p);}
    static bool pickup_model(RDFW&w){return w.DryRunActionSucceeds("PickUp",{3});}
};}
static bool close(double a,double b){return std::abs(a-b)<1e-10;}
static JointWorld joint(int at) {
    JointWorld w;w.robot=1;w.locations={1,2};
    w.objects[3]=JointObject(true,false,at);return w;
}
int main(int argc,char**argv) {
    assert(argc==3);const int test=std::atoi(argv[2]);
    if(test>=4 && test<=8) {
        JointBelief b({{joint(1),.3},{joint(2),.5}},test==7?0:.2);
        const auto event=[](const JointWorld&w){return w.objects.at(3).at==1;};
        if(test==4) {
            const auto bound=b.probabilityBounds(event);assert(close(bound.lower,.3) && close(bound.upper,.5));
            assert(b.condition([&](const JointWorld&w){return event(w)?1.:0.;},9));
            const auto after=b.probabilityBounds(event);assert(close(after.lower,.6) && close(after.upper,1));
            assert(!b.condition([](const JointWorld&){return 1.;},9) && close(b.residualMass(),.4));
        } else if(test==5) {
            bool threw=false;try{b.condition([](const JointWorld&){return -1.;},10);}catch(const std::invalid_argument&){threw=true;}
            assert(threw && close(b.residualMass(),.2));
            assert(b.condition([](const JointWorld&){return 1.;},10));
        } else if(test==6) {
            assert(!b.condition([](const JointWorld&){return 0.;},11));
            assert(close(b.residualMass(),1));const auto bound=b.probabilityBounds(event);
            assert(close(bound.lower,0) && close(bound.upper,1));
        } else if(test==7) {
            const auto before=b.probabilityBounds(event);
            assert(!b.condition([](const JointWorld&){return 0.;},12));
            assert(close(before.lower,b.probabilityBounds(event).lower));
            assert(b.condition([](const JointWorld&){return 1.;},12));
        } else {
            // Non-deterministic likelihood: covered mass=.3*.2+.5*.8=.46.
            assert(b.condition([&](const JointWorld&w){return event(w)?.2:.8;}));
            const auto bound=b.probabilityBounds(event);
            assert(close(bound.lower,.06/.66) && close(bound.upper,.26/.66));
        }return 0;
    }
    if(test==9) {
        LocationBelief b;b.initialize({{'a',1},{'a',2},{'i',4}},{'?',-1});
        const auto before=b.distribution();
        assert(!b.filterVisibility(1,true,{{4,{2,0}}},true));assert(b.distribution()==before);
        assert(b.filterVisibility(1,false,{{4,{1,1}}},true));
        assert(close(b.probability({'a',1}),0) && close(b.probability({'i',4}),0));return 0;
    }
    auto w=std::make_shared<RDFW>();char n[]="visibility",p[]="-path";char*args[]={n,p,argv[1]};
    w->Init(3,args);w->stage=1;
    const std::string at=test==1 || test==13 || test==15?"":test==12?"(at 3 0) ":"(at 3 2) ";
    assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 table) (size 2 big) (at 2 2) (sort 4 cupboard) (size 4 big) "
        "(type 4 container) (at 4 1) (closed 4) (sort 3 cup) (size 3 small) "+at+"(inside 3 4)"));
    w->stage=2;
    if(test==0) {
        Instruction put;put.behave="puton";put.X={w->objects[3]};put.Y={w->objects[2]};put.isUseY=true;
        Instruction go;go.behave="goto";go.X={w->objects[2]};w->tasks={put,go};
        const auto before=w->DebugStateSnapshot();const auto plan=w->PreviewTaskGroupPlan({1});
        assert(plan.dry_run_succeeded && plan.lost_goals.empty() && plan.gained_goals==std::vector<std::size_t>{1});
        assert(plan.marginal_score==35 && w->DebugStateSnapshot()==before);
    } else if(test==1) {
        assert(w->ExplicitAt(3)==-2);
        std::vector<unsigned> ids;InformationModelTestAccess::ids(*w,ids);
        assert(std::find(ids.begin(),ids.end(),3)==ids.end());
        w->ApplyStateValue(StateField::CONTAINER_STATE,4,1,true,EvidenceSource::ACTION_SUCCESS);
        InformationModelTestAccess::ids(*w,ids);assert(std::find(ids.begin(),ids.end(),3)!=ids.end());
    } else if(test==2) {
        const auto bound=InformationModelTestAccess::forecast(*w,3,2);
        assert(close(bound.lower,1) && close(bound.upper,1));
        const auto nowhere=InformationModelTestAccess::forecast(*w,3,1);
        assert(close(nowhere.lower,0) && close(nowhere.upper,0));
    } else if(test==3) {
        w->SetPlate(w->smallObjects[0]);std::vector<unsigned> ids;InformationModelTestAccess::ids(*w,ids);
        assert(std::find(ids.begin(),ids.end(),3)!=ids.end());
    } else if(test==10) {
        w->SetActionResults({true});assert(InformationModelTestAccess::act(*w,0)); // simulator stub only
        assert(w->ExplicitAt(3)==1 && w->InsideRelation(3,4)==1);
        w->SetActionResults({true});assert(InformationModelTestAccess::act(*w,1));assert(w->ExplicitAt(3)==-2);
        w->SetActionResults({true,true});assert(InformationModelTestAccess::act(*w,2));assert(w->ExplicitAt(3)==1);
    } else if(test==11) {
        // Weak route replacement never overwrites independent physical at.
        w->ApplyStateValue(StateField::LOCATION,3,1,false,EvidenceSource::ASK_ANSWER);
        assert(w->ExplicitAt(3)==2 && close(InformationModelTestAccess::forecast(*w,3,2).lower,1));
    } else if(test==12) {
        assert(w->ExplicitAt(3)==0 && close(InformationModelTestAccess::forecast(*w,3,0).lower,1));
    } else if(test==13) {
        assert(w->ParseEnv("(sort 5 closet) (size 5 big) (type 5 container) (at 5 2) (opened 5)"));
        w->ApplyStateValue(StateField::LOCATION,5,2,true,EvidenceSource::ACTION_SUCCESS);
        w->ApplyStateValue(StateField::CONTAINER_STATE,5,1,true,EvidenceSource::ACTION_SUCCESS);
        w->SetInsideRelation(3,5,1,true,EvidenceSource::ACTION_SUCCESS);
        const auto p=InformationModelTestAccess::forecast(*w,3,2);assert(close(p.lower,1) && close(p.upper,1));
    } else if(test==14) {
        ProbeCandidate p;p.kind=ProbeKind::ASK_LOCATION;p.target_object=3;p.eligible=true;
        InformationModelTestAccess::ask(*w,p);
        assert(!p.eligible && p.rejection=="unmodeled_truthful_reply_order" && close(p.residual_mass,1));
    } else if(test==15) {
        // Being visible through an opened parent is not explicit at evidence.
        w->ApplyStateValue(StateField::CONTAINER_STATE,4,1,true,EvidenceSource::ACTION_SUCCESS);
        w->ApplyStateValue(StateField::LOCATION,3,1,true,EvidenceSource::SENSE);
        assert(w->ScoreFactLocation(3)==UNKNOWN && !w->TaskFactSatisfied("puton",3,4));
        assert(!InformationModelTestAccess::pickup_model(*w));
    }
    assert(w->DebugStateConsistency().empty());
}
