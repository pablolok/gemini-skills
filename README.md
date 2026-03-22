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
| **[Compliance Audit (Scripts)](./skills/compliance-audit-scripts/)** | Specialized audit for automation and script-based projects. |

## Installation & Usage

1.  **Clone this repository** into your local projects directory.
2.  **Activate a Skill**: Use the `activate_skill` command within the Gemini CLI. We recommend activating `compliance-audit-orchestrator`.
3.  **Automatic Integration**: These skills are designed to integrate with the **Conductor** workflow and will automatically update `conductor/workflow.md` if it exists.

## Official 'Published' Skills

This repository provides a set of official, stable skills in the `published/` directory. These skills are categorized and ready for use in any project.

### Available Categories:
- **audit/**: Skills for code quality and compliance audits.
- **workflow/**: Skills for enhancing the Conductor workflow.
- **utility/**: General purpose utility skills.

## Using this Repository as a Skill Provider

You can easily install any of the official skills into your own projects using the interactive installer.

### Interactive Installation

To install skills into your current project, run the following command from your project's root:

```bash
python <path-to-gemini-skills>/install.py
```

The installer will:
1.  **Scan** the `published/` directory for available skills.
2.  **Prompt** you to select which skills you want to install.
3.  **Create Junctions**: Automatically link the skills into your project's `.gemini/skills/` directory.
4.  **Run Hooks**: Execute any skill-specific `post_install.py` hooks (e.g., to integrate with your `conductor/workflow.md`).

---
Created by [pablolok](https://github.com/pablolok)
