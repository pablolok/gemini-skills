# Subagent Balancer API

A Gemini API and Vertex AI model balancer for billed usage.

## What It Adds

- Deterministic cost-aware model selection for Google AI Developer API and Vertex AI workflows.
- Quality-floor routing so the cheapest acceptable model wins instead of the strongest model by default.
- Support for `standard` and `batch` pricing modes.
- Explicit cost estimates from expected token volume.
- Live pricing refresh from the official Google Gemini pricing page into a local catalog file.

## Main Files

- `SKILL.md`: API-specific routing policy and usage rules.
- `scripts/select_model.py`: Selects the cheapest acceptable Gemini API model for a task.
- `scripts/refresh_pricing.py`: Refreshes `pricing_catalog.json` from the official Google Gemini pricing page.

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

The local pricing catalog reflects the official Google Gemini API pricing page as of `2026-03-18 UTC`. Refresh the catalog when Google updates pricing.
