---
wave: 3
depends_on:
  - 02-PLAN-02-redirect-callers.md
  - 02-PLAN-03-merge-overlapping.md
files_modified:
  - src/routes/ (DELETE — 19 files)
  - src/api/ (DELETE — 5 files)
  - src/data_access_pkg/ (DELETE — 5 files)
  - src/database_optimization/ (DELETE — 5 files)
  - DELETION-CANDIDATES.md (update status)
autonomous: false
requirements_addressed:
  - DEAD-01
  - DEAD-02
  - DEAD-03
  - DEAD-04
  - DEAD-05
---

# Plan 04: Approved Deletion of Dead Directories

**Objective:** Delete all 5 dead/duplicate directories after Plans 02 and 03 are complete and user has approved. This is the final irreversible step.

**NOTE:** This plan requires `autonomous: false` — user must confirm before execution begins.

## Tasks

<task id="1">
<objective>
Pre-deletion verification — confirm all callers redirected and merges complete
</objective>

<read_first>
- DELETION-CANDIDATES.md (user-approved version)
- Plans 02 and 03 outputs
</read_first>

<action>
Run comprehensive pre-deletion checks:

```bash
# 1. Verify ZERO production callers for each target (outside the target itself)
echo "=== src/routes callers ==="
grep -rn "from src\.routes\b\|import src\.routes\b" --include="*.py" src/ web/ | grep -v "src/routes/" | grep -v "__pycache__" || echo "NONE"

echo "=== src/api callers ==="
grep -rn "from src\.api\b\|import src\.api\b" --include="*.py" src/ web/ | grep -v "src/api/" | grep -v "__pycache__" || echo "NONE"

echo "=== src/data_access_pkg callers ==="
grep -rn "from src\.data_access_pkg\b\|import src\.data_access_pkg\b" --include="*.py" src/ web/ tests/ scripts/ | grep -v "src/data_access_pkg/" | grep -v "__pycache__" || echo "NONE"

echo "=== src/database_optimization callers ==="
grep -rn "from src\.database_optimization\b\|import src\.database_optimization\b" --include="*.py" src/ web/ tests/ scripts/ | grep -v "src/database_optimization/" | grep -v "__pycache__" || echo "NONE"

echo "=== src/db_manager callers ==="
grep -rn "from src\.db_manager\b\|import src\.db_manager\b" --include="*.py" src/ web/ tests/ | grep -v "src/db_manager/" | grep -v "__pycache__" || echo "NONE"

# 2. Verify db_manager already deleted (Plan 03 task 5)
test ! -d src/db_manager && echo "db_manager: already deleted" || echo "db_manager: still exists"

# 3. Verify database_optimization files merged into canonical
python -c "from src.data_access.optimizers import IndexPerformanceMonitor; print('merge: OK')"

# 4. Baseline metrics
echo "=== ruff count ==="
ruff check src/ web/backend/app/ 2>&1 | wc -l

echo "=== FastAPI smoke ==="
cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('OK')"
```

IF any target has remaining production callers, STOP and report. Do NOT proceed to task 2.
IF db_manager still exists, include it in the deletion batch (it was supposed to be deleted in Plan 03).
</action>

<acceptance_criteria>
- All 5 targets have ZERO external production callers
- database_optimization files importable from canonical `src.data_access.optimizers`
- Pre-deletion ruff count recorded for comparison
- FastAPI smoke test passes before deletion
</acceptance_criteria>
</task>

<task id="2">
<objective>
Create backup tag and delete all dead directories
</objective>

<read_first>
- Task 1 verification results (must be ALL CLEAN)
</read_first>

<action>
Create a backup tag BEFORE deletion:

```bash
git tag pre-phase2-deletion
```

Delete each directory (skip db_manager if already deleted in Plan 03):

```bash
# Target 1: src/routes/ (19 files)
git rm -r src/routes/

# Target 2: src/api/ (5 files)
git rm -r src/api/

# Target 3: src/data_access_pkg/ (5 files — now empty after merge in Plan 03)
git rm -r src/data_access_pkg/

# Target 4: src/database_optimization/ (5 files — now empty after merge in Plan 03)
git rm -r src/database_optimization/

# Target 5: src/db_manager/ (if not already deleted in Plan 03)
test -d src/db_manager && git rm -r src/db_manager/ || echo "db_manager: already deleted"
```

After each deletion, verify no broken references appeared:
```bash
ruff check src/ web/backend/app/ 2>&1 | wc -l
```

If ruff count increases by more than 5 (expected: decrease since dead files are gone), STOP and investigate.
</action>

