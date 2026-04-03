# Frontend Directory Restructure Migration Progress

Date: 2026-04-04
OpenSpec change: `restructure-frontend-directory`
Mongo work item: `2026-04-04-restructure-frontend-shared-target-inventory-main`

## Phase 2 Baseline Inventory

This record captures the actual repository baseline before any shared-asset extraction begins.

### Expected paths from the approved change

| Path | Expected role | Exists before this batch |
| --- | --- | --- |
| `web/frontend/src/shared/components/` | shared component target | No |
| `web/frontend/src/shared/composables/` | shared composable target | No |
| `web/frontend/src/views/shared/components/` | assumed extraction source | No |
| `web/frontend/src/views/shared/composables/` | assumed extraction source | No |

### Actual shared-like locations found in the repo

| Path | File count | Notes |
| --- | ---: | --- |
| `web/frontend/src/components/shared/` | 12 | Already acts as a canonical shared UI layer. Excludes `.claude` logs. |
| `web/frontend/src/composables/` | 49 | Already acts as a canonical shared composable layer. |
| `web/frontend/src/views/components/` | 5 | View-adjacent reusable fragments; candidate extraction sources. |
| `web/frontend/src/views/composables/` | 17 | View-adjacent composables; candidate extraction sources. |

### Import baseline

- No `@/views/shared/...` imports were found in the active frontend tree during this inventory pass.
- Current shared-style imports primarily use:
  - `@/components/shared/...`
  - `@/components/shared`
  - `@/composables/...`

## Merge / Keep Strategy

Because the approved source and target shared paths do not exist in the current repo baseline, there are no target-location conflicts to merge in this batch.

The extraction strategy for follow-up batches is:

1. Keep `src/components/shared/` as the canonical shared component base unless a specific file must move into `src/shared/components/`.
2. Keep `src/composables/` as the canonical shared composable base unless a specific file must move into `src/shared/composables/`.
3. Treat `src/views/components/` and `src/views/composables/` as the real candidate extraction sources that need classification before any `git mv`.
4. Do not execute `git mv` commands that reference `src/views/shared/*`, because that source tree does not exist in the repository baseline.

## Immediate Next Boundary

- Establish tracked target directories under `src/shared/`.
- Re-scope Phase 2 micro-batches against actual source locations:
  - `src/views/components/`
  - `src/views/composables/`
- Only start file moves after each candidate is classified as either:
  - keep in current canonical shared layer
  - move to `src/shared/*`
  - keep view-local
