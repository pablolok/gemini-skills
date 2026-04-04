# Product Guidelines: Gemini CLI Skills

## Prose & Style
- **Technical & Concise**: Documentation and CLI feedback should be direct, objective, and information-dense, avoiding conversational filler or unnecessary fluff.
- **Clarity First**: Prioritize technical accuracy and clarity in all explanations and error messages.

## UX & Design Principles
- **Minimal Interruption**: The skills should operate autonomously whenever possible, avoiding unnecessary confirmation prompts to maintain a fast development loop.
- **Clear Feedback & Recovery**: When an error or ambiguity occurs, provide concise, actionable feedback with clear steps for recovery.
- **CLI Native**: Design all interactions to feel native to a terminal environment, focusing on text-based signals and status indicators.

## Architecture & Standards
- **Standard Skill Layout**: Adhere strictly to the established Gemini CLI skill structure (e.g., `README.md`, `SKILL.md`) to ensure consistent behavior across all skills in the collection.
- **Conductor Compatibility**: Maintain seamless integration with the Conductor workflow, ensuring that all automated updates (e.g., `workflow.md`) are accurate and follow established conventions.
