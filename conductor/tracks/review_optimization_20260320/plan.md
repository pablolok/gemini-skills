# Implementation Plan: Post-Execution Review & Optimization Skill

## Phase 1: Foundation & Integration [checkpoint: 669ac12]
- [x] **Task: Conductor - Setup Track Artifacts (metadata, index, spec, plan)** 49dcf71
- [x] **Task: Write TDD - Basic Skill Skeleton and Metadata** 6bd85a0
- [x] **Task: Implement - `SKILL.md` and basic trigger mechanism** 04f235e
- [x] **Task: Write TDD - Skill Activation within Checkpoint Protocol** 28e88b2
- [x] **Task: Implement - Integration with `workflow.md` checkpoint steps** 7660962
- [x] **Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)** 669ac12

## Phase 2: Execution Analysis & Detection [checkpoint: 4174949]
- [x] **Task: Write TDD - Tool Call Log Parsing and Reconstruct Path** a4a9fad
- [x] **Task: Implement - Analyzer to parse session history and identify tool sequences** a4a9fad
- [x] **Task: Write TDD - Skill Efficiency Detection (Missed or Badly Written Skills)** d403f5b
- [x] **Task: Implement - Logic to cross-reference history with available skills and metadata** d403f5b
- [x] **Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)** 4174949

## Phase 3: Workflow Optimization & Advice [checkpoint: 8e6ef1d]
- [x] **Task: Write TDD - Workflow vs. Plan Comparison** 0033ea4
- [x] **Task: Implement - Optimization Advisor to compare actual path with `plan.md`** 0033ea4
- [x] **Task: Write TDD - Suggesting Alternative Tool Sequences** 6a14b5e
- [x] **Task: Implement - Recommendation engine based on project tech stack** 6a14b5e
- [x] **Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)** 8e6ef1d

## Phase 4: Interactive Remediation & Final E2E
- [x] **Task: Write TDD - Interactive Prompting via `ask_user`** 8e3c172
- [x] **Task: Implement - Remediation UI/Flow for detected issues** 8e3c172
- [x] **Task: Write TDD - 'Propose New Skill' Detection & Creation Initiation** 95fe1e5
- [x] **Task: Implement - Logic to suggest and initiate new skill creation via `ask_user`** 95fe1e5
- [x] **Task: Write TDD - End-to-End Skill Validation (Mock Execution)** f1cf06d
- [x] **Task: Implement - Full E2E test suite for the new skill** f1cf06d
- [ ] **Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)**
