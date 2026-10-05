import json,math,unittest
from audit_executed_predictions import receipt_predictions,summary

def trace(action,args,edges,feedback,outcome='observed',status='committed'):
    root=dict(action=action,args=args,children=edges)
    catalogue=dict(decision=1,root=root)
    selected=dict(schema='full_policy.v2',decision=1,node=1,receipt=1)
    receipt=dict(event='finalized',id=1,action=action,args=args,feedback=feedback,outcome=outcome,status=status,permit='modeled_probe')
    return '\n'.join('[{}] {}'.format(name,json.dumps(value)) for name,value in
                     [('FullPolicyCatalogue',catalogue),('FullPolicy',selected),('ExecutionEvidence',receipt)])
def edge(kind,probability,success=False,ids=None,reply=None):
    return dict(kind=kind,probability=probability,success=success,ids=ids or [],reply=reply or ['?',-1],node={'stop':True})

class PredictionTests(unittest.TestCase):
    def test_paid_failed_physical(self):
        rows=receipt_predictions(trace('PickUp',[3],[edge(0,.2,True),edge(0,.8)],'false','failed'))
        r=rows[0];self.assertAlmostEqual(r['predicted_success_probability'],.2)
        self.assertAlmostEqual(r['predicted_received_reply_probability'],.8)
        s=summary(rows);self.assertAlmostEqual(s['brier'],.04);self.assertAlmostEqual(s['ece'],.2)
        self.assertAlmostEqual(s['reply_log_scores']['PickUp']['mean_clipped_log_loss'],-math.log(.8))
    def test_actual_success(self):
        r=receipt_predictions(trace('PickUp',[3],[edge(0,.2,True),edge(0,.8)],'true','succeeded'))
        self.assertAlmostEqual(summary(r)['brier'],.64);self.assertEqual(r[0]['actual_success'],1)
    def test_unknown_visibility_has_no_goal_label(self):
        r=receipt_predictions(trace('Sense',[],[edge(1,1,ids=[3])],'[2]'))
        self.assertTrue(r[0]['unrepresented_reply']);self.assertEqual(r[0]['predicted_received_reply_probability'],0)
        self.assertNotIn('actual_success',r[0]);self.assertIsNone(summary(r)['brier'])
    def test_not_known_answer(self):
        r=receipt_predictions(trace('AskLoc',[3],[edge(2,.1),edge(2,.9,reply=['a',2])],'not_known'))
        self.assertAlmostEqual(r[0]['predicted_received_reply_probability'],.1)
    def test_blank_answer_distinct(self):
        r=receipt_predictions(trace('AskLoc',[3],[edge(2,.1),edge(2,.9,reply=['!',-1])],''))
        self.assertAlmostEqual(r[0]['predicted_received_reply_probability'],.9)
    def test_indeterminate_unlabeled(self):
        r=receipt_predictions(trace('Move',[2],[edge(0,1,True)],'timeout','indeterminate','cancelled'))
        self.assertFalse(r[0]['labeled']);self.assertEqual(summary(r)['unlabeled_receipts'],1)
    def test_wrong_command_binding_rejected(self):
        text=trace('PickUp',[3],[edge(0,1,True)],'true','succeeded')
        text=text.replace('"event": "finalized", "id": 1, "action": "PickUp", "args": [3]',
                          '"event": "finalized", "id": 1, "action": "PickUp", "args": [4]')
        with self.assertRaises(AssertionError):receipt_predictions(text)
    def test_visibility_separate_from_physical_rate(self):
        rows=receipt_predictions(trace('Sense',[],[edge(1,1,ids=[3])],'[3]'))
        rows+=receipt_predictions(trace('PickUp',[3],[edge(0,1,True)],'true','succeeded'))
        s=summary(rows);self.assertEqual(s['physical_count'],1);self.assertEqual(s['actual_success_rate'],1)
        self.assertEqual(s['brier'],0);self.assertEqual(s['bins'][0]['bin'],9)
if __name__=='__main__':unittest.main()
