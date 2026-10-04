"""One-time development transform; never a release-gate entry point."""
from pathlib import Path
import re, json, hashlib
root=Path(__file__).resolve().parents[2]
base=root/'src1.6.6'; out=root/'src1.6.7'
(out/'docs/BASELINE_SHA256.json').write_text(json.dumps({p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file()},indent=2))
h=(out/'rdfw.hpp').read_text(encoding='utf-8-sig')
anchor='        bool EnsureEvidenceCapacity(unsigned int id);'
addition='''        // Local exception journal, shared by nested mutation APIs. No world scan.
        // Compatibility staging is private and must finish inside this scope.
        class StateMutation {
            struct Row {
                unsigned id;
                int location, inside, on, open;
                StateProvenance loc, in, cont;
                bool lv, iv, cv, inferred;
                EvidenceSource ls, is, cs;
                std::vector<shared_ptr<SmallObject>> members;
            };
            struct SensedRow { int loc; bool sensed; LocationSensedInfo info; };
            RDFW& w;
            StateMutation* root;
            bool touched[MAX_OBJECT_ID+1] = {};
            std::vector<Row> rows;
            std::vector<SensedRow> sensed_rows;
            bool storage_saved=false, ledger_saved=false, aborted=false;
            int hand_id=NONE, tray_id=NONE;
            shared_ptr<SmallObject> hand, tray;
            StateProvenance hp, pp;
            std::vector<bool> eligible, uncertain;
            std::vector<int> score;
            std::size_t revision=0;
            void rollback() noexcept;
        public:
            explicit StateMutation(RDFW& world);
            ~StateMutation() noexcept;
            void touch(unsigned id);
            void storage();
            void sensed(int loc);
            void ledger();
            void cancel() noexcept { root->aborted=true; }
            StateMutation(const StateMutation&)=delete;
            StateMutation& operator=(const StateMutation&)=delete;
        };
        StateMutation* active_mutation=nullptr;
        void StageStateValue(StateField field, unsigned id, int value);
        void AddContainerMembership(const shared_ptr<Container>& container,
                                    const shared_ptr<SmallObject>& item);
'''
assert anchor in h;h=h.replace(anchor,addition+anchor)
(out/'rdfw.hpp').write_text(h,encoding='utf-8')
s=(out/'rdfw.cpp').read_text(encoding='utf-8-sig')
# Scope fact-changing API implementations. Nested scopes reuse the outer journal.
names=['SetHold','SetPlate','ReceiveWeakClaim','MarkUnresolved','DependOn','SetConstraintSupport','MarkDirectLocationEvidence','SetInsideEvidence','SetContainerEvidence','GetSmallObjectStatus','GetBigObjectStatus','SenseCurrentLocationOnly','sense','ClearContainerMembership','ReconcileLocationRelation','ConfirmContainerLocation','ParseInfo','RefreshMustNearConstraintState','ApplyMustInConstraintCorrection','ApplyOpenCloseCorrection','InvalidateSenseAtLocation','UpdateConstraintLedger']
for name in names:
    pattern=r'((?:void|bool) RDFW::'+name+r'\([^{}]*?\)(?:[^\n{]*)\s*\{)'
    s,n=re.subn(pattern,r'\1\n    StateMutation mutation(*this);',s,count=1)
    assert n==1,name
