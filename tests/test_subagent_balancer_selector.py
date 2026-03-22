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

    def test_prefers_flash_lite_for_small_review(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        result = MODULE.choose_model(
            models=models,
            task_type="review",
            scope="small",
            preferred_model=None,
            avoid_models=set(),
            allow_preview=True,
        )
        self.assertEqual(result["route"], "subagent")
        self.assertEqual(result["selected_model"], "gemini-2.5-flash-lite")

    def test_prefers_pro_for_large_implementation(self) -> None:
        models = MODULE.parse_snapshot(SNAPSHOT)
        result = MODULE.choose_model(
            models=models,
            task_type="implementation",
            scope="large",
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
            preferred_model="gemini-2.5-flash",
            avoid_models=set(),
            allow_preview=True,
        )
        self.assertEqual(result["route"], "local")


if __name__ == "__main__":
    unittest.main()
