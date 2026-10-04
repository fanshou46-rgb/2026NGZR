from pathlib import Path
import re
p=Path(__file__).resolve().parents[1]/'rdfw.cpp'
s=p.read_text(encoding='utf-8')
# Collapse adjacent write+evidence pairs only; staged relation/parse assignments
# are separately reviewed and retained where a multi-field transition is required.
rules=[('location','MarkDirectLocationEvidence','LOCATION'),('inside','SetInsideEvidence','INSIDE'),('isOpen','SetContainerEvidence','CONTAINER_STATE')]
for member,method,field in rules:
    pat=re.compile(r'(?P<indent>^[ \t]*)(?P<lhs>\w+(?:\[[^\n\]]+\])?)->'+member+r'\s*=\s*(?P<value>[^;\n]+);\n[ \t]*'+method+r'\((?P<id>[^,\n]+),\s*(?P<verified>[^,\n]+),\s*(?P<source>EvidenceSource::\w+)\);',re.M)
    s=pat.sub(lambda m:m['indent']+'ApplyStateValue(StateField::'+field+','+m['id']+','+m['value']+','+m['verified']+','+m['source']+');',s)
p.write_text(s,encoding='utf-8')
