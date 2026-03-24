"""Tests for Angular audit skill registration."""

from __future__ import annotations

import os
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from install import SkillInstaller


class TestAngularAuditSkill(unittest.TestCase):
    def setUp(self) -> None:
        self.installer = SkillInstaller("published", lambda _config: {})

    def test_angular_audit_is_listed_in_published_audit_skills(self) -> None:
        available = self.installer.get_available_skills()
        self.assertIn("audit", available)
        self.assertIn("compliance-audit-angular", available["audit"])

    def test_orchestrator_mentions_angular_audit(self) -> None:
        path = os.path.join("skills", "compliance-audit-orchestrator", "SKILL.md")
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn("Angular Audit", content)
        self.assertIn("compliance-audit-angular", content)

    def test_audit_skills_are_read_only_for_skill_infrastructure(self) -> None:
        angular_path = os.path.join("skills", "compliance-audit-angular", "SKILL.md")
        orchestrator_path = os.path.join("skills", "compliance-audit-orchestrator", "SKILL.md")

        with open(angular_path, "r", encoding="utf-8") as handle:
            angular_content = handle.read()
        with open(orchestrator_path, "r", encoding="utf-8") as handle:
            orchestrator_content = handle.read()

        self.assertIn("read-only with respect to skill infrastructure", angular_content)
        self.assertIn("read-only with respect to skill infrastructure", orchestrator_content)