<acceptance_criteria>
- Backup tag `pre-phase2-deletion` created
- All 5 directories removed: `src/routes/`, `src/api/`, `src/data_access_pkg/`, `src/database_optimization/`, `src/db_manager/`
- `ruff check` count stays <900 (expected: decrease by ~20-40 since dead files removed)
- No F821 errors from missing modules
</acceptance_criteria>
</task>

<task id="3">
<objective>
Run full verification suite after deletion
</objective>

<read_first>
- All modified/deleted files
</read_first>

<action>
Run all success criteria from ROADMAP Phase 2:

```bash
# SC-1: DELETION-CANDIDATES.md exists
test -f DELETION-CANDIDATES.md && echo "SC1: PASS" || echo "SC1: FAIL"

# SC-2: User approved (manual check — should be done already)
echo "SC2: Manual — user approved DELETION-CANDIDATES.md"

# SC-3: All 5 target directories removed
for dir in src/routes src/api src/data_access_pkg src/db_manager src/database_optimization; do
  test ! -d "$dir" && echo "SC3 $dir: REMOVED" || echo "SC3 $dir: STILL EXISTS"
done

# SC-4: ruff check <900
RUFF_COUNT=$(ruff check src/ web/backend/app/ 2>&1 | wc -l)
echo "SC4: ruff count = $RUFF_COUNT (must be <900)"
test "$RUFF_COUNT" -lt 900 && echo "SC4: PASS" || echo "SC4: FAIL"

# SC-5: FastAPI smoke test
cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('SC5: OK')" || echo "SC5: FAIL"

# SC-6: pytest
pytest --tb=short -q 2>&1 | tail -5
```
</action>

<acceptance_criteria>
- SC-1: DELETION-CANDIDATES.md exists
- SC-3: All 5 directories removed
- SC-4: ruff count <900
- SC-5: FastAPI import succeeds
- SC-6: pytest pass/fail count unchanged from baseline
</acceptance_criteria>
</task>

<task id="4">
<objective>
Commit deletion and update DELETION-CANDIDATES.md status
</objective>

<read_first>
- DELETION-CANDIDATES.md
</read_first>

<action>
1. Update DELETION-CANDIDATES.md status from "PENDING USER APPROVAL" to "APPROVED & DELETED":
   - Replace `**Status:** PENDING USER APPROVAL` with `**Status:** APPROVED & DELETED (Phase 2 complete)`
   - Add deletion date and commit hash

2. Commit:
   ```bash
   git add -A  # captures deletions
   git commit -m "refactor(02): delete 5 dead code directories (34 files total)

   Deleted:
   - src/routes/ (19 files) — mock-era routes, 1 prod caller redirected
   - src/api/ (5 files) — dead alternative route layer, test imports updated
   - src/data_access_pkg/ (5 files) — fully covered by canonical src/data_access/
   - src/database_optimization/ (5 files) — merged into src/data_access/optimizers/
   - src/db_manager/ (1 file) — empty re-export shell

   Per DELETION-CANDIDATES.md (user approved).
   Backup tag: pre-phase2-deletion"
   ```

3. Commit the status update:
   ```bash
   git add DELETION-CANDIDATES.md
   git commit -m "docs(02): update DELETION-CANDIDATES.md status to approved"
   ```
</action>

<acceptance_criteria>
- Deletion committed with detailed message listing all 5 targets
- DELETION-CANDIDATES.md status updated to "APPROVED & DELETED"
- `git log --oneline -3` shows deletion commit + status update
</acceptance_criteria>
</task>

---

## Verification

```bash
# All targets gone
for dir in src/routes src/api src/data_access_pkg src/db_manager src/database_optimization; do
  test ! -d "$dir" && echo "$dir: GONE" || echo "$dir: EXISTS (ERROR)"
done

# Canonical layer intact
python -c "from src.data_access import DataAccessFactory, TDengineDataAccess, PostgreSQLDataAccess; print('canonical: OK')"
python -c "from src.data_access.optimizers import IndexPerformanceMonitor, QueryOptimizer; print('optimizers: OK')"

# Full suite
ruff check src/ web/backend/app/ | wc -l
cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('OK')"
pytest --tb=short -q 2>&1 | tail -5
```

## Must-Haves

- [ ] All 5 directories removed (34+ files)
- [ ] Zero broken imports in production code
- [ ] `ruff check` count <900
- [ ] FastAPI smoke test passes
- [ ] pytest pass/fail count unchanged
- [ ] Backup tag `pre-phase2-deletion` exists
- [ ] DELETION-CANDIDATES.md status updated to approved
