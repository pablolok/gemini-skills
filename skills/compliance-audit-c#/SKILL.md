---
name: compliance-audit-c#
description: A specialized compliance audit for C# and .NET projects. Enforces architectural patterns like TDD, Dependency Injection, and the Repository Pattern for .cs files.
---

# Conductor Compliance Audit (C#)

When you invoke this skill, you must perform a strict, holistic audit of the C#/.NET code you just wrote.

## Subagent Delegation

You MUST resolve delegation through the balancer layer before delegating review work.

Use this order:

1. If `subagent-balancer-orchestrator` is available, use it first.
2. If the orchestrator is unavailable but the correct direct balancer is already explicit from task context, you may use that balancer directly.
3. If no balancer layer is available, prefer a local audit instead of re-implementing balancing policy here.
4. Only if the audit is still too broad or risky to keep local should you delegate directly, using one bounded generalist review subagent and avoiding chained review agents.

If you choose delegation, provide the sub-agent with the following prompt:

```text
Please review the recently modified files in this project and verify strict compliance with the following Engineering Principles:

1. **C# Standards:** Use C# 12+ features where appropriate. Follow Microsoft's .NET naming conventions and use modern language features (e.g., primary constructors, collection expressions).
2. **Cross-Platform Compatibility:** Ensure file paths are handled using platform-agnostic methods (`System.IO.Path`). No hardcoded slashes.
3. **Unit of Work & DbContext Factory Pattern:** The `UnitOfWork` and `DbContext` must NOT be injected as scoped dependencies into long-lived or singleton services. Use `IUnitOfWorkFactory` (or `IDbContextFactory`) to create short-lived instances on-demand.
4. **Base Repository Pattern:** Entities must implement `IEntity<TId>`. Repositories must inherit from a generic `IRepository<TEntity, TId>` and its EF implementation `EfRepository<TEntity, TId>`.
5. **Dependency Injection:** Runtime collaborators must come from constructor injection. No hidden `new Service()` calls in production code.
6. **TDD & Coverage:** Ensure adequate automated tests for new logic. Tests must be deterministic. The codebase MUST maintain a minimum baseline of 90% Line Coverage and 85% Branch Coverage.
7. **Static Logic Policy:** Business rules and orchestration must NOT live in static classes. Statics are strictly for constants and extensions.
8. **SOLID Principles:** Verify single responsibility, proper abstractions, and "Tell-Don't-Ask" encapsulation.
9. **Logging & Observability:** Inject `ILogger<T>` for all logging; avoid raw `Console.WriteLine` or `Debug.WriteLine` for business logic tracking.
10. **Fail-Fast Configuration:** Validate `IOptions<T>` or configuration values at the beginning of the service or application startup.
11. **Documentation:** Verify all public members include standard XML documentation (`///`).
12. **Static Analysis:** Code must pass standard static analysis (Roslyn analyzers, `.editorconfig`) without warnings.
13. **Warning Suppression Policy:** Do not use `#pragma warning disable`, `NoWarn`, `[SuppressMessage]`, GlobalSuppressions, or analyzer severity downgrades to bypass required diagnostics unless the repository explicitly documents a justified exception.
14. **Reusability Audit:** Look for the same behavior, mapping logic, validation flow, orchestration pattern, or UI-support code being implemented more than once across services, handlers, helpers, view models, controllers, or other classes. When similar logic appears multiple times, treat that as a violation unless there is a clear bounded-context reason to keep it separate. Prefer a generic reusable abstraction built with shared services, typed helper classes, extension methods, base classes, composition, or interfaces so patterns like dropdown option builders, filtering pipelines, and repeated request/response orchestration are implemented once and adapted for multiple scenarios.

If you find ANY violations, you MUST return a detailed bulleted list of the violations found.
For each violation, you must specify:
* **[File Path:Line Number]**
  * **Violation:** <Description of which principle was violated and why>
  * **Suggested Fix:** <General text description of how to fix the violation>

Otherwise, state "NO violations".
```

## Remediation

1. If the sub-agent reports **NO violations**, you may proceed with the "User Manual Verification" step.
2. If the sub-agent reports **ANY violations**, you MUST fix the code yourself to adhere to the principles before asking the user for verification. You must loop this audit until it reports "NO violations".


