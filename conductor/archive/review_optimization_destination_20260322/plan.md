# Implementation Plan: Skill Destination Selection for Review Optimization

## Phase 1: Core Logic & Tests
- [x] **Task: Setup Track Artifacts (metadata, index, spec, plan)** f63c1ad
- [x] **Task: Write TDD - Update `test_proposer.py` for destination choice menu** f63c1ad
    - [x] Update `test_propose_new_skill_detects_recurring_shell_commands` to expect the new choice menu options.
    - [x] Add new test `test_custom_path_auto_creation` to verify directory creation logic.
- [x] **Task: Implement - Update `proposer.py`** f63c1ad
    - [x] Refactor `ask_user_fn` call to use `choice` type with Global, Local, and Custom Path options.
    - [x] Add logic to handle the "Custom Path" response, including a secondary `ask_user` prompt if needed.
    - [x] Add `os.makedirs` logic to auto-create the custom path if it doesn't exist.
- [x] **Task: Write TDD - Update `test_review_optimization_e2e.py`** f63c1ad
    - [x] Update the E2E mock `ask_user` responses to handle the new choice structure.
- [~] **Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)**

## Phase 2: Documentation & Finalization
- [x] **Task: Implement - Update `SKILL.md`** 8f12065
    - [x] Revise the "Interactive Remediation" section to document the Global/Local/Custom Path selection options.
- [~] **Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)**