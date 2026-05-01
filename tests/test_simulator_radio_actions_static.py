"""Static checks for simulator/radio action wiring."""

from __future__ import annotations

import ast
from pathlib import Path
import unittest

from src_trainer.models import RadioAction

REPO_ROOT = Path(__file__).resolve().parent.parent


class SimulatorRadioActionStaticTests(unittest.TestCase):
    def test_radio_controls_reference_only_valid_radio_action_members(self) -> None:
        valid = {member.name for member in RadioAction}
        invalid: list[str] = []
        paths = [
            REPO_ROOT / "src_trainer/components/radio_panel.py",
            REPO_ROOT / "src_trainer/components/radio_state.py",
        ]

        for path in paths:
            module = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(module):
                if (
                    isinstance(node, ast.Attribute)
                    and isinstance(node.value, ast.Name)
                    and node.value.id == "RadioAction"
                    and node.attr not in valid
                ):
                    invalid.append(node.attr)

        self.assertEqual([], invalid, f"Invalid RadioAction references: {sorted(set(invalid))}")


if __name__ == "__main__":
    unittest.main()
