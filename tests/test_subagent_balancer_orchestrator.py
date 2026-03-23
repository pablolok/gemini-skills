"""Tests for the balancing orchestrator router."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "skills"
    / "subagent-balancer-orchestrator"
    / "scripts"
    / "select_balancer.py"
)

SPEC = importlib.util.spec_from_file_location("subagent_balancer_orchestrator", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TestSubagentBalancerOrchestrator(unittest.TestCase):
    """Verify CLI-vs-API balancer routing."""

    def test_detects_cli_quota_context(self) -> None:
        result = MODULE.select_balancer("auto", "Gemini CLI /stats model shows quota almost exhausted")
        self.assertEqual(result["selected_balancer"], "subagent-balancer")

    def test_detects_api_cost_context(self) -> None:
        result = MODULE.select_balancer("auto", "Vertex AI batch job with token pricing and GEMINI_API_KEY")
        self.assertEqual(result["selected_balancer"], "subagent-balancer-api")

    def test_returns_local_when_context_is_ambiguous(self) -> None:
        result = MODULE.select_balancer("auto", "Need a review of these files")
        self.assertEqual(result["route"], "local")
        self.assertIsNone(result["selected_balancer"])

    def test_explicit_mode_overrides_context(self) -> None:
        result = MODULE.select_balancer("cli", "Vertex AI batch job with token pricing")
        self.assertEqual(result["selected_balancer"], "subagent-balancer")


if __name__ == "__main__":
    unittest.main()
