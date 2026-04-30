"""Helpers for loading packaged resources."""

from __future__ import annotations

from importlib import resources
import json

from src_trainer.models import Scenario

SCENARIOS_PACKAGE = "src_trainer.scenarios"


def list_scenarios() -> list[Scenario]:
    """Load all packaged scenario JSON files."""
    scenario_dir = resources.files(SCENARIOS_PACKAGE)
    scenarios: list[Scenario] = []
    for entry in sorted(scenario_dir.iterdir(), key=lambda path: path.name):
        if entry.is_file() and entry.name.endswith(".json"):
            with entry.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
                scenarios.append(Scenario.model_validate(payload))
    return scenarios
