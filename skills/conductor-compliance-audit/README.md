# Conductor Compliance Audit Skill

A specialized skill for the **Gemini CLI** to enforce architectural rigor and engineering standards during the development of C#/.NET projects.

## Overview

This skill automates the "Sub-Agent Compliance Audit" step of the **Conductor** workflow. When invoked, it delegates a comprehensive review to a `generalist` sub-agent to verify that newly implemented code strictly adheres to project-specific engineering principles.

## Audit Criteria

The skill checks for:
1.  **Unit of Work & DbContext Factory Pattern**: Prevents captive dependencies by ensuring short-lived UoW/DbContext instances.
2.  **Base Repository Pattern**: Ensures entities implement `IEntity<TId>` and repositories follow a standard generic structure.
3.  **Dependency Injection (DI)**: Enforces constructor injection and prohibits static logic or manual `new` instantiation for runtime collaborators.
4.  **TDD & Coverage**: Verifies automated test presence and adherence to coverage baselines (min. 90% Line / 85% Branch).
5.  **Static Logic Policy**: Prohibits business logic in static classes.
6.  **SOLID Principles**: Validates single responsibility and proper encapsulation.

## Installation & Integration

### Automatic Workflow Setup
The first time an agent invokes this skill, it checks for the existence of `conductor/workflow.md`. If the skill is not listed in the "Mandatory Verification Workflow", it will **automatically update the workflow file** to include the audit as a required step.

### Usage
To trigger the audit, simply instruct the Gemini CLI:
> "Run the conductor compliance audit."
