"""Checks for local-distribution reliability without launching NiceGUI."""

from __future__ import annotations

import ast
import tempfile
from pathlib import Path
import unittest

import src_trainer.db as db
from src_trainer.paths import get_db_path, get_user_data_dir

REPO_ROOT = Path(__file__).resolve().parent.parent


class LocalDistributionTests(unittest.TestCase):
    def test_db_path_is_under_user_data_dir(self) -> None:
        self.assertEqual(get_db_path().parent, get_user_data_dir())
        self.assertEqual(get_db_path().name, "src_trainer.db")

    def test_init_db_creates_tables_in_writable_location(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_db = Path(tmp) / "src_trainer.db"
            original = db.DB_PATH
            try:
                db.DB_PATH = temp_db
                db.init_db()
                self.assertTrue(temp_db.exists())
                rows = db.get_progress_rows()
                self.assertEqual(rows, [])
            finally:
                db.DB_PATH = original

    def test_app_has_port_check_before_ui_run(self) -> None:
        module = ast.parse((REPO_ROOT / "src_trainer" / "app.py").read_text(encoding="utf-8"))
        fn_names = {node.name for node in ast.walk(module) if isinstance(node, ast.FunctionDef)}
        self.assertIn("_can_bind_port", fn_names)


if __name__ == "__main__":
    unittest.main()
