"""Full C++ line inventory plus explicit owner-based write closure gate.
The static inventory is evidence for review, not a C++ alias-analysis proof.
"""
from pathlib import Path
import argparse,collections,hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
baseline=ROOT/'src1.6.6'
old=(baseline/'tests/canonical_audit.py').read_text()
ns={};exec(old[old.index('def functions_by_line'):old.index('def classify')],dict(re=re),ns)
owners_for=ns['functions_by_line']
FIELDS=r'location|inside|on|isOpen|hold|plate|hold_id|plate_id|smallObjectsInside|\w*Source|\w*Verified|\w*Provenance|objectLocationInferredByMustNear|received|conflicting|resolved_value|resolved_source|resolved_verified|revision|dependencies|dependency_count|support_constraint_index|supporting_constraints|constraint_eligible|constraint_uncertain|score_locations|posSensedFlag|locationSensedObjects'
pattern=re.compile(r'\b('+FIELDS+r')\b')
write=re.compile(r'\b(?:'+FIELDS+r')\b(?:\[[^;]*?\])?\s*(?:=(?!=)|\+\+|\+=)|\b(?:'+FIELDS+r')\.(?:assign|resize|reserve|clear|push_back|erase|swap)\(')
initial={'Init','Plan','InitializeDynamicArrays','InitializeConstraintLedger','EnsureEvidenceCapacity','EnsureObjectCapacity','EnsureLocationCapacity','EnsureObjectExists','ParseEnv','ParseEnvSentence','Fini','Object','SmallObject','BigObject','Container','Robot','LocationSensedInfo'}
mutation={'SetHold','SetPlate','ReceiveWeakClaim','MarkUnresolved','UpdateProvenance','DependOn','SetConstraintSupport','RecordConstraintSupports','MarkDirectLocationEvidence','SetInsideEvidence','SetContainerEvidence','StageStateValue','AddContainerMembership','ClearContainerMembership','ApplyStateValue','UpdateConstraintLedger','InvalidateSenseAtLocation','SenseCurrentLocationOnly','ParseInfo','RefreshMustNearConstraintState','ApplyMustInConstraintCorrection'}
cache={'BuildMustNearRelations','OptimizeMemoryUsage','GetSmallObjectStatus','GetBigObjectStatus','sense'}
def scan(version):
    rows=[]
    for path in sorted((ROOT/version).rglob('*')):
        if path.suffix not in ('.cpp','.hpp','.h'):continue
        source=path.read_text(encoding='utf-8-sig');owners=owners_for(source)
        for line,code in enumerate(source.splitlines(),1):
            fields=sorted(set(pattern.findall(code)))
            if not fields:continue
            owner=owners.get(line,'declaration/inline')
            masked=re.sub(r'//[^\n]*|"(?:\\.|[^"\\])*"', '',code)
            is_write=bool(write.search(masked))
            if 'tests' in path.parts:category='test_fixture';reason='Isolated test/stub or stress fixture; not linked into competition binary'
            elif code.lstrip().startswith(('//','/*','*')) or (owner=='declaration/inline' and path.suffix!='.cpp'):category='declaration';reason='Declaration, default initializer, or documentation'
            elif path.name=='state_mutation.cpp':category='mutation_journal';reason='Local first-write snapshot / allocation-free rollback / private staging implementation'
            elif owner=='BuildTaskGroupPlan':category='snapshot_restore';reason='Existing dry-run isolation; complete provenance/dependency/member snapshot restored by move/swap'
            elif owner in initial:category='initialization';reason='Graph/type creation, teardown, or capacity/ledger initialization; no second fact authority'
            elif owner=='DeleteObjectInside':category='membership_primitive';reason='Erase-only primitive; runtime callers journal owning container before invocation; no allocation'
            elif is_write and (re.search(r'\bresult\.constraint_eligible\.',masked) or re.search(r'\bconst auto inside\s*=',masked)):category='local_result';reason='Local query result or terminal summary; does not mutate world facts'
            elif 'structuredSource' in fields:category='instruction_metadata';reason='Parser syntax origin flag, not EvidenceSource or canonical world state'
            elif is_write and re.search(r'->on\s*=',code):category='planning_cache';reason='on has no canonical fact semantics; relation is evaluated via location/inside/storage'
            elif owner in mutation:category='canonical_mutation';reason='Canonical API implementation; first write participates in active local journal'
            elif owner in cache and not is_write:category='mutation_consumer';reason='Evidence/relationship wrapper reads candidates; runtime fact writes delegate to canonical API'
            elif is_write:category='UNCLASSIFIED';reason='Requires explicit semantic review'
            else:category='read_access';reason='Planning hypothesis, serialization/debug, or canonical query; consumer boundaries reviewed in MUTATION_CLOSURE.md'
            rows.append(dict(file=path.relative_to(ROOT).as_posix(),line=line,function=owner,fields=fields,write=is_write,category=category,reason=reason,code=code.strip()))
    return rows
def main():
    p=argparse.ArgumentParser();p.add_argument('--version',default='src1.6.7');a=p.parse_args()
    out=ROOT/a.version/'docs';rows=scan(a.version)
    (out/'DIRECT_ACCESS_AFTER.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    counts=collections.Counter(r['category'] for r in rows)
    writes=collections.Counter(r['category'] for r in rows if r['write'])
    result=dict(access_lines=len(rows),write_lines=sum(writes.values()),categories=dict(counts),write_categories=dict(writes),unclassified=[r for r in rows if r['category']=='UNCLASSIFIED'],source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/a.version).iterdir() if p.suffix in ('.cpp','.hpp')})
    (out/'mutation-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    text=['# Direct access inventory','','Categories reflect owner and role; each write is reviewed with the closure report. Aliased vector erases and Robot primitive writes are explicitly covered there.','','| File:line | Function | Write | Category | Code |','|---|---|---|---|---|']
    text += ['| {}:{} | {} | {} | {} | {} |'.format(r['file'],r['line'],r['function'],r['write'],r['category'],r['code'].replace('|','\\|')) for r in rows]
    (out/'DIRECT_ACCESS_AFTER.md').write_text('\n'.join(text)+'\n')
    print(json.dumps(dict(counts=counts,writes=writes,unclassified=result['unclassified']),ensure_ascii=False))
    assert not result['unclassified']
if __name__=='__main__':main()
