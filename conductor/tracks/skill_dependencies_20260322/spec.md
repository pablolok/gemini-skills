# Specification: Skill Dependency Management

## Overview
This track implements a dependency management system for Gemini CLI skills. It ensures that when a skill is installed, all other skills it depends on are also present and correctly configured. For example, the `compliance-audit-c#` and `compliance-audit-scripts` skills will depend on `compliance-audit-orchestrator`.

## Functional Requirements
- **Dependency Declaration**: Skills declare their dependencies in a `dependencies` array within `metadata.json`.
- **Dependency Resolution**: During installation, the installer (`install.py`) must recursively check for all dependencies.
- **Validation**: Ensure that all declared dependencies are valid skills within the `skills/` or `published/` directory.
- **Interactive Installation**: If a dependency is missing, the installer should prompt the user for confirmation before installing it.
- **Cycle Detection**: Prevent infinite loops in recursive dependency resolution.
- **Lifecycle Management**: When a skill is removed, its dependencies should only be removed if no other skill depends on them (optional, to be decided).

## Non-Functional Requirements
- **Robustness**: The installation process must fail gracefully if a dependency cannot be found or installed.
- **User Feedback**: Provide clear status messages during dependency resolution and installation.
- **Performance**: Resolution should be fast and not significantly delay the installation of a single skill.

## Acceptance Criteria
- [ ] Skills can successfully declare dependencies in `metadata.json`.
- [ ] The installer identifies missing dependencies and prompts for their installation.
- [ ] All required dependencies are correctly installed alongside the target skill.
- [ ] Circular dependencies are detected and handled with an error message.
- [ ] Failed dependency installation halts the main skill's installation.

## Out of Scope
- Version constraints for dependencies (e.g., `skill-a >= 1.2.0`). For now, we only care about the existence of the skill.
- Automatic removal of orphaned dependencies (will be considered in a separate track if needed).
