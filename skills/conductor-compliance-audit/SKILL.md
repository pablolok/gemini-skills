---
name: conductor-compliance-audit
description: Ensure all code implemented in a track phase adheres to the strict engineering principles defined in the workflow (e.g., TDD, Repository/UoW Pattern, Dependency Injection). Use this immediately before finalizing any implementation phase.
---

# Conductor Compliance Audit

When you invoke this skill, you must perform a strict, holistic audit of the code you just wrote during the current implementation phase.

## Subagent Delegation

You MUST invoke the `generalist` sub-agent to review the specific files modified.

Provide the sub-agent with the following prompt:

```text
Please review the recently modified files in this project and verify strict compliance with the following Engineering Principles:

1. **Unit of Work & DbContext Factory Pattern:** The `UnitOfWork` and `DbContext` must NOT be injected as scoped dependencies into long-lived or singleton services. Instead, an `IUnitOfWorkFactory` (or `IDbContextFactory`) should be used to create short-lived instances on-demand to avoid captive dependency issues.
2. **Base Repository Pattern:** The project MUST utilize a generic base repository pattern. Entities must implement `IEntity<TId>`. Repositories must inherit from a generic `IRepository<TEntity, TId>` and its EF implementation `EfRepository<TEntity, TId>`.
3. **Dependency Injection:** Runtime collaborators must come from constructor injection. No static fallback wiring or hidden `new Service()` calls in production code.
4. **TDD & Coverage:** Ensure there are adequate automated tests for the new logic. Tests must be deterministic. The codebase MUST maintain a minimum baseline of 90% Line Coverage and 85% Branch Coverage.
5. **Static Logic Policy:** Business rules and orchestration must NOT live in static classes. Statics are only for constants and extensions.
6. **SOLID Principles:** Verify that new classes have a single responsibility, proper abstractions, and use encapsulation (Tell-Don't-Ask).

If you find ANY violations, report them clearly. Otherwise, state "NO violations".
```

## Remediation

1. If the sub-agent reports **NO violations**, you may proceed with the "User Manual Verification" step.
2. If the sub-agent reports **ANY violations**, you MUST fix the code yourself to adhere to the principles before asking the user for verification. You must loop this audit until it reports "NO violations".

## Automatic Workflow Integration

If the file `conductor/workflow.md` exists and does not already mention the `conductor-compliance-audit` skill as a mandatory step in the "Verification Workflow", you MUST update that file to include it. This ensures that the compliance audit is strictly integrated into the local development lifecycle.
