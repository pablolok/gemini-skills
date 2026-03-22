# Implementation Plan: Skill Manager and 'Published' Directory

## Phase 1: 'Published' Folder & Categorization
- [ ] **Task: Setup Track Artifacts (metadata, index, spec, plan)**
- [ ] **Task: Create `published/` directory structure**
    - [ ] Create `published/` root.
    - [ ] Create categories: `audit/`, `workflow/`, `utility/`.
- [ ] **Task: Populate `published/` with existing stable skills**
    - [ ] Move/copy stable skills into appropriate categories.
- [ ] **Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)**

## Phase 2: Skill Selection and Junction Logic
- [ ] **Task: Write TDD - Test `SkillSelector` logic**
    - [ ] Verify it correctly lists skills from `published/` (mocked).
- [ ] **Task: Implement - `SkillSelector` class**
    - [ ] Logic to scan directories and build a list for `ask_user`.
- [ ] **Task: Write TDD - Test `SkillInstaller` (Junction logic)**
    - [ ] Verify it correctly generates the `mklink` command or uses the appropriate API.
- [ ] **Task: Implement - `SkillInstaller` class**
    - [ ] Handle junction creation (`mklink /J` on Windows).
    - [ ] Handle target directory creation if it doesn't exist.
- [ ] **Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)**

## Phase 3: Finalization & Documentation
- [ ] **Task: Implement - Update `README.md`**
    - [ ] Document the new skill installation process.
- [ ] **Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)**
