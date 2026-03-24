# Conductor Workflow Optimization

Detect and remediate Gemini Conductor workflow drift caused by stale tool names, invalid plan-mode transitions, and unexpected tool calls.

## What It Helps With

- invalid or removed tool references such as `exit_plan_mode`
- plan-mode instructions that no longer match Gemini CLI behavior
- drift between `conductor/workflow.md`, installed skills, and generated Gemini commands
- binary confirmation prompts that should allow `yes`, `no`, or free-text feedback
- repetitive manual debugging of workflow-level failures after a CLI update

## Usage

Install the skill, then invoke it when a Conductor workflow fails at the orchestration layer rather than in project code.

Typical first pass:

```bash
python .gemini/skills/conductor-workflow-optimization/scripts/workflow_guard.py --root .
```

If Gemini names a specific missing tool:

```bash
python .gemini/skills/conductor-workflow-optimization/scripts/workflow_guard.py --root . --forbid exit_plan_mode
```

Use the report to patch the narrowest broken workflow artifact, then verify the fix against live Gemini CLI help before retrying the workflow.
