# Gemini Skill Installation Instructions

This file provides the necessary context for the Gemini CLI to install official skills from this repository into another project.

## Gemini Instruction Protocol

When a user asks you to install skills from this repository, you should:

1.  **Load the Skill Manager**:
    Read and activate the skill defined in `./published/utility/skill-manager/SKILL.md`.

2.  **Initialize the Installer**:
    Use the `SkillInstaller` and `SkillSelector` classes from `./install.py` in this repository.

3.  **Process**:
    -   Check for updates: Use `installer.check_for_updates(target_project_path)` to see if any installed skills have newer versions.
    -   Notify user: If updates are available, inform the user and ask if they'd like to update.
    -   Scan for new skills: Scan the `./published/` directory for available skills.
    -   Prompt the user (via `ask_user`) to select the skills they want to install or update.
    -   Perform the installation/update using `installer.install_skill(skill_path, target_project_path)`.
    -   `target_project_path` should be the current working directory where you were first activated.

4.  **Post-Install**:
    Ensure all `post_install.py` hooks for the selected skills are executed successfully.
