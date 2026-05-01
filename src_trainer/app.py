"""NiceGUI application entrypoint."""

import socket

from nicegui import ui

from src_trainer.db import DB_PATH, init_db
from src_trainer.pages import dashboard, learn, progress, settings, simulator


def _navbar() -> None:
    with ui.header().classes("items-center justify-between"):
        ui.label("SRC Trainer").classes("text-h6")
        with ui.row():
            ui.button("Dashboard", on_click=lambda: ui.navigate.to("/"))
            ui.button("Learn", on_click=lambda: ui.navigate.to("/learn"))
            ui.button("Simulator", on_click=lambda: ui.navigate.to("/simulator"))
            ui.button("Progress", on_click=lambda: ui.navigate.to("/progress"))
            ui.button("Settings/Quit", on_click=lambda: ui.navigate.to("/settings"))


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
    ui.navigate.to("/learn")


@ui.page("/settings")
def settings_page() -> None:
    _page_container(settings.render)


def _can_bind_port(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def main() -> None:
    init_db()
    host = "127.0.0.1"
    port = 8080
    if not _can_bind_port(host, port):
        print(f"Port {port} is already in use on {host}. Please close the other app and try again.")
        print(f"Your local progress database is at: {DB_PATH}")
        return
    print(f"Using local progress database: {DB_PATH}")
    ui.run(host=host, port=port, reload=False, show=True)


if __name__ in {"__main__", "__mp_main__"}:
    main()
