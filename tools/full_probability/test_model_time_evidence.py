import unittest
from model_time_evidence import verify_model_time_evidence

class TimeTests(unittest.TestCase):
    def setUp(self):
        rows=[('initialize',0,2,0),('initial_forecast',2,4,0),('policy_catalogue',4,5,0),
              ('feedback_replay',15,17,1),('candidate_selection',17,32,1)]
        self.text='\n'.join('[FullModelTimeSpan] id={} phase={} receipt_mark={} begin_ns={} end_ns={} duration_ns={} scope=model_only_receipt_watermark_unchanged'.format(i+1,p,m,b,e,e-b)
                            for i,(p,b,e,m) in enumerate(rows))
        self.text+='\n[FullModel] stopped receipts=1 model_ms=0 sdk_ms=0.000010 dispatch_overhead_ms=0\n[FullStopEvidence] reason=no_remaining_search_budget model_ns=22'
    def audit(self,text=None,required=True):return verify_model_time_evidence(self.text if text is None else text,[{'id':1}],required)
    def bad(self,text):
        with self.assertRaises(AssertionError):self.audit(text)
    def test_valid_abort_and_sdk_gap(self):self.assertEqual(self.audit(),dict(segments=5,ns=22))
    def test_omitted_abort(self):self.bad(self.text.replace('model_ns=22','model_ns=7'))
    def test_double_charge(self):self.bad(self.text.replace('model_ns=22','model_ns=37'))
    def test_duration_mismatch(self):self.bad(self.text.replace('duration_ns=15','duration_ns=14'))
    def test_overlap(self):self.bad(self.text.replace('begin_ns=17','begin_ns=16').replace('duration_ns=15','duration_ns=16').replace('model_ns=22','model_ns=23'))
    def test_wrong_watermark(self):self.bad(self.text.replace('phase=policy_catalogue receipt_mark=0','phase=policy_catalogue receipt_mark=1'))
    def test_missing_policy_phase(self):self.bad(self.text.replace('phase=policy_catalogue','phase=candidate_selection'))
    def test_unknown_phase(self):self.bad(self.text.replace('phase=feedback_replay','phase=sdk_wait'))
    def test_duplicate_id(self):self.bad(self.text.replace('id=5','id=4'))
    def test_missing_required_ledger(self):self.bad('')
    def test_legacy(self):self.assertEqual(self.audit('',False),dict(segments=0,ns=0))
    def test_reported_ms(self):self.bad(self.text.replace('model_ms=0','model_ms=1'))
if __name__=='__main__':unittest.main()
