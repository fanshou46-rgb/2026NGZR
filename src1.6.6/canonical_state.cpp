#include "rdfw.hpp"
#include <sstream>
#include <algorithm>
using namespace _home;

int RDFW::FactValue(StateField field, unsigned int id) const {
    const StateClaim claim = ResolvedState(field, id);
    return claim.present ? claim.value : UNKNOWN;
}

int RDFW::ScoreFactLocation(unsigned int id) const {
    // Official Stage 1 ASP at facts intentionally exclude inside propagation.
    // This is the scoring representation of canonical location, not a planner read.
    if (stage == 1 && id > 0)
        return FactLocation(id)!=UNKNOWN && id < score_locations.size() ? score_locations[id] : UNKNOWN;
    return FactLocation(id);
}

bool RDFW::IsStoredFact(unsigned int id) const {
    return id > 0 && (FactValue(StateField::HOLD) == static_cast<int>(id) ||
                      FactValue(StateField::PLATE) == static_cast<int>(id));
}

bool RDFW::IsNotStoredFact(unsigned int id) const {
    if (!IsValidObjectId(id) || IsStoredFact(id)) return false;
    const int hand = FactValue(StateField::HOLD), tray = FactValue(StateField::PLATE);
    if (hand != UNKNOWN && tray != UNKNOWN)
        return hand != static_cast<int>(id) && tray != static_cast<int>(id);
    const auto inside = ResolvedState(StateField::INSIDE, id);
    if (!inside.present) return false;
    if (inside.value > 0) return true;
    // A current direct observation of an outside item (or its successful
    // placement) proves absence from storage even when initial empty slots are weak.
    const auto loc = ResolvedState(StateField::LOCATION, id);
    return loc.present && inside.value == NONE &&
        (inside.source == EvidenceSource::SENSE || inside.source == EvidenceSource::ACTION_SUCCESS);
}

bool RDFW::TaskFactSatisfied(const std::string& behave, unsigned int x, unsigned int y) const {
    if (!IsValidObjectId(x) || (y && !IsValidObjectId(y))) return false;
    if (behave == "goto") return FactLocation(0) != UNKNOWN && FactLocation(0) == FactLocation(x);
    if (behave == "pickup") return IsStoredFact(x);
    if (behave == "putdown") return FactInside(x) != UNKNOWN && IsNotStoredFact(x);
    if (behave == "open") return FactContainerState(x) == 1;
    if (behave == "close") return FactContainerState(x) == 0;
    if (behave == "putin") return FactInside(x) != UNKNOWN && FactInside(x) == static_cast<int>(y);
    if (behave == "takeout") return FactInside(x) != UNKNOWN && FactInside(x) != static_cast<int>(y);
    if (behave == "puton" || behave == "give")
        return y && FactInside(x) == NONE && IsNotStoredFact(x) &&
            FactLocation(x) != UNKNOWN && FactLocation(x) == FactLocation(y);
    return false;
}

void RDFW::ApplyStateValue(StateField field, unsigned int id, int value,
                           bool verified, EvidenceSource source) {
    if (id >= objects.size() || !objects[id] || !EnsureEvidenceCapacity(id)) return;
    if (field == StateField::LOCATION) {
        objects[id]->location = value;
        MarkDirectLocationEvidence(id, verified, source);
    } else if (field == StateField::INSIDE) {
        auto item = std::dynamic_pointer_cast<SmallObject>(objects[id]);
        if (!item) return;
        ClearContainerMembership(item);
        item->inside = value;
        if (value > 0) {
            auto container = std::dynamic_pointer_cast<Container>(GetObject(value));
            if (container) container->smallObjectsInside.push_back(item);
        }
        SetInsideEvidence(id, verified, source);
    } else if (field == StateField::CONTAINER_STATE) {
        auto container = std::dynamic_pointer_cast<Container>(objects[id]);
        if (!container) return;
        container->isOpen = value;
        SetContainerEvidence(id, verified, source);
    }
}

