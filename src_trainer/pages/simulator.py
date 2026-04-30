"""Simulator page."""

from __future__ import annotations

import random

from nicegui import ui

from src_trainer.db import record_attempt
from src_trainer.grading import grade_scenario
from src_trainer.models import ActionEvent, RadioAction
from src_trainer.resources import list_scenarios
from src_trainer.components.radio_panel import RadioPanel


def render() -> None:
    scenarios = list_scenarios()
    scenario_map = {s.id: s for s in scenarios}
    selected = {"id": scenarios[0].id if scenarios else ""}
    test_mode = {"value": False}
    state: dict[str, object] = {
        "step": 0,
        "actions": [[] for _ in scenarios[0].steps] if scenarios else [],
        "hints_used": [0 for _ in scenarios[0].steps] if scenarios else [],
        "transcript": [],
        "mistakes": 0,
    }

    def set_scenario(scenario_id: str) -> None:
        selected["id"] = scenario_id
        scenario = scenario_map[scenario_id]
        state["step"] = 0
        state["actions"] = [[] for _ in scenario.steps]
        state["hints_used"] = [0 for _ in scenario.steps]
        state["transcript"] = [f"Loaded scenario: {scenario.title}"]
        state["mistakes"] = 0
        render_panels()

    def current_scenario():
        if test_mode["value"] and scenarios:
            return scenario_map[selected["id"]]
        return scenario_map[selected["id"]] if selected["id"] else None

    def add_action(action: RadioAction, value: str | None = None) -> None:
        scenario = current_scenario()
        if not scenario:
            return
        step = int(state["step"])
        event = ActionEvent(action=action, value=value)
        state["actions"][step].append(event)
        state["transcript"].append(f"Action: {action.value}{' -> ' + value if value else ''}")
        render_panels()

    def give_hint() -> None:
        if test_mode["value"]:
            state["transcript"].append("Hints disabled in test mode.")
            render_panels()
            return
        scenario = current_scenario()
        step = int(state["step"])
        if scenario and scenario.steps[step].hints:
            state["hints_used"][step] += 1
            hint = scenario.steps[step].hints[min(state["hints_used"][step] - 1, len(scenario.steps[step].hints) - 1)]
            state["transcript"].append(f"Hint: {hint}")
        render_panels()

    def next_step() -> None:
        scenario = current_scenario()
        if not scenario:
            return
        if int(state["step"]) < len(scenario.steps) - 1:
            state["step"] = int(state["step"]) + 1
            state["transcript"].append(f"Moved to step {int(state['step']) + 1}")
        render_panels()

    def finish() -> None:
        scenario = current_scenario()
        if not scenario:
            return
        result = grade_scenario(scenario, state["actions"], state["hints_used"])
        state["mistakes"] = result.mistakes
        state["transcript"].append(f"Final score: {result.score} ({'PASS' if result.passed else 'FAIL'})")
        for step_res in result.step_results:
            state["transcript"].append(f"Step {step_res.step_index + 1}: {step_res.feedback}")
        record_attempt(scenario.id, result.score, result.mistakes, result.passed, state["transcript"])
        render_panels(summary=result)

    ui.label("Simulator").classes("text-h4")
    with ui.row().classes("w-full items-center gap-2"):
        ui.select({s.id: s.title for s in scenarios}, value=selected["id"], on_change=lambda e: set_scenario(e.value)).props("dense outlined")
        ui.checkbox("Test mode (random, no hints)", value=False, on_change=lambda e: test_mode.update({"value": bool(e.value)}))
        ui.button("Random scenario", on_click=lambda: set_scenario(random.choice(scenarios).id if scenarios else ""))

    with ui.row().classes("w-full items-start gap-4 wrap"):
        left = ui.column().classes("w-full lg:w-1/4")
        center = ui.column().classes("w-full lg:w-2/4")
        right = ui.column().classes("w-full lg:w-1/4")

    def render_panels(summary=None) -> None:
        left.clear(); center.clear(); right.clear()
        scenario = current_scenario()
        if not scenario:
            left.label("No scenarios")
            return
        step_idx = int(state["step"])
        with left:
            ui.label("Instructions").classes("text-h6")
            ui.label(f"Category: {scenario.category.value} | Difficulty: {scenario.difficulty}")
            ui.label(scenario.situation)
            ui.label("Learning objectives:")
            for obj in scenario.learning_objectives:
                ui.label(f"• {obj}")
            ui.separator()
            ui.label(f"Step {step_idx + 1}/{len(scenario.steps)}: {scenario.steps[step_idx].title}")
            ui.button("Get hint", on_click=give_hint)
            if scenario.steps[step_idx].hints and not test_mode["value"]:
                ui.label(f"Hints available: {len(scenario.steps[step_idx].hints)}")
        with center:
            ui.label("Radio Faceplate").classes("text-h6")
            channel_display = "16" if step_idx == 0 else "72"
            RadioPanel(
                on_action=add_action,
                channel=channel_display,
                powered=True,
                tx_active=False,
                rx_active=True,
                hi_power=True,
                dsc_mode="WATCH" if not test_mode["value"] else "TEST",
            ).render()
            phrase = ui.input("Phrase to transmit").props("outlined")
            ui.button("Speak phrase", on_click=lambda p=phrase: add_action(RadioAction.SPEAK_PHRASE, p.value)).classes("mt-2")
            with ui.row().classes("gap-2 mt-2"):
                ui.button("Next step", on_click=next_step)
                ui.button("Finish scenario", on_click=finish)
        with right:
            ui.label("Transcript + Feedback").classes("text-h6")
            ui.label(f"Mistakes: {state['mistakes']}")
            for line in state["transcript"][-20:]:
                ui.label(line)
            if summary:
                ui.separator()
                ui.label(f"Score: {summary.score}/100")
                ui.label(f"Hints used: {summary.hints_used}")
                ui.label(f"Result: {'PASS' if summary.passed else 'FAIL'}")

    if scenarios:
        set_scenario(selected["id"])
