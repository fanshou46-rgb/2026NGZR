#include "rdfw.hpp"
#include "full_controller.hpp"
#include <sstream>
using namespace _home;

ActionPermit RDFW::MakeActionPermit(const CandidateAction& action) const {
    ActionPermit p;p.action=action.name;p.arguments=action.arguments;
    p.state_signature=PlanStateSignature();p.public_revision=world_revision;
    p.cost=action.cost;p.remaining_ms=deadline_manager.remaining().count();
    p.reserved_ms=plan_safety_margin.count()+action.estimated_duration.count();
    p.selection_reason=guarded_actions_active?"verified_task_group":
        active_probe?"legacy_probe":"legacy_candidate";
    bool qualified=true;
    const auto ref=[&](StateField field,unsigned id,const std::string& predicate,
                       int actual,bool valid) {
        ActionEvidenceRef r;r.predicate=predicate;r.object=id;r.value=actual;
        const auto& provenance=Provenance(field,id);
        r.revision=provenance.revision;r.event=provenance.event;
        r.source=std::to_string(int(provenance.resolved_source));r.confirmed=valid;
        p.evidence.push_back(r);qualified=qualified && valid;
    };
    const auto require=[&](StateField f,unsigned id,int expected,const char* name) {
        const int value=FactValue(f,id);ref(f,id,name,value,value!=UNKNOWN && value==expected);
    };
    const auto at=[&](unsigned id) {
        // ID visibility and containment-derived route hints do not prove at.
        const int v=id?ExplicitAt(id):FactLocation(0);
        if(id && FactValue(StateField::HOLD)==int(id)) {
            require(StateField::HOLD,0,int(id),"confirmed_hand_colocation");return;
        }
        if(id && FactValue(StateField::PLATE)==int(id)) {
            require(StateField::PLATE,0,int(id),"confirmed_tray_colocation");return;
        }
        ref(StateField::LOCATION,id,"independent_at",v,v!=UNKNOWN && v==FactLocation(0));
    };
    ref(StateField::LOCATION,0,"robot_at",FactLocation(0),FactLocation(0)!=UNKNOWN);
    const unsigned a=action.arguments.empty()?0:action.arguments[0];
    const unsigned b=action.arguments.size()<2?0:action.arguments[1];
    const auto typed=[&](unsigned id,bool small) {
        ActionEvidenceRef r;r.object=id;r.predicate=small?"type_small":"type_container";
        r.value=1;r.source="public_domain";r.confirmed=IsValidObjectId(id) &&
            (small?bool(dynamic_cast<SmallObject*>(objects[id].get())):
                   bool(dynamic_cast<Container*>(objects[id].get())));
        p.evidence.push_back(r);qualified=qualified && r.confirmed;
    };
    if(action.name=="Move") {
        ActionEvidenceRef r;r.predicate="legal_location_and_different_destination";
        r.object=a;r.value=int(a);r.source="public_location_domain";
        bool declared=false;
        for(const auto& object:objects)if(object && FactLocation(object->id)==int(a)) {
            const auto source=Provenance(StateField::LOCATION,object->id).resolved_source;
            if(source==EvidenceSource::INITIAL || source==EvidenceSource::EXPLICIT_INFO ||
               source==EvidenceSource::SENSE || source==EvidenceSource::ACTION_SUCCESS)declared=true;
        }
        r.confirmed=declared && a<=unsigned(MAX_LOCATION_ID) && int(a)!=FactLocation(0);
        qualified=qualified&&r.confirmed;p.evidence.push_back(r);
    } else if(action.name=="Sense") {
        // Sense is permitted with unknown object positions and storage.
    } else if(action.name=="AskLoc") {
        ActionEvidenceRef r;r.predicate="public_object";r.object=a;r.value=1;
        r.source="public_domain";r.confirmed=IsValidObjectId(a);
        qualified=qualified&&r.confirmed;p.evidence.push_back(r);
    } else if(action.name=="Open" || action.name=="Close") {
        typed(a,false);require(StateField::HOLD,0,NONE,"empty_hand");at(a);
        require(StateField::CONTAINER_STATE,a,action.name=="Open"?0:1,"door_state");
    } else {
        typed(a,true);
        if(action.name=="PickUp") {
            require(StateField::HOLD,0,NONE,"empty_hand");at(a);
            const int tray=FactValue(StateField::PLATE);
            const bool absent=tray!=UNKNOWN?tray!=int(a):
                bool(Provenance(StateField::INSIDE,a).storage_exclusion&2u);
            if(tray!=UNKNOWN)ref(StateField::PLATE,0,"tray_not_item",tray,absent);
            else {
                ref(StateField::INSIDE,a,"item_absent_from_tray",int(a),absent);
                p.evidence.back().event=Provenance(StateField::INSIDE,a).tray_absence_event;
                p.evidence.back().source="storage_absence_receipt";
            }
        } else if(action.name=="PutDown" || action.name=="ToPlate" || action.name=="PutIn") {
            require(StateField::HOLD,0,int(a),"hand_item");
            if(action.name=="ToPlate")require(StateField::PLATE,0,NONE,"empty_tray");
        } else if(action.name=="FromPlate" || action.name=="TakeOut") {
            require(StateField::HOLD,0,NONE,"empty_hand");
            if(action.name=="FromPlate")require(StateField::PLATE,0,int(a),"tray_item");
        } else qualified=false;
        if(action.name=="PutIn" || action.name=="TakeOut") {
            typed(b,false);at(b);require(StateField::CONTAINER_STATE,b,1,"open_container");
            if(action.name=="TakeOut") {
                const auto& pr=Provenance(StateField::INSIDE,a);
                const int inside=InsideRelation(a,b);
                ref(StateField::INSIDE,a,"inside_"+std::to_string(b),inside,inside==1);
                auto edge=pr.inside_edges.find(b);
                if(edge!=pr.inside_edges.end()) {
                    p.evidence.back().event=edge->second.event;
                    p.evidence.back().source=std::to_string(int(edge->second.source));
                }
            }
        }
    }
    // Existing probes are heuristic candidates, without a complete policy for
    // every physical reply. Do not relabel them as a modeled probe here.
    p.kind=qualified?PermitKind::CONFIRMED:PermitKind::LEGACY_UNQUALIFIED;
    if(full_controller && !full_controller->qualify(p)) {
        LOG_ERROR("[ExecutionEvidence] policy_rejected action=%s args=%zu before=%llu",p.action.c_str(),p.arguments.size(),(unsigned long long)ExecutionEvidence::digest(p.state_signature));
        throw std::logic_error("SDK command is outside selected full-model policy");
    }
    return p;
}
void RDFW::CapturePublicFeedback(bool result) {
    execution_evidence.answer(pending_execution,result?ExecutionStatus::SUCCEEDED:
        ExecutionStatus::FAILED,result?"true":"false");
}
bool RDFW::LearnDoorFromFailure(unsigned container,const char* command) {
    StateMutation mutation(*this);
    // Open/Close=false implies the opposite door state only after every other
    // precondition is proved. ID visibility supplies co-location, not emptiness.
    const ActionReceipt* failed=nullptr;
    for(auto i=execution_evidence.receipts().rbegin();i!=execution_evidence.receipts().rend();++i) {
        if(!i->sent)continue;
        if(i->permit.action=="Sense" || i->permit.action=="AskLoc")continue;
        if(i->outcome==ExecutionStatus::FAILED && i->permit.action==command &&
           i->permit.arguments==std::vector<unsigned>{container})failed=&*i;
        break; // an intervening physical command invalidates this proof
    }
    if(!failed || FactLocation(0)==UNKNOWN || FactLocation(container)!=FactLocation(0))return false;
    bool empty_hand=false,type=false;
    for(const auto& e:failed->permit.evidence) {
        if(e.predicate=="empty_hand" && e.value==NONE && e.confirmed)empty_hand=true;
        if(e.predicate=="type_container" && e.object==container && e.confirmed)type=true;
    }
    if(!empty_hand || !type) {
        LOG("[FailureEvidence] command=%s object=%u verdict=unknown reason=other_preconditions_unproved receipt=%zu\n",command,container,failed->id);
        return false;
    }
    const int opened=std::string(command)=="Open"?1:0;
    ApplyStateValue(StateField::CONTAINER_STATE,container,opened,true,EvidenceSource::ACTION_FAILURE);
    MutableProvenance(StateField::CONTAINER_STATE,container).event=failed->id;
    DependOn(StateField::CONTAINER_STATE,container,StateField::LOCATION,container);
    LOG("[FailureEvidence] command=%s object=%u verdict=confirmed opposite_state=%d receipt=%zu\n",command,container,opened,failed->id);
    return true;
}
void RDFW::CapturePublicFeedback(const std::string& result) {
    execution_evidence.answer(pending_execution,ExecutionStatus::OBSERVED,result);
}
void RDFW::CapturePublicFeedback(const std::vector<unsigned>& result) {
    std::ostringstream raw;raw<<'[';
    for(std::size_t i=0;i<result.size();++i){if(i)raw<<',';raw<<result[i];}raw<<']';
    execution_evidence.answer(pending_execution,ExecutionStatus::OBSERVED,raw.str());
}
void RDFW::FinishEvidenceAction() noexcept {
    if(shadow_dry_run || !pending_execution)return;
    const auto id=pending_execution;
    try {
        if(!execution_evidence.receipt(id).sent) execution_evidence.cancel(id);
        else execution_evidence.commit(id,PlanStateSignature());
        LOG("[ExecutionEvidence] %s\n",ExecutionEvidence::json(execution_evidence.receipt(id),"finalized").c_str());
    } catch(const std::exception& error) {
        LOG_ERROR("execution receipt could not commit: %s",error.what());
        planner_shutdown_requested.store(true);
    }
    pending_execution=0;
}
