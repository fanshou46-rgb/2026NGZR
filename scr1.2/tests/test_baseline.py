import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('baseline', str(Path(__file__).resolve().parents[1] / 'tools/baseline.py'))
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


class BaselineTests(unittest.TestCase):
    def test_negative_score_is_preserved(self):
        result = baseline.parse_result('# Result:\n [Move 3|false]\n# Time: 1.2s\n# Score: -12\n', '', 5000)
        self.assertEqual(result['official_score'], -12)
        self.assertEqual(result['actions'], {'move': 1})

    def test_missing_score_is_not_zero(self):
        self.assertIsNone(baseline.parse_result('connection failed', '', 5000)['raw_score'])

    def test_cap_and_timeout(self):
        result = baseline.parse_result('# Time: 5s\n# Score: 1500\n', '', 5000)
        self.assertEqual(result['raw_score'], 1500)
        self.assertEqual(result['official_score'], 1000)
        self.assertTrue(result['platform_timed_out'])

    def test_does_not_count_client_debug_as_actions(self):
        client = '[Move 3|true]\nRDFW_METRICS {"exit_reason":"budget"}\n'
        result = baseline.parse_result('[Sense|1 3]\n# Score: 40\n', client, 5000)
        self.assertEqual(result['actions'], {'sense': 1})
        self.assertEqual(result['client_metrics']['exit_reason'], 'budget')

    def test_final_goals_from_official_answer(self):
        result = baseline.parse_evaluation('value(1,40) value(2,40) value(3,20)\nSATISFIABLE\n')
        self.assertEqual(result, {'final_goals': 2, 'credited_constraints': 1})
        self.assertIsNone(baseline.parse_evaluation('UNSATISFIABLE\n')['final_goals'])


if __name__ == '__main__':
    unittest.main()
