"""Reusable marine VHF radio panel UI component."""

from __future__ import annotations

from collections.abc import Callable

from nicegui import ui

from src_trainer.components.radio_state import MAX_CHANNEL, MIN_CHANNEL, RadioCommand, RadioState
from src_trainer.models import RadioAction


class RadioDisplay:
    """LCD display for the simulated VHF radio."""

    def __init__(self, state: RadioState, *, dsc_mode: str = "WATCH") -> None:
        self.state = state
        self.dsc_mode = dsc_mode

    def render(self) -> None:
        power_class = "radio-lcd-on" if self.state.power else "radio-lcd-off"
        with ui.column().classes(f"radio-lcd {power_class}"):
            if not self.state.power:
                with ui.element("div").classes("radio-off-screen"):
                    ui.label("OFF").classes("radio-off-label")
                    ui.label("Press PWR to energize set").classes("radio-off-hint")
                return

            with ui.row().classes("radio-lcd-status"):
                ui.label("TX").classes(f"lcd-pill {'active' if self.state.tx else ''}")
                ui.label("RX").classes(f"lcd-pill {'active' if self.state.rx else ''}")
                ui.label("HI" if self.state.hi_power else "LO").classes("lcd-pill active")
                ui.label("STBY" if self.state.standby else "TX MODE").classes("lcd-pill")
                ui.label("SCAN").classes(f"lcd-pill {'active' if self.state.scan else ''}")
                ui.label("DW").classes(f"lcd-pill {'active' if self.state.dual_watch else ''}")
                ui.label("WX").classes(f"lcd-pill {'active' if self.state.weather_mode else ''}")
                ui.label(self.dsc_mode).classes("lcd-pill")
            with ui.row().classes("radio-lcd-main"):
                with ui.column().classes("radio-lcd-meta"):
                    ui.label("25W  USA")
                    ui.label("25 48N")
                    ui.label("080 12W")
                    ui.label("12:00 LT")
                ui.label(f"{self.state.channel:02d}").classes("radio-channel")
            with ui.row().classes("radio-soft-labels"):
                for label in ("SCAN", "DW", "HI/LO", "CH/WX"):
                    ui.label(label).classes("radio-soft-label")


class RadioControls:
    """Clickable controls around the display."""

    def __init__(
        self,
        state: RadioState,
        *,
        on_command: Callable[[Callable[[], RadioCommand | None]], None],
        on_change: Callable[[Callable[[], None]], None],
    ) -> None:
        self.state = state
        self.on_command = on_command
        self.on_change = on_change

    def render_left(self) -> None:
        with ui.column().classes("radio-left"):
            with ui.column().classes("radio-speaker"):
                for _ in range(12):
                    ui.element("span")
            self._command_button(
                "DISTRESS COVER",
                self.state.toggle_distress_cover,
                "radio-distress-cover open" if self.state.distress_cover_open else "radio-distress-cover",
            )
            self._command_button("DISTRESS", self.state.hold_distress, "radio-distress")

    def render_right(self) -> None:
        with ui.column().classes("radio-right"):
            self._command_button("16/C", self.state.press_ch16, "radio-ch16")
            with ui.grid(columns=2).classes("radio-control-grid"):
                self._state_button("CH +", self.state.channel_up, "radio-key")
                self._state_button("CH -", self.state.channel_down, "radio-key")
                self._command_button("SET CH", self.state.set_working_channel, "radio-key radio-key-wide")
            ui.number(
                "Channel",
                value=self.state.channel,
                min=MIN_CHANNEL,
                max=MAX_CHANNEL,
                on_change=lambda event: self.on_change(lambda: self.state.enter_channel(event.value)),
            ).classes("radio-channel-entry").props("dense outlined")
            self._command_button(
                "Power",
                self.state.toggle_power,
                f"radio-knob {'powered' if self.state.power else ''}",
            )

    def render_soft_keys(self) -> None:
        with ui.row().classes("radio-soft-buttons"):
            self._state_button(
                "SCAN",
                self.state.toggle_scan,
                f"radio-soft-button {'active' if self.state.scan else ''}",
            )
            self._state_button(
                "DW",
                self.state.toggle_dual_watch,
                f"radio-soft-button {'active' if self.state.dual_watch else ''}",
            )
            self._state_button(
                "HI/LO",
                self.state.toggle_hi_lo,
                "radio-soft-button",
            )
            self._state_button(
                "CH/WX",
                self.state.toggle_weather_mode,
                f"radio-soft-button {'active' if self.state.weather_mode else ''}",
            )

    def render_hand_mic(self) -> None:
        with ui.column().classes("radio-mic"):
            ui.label("Hand Mic").classes("radio-mic-title")
            with ui.row().classes("radio-mic-buttons"):
                self._command_button("PTT", self.state.hold_ptt, "radio-ptt")
                self._command_button("Release", self.state.release_ptt, "radio-release")
            ui.input(
                "Phrase to transmit",
                value=self.state.phrase,
                on_change=lambda event: setattr(self.state, "phrase", event.value or ""),
            ).classes("radio-phrase").props("outlined dense")
            self._command_button("Transmit phrase", self.state.transmit_phrase, "radio-transmit")

    def _command_button(
        self,
        label: str,
        command: Callable[[], RadioCommand | None],
        classes: str,
        *,
        disabled: bool = False,
    ) -> None:
        button = ui.button(label, on_click=lambda: self.on_command(command)).classes(classes).props("unelevated")
        if disabled:
            button.props("disable")

    def _state_button(
        self,
        label: str,
        mutation: Callable[[], None],
        classes: str,
        *,
        disabled: bool = False,
    ) -> None:
        button = ui.button(label, on_click=lambda: self.on_change(mutation)).classes(classes).props("unelevated")
        if disabled:
            button.props("disable")


class RadioPanel:
    """Render a clickable generic marine VHF/DSC style faceplate."""

    def __init__(
        self,
        *,
        state: RadioState,
        on_action: Callable[[RadioAction, str | None], None],
        on_change: Callable[[], None],
        on_feedback: Callable[[str, bool], None] | None = None,
        dsc_mode: str = "WATCH",
    ) -> None:
        self.state = state
        self.on_action = on_action
        self.on_change = on_change
        self.on_feedback = on_feedback or (lambda _message, _mistake: None)
        self.dsc_mode = dsc_mode

    def render(self) -> None:
        controls = RadioControls(
            self.state,
            on_command=self._handle_command,
            on_change=self._handle_state_change,
        )
        with ui.column().classes("radio-shell"):
            with ui.row().classes("radio-faceplate"):
                controls.render_left()
                with ui.column().classes("radio-center"):
                    ui.label("VHF Marine Radio").classes("radio-brand")
                    RadioDisplay(self.state, dsc_mode=self.dsc_mode).render()
                    controls.render_soft_keys()
                controls.render_right()
            controls.render_hand_mic()

    def _handle_command(self, command_factory: Callable[[], RadioCommand | None]) -> None:
        command = command_factory()
        self._emit_feedback()
        if command is None:
            self.on_change()
            return
        self.on_action(command.action, command.value)

    def _handle_state_change(self, mutation: Callable[[], None]) -> None:
        mutation()
        self._emit_feedback()
        self.on_change()

    def _emit_feedback(self) -> None:
        if self.state.last_feedback:
            self.on_feedback(self.state.last_feedback, self.state.last_mistake)
