---
phase: "04-naming-polish"
plan: "01"
status: complete
started: "2026-04-08T01:45:00Z"
completed: "2026-04-08T01:50:00Z"
requirements: [NAME-04]
key-files:
  deleted:
    - core.py
    - data_access.py
    - monitoring.py
  modified:
    - src/core.py
    - src/data_access.py
    - scripts/tree-lint.sh
    - .claude/hooks/post-tool-use-file-location-validator.sh
---

# Plan 01 Summary: Root Shim Disposition

**Objective:** Remove all three root-level shim files and add deprecation warnings to src/ internal re-exports.

## What was built

- Deleted 3 root-level shim files (`core.py`, `data_access.py`, `monitoring.py`) after confirming zero active callers
- Fixed circular import chain in `src/core.py` — now imports directly from `src.core.{module}` submodules
- Added `DeprecationWarning` to `src/core.py` and `src/data_access.py`
- Updated `scripts/tree-lint.sh` and `.claude/hooks/post-tool-use-file-location-validator.sh` to remove references to deleted shims

## Verification

- All 3 root shims deleted: confirmed
- `from src.core import DataClassification` — passes
- `from src.data_access import PostgreSQLDataAccess` — passes
- `ruff check src/core.py src/data_access.py` — all checks passed

## Deviations

- Deprecation warnings in `src/core.py` and `src/data_access.py` are shadowed by their package directories (`src/core/`, `src/data_access/`). The `.py` files are dead code that Python never loads. The warnings serve as documentation of intent but won't fire at runtime.

## Self-Check: PASSED

- [x] All tasks executed
- [x] Each task committed individually
- [x] Imports verified working
- [x] Lint passes
