# Implementation Plan: Subagent Balancer & Skill Manager Review

## Phase 1: Setup and Context Verification [checkpoint: d4e105a]
- [x] Task: Review existing `install.py` logic for status rendering. 1a285ca
- [x] Task: Review the current `skills/subagent-balancer/SKILL.md` content and prompt. 6a3324c
- [x] Task: Review the current `skills/skill-manager/SKILL.md` to identify where to add new documentation. ad25d57
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup and Context Verification' (Protocol in workflow.md)

## Phase 2: Update `install.py` Version Display [checkpoint: 94bcd5e]
- [x] Task: Write test/script to verify the status string formatting in `install.py`. b6f0ea8
- [x] Task: Implement change in `SkillSelector.select_skills` to format update strings as `[Update Available] (vX -> vY)`. b6f0ea8
- [x] Task: Run tests to verify the UI string formatting. b6f0ea8
- [x] Task: Conductor - User Manual Verification 'Phase 2: Update `install.py` Version Display' (Protocol in workflow.md)

## Phase 3: Enhance `subagent-balancer` Skill [checkpoint: 74eda1f]
- [x] Task: Update the instructions in `subagent-balancer` SKILL.md to explicitly route tasks based on token limits and context awareness.
- [x] Task: Enhance the prompt instructions for choosing between generalist and specialized subagents.
- [x] Task: Perform general review, tweaking phrasing and formatting for clarity and optimizing logic. 10a9949
- [x] Task: Conductor - User Manual Verification 'Phase 3: Enhance `subagent-balancer` Skill' (Protocol in workflow.md)

## Phase 4: Update `skill-manager` Documentation
- [~] Task: Update `skills/skill-manager/SKILL.md` to include documentation on the `post_install.py` hook.
- [~] Task: Conductor - User Manual Verification 'Phase 3: Enhance `subagent-balancer` Skill' (Protocol in workflow.md)
- [ ] Task: Enhance the prompt instructions for choosing between generalist and specialized subagents.
- [ ] Task: Perform general review, tweaking phrasing and formatting for clarity and optimizing logic.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Enhance `subagent-balancer` Skill' (Protocol in workflow.md)

## Phase 4: Update `skill-manager` Documentation
- [ ] Task: Update `skills/skill-manager/SKILL.md` to include documentation on the `post_install.py` hook.
- [ ] Task: Update `skills/skill-manager/SKILL.md` to explain how to update skills and check for updates.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Update `skill-manager` Documentation' (Protocol in workflow.md)

## Phase 5: Final Integration and Testing
- [ ] Task: Run the `install.py` script locally to verify visual output of updates.
- [ ] Task: Verify the updated `subagent-balancer` skill prompt syntax.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Final Integration and Testing' (Protocol in workflow.md)