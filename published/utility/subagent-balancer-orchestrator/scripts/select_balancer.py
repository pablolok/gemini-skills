"""Choose the correct Gemini balancing skill for the current environment."""

from __future__ import annotations

import argparse
import json
import sys


CLI_KEYWORDS = (
    "gemini cli",
    "/stats model",
    "usage resets",
    "model usage",
    "quota",
    "google account",
    "free tier",
)

API_KEYWORDS = (
    "vertex ai",
    "google ai developer api",
    "gemini api",
    "gemini_api_key",
    "google_api_key",
    "api key",
    "token pricing",
    "per 1m tokens",
    "billed",
    "batch",
    "cost",
    "price",
)


def detect_mode(context: str) -> tuple[str, str]:
    """Infer whether the context is CLI/account or billed API usage."""
    lowered = context.lower()
    cli_hits = [keyword for keyword in CLI_KEYWORDS if keyword in lowered]
    api_hits = [keyword for keyword in API_KEYWORDS if keyword in lowered]

    if cli_hits and not api_hits:
        return "cli", f"Detected CLI/quota markers: {', '.join(cli_hits)}."
    if api_hits and not cli_hits:
        return "api", f"Detected API/cost markers: {', '.join(api_hits)}."
    if api_hits and cli_hits:
        return "unknown", (
            "Detected both CLI/quota and API/cost markers; keep work local until the environment is clarified."
        )
    return "unknown", "No clear CLI/quota or API/cost markers were detected."


def select_balancer(mode: str, context: str) -> dict[str, str | None]:
    """Return the selected balancer or a local fallback."""
    if mode == "cli":
        return {
            "route": "subagent",
            "mode": "cli",
            "selected_balancer": "subagent-balancer",
            "reason": "Explicit CLI mode selected.",
        }
    if mode == "api":
        return {
            "route": "subagent",
            "mode": "api",
            "selected_balancer": "subagent-balancer-api",
            "reason": "Explicit API mode selected.",
        }

    inferred_mode, reason = detect_mode(context)
    if inferred_mode == "cli":
        return {
            "route": "subagent",
            "mode": inferred_mode,
            "selected_balancer": "subagent-balancer",
            "reason": reason,
        }
    if inferred_mode == "api":
        return {
            "route": "subagent",
            "mode": inferred_mode,
            "selected_balancer": "subagent-balancer-api",
            "reason": reason,
        }
    return {
        "route": "local",
        "mode": inferred_mode,
        "selected_balancer": None,
        "reason": reason,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["auto", "cli", "api"], default="auto")
    parser.add_argument("--context")
    parser.add_argument("--context-file")
    return parser


def load_context(context: str | None, context_file: str | None) -> str:
    """Load routing context from args or stdin."""
    if context is not None:
        return context
    if context_file:
        with open(context_file, "r", encoding="utf-8") as handle:
            return handle.read()
    return sys.stdin.read()


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    context = load_context(args.context, args.context_file)
    result = select_balancer(args.mode, context)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
