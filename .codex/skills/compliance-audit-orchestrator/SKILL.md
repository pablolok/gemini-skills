---
name: compliance-audit-orchestrator
description: A Codex bridge for the canonical Gemini compliance audit orchestrator skill.
---

# Compliance Audit Orchestrator Bridge

Use the installed Gemini skill at `.gemini/skills/compliance-audit-orchestrator/SKILL.md` as the source of truth.

Workflow:

1. Read and follow `.gemini/skills/compliance-audit-orchestrator/SKILL.md`.
2. If that skill references scripts, metadata, or companion files, resolve them from `.gemini/skills/compliance-audit-orchestrator/`.
3. Do not treat this bridge folder as the implementation source. It exists only so Codex can discover the skill without copying the Gemini payload.

## Codex Integration

Codex does not use Gemini Conductor checkpoints automatically. When code files change during a Codex task, use this bridge as a post-change verification step:

1. Identify the modified files in the current task.
2. If the changed files are scripts or automation files, invoke the Codex bridge for `compliance-audit-scripts`.
3. If the relevant audit reports violations, fix them before finalizing the task.
4. After the compliance audit completes, invoke the Codex bridge for `review-optimization`.
5. Only skip this sequence when the task is read-only, documentation-only, or the changed files are clearly outside the audit scope.

This bridge is the Codex entry point for "audit, then optimize" after file changes.
