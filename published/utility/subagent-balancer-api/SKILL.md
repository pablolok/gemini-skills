---
name: subagent-balancer-api
description: Use when Gemini work is billed through the Google AI Developer API or Vertex AI and you need price-aware model selection that minimizes spend while preserving enough quality for the task.
---

# Subagent Balancer API

Use this skill when Gemini usage is billed per token and the routing goal is cost efficiency rather than quota preservation.

Keep this separate from `subagent-balancer`:

- `subagent-balancer`: Gemini CLI and Google-account quota preservation.
- `subagent-balancer-api`: billed API usage where token price, batch discounts, and quality floors determine the best model.

## Goal

Choose the cheapest acceptable model for the work:

1. Keep the work local when delegation is unnecessary.
2. Use the lowest-cost model that still clears the quality floor for the task.
3. Prefer `batch` pricing for non-interactive or sidecar work when latency is not important.
4. Escalate to `pro` only when the task complexity or quality floor justifies the higher spend.

## Inputs

When available, use:

- The task type: review, search, implementation, verification, or refactor.
- The scope: small, medium, or large.
- The complexity: trivial, normal, hard, or ambiguous.
- The expected input and output token volume.
- Whether the work can use `batch` delivery.
- Whether preview models are allowed.
- Any hard model preference or model exclusions from the user.

## Deterministic Selection

Use the bundled selector:

```bash
python skills/subagent-balancer-api/scripts/select_model.py --task-type implementation --scope medium --complexity normal --budget-mode balanced
```

Useful flags:

- `--delivery-mode standard|batch`
- `--estimated-input-mtokens`
- `--estimated-output-mtokens`
- `--budget-mode min-cost|balanced|quality-first`
- `--preferred-model`
- `--avoid-model`
- `--no-preview`

Interpret the result as follows:

- `route=subagent`: use `selected_model`
- `route=local`: keep the work local or narrow scope
- `estimated_cost_usd`: expected model inference cost for the task estimate
- `ranked_candidates`: fallback order after applying the same cost-and-quality policy

## Routing Policy

Apply these rules in order:

1. If the work can be completed reliably in the current agent, do it locally.
2. If the task is trivial or narrow, prefer `flash-lite` or equivalent cost-efficient models.
3. For normal implementation or refactor work, `flash` should usually be the default delegated tier.
4. For hard or ambiguous work, raise the quality floor and allow `pro` to win when the extra spend is justified.
5. If `batch` is acceptable, prefer it because it typically halves input and output model cost.
6. If the user sets a hard model preference, preserve it exactly or return `local`.
7. If preview models are disallowed, do not select them even if they are cheaper or stronger.

## Cost Guidance

- `min-cost`:
  Minimize spend aggressively. Use the cheapest model that still meets the lowered quality floor.
- `balanced`:
  Default. Minimize spend while keeping a stronger quality floor for coding and reasoning work.
- `quality-first`:
  Raise the quality floor and allow more expensive models when they materially reduce failure risk.

## Pricing Data

The selector script contains a built-in model catalog based on the official Google Gemini API pricing page and supports both `standard` and `batch` delivery modes.

Because pricing changes over time, refresh the catalog whenever the official pricing changes. Do not assume the catalog is permanently current.

## Output Contract

When you apply this skill, produce a short decision before delegating:

- `Route:` local or subagent
- `Reason:` one sentence tied to cost and task quality needs
- `Model:` selected model name
- `Estimated cost:` expected model cost for the estimated token volume
- `Scope:` exact files or bounded objective

Example:

```text
Route: subagent
Reason: gemini-2.5-flash meets the quality floor for normal implementation work at much lower cost than gemini-2.5-pro.
Model: gemini-2.5-flash
Estimated cost: $0.06
Scope: targeted implementation for the changed Python files only.
```
