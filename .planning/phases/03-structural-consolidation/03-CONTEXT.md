# Phase 3: Structural Consolidation - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish single canonical locations for frontend components (resolve case-conflict directories), verify single canonical data access layer, consolidate frontend entry point, and clean dead frontend artifacts. Data access consolidation was completed in Phase 2 — this phase verifies it and handles remaining structural cleanup.

Requirements: LINT-04, STRU-01, STRU-02, STRU-03, STRU-04, STRU-05

</domain>

<decisions>
## Implementation Decisions

### Case-Conflict Directory Merge
- **D-01:** Merge uppercase directories into lowercase counterparts (Vue convention): `Charts/` → `charts/`, `Common/` → `common/`, `Market/` → `market/`
- **D-02:** For files that exist in BOTH cases (e.g., `AdvancedHeatmap.vue` in `Charts/` AND `charts/`): diff each file individually and keep the better version
- **D-03:** For files that ONLY exist in uppercase (e.g., `OscillatorChart.vue` in `Charts/` but not `charts/`): move them into the lowercase directory
- **D-04:** After all content merged, delete the now-empty uppercase directories (`Charts/`, `Common/`, `Market/`)
- **D-05:** Use `git mv` to preserve file history during moves (not delete+add)
- **D-06:** After merge, standardize ALL imports to lowercase paths (e.g., `@/components/charts/ProKLineChart.vue`) regardless of original casing

### Overlap Inventory (pre-discussion scout)
| Pair | Uppercase | Lowercase | Overlapping files |
|------|-----------|-----------|-------------------|
| Charts/ vs charts/ | 7 vue + composables + styles | 4 vue + styles | AdvancedHeatmap, RelationChart, SankeyChart, TreeChart |
| Common/ vs common/ | 1 vue (ResponsiveSidebar) + styles | 8 vue + styles | ResponsiveSidebar |
| Market/ vs market/ | 1 vue (SmartRecommendation) + styles | 15 vue + composables + styles | SmartRecommendation |

### Frontend Entry Point
- **D-07:** Canonical entry is `main-standard.ts` (confirmed by `index.html` `<script type="module" src="/src/main-standard.ts">`)
- **D-08:** Rename `main-standard.ts` → `main.ts` for convention clarity, replacing current `main.js`
- **D-09:** Delete all 7 other entry variants: `main-debug.js`, `main-enhanced.ts`, `main-minimal.ts`, `main-original.js`, `main-simplified.js`, `main-test.js`, and the old `main.js`
- **D-10:** Update `index.html` to load `/src/main.ts` instead of `/src/main-standard.ts`

### Frontend Cleanup
- **D-11:** Move all 16 files from `views/composables/` into `src/composables/` (which already has 35+ files). Handle name conflicts by diffing and keeping the better version.
- **D-12:** Delete `views/converted.archive/` (10 old archived pages) from source tree
- **D-13:** Delete `views/demo/` (12 demo/test files) from source tree

### Data Access Verification
- **D-14:** Full import test of every file in `src/data_access/` — not just grep for stale imports
- **D-15:** Verify zero imports still point to deleted directories (`data_access_pkg`, `database_optimization`, `db_manager`)
- **D-16:** Run FastAPI smoke test after verification

### Sub-Stage Ordering
- **D-17:** Sub-stage 3a (entry verification) runs FIRST to establish baseline
- **D-18:** After 3a completes, sub-stages 3b (case merge), 3c (data access verify), and 3d (frontend cleanup) can run in any order or in parallel
- **D-19:** Final verification (build + lint + smoke test) runs after ALL sub-stages complete

### Verification
- **D-20:** Full verification after all changes: `npm run build` + `npx stylelint` + FastAPI smoke test (`python -c "from app.main import app; print('OK')"`)
- **D-21:** No route/layout changes expected, so E2E test (`scripts/run_e2e_pm2.sh`) not required unless routes are affected

### Claude's Discretion
- Exact diff methodology for overlapping case-conflict files (line-by-line vs structural comparison)
- How to handle `composables/` and `styles/` subdirectories within case-conflict dirs during merge
- Whether to batch import updates or do them file-by-file
- Handling of `.backup` files (`App.vue.backup`, `main.js.backup`) found in frontend src/

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 3 Scope
- `.planning/ROADMAP.md` §Phase 3 — Phase boundary, sub-stages, success criteria, risk notes
- `.planning/REQUIREMENTS.md` §Structural Consolidation — STRU-01 through STRU-05, LINT-04

### Codebase Maps
- `.planning/codebase/STRUCTURE.md` — Current directory structure (frontend section)
- `.planning/codebase/ARCHITECTURE.md` — Data flow, entry points
- `.planning/codebase/CONCERNS.md` — Structural issues documented

### Prior Phase Context
- `.planning/phases/01-python-lint-baseline/01-CONTEXT.md` — D-01 (full deletion pattern established)
- `.planning/phases/02-dead-code-inventory-removal/02-CONTEXT.md` — D-05/D-06/D-07 (canonical wins on merge)

### Project Governance
- `architecture/STANDARDS.md` — Migration governance rules, code organization rules
- `.planning/research/PITFALLS.md` — P-03 (case-conflict filesystem issues), P-05 (entry point confusion)

</canonical_refs>

<code_context>
## Existing Code Insights

### Case-Conflict Directories (current state)
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

### Frontend Entry Files
- `index.html` loads: `<script type="module" src="/src/main-standard.ts">`
- `main-standard.ts` imports: `createApp`, `createPinia`, `App.vue`, `router/index.ts`
- `main.js` imports: `createApp`, `createPinia`, Element Plus icons (different setup)
- Backup files present: `App.vue.backup`, `main.js.backup`

### Data Access Layer (post-Phase 2)
- `src/data_access/` — 15 files, sole canonical data access layer
- All overlapping directories deleted by Phase 2: `data_access_pkg/`, `db_manager/`, `database_optimization/`

### Established Patterns (from prior phases)
- Full deletion for duplicate layers (Phase 1 pattern)
- Grep evidence before any deletion (Phase 2 pattern)
- Canonical version wins on file conflicts (Phase 2, D-05)
- `ruff check` + `pytest` + FastAPI smoke test after each batch of changes

### Integration Points
- Vite resolves `@/` → `web/frontend/src/`
- Component imports use `@/components/{dirname}/{filename}.vue`
- Case-conflict resolution affects all `.vue` files importing from these directories

</code_context>

<specifics>
## Specific Ideas

- Lowercase imports already dominate — merging uppercase into lowercase minimizes import changes
- `main-standard.ts` is already the loaded entry — renaming to `main.ts` is a rename-only change
- The `views/composables/` files (useTradingDashboard, useAnalysis, etc.) are view-specific composables that may conflict with existing `src/composables/` files (useTrading.ts, useChart.ts, etc.)
- Git case-sensitivity on WSL: `git mv` via temp path may be needed (e.g., `Charts/X.vue` → `charts/x_temp.vue` → `charts/X.vue`)

</specifics>

<deferred>
## Deferred Ideas

- Fixing ALL ruff errors to zero — Phase 4 (Naming & Polish)
- Backend API directory reorganization (205-file split) — out of scope entirely
- Test quality improvements — separate initiative
- Store domain clarification (market.ts vs marketData.ts) — Phase 4

</deferred>

---
*Phase: 03-structural-consolidation*
*Context gathered: 2026-04-07*
