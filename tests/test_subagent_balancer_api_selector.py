"""Tests for the API-focused subagent balancer selector."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "skills"
    / "subagent-balancer-api"
    / "scripts"
    / "select_model.py"
)

SPEC = importlib.util.spec_from_file_location("subagent_balancer_api_selector", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TestSubagentBalancerApiSelector(unittest.TestCase):
    """Verify API price-aware model routing."""

    def test_prefers_flash_lite_for_trivial_verification(self) -> None:
        result = MODULE.choose_model(
            task_type="verification",
            scope="small",
            complexity="trivial",
            budget_mode="min-cost",
            delivery_mode="standard",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
            estimated_input_mtokens=None,
            estimated_output_mtokens=None,
        )
        self.assertEqual(result["selected_model"], "gemini-2.5-flash-lite")

    def test_prefers_flash_for_normal_implementation(self) -> None:
        result = MODULE.choose_model(
            task_type="implementation",
            scope="medium",
            complexity="normal",
            budget_mode="balanced",
            delivery_mode="standard",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
            estimated_input_mtokens=None,
            estimated_output_mtokens=None,
        )
        self.assertEqual(result["selected_model"], "gemini-2.5-flash")

    def test_prefers_pro_for_hard_quality_first_work(self) -> None:
        result = MODULE.choose_model(
            task_type="implementation",
            scope="medium",
            complexity="hard",
            budget_mode="quality-first",
            delivery_mode="standard",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
            estimated_input_mtokens=None,
            estimated_output_mtokens=None,
        )
        self.assertEqual(result["selected_model"], "gemini-2.5-pro")

    def test_batch_delivery_reduces_estimated_cost(self) -> None:
        standard = MODULE.choose_model(
            task_type="implementation",
            scope="medium",
            complexity="normal",
            budget_mode="balanced",
            delivery_mode="standard",
            preferred_model="gemini-2.5-flash",
            avoid_models=set(),
            allow_preview=False,
            estimated_input_mtokens=0.2,
            estimated_output_mtokens=0.05,
        )
        batch = MODULE.choose_model(
            task_type="implementation",
            scope="medium",
            complexity="normal",
            budget_mode="balanced",
            delivery_mode="batch",
            preferred_model="gemini-2.5-flash",
            avoid_models=set(),
            allow_preview=False,
            estimated_input_mtokens=0.2,
            estimated_output_mtokens=0.05,
        )
        self.assertLess(batch["estimated_cost_usd"], standard["estimated_cost_usd"])

    def test_no_preview_blocks_preview_models(self) -> None:
        result = MODULE.choose_model(
            task_type="refactor",
            scope="large",
            complexity="ambiguous",
            budget_mode="quality-first",
            delivery_mode="standard",
            preferred_model=None,
            avoid_models={"gemini-2.5-pro"},
            allow_preview=False,
            estimated_input_mtokens=None,
            estimated_output_mtokens=None,
        )
        self.assertNotIn("preview", result["selected_model"])

    def test_long_prompt_uses_long_context_pricing(self) -> None:
        result = MODULE.choose_model(
            task_type="implementation",
            scope="large",
            complexity="hard",
            budget_mode="quality-first",
            delivery_mode="standard",
            preferred_model="gemini-2.5-pro",
            avoid_models=set(),
            allow_preview=False,
            estimated_input_mtokens=0.4,
            estimated_output_mtokens=0.12,
        )
        self.assertAlmostEqual(result["estimated_cost_usd"], 2.8, places=6)


if __name__ == "__main__":
    unittest.main()
