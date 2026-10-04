"""Line inventory, with function-level semantic classification; no edits/deletes."""
import re, json, hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[2]
out = root / 'src1.6.6/docs'
pattern = re.compile(r'\b(location|inside|isOpen|hold|plate|hold_id|plate_id|\w*Source|\w*Verified|objectLocationInferredByMustNear|\w*Provenance|ResolvedState|DependenciesCurrent|Fact\w*|IsStoredFact|IsNotStoredFact|TaskFactSatisfied)\b')
mutation = re.compile(r'ParseEnv|ParseInfo|Mark|Set|UpdateProvenance|Receive|DependOn|Confirm|Reconcile|ClearContainer|Sense|Apply|RefreshMustNear|Initialize|Ensure|Fini|^(Move|PickUp|PutDown|Open|Close|PutIn|TakeOut|FromPlate|ToPlate)$')
fact = re.compile(r'Is.*Verified|ResolvedState|ResolutionEligible|DependenciesCurrent|Fact|evaluatePair|isLocationKnown|isInsideKnown|isContainerStateKnown|scoreLocation|locationValue|insideValue|containerValue|CaptureCandidateEvidence')
debug = re.compile(r'BuildTaskGroupPlan|PlanStateSignature|Print|ToString|Debug')

def functions_by_line(source):
    # Mask literals/comments while retaining exact offsets and newlines. Only
    # signatures followed by a function body are accepted; calls never rename
    # the enclosing function. Control blocks and lambdas retain their owner.
    mask = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                  lambda m: ''.join('\n' if c=='\n' else ' ' for c in m[0]), source)
    signatures = re.compile(r'^[ \t]*(?:[\w:<>,*&~]+[ \t\r\n]+)*(?:\w+::)*([A-Za-z_]\w*)[ \t]*\([^;{}]*\)[ \t\r\n]*(?:const[ \t\r\n]*)?(?:override[ \t\r\n]*)?(?:noexcept[ \t\r\n]*)?(?::[^;{}]*)?\{', re.M)
    owners = {}
    for match in signatures.finditer(mask):
        name = match[1]
        if name in ('if','for','while','switch','catch'): continue
        depth = 1
        end = match.end()
        while end < len(mask) and depth:
            if mask[end]=='{': depth += 1
            elif mask[end]=='}': depth -= 1
            end += 1
        start_line = source.count('\n',0,match.start())+1
        end_line = source.count('\n',0,end)+1
        for n in range(start_line,end_line+1): owners[n]=name
    return owners

def classify(version,path,function,line,nearby):
    after = version=='src1.6.6'
    test = 'tests' in path.parts
    if test or debug.search(function) or line.lstrip().startswith(('//','/*','*')):
        return 'D',True,False,'fixture, documentation, snapshot/restore/debug; no independent truth'
    if path.suffix in ('.h','.hpp') and function=='declaration/inline':
        return 'D',True,False,'state/API declaration; role documented in semantic review'
    if function in ('Provenance','LocationSource','InsideSource','ContainerSource'):
        return 'D',True,False,'metadata accessor; does not grant world-fact qualification'
    value_write = re.search(r'\b(?:location|inside|isOpen|hold_id|plate_id)\s*=(?!=)|\b\w*(?:Source|Verified)\s*\[[^]]+\]\s*=(?!=)',line)
    if mutation.search(function) or value_write or function in ('sense','DependOn','RecordConstraintSupports','MutableProvenance','Init','Object','SmallObject','BigObject','Container','Robot'):
        broken = not after and function in ('SetHold','SetPlate','MarkUnresolved','ApplyMustInConstraintCorrection','Fini','sense','Move')
        return 'C',not broken,broken,'mutation implementation; metadata synchronization reviewed by function'
    if path.name in ('terminal_checker.cpp','legacy_priority.cpp'):
        raw = re.search(r'(?:->|\.)(?:location|inside|isOpen|hold_id|plate_id)\b',line)
        if after and raw:
            return 'A',True,False,'explicit hypothesis branch only; defaults use canonical values (see final review)'
        return 'B',after,not after,'terminal/priority fact consumer; canonical value and qualification required'
    if fact.search(function) or re.search(r'\b(?:Fact\w*|TaskFactSatisfied|IsStoredFact|IsNotStoredFact)\s*\(',line):
        return 'B',after,not after,'canonical query/adapter or fact-consuming call; reviewed with dependencies'
    if function.startswith('SolveTask') or function in ('HoldSmallObject','TakeOutLogic'):
        if not after and 'return true' in nearby:
            return 'B',False,True,'early-return candidate: requires manual completion-vs-action review'
        return 'A',True,False,'solver route/capacity/action-selection hypothesis; completion uses canonical API'
    return 'A',True,False,'planning candidate/risk/route read; mixed-function semantic review applies'
def scan(version):
    rows=[]
    for path in sorted((root/version).rglob('*')):
        if path.suffix not in ('.cpp','.hpp','.h'): continue
        source=path.read_text(encoding='utf-8-sig')
        owners=functions_by_line(source)
        lines=source.splitlines()
        for n,line in enumerate(lines,1):
            function=owners.get(n,'declaration/inline')
            fields=pattern.findall(line)
            if not fields: continue
            kind,safe,modify,note=classify(version,path,function,line,' '.join(lines[n-1:n+2]))
            rows.append(dict(file=path.relative_to(root).as_posix(),line=n,function=function,fields=sorted(set(fields)),kind=kind,safe=safe,modify=modify,code=line.strip(),reason=note))
    return rows
version=__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'src1.6.5'
rows=scan(version)
tag='BEFORE' if version=='src1.6.5' else 'AFTER'
(out/('DIRECT_ACCESS_'+tag+'.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# Direct access inventory '+tag,'','A hypothesis; B fact query; C mutation; D serialization/restore/debug.','Functions are tracked by definition/body scope; mixed-function classifications are completed in CANONICAL_AUDIT_REVIEW.md / CANONICAL_AUDIT_FINAL.md.','Safe/Modify are review triage; each JSON row also records its semantic reason.','', '| File:line | Function | Fields | Type | Safe | Modify | Code |','|---|---|---|---|---|---|---|']
for r in rows: lines.append('| {file}:{line} | {function} | {fields} | {kind} | {safe} | {modify} | {code} |'.format(**dict(r,fields=','.join(r['fields']),code=r['code'].replace('|','\\|'))))
(out/('DIRECT_ACCESS_'+tag+'.md')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
if tag=='BEFORE' and not (out/'BASELINE_SHA256.json').exists():
    hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/version).rglob('*') if p.is_file()}
    (out/'BASELINE_SHA256.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
print(tag,len(rows),'access lines')
