---
phase: 08-adapters-f821-resolution
plan: 08-01
subsystem: lint
tags: [ruff, f821, akshare, adapters]

requires: []
provides:
  - Zero F821 errors in src/adapters/akshare/
affects: [lint, adapters]

tech-stack:
  added: []
  patterns: [import-only-fix]

key-files:
  created: []
  modified:
    - src/adapters/akshare/index_daily.py
    - src/adapters/akshare/industry_data.py
    - src/adapters/akshare/misc_data/get_futures_index_daily.py
    - src/adapters/akshare/misc_data/get_ths_industry_names.py
    - src/adapters/akshare/realtime_data.py
    - src/adapters/akshare/stock_basic.py
    - src/adapters/akshare/stock_daily.py

key-decisions:
  - "Added logging, pandas, akshare, and utility imports per plan specification"

patterns-established:
  - "Mixin module import pattern: stdlib → third-party → local, logger after imports"

requirements-completed: [LINT-05]

duration: 5min
completed: 2026-04-10
---

# Plan 08-01: Akshare Adapters F821 Fix Summary

**Added missing imports to 7 akshare adapter files, resolving 236 F821 (undefined name) errors — zero logic changes**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-10T01:28:00Z
- **Completed:** 2026-04-10T01:33:00Z
- **Tasks:** 8 (7 file fixes + 1 verification)
- **Files modified:** 7

## Accomplishments
- Resolved all 236 F821 errors in akshare adapter directory
- Verified zero new error categories introduced (baseline: 0 non-F821)
- Confirmed all changes are import-only (no logic modifications)

## Task Commits

1. **Tasks 1-7: Fix imports in 7 akshare files** - `5b4e68939` (fix)

## Files Created/Modified
- `src/adapters/akshare/index_daily.py` - Added logging, pd, ak, normalize_date, format_index_code_for_source
- `src/adapters/akshare/industry_data.py` - Added logging, pd, ak (linter removed unused ColumnMapper/format_stock_code_for_source)
- `src/adapters/akshare/misc_data/get_futures_index_daily.py` - Added logging, pd, ak
- `src/adapters/akshare/misc_data/get_ths_industry_names.py` - Added logging, pd, ak
- `src/adapters/akshare/realtime_data.py` - Added logging, typing, pd, ak, normalize_date
- `src/adapters/akshare/stock_basic.py` - Added logging, typing, pd, ak, ColumnMapper, format_stock_code_for_source
- `src/adapters/akshare/stock_daily.py` - Added logging, datetime, pd, ak, ColumnMapper, normalize_date, format_stock_code_for_source

## Decisions Made
- Followed plan exactly — added only the imports specified, no extra changes
- Linter auto-removed unused imports in industry_data.py (ColumnMapper, format_stock_code_for_source were not needed there)

## Deviations from Plan
None — plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None

## Next Phase Readiness
- Akshare adapters F821-clean, ready for combined LINT-05 verification with Plan 08-02

---
*Phase: 08-adapters-f821-resolution*
*Completed: 2026-04-10*
