#include "stage_timing.hpp"
#include "terminal_checker.hpp"
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

// The optional hypothesis view is only used by evaluatePlanningHypothesis.
// All terminal, constraint and score callers use canonical values.
int locationValue(const RDFW& w, const std::shared_ptr<Object>& o, bool hypothesis=false) {
    if (!o) return UNKNOWN;
    return hypothesis ? o->location : w.FactLocation(o->id);
}
int insideValue(const RDFW& w, const std::shared_ptr<SmallObject>& o, bool hypothesis=false) {
    if (!o) return UNKNOWN;
    return hypothesis ? o->inside : w.FactInside(o->id);
}
int containerValue(const RDFW& w, const std::shared_ptr<Container>& o, bool hypothesis=false) {
    if (!o) return UNKNOWN;
    return hypothesis ? o->isOpen : w.FactContainerState(o->id);
}
bool isLocationKnown(const RDFW& w, const std::shared_ptr<Object>& o, bool h=false) {
    return locationValue(w,o,h)!=UNKNOWN;
}
int scoreLocation(const RDFW& w, const std::shared_ptr<Object>& o, bool h=false) {
    if (!o) return UNKNOWN;
    if (h) {
        if (o->id==0) return w.location;
        return o->id < w.score_locations.size() ? w.score_locations[o->id] : o->location;
    }
    return w.ScoreFactLocation(o->id);
}
bool isInsideKnown(const RDFW& w, const std::shared_ptr<SmallObject>& o, bool h=false) {
    return insideValue(w,o,h)!=UNKNOWN;
}
bool isContainerStateKnown(const RDFW& w, const std::shared_ptr<Container>& o, bool h=false) {
    const int state=containerValue(w,o,h); return state==0 || state==1;
}
TerminalStatus boolStatus(bool value) {
    return value ? TerminalStatus::SATISFIED : TerminalStatus::UNSATISFIED;
}

std::vector<std::shared_ptr<Object>> scoreBindings(
    const RDFW& world, const Condition& condition,
    const std::vector<std::shared_ptr<Object>>& planner_bindings) {
    StageTimer timer(StageTiming::BINDING);
    if (condition.sort.empty() && condition.color.empty() &&
        condition.declared_type.empty() && !condition.has_explicit_id)
        return planner_bindings;
    std::vector<std::shared_ptr<Object>> result;
    for (const auto& object : world.objects)
        if (object && object->id > 0 && condition.IsObjectSatisfy(object))
            result.push_back(object);
    return result;
}

