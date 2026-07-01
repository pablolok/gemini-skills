"""Uninstall one or more installed skills from the current project."""

from __future__ import annotations

import logging
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from runtime import list_managed_installed_skills, uninstall_named_skills


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger("skill_manager_uninstall")


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    try:
        if not args:
            print("No skill names provided.")
            print("Managed installed skills:")
            for item in list_managed_installed_skills():
                print(f"- {item['name']}")
            print("Use: /skill-manager:uninstall <skill-name> [more-skills]")
            return 0

        removed = uninstall_named_skills(args)
        if not removed:
            print("No skills were removed.")
            return 1

        print(f"Removed {len(removed)} skill(s):")
        for item in removed:
            print(f"- {item}")
        print("Run /skills reload and /commands reload if Gemini CLI is already open.")
        return 0
    except Exception as exc:  # pragma: no cover
        LOGGER.error("Skill uninstall failed: %s", exc)
        print(f"Skill uninstall failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
