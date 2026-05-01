"""Learn page with lessons, checklists, glossary, and quick quizzes."""

from nicegui import ui


LESSONS = [
    (
        "Mayday",
        "Use MAYDAY for grave and imminent danger to a vessel or person. Include the priority signal, vessel name, position, nature of distress, assistance required, and persons onboard.",
    ),
    (
        "Mayday Relay",
        "Relay a MAYDAY only when a distress call is not acknowledged or the distressed station cannot communicate effectively. Listen first to avoid blocking a coast station.",
    ),
    (
        "Pan-Pan",
        "Use PAN-PAN for urgent situations that need priority handling but are not immediately life-threatening, such as engine failure near traffic or serious medical advice.",
    ),
    (
        "Securite",
        "Use SECURITE for important safety information such as hazards to navigation or weather warnings. Keep the initial call short and move details off Channel 16 when appropriate.",
    ),
    (
        "Routine calls",
        "Routine calls identify the called station and your vessel, establish contact, then move to a working channel for longer traffic.",
    ),
    (
        "DSC basics",
        "Digital Selective Calling sends alerts with vessel identity and, when connected, position. Channel 70 is for DSC data only, not voice.",
    ),
    (
        "Channel 16",
        "Channel 16 is for distress, urgency, safety, and calling. Keep it clear by moving routine working traffic to another channel.",
    ),
    (
        "Channel 70",
        "Channel 70 is DSC-only. Do not press PTT or transmit voice messages on Channel 70.",
    ),
    (
        "Working channels",
        "After contact, switch to an appropriate working channel for routine traffic. Confirm the channel before leaving Channel 16.",
    ),
    (
        "SAR assistance",
        "When SAR requests assistance, listen carefully, acknowledge only if you can help, and avoid interfering with command traffic.",
    ),
    (
        "Distress acknowledgement",
        "Acknowledge distress only when appropriate. If a coast station responds, maintain radio discipline and follow instructions.",
    ),
    (
        "False alerts",
        "Cancel accidental DSC or voice distress alerts immediately using the same channel and give your vessel identity and position.",
    ),
    (
        "Radio discipline",
        "Listen before transmitting, keep messages concise, use plain language, and release PTT promptly.",
    ),
    (
        "Phonetic alphabet",
        "Use standard phonetics for clarity when spelling vessel names, call signs, or difficult words.",
    ),
]

GLOSSARY = {
    "MAYDAY": "Distress signal for grave and imminent danger.",
    "PAN-PAN": "Urgency signal for serious but non-distress situations.",
    "SECURITE": "Safety signal for navigation or weather information.",
    "GMDSS": "Global Maritime Distress and Safety System.",
    "DSC": "Digital Selective Calling for marine radio alerts.",
    "MMSI": "Maritime Mobile Service Identity number.",
    "PTT": "Push-to-talk control. Hold while speaking, release to listen.",
    "Channel 16": "156.8 MHz voice distress, urgency, safety, and calling.",
    "Channel 70": "156.525 MHz DSC-only channel with no voice traffic.",
}

CHECKLISTS = {
    "Distress voice call": [
        "Select Channel 16.",
        "Say MAYDAY three times.",
        "Give vessel name and position.",
        "State nature of distress and assistance required.",
        "Give persons onboard and any other critical information.",
        "Release PTT and listen.",
    ],
    "Urgency call": [
        "Select Channel 16 or appropriate calling channel.",
        "Say PAN-PAN three times.",
        "Identify station called and your vessel.",
        "Give position, problem, and assistance requested.",
        "Release PTT and listen.",
    ],
    "Routine call": [
        "Listen before transmitting.",
        "Call the station and identify your vessel.",
        "Keep Channel 16 exchange brief.",
        "Agree a working channel.",
        "Move and continue on the working channel.",
    ],
}

QUIZ = [
    ("Can you transmit voice on Channel 70?", "No. Channel 70 is DSC-only."),
    ("A vessel is flooding and may be abandoned. Which priority?", "MAYDAY."),
    ("Engine failure near traffic, no immediate danger to life. Which priority?", "PAN-PAN."),
    ("Floating debris in a fairway. Which priority?", "SECURITE."),
]


def render() -> None:
    ui.label("Learn").classes("text-h4")
    with ui.tabs().classes("w-full") as tabs:
        lessons_tab = ui.tab("Lessons")
        glossary_tab = ui.tab("Glossary")
        checklists_tab = ui.tab("Checklists")
        quiz_tab = ui.tab("Quiz")
    with ui.tab_panels(tabs, value=lessons_tab).classes("w-full"):
        with ui.tab_panel(lessons_tab):
            with ui.column().classes("w-full gap-2"):
                for title, text in LESSONS:
                    with ui.card().classes("w-full"):
                        ui.label(title).classes("text-h6")
                        ui.label(text)
        with ui.tab_panel(glossary_tab):
            with ui.column().classes("w-full gap-2"):
                for term, definition in GLOSSARY.items():
                    with ui.card().classes("w-full"):
                        ui.label(term).classes("text-h6")
                        ui.label(definition)
        with ui.tab_panel(checklists_tab):
            with ui.column().classes("w-full gap-2"):
                for title, items in CHECKLISTS.items():
                    with ui.card().classes("w-full"):
                        ui.label(title).classes("text-h6")
                        for item in items:
                            ui.label(f"- {item}")
        with ui.tab_panel(quiz_tab):
            with ui.column().classes("w-full gap-2"):
                for question, answer in QUIZ:
                    with ui.expansion(question).classes("w-full"):
                        ui.label(answer)
