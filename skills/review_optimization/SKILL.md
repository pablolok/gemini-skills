---
name: review-optimization
description: Use after a phase completion but before final user verification to analyze execution history, audit skill efficiency, and suggest workflow optimizations.
---

# Post-Execution Review & Optimization

This skill is a mandatory audit tool that runs during the checkpoint protocol. Its primary goal is to ensure the most efficient implementation path was taken and that custom skills are being utilized and maintained correctly.

## Workflow Optimization Logic

When you are triggered (manually or as part of the checkpoint protocol), you MUST:

1.  **Analyze Execution History:** Review the session's tool call log to reconstruct the sequence of actions taken during the phase.
2.  **Audit Skill Efficiency:**
    *   **Missed Opportunities:** Identify if any existing skills were relevant but NOT activated.
    *   **Performance Evaluation:** Evaluate if activated skills performed as expected or required manual overrides.
    *   **Skill Quality:** Flag any "noisy" or "inefficient" skills that should be refactored.
3.  **Cross-Reference Source of Truth:** Compare the actual execution against the `plan.md` and `workflow.md`.
4.  **Recommend Improvements:** Suggest alternative tool sequences or strategies for future tasks to minimize context usage and turns.

## Analysis Scope

Your analysis MUST cover:
- Tool call frequency and sequence.
- Compliance with the "Standard Task Workflow".
- Accuracy of `plan.md` updates and Git notes.
- Efficiency of search and read patterns.

## Interactive Remediation

You MUST NOT apply changes automatically. Instead, provide interactive recommendations via `ask_user`:
- **Workflow Refinement:** "I noticed a more efficient pattern for [task type]. Would you like to update the `workflow.md` guidelines?"
- **Skill Update:** "The skill '[skill name]' was used but required manual correction. Should we refine its `SKILL.md` now?"
- **New Skill Proposal:** "I detected a recurring manual pattern for [process]. Would you like to create a new skill to automate this?"

## Triggering

This skill is automatically invoked during the `Phase Completion Verification and Checkpointing Protocol` in `workflow.md`. It can also be manually triggered by the user if they suspect workflow drift or skill inefficiency.
