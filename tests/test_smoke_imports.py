"""Static smoke checks for imports and entrypoint wiring without importing NiceGUI."""

from __future__ import annotations

from pathlib import Path
import ast
import tomllib
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent


class StaticSmokeTests(unittest.TestCase):
    def _parse(self, relative_path: str) -> ast.AST:
        return ast.parse((REPO_ROOT / relative_path).read_text(encoding="utf-8"))

    def test_project_script_entrypoint(self) -> None:
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        scripts = pyproject.get("project", {}).get("scripts", {})
        self.assertEqual(scripts.get("src-trainer"), "src_trainer.app:main")

    def test_nicegui_imports_only_from_nicegui(self) -> None:
        for path in (REPO_ROOT / "src_trainer").rglob("*.py"):
            module = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(module):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(
                            alias.name.startswith("nicegui."),
                            f"Unexpected NiceGUI import style in {path}: {alias.name}",
                        )
                if isinstance(node, ast.ImportFrom) and node.module:
                    if "nicegui" in node.module:
                        self.assertEqual(
                            node.module,
                            "nicegui",
                            f"Unexpected NiceGUI import source in {path}: {node.module}",
                        )

    def test_app_has_main_and_routes(self) -> None:
        app_module = self._parse("src_trainer/app.py")
        function_names = {
            node.name for node in ast.walk(app_module) if isinstance(node, ast.FunctionDef)
        }
        for expected in {
            "main",
            "index_page",
            "learn_page",
            "simulator_page",
            "progress_page",
            "glossary_page",
        }:
            self.assertIn(expected, function_names)


if __name__ == "__main__":
    unittest.main()
