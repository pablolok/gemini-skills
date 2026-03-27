---
name: pre-implementation-review
description: Use before writing code, patching files, or scaffolding UI/backend changes to review the planned work for reuse opportunities, existing abstractions, extension points, duplication risk, and implementation boundaries. Trigger during reasoning and planning, especially when a feature may introduce reusable components, shared services, common UI patterns, validators, or orchestration logic.
---

# Pre-Implementation Review

Use this skill before implementation starts. The goal is to prevent duplicate code and late refactors by making reuse decisions during planning rather than after code exists.

## Required Outcome

Before writing code, produce a short implementation-readiness review that answers:

1. What existing code, components, services, helpers, or patterns already solve part of this request?
2. What should be extended versus created new?
3. What abstractions should be introduced now to avoid duplication?
4. What API or interface should that reusable piece expose?
5. What files or modules should own the reusable implementation?
6. What duplication or refactor risk should be avoided during implementation?

## Review Workflow

When invoked, you must:

1. Identify the feature or change being planned.
2. Search the codebase for existing components, controls, services, helpers, validators, templates, or workflows that look similar.
3. Group findings into:
   - direct reuse
   - extend existing abstraction
   - create new reusable abstraction
   - safe to implement locally without reuse
4. Flag duplication risk early:
   - repeated UI widgets such as dropdowns, pickers, menus, cards, dialogs, filters
   - repeated business rules, mappings, validators, request builders, orchestration flows
   - repeated styling, layout structures, or resource dictionaries
5. Recommend the narrowest reusable abstraction that solves the planned work without over-generalizing.
6. Define the intended ownership boundary before implementation:
   - reusable component/control/service/helper location
   - consumer locations
   - tests that should exist with the new abstraction

## Decision Rules

- Prefer reusing or extending existing code when a stable abstraction already exists.
- Prefer creating a reusable abstraction before implementation when the same pattern is likely to appear in more than one place.
- Do not wait for duplication to land in code if the duplication is already obvious from the request and the existing codebase.
- Do not force generic abstractions when the use case is truly isolated and unlikely to repeat.
- Favor explicit inputs/outputs and small extension points over oversized generic frameworks.

## Output Format

Return a concise planning note with these sections:

- `Existing Reuse Candidates`
- `Recommended Approach`
- `Reusable Abstraction`
- `Implementation Boundary`
- `Risks To Avoid`

If no reusable opportunity exists, say so explicitly and justify why local implementation is acceptable.

## Boundary

- This skill runs before code changes.
- It does not replace implementation or post-change audits.
- If implementation proceeds, use the relevant compliance audit afterward to verify the result.
