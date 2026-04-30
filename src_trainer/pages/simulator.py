"""Simulator page."""

from nicegui import ui


def render() -> None:
    ui.label("Simulator").classes("text-h4")
    ui.card().classes("w-full").props('flat bordered').tight()
    ui.label("Radio simulator coming soon.")
