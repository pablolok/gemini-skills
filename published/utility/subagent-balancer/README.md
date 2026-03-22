# Subagent Balancer

A utility skill for Gemini that makes subagent routing quota-aware and model-aware.

## What It Adds

- Deterministic model selection from a Gemini quota snapshot.
- A wrapper that tries to capture `/stats model`, falls back to a cached snapshot, and chooses a safe route.
- Guardrails to avoid silently burning expensive Pro or preview quota when a cheaper or local route is more appropriate.

## Main Files

- `SKILL.md`: Routing policy and usage rules.
- `scripts/select_model.py`: Scores and ranks known Gemini models from a quota table.
- `scripts/balance_subagent.py`: Wrapper that tries live stats capture, then cache fallback, then local fallback.

## Typical Usage

```bash
python .gemini/skills/subagent-balancer/scripts/balance_subagent.py --task-type review --scope small --no-preview --explain
```

With a saved snapshot:

```bash
python .gemini/skills/subagent-balancer/scripts/select_model.py --task-type implementation --scope large < quota.txt
```
