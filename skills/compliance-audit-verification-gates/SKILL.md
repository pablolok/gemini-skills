---
name: compliance-audit-verification-gates
description: A generic compliance audit that verifies required automated verification gates passed before manual verification. Use when reviewing changed code across any stack to ensure relevant tests, builds, compilers, bundlers, linters, and static-analysis commands completed successfully and without warnings unless an explicit warning exception is documented.
---

# Conductor Compliance Audit (Verification Gates)

When you invoke this skill, you must perform a strict audit of whether the implementation is actually ready for user manual verification.

## Repository Boundary

This skill is read-only with respect to skill infrastructure and workflow definitions.

- Do not edit `skills/`, `published/`, installer/publisher tooling, or `conductor/workflow.md` as part of this audit.
- If the audit reveals that the workflow, orchestrator, or another audit skill should change, report that to the user as a proposal.
- Let the user decide whether that follow-up should be handled in the skill repository as a separate task.

## Audit Objective

This skill exists to prevent Gemini from sending work to user manual verification while required automated verification is still red or noisy.

You must verify all of the following for the changed code paths:

1. Required automated verification was identified from the repository context instead of guessed.
2. Each required command was actually run, or the absence is reported as a violation.
3. Required tests passed.
4. Required linting, type-checking, and static-analysis checks passed.
5. Any required build, compile, bundle, or packaging command succeeded.
6. Build, compile, bundle, lint, and static-analysis output is warning-free unless the repository or user explicitly documents an allowed warning exception.
7. Warning-free status must come from fixing the underlying issue, not from suppressing diagnostics through pragmas, `NoWarn`, `.editorconfig` severity downgrades, suppression attributes, or equivalent mechanisms unless an explicit repository exception is documented.
8. Manual verification is blocked until the above conditions are green.

## Verification Rules

When performing this audit, you MUST:

1. Determine the changed code areas and relevant technology stacks from the modified files and repository structure.
2. Derive the expected verification commands from project documentation, scripts, existing CI conventions, or explicit user instructions.
3. Treat missing verification evidence as a violation. Do not assume a check passed just because no failure was mentioned.
4. Treat warnings as violations for required build, compile, bundle, lint, and static-analysis commands unless the warning is explicitly allowed in repository documentation or by direct user instruction.
5. Treat warning suppressions used to hide required diagnostics as violations unless the repository explicitly documents the exception and its rationale.
6. For compiled or bundled codebases, require a successful and warning-free build before approving manual verification.
7. For mixed-stack changes, require all relevant gates for each affected stack.
8. If the correct verification command is genuinely unclear, report that as a blocking gap instead of inventing a command.

Examples of expected gates by stack:

- Angular or other bundled frontend work: production or project-standard build, relevant tests, linting, and framework diagnostics.
- C# or .NET work: solution or project build, tests, analyzers, and warning-free compiler output.
- Script-heavy changes: relevant tests plus linting or static analysis where the repository defines them.
- Library or package changes: packaging or import-validation steps when the repository normally treats them as release gates.

## Subagent Delegation

You MUST resolve delegation through the balancer layer before delegating review work.

Use this order:

1. If `subagent-balancer-orchestrator` is available, use it first.
2. If the orchestrator is unavailable but the correct direct balancer is already explicit from task context, you may use that balancer directly.
3. If no balancer layer is available, prefer a local audit instead of re-implementing balancing policy here.
4. Only if the audit is still too broad or risky to keep local should you delegate directly, using one bounded generalist review subagent and avoiding chained review agents.

If you choose delegation, provide the sub-agent with the following prompt:

```text
Please review the recently modified code and determine whether user manual verification is blocked by incomplete or failing automated verification.

Audit for these requirements:
1. Identify the affected stacks from the changed files.
2. Determine which automated verification commands are required from repository context.
3. Verify that required tests, linting, type checks, static analysis, and build/compile/bundle commands were actually run when applicable.
4. Treat missing execution evidence as a violation.
5. Treat warnings in required build, compile, bundle, lint, or static-analysis output as violations unless the repository explicitly allows them.
6. Treat `#pragma warning disable`, `NoWarn`, `SuppressMessage`, analyzer severity downgrades, and equivalent suppression mechanisms as violations when they are used to avoid required warning remediation.
7. For compiled or bundled code, require a successful warning-free build before manual verification.
8. If the correct command is unclear, report that as a blocking gap rather than guessing.

If you find ANY violations, you MUST return a detailed bulleted list of the violations found.
For each violation, you must specify:
* **[Scope]**
  * **Violation:** <Description of the missing, failing, or warning-producing verification gate>
  * **Suggested Fix:** <General text description of how to obtain a passing, warning-free gate>

Otherwise, state "NO violations".
```

## Remediation

1. If the audit reports **NO violations**, manual verification may proceed.
2. If the audit reports **ANY violations**, you MUST resolve or clearly surface those violations before asking the user for manual verification.
3. Do not downgrade violations into suggestions when they block the verification gate.
