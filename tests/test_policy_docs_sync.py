"""Tests for synchronized root policy documents."""

from __future__ import annotations

import pathlib
import unittest


class TestPolicyDocsSync(unittest.TestCase):
    def test_agents_gemini_and_claude_docs_are_identical(self) -> None:
        root = pathlib.Path(__file__).resolve().parents[1]
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        gemini = (root / "gemini.md").read_text(encoding="utf-8")
        claude = (root / "claude.md").read_text(encoding="utf-8")

        self.assertEqual(agents, gemini)
        self.assertEqual(agents, claude)
