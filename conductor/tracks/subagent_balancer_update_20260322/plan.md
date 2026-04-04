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
- [x] Task: Update the instructions in `subagent-balancer` SKILL.md to explicitly route tasks based on token limits and context awareness. 10a9949
- [x] Task: Enhance the prompt instructions for choosing between generalist and specialized subagents. 10a9949
- [x] Task: Update `scripts/select_model.py` to support modern Gemini models (1.5, 2.0) and refine scoring for better quota preservation. 10a9949
- [x] Task: Add a "Quota Awareness Checklist" and "Prompt Caching Advice" to `subagent-balancer/SKILL.md`. 10a9949
- [x] Task: Perform general review, tweaking phrasing and formatting for clarity and optimizing logic. 10a9949
- [x] Task: Conductor - User Manual Verification 'Phase 3: Enhance `subagent-balancer` Skill' (Protocol in workflow.md)

## Phase 4: Update `skill-manager` Documentation
- [x] Task: Update `skills/skill-manager/SKILL.md` to include documentation on the `post_install.py` hook. 10a9949
- [x] Task: Update `skills/skill-manager/SKILL.md` to explain how to update skills and check for updates. 10a9949
- [x] Conductor - User Manual Verification 'Phase 4: Update `skill-manager` Documentation' (Protocol in workflow.md)

## Phase 5: Final Integration and Testing [checkpoint: dfaba56]
- [x] Task: Run the `install.py` script locally to verify visual output of updates.
- [x] Task: Verify the updated `subagent-balancer` skill prompt syntax.
- [x] Task: Verify model selection scoring and parsing fixes.
- [x] Conductor - User Manual Verification 'Phase 5: Final Integration and Testing' (Protocol in workflow.md)

## Phase 6: Automation for Skill Publishing [checkpoint: 0960c97]
- [x] Task: Create `automate_publish.py` to automate the publishing checklist (copy, version bump, changelog).
- [x] Task: Update `skill-publisher/SKILL.md` to reference the new script.
- [x] Task: Verify the script by publishing `subagent-balancer` one last time.
- [x] Conductor - User Manual Verification 'Phase 6: Automation for Skill Publishing' (Protocol in workflow.md)

# Track Finalization [checkpoint: 73b29f0]
- [x] All tasks completed and verified.
- [x] Documentation synchronized.
- [x] Feature branch merged to main.
