# B4.012-M2a-B Task-Card Preservation Authorization Prep

Date: 2026-06-12

## Scope

This package prepares authorization for governance task-card preservation only.

Included review set:

- `governance/mainline/task-cards/g2-322.yaml`
- `governance/mainline/task-cards/g2-323.yaml`
- `governance/mainline/task-cards/g2-324.yaml`
- `governance/mainline/task-cards/g2-325.yaml`
- `governance/mainline/task-cards/g2-326.yaml`
- `governance/mainline/task-cards/g2-328.yaml`
- `governance/mainline/task-cards/g2-329.yaml`
- `governance/mainline/task-cards/pr-474.yaml`

Explicitly excluded from this batch:

- `governance/mainline/task-cards/g2-327.yaml`
- source, test, runtime, API, route, OpenSpec, ST-HOLD, marketKlineData, `docs/guides/**`, `docs/superpowers/**`, and any external dirty files

## Observed State

- Branch: `wip/root-dirty-20260403`
- HEAD: `89a8856d2 B4.012-M2a-A: close catalog preservation node`
- Staged changes: empty
- Governance task-card residuals: 9 untracked files under `governance/mainline/task-cards/`

## Task-Card Classification

Low-risk preservation candidates:

- `g2-322.yaml`: accepted merged, no-source upkeep, watchlist DataSourceFactory residual lane
- `g2-323.yaml`: accepted merged, no-source upkeep, steward surface compaction
- `g2-324.yaml`: accepted merged, no-source ownership decision, residual candidate selection
- `g2-325.yaml`: accepted merged, no-source technical_analysis ownership classification
- `g2-326.yaml`: accepted merged, no-source provider preflight
- `g2-328.yaml`: accepted reviewed no-source, lane closeout
- `g2-329.yaml`: accepted reviewed no-source, branch-anchor reconciliation
- `pr-474.yaml`: accepted merged watchlist provider injection evidence

High-risk isolated candidate:

- `g2-327.yaml`: `source_implementation_review_required`
- This card is not eligible for the low-risk preservation batch
- It requires a separate review-oriented authorization before any preservation or implementation decision

## Decision

The 8 low-risk cards are suitable for a single preservation authorization batch.

`g2-327.yaml` must stay outside this batch because it explicitly requires source implementation review and carries higher governance risk than the accepted no-source cards.

This worklog prepares the boundary only. No task-card file is staged, preserved, moved, or committed here.

## Requested Follow-Up Authorization

Request `B4.012-M2a-B task-card preservation implementation` authorization with this exact implementation scope:

- Preserve the 8 low-risk task-card files listed above
- Update only required FUNCTION_TREE closeout/worklog artifacts for this node

Forbidden for that implementation package unless separately authorized:

- `governance/mainline/task-cards/g2-327.yaml`
- source, test, runtime, API, route, OpenSpec, ST-HOLD, marketKlineData, `docs/guides/**`, `docs/superpowers/**`
- any broad dirty cleanup or unrelated staged files

## Required Gates

Before any implementation commit:

- Exact staged allowlist
- `git diff --cached --check`
- GitNexus staged verification
- GitNexus staged detect-changes
- OPENDOG blockers check
- Post-commit GitNexus index refresh

## Current Status

`source_edits_authorized: false`

This report prepares the authorization boundary only.
