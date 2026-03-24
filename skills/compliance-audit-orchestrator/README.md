# Compliance Audit Orchestrator Skill

A central dispatcher for the **Gemini CLI** that determines and executes the correct compliance audit based on the files modified during a development phase.

## Overview

This skill is designed to solve the problem of selecting between multiple specialized compliance audits (like C#, Scripts, or Angular). It acts as a smart orchestrator that inspects your changes and delegates the audit to the appropriate specialized skill.

## How it Works

1.  **File Inspection:** The orchestrator identifies which files were modified in the current phase.
2.  **Skill Presence Verification:** Before triggering any specialized audit, the orchestrator MUST verify that the required skill is "installed" and available for use in the current environment (e.g., in the project's local `skills/` directory or the user's global `.gemini/skills/` directory).
3.  **Smart Delegation:**
    *   **C# Files:** Triggers the `compliance-audit-c#` skill if it's available.
    *   **Script Files:** Triggers the `compliance-audit-scripts` skill if it's available.
    *   **Angular Files:** Triggers the `compliance-audit-angular` skill when Angular indicators are present and Angular UI files were changed.
4.  **Sequential Execution:** If you modify multiple supported file groups, it runs all available audits in sequence.
5.  **Graceful Error Handling:** If a specialized audit is required based on your file changes but the skill is NOT found, the orchestrator will inform you and ask for guidance.

## Future Extensibility

To add support for a new specialized audit (e.g., `compliance-audit-react`), simply:
1.  Add a new file pattern to the **Determine and Dispatch** logic.
2.  The orchestrator will automatically handle the presence check and dispatching.

### Mandatory Setup
This is the **only** skill you should manually add to your `conductor/workflow.md`. It is designed to be the single entry point for all compliance audits.

### Usage
To trigger the automated orchestration, simply instruct the Gemini CLI:
> "Use the compliance-audit-orchestrator skill."

## Benefits

*   **No Conflicts:** Prevents Gemini from being confused by multiple audit skills.
*   **Automatic Selection:** You don't have to remember which audit to run.
*   **Workflow Integration:** Automatically registers itself as a mandatory step in the Conductor workflow.
