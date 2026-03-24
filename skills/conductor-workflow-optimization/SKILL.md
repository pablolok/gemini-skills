---
name: conductor-workflow-optimization
description: Detect and remediate Gemini Conductor workflow drift caused by stale tool names, invalid plan-mode transitions, unexpected tool calls, and CLI/workflow mismatches. Use when Gemini emits "unexpected tool call", references a missing tool such as `exit_plan_mode`, or when `conductor/workflow.md`, custom commands, or installed skills may be out of sync with the current CLI behavior.
---

# Conductor Workflow Optimization

Use this skill to repair workflow-level failures, not feature code.

## Installation Model

This skill supports two integration paths:

1. Installer-driven integration.
   - When installed through `install.py` or `/skill-manager:install`, the installer executes this skill's `post_install.py` hook after copying files.
   - The hook attempts to update `conductor/workflow.md` automatically.
2. Manual or conversational integration.
   - If the skill was copied manually, or the hook could not patch the workflow safely, update `conductor/workflow.md` yourself or ask Gemini to do it using this skill's rules.
   - You may also run `python .gemini/skills/conductor-workflow-optimization/post_install.py .` manually from the project root.

## Core Workflow

1. Reproduce or capture the exact workflow failure.
   - Preserve the exact missing tool name, command, or error text.
   - Prefer absolute examples such as `exit_plan_mode` over paraphrases like "plan mode broke".
2. Scan the project for stale workflow references before editing.
   - Run `python .gemini/skills/conductor-workflow-optimization/scripts/workflow_guard.py --root .`
   - If the failure names a specific missing tool, run `python .gemini/skills/conductor-workflow-optimization/scripts/workflow_guard.py --root . --forbid <tool-name>`
3. Verify live CLI behavior before patching prompts or policies.
   - Consult Gemini CLI help and command output in the current environment.
   - Treat the live CLI as the source of truth when it conflicts with workflow text.
4. Patch the workflow layer that introduced the bad reference.
   - Check `conductor/workflow.md`.
   - Check installed skill `SKILL.md`, `README.md`, hooks, and generated commands.
   - Check any policy or command files that preserve plan-mode behavior.
5. Make the fix durable.
   - Replace invalid tool calls with the valid current workflow actions.
   - Add or tighten guardrails so the same stale reference is caught earlier next time.

## What To Detect

- Forbidden or stale tool names such as `exit_plan_mode`.
- Workflow text that talks about leaving plan mode without naming the real current actions.
- "Unexpected tool call" failures that point to generated workflow prompts, installed skills, or post-install hooks.
- Divergence between `conductor/workflow.md` and the behavior described in skill docs or generated commands.
- Binary confirmation prompts that force a yes/no response instead of preserving a free-text feedback path.

## Guard Script

The bundled script is a first-pass detector. It is intentionally conservative and only flags workflow drift signals that are likely actionable.

Default checks:
- known forbidden tool names
- plan-mode sections that omit both `finish_plan` and `cancel_plan`
- binary confirmation prompts such as "type yes to confirm" that should be upgraded to `yes`, `no`, or free-text feedback

Useful invocations:

```bash
python .gemini/skills/conductor-workflow-optimization/scripts/workflow_guard.py --root .
python .gemini/skills/conductor-workflow-optimization/scripts/workflow_guard.py --root . --forbid exit_plan_mode
python .gemini/skills/conductor-workflow-optimization/scripts/workflow_guard.py --root . --json
```

## Repair Rules

- Never invent a replacement tool from memory when the CLI can be queried directly.
- Prefer fixing the narrowest artifact that caused the bad call, then propagate the correction to mirrored docs if needed.
- If the issue originated from a generated command or post-install hook, update the source skill and published copy so future installs inherit the fix.
- If the workflow text says to "exit" plan mode, rewrite it in terms of the valid current actions instead of adding a generic exit abstraction.
- Prefer tri-state confirmation prompts over binary ones. For user confirmation, default to `yes`, `no`, or free-text feedback instead of yes/no-only wording.
