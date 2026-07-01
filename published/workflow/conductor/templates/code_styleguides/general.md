# General Code Style Guide

> Cross-language conventions for this project. Add per-language guides beside this file
> (e.g. `python.md`, `csharp.md`, `typescript.md`) as needed.

## Naming
- Use clear, intention-revealing names. Match the surrounding code's conventions.

## Structure
- Keep functions small and single-purpose. Favor composition over duplication.
- New code should read like the code already around it.

## Comments & Docs
- Document public APIs. Comment the *why*, not the *what*.

## Errors
- Fail fast with actionable messages. Never swallow errors silently.

## Tests
- Every code module has tests. Cover success and failure paths. Mock external dependencies.
