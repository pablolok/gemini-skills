---
name: review-optimization
description: Codex final post-change review step. Uses the installed Gemini review-optimization skill to assess workflow quality, missed skill usage, and improvement opportunities after auditing or significant file edits.
---

# Review Optimization Bridge

Use the installed Gemini skill at `.gemini/skills/review-optimization/SKILL.md` as the source of truth.

Workflow:

1. Read and follow `.gemini/skills/review-optimization/SKILL.md`.
2. If that skill references scripts, metadata, or companion files, resolve them from `.gemini/skills/review-optimization/`.
3. Do not treat this bridge folder as the implementation source. It exists only so Codex can discover the skill without copying the Gemini payload.

## Codex Integration

In Codex, invoke this bridge after compliance auditing or after any substantial file-editing task where workflow quality matters.

Codex-oriented sequence:

1. Review the actual tool usage and file edits from the current task only.
2. Identify missed skill usage, noisy steps, or avoidable context churn.
3. Suggest improvements to the relevant skill or wrapper when needed.
4. Prefer running this after `compliance-audit-orchestrator` or `compliance-audit-scripts`, not as a replacement for them.

This makes `review-optimization` the final post-change step for Codex instead of a Conductor-only checkpoint task.
