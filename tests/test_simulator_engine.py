"""Tests for reactive simulator feedback behavior."""

from __future__ import annotations

import unittest

from src_trainer.grading import GradeResult
from src_trainer.models import ActionEvent, RadioAction
from src_trainer.resources import list_scenarios
from src_trainer.simulator_engine import (
    SimulatorMode,
    apply_device_penalties,
    correct_sequence_lines,
    evaluate_action,
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
