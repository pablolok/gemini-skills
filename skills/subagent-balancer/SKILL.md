---
name: subagent-balancer
description: Use when Gemini CLI or a Google-account Gemini workflow may spawn subagents and you need quota-aware routing, model selection, or fallback-to-local execution to avoid exhausting usage limits.
---

# Subagent Balancing

Use this skill before any Gemini CLI or Google-account Gemini subagent delegation when quota, reset windows, or model scarcity matter.

If the user can provide a current Gemini quota table, use the bundled selector script to make the routing decision deterministic.

## Goal

Choose the cheapest safe execution path:

1. Do the work locally when delegation is unnecessary.
2. Delegate only when delegation meaningfully reduces risk or context pressure.
3. When delegating, prefer `lite` for narrow checks, `flash` for most coding tasks, and reserve `pro` for genuinely hard work.
4. Refuse recursive or excessive delegation when quota is constrained.

## Inputs

When available, use:

- The user's current quota snapshot.
- The user's explicit model selection or refusal to use specific models.
- The reset time for the affected models.
- Whether the task blocks the next step.
- The task type: review, search, implementation, verification, or refactor.
- The expected scope: small, medium, or large.
- The expected complexity: trivial, normal, hard, or ambiguous.

If quota data is missing, assume a constrained budget and bias toward local execution.

## Deterministic Selection

When a quota snapshot is available, run:

```bash
python skills/subagent-balancer/scripts/select_model.py --task-type review --scope small --complexity trivial < quota.txt
```

Use `--preferred-model`, `--avoid-model`, and `--no-preview` when the user has explicit constraints.

Interpret the result as follows:

- `route=subagent`: use `selected_model`
- `route=local`: do not delegate without asking the user or narrowing scope
- `ranked_candidates`: fallback order if the selected model becomes unavailable

## Wrapper

For automatic balancing, prefer the wrapper script:

```bash
python skills/subagent-balancer/scripts/balance_subagent.py --task-type review --scope small --complexity trivial --no-preview --explain
```

Behavior:

- First tries a live stats command. Default: `gemini -p "/stats model" --output-format text`
- If live capture fails, falls back to `.quota-cache.txt`
- If neither source is available, returns `route=local`

You can override the capture command with `GEMINI_STATS_COMMAND` or `--stats-command`.

## Routing Policy

Apply these rules in order:

1. If the task can be completed reliably in the current agent with normal tools and low context usage, do not spawn a subagent.
2. If the user explicitly selected a model family or tier, treat that preference as binding. Do not silently substitute a different tier such as `flash` for `pro`.
3. If the requested model is unavailable, near limit, or would force an unwanted preview fallback, choose one of these options instead of downgrading silently:
   - Keep the work local.
   - Narrow the task scope.
   - Ask the user whether a cheaper model is acceptable.
4. If the task is a sidecar task and does not block the next local step, delegation is allowed.
5. If the task is small or mechanical, use the lightest acceptable model tier or keep it local.
6. If the task is a review or audit, prefer a single subagent pass. Do not chain multiple review agents unless the user explicitly asks for parallel review.
7. If usage for the preferred Gemini model is close to limit, choose one of these fallbacks:
   - Keep the work local.
   - Use a cheaper Gemini subagent if quality is still acceptable.
   - Reduce the task scope to a targeted file set.
   - Skip delegation entirely and perform a manual checklist review.
8. If the quota is exhausted or the reset window is too far away for the task, do not spawn a Gemini subagent.
9. Never delegate a task whose result must be immediately consumed unless the quality gain clearly outweighs the quota cost.
10. Never let a delegated subagent spawn further subagents unless the user explicitly requested a multi-agent workflow.
11. Audits and bounded checks may intentionally stay on the main agent when the work is deterministic or quota pressure makes delegation wasteful.
12. Treat `complexity` as the main quality override: `flash` remains the default delegated tier for normal work, while `pro` is justified mainly for hard or ambiguous tasks.

## Secondary Agent Routing

Agent-role routing is secondary to model and quota routing.

Use it only after you have already decided that delegation is justified.

- `generalist`:
  Use for broad implementation, refactoring, or mixed read/write work.
- `codebase_investigator`:
  Use for read-heavy exploration, architecture mapping, and root-cause analysis.
- Specialized skills or tools:
  Use when the task clearly belongs to a narrower workflow and can be handled with less context than a broad subagent.

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

- `lite`:
  Use for narrow review, file triage, grep-style exploration, metadata extraction, or checklist validation. This is the most quota-efficient tier.
- `flash`:
  The default choice for most delegated development tasks. Prefer this over `pro` when it can do the job reliably because it preserves scarcer `pro` quota.
- `pro`:
  Use only for complex architecture review, ambiguous debugging, or broad code synthesis where `flash` is likely to fail.
- No subagent:
  Use for deterministic edits, small fixes, straightforward audits, and any task that can be completed from local context.

## Quota Awareness Checklist

Before delegating, ask:
1. **Can I do this locally?** (e.g., by reading files or running direct shell commands yourself)
2. **Is the scope minimal?** (Only send the specific files needed, not the whole project)
3. **Is the tier appropriate?** (Do not use Pro for work Lite or Flash can handle)
4. **Is the complexity real?** (`pro` should be justified by hard or ambiguous work, not by routine implementation alone)
5. **Am I chaining agents?** (Avoid having a subagent call another subagent)
6. **Is the result cacheable?** (If the task was just done, reuse the previous output)

## Prompt Caching Advice

To maximize efficiency and take advantage of potential prompt caching:
- **Group related files**: If you need to analyze 5 related files, do it in one subagent call rather than 5 separate ones.
- **Stable Context**: Keep the order of files and the system instructions consistent across calls when possible.
- **Surgical Context**: Use `read_file` with `start_line` and `end_line` even when preparing subagent inputs to keep the prompt size down.

## Output Contract

When you apply this skill, produce a short decision before delegating:

- `Route:` local or subagent
- `Reason:` one sentence tied to quota and task risk
- `Model:` selected model name or tier when available
- `Scope:` exact files or bounded objective

Example:

```text
Route: local
Reason: The user selected Gemini Pro and the available fallback would downgrade to Flash Preview, so this audit should stay local.
Model: none
Scope: Modified Python files and associated tests only.
```

## Integration Guidance

When another skill normally says "MUST invoke a subagent", reinterpret that as:

"You MUST apply the subagent-balancer policy first, then delegate only if the policy justifies it."

If this skill is unavailable in the target environment, inline the same policy rather than defaulting to unconditional delegation.

This skill does not have privileged live access to Gemini quota by itself. The wrapper improves this by trying a shell-level stats capture first, but that still depends on the local Gemini CLI exposing `/stats model` in a scriptable way.
