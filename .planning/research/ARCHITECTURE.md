# Architecture Research: v1.1 Final Polish (Corrected)

**Researched:** 2026-04-08
**Corrected:** 2026-04-08 — aligned with v1.0 Phase 3 VERIFICATION.md

## F821 Error Clusters

### Distribution (verified 2026-04-08)
- 62 files, 791 total F821 errors
- adapters/ (akshare + financial): ~350 errors
- monitoring/: ~56, gpu/: ~34, web/backend/repositories/: ~28
- Long tail: ~323 errors across 42 files

### Top Files
| Errors | File |
|--------|------|
| 81 | src/adapters/akshare/misc_data/get_ths_industry_names.py |
| 54 | src/adapters/akshare/misc_data/get_futures_index_daily.py |
| 50 | src/adapters/financial/stock_daily.py |
| 45 | src/adapters/financial/realtime_data.py |
| 34 | src/advanced_analysis/models/decision_synthesis.py |

## Entry Point Architecture (authoritative from v1.0)

### Chain
```
verify-mount.js (web/frontend/verify-mount.js)
  └→ reads main.js (web/frontend/src/main.js)
       └→ which is NOT the canonical entry
       
main-standard.ts (web/frontend/src/main-standard.ts) ← canonical entry
```

- `main-standard.ts` is the canonical entry point
- `main.js` retained solely because `verify-mount.js` consumes it
- To complete STRU-03: resolve verify-mount.js → remove/update → archive main.js

## Composables Architecture (authoritative from v1.0)

### Layout
- views/composables/: 17 files
- 15/17 are view-local (1 consumer, relative import `./composables/useX`)
- 2 are extraction candidates
- src/composables/: ~30+ files (canonical location for shared composables)

### Correct Approach
- NOT bulk migration — would break 15+ active imports
- Per v1.0 audit: accept view-local as valid pattern, or extract only 2 candidates
- Each view-local composable is co-located with its single consumer — this is idiomatic Vue

## Archive Architecture (authoritative from v1.0)

### views/converted.archive/
- 0 runtime consumers
- 5 test consumers block deletion
- Safe to remove AFTER test dependency resolution

### views/demo/
- ACTIVE code: 5 routes, 3+ view consumers, 8+ tests
- NOT removable — STRU-05 demo portion = "not applicable"

## Suggested Build Order

| Order | Task | Rationale |
|-------|------|-----------|
| 1 | Composables Re-scoping | Decision task, clarifies scope before coding |
| 2 | Archive Removal | Resolve 5 test deps, then delete |
| 3 | Entry Consolidation | Small scope, must get direction right |
| 4 | F821 Top-20 | Concentrated wins, 70%+ of errors |
| 5 | F821 Long Tail | Remaining 42 files, routine |

---
*Architecture research corrected: 2026-04-08*
