# Changelog

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
