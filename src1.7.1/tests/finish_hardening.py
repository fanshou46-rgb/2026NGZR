from pathlib import Path
import re
v=Path(__file__).resolve().parents[1]
s=(v/'rdfw.cpp').read_text()
s=s.replace('if (old_cont) if (active_mutation) active_mutation->touch(old_cont->id);\n        old_cont->DeleteObjectInside(small);','if (old_cont) { active_mutation->touch(old_cont->id); old_cont->DeleteObjectInside(small); }')
s=s.replace('if (old_container) if (active_mutation) active_mutation->touch(old_container->id);\n        old_container->DeleteObjectInside(small);','if (old_container) { active_mutation->touch(old_container->id); old_container->DeleteObjectInside(small); }')
# Eliminate standalone staging in solver feedback; API is atomic on its own.
for obj,id,val in [('target_cont','cont','true'),('cnt','a','true'),('cnt','a','false'),('target_cont','b','true')]:
    pattern=r'StageStateValue\(StateField::CONTAINER_STATE,'+obj+r'->id,'+val+r'\);\n\s*EnsureEvidenceCapacity\('+id+r'\);\n\s*SetContainerEvidence\('+id+r', true, EvidenceSource::ACTION_FAILURE\);'
    s,n=re.subn(pattern,'ApplyStateValue(StateField::CONTAINER_STATE,'+id+','+val+',true,EvidenceSource::ACTION_FAILURE);',s)
    assert n==1,(obj,id,val)
s=s.replace('                if (active_mutation) active_mutation->touch(target_cont->id);\n        target_cont->DeleteObjectInside(small_object);\n                StageStateValue(StateField::INSIDE,small_object->id,UNKNOWN);\n                EnsureEvidenceCapacity(small);\n                SetInsideEvidence(small, false, EvidenceSource::SENSE);','                ApplyStateValue(StateField::INSIDE,small,UNKNOWN,false,EvidenceSource::SENSE);')
# Ledger initialization must prepare both arrays before committing either.
s=s.replace('    constraint_eligible.assign(count, true);\n    constraint_uncertain.assign(count, false);','    std::vector<bool> e(count,true), u(count,false);\n    constraint_eligible.swap(e); constraint_uncertain.swap(u);')
s=s.replace('    InitializeConstraintLedger();\n    active_mutation->ledger();','    active_mutation->ledger();\n    InitializeConstraintLedger();')
# ParseEnv accepted direct initialization must journal membership helper scope;
# no runtime fact journal spans object graph creation/type replacement.
s=s.replace('if (!listed) AddContainerMembership(p,s);','if (!listed) p->smallObjectsInside.push_back(s);')
(v/'rdfw.cpp').write_text(s)
for filename in ['CMakeLists.txt','tests/CMakeLists.txt']:
    p=v/filename;s=p.read_text().replace('canonical_state.cpp','state_mutation.cpp canonical_state.cpp').replace('VERSION 1.6.6','VERSION 1.6.7')
    if filename.startswith('tests'):s=s.replace('../state_mutation.cpp canonical_state.cpp','../state_mutation.cpp ../canonical_state.cpp')
    p.write_text(s)
