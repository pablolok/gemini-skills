# Subagent Balancer Orchestrator

A thin router for Gemini delegation policy selection.

## What It Adds

- One entry point for choosing the correct balancer.
- Automatic routing between Gemini CLI quota preservation and billed Gemini API cost preservation.
- A safe local fallback when the execution environment is unclear.

## Main Files

- `SKILL.md`: Orchestration policy and routing rules.
- `scripts/select_balancer.py`: Detects whether the task should use the CLI or API balancer.

## Codex Integration

- This should be the default Codex entry point for any skill that may delegate Gemini work.
- Codex-side audit and review flows should call the orchestrator first, then follow its selected balancer rather than hardcoding CLI-vs-API logic.
- Only bypass the orchestrator when the environment is already explicit and there is no ambiguity about which balancer applies.

## Typical Usage

```bash
python skills/subagent-balancer-orchestrator/scripts/select_balancer.py --mode auto --context "Vertex AI batch processing with token pricing"
```
