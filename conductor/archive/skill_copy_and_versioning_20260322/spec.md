# Specification: Skill Installation & Versioning

## Overview
This track replaces the current junction-based installation method with a more robust file-copying mechanism. It also implements a versioning system for skills in `metadata.json` to allow Gemini to check for updates and notify the user when a skill can be updated.

## Functional Requirements
- **Copy Installation**: The installer (`install.py`) must copy all files from the `skills/` or `published/` directory to the target project directory, replacing any existing files.
- **Versioning System**: Each skill's `metadata.json` must include a `version` field using Semantic Versioning (SemVer, e.g., `1.0.0`).
- **Update Check Mechanism**:
    - **Skill Manager integration**: The `skill-manager` skill should check for updates to its dependencies when it is run.
    - **Startup Hook**: Implement a script that can be hooked to Gemini startup (if supported) or run manually to check for updates across all installed skills.
    - **Manual Command**: Provide a way for users to manually check for updates.
- **Update Notifications**: If a newer version is available in the `skills/` or `published/` directory compared to the version installed in the project, Gemini should notify the user.
- **Dependency Versioning**: When dependencies are installed, the resolver should also check for the minimum required version (if implemented).

## Non-Functional Requirements
- **Idempotency**: The installation process should be idempotent; running it multiple times should result in the same state.
- **Transparency**: Provide clear feedback on which files are being copied and why.
- **Ease of Use**: The transition from junctions to copying should be seamless for existing projects.

## Acceptance Criteria
- [ ] Skills are installed by copying files instead of creating junctions.
- [ ] `metadata.json` includes a `version` field for all official skills.
- [ ] Gemini detects when an installed skill's version is lower than the version available in the skills repository.
- [ ] The user is notified of available updates through multiple channels (Skill Manager, manual check).
- [ ] A manual update command successfully updates an installed skill to the latest version.

## Out of Scope
- Automatic background updates (updates should always be user-confirmed).
- Rollback mechanism to previous versions (for now).
