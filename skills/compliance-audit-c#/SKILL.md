---
name: compliance-audit-c#
description: A specialized compliance audit for C# and .NET projects. Enforces architectural patterns like TDD, Dependency Injection, and the Repository Pattern for .cs files.
---

# Conductor Compliance Audit (C#)

When you invoke this skill, you must perform a strict, holistic audit of the C#/.NET code you just wrote.

## Subagent Delegation

You MUST apply a quota-aware routing decision before delegating review work.

If the `subagent-balancer` skill is available, use it first.

If it is not available, apply this inline policy:

1. If the modified file set is small and the audit can be completed reliably in the current agent, keep the review local.
2. If delegation is justified, prefer a single lightweight review sub-agent for a bounded file set.
3. Use a stronger sub-agent only for broad, ambiguous, or high-risk audits.
4. If Gemini quota is constrained, reset is far away, or the preferred model is already near limit, do not delegate. Perform the audit locally instead.
5. Never chain multiple review sub-agents for this audit unless the user explicitly requests a multi-agent review.

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


