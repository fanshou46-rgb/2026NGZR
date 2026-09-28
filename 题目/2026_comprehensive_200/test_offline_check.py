"""Small semantic regression checks for the offline verifier's critical rules."""
import unittest
from offline_check import World, Term, Invalid, goal, holds, replay, sexps, parse_nl


def world():
    objects = {
        1: dict(sort='human', size='big'), 2: dict(sort='table', size='big'),
        3: dict(sort='cupboard', size='big', type='container'),
        4: dict(sort='can', color='red', size='small'),
        5: dict(sort='cup', color='white', size='small'),
        6: dict(sort='book', color='white', size='small'),
    }
    return World(objects, 3, {1: 1, 2: 2, 3: 3, 4: 3, 5: 3}, {6: 3}, set())


class OfflineSemantics(unittest.TestCase):
    def test_closed_container_observation_is_not_absence(self):
        w = world()
        self.assertNotIn(6, w.step(['sense'])['visible'])
        self.assertEqual(w.inside[6], 3)
        with self.assertRaises(Invalid): w.step(['takeout', 6, 3])
        w.step(['open', 3])
        self.assertIn(6, w.step(['sense'])['visible'])
        w.step(['takeout', 6, 3])
        self.assertEqual(w.hand, 6)

    def test_doors_need_empty_hand(self):
        w = world()
        w.step(['pickup', 4])
        with self.assertRaises(Invalid): w.step(['open', 3])
        w.step(['toplate', 4])
        w.step(['open', 3])
        self.assertIn(3, w.opened)

    def test_two_pickup_goals_can_use_two_slots(self):
        w = world()
        w.step(['pickup', 4])
        w.step(['toplate', 4])
        w.step(['pickup', 5])
        self.assertTrue(goal(w, 'pickup', (4,)))
        self.assertTrue(goal(w, 'pickup', (5,)))
        self.assertFalse(holds(w, Term('constraint', 'plate', (4,), False)))
        self.assertTrue(holds(w, Term('constraint', 'plate', (5,), False)))
        with self.assertRaises(Invalid): w.step(['takeout', 6, 3])

    def test_constraint_history_survives_physical_restoration(self):
        initial = world()
        constraint = Term('constraint', 'near', (4, 1), False)
        result = replay(initial, [constraint], [
            ['pickup', 4], ['move', 1], ['move', 3], ['putdown', 4]])
        self.assertEqual(initial.snapshot(), result['final'].snapshot())
        self.assertTrue(holds(result['final'], constraint))
        self.assertEqual(result['violated_constraint_ids'], [1])
        self.assertEqual(result['first_violation_step'][1], 2)

    def test_bound_pair_needs_synchronous_transport(self):
        c = Term('constraint', 'near', (4, 5), True)
        bad = replay(world(), [c], [['pickup', 4], ['move', 2]])
        good = replay(world(), [c], [['pickup', 4], ['toplate', 4], ['pickup', 5], ['move', 2]])
        self.assertEqual(bad['violated_constraint_ids'], [1])
        self.assertEqual(good['violated_constraint_ids'], [])

    def test_goal_evaluation_uses_final_state(self):
        w = world()
        w.step(['move', 1])
        self.assertTrue(goal(w, 'goto', (1,)))
        w.step(['move', 2])
        self.assertFalse(goal(w, 'goto', (1,)))
        self.assertTrue(goal(w, 'goto', (2,)))

    def test_putdown_prohibition_differs_from_transit(self):
        w = world()
        c = Term('constraint', 'puton', (4, 2), False, 'task')
        w.step(['pickup', 4])
        w.step(['move', 2])
        self.assertTrue(holds(w, c))
        w.step(['putdown', 4])
        self.assertFalse(holds(w, c))

    def test_language_negation_and_syntax_are_checked(self):
        obj = world().objects
        positive = parse_nl('The red can must be near the table.', obj)
        negative = parse_nl('The red can must not be near the table.', obj)
        self.assertNotEqual(positive.key(), negative.key())
        self.assertEqual(parse_nl('Give the white book to the human.', obj).args, (1, 6))
        with self.assertRaises(Invalid): sexps('(:ins (:task (pickup X))')


if __name__ == '__main__':
    unittest.main()
