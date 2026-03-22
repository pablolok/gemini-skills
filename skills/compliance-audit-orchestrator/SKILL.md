---
name: compliance-audit-orchestrator
description: Use when finalizing an implementation phase in a Conductor track to determine and invoke the correct specialized compliance audit (C# or Scripts) based on the files modified.
---

# Compliance Audit Orchestrator

This skill acts as the central entry point for compliance audits. It ensures that the correct specialized audit is performed based on the files you have modified during the current implementation phase.

## Orchestration Logic

When you invoke this skill, you MUST:

1.  **Identify Modified Files:** List all files created or modified during the current implementation phase.
2.  **Skill Standards Audit**: If any skill-related files (`SKILL.md`, `metadata.json`) were modified, verify that they meet the official standards (SemVer, correct frontmatter, present README).
3.  **Verify Skill Presence:** Before any invocation, you MUST verify if the required specialized skill is "installed" and available for use in the current environment. A skill is considered available if its `SKILL.md` file exists in either:
    *   The project's local `skills/` directory.
    *   The user's global `.gemini/skills/` directory.
3.  **Apply Subagent Routing Guardrails:** Before dispatching to a specialized audit, check whether the user provided model-selection constraints or quota information. If so:
    *   If `subagent-balancer` is available, invoke it first and carry its routing decision into the specialized audit.
    *   If `subagent-balancer` is not available, inline its minimum policy: preserve explicit model selection, do not silently downgrade from Pro to Flash, and prefer a local audit over an unwanted fallback.
4.  **Determine and Dispatch:**
    *   **C# Audit:** If any **C# files** (`.cs`, `.csproj`, `.sln`) were modified, verify the presence of `compliance-audit-c#`. If present, invoke it.
    *   **Scripts Audit:** If any **Script files** (`.ps1`, `.py`, `.sh`, `.bat`, `.js` for Node.js scripts) were modified, verify the presence of `compliance-audit-scripts`. If present, invoke it.
5.  **Handling Missing Skills:** If a specialized audit is required based on the file changes but the skill is NOT found:
    *   DO NOT fail silently. 
    *   Inform the user clearly: *"The implementation modified <file types> but the required specialized audit skill '<skill name>' was not found."*
    *   Propose alternative verification or skip as per user preference.
6.  **Sequential Execution:** If multiple specialized audits are required and available, run them sequentially (C# first, then Scripts).

## Future Extensibility Pattern

To add support for a new specialized audit (e.g., `compliance-audit-frontend`):
1.  Add a new file pattern to the **Determine and Dispatch** logic.
2.  Specify the required skill name.
3.  The orchestrator will automatically handle the presence check and dispatching.

## Remediation

Follow the remediation steps defined within each specialized skill. You are only "Done" when all invoked and available specialized audits report "NO violations".

## Automatic Workflow Integration

If the file `conductor/workflow.md` exists and does not already mention the `compliance-audit-orchestrator` skill as a mandatory step in the "Verification Workflow", you MUST update that file to include it. 

**Note:** If any specialized audit skills were previously registered in the workflow, you MUST replace them with this orchestrator.
