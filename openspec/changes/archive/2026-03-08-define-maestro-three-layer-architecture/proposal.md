# Define Maestro Three-Layer Architecture

## Why

The MyStocks runtime currently uses `Symphony` as the implementation name, but the runtime has now
grown into a broader local-first orchestration and multi-CLI automation system. A more durable
family name and extraction boundary are needed so the generic runtime and collaboration core can be
moved into a standalone tool later.

## What Changes

- Introduce `Maestro` as the recommended long-term runtime family name
- Seed a `src/services/maestro` compatibility namespace in the repository
- Define a three-layer architecture: `kernel`, `collab`, and `profiles`
- Keep `symphony` as the compatibility implementation path for now

## Impact

- Affected specs: `symphony-service`
- Affected code: `src/services/maestro/**`, `src/services/symphony/__init__.py`, `WORKFLOW.md`
- Affected docs: local workflow guide and Maestro architecture plans
