"""Simulator page."""

from __future__ import annotations

import random
from typing import cast

from nicegui import ui

from src_trainer.components.radio_panel import RadioPanel
from src_trainer.components.radio_state import DEFAULT_CHANNEL, RadioState, normalize_channel
from src_trainer.db import record_attempt
from src_trainer.grading import GradeResult, grade_scenario
from src_trainer.models import ActionEvent, RadioAction, Scenario
from src_trainer.resources import list_scenarios
from src_trainer.simulator_engine import (
    SimulatorMode,
    Speaker,
    TranscriptEntry,
    apply_device_penalties,
    correct_sequence_lines,
    evaluate_action,
    transcript_from_strings,
)


def _initial_channel_for_scenario(scenario: Scenario) -> int:
    for step in scenario.steps:
        for event in step.expected_actions:
            if event.action == RadioAction.SET_CHANNEL and event.value:
                return normalize_channel(event.value)
            if event.action == RadioAction.PRESS_CH16:
                return DEFAULT_CHANNEL
    return DEFAULT_CHANNEL


def render() -> None:
    scenarios = list_scenarios()
    scenario_map = {s.id: s for s in scenarios}
    selected = {"id": scenarios[0].id if scenarios else ""}
    mode = {"value": SimulatorMode.practice.value}
    state: dict[str, object] = {
        "step": 0,
        "actions": [[] for _ in scenarios[0].steps] if scenarios else [],
        "hints_used": [0 for _ in scenarios[0].steps] if scenarios else [],
        "transcript": [],
        "mistakes": 0,
        "device_mistakes": 0,
        "feedback": "",
        "assisted": False,
        "show_sequence": False,
        "summary": None,
    }
    radio_state = RadioState(
        channel=_initial_channel_for_scenario(scenarios[0]) if scenarios else DEFAULT_CHANNEL
    )

    def current_mode() -> SimulatorMode:
        return SimulatorMode(mode["value"])

    def transcript() -> list[TranscriptEntry]:
        return cast(list[TranscriptEntry], state["transcript"])

    def actions_by_step() -> list[list[ActionEvent]]:
        return cast(list[list[ActionEvent]], state["actions"])

    def hints_by_step() -> list[int]:
        return cast(list[int], state["hints_used"])

    def add_transcript(speaker: Speaker, text: str) -> None:
        transcript().append(TranscriptEntry(speaker, text))

    def set_feedback(message: str, *, mistake: bool = False, record: bool = True) -> None:
        state["feedback"] = message
        if mistake:
            state["mistakes"] = int(state["mistakes"]) + 1
        if record and message:
            add_transcript(Speaker.system, message)

    def add_radio_feedback(message: str, mistake: bool) -> None:
        if mistake:
            state["device_mistakes"] = int(state["device_mistakes"]) + 1
        if current_mode() == SimulatorMode.test:
            return
        set_feedback(message, mistake=mistake)

    def set_scenario(scenario_id: str) -> None:
        if scenario_id not in scenario_map:
            try:
                scenario_id = scenarios[int(scenario_id)].id
            except (IndexError, TypeError, ValueError):
                return
        if scenario_id not in scenario_map:
            return
        selected["id"] = scenario_id
        scenario = scenario_map[scenario_id]
        state["step"] = 0
        state["actions"] = [[] for _ in scenario.steps]
        state["hints_used"] = [0 for _ in scenario.steps]
        state["transcript"] = [TranscriptEntry(Speaker.system, f"Loaded scenario: {scenario.title}")]
        state["mistakes"] = 0
        state["device_mistakes"] = 0
        state["feedback"] = "Read the context, then power on the radio."
        state["assisted"] = False
        state["show_sequence"] = False
        state["summary"] = None
        radio_state.reset(channel=_initial_channel_for_scenario(scenario))
        transcript().extend(transcript_from_strings(scenario.incoming_events))
        if scenario.steps and scenario.steps[0].event:
            add_transcript(Speaker.system, scenario.steps[0].event)
        render_panels()

    def current_scenario() -> Scenario | None:
        return scenario_map[selected["id"]] if selected["id"] else None

    def add_action(action: RadioAction, value: str | None = None) -> None:
        scenario = current_scenario()
        if not scenario:
            return

        step_index = int(state["step"])
        step_actions = actions_by_step()[step_index]
        evaluation = evaluate_action(
            scenario,
            step_index,
            list(step_actions),
            action,
            value,
            current_mode(),
        )
        event = ActionEvent(action=action, value=value)
        step_actions.append(event)

        if action == RadioAction.SPEAK_PHRASE:
            add_transcript(Speaker.you, value or "")
        else:
            add_transcript(Speaker.radio, f"{action.value}{' -> ' + value if value else ''}")

        if evaluation.mistake and current_mode() == SimulatorMode.practice:
            state["mistakes"] = int(state["mistakes"]) + 1
        if current_mode() == SimulatorMode.practice and evaluation.feedback:
            state["feedback"] = evaluation.feedback
            add_transcript(Speaker.system, evaluation.feedback)

        render_panels()

    def give_hint() -> None:
        scenario = current_scenario()
        if not scenario:
            return
        if current_mode() == SimulatorMode.test:
            set_feedback("Hints are disabled in Test Mode.")
            render_panels()
            return
        step_index = int(state["step"])
        step = scenario.steps[step_index]
        if step.hints:
            hints_by_step()[step_index] += 1
            state["assisted"] = True
            hint_index = min(hints_by_step()[step_index] - 1, len(step.hints) - 1)
            set_feedback(f"Hint: {step.hints[hint_index]}")
        render_panels()

    def show_correct_sequence() -> None:
        if current_mode() == SimulatorMode.test and state["summary"] is None:
            set_feedback("Correct sequence is shown after completion in Test Mode.")
        else:
            state["show_sequence"] = True
            if current_mode() == SimulatorMode.practice:
                state["assisted"] = True
            set_feedback("Correct sequence revealed.")
        render_panels()

    def retry_step() -> None:
        scenario = current_scenario()
        if not scenario:
            return
        step_index = int(state["step"])
        actions_by_step()[step_index] = []
        hints_by_step()[step_index] = 0
        state["assisted"] = True
        set_feedback(f"Retrying step {step_index + 1}. Previous transcript entries remain for review.")
        render_panels()

    def next_step() -> None:
        scenario = current_scenario()
        if not scenario:
            return
        if int(state["step"]) < len(scenario.steps) - 1:
            state["step"] = int(state["step"]) + 1
            step = scenario.steps[int(state["step"])]
            add_transcript(Speaker.system, f"Moved to step {int(state['step']) + 1}: {step.title}")
            if step.event:
                add_transcript(Speaker.system, step.event)
            state["feedback"] = step.objective or step.title
        else:
            set_feedback("Last step reached. Finish the scenario when ready.", record=False)
        render_panels()

    def finish() -> None:
        scenario = current_scenario()
        if not scenario:
            return
        result = apply_device_penalties(
            grade_scenario(scenario, actions_by_step(), hints_by_step()),
            device_mistakes=int(state["device_mistakes"]),
            pass_score=scenario.pass_score,
        )
        state["summary"] = result
        state["mistakes"] = result.mistakes
        state["show_sequence"] = True
        state["feedback"] = f"Final score: {result.score}/100 ({'PASS' if result.passed else 'FAIL'})"
        add_transcript(Speaker.system, state["feedback"])
        if int(state["device_mistakes"]):
            add_transcript(Speaker.system, f"Device operation penalties: {state['device_mistakes']}")
        for step_res in result.step_results:
            add_transcript(Speaker.system, f"Step {step_res.step_index + 1}: {step_res.feedback}")
        transcript_lines = [entry.as_text() for entry in transcript()]
        transcript_lines.append(f"Assisted attempt: {'yes' if state['assisted'] else 'no'}")
        record_attempt(scenario.id, result.score, result.mistakes, result.passed, transcript_lines)
        render_panels()

    def set_mode(value: object) -> None:
        if value in {SimulatorMode.practice.value, "Practice Mode", 0, "0"}:
            mode["value"] = SimulatorMode.practice.value
        elif value in {SimulatorMode.test.value, "Test Mode", 1, "1"}:
            mode["value"] = SimulatorMode.test.value
        else:
            return
        label = "Practice Mode" if current_mode() == SimulatorMode.practice else "Test Mode"
        set_feedback(f"{label} selected.", record=False)
        render_panels()

    ui.label("Simulator").classes("text-h4")
    with ui.row().classes("sim-topbar"):
        ui.select(
            {s.id: s.title for s in scenarios},
            value=selected["id"],
            on_change=lambda e: set_scenario(e.value),
        ).classes("sim-select").props("dense outlined")
        ui.select(
            {
                SimulatorMode.practice.value: "Practice Mode",
                SimulatorMode.test.value: "Test Mode",
            },
            value=mode["value"],
            on_change=lambda e: set_mode(e.value),
        ).classes("sim-mode").props("dense outlined")
        ui.button("Random scenario", on_click=lambda: set_scenario(random.choice(scenarios).id if scenarios else ""))

    with ui.row().classes("sim-grid"):
        left = ui.column().classes("sim-left")
        center = ui.column().classes("sim-center")
        right = ui.column().classes("sim-right")

    def render_panels() -> None:
        left.clear()
        center.clear()
        right.clear()
        scenario = current_scenario()
        if not scenario:
            left.label("No scenarios")
            return

        step_index = int(state["step"])
        step = scenario.steps[step_index]
        summary = cast(GradeResult | None, state["summary"])

        with left:
            ui.label("Scenario Context").classes("panel-title")
            with ui.column().classes("sim-panel"):
                ui.label(scenario.context.what_is_happening).classes("context-main")
                ui.label(f"Concerns: {scenario.context.concerns}")
                ui.label(f"Role: {scenario.context.user_role}")
                ui.label(f"Known vessels: {', '.join(scenario.context.known_vessels) or 'not stated'}")
                ui.label(f"Position: {scenario.context.position or 'unknown'}")
                ui.label(f"Risk: {scenario.context.risk_level}")
                ui.label(f"Objective: {step.objective or scenario.context.current_objective}")
            with ui.column().classes("sim-panel"):
                ui.label("Commands").classes("panel-title-small")
                with ui.row().classes("command-row"):
                    ui.button("Get hint", on_click=give_hint)
                    ui.button("Show Correct Sequence", on_click=show_correct_sequence)
                    ui.button("Retry Step", on_click=retry_step)
                ui.label("Practice gives live correctness feedback. Test mode withholds correctness until finish.").classes("helper-text")
            with ui.column().classes("sim-panel"):
                ui.label("Procedural Checklist").classes("panel-title-small")
                for index, item in enumerate(scenario.steps):
                    prefix = "NOW" if index == step_index else ("DONE" if index < step_index else "NEXT")
                    ui.label(f"{prefix}: {index + 1}. {item.title}")
            with ui.column().classes("sim-panel"):
                ui.label("Initial Conditions").classes("panel-title-small")
                for condition in scenario.initial_conditions:
                    ui.label(f"- {condition}")

        with center:
            ui.label("Physical VHF Radio").classes("panel-title")
            RadioPanel(
                on_action=add_action,
                on_change=render_panels,
                on_feedback=add_radio_feedback,
                state=radio_state,
                dsc_mode="TEST" if current_mode() == SimulatorMode.test else "WATCH",
            ).render()
            with ui.row().classes("command-row"):
                ui.button("Next step", on_click=next_step)
                ui.button("Finish scenario", on_click=finish)

        with right:
            ui.label("Live Feedback").classes("panel-title")
            with ui.column().classes("sim-panel"):
                ui.label(str(state["feedback"]) or "No feedback yet.").classes("feedback-text")
                ui.label(f"Mode: {'Practice' if current_mode() == SimulatorMode.practice else 'Test'}")
                ui.label(f"Step: {step_index + 1}/{len(scenario.steps)}")
                ui.label(f"Mistakes: {state['mistakes']}")
                if summary:
                    ui.label(f"Device penalties: {state['device_mistakes']}")
                ui.label(f"Assisted: {'yes' if state['assisted'] else 'no'}")
                if summary:
                    ui.separator()
                    ui.label(f"Score: {summary.score}/100")
                    ui.label(f"Result: {'PASS' if summary.passed else 'FAIL'}")
            with ui.column().classes("sim-panel transcript-panel"):
                ui.label("Transcript").classes("panel-title-small")
                for entry in transcript()[-24:]:
                    ui.label(entry.as_text()).classes("transcript-entry")
            if state["show_sequence"]:
                with ui.column().classes("sim-panel sequence-panel"):
                    ui.label("Correct Sequence").classes("panel-title-small")
                    for line in correct_sequence_lines(scenario):
                        ui.label(line).classes("sequence-line")

    if scenarios:
        set_scenario(selected["id"])
