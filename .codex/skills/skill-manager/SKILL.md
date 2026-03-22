---
name: skill-manager
description: A Codex bridge for the canonical Gemini skill-manager skill.
---

# Skill Manager Bridge

Use the installed Gemini skill at `.gemini/skills/skill-manager/SKILL.md` as the source of truth.

Workflow:

1. Read and follow `.gemini/skills/skill-manager/SKILL.md`.
2. If that skill references scripts, metadata, or companion files, resolve them from `.gemini/skills/skill-manager/`.
3. Do not treat this bridge folder as the implementation source. It exists only so Codex can discover the skill without copying the Gemini payload.

## Codex Integration

For Codex-managed projects, keep the responsibilities split:

- `.gemini/skills/` contains the actual Gemini/Conductor skill implementations.
- `.codex/skills/` contains only Codex bridges and Codex-specific integration notes.

When installing, updating, or auditing skills from Codex, preserve both layers. Do not replace Gemini skills with Codex wrappers and do not copy full Gemini payloads into `.codex/skills`.
