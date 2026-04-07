# Phase 3: Structural Consolidation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-07
**Revised:** 2026-04-07 (corrected premature deletion decisions after review findings)
**Phase:** 03-structural-consolidation
**Areas discussed:** Case-conflict merge, Frontend entry point, Frontend cleanup, Data access verification, Sub-stage ordering, Git case-sensitivity, Import path convention

---

## Case-Conflict Merge Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Diff each overlap individually | Compare overlapping files one at a time, keep better version | ✓ |
| Lowercase always wins | Delete uppercase variants without comparison | |
| Uppercase always wins | Move uppercase versions into lowercase directory | |

**User's choice:** Diff each overlap individually
**Notes:** User preferred safety over speed — 6 files overlap across 3 pairs (AdvancedHeatmap, RelationChart, SankeyChart, TreeChart, ResponsiveSidebar, SmartRecommendation)

### Unique uppercase file handling

| Option | Description | Selected |
|--------|-------------|----------|
| Move into lowercase | Charts/ unique files (OscillatorChart, IndicatorSelector, ProKLineChart) move to charts/ | ✓ |
| Keep both directories | Avoid import changes but perpetuate conflict | |

**User's choice:** Move into lowercase

### Post-merge cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Delete uppercase dirs | Remove Charts/, Common/, Market/ after merge | ✓ |
| Leave for later cleanup | Keep as-is | |

**User's choice:** Delete uppercase dirs

---

## Frontend Entry Point

| Option | Description | Selected |
|--------|-------------|----------|
| main-standard.ts → canonical | Rename to main.ts, delete other 7 | ✓ (revised) |
| Keep debug + test variants | Also keep main-debug.js and main-test.js | |
| Keep name as-is | Leave main-standard.ts, delete other 7 | |

**User's choice:** main-standard.ts → canonical, rename to main.ts

### Revision after review (Finding 1 — HIGH)

**Original decision (D-08/D-09):** Rename main-standard.ts → main.ts, delete other 7 variants including main.js

**Corrected decision:** AUDIT all variants before any rename/deletion. Known blocking consumers:
- `web/frontend/verify-mount.js` reads `src/main.js` — cannot delete main.js without updating verify-mount.js
- Only archive variants confirmed to have ZERO consumers after grep evidence
- Per ROADMAP §3d: "audit all other main-*.js/ts variants for HTML / script / test / tooling references, then archive only the confirmed-unused set"

**Reason:** Deleting main.js would break verify-mount.js. The discuss-phase incorrectly elevated this to a locked decision when it requires caller audit first, violating `architecture/STANDARDS.md:88` migration governance.

---

## Frontend Cleanup

### Composables move

| Option | Description | Selected |
|--------|-------------|----------|
| Move all into src/composables/ | Diff conflicts, update imports | ✓ (revised) |
| Move only unique files | Leave duplicates for manual review | |

**User's choice:** Move all 16 files into src/composables/

### Revision after review (Finding 2 — HIGH)

**Original decision (D-11):** Move all 16 views/composables/ files into src/composables/

**Corrected decision:** AUDIT per MIGRATION_PROGRESS.md classification first. Known constraints:
- 15 of 17 files classified "Keep view-local" by the project's own migration audit
- 15+ views use relative `./composables/*` imports (TradingDashboard.vue, Analysis.vue, EnhancedDashboard.vue, etc.)
- Only `useTradingDashboard.ts` and `tradingDashboardActions.ts` are confirmed extraction candidates
- Bulk move would break relative imports and alter page coupling boundaries — this is a refactoring decision, not a structural cleanup

**Reason:** MIGRATION_PROGRESS.md already classified most composables as view-local. The discuss-phase did not consult this canonical source and treated a bulk move as a locked decision.

### Dead directories

| Option | Description | Selected |
|--------|-------------|----------|
| Delete both directories | Remove views/converted.archive/ and views/demo/ | ✓ (revised) |
| Delete archive only | Keep views/demo/ for testing | |
| Keep both | Don't block anything | |

**User's choice:** Delete both directories

### Revision after review (Finding 3 — HIGH)

**Original decisions (D-12, D-13):** Delete views/converted.archive/ and views/demo/

**Corrected decision:** AUDIT consumers via functional tree analysis BEFORE deletion. Known blocking consumers:
- `views/demo/` (41 files, not 12): OpenStockDemo.vue imports from `./demo/openstock/*`
- `views/converted.archive/` (11 files, not 10): 8+ Vitest specs reference archive files
- `tests/all-pages-accessibility.spec.ts` tests 5 demo routes
- `tests/menu-configuration.spec.js` tests demo menu navigation
- Deleting without updating/removing these consumers breaks the test suite

**Reason:** Per `architecture/STANDARDS.md:103` — functional tree analysis required before removal. Per ROADMAP §3d — "audit all other main-*.js/ts variants for HTML / script / test / tooling references." Neither audit was performed during discussion.

### File count corrections (Finding 4 — MEDIUM)

| Metric | Context value | Actual (verified) |
|--------|---------------|-------------------|
| views/composables/ | 16 files | 17 files |
| views/converted.archive/ | 10 files | 11 files |
| views/demo/ | 12 files | 41 files |
| src/data_access/ | 15 files | 22 files |

**Reason:** Scout commands ran from wrong CWD (`/opt/claude/mystocks_spec/web/frontend/web/frontend`), producing inaccurate counts. All counts verified via `find` from absolute paths.

---

## Data Access Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Light verification (grep only) | Check for stale imports pointing to deleted dirs | |
| Full import test of each file | Import every module in data_access/ to confirm working | ✓ |

**User's choice:** Full import test of each file

---

## Sub-Stage Ordering

| Option | Description | Selected |
|--------|-------------|----------|
| 3a first, then 3b+3c+3d flexible | Entry verification first, others in parallel or any order | ✓ |
| Strict sequential 3a→3b→3c→3d | Maximum safety | |

**User's choice:** 3a first, then 3b+3c+3d flexible

---

## Git Case-Sensitivity Handling

| Option | Description | Selected |
|--------|-------------|----------|
| git mv to preserve history | Use git mv for all file moves | ✓ |
| Delete + add (simpler) | Loses git history but simpler | |

**User's choice:** git mv to preserve history
**Notes:** WSL2 environment — may need temp-path workaround for case-renames

---

## Import Path Convention

| Option | Description | Selected |
|--------|-------------|----------|
| Lowercase only | All imports use @/components/charts/, @/components/common/, @/components/market/ | ✓ |
| Keep mixed casing | Whatever casing the import already uses | |

**User's choice:** Lowercase only

---

## Claude's Discretion

- Exact diff methodology for overlapping case-conflict files
- How to handle composables/ and styles/ subdirectories within case-conflict dirs
- Whether to batch import updates or do them file-by-file
- Handling of .backup files (App.vue.backup, main.js.backup) in frontend src/

## Deferred Ideas

None — discussion stayed within phase scope
