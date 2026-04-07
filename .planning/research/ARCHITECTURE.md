# Architecture Research: v1.1 Final Polish

**Researched:** 2026-04-08
**Focus:** Integration points, file relationships, suggested build order

## F821 Error Clusters

### Distribution
- 62 files, 791 total F821 errors
- Top: `src/adapters/` (akshare + financial ≈ 350 errors)
- Secondary: `src/monitoring/` (~56), `src/gpu/` (~34), `web/backend/app/repositories/` (~28)
- Long tail: ~323 errors across 42 files

### Top 20 Files
| Errors | File |
|--------|------|
| 81 | src/adapters/akshare/misc_data/get_ths_industry_names.py |
| 54 | src/adapters/akshare/misc_data/get_futures_index_daily.py |
| 50 | src/adapters/financial/stock_daily.py |
| 45 | src/adapters/financial/realtime_data.py |
| 34 | src/advanced_analysis/models/decision_synthesis.py |
| 34 | src/gpu/api_system/services/resource_scheduler/.../core.py |
| 33 | src/adapters/financial/index_daily.py |
| 32 | src/adapters/akshare/index_daily.py |
| 30 | src/adapters/financial/financial_data.py |
| 28 | src/monitoring/multi_channel_alert_manager/... |
| 28 | web/backend/app/repositories/algorithm_model_repository/.../part1.py |
| 25 | src/adapters/financial/stock_basic.py |
| 25 | src/monitoring/threshold/manager.py |

## Frontend Entry Consolidation

### Current State
- verify-mount.js is already in `_entry-archive/` — may be partially done
- Need to verify if any active references remain

## Composables Migration

### Layout
- 17 composable files in views/composables/
- All consumers use relative imports: `'./composables/useX'`
- Target: src/composables/ (already exists with ~30+ composables)
- Each composable has 1-3 consumers (manageable)
- 2 test files in views/composables/__tests__/ and __node_tests__/

## Archive Removal

- 11 files in views/converted.archive/
- Zero imports found — completely dead

## Suggested Build Order

| Order | Task | Rationale |
|-------|------|-----------|
| 1 | Archive Removal (STRU-05) | Easiest win, zero imports |
| 2 | Entry Consolidation (STRU-03) | Small scope, verify status |
| 3 | F821 Top-20 (LINT-05a) | 70%+ of errors in 20 files |
| 4 | Composables Migration (STRU-04) | Highest complexity, full attention |
| 5 | F821 Long Tail (LINT-05b) | Remaining 42 files, routine |

---
*Architecture research complete: 2026-04-08*
