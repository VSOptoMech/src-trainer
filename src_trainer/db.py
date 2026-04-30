"""SQLite database utilities for src-trainer."""

from pathlib import Path
import sqlite3

DB_PATH = Path("src_trainer.db")


def init_db() -> None:
    """Initialize the local SQLite database file."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.commit()
