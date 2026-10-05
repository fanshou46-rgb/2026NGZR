#include "legacy_priority.hpp"
#include "rdfw.hpp"

#include <memory>
#include <string>

namespace _home {
namespace {

TerminalStatus invertStatus(TerminalStatus status) {
    if (status == TerminalStatus::SATISFIED) return TerminalStatus::UNSATISFIED;
    if (status == TerminalStatus::UNSATISFIED) return TerminalStatus::SATISFIED;
    return TerminalStatus::UNKNOWN;
}

TerminalStatus combineStatus(TerminalStatus aggregate, TerminalStatus next) {
    if (aggregate == TerminalStatus::UNSATISFIED || next == TerminalStatus::UNSATISFIED)
        return TerminalStatus::UNSATISFIED;
    if (aggregate == TerminalStatus::UNKNOWN || next == TerminalStatus::UNKNOWN)
        return TerminalStatus::UNKNOWN;
    return TerminalStatus::SATISFIED;
}

bool isLocationKnown(const RDFW& w, const std::shared_ptr<Object>& o, bool h) {
    return o && (h?o->location:w.FactLocation(o->id))!=UNKNOWN;
}
bool isInsideKnown(const RDFW& w, const std::shared_ptr<SmallObject>& o, bool h) {
    return o && (h?o->inside:w.FactInside(o->id))!=UNKNOWN;
}
bool isContainerStateKnown(const RDFW& w, const std::shared_ptr<Container>& o, bool h) {
    return o && (h?o->isOpen:w.FactContainerState(o->id))!=UNKNOWN;
}
TerminalStatus boolStatus(bool value) {
    return value ? TerminalStatus::SATISFIED : TerminalStatus::UNSATISFIED;
}

TerminalStatus evaluatePair(const RDFW& world, const std::string& behave,
                            const std::shared_ptr<Object>& x,
                            const std::shared_ptr<Object>& y, bool hypothesis) {
    if (!x) return TerminalStatus::UNKNOWN;

    if (behave == "goto" || behave == "move") {
        if (!hypothesis && (hypothesis?world.location:world.FactLocation(0)) != _home::UNKNOWN &&
            world.IsAbsentFromSensedLocation(x->id, (hypothesis?world.location:world.FactLocation(0))))
            return TerminalStatus::UNSATISFIED;
        if (!isLocationKnown(world, x, hypothesis) || (hypothesis?world.location:world.FactLocation(0)) == _home::UNKNOWN)
            return TerminalStatus::UNKNOWN;
        return boolStatus((hypothesis?world.location:world.FactLocation(0)) == (hypothesis?x->location:world.FactLocation(x->id)));
    }

    if (behave == "open" || behave == "opened" ||
        behave == "close" || behave == "closed") {
        const std::shared_ptr<Object> target = y ? y : x;
        const std::shared_ptr<Container> container =
            std::dynamic_pointer_cast<Container>(target);
        if (!isContainerStateKnown(world, container, hypothesis)) return TerminalStatus::UNKNOWN;
        const bool expect_open = behave == "open" || behave == "opened";
        return boolStatus(static_cast<bool>((hypothesis?container->isOpen:world.FactContainerState(container->id))) == expect_open);
    }

    if (behave == "pickup") {
        const bool stored = (hypothesis?(world.hold_id==x->id || world.plate_id==x->id):world.IsStoredFact(x->id));
        if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id))
            return TerminalStatus::UNKNOWN;
        if (!hypothesis && !stored && !world.IsNotStoredFact(x->id)) return TerminalStatus::UNKNOWN;
        return boolStatus(stored);
    }

    if (behave == "putdown") {
        const std::shared_ptr<SmallObject> small =
            std::dynamic_pointer_cast<SmallObject>(x);
        if ((hypothesis?(world.hold_id==x->id || world.plate_id==x->id):world.IsStoredFact(x->id)))
            return TerminalStatus::UNSATISFIED;
        if (!isLocationKnown(world, x, hypothesis)) return TerminalStatus::UNKNOWN;
        return TerminalStatus::SATISFIED;
    }

