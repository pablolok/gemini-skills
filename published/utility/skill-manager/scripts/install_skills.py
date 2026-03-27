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
            print("Use: /skill-manager:install [--with-codex] [--with-claude] <category/skill> [more-skills]")
            return 0

        include_codex_bridges = False
        include_claude_references = False
        filtered_args: list[str] = []
        for arg in args:
            if arg == "--with-codex":
                include_codex_bridges = True
                continue
            if arg == "--with-claude":
                include_claude_references = True
                continue
            filtered_args.append(arg)

        installed = install_named_skills(
            filtered_args,
            include_codex_bridges=include_codex_bridges,
            include_claude_references=include_claude_references,
        )
        if not installed:
            print("No skills were installed.")
            return 1

        print(f"Installed {len(installed)} skill(s):")
        for item in installed:
            print(f"- {item}")
        if include_codex_bridges:
            print("Requested matching Codex bridge wrappers for supported skills.")
        else:
            print("To add matching Codex bridge wrappers too, rerun with --with-codex.")
        if include_claude_references:
            print("Requested generated Claude reference skills for the selected skills.")
        else:
            print("To add generated Claude reference skills too, rerun with --with-claude.")
        print("Run /skills reload and /commands reload if Gemini CLI is already open.")
        return 0
    except Exception as exc:  # pragma: no cover
        LOGGER.error("Skill install failed: %s", exc)
        print(f"Skill install failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
