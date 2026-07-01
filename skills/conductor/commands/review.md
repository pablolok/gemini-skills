---
description: Review current or completed work against the plan and product guidelines.
argument-hint: "[optional track id or phase name]"
---

You are running `/conductor:review`.

Scope hint (may be empty): $ARGUMENTS

1. Resolve scope: the named track/phase, else the active `in_progress` track from
   `conductor/tracks.md`.
2. Read that track's `spec.md` and `plan.md`, plus `conductor/product-guidelines.md` and the
   relevant `conductor/code_styleguides/`.
3. Determine the diff under review: `git diff --name-only <phase_start_sha> HEAD` (or the
   track's first commit if no prior checkpoint).
4. Review the changes for: alignment with the spec/acceptance criteria, adherence to product
   guidelines and code style, test coverage of changed code, and correctness/security smells.
   Apply the `subagent-balancer` policy if you delegate review to subagents, and prefer the
   matching `compliance-audit-*` skill for stack-specific rules.
5. Report findings as a prioritized list (most severe first) with `file:line` references and a
   concrete fix for each. Do not apply fixes unless the user asks — this command reports.
