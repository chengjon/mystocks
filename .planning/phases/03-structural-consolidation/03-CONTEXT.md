# Phase 3: Structural Consolidation - Context

**Gathered:** 2026-04-07
**Revised:** 2026-04-07 (corrected premature deletion decisions after review)
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish single canonical locations for frontend components (resolve case-conflict directories), verify single canonical data access layer, audit and consolidate frontend entry points, and audit dead frontend artifacts for safe removal. Data access consolidation was completed in Phase 2 — this phase verifies it and handles remaining structural cleanup.

Requirements: LINT-04, STRU-01, STRU-02, STRU-03, STRU-04, STRU-05

**Key constraint (from ROADMAP §3d):** All cleanup operations require caller/tooling audit BEFORE deletion. No deletion based on directory name alone. Per `architecture/STANDARDS.md:103` — functional tree analysis required before removing any artifact.

</domain>

<decisions>
## Implementation Decisions

### Case-Conflict Directory Merge
- **D-01:** Merge uppercase directories into lowercase counterparts (Vue convention): `Charts/` → `charts/`, `Common/` → `common/`, `Market/` → `market/`
- **D-02:** For files that exist in BOTH cases (e.g., `AdvancedHeatmap.vue` in `Charts/` AND `charts/`): diff each file individually and keep the better version
- **D-03:** For files that ONLY exist in uppercase (e.g., `OscillatorChart.vue` in `Charts/` but not `charts/`): move them into the lowercase directory
- **D-04:** After all content merged, delete the now-empty uppercase directories (`Charts/`, `Common/`, `Market/`)
- **D-05:** Use `git mv` to preserve file history during moves (not delete+add)
- **D-06:** After merge, standardize ALL imports to lowercase paths (e.g., `@/components/charts/ProKLineChart.vue`)

### Overlap Inventory (verified counts)
| Pair | Uppercase | Lowercase | Overlapping files |
|------|-----------|-----------|-------------------|
| Charts/ vs charts/ | 7 vue + composables/ + styles/ | 4 vue + styles/ | AdvancedHeatmap, RelationChart, SankeyChart, TreeChart |
| Common/ vs common/ | 1 vue (ResponsiveSidebar) + styles/ | 8 vue + styles/ | ResponsiveSidebar |
| Market/ vs market/ | 1 vue (SmartRecommendation) + styles/ | 15 vue + composables/ + styles/ | SmartRecommendation |

### Frontend Entry Point (audit-first)
- **D-07:** Canonical entry is `main-standard.ts` (confirmed by `index.html` `<script type="module" src="/src/main-standard.ts">`)
- **D-08:** **AUDIT REQUIRED before any rename/deletion:** For each of the 8 main-*.js/ts files, grep for all consumers (HTML, scripts, tests, tooling). Known consumers:
  - `web/frontend/verify-mount.js` reads `src/main.js` — DO NOT delete `main.js` until verify-mount.js is updated or confirmed obsolete
  - `index.html` loads `main-standard.ts` — this is the runtime truth source
- **D-09:** Only archive variants confirmed to have ZERO consumers after audit. Do NOT assume "unused" without grep evidence.
- **D-10:** If renaming `main-standard.ts` → `main.ts`, update BOTH `index.html` AND any tooling that references the old name. Verify build succeeds before committing.

### Frontend Cleanup (audit-first)
- **D-11:** **views/composables/ (17 files) — AUDIT before any move.** 15+ views use relative `./composables/*` imports (e.g., TradingDashboard.vue, Analysis.vue, EnhancedDashboard.vue). Per `web/frontend/MIGRATION_PROGRESS.md`:
  - 15 of 17 files classified "Keep view-local" — these MUST stay in views/composables/
  - 2 files classified as extraction candidates: `useTradingDashboard.ts` and `tradingDashboardActions.ts`
  - Moving view-local composables would break relative imports and change page coupling boundaries
- **D-12:** **views/converted.archive/ (11 files) — AUDIT before deletion.** Known consumers:
  - 8+ Vitest test files reference converted.archive files (e.g., `converted-archive-dashboard-style-source.spec.ts`, `converted-archive-market-data-style-source.spec.ts`)
  - Deleting without updating/removing these tests will break the test suite
  - Per ROADMAP §3d: must classify via functional tree, not just directory name
