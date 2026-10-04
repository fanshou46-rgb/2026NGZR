"""Independent semantic/topology audit and mutation tests before exposure."""
from common import *
import collections, copy, unittest, xml.etree.ElementTree as ET
sys.path.insert(0,str(OLD))
import offline_check as oc, guide_audit as ga

def topology(path):
    d=oc.load_case(path);w=d['world']
    # Stable graph labels remove ID/color/place decoration, retain source/destination dependency.
    small=[i for i,o in w.objects.items() if o['size']=='small']
    labels={i:o['sort'] for i,o in w.objects.items() if o['size']=='big'}
    labels.update({i:('s'+str(j)) for j,i in enumerate(small)})
    furniture={loc:labels[i] for i,loc in w.at.items() if i in labels and w.objects[i]['size']=='big'}
    state=sorted((labels[i],'inside',labels[c]) for i,c in w.inside.items())
    state+=sorted((labels[i],'at',furniture[loc]) for i,loc in w.at.items() if i in small)
    state += [('hand',labels.get(w.hand,'none')),('plate',labels.get(w.plate,'none')),('robot_at',furniture[w.robot])]
    goals=sorted((t.pred,tuple(labels[i] for i in t.args)) for t in d['terms'] if t.kind=='task')
    cons=sorted((t.pred,tuple(labels[i] for i in t.args),t.positive,t.inner) for t in d['terms'] if t.kind=='constraint')
    return json.dumps([sorted(state,key=str),goals,cons],sort_keys=True)
class Audit(unittest.TestCase):
    def test_totals_guides_and_references(self):
        cat=json.loads((BANK/'catalogue.json').read_text(encoding='utf8'))
        self.assertEqual(collections.Counter(c['kind'] for c in cat['cases']),dict(full=70,tradeoff=20,invalid=10))
        for c in cat['cases']:
            if c['kind']=='invalid':continue
            self.assertEqual(ga.audit(BANK/c['path']),[],c['id']);d=oc.load_case(BANK/c['path'])
            self.assertEqual(len({t.key() for t in d['terms']}),37)
            ref=json.loads((BANK/c['reference']).read_text(encoding='utf8'))
            for p in ref['plans']:
                rr=oc.replay(d['world'],d['terms'],p['actions']);self.assertEqual(rr['goal_ids'],p['completed_goal_ids']);self.assertEqual(rr['violated_constraint_ids'],p['violated_constraint_ids'])
    def test_no_old_topology_copy(self):
        oldcat=json.loads((OLD/'catalogue.json').read_text(encoding='utf8'))
        previous={topology(OLD/c['path']) for c in oldcat['cases'] if c.get('stage')==1 and c['kind']!='invalid'}
        cat=json.loads((BANK/'catalogue.json').read_text(encoding='utf8'))
        matches=[c['id'] for c in cat['cases'] if c.get('stage')==1 and c['kind']!='invalid' and topology(BANK/c['path']) in previous]
        self.assertEqual(matches,[])
    def test_counterfactuals(self):
        cat=json.loads((BANK/'catalogue.json').read_text(encoding='utf8'));byid={c['id']:c for c in cat['cases']}
        self.assertEqual(len(cat['counterfactual_pairs']),4)
        for pair in cat['counterfactual_pairs']:
            for stage in (1,2):
                a,b=[oc.load_case(BANK/byid[pair[k]+f'-s{stage}']['path']) for k in ('left','right')]
                self.assertEqual(a['facts'],b['facts']);self.assertEqual(a['world'],b['world'])
                x,y=[{t.key() for t in d['terms']} for d in (a,b)]
                self.assertEqual(len(x-y),1);self.assertEqual(len(y-x),1)
    def test_new_cases_are_not_decoration_duplicates(self):
        cat=json.loads((BANK/'catalogue.json').read_text(encoding='utf8'))
        signatures=[topology(BANK/c['path']) for c in cat['cases'] if c.get('stage')==1 and c['kind']!='invalid']
        self.assertEqual(len(signatures),len(set(signatures)))
    def test_negative_cases_rejected(self):
        cat=json.loads((BANK/'catalogue.json').read_text(encoding='utf8'))
        for c in cat['cases']:
            if c['kind']=='invalid':
                with self.assertRaises((oc.Invalid,ET.ParseError)):oc.load_case(BANK/c['path'])
if __name__=='__main__':unittest.main(verbosity=2)
