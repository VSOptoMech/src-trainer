"""Tests for reactive simulator feedback behavior."""

from __future__ import annotations

import unittest

from src_trainer.grading import GradeResult, grade_scenario
from src_trainer.models import ActionEvent, RadioAction
from src_trainer.resources import list_scenarios
from src_trainer.simulator_engine import (
    SimulatorMode,
    apply_device_penalties,
    correct_sequence_lines,
    evaluate_action,
    should_record_action,
)


class SimulatorEngineTests(unittest.TestCase):
    def test_practice_mode_gives_live_feedback(self) -> None:
        scenario = next(item for item in list_scenarios() if item.id == "mayday_voice")

        result = evaluate_action(
            scenario,
            0,
            [],
            RadioAction.POWER_ON,
            None,
            SimulatorMode.practice,
        )

        self.assertTrue(result.correct)
        self.assertEqual("Correct action for the current step.", result.feedback)

    def test_test_mode_suppresses_live_correctness_feedback(self) -> None:
        scenario = next(item for item in list_scenarios() if item.id == "mayday_voice")

        result = evaluate_action(
            scenario,
            0,
            [],
            RadioAction.POWER_ON,
            None,
            SimulatorMode.test,
        )

        self.assertTrue(result.correct)
        self.assertEqual("", result.feedback)

    def test_wrong_priority_is_reported_in_practice_mode(self) -> None:
        scenario = next(item for item in list_scenarios() if item.id == "mayday_voice")
        prior = [
            ActionEvent(action=RadioAction.HOLD_PTT),
        ]

        result = evaluate_action(
            scenario,
            1,
            prior,
            RadioAction.SPEAK_PHRASE,
            "Pan-Pan BLUE MERIDIAN flooding",
            SimulatorMode.practice,
        )

        self.assertFalse(result.correct)
        self.assertTrue(result.mistake)
        self.assertIn("Wrong priority", result.feedback)

    def test_phrase_matching_accepts_punctuation_spacing_and_order_variants(self) -> None:
        scenario = next(item for item in list_scenarios() if item.id == "securite_hazard")
        prior = [ActionEvent(action=RadioAction.HOLD_PTT)]

        for phrase in [
            "Securite, floating hazard",
            "floating hazard securite",
            "  SÉCURITÉ: floating   hazard!  ",
            "securite - hazard, floating",
            "floating, securite hazard",
        ]:
            with self.subTest(phrase=phrase):
                result = evaluate_action(
                    scenario,
                    1,
                    prior,
                    RadioAction.SPEAK_PHRASE,
                    phrase,
                    SimulatorMode.practice,
                )

                self.assertTrue(result.correct)
                self.assertFalse(result.mistake)

    def test_final_grading_uses_same_phrase_matching_rules(self) -> None:
        scenario = next(item for item in list_scenarios() if item.id == "securite_hazard")
        actions_by_step = [
            [
                ActionEvent(action=RadioAction.POWER_ON),
                ActionEvent(action=RadioAction.PRESS_CH16),
            ],
            [
                ActionEvent(action=RadioAction.HOLD_PTT),
                ActionEvent(action=RadioAction.SPEAK_PHRASE, value="floating hazard securite"),
                ActionEvent(action=RadioAction.RELEASE_PTT),
            ],
            [ActionEvent(action=RadioAction.SET_CHANNEL, value="16")],
        ]

        result = grade_scenario(scenario, actions_by_step)

        self.assertTrue(result.passed)
        self.assertEqual(0, result.mistakes)

    def test_practice_mistakes_do_not_advance_expected_sequence(self) -> None:
        scenario = next(item for item in list_scenarios() if item.id == "dsc_distress_simple")
        prior = [ActionEvent(action=RadioAction.POWER_ON)]

        wrong = evaluate_action(
            scenario,
            0,
            prior,
            RadioAction.SET_CHANNEL,
            "16",
            SimulatorMode.practice,
        )

        self.assertTrue(wrong.mistake)
        self.assertFalse(should_record_action(wrong, SimulatorMode.practice))

        recovered = evaluate_action(
            scenario,
            0,
            prior,
            RadioAction.PRESS_CH16,
            None,
            SimulatorMode.practice,
        )

        self.assertTrue(recovered.correct)

    def test_test_mode_records_mistakes_for_final_grading(self) -> None:
        scenario = next(item for item in list_scenarios() if item.id == "dsc_distress_simple")
        result = evaluate_action(
            scenario,
            0,
            [ActionEvent(action=RadioAction.POWER_ON)],
            RadioAction.SET_CHANNEL,
            "16",
            SimulatorMode.test,
        )

        self.assertTrue(result.mistake)
        self.assertTrue(should_record_action(result, SimulatorMode.test))

    def test_correct_sequence_lines_exist(self) -> None:
        for scenario in list_scenarios():
            self.assertGreater(len(correct_sequence_lines(scenario)), 0, scenario.id)

    def test_device_penalties_reduce_final_score_and_update_mistakes(self) -> None:
        result = GradeResult(
            score=74,
            max_score=100,
            mistakes=2,
            hints_used=0,
            passed=True,
        )

        adjusted = apply_device_penalties(result, device_mistakes=3, pass_score=70)

        self.assertEqual(68, adjusted.score)
        self.assertEqual(5, adjusted.mistakes)
        self.assertFalse(adjusted.passed)

    def test_no_device_penalties_leave_grade_unchanged(self) -> None:
        result = GradeResult(
            score=74,
            max_score=100,
            mistakes=2,
            hints_used=0,
            passed=True,
        )

        adjusted = apply_device_penalties(result, device_mistakes=0, pass_score=70)

        self.assertIs(result, adjusted)


if __name__ == "__main__":
    unittest.main()
