# Project Workflow

> This is the Conductor workflow protocol for Claude Code. `/conductor:implement` follows it
> exactly. Adapt the **Development Commands** section to your project; the lifecycle protocol
> below should stay intact.

## Guiding Principles

1. **The Plan is the Source of Truth:** All work is tracked in the track's `plan.md`.
2. **The Tech Stack is Deliberate:** Changes to the stack are documented in `tech-stack.md`
   *before* implementation.
3. **Test-Driven Development:** Write failing tests before implementing functionality.
4. **High Code Coverage:** Aim for >80% coverage for new code.
5. **User Experience First:** Every decision should prioritize the end user.
6. **Non-Interactive & CI-Aware:** Prefer non-interactive commands. Use `CI=true` for
   watch-mode tools (tests, linters) so they run once and exit.
7. **Shell Portability Before Alias Convenience:** When Claude invokes shell commands, prefer
   commands that match the active shell. In PowerShell, avoid Unix-style alias patterns like
   multi-path `ls`; use shell-native commands or one path per command.

## Standard Task Workflow

Each task follows a strict lifecycle:

0. **Check for Skill Updates:** Periodically run `/skill-manager:update` (or
   `python check_updates.py` from the `claude-skills` repo) to keep installed skills current.

1. **Select Task:** Choose the next `[ ]` task from `plan.md` in sequential order.

2. **Mark In Progress:** Change the task from `[ ]` to `[~]` in `plan.md`.

3. **Run Pre-Implementation Review:** Invoke the `pre-implementation-review` skill before
   writing tests or code. Use it to find reuse opportunities, extension points, and shared
   abstractions. If it changes the implementation boundary, update the current phase tasks in
   `plan.md` first.

4. **Write Failing Tests (Red):** Create test(s) that define the expected behavior and
   acceptance criteria. Run them and **confirm they fail** before proceeding.

5. **Implement to Pass Tests (Green):** Write the minimum code to make the tests pass. Rerun
   the suite and confirm all tests pass.

6. **Refactor (recommended):** With tests green, improve clarity and remove duplication without
   changing behavior. Rerun tests.

7. **Verify Coverage:** Run the project's coverage tool. Target >80% for new code.

8. **Document Deviations:** If implementation differs from `tech-stack.md`: STOP, update
   `tech-stack.md` with a dated note, then resume.

9. **Commit Code Changes:** Stage the task's changes and commit with a clear Conventional
   Commits message, e.g. `feat(ui): Create basic HTML structure for calculator`.

10. **Attach Task Summary with Git Notes:**
    - Get the commit hash: `git log -1 --format="%H"`.
    - Draft a summary (task name, changes, created/modified files, the core "why").
    - Attach it: `git notes add -f -m "<note content>" <commit_hash>`.

11. **Record Task Commit SHA:** In `plan.md`, change the task `[~]` → `[x]` and append the
    first 7 characters of the commit hash.

12. **Commit Plan Update:** Stage `plan.md` and commit, e.g.
    `conductor(plan): Mark task 'Create user model' as complete`.

## Phase Completion Verification and Checkpointing Protocol

**Trigger:** immediately after a task completes that also concludes a phase in `plan.md`.

1. **Announce Protocol Start:** Tell the user the phase is complete and verification has begun.

2. **Ensure Test Coverage for Phase Changes:**
   - Find the previous phase checkpoint SHA in `plan.md` (or the first commit if none).
   - `git diff --name-only <previous_checkpoint_sha> HEAD` to list changed files.
   - For each **code** file (exclude `.json`, `.md`, `.yaml`, etc.), verify a test exists;
     create one if missing, matching the repo's existing test conventions.