TerminalStatus evaluatePair(const RDFW& world, const std::string& behave,
                            const std::shared_ptr<Object>& x,
                            const std::shared_ptr<Object>& y, bool hypothesis=false) {
    if (!x) return TerminalStatus::UNKNOWN;
    const int robot_location=hypothesis?world.location:world.FactLocation(0);
    const int hand=hypothesis?world.hold_id:world.FactValue(StateField::HOLD);
    const int tray=hypothesis?world.plate_id:world.FactValue(StateField::PLATE);
    const bool stored=hand==x->id || tray==x->id;
    const bool not_stored=hypothesis?(hand!=x->id && tray!=x->id):world.IsNotStoredFact(x->id);

    if (behave == "goto" || behave == "move") {
        if (world.stage == 1 || hypothesis)
            return boolStatus(scoreLocation(world, x, hypothesis) != _home::UNKNOWN &&
                              robot_location == scoreLocation(world, x, hypothesis));
        if (!hypothesis && robot_location != _home::UNKNOWN &&
            world.IsAbsentFromSensedLocation(x->id, robot_location))
            return TerminalStatus::UNSATISFIED;
        if (!isLocationKnown(world, x, hypothesis) || robot_location == _home::UNKNOWN)
            return TerminalStatus::UNKNOWN;
        return boolStatus(robot_location == locationValue(world,x,hypothesis));
    }

    if (behave == "open" || behave == "opened" ||
        behave == "close" || behave == "closed") {
        const std::shared_ptr<Object> target = y ? y : x;
        const std::shared_ptr<Container> container =
            std::dynamic_pointer_cast<Container>(target);
        if (!isContainerStateKnown(world, container, hypothesis)) return TerminalStatus::UNKNOWN;
        const bool expect_open = behave == "open" || behave == "opened";
        return boolStatus(static_cast<bool>(containerValue(world,container,hypothesis)) == expect_open);
    }

    if (behave == "pickup") {
        if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id))
            return TerminalStatus::UNKNOWN;
        if (!stored && !not_stored) return TerminalStatus::UNKNOWN;
        return boolStatus(stored);
    }

    if (behave == "putdown") {
        const std::shared_ptr<SmallObject> small =
            std::dynamic_pointer_cast<SmallObject>(x);
        if (!small) return TerminalStatus::UNKNOWN;
        if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id))
            return TerminalStatus::UNKNOWN;
        if (stored)
            return TerminalStatus::UNSATISFIED;
        return not_stored ? TerminalStatus::SATISFIED : TerminalStatus::UNKNOWN;
    }

    if (behave == "putin" || behave == "inside" || behave == "in") {
        const std::shared_ptr<SmallObject> small =
            std::dynamic_pointer_cast<SmallObject>(x);
        if (!small || !y || !isInsideKnown(world, small, hypothesis)) return TerminalStatus::UNKNOWN;
        return boolStatus(insideValue(world,small,hypothesis) == y->id);
    }

    if (behave == "takeout") {
        const std::shared_ptr<SmallObject> small =
            std::dynamic_pointer_cast<SmallObject>(x);
        if (!small || !y || !isInsideKnown(world, small, hypothesis)) return TerminalStatus::UNKNOWN;
        return boolStatus(insideValue(world,small,hypothesis) != y->id);
    }

    if (behave == "puton" || behave == "on" || behave == "near" ||
        behave == "nextto" || behave == "give") {
        std::shared_ptr<Object> target = y;
        if (behave == "give") target = world.human;
        if ((world.stage == 1 || hypothesis) && target &&
            (scoreLocation(world, x, hypothesis) == _home::UNKNOWN ||
             scoreLocation(world, target, hypothesis) == _home::UNKNOWN))
            return TerminalStatus::UNSATISFIED;
        if (!hypothesis && target && isLocationKnown(world, x, hypothesis) &&
            world.IsAbsentFromSensedLocation(target->id, locationValue(world,x,hypothesis)))
            return TerminalStatus::UNSATISFIED;
        if (!hypothesis && target && isLocationKnown(world, target, hypothesis) &&
            world.IsAbsentFromSensedLocation(x->id, locationValue(world,target,hypothesis)))
            return TerminalStatus::UNSATISFIED;
        if (!target || !isLocationKnown(world, x, hypothesis) || !isLocationKnown(world, target, hypothesis))
            return TerminalStatus::UNKNOWN;

        if (behave == "puton" || behave == "give") {
            const std::shared_ptr<SmallObject> small =
                std::dynamic_pointer_cast<SmallObject>(x);
            if (!isInsideKnown(world, small, hypothesis)) return TerminalStatus::UNKNOWN;
            if (stored) return TerminalStatus::UNSATISFIED;
            if (!not_stored) return TerminalStatus::UNKNOWN;
        }
        return boolStatus(scoreLocation(world, x, hypothesis) == scoreLocation(world, target, hypothesis));
    }

    if (behave == "plate") {
        if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id))
            return TerminalStatus::UNKNOWN;
        if (tray==UNKNOWN && !not_stored) return TerminalStatus::UNKNOWN;
        return boolStatus(tray == x->id);
    }

    if (behave == "hold") {
        if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id))
            return TerminalStatus::UNKNOWN;
        if (hand==UNKNOWN && !not_stored) return TerminalStatus::UNKNOWN;
        return boolStatus(hand == x->id);
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

const char* TerminalStatusName(TerminalStatus status) {
    switch (status) {
    case TerminalStatus::SATISFIED: return "SATISFIED";
    case TerminalStatus::UNSATISFIED: return "UNSATISFIED";
    case TerminalStatus::UNKNOWN: return "UNKNOWN";
    }
    return "UNKNOWN";
}

TerminalSummary::TerminalSummary()
    : satisfied_goals(0), unsatisfied_goals(0), unknown_goals(0),
      satisfied_constraints(0), unsatisfied_constraints(0),
      unknown_constraints(0), credited_constraints(0) {
}

bool TerminalSummary::allGoalsSatisfied() const {
    return !goals.empty() && satisfied_goals == goals.size();
}

TerminalStatus TerminalChecker::evaluateTask(
    const RDFW& world, const Instruction& task) const {
    if (!task.IsUsable() || task.X.empty()) return TerminalStatus::UNKNOWN;
    const auto xs = scoreBindings(world, task.conditionX, task.X);
    const auto ys = scoreBindings(world, task.conditionY, task.Y);
    // The SDK selects exactly one grounding with 1{task(...):cond}1,
    // then reads the first answer set. Mixed groundings cannot prove a score.
    TerminalStatus result = TerminalStatus::UNKNOWN;
    bool first = true;
    for (const auto& x : xs) {
        const std::size_t count = ys.empty() ? 1 : ys.size();
        for (std::size_t i = 0; i < count; ++i) {
            const TerminalStatus next = evaluatePair(world, task.behave, x,
                ys.empty() ? nullptr : ys[i]);
            if (!first && result != next) return TerminalStatus::UNKNOWN;
            result = next;
            first = false;
        }
    }
    return result;
}

