"""Progress page."""

from nicegui import ui

from src_trainer.db import get_progress_rows


def render() -> None:
    ui.label("Progress").classes("text-h4")
    rows = get_progress_rows()
    if not rows:
        ui.label("No attempts recorded yet.")
        return
    columns = [
        {"name": "scenario_id", "label": "Scenario", "field": "scenario_id"},
        {"name": "best_score", "label": "Best Score", "field": "best_score"},
        {"name": "attempts_count", "label": "Attempts", "field": "attempts_count"},
        {"name": "passed", "label": "Passed", "field": "passed"},
    ]
    ui.table(columns=columns, rows=rows, row_key="scenario_id").classes("w-full")
