# Changelog

## [1.3.2] - 2026-03-23
- Add /skill-manager commands, fix runtime pathing, and document trust verification


## [1.3.1] - 2026-03-23
- Replace /skills:update with /skill-manager:* commands and fix runtime hook paths


## 1.3.0 (2026-03-23)
- Replace the misleading `/skills:update` custom command with a `/skill-manager:*` command namespace
- Add generated `list`, `install`, `update`, and `uninstall` commands during skill-manager install/update
- Fix the runtime config source-repo path so updates resolve the correct `published/` directory
- Update the startup hook message to tell users to run `/skill-manager:update`

## 1.2.0 (2026-03-23)
- Add a richer terminal multi-select installer UI for direct CLI use
- Keep a lightweight ask-user installer path for Gemini and programmatic integrations
- Add `--simple` to force the lightweight numbered prompt

## [1.1.1] - 2026-03-23
- Add Gemini startup update hook and /skills:update command


## 1.1.0 (2026-03-23)
-   Added a real `post_install.py` hook for `skill-manager`.
-   Added project-local Gemini integration:
    -   `SessionStart` update hook in `.gemini/settings.json`
    -   `/skills:update` custom command in `.gemini/commands/skills/update.toml`
-   Added runtime scripts so the installed `skill-manager` can check and apply updates using the source `gemini-skills` repository path captured at install time.
-   Clarified in docs that `/skills update` is not a built-in Gemini subcommand and that `/skills:update` is the supported custom command.

## 1.0.1 (2026-03-23)
-   Added documentation for `post_install.py` hooks.
-   Added documentation for `check_updates.py`.
-   Standardized update format: `[Update Available] <skill-name> (vX -> vY)`.
-   Improved version tracking and physical copying support.

## 1.0.0
-   Initial release of the skill manager.
-   Support for `SkillInstaller` and `SkillSelector`.
