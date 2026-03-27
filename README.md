# Gemini CLI Skills

A collection of custom skills for the Gemini CLI to automate and enhance software engineering workflows.

## Recommended Workflow

For most users, we recommend installing the **Compliance Audit Orchestrator**. It automatically detects which specialized audit (C#, Scripts, Angular, or Avalonia UI) to run based on your project changes.

| Skill | Description |
| :--- | :--- |
| **[Compliance Audit Orchestrator](./skills/compliance-audit-orchestrator/)** | **[Recommended]** Smart dispatcher that determines the correct specialized audit (C#, Scripts, Angular, or Avalonia UI) to perform. |
| **[Pre-Implementation Review](./skills/pre-implementation-review/)** | Reuse-first planning skill that checks for existing abstractions and duplication risk before implementation starts. |

## Specialized Skills

These are called automatically by the orchestrator but can also be invoked manually.

| Skill | Description |
| :--- | :--- |
| **[Compliance Audit (C#)](./skills/compliance-audit-c#/)** | Specialized audit for C#/.NET architectural rigor. |
| **[Compliance Audit (Angular)](./skills/compliance-audit-angular/)** | Specialized audit for Angular UI reviews. |
| **[Compliance Audit (Avalonia UI)](./skills/compliance-audit-avalonia/)** | Specialized audit for Avalonia desktop UI reviews. |
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

If you are using the Gemini CLI, you can automate the entire installation process.

**How to use:**
1.  **Activate Gemini** in your project.
2.  **Give the Command**: Copy and paste the following prompt to Gemini (replace `<path>` with the absolute path to where you cloned this repository):
    > *"Read the installation instructions at `<path>/gemini-install.md` and help me install the official skills."*
3.  **Interactive Selection**: Gemini will read the instructions, scan the repository, and prompt you to select the skills you want.
4.  **Auto-Integration**: Gemini will physically copy the skill files into your project and execute any `post_install.py` hooks automatically.

> [!TIP]
> **Versioning & Updates**: All skills now include version tracking. You can check for updates by running `python <path>/check_updates.py` from your project's root.

> [!IMPORTANT]
> **Workspace Boundaries**: Gemini may refuse to read files outside of your current project's workspace for security reasons. If you encounter this, you can use the `/directory add <path>` command to include the skills folder in your session, or use the **Manual Installation** method below.

## 🛠️ Manual Installation

If you prefer to install or update skills manually from your terminal, run this command from your project's root:

```bash
python <path-to-gemini-skills>/install.py
```

The installer will guide you through the interactive selection and handle copying/updating automatically.
If the selected skills have explicit bridge wrappers in this repository, the installer will also ask whether you want matching `.codex/skills/` support added.

## Codex Bridge Layer

This repository supports a two-layer setup when you want the same project to work well with both Gemini and Codex:

- `.gemini/skills/` contains the real Gemini skills and their implementation files.
- `.codex/skills/` contains lightweight Codex bridge wrappers that point Codex at the installed Gemini skills and add Codex-specific usage notes.

Recommended flow for Codex-enabled projects:

1. Install or update the Gemini skill into `.gemini/skills/`.
2. Add or refresh the matching Codex bridge in `.codex/skills/`.
3. Keep the bridge lightweight. It should describe when Codex should use the installed Gemini skill, not duplicate the Gemini implementation.

For Codex, the useful bridge skills in this repo are currently centered on:
- `skill-manager`
- `skill-publisher`
- `compliance-audit-avalonia`
- `compliance-audit-orchestrator`
- `compliance-audit-scripts`
- `pre-implementation-review`
- `review-optimization`

Important:
- The balancer family is Gemini-specific.
- `subagent-balancer`, `subagent-balancer-api`, and `subagent-balancer-orchestrator` should be treated as Gemini skills, not standard Codex bridge skills.
- Codex should generally ignore those balancers unless you are explicitly building a Codex integration for them.

## Skill Scope Catalog

This repository now includes a machine-readable installer catalog at [`install.config.json`](./install.config.json).

- `distribution: "shared"` means the skill is intended to be shared across AI-tool integrations.
- `distribution: "gemini-only"` means the skill is personal to Gemini flows and should not automatically be treated as a Codex bridge or Claude reference candidate.
- `supports.codex_bridge` and `supports.claude_reference` control whether `skill-manager` should offer or generate those companion artifacts during install flows.

The balancer family is the canonical `gemini-only` example:
- `subagent-balancer`
- `subagent-balancer-api`
- `subagent-balancer-orchestrator`

### 🔄 Checking for Updates

To check for newer versions of installed skills without running the full installer:

```bash
python <path-to-gemini-skills>/check_updates.py
```

---
Created by [pablolok](https://github.com/pablolok)
