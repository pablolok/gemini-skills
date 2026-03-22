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

### Gemini CLI Integration

If you are using the Gemini CLI, you can ask Gemini to manage skills for you. Gemini uses the **[Skill Manager](./published/utility/skill-manager/)** skill to:
1.  **Locate** the global skills repository.
2.  **Scan** for available official skills.
3.  **Prompt** you interactively (using the standard `ask_user` tool) to select which skills to install.
4.  **Execute** the installation and post-install hooks automatically.

To try it, simply tell Gemini: *"Install official skills from the global repository."*

---
Created by [pablolok](https://github.com/pablolok)
