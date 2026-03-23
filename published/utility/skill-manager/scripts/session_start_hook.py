"""Gemini SessionStart hook for skill-manager update notifications."""

from __future__ import annotations

import json
import logging
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from runtime import check_updates


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("skill_manager_session_start")


def _build_message(updates):
    names = ", ".join(f"{item['name']} ({item['installed']} -> {item['latest']})" for item in updates[:5])
    remainder = len(updates) - 5
    if remainder > 0:
        names = f"{names}, and {remainder} more"
    return (
        f"Skill updates are available: {names}. "
        "Run /skill-manager:update to apply them in this project."
    )


def main() -> None:
    try:
        raw_input = sys.stdin.read().strip()
        if raw_input:
            json.loads(raw_input)

        updates = check_updates()
        if not updates:
            print("{}")
            return

        print(json.dumps({"systemMessage": _build_message(updates)}))
    except Exception as exc:  # pragma: no cover
        LOGGER.error("Skill-manager startup hook failed: %s", exc)
        print("{}")


if __name__ == "__main__":
    main()
