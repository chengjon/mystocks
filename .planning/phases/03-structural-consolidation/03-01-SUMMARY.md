---
plan: "03-01"
phase: "03"
wave: 1
status: complete
started: 2026-04-07
completed: 2026-04-07
---

# Plan 03-01: Summary

## Objective
Merge case-conflict directories, document canonical entry, archive unused variants.

## Results

### Task 1: Frontend Entry Verification ✅
- Created `web/frontend/ENTRY-TRUTH.md`
- Confirmed `main-standard.ts` as canonical entry (loaded by index.html)
- Documented `verify-mount.js` as consumer of `main.js`
- Inventoried all 8 main variants with consumer counts

### Task 2: Charts/ → charts/ ✅
- Renamed 13 tracked files via `git mv` (two-step temp path)
- AdvancedHeatmap.vue, RelationChart.vue: identical — kept as-is
- SankeyChart.vue, TreeChart.vue: Charts/ had responsive media queries — preserved
- IndicatorSelector.vue, OscillatorChart.vue, ProKLineChart.vue: unique, moved
- composables/, styles/: merged into charts/

### Task 3: Common/ → common/ ✅
- Common/ was entirely untracked (not in git)
- Tracked common/ResponsiveSidebar.vue already had a11y attributes (role="navigation", aria-label)
- Deleted untracked Common/ directory

### Task 4: Market/ → market/ ✅
- Market/ was entirely untracked (not in git)
- Untracked Market/SmartRecommendation.vue had debug console.log statements
- Tracked market/ version was clean — kept it
- Deleted untracked Market/ directory

### Task 5: Archive 6 Unused Variants ✅
- Created `web/frontend/src/_entry-archive/`
- Moved 6 zero-consumer variants: main-debug.js, main-original.js, main-simplified.js, main-test.js, main-enhanced.ts, main-minimal.ts
- Preserved main-standard.ts (canonical) and main.js (verify-mount.js consumer)

### Task 6: Final Verification ✅
- `npm run build`: exits 0 (pre-existing TS warnings unrelated to our changes)
- `stylelint`: 126 pre-existing errors, 0 in changed files
- FastAPI smoke test: prints "OK"

## Key Decisions
- Charts/ content was canonical (had responsive media queries) → renamed to charts/
- Common/ and Market/ were untracked → simply deleted (tracked lowercase dirs were canonical)
- Two-step `git mv` via temp path used for Charts/ rename (WSL2 case-sensitivity)

## Commits
1. `docs(frontend): add ENTRY-TRUTH.md documenting canonical entry point`
2. `refactor(03): merge case-conflict dirs Charts→charts, remove Common/ Market/`
3. `refactor(03): archive 6 zero-consumer frontend entry variants`
