---
description: Show progress across all Conductor tracks and the active plan.
---

You are running `/conductor:status`.

1. If `conductor/` does not exist, tell the user to run `/conductor:setup` and stop.
2. Read `conductor/tracks.md` and list every track with its status (`[ ]` open / `[x]` done)
   and a link to its folder.
3. For each `in_progress` track, read its `plan.md` and summarize:
   - phases complete vs total (a phase is complete when its heading has `[checkpoint: <sha>]`),
   - tasks `[x]` / `[~]` / `[ ]` counts,
   - the next actionable `[ ]` task.
4. Present a compact overview and point to `/conductor:implement` for the active track or
   `/conductor:new-track` if none is open. Do not modify any files.
