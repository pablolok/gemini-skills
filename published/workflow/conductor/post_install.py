"""Post-installation hook for the `conductor` skill.

Two responsibilities:
  1. Install the Conductor slash commands into the target project's
     `.claude/commands/conductor/` so `/conductor:setup`, `/conductor:new-track`, etc.
     become available.
  2. Scaffold the `conductor/` Context-Driven-Development workspace from the bundled
     `templates/`, without ever overwriting files the project already has.

The hook locates its own bundled `commands/` and `templates/` relative to this file, so it
works both when run by the installer and when invoked manually:

    python .claude/skills/conductor/post_install.py .
"""

from __future__ import annotations

import os
import shutil
import sys


SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
COMMANDS_SRC = os.path.join(SKILL_DIR, "commands")
TEMPLATES_SRC = os.path.join(SKILL_DIR, "templates")


def install_commands(target_project_path: str) -> int:
    """Copy every command file into `.claude/commands/conductor/`. Overwrites commands so
    upgrades ship the latest behavior. Returns the number of commands installed."""
    if not os.path.isdir(COMMANDS_SRC):
        print(f"No bundled commands found at {COMMANDS_SRC}; skipping command install.")
        return 0

    dest_dir = os.path.join(target_project_path, ".claude", "commands", "conductor")
    os.makedirs(dest_dir, exist_ok=True)

    count = 0
    for name in sorted(os.listdir(COMMANDS_SRC)):
        if not name.endswith(".md"):
            continue
        shutil.copy2(os.path.join(COMMANDS_SRC, name), os.path.join(dest_dir, name))
        count += 1
    print(f"Installed {count} Conductor command(s) into {dest_dir}.")
    return count


def scaffold_workspace(target_project_path: str) -> int:
    """Copy template files into `conductor/`, skipping anything that already exists so an
    existing Conductor workspace is never clobbered. Returns the number of files created."""
    if not os.path.isdir(TEMPLATES_SRC):
        print(f"No bundled templates found at {TEMPLATES_SRC}; skipping workspace scaffold.")
        return 0

    dest_root = os.path.join(target_project_path, "conductor")
    created = 0
    for root, _dirs, files in os.walk(TEMPLATES_SRC):
        rel_dir = os.path.relpath(root, TEMPLATES_SRC)
        for filename in files:
            rel_path = filename if rel_dir == "." else os.path.join(rel_dir, filename)
            dest_path = os.path.join(dest_root, rel_path)
            if os.path.exists(dest_path):
                continue
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(os.path.join(root, filename), dest_path)
            created += 1

    # Ensure the tracks directory exists for future tracks.
    os.makedirs(os.path.join(dest_root, "tracks"), exist_ok=True)

    if created:
        print(f"Scaffolded {created} Conductor workspace file(s) under {dest_root}.")
    else:
        print(f"Conductor workspace already present at {dest_root}; nothing scaffolded.")
    return created


def main(target_project_path: str) -> None:
    target_project_path = os.path.abspath(target_project_path)
    install_commands(target_project_path)
    scaffold_workspace(target_project_path)
    print(
        "Conductor is ready. Reload slash commands, then run /conductor:setup to fill in the "
        "workspace, or /conductor:new-track to start work."
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
