#include "rdfw.hpp"
#include <algorithm>

using namespace _home;

int RDFW::InsideRelation(unsigned id, unsigned container, bool hypothesis) const {
    if (!IsValidObjectId(id) || !IsValidObjectId(container) ||
        !dynamic_cast<SmallObject*>(objects[id].get()) ||
        !dynamic_cast<Container*>(objects[container].get())) return UNKNOWN;
    const auto& p=Provenance(StateField::INSIDE,id);
    const auto edge=p.inside_edges.find(container);
    if(edge!=p.inside_edges.end() && (edge->second.verified || hypothesis))
        return edge->second.value;
    // Legacy derived evidence retains its dependency/constraint qualifications.
    // It proves this positive edge only, never that all other edges are false.
    const auto scalar=ResolvedState(StateField::INSIDE,id);
    if(scalar.present && scalar.value==static_cast<int>(container)) return 1;
    if(p.inside_complete) return 0;
    if(hypothesis) {
        const auto small=dynamic_cast<SmallObject*>(objects[id].get());
        if(small->inside==static_cast<int>(container)) return 1;
        if(small->inside==NONE) return 0; // a planning hypothesis, not a fact
    }
    return UNKNOWN;
}

void RDFW::SetInsideRelation(unsigned id, unsigned container, int value,
                             bool verified, EvidenceSource source) {
    StateMutation mutation(*this);
    if(!IsValidObjectId(id) || container==0 || container>MAX_OBJECT_ID ||
       (value!=0 && value!=1) || !EnsureEvidenceCapacity(id)) return;
    const auto small=dynamic_pointer_cast<SmallObject>(objects[id]);
    if(!small) return;
    const auto target=container<objects.size()?dynamic_pointer_cast<Container>(objects[container]):nullptr;
    // Initial domain forms can precede the target's type declaration. Readers
    // still validate the completed graph before qualifying any such fact.
    if(!target && source!=EvidenceSource::INITIAL) return;
    auto& p=MutableProvenance(StateField::INSIDE,id);
    auto old=p.inside_edges.find(container);
    if(!verified && old!=p.inside_edges.end() && old->second.verified) return;
    const bool derived=source==EvidenceSource::CONSTRAINT_DERIVED ||
                       source==EvidenceSource::RELATION_DERIVED ||
                       source==EvidenceSource::CONSTRAINT_HEURISTIC;
    const bool independent=verified && !derived;
    const bool changed=old==p.inside_edges.end() || old->second.value!=value ||
                       old->second.verified!=independent || old->second.source!=source;
    p.inside_edges[container]=InsideEdge(value,independent,source);
    if(!shadow_dry_run && pending_execution) p.inside_edges[container].event=pending_execution;
    if(target) {
        active_mutation->touch(container);
        if(value==0) target->DeleteObjectInside(small);
        else if(std::none_of(target->smallObjectsInside.begin(),target->smallObjectsInside.end(),
                            [&](const shared_ptr<SmallObject>& x){return x && x->id==id;}))
            AddContainerMembership(target,small);
    }
    // A new weak edge cannot demote an already qualified scalar resolution,
    // including a constraint-derived one with live dependencies.
    if(!verified && ResolvedState(StateField::INSIDE,id).present) {
        if(changed) ++p.revision;
        return;
    }
    // Keep one representative for old route construction. Authority resides
    // in the edge map; NONE here cannot imply globally empty containment.
    int representative=UNKNOWN; bool representative_verified=false;
    EvidenceSource representative_source=source;
    for(const auto& item:p.inside_edges) if(item.second.value==1) {
        if(representative==UNKNOWN || (item.second.verified && !representative_verified) ||
           (item.second.verified==representative_verified && item.first==container)) {
            representative=item.first; representative_verified=item.second.verified;
            representative_source=item.second.source;
        }
    }
    if(representative==UNKNOWN) {
        representative=NONE; representative_verified=p.inside_complete;
    }
    StageStateValue(StateField::INSIDE,id,representative);
    const unsigned exclusions=p.storage_exclusion;
    const auto hand_event=p.hand_absence_event,tray_event=p.tray_absence_event;
    UpdateProvenance(StateField::INSIDE,id,representative,
                     representative_verified || (verified && derived && value==1),
                     representative_source);
    p.storage_exclusion=exclusions;
    p.hand_absence_event=hand_event;p.tray_absence_event=tray_event;
    if(changed) ++p.revision;
}

void RDFW::SetStorageExclusions(unsigned id,unsigned bits,std::size_t retained_tray_event) {
    auto& p=MutableProvenance(StateField::INSIDE,id);
    p.storage_exclusion=bits;
    p.hand_absence_event=(bits&1u)?pending_execution:0;
    p.tray_absence_event=(bits&2u)?(retained_tray_event?retained_tray_event:pending_execution):0;
}
