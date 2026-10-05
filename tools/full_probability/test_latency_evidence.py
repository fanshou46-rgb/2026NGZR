"""Independent arithmetic/feedback-tree checks for experimental time proxy."""
import copy,unittest
from latency_evidence import verify_latency_evidence,future_millis

class LatencyTests(unittest.TestCase):
    def setUp(self):
        self.parameters={'actions':{'PickUp':dict(median_ms=111,count=5),'Move':dict(median_ms=120,count=10)},
                         'outcomes':{'Move/failed':dict(median_ms=100,count=2)}}
        self.root=dict(action='PickUp',children=[dict(kind=0,success=True,probability=1,node={'stop':True})])
        self.catalogues={2:dict(root=self.root)}
        self.decisions={2:dict(scope='finite_catalogue_complete_candidates',selected_stop='false',support='64',selected_lower='38',selected_upper='38')}
        self.physical='[FullPhysicalEvaluation] decision=2 inputs=64 retained=1 replay_support=64 scope=pure_physical_candidate_evaluation canonical_answer_authority=false\n'
        self.evidence='[FullLatencyEvidence] decision=2 predicted_sdk_ms=111 proxy_lower=35.78 proxy_upper=35.78 base_lower=38 base_upper=38 rate_per_ms=0.02 past_time_constant=true scope=descriptive_future_sdk_continuous_proxy hard_bound=false\n'
        self.text='latency_scope=f19_actual_repeat0_sdk_median_proxy physical_eval_scope=ledger_exact_view\n'+self.physical+self.evidence
    def audit(self,text=None,decisions=None,catalogues=None):
        return verify_latency_evidence(self.text if text is None else text,self.decisions if decisions is None else decisions,
            self.catalogues if catalogues is None else catalogues,self.parameters)
    def rejected(self,text):
        with self.assertRaises(AssertionError):self.audit(text)
    def test_valid(self):
        r=self.audit();self.assertEqual(r['latency_trees'],1);self.assertEqual(r['physical_retained_worlds'],1)
    def test_time_not_matching_policy(self):self.rejected(self.text.replace('predicted_sdk_ms=111','predicted_sdk_ms=110').replace('35.78','35.8'))
    def test_proxy_mismatch(self):self.rejected(self.text.replace('proxy_lower=35.78','proxy_lower=38'))
    def test_base_mismatch(self):self.rejected(self.text.replace('base_lower=38','base_lower=40').replace('proxy_lower=35.78','proxy_lower=37.78'))
    def test_rate(self):self.rejected(self.text.replace('rate_per_ms=0.02','rate_per_ms=0.01'))
    def test_past_time(self):self.rejected(self.text.replace('past_time_constant=true','past_time_constant=false'))
    def test_hard_bound(self):self.rejected(self.text.replace('hard_bound=false','hard_bound=true'))
    def test_negative_time(self):self.rejected(self.text.replace('predicted_sdk_ms=111','predicted_sdk_ms=-111'))
    def test_nan(self):self.rejected(self.text.replace('predicted_sdk_ms=111','predicted_sdk_ms=nan'))
    def test_missing_time(self):self.rejected(self.text.replace(self.evidence,''))
    def test_missing_physical(self):self.rejected(self.text.replace(self.physical,''))
    def test_duplicate(self):self.rejected(self.text+self.evidence)
    def test_merged_more_than_original(self):self.rejected(self.text.replace('retained=1','retained=65'))
    def test_hard_answer(self):self.rejected(self.text.replace('canonical_answer_authority=false','canonical_answer_authority=true'))
    def test_posterior_size(self):self.rejected(self.text.replace('replay_support=64','replay_support=1'))
    def test_wrong_decision(self):self.rejected(self.text.replace('decision=2','decision=3'))
    def test_stop_time(self):
        d=copy.deepcopy(self.decisions);d[2]['selected_stop']='true'
        with self.assertRaises(AssertionError):self.audit(decisions=d)
    def test_false_and_continuation(self):
        root=dict(action='Move',children=[dict(kind=0,success=False,probability=.25,node={'stop':True}),
            dict(kind=0,success=True,probability=.75,node=self.root)])
        self.assertEqual(future_millis(root,self.parameters),.25*100+.75*(120+111))
        fail=copy.deepcopy(self.root);fail['children'][0]['success']=False
        self.assertEqual(future_millis(fail,self.parameters),111) # no invented failure labels
    def test_unexecuted_no_feedback_claim(self):self.assertEqual(self.audit(catalogues={})['unexecuted_selected'],1)
    def test_legacy(self):self.assertEqual(self.audit(text='',catalogues={})['latency_decisions'],0)

if __name__=='__main__':unittest.main()
