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

## Installation And Integration

If the skill is installed through this repository's supported installer flow, the workflow integration is automatic:

- `python <path-to-gemini-skills>/install.py`
- `/skill-manager:install workflow/conductor-workflow-optimization`

In that path, the installer copies the skill into `.gemini/skills/` and then runs the skill's `post_install.py` hook. That hook updates `conductor/workflow.md` when a Conductor workflow is present.

Important limits:

- If the target project does not have `conductor/workflow.md`, the hook skips integration.
- If the workflow structure is too different for the hook to patch safely, it reports that manual integration is required.
- If you copy the skill folder manually instead of using the installer, no hook runs automatically.

Manual integration path:

```bash
python .gemini/skills/conductor-workflow-optimization/post_install.py .
```

If you prefer Gemini to apply the workflow change conversationally, install the skill first, then ask Gemini to update `conductor/workflow.md` according to the skill instructions.

Typical first pass:

```bash
python .gemini/skills/conductor-workflow-optimization/scripts/workflow_guard.py --root .
```

If Gemini names a specific missing tool:

```bash
python .gemini/skills/conductor-workflow-optimization/scripts/workflow_guard.py --root . --forbid exit_plan_mode
```

Use the report to patch the narrowest broken workflow artifact, then verify the fix against live Gemini CLI help before retrying the workflow.
