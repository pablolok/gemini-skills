"""Tests for the API-focused subagent balancer selector."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import tempfile
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
            pricing_file=None,
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
            pricing_file=None,
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
            pricing_file=None,
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
            pricing_file=None,
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
            pricing_file=None,
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
            pricing_file=None,
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
            pricing_file=None,
        )
        self.assertAlmostEqual(result["estimated_cost_usd"], 2.8, places=6)

    def test_custom_pricing_file_can_change_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pricing_path = pathlib.Path(tmp) / "pricing.json"
            pricing_path.write_text(
                json.dumps(
                    {
                        "models": {
                            "gemini-2.5-flash-lite": {
                                "standard": {"input": 0.1, "output": 0.4},
                                "batch": {"input": 0.05, "output": 0.2},
                            },
                            "gemini-2.5-flash": {
                                "standard": {"input": 9.0, "output": 9.0},
                                "batch": {"input": 4.5, "output": 4.5},
                            },
                            "gemini-2.5-pro": {
                                "standard": {"input": 1.25, "output": 10.0},
                                "batch": {"input": 0.625, "output": 5.0},
                                "standard_long": {"input": 2.5, "output": 15.0},
                                "batch_long": {"input": 1.25, "output": 7.5},
                            },
                            "gemini-3-flash-preview": {
                                "standard": {"input": 0.5, "output": 3.0},
                                "batch": {"input": 0.25, "output": 1.5},
                            },
                            "gemini-3.1-flash-lite-preview": {
                                "standard": {"input": 0.25, "output": 1.5},
                                "batch": {"input": 0.125, "output": 0.75},
                            },
                            "gemini-3.1-pro-preview": {
                                "standard": {"input": 2.0, "output": 12.0},
                                "batch": {"input": 1.0, "output": 6.0},
                                "standard_long": {"input": 4.0, "output": 18.0},
                                "batch_long": {"input": 2.0, "output": 9.0},
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
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
                pricing_file=pricing_path,
            )
        self.assertEqual(result["selected_model"], "gemini-2.5-pro")


if __name__ == "__main__":
    unittest.main()
