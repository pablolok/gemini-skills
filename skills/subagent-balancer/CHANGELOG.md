# Changelog

## [1.4.4] - 2026-03-23
- Harden quota-aware routing with reset-aware scoring and a unified local-or-subagent contract


## [1.4.3] - 2026-03-23
- Standardized the balancer contract on `route=local|subagent` across the source skill docs and scripts.
- Tightened selector scoring to preserve quota more aggressively, making `flash` the normal delegated tier and keeping `pro` as an escalation tier.
- Added reset-aware scoring and clearer model-selection explanations while keeping parsing resilient to unknown reset formats.

## [1.4.2] - 2026-03-23
- Re-centered the skill on model and quota balancing, with agent-role routing as a secondary decision only.
- Restored support for current Gemini 2.5 and 3.x model names while keeping heuristic fallback for unknown models.
- Simplified quota parsing back to a line-based parser and fixed the no-candidates error path in the selector.

## [1.4.1] - 2026-03-23
- Verify automated publishing script.


## [1.4.0] - 2026-03-23
-   Added explicit model selection guidance (codebase_investigator vs generalist).
-   Enhanced routing policy with stricter context/token awareness rules.
-   Added support for modern Gemini models (1.5, 2.0) and refined scoring.
-   Added Quota Awareness Checklist and Prompt Caching Advice to SKILL.md.

## [1.3.0] - 2026-03-23
-   Added deterministic model selection from Gemini quota snapshots.
-   Added a wrapper script that tries live `/stats model` capture with cache fallback.
-   Added explicit model-preference guardrails to avoid silent downgrade to preview or cheaper tiers.
-   Added README documentation for publishing consistency.

## [1.0.1] - 2026-03-22
-   Initial changelog creation and version bump for testing.
