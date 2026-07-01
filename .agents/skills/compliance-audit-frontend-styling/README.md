# Conductor Compliance Audit Skill (Frontend Styling)

A specialized Gemini skill for cross-framework frontend styling compliance reviews.

## What It Checks

- reusable styling primitives instead of duplicated component-local CSS
- design token usage for spacing, color, typography, radius, shadow, and breakpoints
- themeable semantic color tokens instead of hardcoded product colors in component or app styling
- selector discipline, maintainable specificity, and avoidance of fragile DOM-coupled rules
- responsive behavior, accessibility-aware focus and contrast patterns, and theme consistency
- cleanup of dead styles, duplicated rules, and styling drift across frontend components

## Typical Trigger

Use this when a phase changes frontend styling or UI structure such as:

- `.css`, `.scss`, `.sass`, or `.less` files
- component files with co-located styling concerns
- shared theme, token, utility, or design-system stylesheets
- frontend UI code where repeated styling suggests a missing shared primitive

especially when the project contains frontend indicators such as Angular, React, Vue, Svelte, Vite, Next.js, Nuxt, or similar web UI tooling.

## Installation & Integration

### Recommended Strategy
The **[Compliance Audit Orchestrator](../compliance-audit-orchestrator/)** is the primary way to use this skill. It automatically detects frontend styling changes and invokes this audit when styling files or co-located UI styling concerns were modified.

This keeps `conductor/workflow.md` clean: the workflow should reference the orchestrator as the single compliance-audit entrypoint, not each specialized audit skill directly.

### Manual Usage
To trigger this specific audit manually:
> "Use the compliance-audit-frontend-styling skill."
