"""Migrate synthetic state inputs; preserve assertions and policies except the
explicit legacy-source assertion now inspects received evidence metadata."""
from pathlib import Path
r=Path(__file__).resolve().parent
def change(name,pairs):
    p=r/name;s=p.read_text(encoding='utf-8')
    for old,new in pairs:
        assert old in s,(name,old);s=s.replace(old,new)
    p.write_text(s,encoding='utf-8')
change('three_a_tests.cpp',[
('world->containerStateVerified[2] = false;', 'world->MarkUnresolved(StateField::CONTAINER_STATE,2);'),
('world->containerStateVerified[2] = true;', 'world->ApplyStateValue(StateField::CONTAINER_STATE,2,0,true,EvidenceSource::SENSE);'),
('world->location = 3;', 'world->ApplyStateValue(StateField::LOCATION,0,3,true,EvidenceSource::ACTION_SUCCESS);')])
change('recovery_evidence_tests.cpp',[
('changed->objects[2]->location = 4;', 'changed->ApplyStateValue(StateField::LOCATION,2,4,true,EvidenceSource::SENSE);')])
change('interval_gate_tests.cpp',[
('std::dynamic_pointer_cast<Container>(w->objects[1])->isOpen = true;', 'w->ApplyStateValue(StateField::CONTAINER_STATE,1,1,true,EvidenceSource::SENSE);')])
change('score_semantics_tests.cpp',[
('w->containerStateVerified[2] = false;', 'w->MarkUnresolved(StateField::CONTAINER_STATE,2);'),
('w->containerStateVerified[2] = true;\n    std::dynamic_pointer_cast<Container>(w->objects[2])->isOpen = 1;', 'w->ApplyStateValue(StateField::CONTAINER_STATE,2,1,true,EvidenceSource::SENSE);'),
('w->containerStateSource[2] = EvidenceSource::CONSTRAINT_DERIVED;\n    std::dynamic_pointer_cast<Container>(w->objects[2])->isOpen = 0;', 'w->ApplyStateValue(StateField::CONTAINER_STATE,2,0,true,EvidenceSource::CONSTRAINT_DERIVED);')])
change('state_invariant_tests.cpp',[
('w->SetHold(s); w->objectInsideVerified[3]=true;', 'w->SetHold(s,EvidenceSource::INITIAL); w->SetInsideEvidence(3,true,EvidenceSource::SENSE);'),
('        w->objectInsideVerified[3]=true;\n        w->ParseInfo(Task("on",s,c));', '        w->SetInsideEvidence(3,true,EvidenceSource::SENSE);\n        w->ParseInfo(Task("on",s,c));'),
('s->inside=UNKNOWN; w->objectInsideVerified[3]=false;', 'w->ApplyStateValue(StateField::INSIDE,3,UNKNOWN,false,EvidenceSource::UNKNOWN);')])
