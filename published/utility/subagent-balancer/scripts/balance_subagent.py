"""Capture Gemini quota stats and choose a subagent model safely."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
from typing import Any


THIS_DIR = pathlib.Path(__file__).resolve().parent
SELECTOR_PATH = THIS_DIR / "select_model.py"
SPEC = importlib.util.spec_from_file_location("subagent_balancer_select_model", SELECTOR_PATH)
SELECTOR = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = SELECTOR
SPEC.loader.exec_module(SELECTOR)


DEFAULT_STATS_COMMAND = 'gemini -p "/stats model" --output-format text'
DEFAULT_CACHE_FILE = THIS_DIR.parent / ".quota-cache.txt"


def run_stats_command(command: str, timeout_seconds: int) -> str:
    """Run the stats command and return captured stdout."""
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        shell=True,
        check=True,
    )
    output = completed.stdout.strip()
    if not output:
        raise RuntimeError("Stats command returned no stdout.")
    return output


def read_text_file(path: pathlib.Path) -> str:
    """Read a UTF-8 text file."""
    return path.read_text(encoding="utf-8")


def write_text_file(path: pathlib.Path, text: str) -> None:
    """Write a UTF-8 text file."""
    path.write_text(text, encoding="utf-8")


def acquire_snapshot(
    snapshot_file: str | None,
    stats_command: str,
    cache_file: pathlib.Path,
    timeout_seconds: int,
) -> tuple[str | None, str]:
    """Acquire snapshot text from file, live command, or cache."""
    if snapshot_file:
        if snapshot_file == "-":
            return sys.stdin.read(), "stdin"
        return read_text_file(pathlib.Path(snapshot_file)), "snapshot-file"

    try:
        live_text = run_stats_command(stats_command, timeout_seconds)
        write_text_file(cache_file, live_text)
        return live_text, "live-stats"
    except Exception as exc:  # pragma: no cover - exercised through wrapper tests
        if cache_file.exists():
            return read_text_file(cache_file), f"cache-fallback ({exc})"
        return None, f"unavailable ({exc})"


def choose_route(args: argparse.Namespace) -> dict[str, Any]:
    """Choose the final route from the available snapshot data."""
    cache_file = pathlib.Path(args.cache_file)
    snapshot_text, source = acquire_snapshot(
        snapshot_file=args.snapshot_file,
        stats_command=args.stats_command,
        cache_file=cache_file,
        timeout_seconds=args.timeout_seconds,
    )

    if not snapshot_text:
        return {
            "route": "local",
            "selected_model": None,
            "reason": "Could not acquire live Gemini stats or a cached quota snapshot.",
            "snapshot_source": source,
            "ranked_candidates": [],
        }

    models = SELECTOR.parse_snapshot(snapshot_text)
    result = SELECTOR.choose_model(
        models=models,
        task_type=args.task_type,
        scope=args.scope,
        preferred_model=args.preferred_model,
        avoid_models=set(args.avoid_model),
        allow_preview=not args.no_preview,
    )
    result["snapshot_source"] = source
    result["stats_command"] = args.stats_command
    return result


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-file")
    parser.add_argument(
        "--stats-command",
        default=os.environ.get("GEMINI_STATS_COMMAND", DEFAULT_STATS_COMMAND),
    )
    parser.add_argument("--cache-file", default=str(DEFAULT_CACHE_FILE))
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument(
        "--task-type",
        choices=["review", "search", "implementation", "verification", "refactor"],
        default="review",
    )
    parser.add_argument("--scope", choices=["small", "medium", "large"], default="medium")
    parser.add_argument("--preferred-model")
    parser.add_argument("--avoid-model", action="append", default=[])
    parser.add_argument("--no-preview", action="store_true")
    parser.add_argument("--explain", action="store_true")
    return parser


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    result = choose_route(args)

    if args.explain:
        print(f"Route: {result['route']}")
        print(f"Selected model: {result['selected_model']}")
        print(f"Reason: {result['reason']}")
        print(f"Snapshot source: {result['snapshot_source']}")
        candidates = ", ".join(result.get("ranked_candidates", [])) or "none"
        print(f"Candidates: {candidates}")
        return 0

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
