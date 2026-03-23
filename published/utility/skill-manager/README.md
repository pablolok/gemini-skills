# Skill Manager

Manage and install official Gemini skills from the global skills repository.

## Features

- **Interactive Installation**: Use `install.py` to select and install skills.
- **Update Checking**: Use `check_updates.py` to see if your installed skills are out of date.
- **Post-Installation Hooks**: Automatically executes `post_install.py` for project-specific setup.
- **Physical Copying**: Replaces legacy junctions with robust file copying for better version tracking.
- **Gemini CLI Integration**: Installing `skill-manager` now adds a startup update hook and a project-local `/skill-manager:*` command set.

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
/skill-manager:install <category/skill> [more-skills]
/skill-manager:update
/skill-manager:uninstall <skill-name> [more-skills]
```

Important notes:
- The built-in Gemini command is `/skills`, and it does not have an official `update` subcommand. `/skills update` will not work.
- `/skill-manager:*` are custom namespaced commands provided by `skill-manager`.
- `skill-manager` adds `run_shell_command(python)` to workspace `tools.core` so these commands can execute their helper scripts.
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

If `/skill-manager:*` exists but the shell command is blocked, that usually means your current Gemini policy or approval mode is preventing custom-command shell execution. In that case, verify the workspace is trusted first, then re-check your Gemini permissions and approval settings.

Expected settings change:
```json
{
  "tools": {
    "core": ["run_shell_command(python)"]
  }
}
```

`skill-manager` adds that allowlist entry during install or update if it is missing. It does not remove broader existing tool allowances if you already configured them.

### Codex Bridge Integration

If a project is used with both Gemini and Codex, keep the responsibilities split:

- `.gemini/skills/` contains the real Gemini skill payloads.
- `.codex/skills/` contains lightweight Codex bridge wrappers that point Codex at the installed Gemini skills.

Recommended Codex flow:
- install or update the Gemini skill first
- add or refresh the matching Codex bridge
- keep the bridge lightweight and descriptive instead of copying the Gemini implementation

The standard Codex bridge skills in this repo are audit/review/publishing/install bridges. The balancer family is Gemini-specific and should not normally be treated as Codex bridge skills.

## Post-Installation Hooks

Skills can include a `post_install.py` script that will be executed after installation. This is commonly used by skills like `review-optimization` to inject protocol entries into `conductor/workflow.md`, or by `skill-manager` to configure Gemini-local hooks and commands.
