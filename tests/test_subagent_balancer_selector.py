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


# Claude tiers: haiku (cheapest), sonnet (mid workhorse), opus (top).
SNAPSHOT = """
Model                   Reqs    Model usage                 Usage resets
claude-sonnet-5            -    ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ Limit  7:00 PM (19h 21m)
claude-haiku-4-5          -    ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬    2%  9:10 PM (21h 30m)
claude-opus-4-8           -    ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬   11%  7:24 PM (19h 45m)
claude-sonnet-6-preview   -    ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ Limit  7:00 PM (19h 21m)
claude-opus-5-preview     -    ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬   11%  7:24 PM (19h 45m)
"""


class TestSubagentBalancerSelector(unittest.TestCase):
    """Verify deterministic model routing from a quota snapshot."""

    def test_parse_snapshot(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        self.assertEqual(len(models), 5)
        self.assertEqual(models[0].name, "claude-sonnet-5")
        self.assertTrue(models[0].limited)
        self.assertEqual(models[1].usage_percent, 2)
        self.assertEqual(models[1].reset_window_minutes, 21 * 60 + 30)

    def test_parse_snapshot_preserves_decimal_percentages(self) -> None:
        snapshot = """
claude-haiku-4-5    -    0.7%  7:23 AM (20h 23m)
claude-sonnet-5     -    83%   7:12 AM (20h 12m)
"""
        models = MODULE.parse_snapshot(snapshot)
        self.assertEqual(models[0].usage_percent, 0.7)
        self.assertEqual(models[1].usage_percent, 83.0)

    def test_prefers_haiku_for_small_review(self) -> None:
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
        self.assertEqual(result["selected_model"], "claude-haiku-4-5")

    def test_prefers_opus_for_large_implementation_when_sonnet_is_unavailable(self) -> None:
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
        self.assertEqual(result["selected_model"], "claude-opus-4-8")

    def test_prefers_sonnet_over_opus_for_typical_implementation_work(self) -> None:
        snapshot = """
claude-sonnet-5         -    22%  4:00 PM (4h 0m)
claude-opus-4-8         -     7%  4:00 PM (4h 0m)
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
        self.assertEqual(result["selected_model"], "claude-sonnet-5")

    def test_prefers_opus_only_for_clearly_harder_case(self) -> None:
        snapshot = """
claude-sonnet-5         -    84%  11:00 PM (18h 0m)
claude-opus-4-8         -    14%  1:00 PM (8h 0m)
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
        self.assertEqual(result["selected_model"], "claude-opus-4-8")

    def test_respects_explicit_preferred_model(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        result = MODULE.choose_model(
            models=models,
            task_type="review",
            scope="small",
            complexity="normal",
            preferred_model="claude-opus-4-8",
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["selected_model"], "claude-opus-4-8")

    def test_falls_back_to_local_when_preferred_model_is_limited(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        result = MODULE.choose_model(
            models=models,
            task_type="review",
            scope="small",
            complexity="trivial",
            preferred_model="claude-sonnet-5",
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
            preferred_model="claude-opus-5-preview",
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
            avoid_models={"claude-haiku-4-5", "claude-opus-4-8"},
            allow_preview=False,
        )
        self.assertEqual(result["route"], "local")
        self.assertIn("ranked_candidates", result)

    def test_reset_window_breaks_ties_toward_earlier_reset(self) -> None:
        snapshot = """
claude-sonnet-5         -    35%  11:00 AM (2h 0m)
claude-sonnet-4-5       -    35%  5:00 AM (32h 0m)
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
        self.assertEqual(result["selected_model"], "claude-sonnet-5")

    def test_unknown_future_model_name_is_inferred(self) -> None:
        snapshot = """
claude-sonnet-6         -    18%  3:00 PM (6h 0m)
claude-opus-5           -    18%  3:00 PM (6h 0m)
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
        self.assertEqual(result["selected_model"], "claude-sonnet-6")

    def test_unparseable_reset_text_does_not_crash(self) -> None:
        snapshot = """
claude-sonnet-5         -    18%  resets sometime later
claude-opus-4-8         -    18%  resets sometime later
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
        self.assertEqual(result["selected_model"], "claude-sonnet-5")

    def test_hard_complexity_can_escalate_to_opus(self) -> None:
        snapshot = """
claude-sonnet-5         -    18%  2:00 PM (8h 0m)
claude-opus-4-8         -    20%  2:00 PM (8h 0m)
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
        self.assertEqual(result["selected_model"], "claude-opus-4-8")

    def test_normal_complexity_preserves_opus_quota_even_when_opus_is_slightly_healthier(self) -> None:
        snapshot = """
claude-sonnet-5         -    24%  5:00 PM (6h 0m)
claude-opus-4-8         -    12%  5:00 PM (6h 0m)
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
        self.assertEqual(result["selected_model"], "claude-sonnet-5")

    def test_haiku_is_preferred_for_trivial_audit_style_work(self) -> None:
        snapshot = """
claude-haiku-4-5    -    31%  7:00 PM (4h 0m)
claude-sonnet-5     -    14%  7:00 PM (4h 0m)
claude-opus-4-8     -     2%  7:00 PM (4h 0m)
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
        self.assertEqual(result["selected_model"], "claude-haiku-4-5")

    def test_haiku_can_win_for_small_trivial_implementation_when_sonnet_is_heavily_used(self) -> None:
        snapshot = """
claude-haiku-4-5    -    1.2%  7:00 PM (18h 0m)
claude-sonnet-5     -    88%   7:00 PM (18h 0m)
claude-opus-4-8     -    61%   7:00 PM (18h 0m)
"""
        models = MODULE.parse_snapshot(snapshot)
        result = MODULE.choose_model(
            models=models,
            task_type="implementation",
            scope="small",
            complexity="trivial",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=False,
        )
        self.assertEqual(result["selected_model"], "claude-haiku-4-5")

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
