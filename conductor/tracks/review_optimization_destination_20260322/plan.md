# Implementation Plan: Skill Destination Selection for Review Optimization

## Phase 1: Core Logic & Tests
- [ ] **Task: Setup Track Artifacts (metadata, index, spec, plan)**
- [ ] **Task: Write TDD - Update `test_proposer.py` for destination choice menu**
    - [ ] Update `test_propose_new_skill_detects_recurring_shell_commands` to expect the new choice menu options.
    - [ ] Add new test `test_custom_path_auto_creation` to verify directory creation logic.
- [ ] **Task: Implement - Update `proposer.py`**
    - [ ] Refactor `ask_user_fn` call to use `choice` type with Global, Local, and Custom Path options.
    - [ ] Add logic to handle the "Custom Path" response, including a secondary `ask_user` prompt if needed.
    - [ ] Add `os.makedirs` logic to auto-create the custom path if it doesn't exist.
- [ ] **Task: Write TDD - Update `test_review_optimization_e2e.py`**
    - [ ] Update the E2E mock `ask_user` responses to handle the new choice structure.
- [ ] **Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)**

## Phase 2: Documentation & Finalization
- [ ] **Task: Implement - Update `SKILL.md`**
    - [ ] Revise the "Interactive Remediation" section to document the Global/Local/Custom Path selection options.
- [ ] **Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)**