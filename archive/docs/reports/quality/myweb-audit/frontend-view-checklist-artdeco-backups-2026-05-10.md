# Frontend View Checklist: `views/artdeco-pages/*.backup*`

> Date: 2026-05-10
> Scope: backup-like root files under `web/frontend/src/views/artdeco-pages/`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `ArtDecoMarketData.vue.backup` | Vue backup snapshot | none found | no active source import found | docs mention the active `ArtDecoMarketData.vue`; backup file itself has no guard owner | `candidate-review/temp-backup/market-data-workbench` | `not-archive-approved` |
| `ArtDecoMarketData.vue.backup.20260130` | dated Vue backup snapshot | none found | no active source import found | docs mention the active `ArtDecoMarketData.vue`; backup file itself has no guard owner | `candidate-review/temp-backup/market-data-workbench-dated` | `not-archive-approved` |

## Evidence

- `wc -l` shows the active `ArtDecoMarketData.vue` is 335 lines, while `ArtDecoMarketData.vue.backup` is 3,179 lines and `ArtDecoMarketData.vue.backup.20260130` is 3,238 lines.
- `diff -q ArtDecoMarketData.vue.backup ArtDecoMarketData.vue.backup.20260130` reports that the two backup snapshots differ.
- Focused source search did not find active imports of either backup file.
- Existing docs and inventories discuss the active `ArtDecoMarketData.vue` and its split `market-data-tabs/*` children, not the backup filenames as runtime truth.
- `frontend-view-checklist-artdeco-root-pages-2026-05-10.md` keeps active `ArtDecoMarketData.vue` as `candidate-review/legacy-market-data-workbench`, not archive-approved.
- `frontend-view-checklist-artdeco-market-data-tabs-2026-05-10.md` keeps the child tabs and helper assets under review, with no archive approval.

## Functional Asset Assessment

- The backup files appear to be historical single-file snapshots of the market-data workbench before or during tab extraction.
- They are not current router/menu truth and should not be treated as active page implementations.
- Their size and old inline content suggest possible historical asset value, but that value must be compared against the active `ArtDecoMarketData.vue` plus `market-data-tabs/*` before any cleanup.
- The two backup snapshots differ, so they cannot be collapsed into a single duplicate decision without a deliberate comparison or explicit decision that historical backup retention is no longer needed.

## Redundant Page Decision

No file in this batch is archive-approved.

- These files are not active runtime pages, but `STANDARDS.md` forbids deleting or moving backup/temporary artifacts solely because static search finds no imports.
- Archive or removal requires an approved mutation batch that records the owner, confirms the active market-data tabs have absorbed any reusable assets, and states whether historical backup retention is still required.
- If cleaned later, classify the action as temporary-backup governance, not canonical page archive.

## Follow-Up Notes

- Review backup content only if a market-data workbench retirement/absorption mutation batch needs to recover missed UI fragments, calculations, table columns, or selector logic.
- If backup retention is no longer desired, move or archive both backup snapshots together with an explicit `no-successor-needed` rationale.
- Do not use this checklist to approve deletion of active `ArtDecoMarketData.vue` or its `market-data-tabs/*` children.
