---
name: skill-publisher
description: Standardize and automate the publishing of stable skills from the development directory to the 'published' directory.
---

# Skill Publisher

This skill helps you maintain the integrity of official skills by automating the synchronization between the development `skills/` directory and the public-facing `published/` directory.

## Publishing Protocol

When a user asks you to "publish" or "sync" a skill, follow these steps:

### 1. Identify and Validate Source
-   Ensure the skill exists in `skills/<skill-name>`.
-   **Validation Checklist**:
    -   [ ] `SKILL.md`: Must have correct frontmatter (name, description).
    -   [ ] `README.md`: Must be present, accurately describe the skill, and reflect the current workflow, scripts, installation path, and trigger behavior.
    -   [ ] Code Quality: All tests in `tests/skills/` must pass.
    -   [ ] Structure: Follows the standard skill layout (e.g., Python packages use `_`, folders use `-`).

### 2. Determine Destination
-   Map the skill to its category in `published/`:
    -   `audit/`: Compliance, linting, review tools.
    -   `workflow/`: Project management, Conductor integrations.
    -   `utility/`: General tools, managers.

### 3. Synchronize
-   **Step 3.1**: Clean the existing destination folder in `published/<category>/<skill-name>`.
-   **Step 3.2**: Perform a recursive copy of the validated source.
-   **Step 3.3**: Verify that all file names remain consistent (e.g., maintain hyphens for folders).
-   **Step 3.4**: Ensure `README.md` is copied and remains aligned with the newly published `SKILL.md`, scripts, and metadata. If the README is stale, update it before finishing the publish.

### 4. Finalize
-   **Step 4.1: Versioning**:
    -   Compare the version in `skills/<skill-name>/metadata.json` with `published/<category>/<skill-name>/metadata.json`.
    -   If changes are detected, increment the version in the source `metadata.json` (use SemVer: patch for fixes, minor for features).
    -   Ensure the destination `metadata.json` matches the new version.
-   **Step 4.2: Changelog**:
    -   Use the workspace-local `changelog-manager` skill at `.gemini/skills/changelog-manager/SKILL.md` as the source of truth for changelog formatting.
    -   If a `CHANGELOG.md` exists in the skill folder, append the current date and version with a summary of changes using the canonical changelog format.
    -   If it doesn't exist, create one using that same canonical format.
-   **Step 4.3: Documentation Check**:
    -   Re-read the source and published `README.md` files.
    -   Confirm they mention any newly added scripts, hooks, Codex integration notes, or workflow changes introduced by this publish.
-   **Step 4.4: Global Metadata**: Update any global metadata if required.
-   **Step 4.5: Commit**: Commit the changes with a clear message: `feat(published): sync skill '<skill-name>' to version <new-version>`.
