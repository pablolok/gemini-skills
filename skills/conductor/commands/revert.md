---
description: Git-aware revert of a Conductor task, phase, or track using the git-notes audit trail.
argument-hint: "<task | phase | track> <name-or-id>"
---

You are running `/conductor:revert` — undo a logical unit of work, not a raw SHA.

Request: $ARGUMENTS

## Steps

1. **Parse the request** into a level (`task`, `phase`, or `track`) and a target name/id. If
   ambiguous, ask with `AskUserQuestion`.

2. **Resolve the commits.** Use the plan and the git-notes audit trail to map the logical unit
   to real commits:
   - Read the track's `plan.md`; completed tasks carry a 7-char SHA and phases carry
     `[checkpoint: <sha>]`.
   - Inspect notes with `git log --notes --oneline` to confirm which commits belong to the unit.

3. **Show the plan before touching history.** List exactly which commits will be reverted and
   how, then get explicit confirmation via `AskUserQuestion`. Never rewrite history silently.

4. **Revert safely.** Prefer `git revert` (new commits that undo the change) over history
   rewriting unless the user explicitly wants the commits removed. Handle conflicts by pausing
   and asking.

5. **Resync Conductor state.** Update `plan.md` (flip `[x]`→`[ ]` for reverted tasks, strip the
   stale `[checkpoint: <sha>]`) and `tracks.md` if a whole track was reverted. Attach a git note
   documenting the revert.

6. **Commit** the state resync with `conductor(revert): <what was reverted and why>` and report
   the result.
