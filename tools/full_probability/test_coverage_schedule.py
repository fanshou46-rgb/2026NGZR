"""Independently reject incomplete or false deferred-coverage evidence."""
import sys,unittest
sys.dont_write_bytecode=True
from verify_receipts import verify_coverage_schedule,verify_policy_interruptions

class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.decisions={3:dict(scope='finite_catalogue_complete_candidates',selected_stop='true',support='12'),
            4:dict(scope='necessary_initial_missing_acquisition_location',selected_stop='false',support='12')}
        self.header='acquisition_schedule=after_ordinary_stop\n'
        self.marker='[FullCoverageSchedule] decision=4 source_decision=3 before=42 trigger=ordinary_finite_candidate_stop acquisitions=deferred canonical_answer_authority=false\n'
    def test_valid(self):
        self.assertEqual(verify_coverage_schedule(self.header+self.marker,self.decisions)[4]['before'],'42')
    def test_missing(self):
        with self.assertRaises(AssertionError):verify_coverage_schedule(self.header,self.decisions)
    def test_duplicate(self):
        with self.assertRaises(AssertionError):verify_coverage_schedule(self.header+self.marker+self.marker,self.decisions)
    def test_profitable_predecessor(self):
        self.decisions[3]['selected_stop']='false'
        with self.assertRaises(AssertionError):verify_coverage_schedule(self.header+self.marker,self.decisions)
    def test_support_changed(self):
        self.decisions[3]['support']='13'
        with self.assertRaises(AssertionError):verify_coverage_schedule(self.header+self.marker,self.decisions)
    def test_wrong_source(self):
        with self.assertRaises(AssertionError):verify_coverage_schedule(self.header+self.marker.replace('source_decision=3','source_decision=2'),self.decisions)
    def test_hard_answer(self):
        with self.assertRaises(AssertionError):verify_coverage_schedule(self.header+self.marker.replace('authority=false','authority=true'),self.decisions)
    def test_legacy(self):
        self.assertEqual(verify_coverage_schedule('',self.decisions),{})
    def refutation(self):
        self.decisions[4]['target']='7'
        text=self.header+'[FullCoverageRefutation] decision=4 before=42 object=7 site=1 source_sense=1 source_query=2 trigger=actual_at_clue_refuted canonical_answer_authority=false\n'
        receipts=[dict(id=1,policy=1,action='Sense',args=[],status='committed',outcome='observed',feedback='[1,2]',
            evidence=[dict(predicate='robot_at',object=0,value=1,confirmed=True)]),
            dict(id=2,policy=2,action='AskLoc',args=[7],status='committed',outcome='observed',feedback='at(7,1)'),
            dict(id=3,policy=4,action='AskLoc',args=[7],before=42)]
        return text,receipts
    def test_actual_refutation(self):
        text,receipts=self.refutation()
        self.assertEqual(verify_coverage_schedule(text,self.decisions,receipts)[4]['source_sense'],'1')
    def test_visible_object_cannot_refute(self):
        text,receipts=self.refutation();receipts[0]['feedback']='[1,2,7]'
        with self.assertRaises(AssertionError):verify_coverage_schedule(text,self.decisions,receipts)
    def test_physical_invalidates(self):
        text,receipts=self.refutation()
        receipts.insert(2,dict(id=3,policy=3,action='Move',args=[2],outcome='failed'))
        receipts[-1]['id']=4
        with self.assertRaises(AssertionError):verify_coverage_schedule(text,self.decisions,receipts)
    def test_pose_requires_evidence(self):
        text,receipts=self.refutation();receipts[0]['evidence'][0]['confirmed']=False
        with self.assertRaises(AssertionError):verify_coverage_schedule(text,self.decisions,receipts)
    def test_at_only(self):
        text,receipts=self.refutation();receipts[1]['feedback']='inside(7,1)'
        with self.assertRaises(AssertionError):verify_coverage_schedule(text,self.decisions,receipts)
    def test_latest_query_required(self):
        text,receipts=self.refutation()
        receipts.insert(2,dict(id=3,policy=3,action='AskLoc',args=[7],status='committed',outcome='observed',feedback='not_known'))
        receipts[-1]['id']=4
        with self.assertRaises(AssertionError):verify_coverage_schedule(text,self.decisions,receipts)
    def test_refutation_state_signature(self):
        text,receipts=self.refutation();receipts[-1]['before']=43
        with self.assertRaises(AssertionError):verify_coverage_schedule(text,self.decisions,receipts)
    def interruption(self):
        _,receipts=self.refutation();receipts=receipts[:2];receipts[-1]['after']=42
        text='[FullPolicyInterruption] receipt=2 decision=2 before=42 source_sense=1 object=7 site=1 reason=actual_at_clue_refuted paid_history_retained=true\n'
        return text,receipts
    def test_actual_interruption(self):
        text,receipts=self.interruption();self.assertEqual(verify_policy_interruptions(text,receipts),{2})
    def test_interruption_hash(self):
        text,receipts=self.interruption();receipts[-1]['after']=43
        with self.assertRaises(AssertionError):verify_policy_interruptions(text,receipts)
    def test_interruption_duplicate(self):
        text,receipts=self.interruption()
        with self.assertRaises(AssertionError):verify_policy_interruptions(text+text,receipts)

if __name__=='__main__':unittest.main()
