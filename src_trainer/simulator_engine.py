"""Small reactive helpers for simulator feedback and transcript formatting."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from src_trainer.grading import GradeResult
from src_trainer.models import ActionEvent, RadioAction, Scenario, ScenarioCategory


class SimulatorMode(StrEnum):
    practice = "practice"
    test = "test"


class Speaker(StrEnum):
    you = "YOU"
    sar = "SAR"
    coastguard = "COASTGUARD"
    other_vessel = "OTHER VESSEL"
    system = "SYSTEM"
    radio = "RADIO"


@dataclass
class TranscriptEntry:
    speaker: Speaker
    text: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))

    def as_text(self) -> str:
        return f"[{self.timestamp}] {self.speaker.value}: {self.text}"


@dataclass(frozen=True)
class ActionEvaluation:
    correct: bool
    feedback: str
    mistake: bool = False


def apply_device_penalties(
    result: GradeResult,
    *,
    device_mistakes: int,
    pass_score: int,
    penalty_per_mistake: int = 2,
) -> GradeResult:
    """Return a final grade including blocked radio/device-operation mistakes."""
    if device_mistakes <= 0:
        return result
    score = max(0, result.score - (device_mistakes * penalty_per_mistake))
    return GradeResult(
        score=score,
        max_score=result.max_score,
        mistakes=result.mistakes + device_mistakes,
        hints_used=result.hints_used,
        passed=score >= pass_score,
        step_results=result.step_results,
    )


def evaluate_action(
    scenario: Scenario,
    step_index: int,
    prior_actions: list[ActionEvent],
    action: RadioAction,
    value: str | None,
    mode: SimulatorMode,
) -> ActionEvaluation:
    """Evaluate one action against the current step for live simulator feedback."""
    if step_index >= len(scenario.steps):
        return ActionEvaluation(False, "Scenario is already complete.", True)

    step = scenario.steps[step_index]
    expected_position = len(prior_actions)
    expected = step.expected_actions
    correctness_feedback = _correctness_feedback(scenario, step_index, expected_position, expected, action, value)
    if mode == SimulatorMode.test:
        return ActionEvaluation(correctness_feedback.correct, "", correctness_feedback.mistake)
    return correctness_feedback


def _correctness_feedback(
    scenario: Scenario,
    step_index: int,
    expected_position: int,
    expected: list[ActionEvent],
    action: RadioAction,
    value: str | None,
) -> ActionEvaluation:
    if action == RadioAction.SPEAK_PHRASE:
        wrong_priority = _wrong_priority_feedback(scenario, value or "")
        if wrong_priority:
            return ActionEvaluation(False, wrong_priority, True)

    if expected_position >= len(expected):
        return ActionEvaluation(
            False,
            "Unexpected extra action for this step. Check the current objective before continuing.",
            True,
        )

    expected_action = expected[expected_position]
    if action != expected_action.action:
        return ActionEvaluation(
            False,
            f"Expected {expected_action.action.value} next, but received {action.value}.",
            True,
        )

    if expected_action.value is not None:
        actual_value = (value or "").strip().lower()
        expected_value = expected_action.value.strip().lower()
        if actual_value != expected_value:
            if action == RadioAction.SET_CHANNEL:
                return ActionEvaluation(
                    False,
                    f"Wrong channel. Expected channel {expected_action.value}.",
                    True,
                )
            return ActionEvaluation(
                False,
                f"Message content does not match the expected structure for step {step_index + 1}.",
                True,
            )

    return ActionEvaluation(True, "Correct action for the current step.")


def _wrong_priority_feedback(scenario: Scenario, phrase: str) -> str:
    normalized = phrase.lower()
    if scenario.category == ScenarioCategory.distress and "pan-pan" in normalized:
        return "Wrong priority. This is a distress situation, so use MAYDAY rather than PAN-PAN."
    if scenario.category == ScenarioCategory.urgency and "mayday" in normalized:
        return "Wrong priority. This is urgent but not grave and imminent danger, so use PAN-PAN."
    if scenario.category == ScenarioCategory.safety and ("mayday" in normalized or "pan-pan" in normalized):
        return "Wrong priority. A navigation hazard should use SECURITE, not distress or urgency priority."
    return ""


def correct_sequence_lines(scenario: Scenario) -> list[str]:
    lines: list[str] = []
    for index, item in enumerate(scenario.correct_sequence, 1):
        action = item.action.value if item.action else "ASSESS"
        value = f" -> {item.value}" if item.value else ""
        reason = f" ({item.why_it_matters})" if item.why_it_matters else ""
        lines.append(f"{index}. {item.title}: {action}{value}{reason}")
        if item.message_structure:
            lines.append(f"   Message structure: {item.message_structure}")
        if item.common_mistakes:
            lines.append(f"   Common mistakes: {', '.join(item.common_mistakes[:3])}")
    return lines


def transcript_from_strings(lines: list[str]) -> list[TranscriptEntry]:
    entries: list[TranscriptEntry] = []
    for line in lines:
        if ":" in line:
            speaker_text, message = line.split(":", 1)
            speaker = _speaker_from_text(speaker_text.strip())
            entries.append(TranscriptEntry(speaker, message.strip()))
        else:
            entries.append(TranscriptEntry(Speaker.system, line))
    return entries


def _speaker_from_text(value: str) -> Speaker:
    normalized = value.upper().replace(" ", "_")
    for speaker in Speaker:
        if speaker.value.replace(" ", "_") == normalized:
            return speaker
    return Speaker.system