TerminalStatus TerminalChecker::evaluateConstraint(
    const RDFW& world, const Instruction& constraint, ConstraintKind kind) const {
    // cons(task) forbids the task's resulting predicate, not the command.
    // Each grounded constraint must hold; negate BEFORE combining bindings.
    if (!constraint.IsUsable() || constraint.X.empty()) return TerminalStatus::UNKNOWN;
    const auto xs = scoreBindings(world, constraint.conditionX, constraint.X);
    const auto ys = scoreBindings(world, constraint.conditionY, constraint.Y);
    TerminalStatus result = TerminalStatus::SATISFIED;
    for (const auto& x : xs) {
        const std::size_t count = ys.empty() ? 1 : ys.size();
        for (std::size_t i = 0; i < count; ++i) {
            TerminalStatus next = evaluatePair(world, constraint.behave, x,
                ys.empty() ? nullptr : ys[i]);
            if (kind != ConstraintKind::MUST_HOLD) next = invertStatus(next);
            result = combineStatus(result, next);
        }
    }
    return result;
}

TerminalSummary TerminalChecker::evaluatePlanningHypothesis(const RDFW& world) const {
    TerminalSummary result;
    for (const auto& task:world.tasks) {
        TerminalStatus status=TerminalStatus::UNKNOWN;
        bool first=true;
        bool mixed=false;
        if (task.IsUsable()) for (auto x:scoreBindings(world,task.conditionX,task.X)) {
            const auto ys=scoreBindings(world,task.conditionY,task.Y);
            for (std::size_t i=0; i<(ys.empty()?1:ys.size()); ++i) {
                const auto next=evaluatePair(world,task.behave,x,ys.empty()?nullptr:ys[i],true);
                if (!first && status!=next) { status=TerminalStatus::UNKNOWN; mixed=true; break; }
                status=next; first=false;
            }
            if (mixed) break;
        }
        result.goals.push_back(status);
    }
    return result;
}

TerminalSummary TerminalChecker::evaluateAll(const RDFW& world) const {
    StageTimer timer(StageTiming::TERMINAL);
    TerminalSummary result = evaluateConstraints(world);
    result.goals.reserve(world.tasks.size());
    for (std::size_t i = 0; i < world.tasks.size(); ++i) {
        const TerminalStatus status = evaluateTask(world, world.tasks[i]);
        result.goals.push_back(status);
        countStatus(status, result.satisfied_goals,
                    result.unsatisfied_goals, result.unknown_goals);
    }

    return result;
}

TerminalSummary TerminalChecker::evaluateConstraints(const RDFW& world) const {
    TerminalSummary result;
    result.constraints.reserve(world.not_infoConstrains.size() +
                               world.notnot_infoConstrains.size() +
                               world.not_taskConstrains.size());
    const bool has_ledger = world.constraint_eligible.size() ==
        world.not_infoConstrains.size() + world.notnot_infoConstrains.size() +
        world.not_taskConstrains.size();
    for (std::size_t i = 0; i < world.not_infoConstrains.size(); ++i) {
        const TerminalStatus status = evaluateConstraint(
            world, world.not_infoConstrains[i], ConstraintKind::MUST_NOT_HOLD);
        result.constraints.push_back(status);
        const bool eligible = !has_ledger || world.constraint_eligible[result.constraints.size()-1];
        result.constraint_eligible.push_back(eligible);
        const bool certain = !has_ledger || world.constraint_uncertain.size() != world.constraint_eligible.size() ||
            !world.constraint_uncertain[result.constraints.size()-1];
        result.constraint_credited.push_back(eligible && certain);
        if (eligible && certain) ++result.credited_constraints;
        countStatus(status, result.satisfied_constraints,
                    result.unsatisfied_constraints, result.unknown_constraints);
    }
    for (std::size_t i = 0; i < world.notnot_infoConstrains.size(); ++i) {
        const TerminalStatus status = evaluateConstraint(
            world, world.notnot_infoConstrains[i], ConstraintKind::MUST_HOLD);
        result.constraints.push_back(status);
        const bool eligible = !has_ledger || world.constraint_eligible[result.constraints.size()-1];
        result.constraint_eligible.push_back(eligible);
        const bool certain = !has_ledger || world.constraint_uncertain.size() != world.constraint_eligible.size() ||
            !world.constraint_uncertain[result.constraints.size()-1];
        result.constraint_credited.push_back(eligible && certain);
        if (eligible && certain) ++result.credited_constraints;
        countStatus(status, result.satisfied_constraints,
                    result.unsatisfied_constraints, result.unknown_constraints);
    }
    for (std::size_t i = 0; i < world.not_taskConstrains.size(); ++i) {
        const TerminalStatus status = evaluateConstraint(
            world, world.not_taskConstrains[i], ConstraintKind::FORBIDDEN_TASK_STATE);
        result.constraints.push_back(status);
        const bool eligible = !has_ledger || world.constraint_eligible[result.constraints.size()-1];
        result.constraint_eligible.push_back(eligible);
        const bool certain = !has_ledger || world.constraint_uncertain.size() != world.constraint_eligible.size() ||
            !world.constraint_uncertain[result.constraints.size()-1];
        result.constraint_credited.push_back(eligible && certain);
        if (eligible && certain) ++result.credited_constraints;
        countStatus(status, result.satisfied_constraints,
                    result.unsatisfied_constraints, result.unknown_constraints);
    }
    return result;
}

} // namespace _home
