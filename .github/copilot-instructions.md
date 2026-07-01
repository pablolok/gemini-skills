# Copilot Instructions

## Commands

```bash
# Run all tests
python3 -m pytest tests/

# Run a single test file
python3 -m pytest tests/test_versioning.py

# Run a single test
python3 -m pytest tests/test_versioning.py::TestVersionComparator::test_is_newer

# Lint
pylint install.py versioning.py automate_publish.py check_updates.py manage.py uninstall.py
```

> pytest is not globally installed — always use `python3 -m pytest`.

---

## Architecture

This is a **Claude Code skill distribution and management system**. It has two primary concerns:

1. **Skill authoring** — Skills live in `skills/<name>/` and are the source of truth.
2. **Skill publishing** — The `published/` directory is a deployed snapshot. Never edit it directly; always publish from `skills/` via `automate_publish.py`.

### Key directories

| Path | Purpose |
|---|---|
| `skills/` | Authoritative skill sources (edit here) |
| `published/` | Published snapshots (`audit/`, `utility/`, `workflow/` sub-categories) |
| `tests/` | All Python tests |
| `schemas/` | JSON schema for `metadata.json` validation |
| `.claude/skills/` | Managed Claude skills installed into a target project by the installer (not repo-owned) |
| `.claude/commands/` | Managed Claude slash commands installed by the installer (e.g. `conductor/`, `skill-manager/`) |

### Skill structure

Every skill under `skills/<name>/` must contain:
- `SKILL.md` — Frontmatter (`name`, `description`) + AI-facing instructions
- `metadata.json` — `{ "name", "version", "description" }` (SemVer)
- `CHANGELOG.md` — Version history
- `README.md` — Human-facing documentation

### Installer layer

- `manage.py` — CLI launcher; routes to `install.py` or `uninstall.py`
- `install.py` — Core installer (`SkillInstaller`, `SkillSelector`); handles skill copying into `.claude/skills/`, legacy-layout migration (`.gemini`/`.agents`/`.codex` → `.claude`), `.gitignore` management, and `post_install.py` hooks
- `install.config.json` — Machine-readable skill catalog (schema v2); maps each skill to its `category` (`audit` | `utility` | `workflow`)
- `automate_publish.py` — Bumps version, updates changelog, copies `skills/` → `published/`
- `versioning.py` — `VersionComparator` for SemVer comparison

---

## Key Conventions

### Skill routing (mandatory)

| Task | Route through |
|---|---|
| Publish / sync to `published/` | `skill-publisher` skill |
| Install / update / migration | `skill-manager` skill |
| Changelog normalization | `changelog-manager` skill (before publishing) |

### Policy doc sync

`CLAUDE.md` and `AGENTS.md` are **policy mirrors** — they must always stay identical. When changing one, update the other in the same commit.

### Skill catalog

- Every skill installs the same way: a full copy into the target project's `.claude/skills/<name>/`.
- `install.config.json` (schema v2) is the source of truth for a skill's `category`
  (`audit` / `utility` / `workflow`), which determines its `published/<category>/` location.
- There is no per-tool distribution split anymore — this is a Claude-Code-only distribution.

### `.gitignore` guardrail

Never rewrite the full `.gitignore`. Only modify lines inside the managed block:
```
# >>> skill-manager managed workspace files >>>
...
# <<< skill-manager managed workspace files <<<
```
All content outside that block must be preserved exactly.

### Publishing flow

```bash
python automate_publish.py <skill-name> <category> "<summary>" --bump <patch|minor|major>
```

Then commit: `feat(published): sync skill '<skill-name>' to version <new-version>`

After publishing, verify that any related `.agents/skills/` and `.claude/skills/` entries still accurately describe the updated skill.

### Versioning

SemVer only. `versioning.py::VersionComparator` handles parsing and comparison. Versions like `v1.0.0` (with `v` prefix) are **invalid** — use `1.0.0`.
