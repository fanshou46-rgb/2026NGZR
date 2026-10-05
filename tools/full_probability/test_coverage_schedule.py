"""Independently reject incomplete or false deferred-coverage evidence."""
import sys,unittest
sys.dont_write_bytecode=True
from verify_receipts import verify_coverage_schedule

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

if __name__=='__main__':unittest.main()
