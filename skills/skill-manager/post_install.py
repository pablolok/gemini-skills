"""Post-install hook for skill-manager.

Adds Gemini-local skill-manager integration for installed skills:
- a SessionStart hook that reports available updates on startup
- custom `/skill-manager:*` commands for list/install/update/uninstall
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict


HOOK_NAME = "skill-manager-update-check"
HOOK_COMMAND = "python .gemini/skills/skill-manager/scripts/session_start_hook.py"
PLAN_POLICY_FILENAME = "skill-manager-plan-mode.toml"
PLAN_POLICY_CONTENT = '''[[rule]]
toolName = "run_shell_command"
commandPrefix = [
  "python .gemini/skills/skill-manager/scripts/list_skills.py",
  "python .gemini/skills/skill-manager/scripts/install_skills.py",
  "python .gemini/skills/skill-manager/scripts/update_skills.py",
  "python .gemini/skills/skill-manager/scripts/uninstall_skills.py"
]
decision = "allow"
priority = 100
modes = ["plan"]
'''
COMMAND_TEMPLATES = {
    "list.toml": '''description = "List installed skills, available published skills, and pending updates."

prompt = """
Use the command output below as the source of truth.
Summarize:
- installed skills
- available published skills
- any updates available right now

```text
!{python .gemini/skills/skill-manager/scripts/list_skills.py}
```
"""
''',
    "update.toml": '''description = "Update installed Gemini skills from the configured gemini-skills repository."

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
''',
    "install.toml": '''description = "Install one or more published Gemini skills into the current project."

prompt = """
A skill installation was requested.

The user may pass arguments after the command. The raw arguments are: {{args}}

Use the command output below as the source of truth. If the install succeeds, summarize what was installed and recommend `/skills reload`.
If the user did not provide any skill names, explain the available skills from the command output and tell them to rerun `/skill-manager:install [--with-codex] [--with-claude] <category/skill> [more-skills]`.
If the project also uses Codex and the command was run without `--with-codex`, tell the user they can rerun the same install command with `--with-codex` to add matching lightweight `.codex/skills/` bridge wrappers for supported skills only.
If the project also uses Claude and the command was run without `--with-claude`, tell the user they can rerun the same install command with `--with-claude` to add generated lightweight `.claude/skills/` reference skills for the selected Gemini skills.

```text
!{python .gemini/skills/skill-manager/scripts/install_skills.py {{args}}}
```
"""
''',
    "uninstall.toml": '''description = "Uninstall one or more Gemini skills from the current project."

prompt = """
A skill uninstall was requested.

The user may pass arguments after the command. The raw arguments are: {{args}}

Use the command output below as the source of truth. If the uninstall succeeds, summarize what was removed and recommend `/skills reload`.
If the user did not provide any skill names, explain the installed skills from the command output and tell them to rerun `/skill-manager:uninstall <skill-name> [more-skills]`.

```text
!{python .gemini/skills/skill-manager/scripts/uninstall_skills.py {{args}}}
```
"""
''',
}
GITIGNORE_MARKER_START = "# >>> skill-manager managed workspace files >>>"
GITIGNORE_MARKER_END = "# <<< skill-manager managed workspace files <<<"
GITIGNORE_ENTRIES = [
    ".gemini/skills/",
    ".gemini/commands/",
    ".gemini/settings.json",
    ".codex/skills/",
    ".claude/skills/",
]


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


def _write_custom_commands(target_project_path: str) -> None:
    command_dir = os.path.join(
        target_project_path,
        ".gemini",
        "commands",
        "skill-manager",
    )
    os.makedirs(command_dir, exist_ok=True)
    for filename, content in COMMAND_TEMPLATES.items():
        command_path = os.path.join(command_dir, filename)
        with open(command_path, "w", encoding="utf-8") as handle:
            handle.write(content)


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


def _ensure_gitignore_entries(target_project_path: str) -> None:
    gitignore_path = os.path.join(target_project_path, ".gitignore")
    managed_block = "\n".join(
        [
            GITIGNORE_MARKER_START,
            "# Ignore installed Gemini skills managed by skill-manager",
            GITIGNORE_ENTRIES[0],
            "# Ignore local Gemini workspace commands generated by skill-manager",
            GITIGNORE_ENTRIES[1],
            "# Ignore local Gemini workspace settings written by skill-manager",
            GITIGNORE_ENTRIES[2],
            "# Ignore local Codex bridge wrappers managed by skill-manager",
            GITIGNORE_ENTRIES[3],
            "# Ignore local Claude reference skills managed by skill-manager",
            GITIGNORE_ENTRIES[4],
            GITIGNORE_MARKER_END,
        ]
    )

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as handle:
            content = handle.read()
    else:
        content = ""

    if GITIGNORE_MARKER_START in content and GITIGNORE_MARKER_END in content:
        start = content.index(GITIGNORE_MARKER_START)
        end = content.index(GITIGNORE_MARKER_END) + len(GITIGNORE_MARKER_END)
        updated = content[:start].rstrip() + "\n" + managed_block + content[end:]
    else:
        updated = content.rstrip()
        if updated:
            updated += "\n\n"
        updated += managed_block + "\n"

    with open(gitignore_path, "w", encoding="utf-8") as handle:
        handle.write(updated)


def _gemini_home_dir() -> str:
    cli_home = os.environ.get("GEMINI_CLI_HOME")
    if cli_home:
        return os.path.join(os.path.abspath(cli_home), ".gemini")

    user_profile = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    return os.path.join(os.path.abspath(user_profile), ".gemini")


def _write_plan_policy() -> str:
    policies_dir = os.path.join(_gemini_home_dir(), "policies")
    os.makedirs(policies_dir, exist_ok=True)
    policy_path = os.path.join(policies_dir, PLAN_POLICY_FILENAME)
    with open(policy_path, "w", encoding="utf-8") as handle:
        handle.write(PLAN_POLICY_CONTENT)
    return policy_path


def integrate(target_project_path: str) -> None:
    target_project_path = os.path.abspath(target_project_path)
    source_repo_root = os.environ.get("GEMINI_SKILLS_REPO_ROOT")
    if not source_repo_root:
        published_dir = os.environ.get("GEMINI_SKILLS_PUBLISHED_DIR")
        if published_dir:
            source_repo_root = os.path.dirname(os.path.abspath(published_dir))
        else:
            source_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    source_repo_root = os.path.abspath(source_repo_root)

    settings_path = os.path.join(target_project_path, ".gemini", "settings.json")
    settings = _load_json(settings_path)
    updated_settings = _ensure_session_start_hook(settings)
    _write_json(settings_path, updated_settings)

    _write_custom_commands(target_project_path)
    _write_runtime_config(target_project_path, source_repo_root)
    _ensure_gitignore_entries(target_project_path)
    policy_path = _write_plan_policy()

    print("Configured Gemini startup update hook and /skill-manager:* commands.")
    print("Preserved existing Gemini tool configuration; no workspace tool overrides were written.")
    print("Updated .gitignore to exclude local Gemini, Codex, and Claude skill-manager files.")
    print(f"Installed a Plan Mode policy for skill-manager commands at {policy_path}.")
    print("If Gemini CLI is already open, run /commands reload to load the new commands.")
    print("The startup hook will take effect the next time Gemini opens this trusted workspace.")
    print("If you use Plan Mode, restart Gemini or reload policies so the new plan policy is picked up.")
    print("If Gemini does not load the hook or commands, trust the workspace with /permissions and then retry /commands reload.")
    print("You can verify the setup with /skill-manager:list.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python post_install.py <target_project_path>")
        sys.exit(1)

    integrate(sys.argv[1])
