---
description: Execute the active Conductor track's plan task-by-task, following the project workflow.
argument-hint: "[optional track id — defaults to the active in_progress track]"
---

You are running `/conductor:implement` to advance a track's plan.

Optional track id: $ARGUMENTS

## The Rule

`conductor/workflow.md` is the source of truth. **Read it now and follow it exactly.** The
steps below are a summary; the project's `workflow.md` wins wherever they differ.

## Select the track

1. If a track id was given, use it. Otherwise read `conductor/tracks.md` and pick the
   `in_progress` track. If several qualify, ask the user with `AskUserQuestion`.
2. Open that track's `plan.md`.

## Per-task loop (Standard Task Workflow)

For the next `[ ]` task in sequence:

1. Mark it `[~]` in `plan.md`.
2. Invoke the `pre-implementation-review` skill before writing code, and adjust the plan if it
   reveals a better reuse boundary.
3. **Red:** write failing test(s) that pin the acceptance criteria; run them and confirm they fail.
4. **Green:** write the minimum code to pass; run the suite and confirm green.
5. **Refactor** with tests as a safety net; keep them green.
6. Verify coverage against the project target.
7. If implementation deviates from `tech-stack.md`, stop, update `tech-stack.md` with a dated
   note, then resume.
8. Commit the change with a Conventional Commits message.
9. Attach a task summary as a git note:
   `git notes add -f -m "<summary: task, changes, files, why>" <commit_sha>`.
10. Mark the task `[x]` in `plan.md` and append the 7-char commit SHA.
11. Commit the plan update: `conductor(plan): Mark task '<task>' complete`.

## Phase boundary → verification protocol

When a completed task ends a phase, run the **Phase Completion Verification and Checkpointing
Protocol** from `workflow.md`:

1. Ensure tests exist for every code file changed in the phase
   (`git diff --name-only <prev_checkpoint_sha> HEAD`).
2. Run the automated test suite (announce the exact command first; use `CI=true` for watch-mode tools).
3. Apply the `subagent-balancer` policy, then invoke `compliance-audit-orchestrator`
   (verification-gates first, then specialized audits for the changed stack). Required build/
   compile/bundle gates must pass without warnings unless the repo documents an exception.
4. Invoke `review-optimization` to audit the phase's execution and refine the workflow. If a
   workflow instruction drifted from current tool behavior, invoke `conductor-workflow-optimization`.
5. Propose a concrete manual-verification plan and **pause** for the user's explicit `yes`
   (use `AskUserQuestion`). Address `no`/free-text feedback and repeat.
6. Create the checkpoint commit, attach the full verification report as a git note, append
   `[checkpoint: <sha>]` to the phase heading, and commit the plan update.

## Track finalization

When all phases are checkpointed, run the **Track Finalization and Cleanup Protocol** from
`workflow.md`: sync project docs, merge to the main branch, mark the track `[x]` in
`tracks.md`, and offer to archive or delete the track folder.