# Action success has its own mutation boundary, after platform success. Avoid
# rolling back facts for earlier, already completed platform calls in a solver.
start=s.index('bool RDFW::TakeOut(unsigned');end=s.index('void RDFW::PrintEnv()',start)
part=s[start:end].replace('if (action_succeeded)\n    {','if (action_succeeded)\n    {\n        StateMutation mutation(*this);')
part=part.replace('    // 6) 成功后的状态更新（全部带边界/判空）','    StateMutation mutation(*this);\n    // 6) 成功后的状态更新（全部带边界/判空）')
s=s[:start]+part+s[end:]
# First-write provenance capture. EnsureEvidenceCapacity does not grant facts.
s=s.replace('StateProvenance& RDFW::MutableProvenance(StateField field, unsigned int id) {','StateProvenance& RDFW::MutableProvenance(StateField field, unsigned int id) {\n    if (active_mutation) {\n        if (field==StateField::HOLD || field==StateField::PLATE) active_mutation->storage();\n        else active_mutation->touch(id);\n    }')
s=s.replace('    Robot::SetHold(item);','    if (item && (!IsValidObjectId(item->id) || objects[item->id]!=item)) return;\n    active_mutation->storage();\n    if (item) active_mutation->touch(item->id);\n    Robot::SetHold(item);')
s=s.replace('    Robot::SetPlate(item);','    if (item && (!IsValidObjectId(item->id) || objects[item->id]!=item)) return;\n    active_mutation->storage();\n    if (item) active_mutation->touch(item->id);\n    Robot::SetPlate(item);')
# Fields are staged through one private journal-aware API, then committed by
# existing evidence wrappers. Initialization and snapshot/restore remain direct.
import sys
sys.path.insert(0,str(base/'tests'))
from importlib.util import spec_from_file_location, module_from_spec
# Avoid importing the old inventory's executable top-level.
audit=(base/'tests/canonical_audit.py').read_text()
ns={};exec(audit[audit.index('def functions_by_line'):audit.index('def classify')],dict(re=re),ns)
owners=ns['functions_by_line'](s)
lines=s.splitlines()
allowed={'BuildTaskGroupPlan','Init','ParseEnvSentence','ParseEnv','Fini'}
for n,line in enumerate(lines,1):
    owner=owners.get(n,'')
    if owner in allowed:continue
    # Actual assignment, not comparison. All object references carry stable ids.
    line=re.sub(r'\b(\w+)(?:->)(location|inside|isOpen)\s*=(?!=)\s*([^;]+);',lambda m:'StageStateValue(StateField::'+{'location':'LOCATION','inside':'INSIDE','isOpen':'CONTAINER_STATE'}[m[2]]+','+m[1]+'->id,'+m[3]+');',line)
    line=re.sub(r'objects\[([^]]+)\]->(location|inside|isOpen)\s*=(?!=)\s*([^;]+);',lambda m:'StageStateValue(StateField::'+{'location':'LOCATION','inside':'INSIDE','isOpen':'CONTAINER_STATE'}[m[2]]+','+m[1]+','+m[3]+');',line)
    lines[n-1]=line
s='\n'.join(lines)+'\n'
# Invalid inside cleanup was an uncommitted solver write; canonical weak clear.
s=s.replace('StageStateValue(StateField::INSIDE,target_small->id,UNKNOWN);','ApplyStateValue(StateField::INSIDE,target_small->id,UNKNOWN,false,EvidenceSource::UNKNOWN);')
# Membership writes are journal aware. Preserve previous DeleteObjectInside
# behavior (erase matching id only), but capture its owning container first.
s=re.sub(r'(\b\w+)->DeleteObjectInside\((\w+)\);',r'if (active_mutation) active_mutation->touch(\1->id);\n        \1->DeleteObjectInside(\2);',s)
s=re.sub(r'(\b\w+)->smallObjectsInside.push_back\((\w+)\);',r'AddContainerMembership(\1,\2);',s)
# Clear/explicit erase: capture before modifying any member vector.
s=s.replace('auto& items = container->smallObjectsInside;','auto& items = container->smallObjectsInside;\n        if (std::any_of(items.begin(),items.end(),[&](const shared_ptr<SmallObject>& p){return p && p->id==small->id;}))\n            active_mutation->touch(container->id);')
s=s.replace('auto& vec = old_cont->smallObjectsInside;','active_mutation->touch(old_cont->id);\n                                auto& vec = old_cont->smallObjectsInside;')
s=s.replace('auto& vec = cont->smallObjectsInside;','active_mutation->touch(cont->id);\n                auto& vec = cont->smallObjectsInside;')
s=s.replace('    const std::vector<bool> eligibility_before = constraint_eligible;','    active_mutation->ledger();\n    const std::vector<bool> eligibility_before = constraint_eligible;')
s=s.replace('    posSensedFlag[loc] = false;','    active_mutation->sensed(loc);\n    posSensedFlag[loc] = false;')
s=s.replace('    posSensedFlag[curr_loc] = true;','    active_mutation->sensed(curr_loc);\n    posSensedFlag[curr_loc] = true;')
# API metadata mirrors no longer stage separately before provenance capture.
for arr in ['objectLocationVerified','objectInsideVerified','containerStateVerified','objectLocationSource','objectInsideSource','containerStateSource']:
    s=re.sub(r'^    '+arr+r'\[id\] = (?:verified|source);\n','',s,flags=re.M)
