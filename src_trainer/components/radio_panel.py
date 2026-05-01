"""Reusable marine VHF radio panel UI component."""

from __future__ import annotations

from collections.abc import Callable

from nicegui import ui

from src_trainer.components.radio_state import MAX_CHANNEL, MIN_CHANNEL, RadioCommand, RadioState
from src_trainer.models import RadioAction

_STYLES_ADDED = False


class RadioDisplay:
    """LCD display for the simulated VHF radio."""

    def __init__(self, state: RadioState, *, dsc_mode: str = "WATCH") -> None:
        self.state = state
        self.dsc_mode = dsc_mode

    def render(self) -> None:
        with ui.column().classes(f"radio-lcd {'radio-lcd-off' if not self.state.power else ''}"):
            if not self.state.power:
                ui.element("div").classes("radio-off-screen")
                return

            with ui.row().classes("radio-lcd-status"):
                ui.label("TX").classes(f"lcd-pill {'active' if self.state.tx else ''}")
                ui.label("RX").classes(f"lcd-pill {'active' if self.state.rx else ''}")
                ui.label("HI" if self.state.hi_power else "LO").classes("lcd-pill active")
                ui.label("STBY" if self.state.standby else "TX MODE").classes("lcd-pill")
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
                self._state_button("HI/LO", self.state.toggle_hi_lo, "radio-key")
                self._command_button("SET CH", self.state.set_working_channel, "radio-key")
            ui.number(
                "Channel",
                value=self.state.channel,
                min=MIN_CHANNEL,
                max=MAX_CHANNEL,
                on_change=lambda event: self.on_change(lambda: self.state.enter_channel(event.value)),
            ).classes("radio-channel-entry").props("dense outlined")
            self._command_button(
                "PWR",
                self.state.toggle_power,
                f"radio-knob {'powered' if self.state.power else ''}",
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
        _ensure_styles()
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
                    with ui.row().classes("radio-soft-buttons"):
                        for _ in range(4):
                            ui.element("span")
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


def _ensure_styles() -> None:
    global _STYLES_ADDED
    if _STYLES_ADDED:
        return
    _STYLES_ADDED = True
    ui.add_head_html(
        """
        <style>
        .radio-shell{width:min(100%,920px);margin-inline:auto;gap:12px}
        .radio-faceplate{width:100%;align-items:stretch;gap:14px;padding:18px;border-radius:22px;background:linear-gradient(160deg,#252a33,#11151d 55%,#090b10);border:2px solid #414855;box-shadow:0 18px 32px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.08);color:#e7edf7}
        .radio-left{width:150px;gap:10px;justify-content:space-between}
        .radio-speaker{height:154px;padding:12px;border-radius:12px;background:#07090d;border:1px solid #313845;gap:7px;justify-content:center}
        .radio-speaker span{display:block;height:8px;border-radius:999px;background:linear-gradient(90deg,#2a303a,#11151b)}
        .radio-distress-cover,.radio-distress{width:100%;min-height:42px;border-radius:8px;font-size:.72rem;font-weight:700;white-space:normal}
        .radio-distress-cover{background:linear-gradient(180deg,#b73535,#751b1b)!important;border:1px solid #ec7979;color:#ffe8e8!important}
        .radio-distress-cover.open{transform:translateY(-2px);filter:brightness(1.12)}
        .radio-distress{background:linear-gradient(180deg,#ff604d,#9e221c)!important;border:1px solid #ff8b7e;color:#fff5f2!important}
        .radio-center{flex:1;min-width:300px;gap:8px}
        .radio-brand{font-size:.78rem;text-transform:uppercase;letter-spacing:0;color:#cfd6e2;text-align:center}
        .radio-lcd{min-height:210px;border-radius:12px;padding:12px 14px;background:linear-gradient(180deg,#efb74d,#d69528);border:4px solid #15191f;box-shadow:inset 0 3px 8px rgba(0,0,0,.35);color:#161007;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
        .radio-lcd-off{background:#171a14;color:transparent}
        .radio-off-screen{height:178px;border-radius:6px;background:linear-gradient(180deg,#11140f,#070807)}
        .radio-lcd-status{align-items:center;gap:6px;font-size:.75rem;flex-wrap:wrap}
        .lcd-pill{padding:2px 6px;border-radius:3px;background:rgba(31,23,7,.2);border:1px solid rgba(31,23,7,.35);font-weight:700}
        .lcd-pill.active{background:#201705;color:#f1b84d}
        .radio-lcd-main{align-items:center;justify-content:space-between;gap:16px;flex:1}
        .radio-lcd-meta{gap:0;font-size:1rem;line-height:1.15;font-weight:700}
        .radio-channel{font-size:7rem;line-height:.9;font-weight:900;letter-spacing:0;color:#161007}
        .radio-soft-labels{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin-top:auto}
        .radio-soft-label{padding:3px 4px;text-align:center;border-radius:3px;background:#201705;color:#f1b84d;font-size:.78rem;font-weight:700}
        .radio-soft-buttons{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;padding-inline:8px}
        .radio-soft-buttons span{height:24px;border-radius:8px;background:linear-gradient(180deg,#6a707b,#353b45);border:1px solid #9299a6;box-shadow:inset 0 -2px 2px rgba(0,0,0,.4)}
        .radio-right{width:185px;align-items:center;justify-content:space-between;gap:10px}
        .radio-control-grid{width:100%;gap:8px}
        .radio-key,.radio-ch16,.radio-knob,.radio-ptt,.radio-release,.radio-transmit{border:1px solid #838b98;color:#f6f8fc!important;background:linear-gradient(180deg,#5b6370,#303741)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.18);font-weight:700}
        .radio-key{min-height:42px;border-radius:9px;font-size:.78rem}
        .radio-channel-entry{width:100%}
        .radio-ch16{width:74px;height:74px;border-radius:999px!important;background:linear-gradient(180deg,#4f93d8,#1760a9)!important;border-color:#9ed1ff!important}
        .radio-knob{width:96px;height:96px;border-radius:999px!important;background:radial-gradient(circle at 35% 30%,#8c94a2,#252b33 62%,#0a0d11)!important;border:4px solid #68707c}
        .radio-knob.powered{box-shadow:0 0 0 3px rgba(239,183,77,.2),inset 0 1px 0 rgba(255,255,255,.18)}
        .radio-mic{width:100%;padding:12px;border-radius:14px;background:#151922;border:1px solid #3a424f;color:#e7edf7}
        .radio-mic-title{font-size:.82rem;text-transform:uppercase;letter-spacing:0;color:#cfd6e2}
        .radio-mic-buttons{gap:8px;align-items:center}
        .radio-ptt{min-width:112px;min-height:54px;border-radius:12px;background:linear-gradient(180deg,#f1c45b,#a87918)!important;color:#231900!important}
        .radio-release,.radio-transmit{min-height:42px;border-radius:9px}
        .radio-phrase{width:100%;max-width:520px}
        @media (max-width: 900px){
          .radio-faceplate{flex-direction:column}
          .radio-left,.radio-right{width:100%;flex-direction:row;align-items:center}
          .radio-speaker{width:40%;min-width:160px}
          .radio-control-grid{max-width:260px}
          .radio-channel{font-size:5.5rem}
        }
        @media (max-width: 560px){
          .radio-left,.radio-right{flex-direction:column}
          .radio-speaker{width:100%}
          .radio-lcd-main{align-items:flex-start}
          .radio-channel{font-size:4.2rem}
        }
        </style>
        """
    )
