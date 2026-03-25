---
name: compliance-audit-avalonia
description: Codex bridge for the installed Gemini Avalonia UI compliance audit. Use after modifying Avalonia views, XAML, view models, code-behind, styling, resources, or related desktop UI files so Codex can run the Avalonia-specific audit without copying the Gemini skill payload.
---

# Compliance Audit Avalonia Bridge

Use the installed Gemini skill at `.gemini/skills/compliance-audit-avalonia/SKILL.md` as the source of truth.

Workflow:

1. Read and follow `.gemini/skills/compliance-audit-avalonia/SKILL.md`.
2. If that skill references companion files, resolve them from `.gemini/skills/compliance-audit-avalonia/`.
3. Do not treat this bridge folder as the implementation source. It exists only so Codex can discover the skill without copying the Gemini payload.

## Codex Integration

Use this bridge after changing Avalonia UI code in Codex-managed projects:

1. Identify the modified Avalonia-facing files in the current task.
2. Run the installed Avalonia audit guidance against those changes.
3. Fix any violations before finalizing the task.
4. Follow with `review-optimization` when the task was substantial enough to warrant a post-change workflow review.

This bridge makes the Avalonia audit discoverable to Codex while keeping the real implementation in `.gemini/skills/`.
