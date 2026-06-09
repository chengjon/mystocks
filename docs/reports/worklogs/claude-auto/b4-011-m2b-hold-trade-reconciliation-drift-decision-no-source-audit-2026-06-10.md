# B4.011-M2b-HOLD trade reconciliation drift decision no-source audit

Date: 2026-06-10

## Scope

This no-source audit covers only:

- `docs/superpowers/specs/2026-05-06-trade-reconciliation-statement-design.md`
- `archive/docs/superpowers/specs/2026-05-06-trade-reconciliation-statement-design.md`

It does not authorize source, test, runtime, route, UI, API, `docs/guides`, or
other `docs/superpowers` changes.

## Current State

- Active file status: clean after restore.
- Archive file exists but is ignored/untracked.
- Active and archive copies both have 471 lines.
- Active size: 16435 bytes.
- Archive size: 16684 bytes.
- Content hashes differ.
- Tracked references outside `docs/superpowers/**` and `archive/**`: none for the path or basename.

## Drift

Only two line positions differ.

Line 16:

- Active: `Support multi-account switching for reconciliation workflows.`
- Archive: `Support multi-account switching via a first-batch account-descriptor contract (GET /api/trade/reconciliation/accounts), not by assuming the current /trades endpoint already exposes account-aware filtering.`

Line 43:

- Active: `multi-account switching`
- Archive: `multi-account switching via a new first-batch account-descriptor contract (not reusing existing /trades account filtering)`

## Consistency Check

The archive drift is consistent with the active document body:

- Active line 98 already states the account switcher is backed by the new
  reconciliation account-descriptor contract and must not assume the current
  `/api/trade/trades` endpoint exposes an account-filterable UI surface.
- Active lines 141 and 158 already list
  `GET /api/trade/reconciliation/accounts`.
- Git history for the active file includes
  `docs(spec): clarify reconciliation account contract`.

Therefore the archive variant does not introduce a new product direction; it
brings the summary/acceptance wording into alignment with the existing detailed
body.

## Decision

Recommended disposition:

- Accept the archive variant as the corrected archived copy.
- Retire the active `docs/superpowers` file in a separate deletion-retirement
  package.
- Stage the active deletion and `git add -f` the ignored archive copy.
- Do not modify runtime/API/source/test behavior.

Risk:

- Documentation-only.
- No tracked external references.
- The drift is bounded to two summary/acceptance lines and aligns with the same
  document's detailed contract section.

## Required Gates

- Exact path-scoped staged list.
- `git diff --cached --check`.
- GitNexus `verify-staged`.
- GitNexus `detect-changes --scope staged`.
- OPENDOG freshness.
- Post-commit GitNexus index refresh.
