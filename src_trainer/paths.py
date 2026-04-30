"""Filesystem path helpers for local user data."""

from __future__ import annotations

import os
import sys
from pathlib import Path


APP_DIR_NAME = "src-trainer"
DB_FILE_NAME = "src_trainer.db"


def get_user_data_dir() -> Path:
    """Return a per-user writable data directory for this app."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / APP_DIR_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_DIR_NAME
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / APP_DIR_NAME
    return Path.home() / ".local" / "share" / APP_DIR_NAME


def get_db_path() -> Path:
    """Return SQLite path under the user data directory."""
    return get_user_data_dir() / DB_FILE_NAME
