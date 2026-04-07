---
wave: 1
depends_on: []
files_modified:
  - core.py
  - data_access.py
  - monitoring.py
  - src/core.py
  - src/data_access.py
requirements_addressed: [NAME-04]
autonomous: true
must_haves:
  - All three root-level shims deleted
  - src/core.py imports directly from src/core/ (no longer chains through root shim)
  - src/data_access.py has deprecation warning
  - python -c "from src.core import DataClassification" succeeds
---

# Plan 01: Root Shim Disposition (NAME-04)

**Objective:** Remove all three root-level shim files (zero callers) and add deprecation warnings to src/ internal re-exports (20+ callers each).

## Task 1: Complete caller inventory then remove root-level shim files

<read_first>
- `core.py` (root) — current shim content
- `data_access.py` (root) — current shim content
- `monitoring.py` (root) — current shim content
- `src/core.py` — imports `from core import *` (chains through root shim)
- `scripts/dev/project/update_imports.py` — references shim import patterns (migration utility)
- `scripts/dev/fix_test_imports.py` — references shim import patterns
- `Dockerfile*` — check for `FROM` or `COPY` referencing root shims
- `docker-compose*.yml` — check for volume mounts or env vars referencing root shims
- `.github/workflows/*.yml` — check for CI steps referencing root shims
</read_first>

<action>
1. **Complete caller inventory (ROADMAP 4a step 1):** Before any deletion, grep ALL caller surfaces:
   ```bash
   # Python imports
   grep -rn "from core import\|import core\b" --include="*.py" --exclude-dir=".worktrees" --exclude-dir="archive" --exclude-dir="__pycache__" .
   grep -rn "from data_access import\|import data_access\b" --include="*.py" --exclude-dir=".worktrees" --exclude-dir="archive" --exclude-dir="__pycache__" .
   grep -rn "from monitoring import\|import monitoring\b" --include="*.py" --exclude-dir=".worktrees" --exclude-dir="archive" --exclude-dir="__pycache__" .

   # Non-Python callers (scripts, Docker, CI)
   grep -rn "core\.\|data_access\.\|monitoring\." --include="*.sh" --include="*.yml" --include="*.yaml" --include="Dockerfile*" --include="docker-compose*" .
   ```
   Research found zero active callers for all three root shims. Verify this is still true before proceeding.

2. Fix circular import chain in `src/core.py`:
   - Current line: `from core import *  # noqa: F401, F403`
   - Read `src/core/__init__.py` to see what it exports, then update `src/core.py` to import directly from `src.core.{module}` packages instead of the root shim
   - The exact import list depends on what `src/core/__init__.py` exports — read it first

3. After fixing src/core.py AND confirming zero callers from step 1, delete root shims:
   - `git rm core.py`
   - `git rm data_access.py`
   - `git rm monitoring.py`
</action>

<acceptance_criteria>
- Caller inventory completed: grep results recorded showing zero active callers for all three root shims
- `ls core.py data_access.py monitoring.py` returns "No such file or directory" for all three
- `grep -n "from core import" src/core.py` returns nothing (no root shim reference)
- `cd /opt/claude/mystocks_spec && PYTHONPATH=. python -c "from src.core import DataClassification; print('OK')"` exits 0 and prints "OK"
- `cd /opt/claude/mystocks_spec && PYTHONPATH=. python -c "from src.data_access import PostgreSQLDataAccess; print('OK')"` exits 0 and prints "OK"
</acceptance_criteria>

## Task 2: Add deprecation warnings to src/ internal re-exports

<read_first>
- `src/core.py` — internal re-export shim (after Task 1 fix)
- `src/data_access.py` — internal re-export shim
</read_first>

<action>
1. In `src/core.py`, add at the top (after any existing docstring):
```python
import warnings
warnings.warn(
    "src.core is a compatibility shim. Import directly from src.core.{module} instead.",
    DeprecationWarning,
    stacklevel=2
)
```

2. In `src/data_access.py`, add at the top (after any existing docstring):
```python
import warnings
warnings.warn(
    "src.data_access is a compatibility shim. Import directly from src.data_access.{module} instead.",
    DeprecationWarning,
    stacklevel=2
)
```
</action>

<acceptance_criteria>
- `src/core.py` contains `warnings.warn` and `DeprecationWarning`
- `src/data_access.py` contains `warnings.warn` and `DeprecationWarning`
- `grep -c "DeprecationWarning" src/core.py` returns 1 or more
- `grep -c "DeprecationWarning" src/data_access.py` returns 1 or more
- `PYTHONPATH=. python -c "from src.core import DataClassification; print('OK')"` still exits 0 (with deprecation warning on stderr)
</acceptance_criteria>

## Verification

```bash
# Root shims gone
ls core.py data_access.py monitoring.py 2>&1 | grep -c "No such file" | grep -q 3

# Imports still work
cd /opt/claude/mystocks_spec && PYTHONPATH=. python -c "from src.core import DataClassification; print('OK')"
cd /opt/claude/mystocks_spec && PYTHONPATH=. python -c "from src.data_access import PostgreSQLDataAccess; print('OK')"

# ROADMAP startup-level check (per Phase 4 sub-stage 4a step 5)
cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('OK')"

# No new lint errors
ruff check src/core.py src/data_access.py
```
