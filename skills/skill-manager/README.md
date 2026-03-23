# Skill Manager

Manage and install official Gemini skills from the global skills repository.

## Features

- **Interactive Installation**: Use `install.py` to select and install skills.
- **Update Checking**: Use `check_updates.py` to see if your installed skills are out of date.
- **Post-Installation Hooks**: Automatically executes `post_install.py` for project-specific setup.
- **Physical Copying**: Replaces legacy junctions with robust file copying for better version tracking.
- **Gemini CLI Integration**: Installing `skill-manager` now adds a startup update hook and a project-local `/skills:update` custom command.

## Usage

### Install/Update Skills
Run the installer from your project's root:
```bash
python <path-to-gemini-skills>/install.py
```

### Check for Updates
Run the update checker from your project's root:
```bash
python <path-to-gemini-skills>/check_updates.py
```

### Gemini CLI Startup Hook
When `skill-manager` is installed into a project, its `post_install.py` hook adds a `SessionStart` hook to `<project>/.gemini/settings.json`.

Behavior:
- On Gemini startup for that trusted workspace, the hook checks installed skills against the source `gemini-skills` repository used during installation.
- If updates are available, Gemini shows a startup message telling you to run `/skills:update`.

Important notes:
- This only works in a trusted Gemini workspace. Untrusted workspaces do not load local `.gemini/settings.json` or project commands.
- The startup hook takes effect the next time Gemini opens the project.

### `/skills:update` Custom Command
Installing `skill-manager` also creates:
```text
<project>/.gemini/commands/skills/update.toml
```

That command is invoked as:
```text
/skills:update
```

Important notes:
- The built-in Gemini command is `/skills`, and it does not have an official `update` subcommand. `/skills update` will not work.
- `/skills:update` is a custom namespaced command provided by `skill-manager`.
- If Gemini is already open when the skill is installed, run `/commands reload` once so Gemini picks up the new custom command without restarting.
- After updates are applied, run `/skills reload` to refresh Gemini's discovered skill list in the current session.

## Post-Installation Hooks

Skills can include a `post_install.py` script that will be executed after installation. This is commonly used by skills like `review-optimization` to inject protocol entries into `conductor/workflow.md`, or by `skill-manager` to configure Gemini-local hooks and commands.
