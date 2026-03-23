"""Tests for the subagent balancer model selector."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "skills"
    / "subagent-balancer"
    / "scripts"
    / "select_model.py"
)

SPEC = importlib.util.spec_from_file_location("subagent_balancer_select_model", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


SNAPSHOT = """
Model                   Reqs    Model usage                 Usage resets
gemini-2.5-flash           -    ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ Limit  7:00 PM (19h 21m)
gemini-2.5-flash-lite      -    ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬    2%  9:10 PM (21h 30m)
gemini-2.5-pro             -    ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬   11%  7:24 PM (19h 45m)
gemini-3-flash-preview     -    ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ Limit  7:00 PM (19h 21m)
gemini-3.1-pro-preview     -    ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬   11%  7:24 PM (19h 45m)
"""


class TestSubagentBalancerSelector(unittest.TestCase):
    """Verify deterministic model routing from a quota snapshot."""

    def test_parse_snapshot(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        self.assertEqual(len(models), 5)
        self.assertEqual(models[0].name, "gemini-2.5-flash")
        self.assertTrue(models[0].limited)
        self.assertEqual(models[1].usage_percent, 2)
        self.assertEqual(models[1].reset_window_minutes, 21 * 60 + 30)

    def test_prefers_flash_lite_for_small_review(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        result = MODULE.choose_model(
            models=models,
            task_type="review",
            scope="small",
            complexity="trivial",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=True,
        )
        self.assertEqual(result["route"], "subagent")
        self.assertEqual(result["selected_model"], "gemini-2.5-flash-lite")

    def test_prefers_pro_for_large_implementation_when_flash_is_unavailable(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        result = MODULE.choose_model(
            models=models,
            task_type="implementation",
            scope="large",
            complexity="hard",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["selected_model"], "gemini-2.5-pro")

    def test_prefers_flash_over_pro_for_typical_implementation_work(self) -> None:
        snapshot = """
gemini-2.5-flash         -    22%  4:00 PM (4h 0m)
gemini-2.5-pro           -     7%  4:00 PM (4h 0m)
"""
        models = MODULE.parse_snapshot(snapshot)
        result = MODULE.choose_model(
            models=models,
            task_type="implementation",
            scope="medium",
            complexity="normal",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["selected_model"], "gemini-2.5-flash")

    def test_prefers_pro_only_for_clearly_harder_case(self) -> None:
        snapshot = """
gemini-2.5-flash         -    84%  11:00 PM (18h 0m)
gemini-2.5-pro           -    14%  1:00 PM (8h 0m)
"""
        models = MODULE.parse_snapshot(snapshot)
        result = MODULE.choose_model(
            models=models,
            task_type="refactor",
            scope="large",
            complexity="ambiguous",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["selected_model"], "gemini-2.5-pro")

    def test_respects_explicit_preferred_model(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        result = MODULE.choose_model(
            models=models,
            task_type="review",
            scope="small",
            complexity="normal",
            preferred_model="gemini-2.5-pro",
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["selected_model"], "gemini-2.5-pro")

    def test_falls_back_to_local_when_preferred_model_is_limited(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        result = MODULE.choose_model(
            models=models,
            task_type="review",
            scope="small",
            complexity="trivial",
            preferred_model="gemini-2.5-flash",
            avoid_models=set(),
            allow_preview=True,
        )
        self.assertEqual(result["route"], "local")

    def test_returns_local_when_preferred_model_is_blocked_by_preview_policy(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        result = MODULE.choose_model(
            models=models,
            task_type="review",
            scope="small",
            complexity="normal",
            preferred_model="gemini-3.1-pro-preview",
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["route"], "local")

    def test_returns_local_when_all_models_are_blocked(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        result = MODULE.choose_model(
            models=models,
            task_type="review",
            scope="small",
            complexity="trivial",
            preferred_model=None,
            avoid_models={"gemini-2.5-flash-lite", "gemini-2.5-pro"},
            allow_preview=False,
        )
        self.assertEqual(result["route"], "local")
        self.assertIn("ranked_candidates", result)

    def test_reset_window_breaks_ties_toward_earlier_reset(self) -> None:
        snapshot = """
gemini-2.5-flash         -    35%  11:00 AM (2h 0m)
gemini-2.0-flash         -    35%  5:00 AM (32h 0m)
"""
        models = MODULE.parse_snapshot(snapshot)
        result = MODULE.choose_model(
            models=models,
            task_type="implementation",
            scope="medium",
            complexity="normal",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["selected_model"], "gemini-2.5-flash")

    def test_unknown_future_model_name_is_inferred(self) -> None:
        snapshot = """
gemini-4-flash           -    18%  3:00 PM (6h 0m)
gemini-4-pro             -    18%  3:00 PM (6h 0m)
"""
        models = MODULE.parse_snapshot(snapshot)
        result = MODULE.choose_model(
            models=models,
            task_type="implementation",
            scope="medium",
            complexity="normal",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["selected_model"], "gemini-4-flash")

    def test_unparseable_reset_text_does_not_crash(self) -> None:
        snapshot = """
gemini-2.5-flash         -    18%  resets sometime later
gemini-2.5-pro           -    18%  resets sometime later
"""
        models = MODULE.parse_snapshot(snapshot)
        result = MODULE.choose_model(
            models=models,
            task_type="implementation",
            scope="medium",
            complexity="normal",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["route"], "subagent")
        self.assertEqual(result["selected_model"], "gemini-2.5-flash")

    def test_hard_complexity_can_escalate_to_pro(self) -> None:
        snapshot = """
gemini-2.5-flash         -    18%  2:00 PM (8h 0m)
gemini-2.5-pro           -    20%  2:00 PM (8h 0m)
"""
        models = MODULE.parse_snapshot(snapshot)
        result = MODULE.choose_model(
            models=models,
            task_type="implementation",
            scope="medium",
            complexity="hard",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["selected_model"], "gemini-2.5-pro")

    def test_normal_complexity_preserves_pro_quota_even_when_pro_is_slightly_healthier(self) -> None:
        snapshot = """
gemini-2.5-flash         -    24%  5:00 PM (6h 0m)
gemini-2.5-pro           -    12%  5:00 PM (6h 0m)
"""
        models = MODULE.parse_snapshot(snapshot)
        result = MODULE.choose_model(
            models=models,
            task_type="implementation",
            scope="medium",
            complexity="normal",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["selected_model"], "gemini-2.5-flash")

    def test_flash_lite_is_preferred_for_trivial_audit_style_work(self) -> None:
        snapshot = """
gemini-2.5-flash-lite    -    31%  7:00 PM (4h 0m)
gemini-2.5-flash         -    14%  7:00 PM (4h 0m)
gemini-2.5-pro           -     2%  7:00 PM (4h 0m)
"""
        models = MODULE.parse_snapshot(snapshot)
        result = MODULE.choose_model(
            models=models,
            task_type="verification",
            scope="small",
            complexity="trivial",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["selected_model"], "gemini-2.5-flash-lite")

    def test_reason_includes_complexity(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        result = MODULE.choose_model(
            models=models,
            task_type="review",
            scope="small",
            complexity="trivial",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=True,
        )
        self.assertIn("complexity=trivial", result["reason"])


if __name__ == "__main__":
    unittest.main()
