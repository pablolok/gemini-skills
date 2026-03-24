"""Tests for verification-gate audit skill registration and workflow policy."""

from __future__ import annotations

import os
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from install import SkillInstaller


class TestVerificationGateAuditSkill(unittest.TestCase):
    def setUp(self) -> None:
        self.installer = SkillInstaller("published", lambda _config: {})

    def test_verification_gate_audit_is_listed_in_published_audit_skills(self) -> None:
        available = self.installer.get_available_skills()
        self.assertIn("audit", available)
        self.assertIn("compliance-audit-verification-gates", available["audit"])

    def test_orchestrator_mentions_verification_gate_audit(self) -> None:
        path = os.path.join("skills", "compliance-audit-orchestrator", "SKILL.md")
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn("Verification Gates Audit", content)
        self.assertIn("compliance-audit-verification-gates", content)

    def test_verification_gate_skill_is_read_only_for_skill_infrastructure(self) -> None:
        path = os.path.join("skills", "compliance-audit-verification-gates", "SKILL.md")
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn("read-only with respect to skill infrastructure", content)
        self.assertIn("warning-free build", content)