# Prepare capacity atomically (all reserves before nonthrowing size changes).
cap_start=s.index('bool RDFW::EnsureEvidenceCapacity');cap_end=s.index('StateProvenance& RDFW::MutableProvenance',cap_start)
cap=s[cap_start:cap_end];arrays=re.findall(r'if \((\w+)\.size\(\) < required\)',cap)
reserve=''.join('    if ('+a+'.capacity()<required) '+a+'.reserve(required);\n' for a in arrays)
cap=cap.replace('    if (objectLocationVerified.size() < required)',reserve+'    if (objectLocationVerified.size() < required)',1)
s=s[:cap_start]+cap+s[cap_end:]
# RTTI qualification uses raw pointers: same dynamic type test without shared
# reference-count increment/decrement on each query.
qstart=s.index('bool RDFW::ResolutionEligible');qend=s.index('StateClaim RDFW::ResolvedState',qstart)
q=s[qstart:qend];q=re.sub(r'dynamic_pointer_cast<(SmallObject|Container)>\(objects\[([^]]+)\]\)',r'dynamic_cast<\1*>(objects[\2].get())',q)
s=s[:qstart]+q+s[qend:]
# Projection snapshots already exist; restore must use swaps/moves, including
# members. Move ledger initialization after snapshot preparation.
projstart=s.index('    const std::vector<bool> original_constraint_eligible');projend=s.index('    ScopeExit restore_guard(restore_state);',projstart)
p=s[projstart:projend];p=p.replace('    InitializeConstraintLedger();\n','')
p=p.replace('std::vector<int> contents;','std::vector<shared_ptr<SmallObject>> contents;').replace('false, 0, std::vector<int>()','false, 0, std::vector<shared_ptr<SmallObject>>()')
p=re.sub(r'                for \(std::size_t j = 0; j < container->smallObjectsInside.size\(\); \+\+j\)\n                    if \(container->smallObjectsInside\[j\]\)\n                        state.contents.push_back\(container->smallObjectsInside\[j\]->id\);','                state.contents = container->smallObjectsInside;',p)
p=p.replace('object_states[i] = state;','object_states[i] = std::move(state);')
p=re.sub(r'const (std::vector<[^;]+?>|StateProvenance|CandidatePlan|TerminalSummary|DecisionFeedback) (saved_\w+)',r'\1 \2',p)
# All saved compound types can safely move, including nested vectors and strings.
p=re.sub(r'^(        \w+ = )(saved_\w+);',r'\1std::move(\2);',p,flags=re.M)
begin=p.index('            container->smallObjectsInside.clear();');finish=p.index('\n        }',begin)
p=p[:begin]+'            container->smallObjectsInside.swap(object_states[i].contents);'+p[finish:]
s=s[:projstart]+p+s[projend:]
s=s.replace('    ScopeExit restore_guard(restore_state);','    ScopeExit restore_guard(restore_state);\n    InitializeConstraintLedger();',1)
(out/'rdfw.cpp').write_text(s,encoding='utf-8')
c=(out/'canonical_state.cpp').read_text()
c=c.replace('    if (id >= objects.size() || !objects[id] || !EnsureEvidenceCapacity(id)) return;','    StateMutation mutation(*this);\n    if (id >= objects.size() || !objects[id] || !EnsureEvidenceCapacity(id)) return;\n    active_mutation->touch(id);')
c=c.replace('objects[id]->location = value;','StageStateValue(field,id,value);').replace('item->inside = value;','StageStateValue(field,id,value);').replace('container->isOpen = value;','StageStateValue(field,id,value);')
c=c.replace('container->smallObjectsInside.push_back(item);','AddContainerMembership(container,item);')
(out/'canonical_state.cpp').write_text(c,encoding='utf-8')
