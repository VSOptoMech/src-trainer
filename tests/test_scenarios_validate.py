"""Scenario content validation tests."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest
import warnings

from src_trainer.resources import ScenarioLoadError, list_scenarios, load_scenarios_from_directory

REPO_ROOT = Path(__file__).resolve().parent.parent


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

    def test_invalid_scenario_files_report_all_failures(self) -> None:
        valid_payload = json.loads(
            (REPO_ROOT / "src_trainer/scenarios/mayday_voice.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as tmp:
            scenario_dir = Path(tmp)
            (scenario_dir / "valid.json").write_text(json.dumps(valid_payload), encoding="utf-8")
            (scenario_dir / "bad_json.json").write_text("{", encoding="utf-8")
            (scenario_dir / "bad_schema.json").write_text(
                json.dumps({"id": "missing_required_fields"}),
                encoding="utf-8",
            )

            with self.assertRaises(ScenarioLoadError) as raised:
                load_scenarios_from_directory(scenario_dir)

        filenames = {item.filename for item in raised.exception.diagnostics}
        self.assertEqual({"bad_json.json", "bad_schema.json"}, filenames)
        self.assertIn("Failed to load 2 scenario file(s)", str(raised.exception))

    def test_missing_training_metadata_emits_warning_but_still_loads(self) -> None:
        minimal_payload = {
            "id": "minimal",
            "title": "Minimal scenario",
            "description": "A valid scenario with generated training metadata.",
            "category": "routine",
            "difficulty": "intro",
            "situation": "Routine radio practice.",
            "learning_objectives": ["Practice one radio action."],
            "pass_score": 70,
            "steps": [
                {
                    "title": "Power on",
                    "expected_actions": [{"action": "POWER_ON"}],
                    "required_actions": ["POWER_ON"],
                    "feedback_correct": "Powered on.",
                    "feedback_incorrect": "Power on first.",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            scenario_dir = Path(tmp)
            (scenario_dir / "minimal.json").write_text(json.dumps(minimal_payload), encoding="utf-8")

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                scenarios = load_scenarios_from_directory(scenario_dir)

        self.assertEqual(["minimal"], [scenario.id for scenario in scenarios])
        self.assertEqual(1, len(caught))
        self.assertIn("minimal.json relies on generated training metadata", str(caught[0].message))


if __name__ == "__main__":
    unittest.main()