- **D-13:** **views/demo/ (41 files) — AUDIT before deletion.** Known consumers:
  - `OpenStockDemo.vue` imports from `./demo/openstock/*` (config + components)
  - `tests/all-pages-accessibility.spec.ts` references 5 demo routes (`/demo/openstock`, `/demo/freqtrade`, `/demo/stock-analysis`, `/demo/tdxpy`, `/demo/smart-data`)
  - `tests/menu-configuration.spec.js` tests demo menu navigation
  - Deleting without updating/removing these consumers will break tests and active pages
- **D-14:** For all three cleanup targets (composables, archive, demo): produce a DELETION-CANDIDATES style inventory with grep evidence before any removal, following the pattern established in Phase 2

### Data Access Verification
- **D-15:** Full import test of every file in `src/data_access/` (22 files) — not just grep for stale imports
- **D-16:** Verify zero imports still point to deleted directories (`data_access_pkg`, `database_optimization`, `db_manager`)
- **D-17:** Run FastAPI smoke test after verification

### Sub-Stage Ordering
- **D-18:** Sub-stage 3a (entry verification) runs FIRST to establish baseline
- **D-19:** After 3a completes, sub-stages 3b (case merge), 3c (data access verify), and 3d (frontend cleanup) can run in any order or in parallel
- **D-20:** Final verification (build + lint + smoke test) runs after ALL sub-stages complete

### Verification
- **D-21:** Full verification after all changes: `npm run build` + `npx stylelint` + FastAPI smoke test
- **D-22:** No route/layout changes expected, so E2E test not required unless routes are affected

### Claude's Discretion
- Exact diff methodology for overlapping case-conflict files
- How to handle `composables/` and `styles/` subdirectories within case-conflict dirs during merge
- Whether to batch import updates or do them file-by-file
- Handling of `.backup` files (`App.vue.backup`, `main.js.backup`) found in frontend src/
- How to handle test files that reference converted.archive/demo after audit determines disposition

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 3 Scope
- `.planning/ROADMAP.md` §Phase 3 — Phase boundary, sub-stages, success criteria, risk notes (especially §3d caveat about verify-mount.js)
- `.planning/REQUIREMENTS.md` §Structural Consolidation — STRU-01 through STRU-05, LINT-04

### Codebase Maps
- `.planning/codebase/STRUCTURE.md` — Current directory structure (frontend section)
- `.planning/codebase/ARCHITECTURE.md` — Data flow, entry points
- `.planning/codebase/CONCERNS.md` — Structural issues documented

### Migration Context
- `web/frontend/MIGRATION_PROGRESS.md` — Classification of views/composables/ (15 "keep view-local", 2 extraction candidates)

### Prior Phase Context
- `.planning/phases/01-python-lint-baseline/01-CONTEXT.md` — D-01 (full deletion pattern established)
- `.planning/phases/02-dead-code-inventory-removal/02-CONTEXT.md` — D-05/D-06/D-07 (canonical wins on merge, DELETION-CANDIDATES pattern)

### Project Governance
- `architecture/STANDARDS.md` — Deletion governance rules (lines 103-111), migration governance (line 88)
- `.planning/research/PITFALLS.md` — P-03 (case-conflict filesystem issues), P-05 (entry point confusion)

</canonical_refs>

<code_context>
## Existing Code Insights

### Case-Conflict Directories (verified counts)
- `Charts/` (7 files): AdvancedHeatmap, IndicatorSelector, OscillatorChart, ProKLineChart, RelationChart, SankeyChart, TreeChart + composables/ + styles/
- `charts/` (4 files): AdvancedHeatmap, RelationChart, SankeyChart, TreeChart + styles/
- `Common/` (1 file): ResponsiveSidebar + styles/
- `common/` (8 files): ApiVersionManager, ChartLoadingSkeleton, ErrorBoundary, KeyboardShortcuts, PerformanceMonitor, ResponsiveSidebar, RoleSwitcher, SmartDataIndicator + styles/
- `Market/` (1 file): SmartRecommendation + styles/
- `market/` (15 files): ChipRacePanel, ChipRaceTable, ETFDataPanel, ETFDataTable, FundFlowPanel, IndicatorSelector, LongHuBangPanel, LongHuBangTable, ProKLineChart, SmartRecommendation, WencaiPanel, WencaiPanelSimple, WencaiPanelV2, WencaiQueryTable, WencaiTest + composables/ + styles/

