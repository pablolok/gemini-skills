"""Post-install hook for skill-manager.

Adds Gemini-local update integration for installed skills:
- a SessionStart hook that reports available updates on startup
- a custom `/skills:update` command that applies updates from the source repo
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict


HOOK_NAME = "skill-manager-update-check"
HOOK_COMMAND = "python .gemini/skills/skill-manager/scripts/session_start_hook.py"
COMMAND_FILE_CONTENT = '''description = "Update installed Gemini skills from the configured gemini-skills repository."

prompt = """
A skill update was requested for the current project.

Use the command output below as the source of truth. Report the result clearly:
- if updates were applied, list the updated skills and recommend `/skills reload`
- if command files changed and Gemini is already open, also recommend `/commands reload`
- if no updates were available, say that explicitly
- if the updater failed, surface the failure reason

```text
!{python .gemini/skills/skill-manager/scripts/update_skills.py}
```
"""
'''


def _load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _ensure_session_start_hook(settings: Dict[str, Any]) -> Dict[str, Any]:
    hooks = settings.setdefault("hooks", {})
    session_start = hooks.setdefault("SessionStart", [])

    hook_entry = {
        "matcher": "startup",
        "hooks": [
            {
                "name": HOOK_NAME,
                "type": "command",
                "command": HOOK_COMMAND,
            }
        ],
    }

    for entry in session_start:
        if entry.get("matcher") != "startup":
            continue

        nested_hooks = entry.setdefault("hooks", [])
        for nested in nested_hooks:
            if nested.get("name") == HOOK_NAME:
                nested["type"] = "command"
                nested["command"] = HOOK_COMMAND
                return settings

        nested_hooks.append(hook_entry["hooks"][0])
        return settings

    session_start.append(hook_entry)
    return settings


def _write_custom_command(target_project_path: str) -> None:
    command_path = os.path.join(
        target_project_path,
        ".gemini",
        "commands",
        "skills",
        "update.toml",
    )
    os.makedirs(os.path.dirname(command_path), exist_ok=True)
    with open(command_path, "w", encoding="utf-8") as handle:
        handle.write(COMMAND_FILE_CONTENT)


def _write_runtime_config(target_project_path: str, source_repo_root: str) -> None:
    config_path = os.path.join(
        target_project_path,
        ".gemini",
        "skills",
        "skill-manager",
        "runtime_config.json",
    )
    payload = {
        "source_repo_root": source_repo_root,
        "published_dir": os.path.join(source_repo_root, "published"),
    }
    _write_json(config_path, payload)


def integrate(target_project_path: str) -> None:
    target_project_path = os.path.abspath(target_project_path)
    source_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    settings_path = os.path.join(target_project_path, ".gemini", "settings.json")
    settings = _load_json(settings_path)
    updated_settings = _ensure_session_start_hook(settings)
    _write_json(settings_path, updated_settings)

    _write_custom_command(target_project_path)
    _write_runtime_config(target_project_path, source_repo_root)

    print("Configured Gemini startup update hook and /skills:update command.")
    print("If Gemini CLI is already open, run /commands reload to load the new command.")
    print("The startup hook will take effect the next time Gemini opens this trusted workspace.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python post_install.py <target_project_path>")
        sys.exit(1)

    integrate(sys.argv[1])
