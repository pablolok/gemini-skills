# Pre-Implementation Review

Use this skill before coding to decide whether planned work should reuse an existing abstraction, extend one, or create a new reusable component/service/helper up front.

## What It Checks

- existing code that already solves part of the request
- whether a new feature should extend current abstractions instead of adding parallel code
- whether a reusable component, control, service, helper, validator, or template should be created before implementation
- duplication risks that are obvious during planning
- file ownership and test boundaries for the planned abstraction

## Typical Trigger

Use this when a request is still in the reasoning or planning phase, especially for:

- UI features that may repeat across screens
- shared backend or service logic
- validators, mappers, request builders, or orchestration flows
- refactors where the developer should decide reuse strategy before writing code
