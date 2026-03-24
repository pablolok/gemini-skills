# Subagent Balancer

This is the Gemini CLI / Google-account quota balancer.

If the execution environment is not already known, pair it with `subagent-balancer-orchestrator` instead of hardcoding this skill directly.

A utility skill for Gemini CLI and Google-account Gemini workflows that makes subagent routing quota-aware and model-aware.

## What It Adds

- Deterministic model selection from a Gemini quota snapshot.
- A wrapper that tries to capture `/stats model`, falls back to a cached snapshot, and chooses a safe route.
- Guardrails to avoid silently burning expensive Pro or preview quota when a cheaper or local route is more appropriate.
- Reset-aware scoring so near-limit models with distant reset windows are penalized.
- Explicit complexity-aware routing so `flash` remains the default delegated tier and `pro` is reserved for hard or ambiguous work.
- Secondary agent-role guidance only after model and quota routing are already decided.

## Main Files

- `SKILL.md`: Routing policy and usage rules.
- `scripts/select_model.py`: Scores and ranks known Gemini models from a quota table, using task type, scope, complexity, quota usage, reset timing, and per-model scarcity to keep `flash` as the normal delegated tier and `pro` as an escalation tier.
  It now also preserves decimal usage percentages from `/stats model` and allows `lite` to win only for tightly bounded trivial implementation work under heavier `flash` pressure.
- `scripts/balance_subagent.py`: Wrapper that tries live stats capture, then cache fallback, then local fallback.

## Codex Integration

- In Codex-facing flows, prefer `subagent-balancer-orchestrator` as the entry point when the environment is not already explicit.
- Use this CLI balancer directly only when the task is clearly running through Gemini CLI or Google-account Gemini usage and quota preservation is the main objective.
- Audit and review skills should consume the orchestrator or this balancer's routing result, not re-implement quota policy themselves.

## Typical Usage

```bash
python skills/subagent-balancer/scripts/balance_subagent.py --task-type review --scope small --complexity trivial --no-preview --explain
```

With a saved snapshot:

```bash
python skills/subagent-balancer/scripts/select_model.py --task-type implementation --scope large --complexity hard < quota.txt
```
