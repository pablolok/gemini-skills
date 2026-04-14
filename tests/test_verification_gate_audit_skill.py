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

    def test_verification_gate_skill_blocks_warning_suppression_shortcuts(self) -> None:
        path = os.path.join("skills", "compliance-audit-verification-gates", "SKILL.md")
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn("Warning-free status must come from fixing the underlying issue", content)
        self.assertIn("`#pragma warning disable`", content)
        self.assertIn("`NoWarn`", content)
        self.assertIn("suppression mechanisms", content)
        self.assertIn("Entity Framework migration files under `Migrations/`", content)

    def test_verification_gate_skill_blocks_unrequested_removals(self) -> None:
        path = os.path.join("skills", "compliance-audit-verification-gates", "SKILL.md")
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn("Inspect the diff for removals or behavior-reducing edits", content)
        self.assertIn("Treat unexplained removals as regressions", content)
        self.assertIn("removed functionality without an explicit request", content)

    def test_verification_gate_skill_allows_generated_migration_suppressions(self) -> None:
        path = os.path.join("skills", "compliance-audit-verification-gates", "SKILL.md")
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn("generated Entity Framework migration files under `Migrations/`", content)
        self.assertIn("limited to that generated migration code", content)