    if (behave == "putin" || behave == "inside" || behave == "in") {
        const std::shared_ptr<SmallObject> small =
            std::dynamic_pointer_cast<SmallObject>(x);
        if (!small || !y) return TerminalStatus::UNKNOWN;
        const int edge=world.InsideRelation(small->id,y->id,hypothesis);
        return edge==UNKNOWN?TerminalStatus::UNKNOWN:boolStatus(edge==1);
    }

    if (behave == "takeout") {
        const std::shared_ptr<SmallObject> small =
            std::dynamic_pointer_cast<SmallObject>(x);
        if (!small || !y) return TerminalStatus::UNKNOWN;
        const int edge=world.InsideRelation(small->id,y->id,hypothesis);
        return edge==UNKNOWN?TerminalStatus::UNKNOWN:boolStatus(edge==0);
    }

    if (behave == "puton" || behave == "on" || behave == "near" ||
        behave == "nextto" || behave == "give") {
        std::shared_ptr<Object> target = y;
        if (behave == "give") target = world.human;
        if (!hypothesis && target && isLocationKnown(world, x, hypothesis) &&
            world.IsAbsentFromSensedLocation(target->id, (hypothesis?x->location:world.FactLocation(x->id))))
            return TerminalStatus::UNSATISFIED;
        if (!hypothesis && target && isLocationKnown(world, target, hypothesis) &&
            world.IsAbsentFromSensedLocation(x->id, (hypothesis?target->location:world.FactLocation(target->id))))
            return TerminalStatus::UNSATISFIED;
        if (!target || !isLocationKnown(world, x, hypothesis) || !isLocationKnown(world, target, hypothesis))
            return TerminalStatus::UNKNOWN;

        if (behave == "puton" || behave == "on" || behave == "give") {
            const std::shared_ptr<SmallObject> small =
                std::dynamic_pointer_cast<SmallObject>(x);
                if ((hypothesis?(world.hold_id==x->id || world.plate_id==x->id):world.IsStoredFact(x->id)))
                return TerminalStatus::UNSATISFIED;
            }
        return boolStatus((hypothesis?x->location:world.FactLocation(x->id)) == (hypothesis?target->location:world.FactLocation(target->id)));
    }

    if (behave == "plate") {
        if (hypothesis) return boolStatus(world.plate_id==x->id);
        if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id))
            return TerminalStatus::UNKNOWN;
        return (hypothesis?world.plate_id:world.FactValue(StateField::PLATE))==UNKNOWN && !world.IsNotStoredFact(x->id) ? TerminalStatus::UNKNOWN : boolStatus((hypothesis?world.plate_id:world.FactValue(StateField::PLATE)) == x->id);
    }

    if (behave == "hold") {
        if (hypothesis) return boolStatus(world.hold_id==x->id);
        if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id))
            return TerminalStatus::UNKNOWN;
        return (hypothesis?world.hold_id:world.FactValue(StateField::HOLD))==UNKNOWN && !world.IsNotStoredFact(x->id) ? TerminalStatus::UNKNOWN : boolStatus((hypothesis?world.hold_id:world.FactValue(StateField::HOLD)) == x->id);
    }

    return TerminalStatus::UNKNOWN;
}

void countStatus(TerminalStatus status, std::size_t& satisfied,
                 std::size_t& unsatisfied, std::size_t& unknown) {
    if (status == TerminalStatus::SATISFIED) ++satisfied;
    else if (status == TerminalStatus::UNSATISFIED) ++unsatisfied;
    else ++unknown;
}

} // namespace

TerminalStatus LegacyPriorityChecker::evaluatePredicate(
    const RDFW& world, const Instruction& instruction, bool hypothesis) const {
    if (!hypothesis) return TerminalChecker().evaluateTask(world,instruction);
    if (!instruction.IsUsable() || instruction.X.empty())
        return TerminalStatus::UNKNOWN;

    TerminalStatus aggregate = TerminalStatus::SATISFIED;
    for (std::size_t xi = 0; xi < instruction.X.size(); ++xi) {
        if (instruction.Y.empty()) {
            aggregate = combineStatus(
                aggregate,
                evaluatePair(world, instruction.behave, instruction.X[xi], nullptr, hypothesis));
        } else {
            for (std::size_t yi = 0; yi < instruction.Y.size(); ++yi) {
                aggregate = combineStatus(
                    aggregate,
                    evaluatePair(world, instruction.behave,
                                 instruction.X[xi], instruction.Y[yi], hypothesis));
            }
        }
    }
    return aggregate;
}

