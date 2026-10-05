#include "rdfw.hpp"
#include <exception>
#include <algorithm>
#include <stdexcept>
#include <type_traits>
using namespace _home;
static_assert(std::is_nothrow_move_constructible<StateProvenance>::value &&
              std::is_nothrow_move_assignable<StateProvenance>::value,
              "journal rollback must not allocate or throw");

RDFW::StateMutation::StateMutation(RDFW& world) : w(world), root(world.active_mutation) {
    if (!root) { root=this; w.active_mutation=this; }
}
RDFW::StateMutation::~StateMutation() noexcept {
    if (root!=this) return;
    if (aborted || std::uncaught_exception()) rollback();
    w.active_mutation=nullptr;
}
void RDFW::StateMutation::touch(unsigned id) {
    if (root!=this) { root->touch(id); return; }
    if (id>MAX_OBJECT_ID || id>=w.objects.size() || !w.objects[id] || touched[id]) return;
    if (!w.EnsureEvidenceCapacity(id)) return;
    const auto small=dynamic_pointer_cast<SmallObject>(w.objects[id]);
    const auto container=dynamic_pointer_cast<Container>(w.objects[id]);
    Row row;
    row.id=id; row.location=w.objects[id]->location;
    row.inside=small?small->inside:UNKNOWN; row.on=small?small->on:UNKNOWN;
    row.open=container?container->isOpen:UNKNOWN;
    row.loc=w.Provenance(StateField::LOCATION,id);
    row.in=w.Provenance(StateField::INSIDE,id);
    row.cont=w.Provenance(StateField::CONTAINER_STATE,id);
    row.lv=w.objectLocationVerified[id]; row.iv=w.objectInsideVerified[id];
    row.cv=w.containerStateVerified[id]; row.inferred=w.objectLocationInferredByMustNear[id];
    row.ls=w.objectLocationSource[id]; row.is=w.objectInsideSource[id]; row.cs=w.containerStateSource[id];
    if (container) row.members=container->smallObjectsInside;
    rows.push_back(std::move(row)); // all allocation precedes the first write
    touched[id]=true;
}
void RDFW::StateMutation::storage() {
    if (root!=this) { root->storage(); return; }
    if (storage_saved) return;
    StateProvenance h=w.holdProvenance, p=w.plateProvenance;
    hp=std::move(h); pp=std::move(p);
    hand=w.hold; tray=w.plate; hand_id=w.hold_id; tray_id=w.plate_id;
    storage_saved=true;
}
void RDFW::StateMutation::sensed(int loc) {
    if (root!=this) { root->sensed(loc); return; }
    if (loc<0 || std::size_t(loc)>=w.locationSensedObjects.size()) return;
    for (const auto& row:sensed_rows) if (row.loc==loc) return;
    SensedRow row{loc,w.posSensedFlag[loc],w.locationSensedObjects[loc]};
    sensed_rows.push_back(std::move(row));
}
void RDFW::StateMutation::ledger() {
    if (root!=this) { root->ledger(); return; }
    if (ledger_saved) return;
    auto e=w.constraint_eligible, u=w.constraint_uncertain;
    auto s=w.score_locations;
    eligible.swap(e); uncertain.swap(u); score.swap(s);
    revision=w.world_revision; ledger_saved=true;
}
void RDFW::StateMutation::rollback() noexcept {
    // Default allocators, scalar and shared_ptr assignment: restoration allocates
    // nothing, even while the process-wide allocator is still failing.
    for (auto& r:rows) {
        const auto object=w.objects[r.id];
        object->location=r.location;
        if (auto small=dynamic_pointer_cast<SmallObject>(object)) { small->inside=r.inside; small->on=r.on; }
        if (auto container=dynamic_pointer_cast<Container>(object)) {
            container->isOpen=r.open; container->smallObjectsInside.swap(r.members);
        }
        std::swap(w.locationProvenance[r.id],r.loc);
        std::swap(w.insideProvenance[r.id],r.in);
        std::swap(w.containerProvenance[r.id],r.cont);
        w.objectLocationVerified[r.id]=r.lv; w.objectInsideVerified[r.id]=r.iv;
        w.containerStateVerified[r.id]=r.cv; w.objectLocationInferredByMustNear[r.id]=r.inferred;
        w.objectLocationSource[r.id]=r.ls; w.objectInsideSource[r.id]=r.is; w.containerStateSource[r.id]=r.cs;
    }
    if (storage_saved) {
        w.hold=hand; w.plate=tray; w.hold_id=hand_id; w.plate_id=tray_id;
        std::swap(w.holdProvenance,hp); std::swap(w.plateProvenance,pp);
    }
    for (auto& row:sensed_rows) {
        w.posSensedFlag[row.loc]=row.sensed;
        std::swap(w.locationSensedObjects[row.loc],row.info);
    }
    if (ledger_saved) {
        w.constraint_eligible.swap(eligible); w.constraint_uncertain.swap(uncertain);
        w.score_locations.swap(score); w.world_revision=revision;
    }
    if (physical_confirmed) {
        // A committed external action cannot be rolled back. Restore coherent
        // candidate structure, then withdraw stale pre-action fact confidence.
        // Only touched records/slots are invalidated; no scan or allocation.
        const auto withdraw=[](StateProvenance& p) {
            ++p.revision;p.resolved_value=UNKNOWN;p.resolved_source=EvidenceSource::UNKNOWN;
            p.resolved_verified=false;p.storage_exclusion=0;p.hand_absence_event=p.tray_absence_event=0;p.dependency_count=0;p.support_constraint_index=UNKNOWN;
            p.supporting_constraints.clear();p.inside_complete=false;p.explicit_at=UNKNOWN;
            for(auto& edge:p.inside_edges) edge.second.verified=false;
        };
        for (const auto& r:rows) {
            withdraw(w.locationProvenance[r.id]);withdraw(w.insideProvenance[r.id]);withdraw(w.containerProvenance[r.id]);
            w.objectLocationVerified[r.id]=w.objectInsideVerified[r.id]=w.containerStateVerified[r.id]=false;
            w.objectLocationSource[r.id]=w.objectInsideSource[r.id]=w.containerStateSource[r.id]=EvidenceSource::UNKNOWN;
            w.objectLocationInferredByMustNear[r.id]=false;
        }
        withdraw(w.holdProvenance);withdraw(w.plateProvenance);
        for (const auto& r:sensed_rows) {
            w.posSensedFlag[r.loc]=false;
            w.locationSensedObjects[r.loc].object_ids.clear();
            w.locationSensedObjects[r.loc].has_container=false;
            w.locationSensedObjects[r.loc].container_id=NONE;
        }
        // Recovery only: a committed action with unknown completion of the
        // ledger update cannot preserve certain constraint score credit.
        const std::size_t count=w.not_infoConstrains.size()+w.notnot_infoConstrains.size()+w.not_taskConstrains.size();
        if(w.constraint_eligible.size()!=count && eligible.size()==count) w.constraint_eligible.swap(eligible);
        if(w.constraint_uncertain.size()!=count && uncertain.size()==count) w.constraint_uncertain.swap(uncertain);
        std::fill(w.constraint_uncertain.begin(),w.constraint_uncertain.end(),true);
        ++w.world_revision;
    }
}
void RDFW::PrepareActionState(const std::vector<unsigned int>& arguments,bool moving) {
    active_mutation->storage();active_mutation->ledger();InitializeConstraintLedger();
    active_mutation->touch(0);active_mutation->sensed(location);
    if (moving) {
        if(hold) active_mutation->touch(hold->id);
        if(plate) active_mutation->touch(plate->id);
        if(!arguments.empty()) active_mutation->sensed(arguments[0]);
    } else for(unsigned id:arguments) {
        active_mutation->touch(id);
        if(id>=objects.size() || !objects[id]) continue;
        active_mutation->sensed(objects[id]->location);
        if(auto c=dynamic_pointer_cast<Container>(objects[id]))
            for(const auto& item:c->smallObjectsInside) if(item) active_mutation->touch(item->id);
    }
}
void RDFW::StageStateValue(StateField field,unsigned id,int value) {
    if (!active_mutation) throw std::logic_error("state staging without mutation scope");
    if (id>=objects.size() || !objects[id] || !EnsureEvidenceCapacity(id)) return;
    active_mutation->touch(id);
    if (field==StateField::LOCATION) objects[id]->location=value;
    else if (field==StateField::INSIDE) {
        if (auto s=dynamic_pointer_cast<SmallObject>(objects[id])) s->inside=value;
    } else if (field==StateField::CONTAINER_STATE) {
        if (auto c=dynamic_pointer_cast<Container>(objects[id])) c->isOpen=value;
    }
}
void RDFW::AddContainerMembership(const shared_ptr<Container>& container,const shared_ptr<SmallObject>& item) {
    StateMutation mutation(*this);
    if (!container || !item) return;
    active_mutation->touch(container->id);
    container->smallObjectsInside.push_back(item);
}
