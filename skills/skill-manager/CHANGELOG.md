# Changelog

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
