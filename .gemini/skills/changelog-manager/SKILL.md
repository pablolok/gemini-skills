---
name: changelog-manager
description: Standardize and maintain skill changelogs in this workspace. Use when creating, updating, or normalizing CHANGELOG.md entries for Gemini or Codex skills, especially before publishing or after manual edits caused formatting drift.
---

# Changelog Manager

Use this workspace-local skill whenever a skill changelog needs to be created, updated, or normalized.

## Canonical Format

Use exactly this heading style for new entries:

```md
## [<version>] - YYYY-MM-DD
- Imperative summary line
- Another summary line
```

Rules:
- Use bracketed versions: `[1.2.3]`
- Use ISO dates: `YYYY-MM-DD`
- Use flat bullet lists with `-`
- Keep one blank line between version sections
- Put newest entries at the top, directly under `# Changelog`
- Do not mix alternative heading formats like `## 1.2.3 (2026-03-23)`

## Workflow

1. Read the existing `CHANGELOG.md`.
2. Detect formatting drift or mixed heading styles.
3. Normalize the entire file to the canonical format when practical.
4. Add or update the newest version entry with concise, high-signal bullets.
5. Keep the changelog aligned with `metadata.json`, `README.md`, and `SKILL.md`.

## Scope

Use this skill for:
- `skills/*/CHANGELOG.md`
- `published/*/*/CHANGELOG.md`
- workspace-local skill changelogs under `.gemini/skills/`
- Codex bridge changelog conventions when documented in README or SKILL files

Do not invent release history. If older entries are inconsistent, normalize their heading and bullet format without changing their meaning.
