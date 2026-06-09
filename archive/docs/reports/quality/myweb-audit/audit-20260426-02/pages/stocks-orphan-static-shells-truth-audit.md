# Stocks Orphan Static Shells Truth Audit

## Scope
- Files:
  - `web/frontend/src/views/stocks/Activity.vue`
  - `web/frontend/src/views/stocks/Concept.vue`
  - `web/frontend/src/views/stocks/Industry.vue`
  - `web/frontend/src/views/stocks/Watchlist.vue`
- Synthetic route key: `/secondary/stocks-orphan-static-shells`
- Family: `selector-scoped-snapshot-truth / local-action-and-execution-truth`

## Problem
- These pages were not active route truth or imported by active owners.
- They still rendered local mock trading rows, concept and industry pools, watchlist filters, favorite/remove actions, random local mutation, and refresh success semantics.

## Repair
- Converted the four pages to honest static shells.
- Preserved files for compatibility and linked users to canonical `/trade/history`, `/data/concept`, `/data/industry`, and `/watchlist/manage`.

## Verification
- RED:
  - `cd web/frontend && npx vitest run tests/unit/config/stocks-orphan-static-shells.spec.ts` failed because the old pages lacked `legacy-static-shell`.
- GREEN:
  - `cd web/frontend && npx vitest run tests/unit/config/stocks-orphan-static-shells.spec.ts` passed (`1/1`).
- Source scan:
  - `rg "ElMessage\\.success|setTimeout|Math\\.random|000001|平安银行|selectedConcept|selectedIndustry|filteredStocks|toggleFavorite|Activity data refreshed|CONCEPT STOCK POOLS|INDUSTRY STOCK POOLS|WATCHLIST MANAGEMENT" <batch files>` produced no matches.

## Outcome
- The retired stocks child pages no longer claim selector-owned snapshots, local refresh success, or mock row truth.
