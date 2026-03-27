"""Repository-level invariants for the root .gitignore file."""

from __future__ import annotations

import os
import unittest


class TestRepoGitignoreInvariant(unittest.TestCase):
    def test_root_gitignore_keeps_baseline_content_and_managed_block(self) -> None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        gitignore_path = os.path.join(repo_root, ".gitignore")

        with open(gitignore_path, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn("# Byte-compiled / optimized / DLL files", content)
        self.assertIn("__pycache__/", content)
        self.assertIn("# >>> skill-manager managed workspace files >>>", content)
        self.assertIn("# <<< skill-manager managed workspace files <<<", content)
        self.assertEqual(content.count("# >>> skill-manager managed workspace files >>>"), 1)
        self.assertFalse(content.lstrip().startswith("# >>> skill-manager managed workspace files >>>"))
