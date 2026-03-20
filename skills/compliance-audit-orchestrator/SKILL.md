---
name: compliance-audit-orchestrator
description: Use when finalizing an implementation phase in a Conductor track to determine and invoke the correct specialized compliance audit (C# or Scripts) based on the files modified.
---

# Compliance Audit Orchestrator

This skill acts as the central entry point for compliance audits. It ensures that the correct specialized audit is performed based on the files you have modified during the current implementation phase.

## Orchestration Logic

When you invoke this skill, you MUST:

1.  **Identify Modified Files:** List all files created or modified during the current implementation phase.
2.  **Determine Specialized Skills:**
    *   If any **C# files** (`.cs`, `.csproj`, `.sln`) were modified: You MUST invoke the `compliance-audit-c#` skill.
    *   If any **Script files** (`.ps1`, `.py`, `.sh`, `.bat`, `.js` for Node.js scripts) were modified: You MUST invoke the `complaiance-audit-scripts` skill.
3.  **Sequential Execution:** If both types of files were modified, run the audits sequentially (C# first, then Scripts).
4.  **No Relevant Files:** If no files matching these patterns were found, inform the user and ask if a manual audit is required.

## Remediation

Follow the remediation steps defined within each specialized skill. You are only "Done" when all invoked specialized audits report "NO violations".

## Automatic Workflow Integration

If the file `conductor/workflow.md` exists and does not already mention the `compliance-audit-orchestrator` skill as a mandatory step in the "Verification Workflow", you MUST update that file to include it. 

**Note:** If `compliance-audit-c#` or `complaiance-audit-scripts` were previously registered in the workflow, you MUST replace them with this orchestrator to prevent redundant or conflicting audits.
