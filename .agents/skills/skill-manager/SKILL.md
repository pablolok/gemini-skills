---
name: skill-manager
description: Manage and install official Gemini skills from the global skills repository.
---

# Skill Manager

This skill allows Gemini to manage official skills into the current project by interacting with the `manage.py`, `install.py`, and `uninstall.py` scripts from the global `gemini-skills` repository.

## Usage

### 1. List Available Skills
To see what's available, you must first locate the `gemini-skills` repository on the user's machine.

**Search Pattern:** `**/gemini-skills/manage.py`

Once found, you can scan for skills:
```python
from install import SkillInstaller
installer = SkillInstaller("<path-to-gemini-skills>/published", ask_user_fn)
available = installer.get_available_skills()
```

For direct human CLI usage, prefer `python <path-to-gemini-skills>/manage.py` as the shared launcher entry point.
If the terminal is not already in the destination project root, pass `--target-project <path>` (or `--project-root <path>`) so installs and uninstalls mutate the intended repository instead of the current working directory.

### 2. Install Skills
To install a skill, use the `SkillInstaller` and `SkillSelector` logic.

```python
# 1. Ask user to select from 'available'
# 2. For each selected skill_path:
installer.install_skill(skill_path, os.getcwd())
```

For direct human CLI usage, `install.py` may use a richer terminal multi-select UI. For Gemini or programmatic usage, keep using the lightweight `ask_user`-compatible flow exposed by `SkillSelector` and `SkillInstaller`.
For direct CLI usage, the installer should resolve the target project from `--target-project` / `--project-root` when present, otherwise from the current working directory, and it should print the exact target path plus the managed `.gemini/`, `.codex/`, `.claude/`, and `skill-manager` integration locations after a successful install.

If the user also wants Codex or Claude companion artifacts, install the Gemini skill first and then use `install_codex_bridge(...)` and/or `install_claude_reference(...)`, or pass `--with-codex` and `--with-claude` through the installed `/skill-manager:install` helper.
Only offer those companion artifacts when the repo-level `install.config.json` marks the skill as eligible for them.
For Codex, prefer an explicit repo-owned wrapper when one exists; otherwise generate a lightweight bridge for supported shared skills instead of skipping Codex support entirely.

### 2b. Uninstall Skills
To remove managed skills, use the `uninstall.py` entry point or the installed `/skill-manager:uninstall` helper.

Rules:
- Only offer skills currently tracked as managed.
- Do not treat arbitrary local `.gemini/skills/`, `.codex/skills/`, or `.claude/skills/` folders as uninstall candidates.
- Reuse the existing uninstall runtime path instead of duplicating manifest, companion cleanup, or `.gitignore` refresh logic.
- For direct CLI usage, resolve the target project from `--target-project` / `--project-root` when present, otherwise from the current working directory, and print the exact target path so the user can verify where the uninstall is operating.
- If uninstalling one managed artifact raises an OS-level removal error, log it, keep that artifact registered, and continue removing the other managed companion artifacts instead of crashing the whole uninstall flow.

### 3. Check for Updates
To check if installed skills have newer versions available in the global repository:

```python
updates = installer.check_for_updates(os.getcwd())
if updates:
    # Notify user about available updates
    # Each item in 'updates' has: name, installed, latest, rel_path
```

### 4. Update Skills
To update a skill, simply reinstall it. The installer will handle overwriting existing files and cleaning up legacy junctions.

```python
for update in updates:
    installer.install_skill(update['rel_path'], os.getcwd())
```

### 5. Post-Installation Hooks (`post_install.py`)
Skills can include a `post_install.py` script that will be automatically executed by `SkillInstaller` after copying files into the project. Use this hook for:
- Injecting project-specific protocol entries into `conductor/workflow.md`.
- Modifying local configurations (e.g., updating `.gitignore`).
- Performing environment-specific setup tasks.
- Configuring Gemini-local startup hooks and custom commands.

### 6. Checking for Updates (CLI)
A standalone `check_updates.py` script is available for non-interactive updates checking:
```bash
python <path-to-gemini-skills>/check_updates.py
```
It displays available updates in the standardized format: `[Update Available] <skill-name> (vX -> vY)`.

### 7. Gemini CLI Integration
Installing `skill-manager` should configure two project-local Gemini integration points:

- A `SessionStart` hook in `<project>/.gemini/settings.json` that checks for updates when Gemini opens the trusted workspace.
- A command set under `<project>/.gemini/commands/skill-manager/`, invoked as `/skill-manager:list`, `/skill-manager:install`, `/skill-manager:update`, and `/skill-manager:uninstall`.

