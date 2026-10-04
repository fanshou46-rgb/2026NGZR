#include "rdfw.hpp"
#include <cassert>
#include <cstdlib>
#include <memory>
using namespace _home;
namespace _home {
struct ScoreSemanticsTestAccess {
    static bool OpenContainer(RDFW& w) { return w.Open(2); }
    static bool MoveRobot(RDFW& w) { return w.Move(5); }
    static bool AskBig(RDFW& w) { return w.GetBigObjectStatus(2); }
    static bool AskSmall(RDFW& w) { return w.GetSmallObjectStatus(3); }
    static bool PickUpItem(RDFW& w) { return w.PickUp(3); }
};
}
static Instruction Goal(const char* name, const std::shared_ptr<Object>& x) {
    Instruction result; result.behave=name; result.X.push_back(x); return result;
}
int main(int argc, char** argv) {
    assert(argc == 3);
    const int test = std::atoi(argv[2]);
    auto w = std::make_shared<RDFW>();
    char program[]="state_layer", option[]="-path";
    char* args[]={program,option,argv[1]}; w->Init(3,args); w->stage=2;
    assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) "
        "(sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 4) (closed 2) "
        "(sort 3 cup) (size 3 small) (inside 3 2)"));
    auto c=std::dynamic_pointer_cast<Container>(w->objects[2]);
    auto s=std::dynamic_pointer_cast<SmallObject>(w->objects[3]);
    if (test == 0) {
        const auto& p=w->Provenance(StateField::LOCATION,2);
        assert(p.received.present && p.received.value==4);
        assert(p.received.source==EvidenceSource::INITIAL);
        assert(p.resolved_value==4 && !w->IsLocationVerified(2));
    } else if (test == 1) {
        w->SetAskResult("at(2,5)"); assert(ScoreSemanticsTestAccess::AskBig(*w));
        assert(w->HasContradictoryEvidence(StateField::LOCATION,2));
        assert(c->location==5 && !w->IsLocationVerified(2));
        assert(w->Provenance(StateField::LOCATION,2).resolved_value==UNKNOWN);
        assert(w->Provenance(StateField::LOCATION,2).received.source==EvidenceSource::ASK_ANSWER);
    } else if (test == 2) {
        assert(ScoreSemanticsTestAccess::OpenContainer(*w));
        const auto& p=w->Provenance(StateField::CONTAINER_STATE,2);
        assert(c->isOpen==1 && p.resolved_value==1);
        assert(p.received.source==EvidenceSource::ACTION_SUCCESS && w->IsContainerStateVerified(2));
    } else if (test == 3) {
        w->SetActionResults({false}); assert(!ScoreSemanticsTestAccess::OpenContainer(*w));
        assert(c->isOpen==0 && !w->IsContainerStateVerified(2));
        assert(w->Provenance(StateField::CONTAINER_STATE,2).received.source==EvidenceSource::INITIAL);
    } else if (test == 4) {
        assert(w->ParseEnvSentence("(at 2 5)"));
        assert(c->location==UNKNOWN && w->HasContradictoryEvidence(StateField::LOCATION,2));
        assert(!w->IsLocationVerified(2));
    } else if (test == 5 || test == 6) {
        w->notnot_infoConstrains.push_back(Goal("near",w->objects[2]));
        w->notnot_infoConstrains.back().Y.push_back(w->objects[1]);
        w->objects[1]->location=UNKNOWN;
        c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);
        w->ApplyMustNearConstraintCorrection();
        assert(w->objects[1]->location==1);
        assert(w->Provenance(StateField::LOCATION,1).dependency_count>0);
        if (test==6) {
            w->tasks.push_back(Goal("goto",w->objects[1]));
            assert(w->GetTerminalSummary().goals[0]==TerminalStatus::SATISFIED);
        }
        c->location=5; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);
        assert(!w->DependenciesCurrent(StateField::LOCATION,1));
        assert(!w->IsLocationVerified(1));
        if (test==6)
            assert(w->GetTerminalSummary().goals[0]==TerminalStatus::UNKNOWN);
    } else if (test == 7) {
        // Copy/restore must preserve inference support, not just direct claims.
        c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);
        w->objects[1]->location=UNKNOWN;
        Instruction near=Goal("near",c); near.Y.push_back(w->objects[1]);
        w->notnot_infoConstrains.push_back(near);
        w->ApplyMustNearConstraintCorrection();
        w->constraint_eligible.assign(1,true);
        w->constraint_uncertain.assign(1,false);
        const auto derived_before=w->Provenance(StateField::LOCATION,1);
        assert(derived_before.dependency_count==1);
        assert(derived_before.supporting_constraints.size()==1);
        auto before=w->Provenance(StateField::LOCATION,2);
        w->tasks.push_back(Goal("open",c));
        w->PreviewCandidatePlan(0);
        const auto& after=w->Provenance(StateField::LOCATION,2);
        assert(after.revision==before.revision && after.resolved_value==before.resolved_value);
        assert(after.received.source==before.received.source);
        const auto& derived_after=w->Provenance(StateField::LOCATION,1);
        assert(derived_after.revision==derived_before.revision);
        assert(derived_after.resolved_value==derived_before.resolved_value);
        assert(derived_after.resolved_source==derived_before.resolved_source);
        assert(derived_after.resolved_verified==derived_before.resolved_verified);
        assert(derived_after.dependency_count==derived_before.dependency_count);
        assert(derived_after.dependencies[0].field==derived_before.dependencies[0].field);
        assert(derived_after.dependencies[0].id==derived_before.dependencies[0].id);
        assert(derived_after.dependencies[0].value==derived_before.dependencies[0].value);
        assert(derived_after.dependencies[0].revision==derived_before.dependencies[0].revision);
        assert(derived_after.supporting_constraints==derived_before.supporting_constraints);
        assert(w->ResolvedState(StateField::LOCATION,1).present);
    } else if (test == 8) {
        w->stage=1; c->location=1;
        w->tasks.push_back(Goal("open",c));
        const CandidatePlan plan=w->PreviewCandidatePlan(0);
        assert(plan.dry_run_succeeded);
        bool projected_action_fact=false;
        for (const auto& e : plan.evidence)
            if (e.object_id==2 && e.fact=="container_state" &&
                e.source=="action_success" && e.verified)
                projected_action_fact=true;
        assert(projected_action_fact);
        assert(ScoreSemanticsTestAccess::OpenContainer(*w));
        assert(w->Provenance(StateField::CONTAINER_STATE,2).resolved_value==1);
        assert(w->ContainerSource(2)==EvidenceSource::ACTION_SUCCESS);
        assert(w->GetTerminalSummary().goals==plan.terminal_after.goals);
    } else if (test == 9) {
        s->inside=UNKNOWN; w->SetInsideEvidence(3,false,EvidenceSource::UNKNOWN);
        w->tasks.push_back(Goal("putdown",s));
        assert(w->GetTerminalSummary().goals[0]==TerminalStatus::UNKNOWN);
    } else if (test == 10) {
        w->ParseInfo(Goal("opened",c));
        w->tasks.push_back(Goal("open",c));
        assert(w->Provenance(StateField::CONTAINER_STATE,2).received.source==EvidenceSource::EXPLICIT_INFO);
        assert(!w->IsContainerStateVerified(2));
        assert(w->GetTerminalSummary().goals[0]==TerminalStatus::UNKNOWN);
    } else if (test == 11) {
        assert(ScoreSemanticsTestAccess::MoveRobot(*w));
        assert(w->location==5);
        assert(!w->IsInsideVerified(3));
    } else if (test == 12) {
        w->SetAskResult("at(3,5)");
        assert(ScoreSemanticsTestAccess::AskSmall(*w));
        assert(s->inside==NONE && s->location==5);
        assert(w->Provenance(StateField::INSIDE,3).resolved_value==UNKNOWN);
        assert(w->Provenance(StateField::LOCATION,3).resolved_value==UNKNOWN);
        assert(w->HasContradictoryEvidence(StateField::INSIDE,3));
        assert(w->HasContradictoryEvidence(StateField::LOCATION,3));
    } else if (test == 13) {
        assert(w->ParseEnvSentence("(inside 3 1)"));
        assert(s->inside==UNKNOWN);
        assert(w->HasContradictoryEvidence(StateField::INSIDE,3));
    } else if (test == 14) {
        Instruction must=Goal("inside",s); must.Y.push_back(c);
        w->notnot_infoConstrains.push_back(must);
        w->ApplyMustInConstraintCorrection();
        assert(w->IsInsideVerified(3));
        assert(w->Provenance(StateField::INSIDE,3).support_constraint_index==0);
        w->constraint_eligible.assign(1,false);
        assert(!w->IsInsideVerified(3));
    } else if (test == 15) {
        assert(w->Provenance(StateField::HOLD,0).received.source==EvidenceSource::INITIAL);
        assert(w->Provenance(StateField::PLATE,0).resolved_value==NONE);
        assert(ScoreSemanticsTestAccess::PickUpItem(*w));
        assert(w->Provenance(StateField::HOLD,0).resolved_value==3);
        assert(w->Provenance(StateField::HOLD,0).resolved_verified);
        assert(w->Provenance(StateField::HOLD,0).received.source==EvidenceSource::ACTION_SUCCESS);
    } else if (test == 16) {
        w->notnot_infoConstrains.push_back(Goal("opened",c));
        w->ApplyOpenCloseCorrection();
        assert(w->ResolvedState(StateField::CONTAINER_STATE,2).present);
        assert(w->Provenance(StateField::CONTAINER_STATE,2).supporting_constraints.size()==1);
        w->constraint_eligible.assign(1,false);
        assert(!w->DependenciesCurrent(StateField::CONTAINER_STATE,2));
        assert(!w->ResolvedState(StateField::CONTAINER_STATE,2).present);
        assert(!w->IsContainerStateVerified(2));
    } else if (test == 17) {
        c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);
        w->objects[1]->location=UNKNOWN;
        Instruction near=Goal("near",c); near.Y.push_back(w->objects[1]);
        w->notnot_infoConstrains.push_back(near);
        w->ApplyMustNearConstraintCorrection();
        assert(w->ResolvedState(StateField::LOCATION,1).present);
        assert(w->Provenance(StateField::LOCATION,1).supporting_constraints.size()==1);
        w->constraint_uncertain.assign(1,true);
        assert(!w->ResolvedState(StateField::LOCATION,1).present);
        w->tasks.push_back(Goal("goto",w->objects[1]));
        assert(w->GetTerminalSummary().goals[0]==TerminalStatus::UNKNOWN);
    } else if (test == 18) {
        assert(!w->ResolvedState(StateField::LOCATION,2).present);
        assert(ScoreSemanticsTestAccess::OpenContainer(*w));
        assert(w->ResolvedState(StateField::LOCATION,2).value==1);
        w->DependOn(StateField::LOCATION,2,StateField::LOCATION,2);
        assert(!w->DependenciesCurrent(StateField::LOCATION,2));
        assert(!w->ResolvedState(StateField::LOCATION,2).present);
    }
}