std::string RDFW::DebugStateSnapshot() const {
    std::ostringstream out;
    const auto record = [&](StateField field, unsigned int id) {
        const auto& p = Provenance(field,id);
        out << int(field) << ':' << id << ':' << p.resolved_value << ':'
            << int(p.resolved_source) << ':' << p.resolved_verified << ':' << p.revision;
        for (const auto* claim : {&p.received,&p.conflicting})
            out << ':' << claim->present << ',' << claim->value << ',' << int(claim->source);
        out << ':' << p.dependency_count;
        for (unsigned int k=0; k<std::min(p.dependency_count,2u); ++k) {
            const auto& d=p.dependencies[k];
            out << ':' << int(d.field) << ',' << d.id << ',' << d.value << ',' << d.revision;
        }
        out << ':' << p.support_constraint_index << '[';
        for (auto support : p.supporting_constraints) out << support << ',';
        out << "];";
    };
    for (unsigned int id=0; id<objects.size(); ++id) {
        record(StateField::LOCATION,id); record(StateField::INSIDE,id); record(StateField::CONTAINER_STATE,id);
        const auto object=objects[id];
        if (!object) { out << "null;"; continue; }
        out << object->location << ':';
        auto small=std::dynamic_pointer_cast<SmallObject>(object);
        if (small) out << small->inside << ':' << small->on;
        auto cont=std::dynamic_pointer_cast<Container>(object);
        if (cont) { out << cont->isOpen << '['; for (auto item:cont->smallObjectsInside) out << item->id << ','; out << ']'; }
        out << ':' << (id<objectLocationVerified.size() && objectLocationVerified[id])
            << ':' << (id<objectInsideVerified.size() && objectInsideVerified[id])
            << ':' << (id<containerStateVerified.size() && containerStateVerified[id])
            << ':' << int(LocationSource(id)) << ':' << int(InsideSource(id)) << ':' << int(ContainerSource(id))
            << ':' << (id<objectLocationInferredByMustNear.size() && objectLocationInferredByMustNear[id]) << ';';
    }
    record(StateField::HOLD,0); record(StateField::PLATE,0);
    out << location << ':' << hold_id << ':' << plate_id << ':' << (hold?hold->id:0) << ':' << (plate?plate->id:0) << ';';
    for (bool b:constraint_eligible) out << b;
    out << ';'; for (bool b:constraint_uncertain) out << b;
    out << ';'; for (int v:score_locations) out << v << ',';
    return out.str();
}

std::vector<std::string> RDFW::DebugStateConsistency() const {
    std::vector<std::string> errors;
    const auto issue = [&](unsigned id, const char* message) { errors.push_back(std::to_string(id)+":"+message); };
    const auto check = [&](StateField f, unsigned id, int legacy, bool verified, EvidenceSource source) {
        const auto& p=Provenance(f,id); const auto fact=ResolvedState(f,id);
        if (p.resolved_verified != verified || p.resolved_source != source) issue(id,"compatibility metadata");
        if (p.resolved_verified && p.resolved_value != UNKNOWN && legacy != p.resolved_value) issue(id,"resolved/legacy value");
        if (p.resolved_verified && p.resolved_value != UNKNOWN && !ResolutionEligible(f,id)) issue(id,"invalid resolution");
        if (fact.present && (fact.value==UNKNOWN || !DependenciesCurrent(f,id))) issue(id,"invalid fact");
        if (p.dependency_count>2) issue(id,"dependency bound");
    };
    for (unsigned id=0; id<objects.size(); ++id) {
        if (!objects[id]) continue;
        check(StateField::LOCATION,id,objects[id]->location,id<objectLocationVerified.size() && objectLocationVerified[id],LocationSource(id));
        auto small=std::dynamic_pointer_cast<SmallObject>(objects[id]);
        if (small) check(StateField::INSIDE,id,small->inside,id<objectInsideVerified.size() && objectInsideVerified[id],InsideSource(id));
        auto cont=std::dynamic_pointer_cast<Container>(objects[id]);
        if (cont) check(StateField::CONTAINER_STATE,id,cont->isOpen,id<containerStateVerified.size() && containerStateVerified[id],ContainerSource(id));
        if (IsStoredFact(id)) {
            if (!small || FactInside(id)!=NONE || FactLocation(id)!=FactLocation(0)) issue(id,"stored relation");
        }
        if (small && FactInside(id)>0) {
            auto container=std::dynamic_pointer_cast<Container>(GetObject(FactInside(id)));
            if (!container) issue(id,"inside target");
            else if (FactLocation(id)!=UNKNOWN && FactLocation(container->id)!=UNKNOWN && FactLocation(id)!=FactLocation(container->id)) issue(id,"inside location");
        }
        if (cont) for (auto item:cont->smallObjectsInside)
            if (!item || item->inside!=cont->id) issue(id,"membership cache");
    }
    for (StateField f:{StateField::HOLD,StateField::PLATE}) {
        const int legacy=f==StateField::HOLD?hold_id:plate_id;
        const auto ptr=f==StateField::HOLD?hold:plate;
        if ((ptr?ptr->id:NONE)!=(legacy==UNKNOWN?NONE:legacy)) issue(0,"storage pointer");
        const auto& p=Provenance(f,0);
        check(f,0,legacy,p.resolved_verified,p.resolved_source);
    }
    if (holdProvenance.resolved_verified && plateProvenance.resolved_verified &&
        holdProvenance.resolved_value>0 && holdProvenance.resolved_value==plateProvenance.resolved_value) issue(0,"exclusive storage");
    return errors;
}
