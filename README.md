# Gemini CLI Skills

A collection of custom skills for the Gemini CLI to automate and enhance software engineering workflows.

## Recommended Workflow

For most users, we recommend installing the **Compliance Audit Orchestrator**. It automatically detects which specialized audit (C# or Scripts) to run based on your project changes.

| Skill | Description |
| :--- | :--- |
| **[Compliance Audit Orchestrator](./skills/compliance-audit-orchestrator/)** | **[Recommended]** Smart dispatcher that determines the correct specialized audit (C# or Scripts) to perform. |

## Specialized Skills

These are called automatically by the orchestrator but can also be invoked manually.

| Skill | Description |
| :--- | :--- |
| **[Compliance Audit (C#)](./skills/compliance-audit-c#/)** | Specialized audit for C#/.NET architectural rigor. |
| **[Compliance Audit (Scripts)](./skills/complaiance-audit-scripts/)** | Specialized audit for automation and script-based projects. |

## Installation & Usage

1.  **Clone this repository** into your local projects directory.
2.  **Activate a Skill**: Use the `activate_skill` command within the Gemini CLI. We recommend activating `compliance-audit-orchestrator`.
3.  **Automatic Integration**: These skills are designed to integrate with the **Conductor** workflow and will automatically update `conductor/workflow.md` if it exists.

---
Created by [pablolok](https://github.com/pablolok)
