"""Settings and quit guidance page."""

from nicegui import ui

from src_trainer.db import DB_PATH


def render() -> None:
    ui.label("Settings / Quit").classes("text-h4")
    with ui.column().classes("w-full gap-3"):
        ui.label("Local data").classes("text-h6")
        ui.label(f"Progress database: {DB_PATH}")
        ui.label("SRC Trainer runs locally with no login, cloud service, or external API.")
        ui.separator()
        ui.label("Quit").classes("text-h6")
        ui.label("Close this browser tab or stop the terminal process with Ctrl+C.")
        ui.button("Show quit instruction", on_click=lambda: ui.notify("Close the browser tab or press Ctrl+C in the terminal."))
