"""SQLite database utilities for src-trainer."""

from __future__ import annotations

import json
import sqlite3

from src_trainer.paths import get_db_path

DB_PATH = get_db_path()


def init_db() -> None:
    """Initialize the local SQLite database file."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id TEXT NOT NULL,
                score INTEGER NOT NULL,
                mistakes INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                transcript TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                scenario_id TEXT PRIMARY KEY,
                best_score INTEGER NOT NULL DEFAULT 0,
                attempts_count INTEGER NOT NULL DEFAULT 0,
                passed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()


def record_attempt(scenario_id: str, score: int, mistakes: int, passed: bool, transcript: list[str]) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO attempts (scenario_id, score, mistakes, passed, transcript) VALUES (?, ?, ?, ?, ?)",
            (scenario_id, score, mistakes, 1 if passed else 0, json.dumps(transcript)),
        )
        conn.execute(
            """
            INSERT INTO progress (scenario_id, best_score, attempts_count, passed)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(scenario_id) DO UPDATE SET
                best_score = MAX(progress.best_score, excluded.best_score),
                attempts_count = progress.attempts_count + 1,
                passed = MAX(progress.passed, excluded.passed)
            """,
            (scenario_id, score, 1 if passed else 0),
        )
        conn.commit()


def get_progress_rows() -> list[dict[str, int | str]]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT scenario_id, best_score, attempts_count, passed FROM progress ORDER BY scenario_id"
        ).fetchall()
    return [dict(row) for row in rows]
