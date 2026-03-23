# Subagent Balancer Orchestrator

A thin router for Gemini delegation policy selection.

## What It Adds

- One entry point for choosing the correct balancer.
- Automatic routing between Gemini CLI quota preservation and billed Gemini API cost preservation.
- A safe local fallback when the execution environment is unclear.

## Main Files

- `SKILL.md`: Orchestration policy and routing rules.
- `scripts/select_balancer.py`: Detects whether the task should use the CLI or API balancer.

## Typical Usage

```bash
python skills/subagent-balancer-orchestrator/scripts/select_balancer.py --mode auto --context "Vertex AI batch processing with token pricing"
```
