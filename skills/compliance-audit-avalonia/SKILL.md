---
name: compliance-audit-avalonia
description: A specialized compliance audit for Avalonia UI applications and Avalonia .NET desktop code. Use when reviewing modified Avalonia views, XAML, code-behind, view models, styling, resources, or related `.axaml`, `.xaml`, `.cs`, `.csproj`, and asset files in an Avalonia project to enforce Avalonia UI best practices, MVVM discipline, accessibility, theming consistency, and desktop test coverage gates.
---

# Conductor Compliance Audit (Avalonia UI)

When you invoke this skill, you must perform a strict, holistic audit of the Avalonia UI code that was just changed.

## Repository Boundary

This skill is read-only with respect to skill infrastructure and workflow definitions.

- Do not edit `skills/`, `published/`, installer/publisher tooling, or `conductor/workflow.md` as part of this audit.
- If the audit reveals a missing Avalonia rule, a gap in the orchestrator, or a skill-design problem, report it to the user as a proposal.
- Let the user decide whether that follow-up should be handled in the skill repository as a separate task.

## Subagent Delegation

You MUST resolve delegation through the balancer layer before delegating review work.

Use this order:

1. If `subagent-balancer-orchestrator` is available, use it first.
2. If the orchestrator is unavailable but the correct direct balancer is already explicit from task context, you may use that balancer directly.
3. If no balancer layer is available, prefer a local audit instead of re-implementing balancing policy here.
4. Only if the audit is still too broad or risky to keep local should you delegate directly, using one bounded generalist review subagent and avoiding chained review agents.

If you choose delegation, provide the sub-agent with the following prompt:

```text
Please review the recently modified Avalonia UI files in this project and verify strict compliance with the following Engineering Principles:

1. **Avalonia UI Architecture:**
   - Prefer clear MVVM boundaries.
   - Keep view logic in XAML or presentation-focused code-behind only when justified.
   - Push business logic, persistence, and navigation orchestration out of views and controls.
   - Flag repeated UI patterns across views, styles, and control themes that indicate a missing reusable control, templated control, behavior, or style.
2. **XAML Discipline:** Keep markup readable, avoid deeply nested or duplicated layout trees, repeated widget structures such as custom pickers or menus, and prefer reusable styles, templates, and controls over repeated view fragments.
3. **ViewModel Rigor:** Use strongly typed properties/commands, explicit state transitions, and predictable notification patterns. Avoid hidden mutable shared state.
4. **Binding Correctness:** Flag fragile bindings, missing null-state handling, silent binding failures, and unnecessarily complex converters or code-behind event wiring.
5. **Threading & Responsiveness:** Ensure UI-bound state changes are marshalled correctly, background work does not block the UI thread, and async command flows remain deterministic.
6. **Styling & Theming:** Prefer theme resources, reusable styles, and centralized tokens over hardcoded colors, dimensions, or duplicated control styling. Preserve light/dark and high-contrast compatibility when the project supports it. Repeated styling for the same widget across multiple views is a signal to extract a generic reusable control or theme primitive.
7. **Accessibility & Input:** Verify keyboard navigation, focus visibility, semantic labels/tooltips where needed, contrast-sensitive choices, and screen-reader-relevant naming patterns where the app already supports them.
8. **Resource Management:** Keep assets, resource dictionaries, and merged theme files organized. Avoid dead resources, inconsistent naming, or view-local resource duplication when a shared location is warranted.
9. **Testing & Coverage:** Ensure new UI logic, converters, view models, and interaction behavior have adequate automated coverage. Desktop changes must preserve or improve the project's verification gates.
10. **Performance:** Flag avoidable visual-tree churn, oversized item templates, repeated expensive converters, synchronous IO on the UI path, or obviously wasteful redraw/layout patterns.
11. **Platform Compatibility:** Respect Avalonia cross-platform expectations. Avoid OS-specific assumptions in UI code unless the feature is explicitly platform-scoped and guarded.
12. **Documentation & Clarity:** Public reusable controls, behaviors, and styling extension points should be named clearly and documented where the codebase expects it.
13. **Static Analysis:** Code should be compatible with the project's configured analyzers, XAML checks, and build diagnostics without introducing warnings.
14. **Reusability Audit:** Look for the same widget, control composition, interaction pattern, or styling package being implemented more than once across views, controls, code-behind, or resource dictionaries. When similar structure, behavior, and styling appear multiple times, treat that as a violation unless there is a clear product reason to keep them separate. Prefer a generic reusable control API built with custom controls, templated controls, styles, behaviors, attached properties, data templates, or shared view models so patterns like dropdowns, pickers, flyouts, and repeated cards are implemented once and adapted for multiple scenarios.

If you find ANY violations, you MUST return a detailed bulleted list of the violations found.
For each violation, you must specify:
* **[File Path:Line Number]**
  * **Violation:** <Description of which principle was violated and why>
  * **Suggested Fix:** <General text description of how to fix the violation>

Otherwise, state "NO violations".
```

## Remediation

1. If the audit reports **NO violations**, you may proceed with the "User Manual Verification" step.
2. If the audit reports **ANY violations**, you MUST fix the code yourself to adhere to the principles before asking the user for verification. You must loop this audit until it reports "NO violations".
