---
name: conductor
description: Use to set up or run Context-Driven Development in a project with Claude Code. Installs the /conductor:setup, /conductor:new-track, /conductor:implement, /conductor:status, /conductor:review, and /conductor:revert slash commands and scaffolds the conductor/ workspace. Invoke when the user wants spec-first tracks, phase checkpoints, TDD enforcement, or a git-notes audit trail for their work.
---

# Conductor — Context-Driven Development for Claude Code

Conductor moves project context out of the ephemeral chat window and into persistent
Markdown files committed alongside the code, so the repository itself is the single source
of truth. Work flows through three stages: **Context → Spec & Plan → Implement**.

This is the Claude Code adaptation of the Conductor workflow. It ships as native slash
commands plus a scaffolded `conductor/` workspace, so a project is driven the same way you
would drive it with the Gemini CLI Conductor extension — but using Claude Code tools
(`Skill`, `AskUserQuestion`, `Task`, `Read`/`Write`/`Edit`, `Bash`, and git notes).

## Installation

When installed through `install.py` or `/skill-manager:install`, this skill's
`post_install.py` hook runs automatically and:

1. Copies the slash commands into the target project's `.claude/commands/conductor/`
   (so `/conductor:setup`, `/conductor:new-track`, etc. become available after
   `/` reloads commands).
2. Scaffolds the `conductor/` workspace from `templates/` **only if it does not already
   exist**, so an existing Conductor project is never overwritten.

You can also run the hook manually from the project root:

```bash
python .claude/skills/conductor/post_install.py .
```

## The Commands

| Command | Purpose |
| :--- | :--- |
| `/conductor:setup` | Run once. Bootstraps `conductor/` context (product, guidelines, tech-stack, workflow, tracks) for a greenfield or brownfield project. |
| `/conductor:new-track` | Start a feature or bug track: generate `spec.md` + `plan.md` and register it in `tracks.md`. |
| `/conductor:implement` | Execute the current track's plan task-by-task following `workflow.md` (TDD, commits, git notes, phase checkpoints). |
| `/conductor:status` | Show progress across all tracks from `tracks.md` and the active plan. |
| `/conductor:review` | Review work-in-progress or a completed phase against `product-guidelines.md` and the plan. |
| `/conductor:revert` | Git-aware revert of a task, phase, or track using the git-notes audit trail — logical units, not raw SHAs. |

## Core Concepts

- **Track** — a unit of work (feature or bug) living in `conductor/tracks/<id>/` with
  `spec.md` (requirements/constraints), `plan.md` (phased execution plan), and
  `metadata.json` (id, type, status, description).
- **Plan hierarchy** — Phases → Tasks. Task checkboxes: `[ ]` pending, `[~]` in progress,
  `[x]` done. The 7-char commit SHA is appended to each completed task.
- **Phase checkpoint** — each phase heading ends with `[checkpoint: <sha>]`. Phase
  boundaries trigger a verification protocol that **pauses for human confirmation** before
  the checkpoint commit.
- **Git notes** — task summaries and full verification reports are attached to commits with
  `git notes add -f`, giving an auditable trail tied to logical units. This is what powers
  `/conductor:revert`.

## The Workflow Is the Source of Truth

The full lifecycle protocol lives in `conductor/workflow.md` inside the target project. The
slash commands defer to it. When running `/conductor:implement`, always read and follow the
project's `conductor/workflow.md` — it defines the exact TDD, commit, checkpoint, and audit
steps for that repository.

## Companion Skills

Conductor integrates with the other skills in this collection at phase boundaries:

- `pre-implementation-review` — run before writing code for a task.
- `compliance-audit-orchestrator` — run after tests pass at a phase boundary.
- `review-optimization` — run after audits to refine the workflow.
- `conductor-workflow-optimization` — run when a workflow instruction drifts from current
  Claude Code tool behavior.
- `subagent-balancer` — apply when delegating review work to subagents.
