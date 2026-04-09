# Phase 3: Structural Consolidation — Research

**Phase:** 03-structural-consolidation
**Date:** 2026-04-07
**Status:** Research complete

---

## R-01: WSL2 Git Case-Sensitivity

**Finding:** `git config core.ignoreCase` returns `true`. Git treats filenames case-insensitively.

**Implication for case-conflict merge:**
- `git mv Charts/X.vue charts/X.vue` will FAIL on case-insensitive git because it sees them as the same file
- **Required workaround:** Two-step rename via temp path:
  ```bash
  git mv Charts/X.vue charts/x_temp.vue
  git mv charts/x_temp.vue charts/X.vue
  ```
- Or use `git config core.ignoreCase false` temporarily, then restore after merge
- For directory-level moves, process files individually since git can't move directories

**Recommendation:** Process each file individually via two-step `git mv`. Do NOT change `core.ignoreCase` as it affects the entire repo.

---

## R-02: Case-Conflict File Diffs

### Charts/ vs charts/ (4 overlapping files)

| File | Verdict | Detail |
|------|---------|--------|
| AdvancedHeatmap.vue | **IDENTICAL** | Zero diff — lowercase copy is sufficient |
| RelationChart.vue | **IDENTICAL** | Zero diff — lowercase copy is sufficient |
| SankeyChart.vue | **Charts/ is NEWER** | Charts/ has responsive media queries (lines 403-421) not in charts/ |
| TreeChart.vue | **Charts/ is NEWER** | Charts/ has responsive media queries (lines 455-479) not in charts/ |

**Unique to Charts/ only (move to charts/):** IndicatorSelector.vue, OscillatorChart.vue, ProKLineChart.vue
**Subdirectories to handle:** Charts/composables/, Charts/styles/, charts/styles/

### Common/ vs common/ (1 overlapping file)

| File | Verdict | Detail |
|------|---------|--------|
| ResponsiveSidebar.vue | **Significant diffs** | Common/ has mobile overlay with `<transition>`, accessibility attributes (`role="navigation"`, `aria-label`). common/ has different formatting (2-space indent vs 4-space). Both are functional. |

**Recommendation:** Diff-then-decide: compare functional features, not formatting. Common/ version has accessibility enhancements that common/ lacks.

### Market/ vs market/ (1 overlapping file)

| File | Verdict | Detail |
|------|---------|--------|
| SmartRecommendation.vue | **Market/ has debug logging** | Market/ has 2 extra `console.log` statements (lines 171, 177). Otherwise identical. |

**Recommendation:** Keep market/ version (without debug console.log). The Market/ console.logs are debug artifacts.

---

## R-03: Consumer Maps for Cleanup Targets

### views/demo/ (41 files, NOT 12)

**Active consumers — CANNOT delete without cleanup:**
- 6 routes in `router/index.js`: openstock-demo, pyprofiling-demo, freqtrade-demo, stock-analysis-demo, tdxpy-demo, smart-data
- Vue views importing from demo: OpenStockDemo.vue, TdxpyDemo.vue, FreqtradeDemo.vue
- Tests: `tests/all-pages-accessibility.spec.ts` tests 5 demo routes
- Tests: `tests/menu-configuration.spec.js` tests demo menu navigation

**Verdict:** views/demo/ is ACTIVE CODE with routes and tests. Deletion would break router and 2+ test suites. Must update router + tests BEFORE any removal.

### views/converted.archive/ (11 files, NOT 10)

**Active consumers:**
- ZERO imports in src/ views/components — no runtime dependency
- 8+ Vitest spec files reference archive files for style source testing:
  - `converted-archive-dashboard-style-source.spec.ts`
  - `converted-archive-market-data-style-source.spec.ts`
  - `converted-archive-trading-management-style-source.spec.ts`
  - `converted-archive-backtest-style-source.spec.ts`
  - `converted-archive-shared-style-template.spec.ts`

**Verdict:** No runtime dependency, but test consumers exist. Safe to archive/delete ONLY after updating or removing those test files.

