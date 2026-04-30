"""Simulator page."""

from nicegui import ui

from src_trainer.resources import list_scenarios


def render() -> None:
    scenarios = list_scenarios()

    ui.label("Simulator").classes("text-h4")
    with ui.card().classes("w-full").props('flat bordered'):
        ui.label("Radio simulator scenario catalog")
        if scenarios:
            for scenario in scenarios:
                ui.label(f"- {scenario.get('title', scenario.get('id', 'Untitled scenario'))}")
        else:
            ui.label("No scenarios packaged.")
