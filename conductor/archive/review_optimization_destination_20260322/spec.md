# Specification: Skill Destination Selection for Review Optimization

## Overview
**Track ID:** `review_optimization_destination_20260322`
**Description:** Update the `review-optimization` skill's proposer logic to give users the option to choose where a newly proposed skill should be saved (Global `gemini-skills` project, Local current project, or a Custom Path).

## Functional Requirements
1.  **Destination Prompt:** When a new skill is proposed due to repetitive actions, the CLI must present a choice menu with three options:
    -   **Global:** Save to the central `gemini-skills` repository.
    -   **Local:** Save to the current project's `.gemini/skills/` directory.
    -   **Custom Path:** Prompt the user to enter a specific file path.
2.  **Auto-Creation:** If the user selects a "Custom Path" that does not exist, the system must automatically create the necessary directory structure.
3.  **Component Updates:**
    -   **`proposer.py`:** Update the logic to format and handle the new choice menu and subsequent text prompt for custom paths.
    -   **`SKILL.md`:** Update the interactive remediation section to document these new options.
    -   **Tests:** Add unit tests for the new `proposer.py` logic and update E2E tests to cover the new interaction flow.

## Non-Functional Requirements
-   **Seamless UX:** The choice menu should use the standard `ask_user` tool format with clear labels and descriptions.
-   **Backwards Compatibility:** Existing checks and detection logic in the analyzer and auditor should remain unchanged.

## Acceptance Criteria
-   [ ] The `ask_user` call for a new skill includes the Global, Local, and Custom Path options.
-   [ ] Selecting "Custom Path" correctly prompts for a path and creates the directories if missing.
-   [ ] `SKILL.md` accurately describes the new feature.
-   [ ] All unit and E2E tests pass, covering the new logic paths.

## Out of Scope
-   Modifying the logic that detects *when* a skill should be proposed (repetition threshold).