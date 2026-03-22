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

## 🚀 Gemini CLI Integration (Recommended)

If you are using the Gemini CLI, you don't need to run scripts manually. You can ask Gemini to manage the installation process for you.

**How to use:**
1.  **Activate Gemini** in your project.
2.  **Give the Command**: Tell Gemini: *"Install official skills from the global repository."*
3.  **Interactive Selection**: Gemini will use the built-in **[Skill Manager](./published/utility/skill-manager/)** to scan for available skills and prompt you to select the ones you want.
4.  **Auto-Integration**: Gemini will handle the junctions and any `post_install.py` hooks (like updating your `workflow.md`) automatically.

## 🛠️ Manual Installation

If you prefer to install skills manually from your terminal, run this command from your project's root:

```bash
python <path-to-gemini-skills>/install.py
```

The installer will guide you through the same interactive process.

---
Created by [pablolok](https://github.com/pablolok)
