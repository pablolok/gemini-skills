# AGENTS.md

This repository is skill-driven. When a task matches an installed repo-local skill, use that skill instead of handling the workflow manually.

## Mandatory Routing

- If the user asks to `publish`, `sync`, `republish`, or otherwise update `published/`, use `skill-publisher`.
- Do not edit `published/` manually to satisfy a publish request. Publish from `skills/` through the publisher flow.
- If a task involves skill installation, updates, Codex bridge setup, Claude reference-skill setup, or managed `.gitignore` behavior, use `skill-manager`.
- If a task involves changelog normalization or version-entry cleanup, use `changelog-manager` before publishing when needed.

## Gitignore Guardrail

- Never rewrite the full project `.gitignore` when working on `skill-manager`.
- Only add or replace the lines inside the `# >>> skill-manager managed workspace files >>>` and `# <<< skill-manager managed workspace files <<<` markers.
- Preserve all `.gitignore` content outside that managed block exactly as-is.
- If the current edit path would replace, truncate, regenerate, or otherwise rewrite the full `.gitignore`, stop and fix the implementation instead of touching the file.
- Before any commit or push involving installer or `skill-manager` changes, re-read `.gitignore` from disk and verify that non-`skill-manager` baseline content is still present.

## Usable Repo Skills

These repo-local skills are expected to be usable when their task type matches:

- `changelog-manager`
- `compliance-audit-angular`
- `compliance-audit-avalonia`
- `compliance-audit-c#`
- `compliance-audit-orchestrator`
- `compliance-audit-scripts`
- `compliance-audit-verification-gates`
- `conductor-workflow-optimization`
- `pre-implementation-review`
- `review-optimization`
- `skill-manager`
- `skill-publisher`
- `subagent-balancer`
- `subagent-balancer-api`
- `subagent-balancer-orchestrator`

## Shared Vs Tool-Specific Skills

- Use `install.config.json` as the source of truth for installer-facing skill scope.
- Treat skills marked `distribution: "shared"` as normal cross-tool skills.
- Treat skills marked `distribution: "gemini-only"` as Gemini-specific skills that should not automatically be treated as Codex bridge or Claude reference candidates.
- The balancer family is Gemini-only unless a future task explicitly adds real cross-tool integration for it.

## Publish Expectations

- Treat `skills/` as the source of truth.
- Keep `skills/<skill>/metadata.json`, `CHANGELOG.md`, `README.md`, and `SKILL.md` aligned before publishing.
- Let the publish flow update metadata/changelog versions and copy to `published/`.
- After publishing, verify any related Codex bridge wrappers in `.codex/skills/` still accurately describe the Gemini skill they bridge.

## Audit Expectations

- If a task changes code and a compliance audit skill applies, route through the matching specialized audit or the orchestrator.
- Do not update audit rules inside `published/` directly; change the source skill and publish it.
