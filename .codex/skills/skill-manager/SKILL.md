---
name: skill-manager
description: Install, update, and manage Gemini skills in a project from Codex while preserving the split between real Gemini skills in `.gemini/skills` and lightweight Codex bridge wrappers in `.codex/skills`.
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

When installing or updating skills from Codex:

1. Install or update the real Gemini skill into `.gemini/skills/` first.
2. Ensure the matching Codex bridge exists in `.codex/skills/` and still points at the installed Gemini skill path.
3. Do not replace Gemini skills with Codex wrappers and do not copy full Gemini payloads into `.codex/skills`.
4. Treat Gemini-only routing skills, especially `subagent-balancer`, `subagent-balancer-api`, and `subagent-balancer-orchestrator`, as Gemini-layer skills. They should not be installed as Codex bridges unless you are intentionally building Codex support for them.

The bridge layer exists so Codex can discover and use installed Gemini skills with Codex-specific instructions, not to duplicate the Gemini implementation.
