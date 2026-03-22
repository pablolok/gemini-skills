# Specification: Subagent Balancer & Skill Manager Review

## Overview
This track involves three main objectives: 
1. Reviewing and improving the `subagent-balancer` skill to ensure better routing and context management.
2. Updating the `install.py` script to clearly show when an update is available for an installed skill, including the version difference.
3. Updating the `skill-manager` documentation to explain the existence of the `post_install.py` hook, the different ways of updating skills, and how to check for updates.

## Functional Requirements
- **`install.py` Update:**
  - Modify the interactive skill selection menu in `install.py`.
  - When an installed skill has an update available, its status string should be formatted as: `[Update Available] (vX -> vY)` (where vX is the installed version and vY is the latest version).
  - The latest version should be fetched from the updates data structure.
- **`subagent-balancer` Review & Enhancement:**
  - **Enhance Prompt Instructions:** Improve the instructions given to the LLM to better choose between generalist and specialized subagents.
  - **Token/Context Awareness:** Ensure the balancer considers context windows and limits when routing tasks.
  - **General Review & Tweaks:** Conduct a general review of the skill's logic and make minor optimizations without major restructuring.
- **`skill-manager` Documentation Update:**
  - Update `skills/skill-manager/SKILL.md` to document the existence and purpose of the `post_install.py` hook.
  - Detail the commands and processes for checking for skill updates and applying them (e.g., using `python install.py`, `python check_updates.py`).

## Non-Functional Requirements
- Maintain backward compatibility with existing skill installations.
- Keep the CLI output readable and professional.

## Out of Scope
- Adding new features to the skill installer beyond the version display change.
- Creating new skills.