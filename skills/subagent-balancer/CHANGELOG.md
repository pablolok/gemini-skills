# Changelog

## [1.6.3] - 2026-07-01
- Publish Claude Code migration (retarget from Gemini CLI distribution)


## [1.6.2] - 2026-03-24
- Refine haiku routing for bounded trivial implementation work and fix decimal percentage parsing.


## [1.6.1] - 2026-03-23
- Publish Codex integration notes and robust CLI balancing updates


## [1.6.0] - 2026-03-23
- Added more robust stats capture with multiple Claude Code CLI command candidates and JSON-like output normalization before cache fallback.
- Clarified that this CLI balancer should pair with `subagent-balancer-orchestrator` when the environment is not already explicit.

## [1.5.3] - 2026-03-23
- Clarify Claude Code quota balancing scope after splitting API billing into a separate skill


## [1.5.2] - 2026-03-23
- Clarified that `subagent-balancer` is the Claude Code and Claude subscription quota-preservation skill after splitting API billing concerns into a separate skill.

## [1.5.1] - 2026-03-23
- Add complexity-aware and scarcity-aware quota balancing for sonnet-first Claude Code routing


## [1.5.0] - 2026-03-23
- Added explicit complexity-aware routing so `sonnet` remains the default delegated tier and `opus` is reserved for hard or ambiguous work.
- Added model-family scarcity tuning to preserve scarcer `opus` quota and prefer cheaper models when quality is still acceptable.
- Reworked reset-window scoring to be more proportional and extended the selector and wrapper interfaces to accept `--complexity`.

## [1.4.4] - 2026-03-23
- Harden quota-aware routing with reset-aware scoring and a unified local-or-subagent contract


## [1.4.3] - 2026-03-23
- Standardized the balancer contract on `route=local|subagent` across the source skill docs and scripts.
- Tightened selector scoring to preserve quota more aggressively, making `sonnet` the normal delegated tier and keeping `opus` as an escalation tier.
- Added reset-aware scoring and clearer model-selection explanations while keeping parsing resilient to unknown reset formats.

## [1.4.2] - 2026-03-23
- Re-centered the skill on model and quota balancing, with agent-role routing as a secondary decision only.
- Restored support for current Claude model names while keeping heuristic fallback for unknown models.
- Simplified quota parsing back to a line-based parser and fixed the no-candidates error path in the selector.

## [1.4.1] - 2026-03-23
- Verify automated publishing script.


## [1.4.0] - 2026-03-23
- Added explicit model selection guidance (codebase_investigator vs generalist).
- Enhanced routing policy with stricter context/token awareness rules.
- Added support for modern Claude models and refined scoring.
- Added Quota Awareness Checklist and Prompt Caching Advice to SKILL.md.

## [1.3.0] - 2026-03-23
- Added deterministic model selection from Claude quota snapshots.
- Added a wrapper script that tries live `/stats model` capture with cache fallback.
- Added explicit model-preference guardrails to avoid silent downgrade to preview or cheaper tiers.
- Added README documentation for publishing consistency.

## [1.0.1] - 2026-03-22
- Initial changelog creation and version bump for testing.
