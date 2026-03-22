---
name: subagent-balancer
description: Use when a task may spawn Gemini subagents and you need quota-aware routing, model selection, or fallback-to-local execution to avoid exhausting usage limits.
---

# Subagent Balancing

Use this skill before any subagent delegation when quota, reset windows, or model scarcity matter.

## Goal

Choose the cheapest safe execution path:

1. Do the work locally when delegation is unnecessary.
2. Delegate to a lighter subagent when the task is bounded and parallelizable.
3. Reserve stronger subagents for ambiguous, high-risk, or critical-path work.
4. Refuse recursive or excessive delegation when quota is constrained.

## Inputs

When available, use:

- The user's current quota snapshot.
- The reset time for the affected models.
- Whether the task blocks the next step.
- The task type: review, search, implementation, verification, or refactor.
- The expected scope: small, medium, or large.

If quota data is missing, assume a constrained budget and bias toward local execution.

## Routing Policy

Apply these rules in order:

1. If the task can be completed reliably in the current agent with normal tools, do not spawn a subagent.
2. If the task is a sidecar task and does not block the next local step, delegation is allowed.
3. If the task is small or mechanical, use the lightest available subagent or keep it local.
4. If the task is a review or audit, prefer a single subagent pass. Do not chain multiple review agents unless the user explicitly asks for parallel review.
5. If usage for the preferred Gemini model is close to limit, choose one of these fallbacks:
   - Keep the work local.
   - Use a cheaper Gemini subagent if quality is still acceptable.
   - Reduce the task scope to a targeted file set.
   - Skip delegation entirely and perform a manual checklist review.
6. If the quota is exhausted or the reset window is too far away for the task, do not spawn a Gemini subagent.
7. Never delegate a task whose result must be immediately consumed unless the quality gain clearly outweighs the quota cost.
8. Never let a delegated subagent spawn further subagents unless the user explicitly requested a multi-agent workflow.

## Suggested Model Heuristics

- `flash` or equivalent lightweight agent:
  Use for narrow review, file triage, grep-style exploration, metadata extraction, or checklist validation.
- `pro` or equivalent stronger agent:
  Use only for complex architecture review, ambiguous debugging, or broad code synthesis where a weaker agent is likely to fail.
- No subagent:
  Use for deterministic edits, small fixes, straightforward audits, and any task that can be completed from local context.

## Output Contract

When you apply this skill, produce a short decision before delegating:

- `Route:` local, light-subagent, or strong-subagent
- `Reason:` one sentence tied to quota and task risk
- `Scope:` exact files or bounded objective

Example:

```text
Route: local
Reason: The remaining Gemini quota is constrained and this audit can be completed with a targeted manual review.
Scope: Modified Python files and associated tests only.
```

## Integration Guidance

When another skill normally says "MUST invoke a subagent", reinterpret that as:

"You MUST apply the subagent-balancer policy first, then delegate only if the policy justifies it."

If this skill is unavailable in the target environment, inline the same policy rather than defaulting to unconditional delegation.
