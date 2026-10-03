from pathlib import Path
import re
r=Path(__file__).resolve().parents[1]
p=r/'legacy_priority.hpp';s=p.read_text(encoding='utf-8')
s=s.replace('const Instruction&)','const Instruction&, bool hypothesis = false)').replace('ConstraintKind)','ConstraintKind, bool hypothesis = false)').replace('evaluateAll(const RDFW&)','evaluateAll(const RDFW&, bool hypothesis = false)')
p.write_text(s,encoding='utf-8')
p=r/'legacy_priority.cpp';s=p.read_text(encoding='utf-8')
s=s.replace('const std::shared_ptr<Object>& o)', 'const std::shared_ptr<Object>& o, bool h)').replace('const std::shared_ptr<SmallObject>& o)', 'const std::shared_ptr<SmallObject>& o, bool h)').replace('const std::shared_ptr<Container>& o)', 'const std::shared_ptr<Container>& o, bool h)')
s=s.replace('w.FactLocation(o->id)','(h?o->location:w.FactLocation(o->id))').replace('w.FactInside(o->id)','(h?o->inside:w.FactInside(o->id))').replace('w.FactContainerState(o->id)','(h?o->isOpen:w.FactContainerState(o->id))')
s=s.replace('const std::shared_ptr<Object>& y) {', 'const std::shared_ptr<Object>& y, bool hypothesis) {')
start=s.index('TerminalStatus evaluatePair');end=s.index('void countStatus',start)
part=s[start:end]
part=part.replace('world.FactLocation(x->id)','(hypothesis?x->location:world.FactLocation(x->id))').replace('world.FactLocation(target->id)','(hypothesis?target->location:world.FactLocation(target->id))').replace('world.FactInside(small->id)','(hypothesis?small->inside:world.FactInside(small->id))').replace('world.FactContainerState(container->id)','(hypothesis?container->isOpen:world.FactContainerState(container->id))').replace('world.FactLocation(0)','(hypothesis?world.location:world.FactLocation(0))')
part=part.replace('world.IsStoredFact(x->id)','(hypothesis?(world.hold_id==x->id || world.plate_id==x->id):world.IsStoredFact(x->id))')
part=part.replace('world.FactValue(StateField::HOLD)','(hypothesis?world.hold_id:world.FactValue(StateField::HOLD))').replace('world.FactValue(StateField::PLATE)','(hypothesis?world.plate_id:world.FactValue(StateField::PLATE))')
part=part.replace('world.stage == 2','!hypothesis && world.stage == 2').replace('!stored && !world.IsNotStoredFact', '!hypothesis && !stored && !world.IsNotStoredFact')
for name in ['isLocationKnown','isInsideKnown','isContainerStateKnown']:
    part=re.sub(name+r'\(world, (\w+)\)',name+r'(world, \1, hypothesis)',part)
s=s[:start]+part+s[end:]
s=s.replace('const Instruction& instruction) const', 'const Instruction& instruction, bool hypothesis) const').replace('const Instruction& task) const', 'const Instruction& task, bool hypothesis) const').replace('ConstraintKind kind) const', 'ConstraintKind kind, bool hypothesis) const').replace('evaluateAll(const RDFW& world) const','evaluateAll(const RDFW& world, bool hypothesis) const')
s=s.replace('instruction.X[xi], nullptr)', 'instruction.X[xi], nullptr, hypothesis)').replace('instruction.X[xi], instruction.Y[yi])','instruction.X[xi], instruction.Y[yi], hypothesis)').replace('evaluatePredicate(world, task)','evaluatePredicate(world, task, hypothesis)').replace('evaluatePredicate(world, constraint)','evaluatePredicate(world, constraint, hypothesis)').replace('evaluateTask(world, world.tasks[i])','evaluateTask(world, world.tasks[i], hypothesis)').replace('ConstraintKind::MUST_NOT_HOLD);','ConstraintKind::MUST_NOT_HOLD, hypothesis);').replace('ConstraintKind::MUST_HOLD);','ConstraintKind::MUST_HOLD, hypothesis);').replace('ConstraintKind::FORBIDDEN_TASK_STATE);','ConstraintKind::FORBIDDEN_TASK_STATE, hypothesis);')
p.write_text(s,encoding='utf-8')
p=r/'rdfw.cpp';s=p.read_text(encoding='utf-8');s=s.replace('        const int original_stage = stage;\n        stage = 1;\n        hypothesis = LegacyPriorityChecker().evaluateAll(*this);\n        stage = original_stage;', '        hypothesis = LegacyPriorityChecker().evaluateAll(*this,true); // planning priority only')
p.write_text(s,encoding='utf-8')
