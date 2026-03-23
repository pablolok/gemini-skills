"""Tests for the subagent balancer wrapper."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import types
import unittest
from unittest import mock


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "skills"
    / "subagent-balancer"
    / "scripts"
    / "balance_subagent.py"
)

SPEC = importlib.util.spec_from_file_location("subagent_balancer_wrapper", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


SNAPSHOT = """
gemini-2.5-flash-lite      -    2%  9:10 PM (21h 30m)
gemini-2.5-pro             -   11%  7:24 PM (19h 45m)
gemini-3-flash-preview     - Limit 7:00 PM (19h 21m)
"""


class TestSubagentBalancerWrapper(unittest.TestCase):
    """Verify the wrapper's acquisition and fallback behavior."""

    def test_prefers_snapshot_file_when_provided(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = pathlib.Path(tmp) / "quota.txt"
            snapshot_path.write_text(SNAPSHOT, encoding="utf-8")
            args = types.SimpleNamespace(
                snapshot_file=str(snapshot_path),
                stats_command="ignored",
                cache_file=str(pathlib.Path(tmp) / ".quota-cache.txt"),
                timeout_seconds=1,
                task_type="review",
                scope="small",
                complexity="trivial",
                preferred_model=None,
                avoid_model=[],
                no_preview=True,
            )
            result = MODULE.choose_route(args)
            self.assertEqual(result["snapshot_source"], "snapshot-file")
            self.assertEqual(result["selected_model"], "gemini-2.5-flash-lite")

    def test_uses_cache_when_live_command_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = pathlib.Path(tmp) / ".quota-cache.txt"
            cache_path.write_text(SNAPSHOT, encoding="utf-8")
            args = types.SimpleNamespace(
                snapshot_file=None,
                stats_command="gemini something",
                cache_file=str(cache_path),
                timeout_seconds=1,
                task_type="implementation",
                scope="large",
                complexity="hard",
                preferred_model=None,
                avoid_model=[],
                no_preview=True,
            )
            with mock.patch.object(MODULE, "run_stats_command", side_effect=RuntimeError("boom")):
                result = MODULE.choose_route(args)
            self.assertEqual(result["route"], "subagent")
            self.assertEqual(result["selected_model"], "gemini-2.5-pro")
            self.assertIn("cache-fallback", result["snapshot_source"])

    def test_accepts_stdin_marker_for_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = types.SimpleNamespace(
                snapshot_file="-",
                stats_command="ignored",
                cache_file=str(pathlib.Path(tmp) / ".quota-cache.txt"),
                timeout_seconds=1,
                task_type="review",
                scope="small",
                complexity="trivial",
                preferred_model=None,
                avoid_model=[],
                no_preview=True,
            )
            with mock.patch("sys.stdin.read", return_value=SNAPSHOT):
                result = MODULE.choose_route(args)
            self.assertEqual(result["snapshot_source"], "stdin")
            self.assertEqual(result["selected_model"], "gemini-2.5-flash-lite")

    def test_returns_local_when_no_stats_source_is_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = types.SimpleNamespace(
                snapshot_file=None,
                stats_command="gemini something",
                cache_file=str(pathlib.Path(tmp) / ".quota-cache.txt"),
                timeout_seconds=1,
                task_type="review",
                scope="small",
                complexity="trivial",
                preferred_model=None,
                avoid_model=[],
                no_preview=True,
            )
            with mock.patch.object(MODULE, "run_stats_command", side_effect=RuntimeError("boom")):
                result = MODULE.choose_route(args)
            self.assertEqual(result["route"], "local")
            self.assertIsNone(result["selected_model"])

    def test_explain_output_uses_canonical_route_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = pathlib.Path(tmp) / "quota.txt"
            snapshot_path.write_text(SNAPSHOT, encoding="utf-8")
            args = types.SimpleNamespace(
                snapshot_file=str(snapshot_path),
                stats_command="ignored",
                cache_file=str(pathlib.Path(tmp) / ".quota-cache.txt"),
                timeout_seconds=1,
                task_type="review",
                scope="small",
                complexity="trivial",
                preferred_model=None,
                avoid_model=[],
                no_preview=True,
            )
            result = MODULE.choose_route(args)
            self.assertIn(result["route"], {"local", "subagent"})
            self.assertIn("reason", result)
            self.assertIn("ranked_candidates", result)
            self.assertIn("complexity=trivial", result["reason"])


if __name__ == "__main__":
    unittest.main()
