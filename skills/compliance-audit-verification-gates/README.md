# Conductor Compliance Audit Skill (Verification Gates)

A generic Gemini skill that checks whether automated verification is complete before user manual verification.

## What It Checks

- required automated verification was identified from repository context
- tests, linting, type checks, and static analysis completed when relevant
- builds, compiles, and bundles succeeded when the changed stack requires them
- warnings in required verification output are treated as blocking unless explicitly allowed

## Typical Trigger

Use this at the end of an implementation phase when code changed and you need to confirm the work is actually ready for manual verification across any stack.
