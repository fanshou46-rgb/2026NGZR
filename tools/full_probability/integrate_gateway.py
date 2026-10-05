"""One-time integration, assertions prevent partial or repeated rewriting."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'experiments/full_probability/source'
p=S/'rdfw.cpp';s=p.read_text(encoding='utf8')
names=['AskLoc','SenseCurrentLocationOnly','sense','TakeOut','PutIn','Close','Open','FromPlate','ToPlate','PutDown','PickUp','Move']
for name in names:
    import re
    pattern=r'((?:std::string|void|bool) RDFW::'+name+r'\([^\n]*\)\s*[^\n{]*\n\{)'
    s,n=re.subn(pattern,r'\1\n    EvidenceActionScope evidence_scope(*this);',s)
    assert n==1,(name,n)
s=s.replace('TimedPlatformCall([&]() { return Plug::','EvidencePlatformCall([&]() { return Plug::')
for var in ('sensed_ids','A_'):
    before='EvidencePlatformCall([&]() { return Plug::Sense('+var+'); });'
    assert before in s
    s=s.replace(before,'EvidencePlatformCall([&]() { Plug::Sense('+var+'); return '+var+'; });')
p.write_text(s,encoding='utf8',newline='\n')
for relative in ('CMakeLists.txt','tests/CMakeLists.txt'):
    p=S/relative;s=p.read_text(encoding='utf8')
    s=s.replace('state_mutation.cpp','execution_evidence.cpp execution_gateway.cpp state_mutation.cpp') if relative=='CMakeLists.txt' else s.replace('../state_mutation.cpp','../execution_evidence.cpp ../execution_gateway.cpp ../state_mutation.cpp')
    if relative.startswith('tests'):
        s+='\nadd_executable(execution_evidence_tests execution_evidence_tests.cpp)\ntarget_link_libraries(execution_evidence_tests rdfw_test_core)\ntarget_compile_options(execution_evidence_tests PRIVATE -UNDEBUG)\nadd_test(NAME execution_evidence COMMAND execution_evidence_tests)\n'
    p.write_text(s,encoding='utf8',newline='\n')
print('SDK gateway integrated; no frozen source edited')
