"""Learn page."""

from nicegui import ui

LESSONS = {
    "Mayday": "Use MAYDAY only for grave and imminent danger, then give vessel name, position, nature of distress, and assistance required.",
    "Pan-Pan": "Use PAN-PAN for urgent situations that are serious but not immediately life-threatening.",
    "Sécurité": "Use SÉCURITÉ for navigational or meteorological safety messages.",
    "Channels": "Channel 16 is calling/distress; Channel 70 is digital DSC alerting only.",
    "DSC basics": "DSC lets you send digital distress/urgency/safety alerts with MMSI identity and position data.",
}


def render() -> None:
    ui.label("Learn").classes("text-h4")
    for title, text in LESSONS.items():
        with ui.card().classes("w-full"):
            ui.label(title).classes("text-h6")
            ui.label(text)
