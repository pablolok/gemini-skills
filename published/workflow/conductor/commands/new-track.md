---
description: Start a new Conductor track — generate its spec and phased plan, then register it.
argument-hint: "<short description of the feature or bug>"
---

You are running `/conductor:new-track` to open a new unit of work.

Track description from the user: $ARGUMENTS

## Preconditions

- `conductor/` must exist. If it does not, tell the user to run `/conductor:setup` first and stop.
- Read `conductor/product.md`, `conductor/tech-stack.md`, and `conductor/product-guidelines.md`
  for context before writing anything.

## Steps

1. **Clarify intent.** If the description is thin or ambiguous, ask focused questions with
   `AskUserQuestion` (scope, acceptance criteria, constraints, out-of-scope) before drafting.
   Prefer the `brainstorming` skill for anything design-heavy.

2. **Derive a track id.** Slugify the description to `snake_case` and append today's date as
   `YYYYMMDD`, e.g. `user_profile_page_20260701`. Create `conductor/tracks/<track_id>/`.

3. **Write `spec.md`.** Capture: problem statement, goals & non-goals, requirements,
   constraints, acceptance criteria, and any relevant existing code to reuse. Before finalizing,
   invoke the `pre-implementation-review` skill to surface reuse opportunities and the right
   abstraction boundary, and fold its findings into the spec.

4. **Write `plan.md`.** Break the work into **Phases**, each with ordered **Tasks** as
   checkboxes `[ ]`. Every phase ends with a placeholder `[checkpoint: ]`. Keep tasks small
   enough to be one focused commit each. Follow TDD: each implementation task implies a
   preceding failing-test task.

5. **Write `metadata.json`** with:
   ```json
   { "track_id": "<id>", "type": "feature|bug", "status": "in_progress", "description": "<one line>" }
   ```

6. **Register the track.** Add a row to `conductor/tracks.md` with status `[ ]` and a link to
   the track folder.

7. **Commit** the new track files with `conductor(track): Open track '<description>'`.

8. **Hand off.** Tell the user to run `/conductor:implement` to begin executing the plan.
