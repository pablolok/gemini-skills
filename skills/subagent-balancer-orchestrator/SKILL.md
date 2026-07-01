---
name: subagent-balancer-orchestrator
description: Use when work may delegate Claude subagents and you first need to choose the correct balancing policy between Claude Code quota preservation and billed Anthropic API cost preservation.
---

# Subagent Balancer Orchestrator

Use this skill as the single entry point before any Claude subagent delegation when the environment might be either:

- Claude Code or Claude subscription with quota limits
- Anthropic API (Claude API) with billed token pricing

## Goal

Choose the correct balancing skill once, then delegate policy decisions to that skill:

1. Detect whether the environment is quota-driven or price-driven.
2. Route to `subagent-balancer` for Claude Code and Claude subscription usage.
3. Route to `subagent-balancer-api` for billed Anthropic API usage.
4. If the environment is unclear, keep the work local or ask the user before delegating.

## Deterministic Routing

Use the bundled router script when context needs to be inferred:

```bash
python skills/subagent-balancer-orchestrator/scripts/select_balancer.py --mode auto --context "Claude Code /stats model quota is almost exhausted"
```

Interpret the result as follows:

- `selected_balancer=subagent-balancer`: use the CLI quota balancer
- `selected_balancer=subagent-balancer-api`: use the API cost balancer
- `route=local`: environment is unclear, so avoid delegating until clarified

## Routing Rules

Use `subagent-balancer` when the context mentions:

- Claude Code
- `/stats model`
- model usage bars or usage resets
- Claude subscription or free-tier Claude usage
- quota preservation as the main objective

Use `subagent-balancer-api` when the context mentions:

- Anthropic API or Claude API
- an Anthropic account with billed token pricing
- Amazon Bedrock or Google Vertex AI
- API keys such as `ANTHROPIC_API_KEY`
- billed token pricing
- `batch` delivery
- spend, price, or cost-per-token as the main objective

If the environment is still ambiguous after checking the task context:

- keep the review local, or
- ask the user which environment they are using before delegating

## Integration Guidance

Other skills should prefer this orchestrator over hardcoding a specific balancer.

Only call `subagent-balancer` or `subagent-balancer-api` directly when the environment is already explicit.