TerminalStatus LegacyPriorityChecker::evaluateTask(
    const RDFW& world, const Instruction& task, bool hypothesis) const {
    return evaluatePredicate(world, task, hypothesis);
}

TerminalStatus LegacyPriorityChecker::evaluateConstraint(
    const RDFW& world, const Instruction& constraint, ConstraintKind kind, bool hypothesis) const {
    // A prohibited action is a trajectory property.  A current World State cannot
    // prove that it was never executed, so deterministic terminal evaluation is UNKNOWN.
    if (kind == ConstraintKind::FORBIDDEN_TASK_STATE) return TerminalStatus::UNKNOWN;
    const TerminalStatus predicate = evaluatePredicate(world, constraint, hypothesis);
    return kind == ConstraintKind::MUST_NOT_HOLD ? invertStatus(predicate) : predicate;
}

TerminalSummary LegacyPriorityChecker::evaluateAll(const RDFW& world, bool hypothesis) const {
    TerminalSummary result;
    result.goals.reserve(world.tasks.size());
    for (std::size_t i = 0; i < world.tasks.size(); ++i) {
        const TerminalStatus status = evaluateTask(world, world.tasks[i], hypothesis);
        result.goals.push_back(status);
        countStatus(status, result.satisfied_goals,
                    result.unsatisfied_goals, result.unknown_goals);
    }

    result.constraints.reserve(world.not_infoConstrains.size() +
                               world.notnot_infoConstrains.size() +
                               world.not_taskConstrains.size());
    const bool has_ledger = world.constraint_eligible.size() ==
        world.not_infoConstrains.size() + world.notnot_infoConstrains.size() +
        world.not_taskConstrains.size();
    for (std::size_t i = 0; i < world.not_infoConstrains.size(); ++i) {
        const TerminalStatus status = evaluateConstraint(
            world, world.not_infoConstrains[i], ConstraintKind::MUST_NOT_HOLD, hypothesis);
        result.constraints.push_back(status);
        const bool eligible = !has_ledger || world.constraint_eligible[result.constraints.size()-1];
        result.constraint_eligible.push_back(eligible);
        result.constraint_credited.push_back(eligible && status == TerminalStatus::SATISFIED);
        if (eligible && status == TerminalStatus::SATISFIED) ++result.credited_constraints;
        countStatus(status, result.satisfied_constraints,
                    result.unsatisfied_constraints, result.unknown_constraints);
    }
    for (std::size_t i = 0; i < world.notnot_infoConstrains.size(); ++i) {
        const TerminalStatus status = evaluateConstraint(
            world, world.notnot_infoConstrains[i], ConstraintKind::MUST_HOLD, hypothesis);
        result.constraints.push_back(status);
        const bool eligible = !has_ledger || world.constraint_eligible[result.constraints.size()-1];
        result.constraint_eligible.push_back(eligible);
        result.constraint_credited.push_back(eligible && status == TerminalStatus::SATISFIED);
        if (eligible && status == TerminalStatus::SATISFIED) ++result.credited_constraints;
        countStatus(status, result.satisfied_constraints,
                    result.unsatisfied_constraints, result.unknown_constraints);
    }
    for (std::size_t i = 0; i < world.not_taskConstrains.size(); ++i) {
        const TerminalStatus status = evaluateConstraint(
            world, world.not_taskConstrains[i], ConstraintKind::FORBIDDEN_TASK_STATE, hypothesis);
        result.constraints.push_back(status);
        const bool eligible = !has_ledger || world.constraint_eligible[result.constraints.size()-1];
        result.constraint_eligible.push_back(eligible);
        result.constraint_credited.push_back(eligible);
        // A prohibited action remains eligible until that action occurs.
        if (eligible) ++result.credited_constraints;
        countStatus(status, result.satisfied_constraints,
                    result.unsatisfied_constraints, result.unknown_constraints);
    }
    return result;
}

} // namespace _home
