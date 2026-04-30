"""Helpers for loading packaged resources."""

from __future__ import annotations

from importlib import resources
import json


SCENARIOS_PACKAGE = "src_trainer.scenarios"


def list_scenarios() -> list[dict[str, str]]:
    """Load all packaged scenario JSON files."""
    scenario_dir = resources.files(SCENARIOS_PACKAGE)
    scenarios: list[dict[str, str]] = []
    for entry in sorted(scenario_dir.iterdir(), key=lambda path: path.name):
        if entry.is_file() and entry.name.endswith(".json"):
            with entry.open("r", encoding="utf-8") as handle:
                scenarios.append(json.load(handle))
    return scenarios
