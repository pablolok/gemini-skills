---
name: skill-publisher
description: Publish stable Gemini skills from source to `published/`, then verify any Codex bridge wrappers still describe the bridged Gemini skill accurately for Codex users.
---

# Skill Publisher Bridge

Use the installed Gemini skill at `.gemini/skills/skill-publisher/SKILL.md` as the source of truth.

Workflow:

1. Read and follow `.gemini/skills/skill-publisher/SKILL.md`.
2. If that skill references scripts, metadata, or companion files, resolve them from `.gemini/skills/skill-publisher/`.
3. Do not treat this bridge folder as the implementation source. It exists only so Codex can discover the skill without copying the Gemini payload.

## Codex Integration

When publishing or syncing a skill from Codex:

1. Publish from the development source to the stable destination exactly as the Gemini skill defines.
2. Use the Codex bridge for `changelog-manager` first when a `CHANGELOG.md` needs a new entry or format cleanup.
3. Ensure `README.md` is updated alongside `SKILL.md`, scripts, metadata, and changelog changes.
4. If the skill also has a Codex bridge in `.codex/skills/`, verify the bridge still points to the correct installed Gemini skill path and that its Codex-specific notes remain accurate.
5. After publishing a skill that affects post-change verification, run the Codex sequence: compliance audit first, then review optimization.

Do not publish Gemini-only Codex bridges by default. If a skill is Gemini-specific, such as the balancer family, keep it in `.gemini/skills/` and document that Codex should ignore it unless a real Codex integration is being added.
