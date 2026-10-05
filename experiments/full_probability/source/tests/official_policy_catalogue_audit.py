"""Audit catalogue references from an actual SDK transport execution.

Also reject a corrupted catalogue, a valid but stale node, and altered actual
feedback. The SDK executable independently asserts its goals and paid fees.
"""
import json,re,subprocess,sys

def fnv(text):
    value=14695981039346656037
    for byte in text.encode('utf8'):value=((value^byte)*1099511628211)&((1<<64)-1)
    return value

def decode(text):
    cats={};refs=[];receipts=[]
    for line in re.sub(r'\x1b\[[0-9;]*m','',text).splitlines():
        if '[FullPolicyCatalogue] {' in line:
            payload=line.split('[FullPolicyCatalogue] ',1)[1].rstrip();c=json.loads(payload)
            assert c['schema']=='full_policy_catalogue.v2' and c['decision'] not in cats
            c['rawroot']=payload.split('"root":',1)[1][:-1]
            assert json.loads(c['rawroot'])==c['root'];nodes={}
            def visit(node,depth=0):
                assert depth<=64
                if node.get('stop') is True:assert node=={'stop':True};return
                nodes[len(nodes)+1]=node
                assert node['unexpected']=={'stop':True}
                assert node['children'] and abs(sum(b['probability'] for b in node['children'])-1)<1e-8
                for b in node['children']:assert b['probability']>0;visit(b['node'],depth+1)
            visit(c['root']);c['nodes']=nodes;c['ids']={id(node):number for number,node in nodes.items()};cats[c['decision']]=c
        if '[FullPolicy] {' in line:refs.append(json.loads(line.split('[FullPolicy] ',1)[1]))
        if '[ExecutionEvidence] {' in line:
            r=json.loads(line.split('[ExecutionEvidence] ',1)[1])
            if r['event']=='finalized':receipts.append(r)
    assert cats and len(refs)==len(receipts)>2
    return cats,refs,receipts

def observed(node,r):
    for b in node['children']:
        if node['action']=='Sense':match=set(b['ids'])==set(json.loads(r['feedback']))
        elif node['action']=='AskLoc':
            raw=r['feedback'];reply=['!',-1] if raw=='' else ['?',-1]
            m=re.fullmatch(r'(at|inside)\((\d+),(\d+)\)',raw)
            if m:reply=['a' if m[1]=='at' else 'i',int(m[3])]
            match=b['reply']==reply
        else:match=b['success']==(r['outcome']=='succeeded')
        if match:return b['node']
    return None

def audit(cats,refs,receipts):
    for c in cats.values():assert fnv(c['rawroot'])==c['digest']
    previous=None;expected=1;used=set()
    for number,(p,r) in enumerate(zip(refs,receipts),1):
        assert p['schema']=='full_policy.v2' and p['receipt']==r['id']==number
        assert p['decision']==r['policy'] and p['before']==r['before']
        c=cats[p['decision']];assert p['catalogue']==c['digest']
        if previous!=p['decision']:expected=1
        assert p['node']==expected and p['node'] in c['nodes']
        node=c['nodes'][p['node']]
        assert node['action']==r['action'] and node['args']==r['args'] and node['cost']==r['cost']
        assert r['status']=='committed' and r['permit']!='legacy_unqualified'
        tail=observed(node,r);expected=c['ids'].get(id(tail));previous=p['decision'];used.add(previous)
    assert used==set(cats)

def reject(callback):
    try:callback()
    except (AssertionError,KeyError):return
    raise AssertionError('corrupted policy reference was accepted')

run=subprocess.run(sys.argv[1:],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
sys.stdout.buffer.write(run.stdout);sys.stdout.flush();assert run.returncode==0
cats,refs,receipts=decode(run.stdout.decode('utf8',errors='replace'));audit(cats,refs,receipts)
bad_cats=dict(cats);key=refs[0]['decision'];bad_cats[key]=dict(cats[key],digest=cats[key]['digest']^1)
reject(lambda:audit(bad_cats,refs,receipts))
assert refs[2]['decision']==refs[1]['decision'] and refs[2]['node']!=1
bad_refs=list(refs);bad_refs[2]=dict(refs[2],node=1)
reject(lambda:audit(cats,bad_refs,receipts))
bad_receipts=list(receipts);bad_receipts[1]=dict(receipts[1],outcome='failed')
reject(lambda:audit(cats,refs,bad_receipts))
print('actual SDK catalogue digests, every action reference and feedback path checked; three evidence corruptions rejected')