Important:
- Gemini's built-in `/skills` command does not support an `update` subcommand, so `/skills update` is not expected to work.
- Custom `skill-manager` commands should use the `/skill-manager:*` namespace rather than trying to extend the built-in `/skills` tree.
- Custom commands must be reloaded with `/commands reload` if Gemini is already open when the installer adds them.
- The startup hook only loads in trusted workspaces because Gemini ignores local `.gemini/settings.json` in untrusted folders.
- The installer should not write `tools.core`. Workspace tool overrides can shadow built-in Gemini tools such as `ask_user`, so `skill-manager` must preserve any existing tool configuration.
- The installer should also add a narrow user policy in `~/.gemini/policies/skill-manager-plan-mode.toml` so those same commands can run while Gemini is in Plan Mode.
- The installer should also maintain a small managed block in the project `.gitignore` for the managed skill artifacts it creates.
- That block should ignore `.gemini/commands/`, `.gemini/settings.json`, `.gemini/skill-manager-manifest.json`, and only the exact `.gemini/skills/<skill>/`, `.codex/skills/<skill>/`, and `.claude/skills/<skill>/` directories that were installed by `skill-manager`.
- If the managed block already exists, replace only the content between the markers and preserve the rest of the user's `.gitignore`.
- If `.gemini/skill-manager-manifest.json` is missing, bootstrap exact skill entries from the existing local `.gemini/skills/`, `.codex/skills/`, and `.claude/skills/` directories before writing the managed block.
- Use `install.config.json` as the source of truth for whether a skill is `shared` or `gemini-only`, and for whether Codex bridges or Claude references should be offered at install time.
- Hard stop: never rewrite, regenerate, or replace the full `.gitignore` file to satisfy `skill-manager` behavior.
- Hard stop: if an edit path would touch anything outside the managed marker block, abort that path and fix the implementation instead.

### 8. Trust and Verification
If a user reports that the startup hook or `/skill-manager:*` commands do not appear to work:

1. Verify the workspace is trusted in Gemini via `/permissions`.
2. Verify `<project>/.gemini/settings.json` exists and contains the `skill-manager-update-check` SessionStart hook.
3. Verify `<project>/.gemini/settings.json` still contains the `skill-manager-update-check` SessionStart hook and that existing tool settings were preserved rather than overwritten.
4. Verify `~/.gemini/policies/skill-manager-plan-mode.toml` exists and contains the allowlist rule for the `skill-manager` Python helper commands in `modes = ["plan"]`.
5. Verify `<project>/.gemini/commands/skill-manager/` exists with the generated `.toml` command files.
6. Verify the project `.gitignore` contains the managed `skill-manager` block that ignores `.gemini/commands/`, `.gemini/settings.json`, `.gemini/skill-manager-manifest.json`, and the exact installed skill directories managed by `skill-manager`.
7. If Gemini was already open when the skill was installed or updated, instruct the user to run `/commands reload` and restart Gemini if Plan Mode policies appear unchanged.
8. Test with `/skill-manager:list`.
9. If the command exists but Gemini reports the shell command is blocked, explain that the user-level or system-level Gemini policy is still overriding the new plan policy.

### 9. Codex Bridge Hygiene

For projects that also use Codex:
- Keep real Gemini skills in `.gemini/skills/`.
- Keep `.codex/skills/` lightweight and descriptive.
- Only commit Codex bridge wrappers when they are intentionally repo-owned.
- If a Codex bridge is just local helper state for one project, instruct the user to add it to `.gitignore` rather than versioning it.

### 10. Claude Reference Skills

For projects that also use Claude:
- Keep real Gemini skills in `.gemini/skills/`.
- Keep `.claude/skills/` lightweight and reference-only.
- Prefer generated Claude reference skills that point Claude at the installed Gemini skill path instead of copying the Gemini payload.
- If a Claude reference skill is only local helper state for one project, instruct the user to add it to `.gitignore` rather than versioning it.
- Do not generate Claude references for skills marked `distribution: "gemini-only"` or for skills with `supports.claude_reference: false` in `install.config.json`.

## Integration
This skill ensures that official skills are physically copied into the target project (replacing legacy junctions) to enable robust version tracking. It automatically triggers `post_install.py` hooks to maintain workflow consistency across different project environments, including Gemini-local update hooks and custom command setup when the installed skill supports them.
