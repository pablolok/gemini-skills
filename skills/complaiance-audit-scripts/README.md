# Conductor Compliance Audit Skill (Scripts)

A specialized skill for the **Gemini CLI** to enforce engineering standards and best practices during the development of automation and scripting projects (PowerShell, Python, Bash).

## Overview

This skill automates the "Sub-Agent Compliance Audit" step of the **Conductor** workflow for script-based environments. When invoked, it delegates a comprehensive review to a `generalist` sub-agent to verify that the code strictly adheres to platform-agnostic, automated, and idiomatic scripting standards.

## Audit Criteria

The skill performs a holistic review based on 11 key principles:

1.  **Automation & Scripting Standards:** Enforces PowerShell 7 (Core) syntax and Python PEP 8 guidelines.
2.  **Cross-Platform Compatibility:** Mandatory platform-agnostic file path handling (`Join-Path` or `pathlib`).
3.  **Dependency Injection:** Prohibits hidden dependencies; mandates constructor or parameter injection.
4.  **TDD & Coverage:** Enforces 80% Line Coverage (Pester/Pytest).
5.  **Static Logic & Global State:** Prohibits business logic in the global script scope; mandates focused functions/classes.
6.  **SOLID Principles:** Validates single responsibility and decoupling from side effects.
7.  **Idempotency:** Ensures scripts are safe for multiple executions without state corruption.
8.  **Logging & Observability:** Mandatory use of standard logging frameworks instead of raw `print()` or `Write-Host`.
9.  **Fail-Fast Configuration:** Early validation of environment variables and secrets.
10. **Documentation:** Mandatory docstrings or comment-based help for all functions.
11. **Static Analysis & Linting:** Code must pass standard linters (PSScriptAnalyzer, Flake8) without warnings.

## Reporting Format

Violations are reported using a strict, machine-readable format to facilitate quick remediation:

> * **[File Path:Line Number]**
>   * **Violation:** Description of the issue.
>   * **Suggested Fix:** How to fix it.

## Installation & Integration

### Automatic Workflow Setup
The first time an agent invokes this skill, it checks for `conductor/workflow.md`. If the skill is not listed in the "Mandatory Verification Workflow", it will **automatically update the workflow file** to include the audit.

### Usage
To trigger the audit, simply instruct the Gemini CLI:
> "Use the complaiance-audit-scripts skill."
