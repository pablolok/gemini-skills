# Compliance Audit Orchestrator Skill

A central dispatcher for the **Gemini CLI** that determines and executes the correct compliance audit based on the files modified during a development phase.

## Overview

This skill is designed to solve the problem of selecting between multiple specialized compliance audits (like C# or Scripts). It acts as a smart orchestrator that inspects your changes and delegates the audit to the appropriate specialized skill.

## How it Works

1.  **File Inspection:** The orchestrator identifies which files were modified in the current phase.
2.  **Smart Delegation:**
    *   **C# Files:** Triggers the `compliance-audit-c#` skill.
    *   **Script Files:** Triggers the `complaiance-audit-scripts` skill (.ps1, .py, .sh, .bat, .js).
3.  **Sequential Execution:** If you modify both C# and script files, it runs both audits in sequence.

## Installation & Integration

### Mandatory Setup
This is the **only** skill you should manually add to your `conductor/workflow.md`. It is designed to be the single entry point for all compliance audits.

### Usage
To trigger the automated orchestration, simply instruct the Gemini CLI:
> "Use the compliance-audit-orchestrator skill."

## Benefits

*   **No Conflicts:** Prevents Gemini from being confused by multiple audit skills.
*   **Automatic Selection:** You don't have to remember which audit to run.
*   **Workflow Integration:** Automatically registers itself as a mandatory step in the Conductor workflow.
