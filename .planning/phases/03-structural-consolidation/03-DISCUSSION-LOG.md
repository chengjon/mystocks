# Phase 3: Structural Consolidation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-07
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
| main-standard.ts → canonical | Rename to main.ts, delete other 7 | ✓ |
| Keep debug + test variants | Also keep main-debug.js and main-test.js | |
| Keep name as-is | Leave main-standard.ts, delete other 7 | |

**User's choice:** main-standard.ts → canonical, rename to main.ts

### Rename decision

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, rename to main.ts | Update index.html to load main.ts | ✓ |
| No, keep main-standard.ts | Fewer changes but unconventional | |

**User's choice:** Rename to main.ts

**Key evidence:** `index.html` loads `main-standard.ts` (not `main.js` as STRUCTURE.md assumed)

---

## Frontend Cleanup

### Composables move

| Option | Description | Selected |
|--------|-------------|----------|
| Move all into src/composables/ | Diff conflicts, update imports | ✓ |
| Move only unique files | Leave duplicates for manual review | |

**User's choice:** Move all 16 files into src/composables/

### Dead directories

| Option | Description | Selected |
|--------|-------------|----------|
| Delete both directories | Remove views/converted.archive/ (10 files) and views/demo/ (12 files) | ✓ |
| Delete archive only | Keep views/demo/ for testing | |
| Keep both | Don't block anything | |

**User's choice:** Delete both directories

### Verification level

| Option | Description | Selected |
|--------|-------------|----------|
| Full build + lint + smoke test | npm run build + stylelint + FastAPI smoke | ✓ |
| Build only | Faster but riskier | |
| Full + browser check | Most thorough | |

**User's choice:** Full build + lint + smoke test

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