### views/composables/ (17 files, NOT 16)

**Consumer pattern:** 26 relative imports from views:
- 15 files classified "Keep view-local" per MIGRATION_PROGRESS.md
- Only 2 extraction candidates: `useTradingDashboard.ts`, `tradingDashboardActions.ts`
- Bulk move would break 15+ views using `./composables/*` relative imports

**Verdict:** Per MIGRATION_PROGRESS.md classification, 15/17 should STAY. Only 2 are extraction candidates, and even those should only move after task 8.5 resolves TradingDashboard disposition.

---

## R-04: Frontend Entry Point Audit

### index.html truth source
- Loads: `<script type="module" src="/src/main-standard.ts">`
- This is confirmed by direct file read

### Main variant consumer audit

| File | Consumers | Safe to archive? |
|------|-----------|-----------------|
| main-standard.ts | 2 (index.html + itself) | NO — canonical entry |
| main.js | 1 (verify-mount.js reads it) | NO — verify-mount.js depends on it |
| main-debug.js | 0 | YES |
| main-original.js | 0 | YES |
| main-simplified.js | 0 | YES |
| main-test.js | 0 | YES |
| main-enhanced.ts | 0 | YES |
| main-minimal.ts | 0 | YES |

**Safe-to-archive set (6 files):** main-debug.js, main-original.js, main-simplified.js, main-test.js, main-enhanced.ts, main-minimal.ts

**NOT safe to archive (2 files):** main-standard.ts (canonical entry), main.js (verify-mount.js consumer)

### Backup files
- App.vue.backup, main.js.backup — likely stale, but audit for consumers before deletion

---

## R-05: Data Access Consolidation Verification

Phase 2 already deleted: `data_access_pkg/`, `db_manager/`, `database_optimization/`
Phase 2 already established: `src/data_access/` as sole canonical layer

**Current state:** `src/data_access/` has 22 files (excluding __pycache__)

**Verification needed:**
1. Grep for stale imports to deleted directories
2. Import test of each Python module in data_access/
3. FastAPI smoke test

---

## R-06: Vite/TypeScript Config Implications

- Vite resolves `@/` → `web/frontend/src/` (via vite.config.mts alias)
- TypeScript path mapping exists in tsconfig.json
- No component-level aliases — all component imports are relative or via `@/components/...`
- **No Vite/TS config changes needed** for case-conflict merge — only import path updates

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Case-insensitive git mv fails | HIGH | Two-step temp-path rename |
| views/demo/ deletion breaks router | HIGH | Audit routes + tests BEFORE deletion |
| views/converted.archive/ deletion breaks tests | MEDIUM | Update/remove test files first |
| ResponsiveSidebar merge loses accessibility | MEDIUM | Keep Common/ version (has a11y attrs) |
| Composables bulk move breaks 15+ views | HIGH | Per MIGRATION_PROGRESS.md: only 2 candidates |
| verify-mount.js breaks if main.js deleted | HIGH | Update verify-mount.js before deletion |

---

## Recommendations for Planner

1. **Sub-stage 3b (case merge)** is the safest — only 2 files need diff decisions (SankeyChart, TreeChart get Charts/ version; ResponsiveSidebar needs manual merge; SmartRecommendation gets market/ version without console.log)
2. **Sub-stage 3a (entry audit)** should archive only the 6 confirmed-zero-consumer variants, keeping main.js and main-standard.ts
3. **Sub-stage 3d (frontend cleanup)** should be split into:
   - 3d-i: Archive 6 confirmed-unused main variants
   - 3d-ii: views/composables/ — DO NOT bulk move. Only classify and document.
   - 3d-iii: views/converted.archive/ — audit tests, update or remove test files, then delete
   - 3d-iv: views/demo/ — NOT a deletion target. Active routes and tests. Mark as "keep" with documentation.
4. **Sub-stage 3c (data access verify)** is straightforward — grep + import test + smoke test
