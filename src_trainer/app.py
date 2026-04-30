"""NiceGUI application entrypoint."""

from nicegui import ui

from src_trainer.db import init_db
from src_trainer.pages import dashboard, glossary, learn, progress, simulator


def _navbar() -> None:
    with ui.header().classes("items-center justify-between"):
        ui.label("SRC Trainer").classes("text-h6")
        with ui.row():
            ui.button("Dashboard", on_click=lambda: ui.navigate.to("/"))
            ui.button("Learn", on_click=lambda: ui.navigate.to("/learn"))
            ui.button("Simulator", on_click=lambda: ui.navigate.to("/simulator"))
            ui.button("Progress", on_click=lambda: ui.navigate.to("/progress"))
            ui.button("Glossary", on_click=lambda: ui.navigate.to("/glossary"))


def _page_container(renderer) -> None:
    _navbar()
    with ui.column().classes("p-4 gap-4"):
        renderer()


@ui.page("/")
def index_page() -> None:
    _page_container(dashboard.render)


@ui.page("/learn")
def learn_page() -> None:
    _page_container(learn.render)


@ui.page("/simulator")
def simulator_page() -> None:
    _page_container(simulator.render)


@ui.page("/progress")
def progress_page() -> None:
    _page_container(progress.render)


@ui.page("/glossary")
def glossary_page() -> None:
    _page_container(glossary.render)


def main() -> None:
    init_db()
    ui.run(host="127.0.0.1", port=8080, reload=False, show=True)


if __name__ in {"__main__", "__mp_main__"}:
    main()
