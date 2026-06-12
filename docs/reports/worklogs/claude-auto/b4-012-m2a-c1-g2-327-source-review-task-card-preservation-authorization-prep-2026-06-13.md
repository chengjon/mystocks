# B4.012-M2a-C1 g2-327 Source-Review Task-Card Preservation Authorization Prep

Date: 2026-06-13

## Scope

This package prepares authorization only. It does not preserve, delete, migrate, or modify the task-card itself.

Future implementation candidate:

- `governance/mainline/task-cards/g2-327.yaml`

Explicitly excluded:

- source, test, runtime, API, route, OpenSpec, ST-HOLD, marketKlineData, `docs/guides/**`, `docs/superpowers/**`, and all external dirty files
- `web/backend/app/api/technical_analysis.py`
- `tests/api/file_tests/test_technical_analysis_api.py`
- any source-level review of the technical_analysis DataSourceFactory provider
- any deletion or retirement of `g2-327.yaml`

## Baseline

- Branch: `wip/root-dirty-20260403`
- HEAD: `f9d514245aabbb0be423ac3d8baace4a8b95e50b`
- Staged changes: empty before this authorization-prep package
- Residual task-card state: `governance/mainline/task-cards/g2-327.yaml` remains untracked and intentionally untouched

## Evidence Summary

The preceding no-source disposition audit classified `g2-327.yaml` as high-risk governance evidence rather than low-risk task-card residue.

Extracted task-card signals:

- title: `Implement technical_analysis DataSourceFactory provider`
- status: `source_implementation_review_required`
- approval status: `approved`
- review status: `reviewed-but-not-merged`
- phase: `phase_b_dual_hard_gate`
- next gate if accepted: `G2.328 technical_analysis DataSourceFactory provider closeout / residual refresh`
- referenced implementation report archived at `archive/docs/reports/quality/backend-technical-analysis-datasourcefactory-provider-implementation-2026-06-03.md`

The archived report confirms that this task-card belongs to a historical source-review lane, but it does not prove current source correctness. Any current technical_analysis source truth review requires a separate source-authorized package.

## Authorization Decision Prepared

Recommended next implementation package:

- `B4.012-M2a-C1 g2-327 source-review task-card preservation implementation`

Recommended implementation scope:

- preserve only `governance/mainline/task-cards/g2-327.yaml`
- update only the required FUNCTION_TREE closeout and worklog artifacts for this C1 node

Recommended non-goals:

- no source or test edits
- no technical_analysis implementation review
- no API, route, runtime, adapter, or data-flow behavior changes
- no deletion, retirement, rename, or content normalization of the task-card
- no OpenSpec, ST-HOLD, marketKlineData, `docs/guides/**`, `docs/superpowers/**`, or external dirty files

## Required Gates

Any follow-up implementation must pass:

- exact staged allowlist
- `git diff --cached --check`
- GitNexus staged verification
- GitNexus staged detect-changes
- OPENDOG blocker check
- post-commit GitNexus index refresh

## Current Status

`source_edits_authorized: false`

This authorization-prep package does not authorize staging or preserving `governance/mainline/task-cards/g2-327.yaml`. That requires explicit user approval for the implementation package named above.
