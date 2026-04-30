"""Reusable marine VHF radio panel UI component."""

from __future__ import annotations

from collections.abc import Callable

from nicegui import ui

from src_trainer.models import RadioAction


class RadioPanel:
    """Render a clickable generic marine VHF/DSC style faceplate."""

    def __init__(
        self,
        *,
        on_action: Callable[[RadioAction, str | None], None],
        channel: str,
        powered: bool = True,
        tx_active: bool = False,
        rx_active: bool = True,
        hi_power: bool = True,
        dsc_mode: str = "WATCH",
    ) -> None:
        self.on_action = on_action
        self.channel = channel
        self.powered = powered
        self.tx_active = tx_active
        self.rx_active = rx_active
        self.hi_power = hi_power
        self.dsc_mode = dsc_mode
        self._distress_cover_open = False
        self._distress_cover = None

    def render(self) -> None:
        ui.add_head_html(
            """
            <style>
            .radio-faceplate{background:linear-gradient(160deg,#2a2f36,#171a20 45%,#0f1217);border:2px solid #404752;border-radius:14px;box-shadow:0 12px 24px rgba(0,0,0,.45),inset 0 1px 1px rgba(255,255,255,.08);padding:14px;color:#d7dde8;max-width:860px;width:100%}
            .radio-grid{display:grid;grid-template-columns:1.4fr 1.2fr;gap:12px}
            .lcd{background:#7d9a73;border:3px solid #2f372f;border-radius:8px;padding:8px 10px;color:#0f1a0e;box-shadow:inset 0 2px 4px rgba(0,0,0,.35);font-family:monospace}
            .ch{font-size:2rem;font-weight:700;letter-spacing:2px}
            .status{display:flex;gap:8px;font-size:.75rem;flex-wrap:wrap}
            .pill{padding:2px 6px;border-radius:999px;background:#2f353f;color:#b7c0cf;border:1px solid #4a5260}
            .pill.on{background:#13451f;color:#cbf9d1;border-color:#2d8650}
            .pill.warn{background:#4d120f;color:#ffd6d2;border-color:#c73c34}
            .keys,.soft{display:grid;gap:6px}
            .soft{grid-template-columns:repeat(4,minmax(0,1fr));margin-top:8px}
            .keybtn,.round,.ptt{background:linear-gradient(180deg,#5a6371,#39404b);border:1px solid #7c8797;border-bottom-color:#222a34;color:#f2f5fb;border-radius:8px;padding:8px 6px;text-align:center;cursor:pointer;user-select:none}
            .keybtn:hover,.round:hover,.ptt:hover{filter:brightness(1.08)}
            .keybtn:active,.round:active,.ptt:active{transform:translateY(1px);filter:brightness(.92)}
            .keypad{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
            .speaker{border:2px solid #303743;border-radius:10px;padding:10px;height:190px;background:#12161d;display:grid;grid-template-columns:repeat(8,1fr);gap:4px;align-content:start}
            .speaker i{height:4px;background:#2f3744;border-radius:3px;display:block}
            .danger{background:linear-gradient(180deg,#d3473f,#8f1f1d)!important;border-color:#f16f67!important;font-weight:700}
            .distress-cover{background:linear-gradient(180deg,#bd2f2f,#7d1919);border:1px solid #f08f8f;border-radius:8px;padding:8px;text-align:center;color:#ffe8e8;font-weight:700;cursor:pointer}
            .distress-cover.open{opacity:.5;transform:translateY(-3px)}
            .round-wrap{display:flex;gap:10px;margin-top:8px}
            .round{width:68px;height:68px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.75rem}
            .ptt{height:74px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;font-weight:700;background:linear-gradient(180deg,#ffd976,#c5971f);color:#2f2200}
            @media (max-width: 1024px){.radio-grid{grid-template-columns:1fr}.speaker{height:120px}}
            </style>
            """
        )
        with ui.column().classes("radio-faceplate"):
            ui.label("Marine VHF/DSC Radio").classes("text-caption text-blue-2")
            with ui.grid(columns=2).classes("radio-grid"):
                with ui.column():
                    with ui.column().classes("lcd"):
                        with ui.row().classes("justify-between items-end"):
                            ui.label("CH").classes("text-xs")
                            ui.label(self.channel).classes("ch")
                        with ui.row().classes("status"):
                            ui.label("TX").classes(f"pill {'on' if self.tx_active else ''}")
                            ui.label("RX").classes(f"pill {'on' if self.rx_active else ''}")
                            ui.label("PWR ON" if self.powered else "PWR OFF").classes(f"pill {'on' if self.powered else 'warn'}")
                            ui.label("HI" if self.hi_power else "LO").classes("pill")
                        ui.label(f"DSC/MENU: {self.dsc_mode}").classes("text-xs")
                    with ui.row().classes("soft"):
                        self._button("SCAN", RadioAction.CHANNEL_UP)
                        self._button("WATCH", RadioAction.MONITOR)
                        self._button("MENU", RadioAction.OPEN_DISTRESS_COVER)
                        self._button("BACK", RadioAction.CLOSE_DISTRESS_COVER)
                    with ui.row().classes("round-wrap"):
                        self._button("VOL", RadioAction.POWER_ON, "round")
                        self._button("SQL", RadioAction.MONITOR, "round")
                    with ui.column().classes("speaker"):
                        for _ in range(56):
                            ui.html("<i></i>")
                    self._button("PTT", RadioAction.HOLD_PTT, "ptt")
                    self._button("RELEASE", RadioAction.RELEASE_PTT, "keybtn")
                with ui.column().classes("keys"):
                    with ui.row().classes("gap-2"):
                        self._button("CH +", RadioAction.CHANNEL_UP)
                        self._button("CH -", RadioAction.CHANNEL_DOWN)
                        self._button("CH16", RadioAction.SELECT_CHANNEL_16, "keybtn danger")
                    self._button("SET WORK CH", RadioAction.SELECT_WORKING_CHANNEL)
                    self._button("POWER", RadioAction.POWER_ON)
                    self._button("MONITOR", RadioAction.MONITOR)
                    self._button("DISTRESS COVER", RadioAction.OPEN_DISTRESS_COVER, "distress-cover", is_cover=True)
                    self._button("DISTRESS", RadioAction.PRESS_DISTRESS, "keybtn danger")
                    with ui.grid(columns=3).classes("keypad"):
                        self._button("▲", RadioAction.CHANNEL_UP)
                        self._button("OK", RadioAction.SELECT_WORKING_CHANNEL)
                        self._button("▼", RadioAction.CHANNEL_DOWN)
                        self._button("◀", RadioAction.MONITOR)
                        self._button("MENU", RadioAction.OPEN_DISTRESS_COVER)
                        self._button("▶", RadioAction.MONITOR)

    def _button(self, label: str, action: RadioAction, extra: str = "keybtn", *, is_cover: bool = False) -> None:
        def handle_click() -> None:
            if is_cover:
                self._distress_cover_open = not self._distress_cover_open
                if self._distress_cover is not None:
                    self._distress_cover.classes(replace=f"distress-cover {'open' if self._distress_cover_open else ''}")
            self.on_action(action, None)

        element = ui.button(label, on_click=handle_click).classes(extra).props("unelevated")
        if is_cover:
            self._distress_cover = element
