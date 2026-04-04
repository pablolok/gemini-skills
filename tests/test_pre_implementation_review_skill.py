"""Tests for the pre-implementation review skill."""

from __future__ import annotations

import os
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from install import SkillInstaller


class TestPreImplementationReviewSkill(unittest.TestCase):
    def setUp(self) -> None:
        self.installer = SkillInstaller("published", lambda _config: {})

    def test_skill_is_listed_in_published_workflow_skills(self) -> None:
        available = self.installer.get_available_skills()
        self.assertIn("workflow", available)
        self.assertIn("pre-implementation-review", available["workflow"])

    def test_codex_bridge_exists(self) -> None:
        bridge_path = os.path.join(".codex", "skills", "pre-implementation-review", "SKILL.md")
        self.assertTrue(os.path.exists(bridge_path))

        with open(bridge_path, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn(".gemini/skills/pre-implementation-review/SKILL.md", content)

    def test_skill_recommends_enums_over_raw_numeric_codes(self) -> None:
        skill_path = os.path.join("skills", "pre-implementation-review", "SKILL.md")

        with open(skill_path, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn("numeric state/category/status codes", content)
        self.assertIn("Prefer enums or typed named constants over raw numeric codes", content)
