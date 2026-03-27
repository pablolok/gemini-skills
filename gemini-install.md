# Gemini Skill Installation Instructions

This file provides the necessary context for the Gemini CLI to install official skills from this repository into another project.

## Gemini Instruction Protocol

When a user asks you to install skills from this repository, you should:

1.  **Load the Skill Manager**:
    Read and activate the skill defined in `./published/utility/skill-manager/SKILL.md`.

2.  **Initialize the Installer**:
    For a direct human CLI flow, prefer `./manage.py` as the shared launcher.
    For Gemini-driven install logic, use the `SkillInstaller` and `SkillSelector` classes from `./install.py` in this repository.

3.  **Process**:
    -   Check for updates: Use `installer.check_for_updates(target_project_path)` to see if any installed skills have newer versions.
    -   Notify user: If updates are available, inform the user and ask if they'd like to update.
    -   Scan for new skills: Scan the `./published/` directory for available skills.
    -   Prompt the user (via `ask_user`) to select the skills they want to install or update.
    -   If any selected skill supports Codex bridges under `install.config.json`, ask the user whether they also want Codex support added for those supported skills.
    -   Perform the Gemini installation/update using `installer.install_skill(skill_path, target_project_path)`.
    -   If the user opted into Codex support, add the lightweight Codex bridge with `installer.install_codex_bridge(skill_name, target_project_path)`.
    -   Prefer an explicit repo-owned wrapper from `./.codex/skills/` when one exists. Otherwise, let the installer generate a lightweight bridge for supported shared skills.
    -   Do not generate Codex bridges for Gemini-only skills or for skills with `supports.codex_bridge: false` in `install.config.json`. For example, the subagent-balancer family should not be copied into `.codex/skills/` as part of the standard install flow.
    -   `target_project_path` should be the current working directory where you were first activated.

4.  **Post-Install**:
    Ensure all `post_install.py` hooks for the selected skills are executed successfully.
