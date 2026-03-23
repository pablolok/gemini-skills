"""Apply installed Gemini skill updates for the current project."""

from __future__ import annotations

import logging
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from runtime import apply_updates, check_updates


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger("skill_manager_update")


def main() -> int:
    try:
        pending = check_updates()
        if not pending:
            print("All installed Gemini skills are already up to date.")
            return 0

        applied = apply_updates()
        if not applied:
            print("Updates were detected but none were applied successfully.")
            return 1

        print(f"Updated {len(applied)} skill(s):")
        for update in applied:
            print(f"- {update['name']}: {update['installed']} -> {update['latest']}")
        print("Run /skills reload and /commands reload if Gemini CLI is already open.")
        return 0
    except Exception as exc:  # pragma: no cover
        LOGGER.error("Skill update failed: %s", exc)
        print(f"Skill update failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
