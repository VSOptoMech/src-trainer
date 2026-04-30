"""Progress page."""

from nicegui import ui


def render() -> None:
    ui.label("Progress").classes("text-h4")
    ui.label("No training statistics yet.")
