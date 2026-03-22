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
    -   [ ] `README.md`: Must be present and accurately describe the skill.
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

### 4. Finalize
-   Update any global metadata if required.
-   Commit the changes with a clear message: `feat(published): sync skill '<skill-name>' to version <date>`.
