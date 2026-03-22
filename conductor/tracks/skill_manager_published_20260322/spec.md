# Specification: Interactive Skill Management and 'Published' Directory

## Overview
**Track ID:** `skill_manager_published_20260322`
**Description:** Introduce a robust mechanism for managing and distributing official Gemini skills. This includes a categorized `published/` directory for stable versions and an interactive CLI prompt to install these skills into projects using junctions (symlinks).

## Functional Requirements
1.  **Official 'Published' Folder**:
    - Create a `published/` directory in the root of the repository.
    - Structure this directory by category (e.g., `audit/`, `workflow/`, `utility/`).
    - Skills in `published/` are considered stable ("official") versions.
2.  **Interactive Skill Selector**:
    - Implement a command or tool that lists all skills in the `published/` directory.
    - Use an interactive prompt (e.g., checkbox list) to allow users to select multiple skills.
3.  **Automatic Installation (Junctions)**:
    - For each selected skill, automatically create a Windows Directory Junction (or symlink on non-Windows) from the target project's `.gemini/skills/<skill-name>` to the source in `published/<category>/<skill-name>`.
    - Handle cases where the target directory doesn't exist.
4.  **Skill Synchronization**:
    - Ensure that changes made in the `published/` folder are reflected in projects using junctions without requiring re-installation.

## Non-Functional Requirements
- **OS Compatibility**: Primarily focused on Windows (Junctions), but should be extensible to other OS (Symlinks).
- **Clarity**: The interactive prompt should show skill descriptions to help with selection.

## Acceptance Criteria
- [ ] A `published/` directory exists with a categorized structure.
- [ ] An interactive prompt correctly lists all skills in `published/`.
- [ ] Selecting a skill and confirming successfully creates a junction in the project's `.gemini/skills/` folder.
- [ ] The system correctly handles existing junctions (skip or overwrite options).

## Out of Scope
- Automatic updates of skills (since junctions handle this natively).
- Removing skills via the manager (manual deletion for now).
