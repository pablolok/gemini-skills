# Conductor Compliance Audit Skill (Angular)

A specialized Gemini skill for Angular compliance reviews.

## What It Checks

- Angular component/service/template best practices
- TypeScript strictness and maintainability
- accessibility and semantic markup
- Angular testing and coverage expectations
- styling discipline and UI architecture boundaries
- duplicated UI patterns that should become generic reusable components, directives, or shared primitives

## Typical Trigger

Use this when a phase changes Angular files such as:

- component or service `.ts` files
- Angular template `.html` files
- component `.scss` or `.css` files
- routing or shared Angular UI modules

especially when the project contains Angular markers like `angular.json` or `@angular/`.
