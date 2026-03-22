# Specification: Post-Execution Review & Optimization Skill

## Overview
**Track ID:** `review_optimization_skill_20260320`
**Description:** Implement a "Post-Execution Review & Optimization" skill. This specialized agent runs after a phase completion but before final user verification. Its goal is to analyze the preceding execution path to identify missed opportunities for skill usage, evaluate the quality of custom skills employed, and suggest workflow optimizations.

## Functional Requirements
1.  **Checkpoint Integration:** The skill MUST be triggered as a mandatory step within the `Phase Completion Verification and Checkpointing Protocol` defined in `workflow.md`.
2.  **Execution Log Analysis:** The skill MUST analyze the current session's tool call history and task progress to reconstruct the implementation path.
3.  **Skill Efficiency Audit:**
    -   Identify if any existing, relevant skills were NOT activated during the execution.
    -   Evaluate the performance of activated skills (e.g., did they require manual correction? were they used according to their internal instructions?).
    -   Flag "badly written" or "inefficient" custom skills that hindered the workflow.
4.  **Workflow Optimization Advice:**
    -   Compare the actual execution path against the `plan.md` and `workflow.md`.
    -   Suggest alternative tool sequences or strategies for future tasks.
5.  **Interactive Remediation:**
    -   Instead of just reporting, the skill MUST provide interactive prompts (using `ask_user` or similar) to allow the user to immediately:
        -   Refine the workflow.
        -   Update a faulty or inefficient skill.
        -   **Propose the creation of a brand-new skill** if a recurring manual pattern is detected without an existing skill to handle it.

## Non-Functional Requirements
-   **Low Overhead:** The analysis should be fast and not significantly delay the checkpoint process.
-   **High Accuracy:** Recommendations must be grounded in the project's specific context (C#, Python, Gemini CLI).
-   **Context-Aware:** The skill must respect the `GEMINI.md` and `plan.md` as the sources of truth.

## Acceptance Criteria
-   [ ] The skill is successfully activated at the end of a phase.
-   [ ] It identifies at least one "missed skill" or "workflow optimization" in a test scenario.
-   [ ] It provides a clear, interactive prompt to address a detected issue.
-   [ ] The skill's own implementation follows the TDD and coverage standards (>80%).

## Out of Scope
-   Automatic execution of code fixes (remediation must be user-approved/interactive).
-   General-purpose code linting (already covered by existing linter/audit tools).
