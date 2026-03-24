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
