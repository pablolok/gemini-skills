# Skill Manager

Manage and install official Gemini skills from the global skills repository.

## Features

- **Interactive Installation**: Use `install.py` to select and install skills.
- **Update Checking**: Use `check_updates.py` to see if your installed skills are out of date.
- **Post-Installation Hooks**: Automatically executes `post_install.py` for project-specific setup.
- **Physical Copying**: Replaces legacy junctions with robust file copying for better version tracking.
- **Gemini CLI Integration**: Installing `skill-manager` now adds a startup update hook and a project-local `/skill-manager:*` command set.
- **Workspace Ignore Management**: Installing `skill-manager` updates the project `.gitignore` to ignore the generated Gemini workspace files it adds.

## Usage

### Install/Update Skills
Run the installer from your project's root:
```bash
python <path-to-gemini-skills>/install.py
```

Installer UX modes:
- Default CLI behavior uses a richer terminal multi-select component when running in a real TTY.
- Use `python <path-to-gemini-skills>/install.py --simple` to force the lightweight numbered prompt.
- Gemini or other agent-driven integrations should keep using the lightweight ask-user contract through `SkillInstaller` rather than the terminal widget.
- After skill selection, the installer now asks whether matching Codex bridge wrappers should also be installed for supported skills.

### Check for Updates
Run the update checker from your project's root:
```bash
python <path-to-gemini-skills>/check_updates.py
```

### Gemini CLI Startup Hook
When `skill-manager` is installed into a project, its `post_install.py` hook adds a `SessionStart` hook to `<project>/.gemini/settings.json`.

Behavior:
- On Gemini startup for that trusted workspace, the hook checks installed skills against the source `gemini-skills` repository used during installation.
- If updates are available, Gemini shows a startup message telling you to run `/skill-manager:update`.

Important notes:
- This only works in a trusted Gemini workspace. Untrusted workspaces do not load local `.gemini/settings.json` or project commands.
- The startup hook takes effect the next time Gemini opens the project.

### `/skill-manager:*` Custom Commands
Installing `skill-manager` also creates:
```text
<project>/.gemini/commands/skill-manager/list.toml
<project>/.gemini/commands/skill-manager/install.toml
<project>/.gemini/commands/skill-manager/update.toml
<project>/.gemini/commands/skill-manager/uninstall.toml
```

These commands are invoked as:
```text
/skill-manager:list
/skill-manager:install [--with-codex] <category/skill> [more-skills]
/skill-manager:update
/skill-manager:uninstall <skill-name> [more-skills]
```

Important notes:
- The built-in Gemini command is `/skills`, and it does not have an official `update` subcommand. `/skills update` will not work.
- `/skill-manager:*` are custom namespaced commands provided by `skill-manager`.
- `skill-manager` does not write `tools.core` anymore. Workspace tool overrides can shadow built-in Gemini tools such as `ask_user`, so the installer preserves existing tool settings.
- `skill-manager` also installs a user-level Plan Mode policy at `~/.gemini/policies/skill-manager-plan-mode.toml` so these commands can run while Gemini is in Plan Mode.
- `skill-manager` updates the project `.gitignore` to ignore the generated `.gemini/commands/` folder and `.gemini/settings.json`.
- If Gemini is already open when the skill is installed, run `/commands reload` once so Gemini picks up the new custom command without restarting.
- After updates are applied, run `/skills reload` to refresh Gemini's discovered skill list in the current session.

### Trust This Workspace

Project-level hooks and custom commands only work in a trusted Gemini workspace.

Recommended verification flow after installing or updating `skill-manager`:
- open Gemini in the project
- run `/permissions`
- trust the workspace if it is not already trusted
- run `/commands reload` if Gemini was already open during install or update
- test with `/skill-manager:list`

Expected behavior:
- Gemini may show a warning that the project contains a hook such as `skill-manager-update-check`
- that warning is expected for a trusted project using `skill-manager`
- if updates are available, the startup hook should tell you to run `/skill-manager:update`

If `/skill-manager:*` exists but the shell command is blocked, that usually means your current Gemini policy or approval mode is preventing custom-command shell execution. In that case, verify the workspace is trusted first, then re-check your Gemini permissions, approval settings, and any user-level Gemini policies.

Expected settings change:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "name": "skill-manager-update-check",
            "type": "command",
            "command": "python .gemini/skills/skill-manager/scripts/session_start_hook.py"
          }
        ]
      }
    ]
  }
}
```

`skill-manager` now limits its `settings.json` writes to the startup hook. It intentionally preserves existing tool settings so it does not disable built-in Gemini behavior such as `ask_user`.

Expected `.gitignore` block:
```gitignore
# >>> skill-manager managed workspace files >>>
# Ignore local Gemini workspace commands generated by skill-manager
.gemini/commands/
# Ignore local Gemini workspace settings written by skill-manager
.gemini/settings.json
# <<< skill-manager managed workspace files <<<
```

`skill-manager` manages that block during install and update so the generated Gemini workspace state stays local by default.

Expected Plan Mode policy:
```toml
[[rule]]
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
```

That policy is written to `~/.gemini/policies/skill-manager-plan-mode.toml` during install or update so the commands can work in Plan Mode too.

### Codex Bridge Integration

If a project is used with both Gemini and Codex, keep the responsibilities split:

- `.gemini/skills/` contains the real Gemini skill payloads.
- `.codex/skills/` contains lightweight Codex bridge wrappers that point Codex at the installed Gemini skills.

Recommended Codex flow:
- install or update the Gemini skill first
- add or refresh the matching Codex bridge
- keep the bridge lightweight and descriptive instead of copying the Gemini implementation
- if a Codex bridge is only project-local helper state and is not intentionally repo-owned, add it to `.gitignore` instead of committing it

Supported install flows:
- `install.py` asks whether supported selected skills should also get `.codex/skills/` bridge wrappers
- `/skill-manager:install --with-codex ...` installs the Gemini skill and any matching Codex bridge wrappers in one step
- if a skill has no bridge wrapper in this repository, no `.codex` copy is created

The standard Codex bridge skills in this repo are audit/review/publishing/install bridges. The balancer family is Gemini-specific and should not normally be treated as Codex bridge skills.

## Post-Installation Hooks

Skills can include a `post_install.py` script that will be executed after installation. This is commonly used by skills like `review-optimization` to inject protocol entries into `conductor/workflow.md`, or by `skill-manager` to configure Gemini-local hooks and commands.
