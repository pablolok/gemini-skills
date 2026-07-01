# Subagent Balancer API

A Claude / Anthropic API model balancer for billed usage.

## What It Adds

- Deterministic cost-aware model selection for Anthropic API (Claude API) workflows.
- Quality-floor routing so the cheapest acceptable model wins instead of the strongest model by default.
- Support for `standard` and `batch` pricing modes.
- Explicit cost estimates from expected token volume.
- Live pricing refresh from the official Anthropic/Claude pricing page into a local catalog file.

## Main Files

- `SKILL.md`: API-specific routing policy and usage rules.
- `scripts/select_model.py`: Selects the cheapest acceptable Claude API model for a task.
- `scripts/refresh_pricing.py`: Refreshes `pricing_catalog.json` from the official Anthropic/Claude pricing page.

## Codex Integration

- In Codex-facing flows, prefer `subagent-balancer-orchestrator` as the entry point when the task may be either CLI/account or billed API usage.
- Use this API balancer directly only when the environment is already explicit: Anthropic API, Claude API, API keys, billed token pricing, or `batch` delivery.
- Audit and review skills should consume the orchestrator or this balancer's routing result instead of embedding API cost policy directly.

## Typical Usage

```bash
python skills/subagent-balancer-api/scripts/select_model.py --task-type implementation --scope medium --complexity normal --budget-mode balanced
```

With explicit token estimates and batch pricing:

```bash
python skills/subagent-balancer-api/scripts/select_model.py --task-type refactor --scope large --complexity hard --delivery-mode batch --estimated-input-mtokens 0.35 --estimated-output-mtokens 0.12
```

Refresh the local pricing catalog:

```bash
python skills/subagent-balancer-api/scripts/refresh_pricing.py
```

## Pricing Source

The local pricing catalog reflects the official Anthropic/Claude API pricing page (https://platform.claude.com/docs/en/pricing) as of `2026-03-18 UTC`. Refresh the catalog when Anthropic updates pricing.
