# Gemini CLI Skills

A collection of custom skills for the Gemini CLI to automate and enhance software engineering workflows.

## Available Skills

| Skill | Description |
| :--- | :--- |
| **[Compliance Audit (C#)](./skills/compliance-audit-c#/)** | Ensures C#/.NET code adheres to strict architectural principles (TDD, DI, UoW, Repository Pattern). |
| **[Compliance Audit (Scripts)](./skills/complaiance-audit-scripts/)** | Enforces engineering standards for automation and scripting (PowerShell, Python, Bash) with focus on idempotency and cross-platform safety. |

## Installation & Usage

1.  **Clone this repository** into your local projects directory.
2.  **Activate a Skill**: Use the `activate_skill` command within the Gemini CLI.
3.  **Automatic Integration**: These skills are designed to integrate with the **Conductor** workflow and will automatically update `conductor/workflow.md` if it exists.

---
Created by [pablolok](https://github.com/pablolok)
