# Add Maestro Owner Suggestion

## Why

The main CLI is still responsible for deciding task ownership, but that decision currently depends on
manual reading of `.FILE_OWNERSHIP`, `TASK.md`, and path/module context. A conservative suggestion
layer can reduce repetitive work without removing the main CLI's final authority.

## What Changes

- Add a rule-based owner suggestion engine
- Use `.FILE_OWNERSHIP` and task path hints to rank likely owners
- Expose the suggestion engine through the Maestro collab CLI
- Keep assignment as an explicit operator action

## Impact

- Affected specs: `symphony-service`
- Affected code: `src/services/maestro/collab/**`, `scripts/runtime/maestro_collab.py`