### Import Patterns (from grep)
- Lowercase imports dominate: `@/components/common/...`, `@/components/market/...`, `@/components/charts/...`
- Zero imports found using uppercase `@/components/Common/...` or `@/components/Market/...`
- Some files import from `@/components/charts/` (SankeyChart, TreeChart, RelationChart, AdvancedHeatmap, ProKLineChart)

### Frontend Entry Files (8 total)
- `index.html` loads: `<script type="module" src="/src/main-standard.ts">`
- `main-standard.ts` imports: createApp, createPinia, App.vue, router/index.ts
- `main.js` imports: createApp, createPinia, Element Plus icons — **read by verify-mount.js**
- 6 other variants: main-debug.js, main-enhanced.ts, main-minimal.ts, main-original.js, main-simplified.js, main-test.js
- Backup files: App.vue.backup, main.js.backup

### views/composables/ Consumers (17 files, 15+ relative imports)
- TradingDashboard.vue: `import { useTradingDashboard } from './composables/useTradingDashboard'`
- Analysis.vue, monitor.vue, EnhancedDashboard.vue, BacktestWizard.vue, and 10+ others use relative `./composables/*`
- MIGRATION_PROGRESS.md classifies 15/17 as "Keep view-local"
- Only `useTradingDashboard.ts` and `tradingDashboardActions.ts` are extraction candidates

### views/converted.archive/ Consumers (11 files)
- 8+ Vitest specs: `converted-archive-dashboard-style-source.spec.ts`, `converted-archive-market-data-style-source.spec.ts`, `converted-archive-trading-management-style-source.spec.ts`, `converted-archive-backtest-style-source.spec.ts`, `converted-archive-shared-style-template.spec.ts`

### views/demo/ Consumers (41 files)
- OpenStockDemo.vue imports from `./demo/openstock/config` and `./demo/openstock/components`
- tests/all-pages-accessibility.spec.ts tests 5 demo routes
- tests/menu-configuration.spec.js tests demo menu navigation

### Data Access Layer (post-Phase 2)
- `src/data_access/` — 22 files, sole canonical data access layer
- All overlapping directories deleted by Phase 2: `data_access_pkg/`, `db_manager/`, `database_optimization/`

### Established Patterns (from prior phases)
- Full deletion for duplicate layers (Phase 1 pattern)
- Grep evidence before any deletion — DELETION-CANDIDATES.md pattern (Phase 2)
- Canonical version wins on file conflicts (Phase 2, D-05)
- `ruff check` + `pytest` + FastAPI smoke test after each batch of changes

</code_context>

<specifics>
## Specific Ideas

- Lowercase imports already dominate — merging uppercase into lowercase minimizes import changes
- Case-conflict merge (D-01 through D-06) is the safest sub-stage — no deletion audit needed since lowercase dirs already exist and serve as the merge target
- Frontend cleanup (D-11 through D-14) is the riskiest sub-stage — requires caller audit following Phase 2's DELETION-CANDIDATES pattern
- Git case-sensitivity on WSL: `git mv` via temp path may be needed (e.g., `Charts/X.vue` → `charts/x_temp.vue` → `charts/X.vue`)

</specifics>

<deferred>
## Deferred Ideas

- Fixing ALL ruff errors to zero — Phase 4 (Naming & Polish)
- Backend API directory reorganization (205-file split) — out of scope entirely
- Test quality improvements — separate initiative
- Store domain clarification (market.ts vs marketData.ts) — Phase 4
- Moving "keep view-local" composables out of views/ — future initiative after MIGRATION_PROGRESS.md task 8.5 resolves TradingDashboard disposition

</deferred>

---
*Phase: 03-structural-consolidation*
*Context gathered: 2026-04-07*
*Revised: 2026-04-07 — corrected premature deletion decisions per review findings*
