# Conductor (Claude Code)

Context-Driven Development for Claude Code. Conductor keeps project context in versioned
Markdown under `conductor/` and drives work through spec-first **tracks**, phased **plans**,
**phase checkpoints**, and a **git-notes** audit trail.

## What you get

Installing this skill:

- Adds the slash commands under `.claude/commands/conductor/`:
  - `/conductor:setup` — bootstrap the `conductor/` workspace (greenfield or brownfield).
  - `/conductor:new-track` — open a track with a `spec.md` + phased `plan.md`.
  - `/conductor:implement` — execute the plan task-by-task per `conductor/workflow.md`.
  - `/conductor:status` — progress across all tracks.
  - `/conductor:review` — review work against the plan and product guidelines.
  - `/conductor:revert` — git-aware revert of a task/phase/track via git notes.
- Scaffolds the `conductor/` workspace (`product.md`, `product-guidelines.md`,
  `tech-stack.md`, `workflow.md`, `tracks.md`, `code_styleguides/`) — only where files are
  missing, so an existing workspace is preserved.

## Usage

1. Install via `/skill-manager:install workflow/conductor` (or `python install.py`).
2. Reload slash commands.
3. Run `/conductor:setup` once, then `/conductor:new-track` and `/conductor:implement`.

## Manual install / re-scaffold

```bash
python .claude/skills/conductor/post_install.py .
```

## Relationship to the Gemini Conductor extension

This is the Claude Code adaptation of the Gemini CLI **Conductor** extension. Same
Context → Spec & Plan → Implement lifecycle and the same `conductor/` file conventions,
re-expressed with Claude Code tools (`Skill`, `AskUserQuestion`, `Task`, git notes).
