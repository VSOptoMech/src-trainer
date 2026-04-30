"""Scenario grading logic."""

from __future__ import annotations

from dataclasses import dataclass, field

from src_trainer.models import ActionEvent, Scenario


@dataclass
class StepResult:
    step_index: int
    score: int
    max_score: int
    hints_used: int
    mistakes: int
    feedback: str


@dataclass
class GradeResult:
    score: int
    max_score: int
    mistakes: int
    hints_used: int
    passed: bool
    step_results: list[StepResult] = field(default_factory=list)


def grade_scenario(
    scenario: Scenario,
    user_actions_by_step: list[list[ActionEvent]],
    hints_used_by_step: list[int] | None = None,
) -> GradeResult:
    """Grade user actions for a scenario."""
    step_results: list[StepResult] = []
    total_score, total_max, total_mistakes, total_hints = 0, 0, 0, 0
    hints_used_by_step = hints_used_by_step or [0 for _ in scenario.steps]

    for idx, step in enumerate(scenario.steps):
        provided = user_actions_by_step[idx] if idx < len(user_actions_by_step) else []
        hints_used = hints_used_by_step[idx] if idx < len(hints_used_by_step) else 0

        max_score = step.score_weight
        score = max_score
        mistakes = 0

        required = set(step.required_actions)
        provided_set = {action.action for action in provided}
        missing_required = required - provided_set
        mistakes += len(missing_required)
        score -= len(missing_required) * 2

        expected = step.expected_actions
        for pos, expected_action in enumerate(expected):
            if pos >= len(provided):
                mistakes += 1
                score -= 2
                continue
            actual = provided[pos]
            if actual.action != expected_action.action:
                mistakes += 1
                score -= 2
            elif expected_action.value is not None and (actual.value or "").strip().lower() != expected_action.value.strip().lower():
                mistakes += 1
                score -= 1

        extra_actions = max(0, len(provided) - len(expected))
        mistakes += extra_actions
        score -= extra_actions

        hint_penalty = min(hints_used, 3)
        score -= hint_penalty

        score = max(score, 0)
        feedback = step.feedback_correct if mistakes == 0 else step.feedback_incorrect

        total_score += score
        total_max += max_score
        total_mistakes += mistakes
        total_hints += hints_used

        step_results.append(
            StepResult(idx, score, max_score, hints_used, mistakes, feedback)
        )

    normalized = int(round((total_score / total_max) * 100)) if total_max else 0
    return GradeResult(
        score=normalized,
        max_score=100,
        mistakes=total_mistakes,
        hints_used=total_hints,
        passed=normalized >= scenario.pass_score,
        step_results=step_results,
    )
