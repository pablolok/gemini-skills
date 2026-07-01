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
    """Verify API price-aware model routing across Claude tiers."""

    def test_prefers_haiku_for_trivial_verification(self) -> None:
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
        self.assertEqual(result["selected_model"], "claude-haiku-4-5")

    def test_prefers_sonnet_for_normal_implementation(self) -> None:
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
        self.assertEqual(result["selected_model"], "claude-sonnet-5")

    def test_prefers_opus_for_hard_quality_first_work(self) -> None:
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
        self.assertEqual(result["selected_model"], "claude-opus-4-8")

    def test_batch_delivery_reduces_estimated_cost(self) -> None:
        standard = MODULE.choose_model(
            task_type="implementation",
            scope="medium",
            complexity="normal",
            budget_mode="balanced",
            delivery_mode="standard",
            preferred_model="claude-sonnet-5",
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
            preferred_model="claude-sonnet-5",
            avoid_models=set(),
            allow_preview=False,
            estimated_input_mtokens=0.2,
            estimated_output_mtokens=0.05,
            pricing_file=None,
        )
        self.assertLess(batch["estimated_cost_usd"], standard["estimated_cost_usd"])

    def test_no_preview_blocks_preview_models(self) -> None:
        # The canonical Claude catalog has no preview models, so this asserts the
        # selector never returns a preview-named model when previews are disabled.
        result = MODULE.choose_model(
            task_type="refactor",
            scope="large",
            complexity="ambiguous",
            budget_mode="quality-first",
            delivery_mode="standard",
            preferred_model=None,
            avoid_models={"claude-opus-4-8"},
            allow_preview=False,
            estimated_input_mtokens=None,
            estimated_output_mtokens=None,
            pricing_file=None,
        )
        self.assertNotIn("preview", result["selected_model"])

    def test_long_prompt_uses_flat_standard_pricing(self) -> None:
        # Claude has no long-context premium: large prompts bill at flat standard
        # rates. claude-opus-4-8 standard = $5/1M input, $25/1M output, so
        # 0.4M input + 0.12M output = 0.4*5 + 0.12*25 = $5.00.
        result = MODULE.choose_model(
            task_type="implementation",
            scope="large",
            complexity="hard",
            budget_mode="quality-first",
            delivery_mode="standard",
            preferred_model="claude-opus-4-8",
            avoid_models=set(),
            allow_preview=False,
            estimated_input_mtokens=0.4,
            estimated_output_mtokens=0.12,
            pricing_file=None,
        )
        self.assertAlmostEqual(result["estimated_cost_usd"], 5.0, places=6)

    def test_custom_pricing_file_can_change_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pricing_path = pathlib.Path(tmp) / "pricing.json"
            pricing_path.write_text(
                json.dumps(
                    {
                        "models": {
                            "claude-haiku-4-5": {
                                "standard": {"input": 0.1, "output": 0.4},
                                "batch": {"input": 0.05, "output": 0.2},
                            },
                            "claude-sonnet-5": {
                                "standard": {"input": 9.0, "output": 9.0},
                                "batch": {"input": 4.5, "output": 4.5},
                            },
                            "claude-opus-4-8": {
                                "standard": {"input": 1.25, "output": 10.0},
                                "batch": {"input": 0.625, "output": 5.0},
                            },
                            "claude-fable-5": {
                                "standard": {"input": 8.0, "output": 20.0},
                                "batch": {"input": 4.0, "output": 10.0},
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
        self.assertEqual(result["selected_model"], "claude-opus-4-8")


if __name__ == "__main__":
    unittest.main()
