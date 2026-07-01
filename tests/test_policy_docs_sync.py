"""Tests for synchronized root policy documents."""

from __future__ import annotations

import pathlib
import unittest


class TestPolicyDocsSync(unittest.TestCase):
    def test_agents_and_claude_docs_are_identical(self) -> None:
        root = pathlib.Path(__file__).resolve().parents[1]
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        claude = (root / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertEqual(agents, claude)

    def test_legacy_policy_docs_are_removed(self) -> None:
        root = pathlib.Path(__file__).resolve().parents[1]
        self.assertFalse((root / "gemini.md").exists())
        self.assertFalse((root / "claude.md").exists())
