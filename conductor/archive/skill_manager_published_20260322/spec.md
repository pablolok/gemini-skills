# Specification: Interactive Skill Management and 'Published' Directory

## Overview
**Track ID:** `skill_manager_published_20260322`
**Description:** Introduce a robust mechanism for managing and distributing official Gemini skills. This includes a categorized `published/` directory for stable versions, an interactive CLI prompt to install these skills into projects using junctions, and skill-specific post-installation hooks.

## Functional Requirements
1.  **Official 'Published' Folder**:
    - Create a `published/` directory in the root of the repository.
    - Structure this directory by category (e.g., `audit/`, `workflow/`, `utility/`).
2.  **Interactive Skill Manager Tool**:
    - Implement a script (e.g., `install.py`) that can be executed from *other* repositories (e.g., via `python <path-to-gemini-skills>/install.py`).
    - Use an interactive prompt to allow users to select skills from the `published/` folder.
3.  **Automatic Installation (Junctions)**:
    - For each selected skill, automatically create a Windows Directory Junction (or symlink on non-Windows) from the target project's `.gemini/skills/<skill-name>` to the source in `published/<category>/<skill-name>`.
4.  **Skill-Specific Post-Installation Hooks**:
    - Each skill can optionally include a `post_install.py` script.
    - The installer tool MUST execute this script after creating the junction.
    - Examples of post-install actions:
        - Integrate with the project's `conductor/workflow.md`.
        - Add configuration to project files.
        - Create required sample directories.
5.  **Project Context Awareness**:
    - The installer and hooks should detect if the target project uses Conductor and adapt the installation accordingly.

## Non-Functional Requirements
- **OS Compatibility**: Focus on Windows (Junctions) with extensibility.
- **Robustness**: Gracefully handle missing directories or permission issues.

## Acceptance Criteria
- [ ] A `published/` directory exists with a categorized structure.
- [ ] Running `install.py` from an external project correctly prompts for skill selection.
- [ ] Junctions are created successfully in the external project.
- [ ] `post_install.py` hooks are executed and successfully integrate the skill (e.g., adding a task to `workflow.md`).

## Out of Scope
- Automatic updates (handled by junctions).
- Full uninstallation logic (manual for now).