3. **Execute Automated Tests and Compliance Audits:**
   - **Automated Tests:** Announce the exact command, then run it (e.g. `npm test` with
     `CI=true`).
   - **Compliance Audit Orchestration:** Apply the `subagent-balancer` policy whenever an audit
     may delegate review work. If the user explicitly chose a model tier, honor it — do not
     silently downgrade. Then invoke `compliance-audit-orchestrator`: it runs
     `compliance-audit-verification-gates` first for code changes, then the specialized audits
     for the changed stack. Required build/compile/bundle/packaging gates must pass without
     warnings unless the repo documents an allowed exception.
   - **Post-Execution Review:** Invoke `review-optimization` to audit the phase's execution and
     propose workflow refinements.
   - **Workflow Drift Audit:** If Claude Code reports an unexpected tool call, a missing tool,
     or the CLI contradicts the workflow text, invoke `conductor-workflow-optimization` before
     retrying.
   - **Error Handling:** If tests fail, audits report persistent violations, or the review finds
     critical drift, inform the user and debug. Propose a fix at most **twice**; if it still
     fails, stop and ask for guidance.

4. **Propose a Manual Verification Plan:** From `product.md`, `product-guidelines.md`, and
   `plan.md`, generate concrete, step-by-step manual-verification instructions with exact
   commands and expected outcomes (frontend: server command + URL + what to see; backend:
   request + expected response).

5. **Await Explicit User Feedback:** Present the plan and ask with `AskUserQuestion`
   (header "Verify", options `yes` / `no` / free-text). **PAUSE** until the user confirms.
   Address `no`/feedback and repeat.

6. **Create Checkpoint Commit:** Stage all changes (empty commit if none) and commit, e.g.
   `conductor(checkpoint): Checkpoint end of Phase X`.

7. **Attach Verification Report via Git Notes:** Draft a report (test command, manual steps,
   user confirmation) and attach it with `git notes add -f` to the checkpoint commit.

8. **Record Phase Checkpoint SHA:** Get the checkpoint hash and append `[checkpoint: <sha>]`
   (first 7 chars) to the phase heading in `plan.md`.

9. **Commit Plan Update:** Stage `plan.md` and commit,
   `conductor(plan): Mark phase '<PHASE NAME>' as complete`.

10. **Announce Completion:** Tell the user the checkpoint was created with the report attached
    as a git note.

## Track Finalization and Cleanup Protocol

**Trigger:** after all phases in the track's `plan.md` are complete and verified.

1. **Announce Finalization.**
2. **Synchronize Project Documentation:** Update `product.md`, `tech-stack.md`, etc. to reflect
   the delivered work.
3. **Merge to Main:** Ensure tests pass on the branch, then merge the feature branch into the
   main branch and push. Resolve conflicts with the user if any arise.
4. **Mark Track Completed:** Set the track's status to `[x]` in `conductor/tracks.md`.
5. **Commit Track Completion:** `chore(conductor): Mark track '<description>' as complete`.
6. **Cleanup Track:** Ask the user (via `AskUserQuestion`) to Archive, Delete, or Skip the
   track folder.

## Quality Gates

Before marking any task complete, verify:

- [ ] All tests pass
- [ ] Code coverage meets requirements (>80% for new code)
- [ ] Code follows the project's style guides (`code_styleguides/`)
- [ ] Public functions/methods are documented
- [ ] Type safety is enforced where the language supports it
- [ ] No linting or static-analysis errors
- [ ] Required builds/compiles/bundles succeed without warnings unless explicitly allowed
- [ ] Documentation updated if needed
- [ ] No security vulnerabilities introduced

## Development Commands

**ADAPT THIS SECTION to your project's language, framework, and tools.**

### Setup
```bash
# e.g. npm install  |  go mod tidy  |  pip install -e .
```

### Daily Development
```bash
# e.g. npm run dev  |  npm test  |  npm run lint
```

### Before Committing
```bash
# e.g. npm run check  |  make check
```

## Commit Guidelines

Format: `<type>(<scope>): <description>` with types `feat`, `fix`, `docs`, `style`,
`refactor`, `test`, `chore`. Conductor bookkeeping commits use the `conductor` type/scope
(e.g. `conductor(plan): ...`, `conductor(checkpoint): ...`).

## Definition of Done

A task is complete when: code implemented to spec; tests written and passing; coverage met;
docs updated if applicable; lint/static analysis clean; implementation notes in `plan.md`;
changes committed with a proper message; and a git note with the task summary attached.
