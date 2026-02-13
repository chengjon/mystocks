# Change: Update ArtDeco Design System Governance

## Why
ArtDeco design governance currently drifts across implementation and documentation:
- Token definitions, component guidance, and architecture documents are not enforced by a single governance baseline.
- Mixed wording (v2/v3) creates ambiguity for contributors and reviewers.
- Existing token checks do not sufficiently detect duplicate custom properties or reduce false positives.

This change establishes a practical single source of truth and automated checks so governance remains consistent as the frontend evolves.

## What Changes
- Add an ArtDeco governance manifest as the enforceable baseline for token, typography, spacing, and documentation references.
- Standardize core ArtDeco documentation language to the v3/v3.1 baseline and mark historical wording as archived context.
- Harden token governance checks with strict validation for duplicate custom properties, parser improvements, and configurable allowlists.
- Integrate governance checks into daily frontend verification workflow and developer guide.
- Add/extend unit tests that validate governance structure, doc consistency, token checks, and CLI script discoverability.

## Impact
- Affected specs: `artdeco-design-system` (new capability delta for governance requirements)
- Affected code:
  - `web/frontend/src/styles/`
  - `web/frontend/scripts/`
  - `web/frontend/tests/unit/styles/`
  - `web/frontend/tests/unit/scripts/`
  - `docs/guides/`
  - `docs/api/`
- Breaking changes: None
- Runtime business behavior: Unchanged (governance and consistency improvements only)
