# Implement File Directory Migration

## Why

MyStocks accumulated severe directory-structure drift during rapid growth. The repository root contains
far more files than the intended policy allows, related files are scattered across inconsistent folders,
and existing directory rules are documented but not enforced consistently. This reduces maintainability,
increases onboarding cost, and makes automation harder to trust.

## What Changes

- Migrate files from non-canonical locations into governed directories with a gradual, auditable process
- Add and enforce directory-structure checks through existing automation entrypoints
- Normalize documentation, scripts, and source-code layout around approved taxonomy and boundaries
- Document migration decisions, risks, rollback strategy, and validation expectations

## Impact

- Affected specs: `file-organization`
- Affected code: repository structure, directory governance scripts/hooks, and related documentation/indexes
