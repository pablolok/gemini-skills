"""List installed skills, available published skills, and pending updates."""

from __future__ import annotations

import logging
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from runtime import check_updates, list_available_skill_paths, list_installed_skills


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> int:
    installed = list_installed_skills()
    available = list_available_skill_paths()
    updates = check_updates()

    print("Installed skills:")
    if installed:
        for item in installed:
            print(f"- {item['name']} (v{item['version']})")
    else:
        print("- none")

    print("\nAvailable published skills:")
    if available:
        for item in available:
            print(f"- {item}")
    else:
        print("- none")

    print("\nUpdates:")
    if updates:
        for item in updates:
            print(f"- {item['name']}: {item['installed']} -> {item['latest']}")
    else:
        print("- none")

    return 0


if __name__ == "__main__":
    sys.exit(main())
