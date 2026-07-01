---
description: Bootstrap the Conductor workspace (product, guidelines, tech-stack, workflow, tracks) for this project.
argument-hint: "[optional notes about the product/stack]"
---

You are running `/conductor:setup` — the one-time bootstrap for Context-Driven Development.

Extra context from the user (may be empty): $ARGUMENTS

## Goal

Create the `conductor/` workspace so the repository itself holds the project context. Do NOT
overwrite files that already exist — merge or ask before changing them.

## Steps

1. **Detect greenfield vs brownfield.** Inspect the repo: read `README.md`, manifests
   (`package.json`, `*.csproj`, `pyproject.toml`, `go.mod`, etc.), the directory layout, and
   recent `git log`. Decide whether this is a new project (greenfield) or an existing one
   (brownfield).

2. **Check for an existing workspace.** If `conductor/` already exists, tell the user and ask
   (via `AskUserQuestion`) whether to fill only missing files, refresh a specific file, or
   stop. Never clobber existing context silently.

3. **Scaffold the workspace.** Create these files if missing, using
   `.claude/skills/conductor/templates/` as the starting point and filling them in from what
   you learned in step 1:
   - `conductor/index.md` — links to the files below.
   - `conductor/product.md` — who the product is for, goals, key features.
   - `conductor/product-guidelines.md` — prose/brand/UX standards.
   - `conductor/tech-stack.md` — languages, frameworks, tools. Deviations must be documented
     here **before** implementation.
   - `conductor/workflow.md` — the TDD/commit/checkpoint/audit protocol. Copy the template
     verbatim, then adapt the **Development Commands** section to this project's real
     setup/test/lint/build commands.
   - `conductor/tracks.md` — the (initially empty) tracks registry.
   - `conductor/code_styleguides/` — style guides per language actually used.

4. **For brownfield projects**, infer `product.md` and `tech-stack.md` from the code and
   confirm the summary with the user before writing.

5. **Confirm and commit.** Show the user what was created, then stage and commit with
   `chore(conductor): Bootstrap Conductor workspace`.

6. **Point the way forward.** Tell the user to run `/conductor:new-track` to start their first
   piece of work.
