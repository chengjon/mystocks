# Change: Tech Debt Governance Baseline (2026Q1)

## Why
Technical debt tracking exists but lacks a single source of truth, clear ownership, and execution cadence. This change establishes a governance baseline with measurable artifacts so debt work can be planned and verified.

## What Changes
- Define an architecture source-of-truth document for authoritative references.
- Introduce a spec conflict matrix with explicit statuses and owners.
- Establish a debt register with owner/DDL/next-action fields.
- Create execution artifacts (TASK board and reports) to drive weekly cadence.
- Add an OpenSpec capability delta for architecture governance requirements.

## Impact
- Affected specs: `architecture-governance` (new)
- Affected docs: `technical_debt/governance/*`, `TASK*.md`
- No runtime behavior changes in this proposal.
