from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.project_analyzer import build_index


class TestProjectAnalyzer(unittest.TestCase):
    def test_minimal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.py").write_text("import os\n\nclass A: pass\n\ndef f():\n    return 1\n", encoding="utf-8")
            data = build_index(root, excludes=set())
            self.assertIn("meta", data)
            self.assertGreaterEqual(data["stats"]["files_total"], 1)
            self.assertGreaterEqual(data["stats"]["symbols_total"], 2)
            self.assertGreaterEqual(data["stats"]["imports_total"], 1)


if __name__ == "__main__":
    unittest.main()
