---
name: changelog-manager
description: Codex bridge for the workspace-local Gemini changelog-manager skill. Use to normalize CHANGELOG.md files, keep version headings consistent, and update changelog entries before publishing or after manual edits.
---

# Changelog Manager Bridge

Use the installed Gemini skill at `.gemini/skills/changelog-manager/SKILL.md` as the source of truth.

Workflow:

1. Read and follow `.gemini/skills/changelog-manager/SKILL.md`.
2. Apply that canonical changelog format to the relevant `CHANGELOG.md`.
3. Do not treat this bridge folder as the implementation source. It exists only so Codex can discover the workspace-local Gemini skill.

## Codex Integration

Use this bridge:
- before publishing a skill
- after manual changelog edits created format drift
- when a version bump needs a clean new entry

For publisher workflows, run this before the final publish synchronization so changelog format is stable before copying to `published/`.
