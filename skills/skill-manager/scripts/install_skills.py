"""Install one or more named skills into the current project."""

from __future__ import annotations

import logging
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from runtime import install_named_skills, list_available_skill_paths


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger("skill_manager_install")


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    try:
        if not args:
            print("No skill paths provided.")
            print("Available skills:")
            for path in list_available_skill_paths():
                print(f"- {path}")
            print("Use: /skill-manager:install <category/skill> [more-skills]")
            return 0

        installed = install_named_skills(args)
        if not installed:
            print("No skills were installed.")
            return 1

        print(f"Installed {len(installed)} skill(s):")
        for item in installed:
            print(f"- {item}")
        print("Run /skills reload and /commands reload if Gemini CLI is already open.")
        return 0
    except Exception as exc:  # pragma: no cover
        LOGGER.error("Skill install failed: %s", exc)
        print(f"Skill install failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
