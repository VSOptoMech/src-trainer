"""Helpers for loading packaged resources."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
import json
import warnings
from typing import Protocol

from pydantic import ValidationError

from src_trainer.models import Scenario
from src_trainer.scenario_details import SCENARIO_DETAILS

SCENARIOS_PACKAGE = "src_trainer.scenarios"
REQUIRED_TRAINING_METADATA = (
    "required_assessment",
    "correct_procedure",
    "expected_message_elements",
    "possible_wrong_actions",
    "final_explanation",
)


class ScenarioDirectory(Protocol):
    def iterdir(self): ...


@dataclass(frozen=True)
class ScenarioLoadDiagnostic:
    """Structured diagnostic for one scenario file that failed to load."""

    filename: str
    message: str


class ScenarioLoadError(ValueError):
    """Raised when one or more scenario files cannot be loaded."""

    def __init__(self, diagnostics: list[ScenarioLoadDiagnostic]) -> None:
        self.diagnostics = diagnostics
        details = "; ".join(f"{item.filename}: {item.message}" for item in diagnostics)
        super().__init__(f"Failed to load {len(diagnostics)} scenario file(s): {details}")


def list_scenarios() -> list[Scenario]:
    """Load all packaged scenario JSON files."""
    scenario_dir = resources.files(SCENARIOS_PACKAGE)
    return load_scenarios_from_directory(scenario_dir)


def load_scenarios_from_directory(scenario_dir: ScenarioDirectory) -> list[Scenario]:
    """Load scenario JSON files and report all invalid files together."""
    scenarios: list[Scenario] = []
    diagnostics: list[ScenarioLoadDiagnostic] = []
    for entry in sorted(scenario_dir.iterdir(), key=lambda path: path.name):
        if not entry.is_file() or not entry.name.endswith(".json"):
            continue
        try:
            with entry.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            payload.update(SCENARIO_DETAILS.get(payload.get("id", ""), {}))
            missing_metadata = _missing_training_metadata(payload)
            scenario = Scenario.model_validate(payload)
            _warn_for_missing_training_metadata(entry.name, missing_metadata)
            scenarios.append(scenario)
        except json.JSONDecodeError as exc:
            diagnostics.append(ScenarioLoadDiagnostic(entry.name, f"invalid JSON at line {exc.lineno}: {exc.msg}"))
        except ValidationError as exc:
            diagnostics.append(ScenarioLoadDiagnostic(entry.name, _validation_message(exc)))
    if diagnostics:
        raise ScenarioLoadError(diagnostics)
    return scenarios


def _validation_message(exc: ValidationError) -> str:
    fields: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"])
        fields.append(f"{location}: {error['msg']}")
    return "; ".join(fields)


def _missing_training_metadata(payload: dict[str, object]) -> list[str]:
    missing = [field for field in REQUIRED_TRAINING_METADATA if not payload.get(field)]
    context = payload.get("context")
    if not isinstance(context, dict) or not context.get("what_is_happening") or not context.get("current_objective"):
        missing.append("context")
    if not payload.get("initial_conditions"):
        missing.append("initial_conditions")
    return missing


def _warn_for_missing_training_metadata(filename: str, missing: list[str]) -> None:
    if missing:
        warnings.warn(
            f"{filename} relies on generated training metadata for: {', '.join(missing)}",
            RuntimeWarning,
            stacklevel=2,
        )
