"""Dashboard page."""

from nicegui import ui


def render() -> None:
    ui.label("SRC Trainer Dashboard").classes("text-h4")
    with ui.row():
        ui.button("Start Learning", on_click=lambda: ui.navigate.to("/learn"))
        ui.button("Open Simulator", on_click=lambda: ui.navigate.to("/simulator"))
        ui.button("View Progress", on_click=lambda: ui.navigate.to("/progress"))
