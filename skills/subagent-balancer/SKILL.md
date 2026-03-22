---
name: subagent-balancer
description: Use when a task may spawn Gemini subagents and you need quota-aware routing, model selection, or fallback-to-local execution to avoid exhausting usage limits.
---

# Subagent Balancing

Use this skill before any subagent delegation when quota, reset windows, or model scarcity matter.

If the user can provide a current Gemini quota table, use the bundled selector script to make the routing decision deterministic.

## Goal

Choose the cheapest safe execution path:

1. Do the work locally when delegation is unnecessary.
2. Delegate to a lighter subagent when the task is bounded and parallelizable.
3. Reserve stronger subagents for ambiguous, high-risk, or critical-path work.
4. Refuse recursive or excessive delegation when quota is constrained.

## Inputs

When available, use:

- The user's current quota snapshot.
- The user's explicit model selection or refusal to use specific models.
- The reset time for the affected models.
- Whether the task blocks the next step.
- The task type: review, search, implementation, verification, or refactor.
- The expected scope: small, medium, or large.

If quota data is missing, assume a constrained budget and bias toward local execution.

## Deterministic Selection

When a quota snapshot is available, run:

```bash
python skills/subagent-balancer/scripts/select_model.py --task-type review --scope small < quota.txt
```

Use `--preferred-model`, `--avoid-model`, and `--no-preview` when the user has explicit constraints.

Interpret the result as follows:

- `route=subagent`: use `selected_model`
- `route=local`: do not delegate without asking the user or narrowing scope
- `ranked_candidates`: fallback order if the selected model becomes unavailable

## Wrapper

For automatic balancing, prefer the wrapper script:

```bash
python skills/subagent-balancer/scripts/balance_subagent.py --task-type review --scope small --no-preview --explain
```

Behavior:

- First tries a live stats command. Default: `gemini -p "/stats model" --output-format text`
- If live capture fails, falls back to `.quota-cache.txt`
- If neither source is available, returns `route=local`

You can override the capture command with `GEMINI_STATS_COMMAND` or `--stats-command`.

## Routing Policy

Apply these rules in order:

1. **Context & Token Awareness**:
   - If the task requires analyzing a large portion of the codebase (>10 files) or the current session context is already large, you MUST delegate to a fresh subagent to preserve the main session's context window.
   - If the estimated input tokens for the task approach 50% of the current model's limit, delegate immediately.

2. If the task can be completed reliably in the current agent with normal tools and low context usage, do not spawn a subagent.
3. If the user explicitly selected a model family or tier, treat that preference as binding. Do not silently substitute a different tier such as `flash` for `pro`.
4. If the requested model is unavailable, near limit, or would force an unwanted preview fallback, choose one of these options instead of downgrading silently:
   - Keep the work local.
   - Narrow the task scope.
   - Ask the user whether a cheaper model is acceptable.
5. If the task is a sidecar task and does not block the next local step, delegation is allowed.
6. If the task is small or mechanical, use the lightest acceptable subagent or keep it local.
7. If the task is a review or audit, prefer a single subagent pass. Do not chain multiple review agents unless the user explicitly asks for parallel review.
8. If usage for the preferred Gemini model is close to limit, choose one of these fallbacks:
   - Keep the work local.
   - Use a cheaper Gemini subagent if quality is still acceptable.
   - Reduce the task scope to a targeted file set.
   - Skip delegation entirely and perform a manual checklist review.
9. If the quota is exhausted or the reset window is too far away for the task, do not spawn a Gemini subagent.
10. Never delegate a task whose result must be immediately consumed unless the quality gain clearly outweighs the quota cost.
11. Never let a delegated subagent spawn further subagents unless the user explicitly requested a multi-agent workflow.

## Subagent Selection

When delegation is justified, choose the most efficient subagent:

- **codebase_investigator**:
  - Use for: Vague requests ("why is this broken?"), architectural mapping, root cause analysis, or broad system understanding.
  - Best for: "Read-heavy" research tasks that require traversing many files.
- **generalist**:
  - Use for: Batch refactoring, fixing errors across multiple files, high-volume command output, or multi-step implementation tasks.
  - Best for: "Write-heavy" or "Turn-heavy" tasks where keeping the main history clean is a priority.
- **Specialized Skills**:
  - Use for: Tasks strictly within a domain (e.g., `chrome-devtools` for browser debugging, `gws-*` for Google Workspace).
  - Best for: Targeted tasks with minimal context overhead.

## Model Preference Guardrail

If the user says any of the following, preserve it exactly:

- "Use Pro"
- "Do not use Flash"
- "Do not use preview models"
- "Use this selected model only"

In those cases, the valid routes are:

- Use the requested model.
- Keep the work local.
- Ask for permission to change models.

An automatic downgrade to `gemini-3-flash-preview` is not allowed.

## Suggested Model Heuristics

- `lite` (e.g., flash-8b):
  Use for narrow review, file triage, grep-style exploration, metadata extraction, or checklist validation. Extremely quota-efficient.
- `flash` (e.g., gemini-1.5-flash, gemini-2.0-flash):
  The default choice for most development tasks. Good balance of speed and reasoning.
- `pro` (e.g., gemini-1.5-pro):
  Use only for complex architecture review, ambiguous debugging, or broad code synthesis where a weaker agent is likely to fail. Expensive on quota.
- No subagent:
  Use for deterministic edits, small fixes, straightforward audits, and any task that can be completed from local context.

## Quota Awareness Checklist

Before delegating, ask:
1. **Can I do this locally?** (e.g., using `grep_search` or `read_file` yourself).
2. **Is the scope minimal?** (Only send the specific files needed, not the whole project).
3. **Is the tier appropriate?** (Don't use Pro for a task Flash can handle).
4. **Am I chaining agents?** (Avoid having a subagent call another subagent).
5. **Is the result cacheable?** (If the task was just done, reuse the previous output).

## Prompt Caching Advice

To maximize efficiency and take advantage of potential prompt caching:
- **Group related files**: If you need to analyze 5 related files, do it in one subagent call rather than 5 separate ones.
- **Stable Context**: Keep the order of files and the system instructions consistent across calls when possible.
- **Surgical Context**: Use `read_file` with `start_line` and `end_line` even when preparing subagent inputs to keep the prompt size down.

## Output Contract

When you apply this skill, produce a short decision before delegating:

- `Route:` local, light-subagent, or strong-subagent
- `Reason:` one sentence tied to quota and task risk
- `Scope:` exact files or bounded objective

Example:

```text
Route: local
Reason: The user selected Gemini Pro and the available fallback would downgrade to Flash Preview, so this audit should stay local.
Scope: Modified Python files and associated tests only.
```

## Integration Guidance

When another skill normally says "MUST invoke a subagent", reinterpret that as:

"You MUST apply the subagent-balancer policy first, then delegate only if the policy justifies it."

If this skill is unavailable in the target environment, inline the same policy rather than defaulting to unconditional delegation.

This skill does not have privileged live access to Gemini quota by itself. The wrapper improves this by trying a shell-level stats capture first, but that still depends on the local Gemini CLI exposing `/stats model` in a scriptable way.
