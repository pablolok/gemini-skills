# Changelog

## [1.1.0] - 2026-03-23
- Added live pricing refresh from the official Google Gemini pricing page into `pricing_catalog.json`.
- Added selector support for `--pricing-file` and `--refresh-pricing`.
- Prepared the API balancer to be called through the new subagent balancer orchestrator.

## [1.0.1] - 2026-03-23
- Add a cost-aware Gemini API balancer focused on price-quality tradeoffs


## [1.0.0] - 2026-03-23
- Added a separate API-focused balancer skill for billed Gemini usage.
- Added deterministic model selection based on estimated token cost, quality floors, delivery mode, and preview policy.
- Split quota-preservation logic out of the API cost-balancing workflow.
