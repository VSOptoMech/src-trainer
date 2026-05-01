"""Scenario content validation tests."""

from __future__ import annotations

import unittest

from src_trainer.resources import list_scenarios


class ScenarioContentTests(unittest.TestCase):
    def test_all_scenarios_have_training_context(self) -> None:
        scenarios = list_scenarios()
        self.assertGreaterEqual(len(scenarios), 1)
        for scenario in scenarios:
            with self.subTest(scenario=scenario.id):
                self.assertTrue(scenario.context.what_is_happening)
                self.assertTrue(scenario.context.user_role)
                self.assertTrue(scenario.context.risk_level)
                self.assertTrue(scenario.context.current_objective)
                self.assertGreater(len(scenario.initial_conditions), 0)
                self.assertTrue(scenario.required_assessment)
                self.assertTrue(scenario.correct_procedure)
                self.assertGreater(len(scenario.expected_message_elements), 0)
                self.assertGreater(len(scenario.possible_wrong_actions), 0)
                self.assertTrue(scenario.final_explanation)

    def test_correct_sequence_exists_for_each_scenario(self) -> None:
        for scenario in list_scenarios():
            with self.subTest(scenario=scenario.id):
                self.assertGreater(len(scenario.correct_sequence), 0)

    def test_required_actions_are_represented_in_expected_actions(self) -> None:
        for scenario in list_scenarios():
            for index, step in enumerate(scenario.steps, 1):
                with self.subTest(scenario=scenario.id, step=index):
                    expected = {event.action for event in step.expected_actions}
                    self.assertEqual(set(), set(step.required_actions) - expected)


if __name__ == "__main__":
    unittest.main()
