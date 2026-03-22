# Implementation Plan: Skill Installation & Versioning

## Phase 1: Metadata Update & Initial Versioning

- [ ] Task: Research and define the data structure for the `version` field in `metadata.json`.
- [ ] Task: Update the `metadata.json` schema to include the `version` field.
- [ ] Task: Add a `version` field to all skills in the `skills/` and `published/` directories (e.g., `1.0.0`).
- [ ] Task: Write tests to verify that the version fields are correctly parsed.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Metadata Update & Initial Versioning' (Protocol in workflow.md)

## Phase 2: Copy Installation Implementation

- [ ] Task: Modify `install.py` to replace junction creation with file copying for skill installation.
- [ ] Task: Implement the file-copying logic focusing on:
    - [ ] Recursively copying files.
    - [ ] Overwriting existing files in the target directory.
    - [ ] Maintaining the directory structure.
- [ ] Task: Write integration tests to confirm that skills are correctly installed by copying files.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Copy Installation Implementation' (Protocol in workflow.md)

## Phase 3: Version Comparison & Update Check Logic

- [ ] Task: Implement a `VersionComparator` class to handle SemVer comparison logic.
- [ ] Task: Implement the logic to check for updates by comparing the installed version in a project against the version in the `skills/` or `published/` directory.
- [ ] Task: Write tests for the `VersionComparator` and update check logic.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Version Comparison & Update Check Logic' (Protocol in workflow.md)

## Phase 4: Integration & Notifications

- [ ] Task: Integrate update checks into the `skill-manager` skill.
- [ ] Task: Create a standalone `check_updates.py` script for manual update checks.
- [ ] Task: Implement the logic to notify the user when updates are available.
- [ ] Task: Integrate the update check into the Gemini startup process (if possible, or provide a recommended command).
- [ ] Task: Write integration tests for the full update notification flow.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration & Notifications' (Protocol in workflow.md)

## Phase 5: Final Review & Documentation

- [ ] Task: Verify that the transition from junctions to copying works correctly in existing projects.
- [ ] Task: Update the project documentation (e.g., `README.md`) to reflect the new installation method and versioning system.
- [ ] Task: Perform a final end-to-end test of the skill installation and update process.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Final Review & Documentation' (Protocol in workflow.md)
