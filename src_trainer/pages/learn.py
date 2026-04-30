"""Learn page."""

from nicegui import ui


def render() -> None:
    ui.label("Learn").classes("text-h4")
    ui.label("Placeholder lessons:")
    with ui.column():
        ui.label("- Distress, Urgency, and Safety calls")
        ui.label("- DSC basics")
        ui.label("- Channel usage and procedure words")
