"""Glossary page."""

from nicegui import ui


def render() -> None:
    ui.label("Glossary").classes("text-h4")
    ui.label("Glossary is currently empty.")
