#include "rdfw.hpp"
#include <cassert>
#include <memory>
using namespace _home;
namespace _home {struct ScoreSemanticsTestAccess {
    static bool open(RDFW& w){return w.Open(2);}
    static bool from(RDFW& w){return w.FromPlate(3);}
    static bool pick(RDFW& w){return w.PickUp(3);}
    static bool down(RDFW& w){return w.PutDown(3);}
    static void sense(RDFW& w){w.SenseCurrentLocationOnly(true);}
    static void guardedFailure(RDFW& w) {
        w.has_active_candidate=true;w.guarded_actions_active=false;
        assert(!w.FromPlate(3));
        w.guarded_actions_active=true;
        bool rejected=false;try{w.Open(2);}catch(const std::runtime_error&){rejected=true;}
        assert(rejected);w.guarded_actions_active=false;
    }
};}
static std::shared_ptr<RDFW> make(char* words) {
    auto w=std::make_shared<RDFW>();char name[]="gateway",path[]="-path";char* args[]={name,path,words};
    w->Init(3,args);w->stage=1;
    assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) (closed 2) "
        "(sort 3 cup) (size 3 small) (at 3 1)"));return w;
}
int main(int argc,char** argv) {
    assert(argc==2);auto w=make(argv[1]);
    assert(ScoreSemanticsTestAccess::open(*w));
    assert(w->ActionReceipts().size()==w->TestPlatformCalls());
    auto r=w->ActionReceipts().back();
    assert(r.permit.kind==PermitKind::CONFIRMED && r.state_committed && r.sent);
    assert(r.outcome==ExecutionStatus::SUCCEEDED && r.public_feedback=="true");
    assert(w->Provenance(StateField::CONTAINER_STATE,2).event==r.id);
    // Weak Stage2 door information is explicitly unqualified until a complete
    // modeled policy exists; logging does not upgrade it to a fact.
    w=make(argv[1]);w->stage=2;w->ApplyStateValue(StateField::CONTAINER_STATE,2,0,false,EvidenceSource::ASK_ANSWER);
    w->SetActionResults({false});assert(!ScoreSemanticsTestAccess::open(*w));
    assert(w->ActionReceipts().back().permit.kind==PermitKind::LEGACY_UNQUALIFIED);
    assert(w->FactContainerState(2)==UNKNOWN);
    // Negative tray evidence closes before the next policy action is rejected.
    w=make(argv[1]);w->SetActionResults({false});ScoreSemanticsTestAccess::guardedFailure(*w);
    assert(w->TestPlatformCalls()==1 && w->ActionReceipts().size()==1);
    assert(w->Provenance(StateField::INSIDE,3).storage_exclusion&2u);
    assert(w->Provenance(StateField::INSIDE,3).tray_absence_event==1);
    // A relation proven by an earlier action names that receipt rather than
    // pretending the unknown tray scalar is a confirmed fact.
    w=make(argv[1]);w->MarkUnresolved(StateField::PLATE,0);
    assert(ScoreSemanticsTestAccess::pick(*w));
    assert(w->Provenance(StateField::INSIDE,3).tray_absence_event==1);
    assert(ScoreSemanticsTestAccess::down(*w));
    assert(w->Provenance(StateField::INSIDE,3).hand_absence_event==2);
    assert(w->Provenance(StateField::INSIDE,3).tray_absence_event==1);
    assert(ScoreSemanticsTestAccess::pick(*w));
    bool relation_proof=false;
    for(const auto& e:w->ActionReceipts().back().permit.evidence)
        if(e.predicate=="item_absent_from_tray") {
            relation_proof=e.confirmed && e.object==3 && e.value==3 && e.event==1 && e.source=="storage_absence_receipt";
        }
    assert(relation_proof);
    // Raw observations retain returned order and IDs without claiming slots.
    w=make(argv[1]);w->stage=2;w->SetSenseResult({3,2});ScoreSemanticsTestAccess::sense(*w);
    assert(w->ActionReceipts().back().public_feedback=="[3,2]");
    // An exception after actual send cannot be interpreted as a negative reply.
    w=make(argv[1]);w->SetThrowAction(true);bool threw=false;
    try{ScoreSemanticsTestAccess::open(*w);}catch(const std::runtime_error&){threw=true;}
    assert(threw && w->TestPlatformCalls()==1);
    assert(w->ActionReceipts().back().outcome==ExecutionStatus::INDETERMINATE);
    assert(w->FactLocation(0)==UNKNOWN && w->FactContainerState(2)==UNKNOWN);
}
