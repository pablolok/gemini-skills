---
name: pre-implementation-review
description: Codex entry point for reuse-first planning before implementation. Use when reasoning about a feature or refactor before editing files so Codex checks for existing abstractions, reusable components, duplication risk, and the right implementation boundary up front.
---

# Pre-Implementation Review Bridge

Use the installed Gemini skill at `.gemini/skills/pre-implementation-review/SKILL.md` as the source of truth.

Workflow:

1. Read and follow `.gemini/skills/pre-implementation-review/SKILL.md`.
2. Search the current codebase for existing implementations before proposing new code.
3. Produce the reuse decision before editing files.
4. Do not treat this bridge folder as the implementation source. It exists only so Codex can discover the installed Gemini skill.
