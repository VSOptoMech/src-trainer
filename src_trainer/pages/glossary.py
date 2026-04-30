"""Glossary page."""

from nicegui import ui

GLOSSARY = {
    "Mayday": "International distress call for grave and imminent danger.",
    "Pan-Pan": "Urgency signal for important non-distress situations.",
    "Sécurité": "Safety signal for hazards to navigation or weather.",
    "GMDSS": "Global Maritime Distress and Safety System.",
    "DSC": "Digital Selective Calling used for digital marine VHF alerting.",
    "MMSI": "Maritime Mobile Service Identity number.",
    "Channel 16": "156.8 MHz voice distress, urgency, safety, and calling.",
    "Channel 70": "156.525 MHz DSC-only channel (no voice).",
}


def render() -> None:
    ui.label("Glossary").classes("text-h4")
    with ui.column().classes("w-full gap-2"):
        for term, definition in GLOSSARY.items():
            with ui.card().classes("w-full"):
                ui.label(term).classes("text-h6")
                ui.label(definition)
