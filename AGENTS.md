# AGENTS.md

This repository is skill-driven. When a task matches an installed repo-local skill, use that skill instead of handling the workflow manually.

## Mandatory Routing

- If the user asks to `publish`, `sync`, `republish`, or otherwise update `published/`, use `skill-publisher`.
- Do not edit `published/` manually to satisfy a publish request. Publish from `skills/` through the publisher flow.
- If a task involves skill installation, updates, Codex bridge setup, Claude reference-skill setup, or managed `.gitignore` behavior, use `skill-manager`.
- If a task involves changelog normalization or version-entry cleanup, use `changelog-manager` before publishing when needed.

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

## Publish Expectations

- Treat `skills/` as the source of truth.
- Keep `skills/<skill>/metadata.json`, `CHANGELOG.md`, `README.md`, and `SKILL.md` aligned before publishing.
- Let the publish flow update metadata/changelog versions and copy to `published/`.
- After publishing, verify any related Codex bridge wrappers in `.codex/skills/` still accurately describe the Gemini skill they bridge.

## Audit Expectations

- If a task changes code and a compliance audit skill applies, route through the matching specialized audit or the orchestrator.
- Do not update audit rules inside `published/` directly; change the source skill and publish it.
