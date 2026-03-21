---
name: compliance-audit-scripts
description: A specialized compliance audit for automation and scripting (PowerShell, Python, Bash). Enforces best practices for cross-platform safety, idempotency, and TDD in script files.
---

# Conductor Compliance Audit (Scripts)

When you invoke this skill, you must perform a strict, holistic audit of the scripting/automation code you just wrote.

## Subagent Delegation

You MUST invoke the `generalist` sub-agent to review the specific files modified.

Provide the sub-agent with the following prompt:

```text
Please review the recently modified files in this project and verify strict compliance with the following Engineering Principles:

1. **Automation & Scripting Standards:** 
   - **PowerShell:** Use PowerShell 7 (Core) syntax. Follow best practices for error handling (`Try/Catch`), parameter validation, and avoid using aliases in scripts.
   - **Python:** Follow PEP 8 guidelines strictly (e.g., two blank lines between top-level definitions, module-level docstrings). Use type hints for all method signatures (`-> None`, `-> str`, etc.) and complex local variables.
2. **Cross-Platform Compatibility:** Ensure that file paths are handled using platform-agnostic methods (e.g., `Join-Path` in PowerShell, `os.path.join` or `pathlib` in Python).
3. **Dependency Injection & Collaborators:** Runtime collaborators must come from constructor injection or be passed as parameters. No hidden `new Object()` or hardcoded dependency construction inside logic-heavy functions.
4. **TDD & Coverage:** Ensure there are adequate automated tests for the new logic (e.g., Pester for PowerShell, Pytest for Python). Tests must be deterministic. The codebase MUST maintain a minimum baseline of 80% Line Coverage.
5. **Static Logic & Global State:** Avoid global variables. Business rules and orchestration must live in focused functions or classes, not in the global script scope.
6. **SOLID Principles:** Verify that functions and modules have a single responsibility. Use abstractions to decouple logic from external side effects (like API calls or file system access).
7. **Idempotency:** Scripts must be safe to run multiple times. Verify that state is checked before mutating actions occur to prevent duplication or corruption.
8. **Logging & Observability:** Avoid raw `print()` or `Write-Host` for business logic tracking. Ensure a standard logging framework/mechanism is used.
9. **Fail-Fast Configuration:** Ensure all required environment variables, secrets, and file paths are validated at the very beginning of the script.
10. **Documentation:** Verify that all modules, classes, and functions include standard docstrings or comment-based help (PEP 8 compliant for Python).
11. **Static Analysis & Linting:** Code must pass standard static analysis tools without warnings before being considered compliant.

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
