---
name: compliance-audit-scripts
description: Codex bridge for script-focused post-change auditing. Use after editing Python, PowerShell, shell, batch, or automation files to apply the installed Gemini scripting audit with Codex-specific timing and scope.
---

# Compliance Audit Scripts Bridge

Use the installed Gemini skill at `.gemini/skills/compliance-audit-scripts/SKILL.md` as the source of truth.

Workflow:

1. Read and follow `.gemini/skills/compliance-audit-scripts/SKILL.md`.
2. If that skill references scripts, metadata, or companion files, resolve them from `.gemini/skills/compliance-audit-scripts/`.
3. Do not treat this bridge folder as the implementation source. It exists only so Codex can discover the skill without copying the Gemini payload.

## Codex Integration

Use this bridge after Codex modifies script-related files such as `.py`, `.ps1`, `.sh`, `.bat`, or Node-style automation scripts.

Post-change sequence:

1. Gather only the files changed in the current task.
2. Run the compliance audit against that bounded file set.
3. If violations are found, remediate them before proceeding.
4. After the audit is clean, invoke `review-optimization` to assess whether the workflow or skill usage should be improved.

Do not wait for Conductor phase completion. In Codex, this bridge is intended to run immediately after substantive script edits and before the final response.
