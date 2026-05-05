## General Design Instruction
- Use popular 3rd party libraries for non-business logic instead of implementing yourself.
- Prioritize readability and maintainability over performance.
- Refactor when code gets too complex or repeated.
- For ambiguous decisions, leave a TODO comment or clarify — do NOT guess.
- Be conservative. Expect code to be used directly without peer review.

## Avoid AI code slop

When you're generating code, be careful to avoid generating slop code, including but not limited to:

- Extra comments that a human wouldn't add or is inconsistent with the rest of the file. (But do not change existing comments)
- Extra defensive checks or try/catch blocks that are abnormal for that area of the codebase (especially if called by trusted / validated codepaths)
- Casts to any to get around type issues
- Any other style that is inconsistent with the file

## Writing Style
- Be direct
- State facts
- If unsure, say so
- Keep comments minimal and only where logic isn't obvious

