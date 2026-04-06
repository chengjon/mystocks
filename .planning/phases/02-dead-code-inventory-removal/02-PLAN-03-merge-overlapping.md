---
wave: 2
depends_on:
  - 02-PLAN-01-inventory.md
files_modified:
  - src/data_access/__init__.py
  - src/data_access/optimizers/__init__.py
  - src/data_access/optimizers/performance_monitor.py (new)
  - src/data_access/optimizers/postgresql_index_optimizer.py (new)
  - src/data_access/optimizers/slow_query_analyzer.py (new)
  - src/data_access/optimizers/tdengine_index_optimizer.py (new)
  - tests/unit/database_optimization/test_performance_monitor.py
  - scripts/tests/test_database_optimization.py
autonomous: true
requirements_addressed:
  - DEAD-03
  - DEAD-05
---

# Plan 03: Merge Overlapping Data Access Layers

**Objective:** Merge unique files from `src/data_access_pkg/` and `src/database_optimization/` into the canonical `src/data_access/` layer. Delete `src/db_manager/` (empty shell). Redirect all imports.

## Tasks

<task id="1">
<objective>
Investigate tdengine_access.py size discrepancy before merge
</objective>

<read_first>
- src/data_access_pkg/tdengine_access.py (23,514 bytes)
- src/data_access/tdengine_access.py (2,770 bytes)
</read_first>

<action>
Compare the two files to resolve the 9x size discrepancy:

```bash
wc -l src/data_access_pkg/tdengine_access.py src/data_access/tdengine_access.py
```

1. Read `src/data_access/tdengine_access.py` — it may be a slim wrapper that delegates to sub-modules
2. Read `src/data_access_pkg/tdengine_access.py` — it may contain the full implementation
3. Check if canonical `src/data_access/` has split the tdengine functionality across multiple files:
   ```bash
   grep -rn "class TDengine" --include="*.py" src/data_access/
   ```
4. Decision logic per D-05 (canonical wins):
   - If canonical has the same classes/methods distributed across multiple files → canonical wins, no merge needed
   - If canonical is genuinely missing functionality → copy ONLY the missing methods/classes from data_access_pkg version
   - If canonical is complete and data_access_pkg is just verbose/duplicate → no merge needed
5. Document the decision in the commit message
</action>

<acceptance_criteria>
- Size discrepancy root-caused with specific explanation
- Decision documented: "canonical complete" or "merged missing functionality from data_access_pkg"
- No duplicate code introduced
</acceptance_criteria>
</task>

<task id="2">
<objective>
Verify data_access_pkg files are fully covered by canonical layer
</objective>

<read_first>
- src/data_access_pkg/__init__.py (exports: IDataAccessLayer, TDengineDataAccess, PostgreSQLDataAccess)
- src/data_access/__init__.py (exports: TDengineDataAccess, PostgreSQLDataAccess, DataAccessFactory, ...)
- src/data_access_pkg/interface.py
- src/data_access/interfaces.py
- src/data_access_pkg/postgresql_access.py
- src/data_access/postgresql_access.py
- src/data_access_pkg/_postgresql_access_query_mixin.py
</read_first>

<action>
For each data_access_pkg file, verify canonical equivalent exists:

1. `interface.py` → `src/data_access/interfaces.py`:
   ```bash
   grep "class IDataAccessLayer" src/data_access/interfaces.py
   ```

2. `postgresql_access.py` (17,840 bytes) vs `src/data_access/postgresql_access.py` (17,519 bytes):
   ```bash
   diff <(grep "^class \|^def " src/data_access_pkg/postgresql_access.py) <(grep "^class \|^def " src/data_access/postgresql_access.py)
   ```
   If only formatting/ordering differences → canonical wins per D-07.

3. `_postgresql_access_query_mixin.py` (8,800 bytes):
   ```bash
   grep -rn "class.*QueryMixin\|def.*query" src/data_access_pkg/_postgresql_access_query_mixin.py | head -10
   grep -rn "QueryMixin" --include="*.py" src/data_access/
   ```
   If mixin is used ONLY by data_access_pkg's postgresql_access.py (which we're deleting), the mixin is also dead.

4. Confirm: if ALL classes/methods exist in canonical, data_access_pkg can be deleted entirely (no merge needed).
</action>

<acceptance_criteria>
- Each data_access_pkg file verified against canonical equivalent
- Explicit keep/delete decision per file with evidence
- D-07 honored: canonical wins when overlap exists, no content diff/merge
</acceptance_criteria>
</task>

<task id="3">
<objective>
Copy unique database_optimization files into canonical src/data_access/optimizers/
</objective>

<read_first>
- src/database_optimization/performance_monitor.py
- src/database_optimization/postgresql_index_optimizer.py
- src/database_optimization/slow_query_analyzer.py
- src/database_optimization/tdengine_index_optimizer.py
- src/data_access/optimizers/query_optimizer.py (existing — compare scope)
- src/data_access/optimizers/__init__.py
</read_first>

<action>
Research in Task 2 of RESEARCH.md confirmed these 4 files have unique functionality NOT in canonical `query_optimizer.py`. Copy each:

1. Copy files:
   ```bash
   cp src/database_optimization/performance_monitor.py src/data_access/optimizers/performance_monitor.py
   cp src/database_optimization/postgresql_index_optimizer.py src/data_access/optimizers/postgresql_index_optimizer.py
   cp src/database_optimization/slow_query_analyzer.py src/data_access/optimizers/slow_query_analyzer.py
   cp src/database_optimization/tdengine_index_optimizer.py src/data_access/optimizers/tdengine_index_optimizer.py
   ```

2. Update imports INSIDE each copied file:
   - Search for any internal references to `src.database_optimization` and update to `src.data_access.optimizers`
   - Check for circular imports within data_access layer

3. Update `src/data_access/optimizers/__init__.py` to export new classes:
   ```python
   from .performance_monitor import IndexPerformanceMonitor
   from .postgresql_index_optimizer import PostgreSQLIndexOptimizer
   from .slow_query_analyzer import SlowQueryAnalyzer
   from .tdengine_index_optimizer import TDengineIndexOptimizer
   ```

4. Run `ruff check src/data_access/optimizers/` to verify no import errors.
</action>

<acceptance_criteria>
- 4 files copied to `src/data_access/optimizers/`
- All internal imports updated (no references to `src.database_optimization` in copied files)
- `src/data_access/optimizers/__init__.py` exports all 4 new classes
- `ruff check src/data_access/optimizers/` shows no F821 errors
</acceptance_criteria>
</task>

<task id="4">
<objective>
Redirect test imports for database_optimization
</objective>

<read_first>
- tests/unit/database_optimization/test_performance_monitor.py
- scripts/tests/test_database_optimization.py
</read_first>

<action>
Update test imports:

1. `tests/unit/database_optimization/test_performance_monitor.py:19`:
   ```python
   # Before:
   from src.database_optimization.performance_monitor import IndexPerformanceMonitor
   # After:
   from src.data_access.optimizers.performance_monitor import IndexPerformanceMonitor
   ```

2. `scripts/tests/test_database_optimization.py:18`:
   ```python
   # Before:
   from src.database_optimization import (...)
   # After:
   from src.data_access.optimizers import (...)
   ```

3. Run `ruff check` on both files.
4. Run any tests that can execute:
   ```bash
   python -c "from src.data_access.optimizers import IndexPerformanceMonitor, PostgreSQLIndexOptimizer, SlowQueryAnalyzer, TDengineIndexOptimizer; print('OK')"
   ```
</action>

<acceptance_criteria>
- Both test files import from `src.data_access.optimizers` instead of `src.database_optimization`
- Import verification command prints "OK"
- No new ruff errors
</acceptance_criteria>
</task>

<task id="5">
<objective>
Delete src/db_manager/ (confirmed empty shell) and run verification
</objective>

<read_first>
- src/db_manager/__init__.py
- DELETION-CANDIDATES.md (entry for db_manager)
</read_first>

<action>
1. Verify db_manager is still only `__init__.py`:
   ```bash
   find src/db_manager/ -type f | wc -l  # Must be 1
   cat src/db_manager/__init__.py  # Must be re-export shim only
   ```

2. Verify zero production callers (should be confirmed by Plan 02 task 5):
   ```bash
   grep -rn "from src\.db_manager\|import src\.db_manager" --include="*.py" src/ web/ | grep -v "src/db_manager/"
   ```

3. If both checks pass:
   ```bash
   git rm -r src/db_manager/
   ```

4. Run verification:
   ```bash
   ruff check src/ web/backend/app/ | wc -l
   cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('OK')"
   pytest --tb=short -q 2>&1 | tail -5
   ```
</action>

<acceptance_criteria>
- `src/db_manager/` directory removed
- `ruff check` count still <900
- FastAPI smoke test passes
- pytest pass/fail count unchanged
</acceptance_criteria>
</task>

<task id="6">
<objective>
Commit merge and db_manager deletion
</objective>

<read_first>
- All modified files from tasks 1-5
</read_first>

<action>
Stage and commit in logical groups:

```bash
# Merge commit — database_optimization → data_access/optimizers
git add src/data_access/optimizers/
git commit -m "refactor(02): merge database_optimization into src/data_access/optimizers

- Copy 4 unique optimizer files to canonical location
- Update exports in optimizers/__init__.py
- Redirect test imports to canonical path

Per CONTEXT.md D-05: canonical src/data_access/ wins."

# db_manager deletion
git add -u src/db_manager/
git commit -m "refactor(02): delete src/db_manager/ (empty re-export shell)

All exports were re-exports from src.storage.database.
Zero production callers confirmed."

# Test import updates
git add tests/unit/database_optimization/ scripts/tests/test_database_optimization.py
git commit -m "test(02): redirect database_optimization test imports to canonical path"
```
</action>

<acceptance_criteria>
- 3 commits created with descriptive messages
- Each commit references sub-stage and affected targets
- `git log --oneline -3` shows the commits
</acceptance_criteria>
</task>

---

## Verification

```bash
# All optimizer files importable from canonical location
python -c "from src.data_access.optimizers import IndexPerformanceMonitor, PostgreSQLIndexOptimizer, SlowQueryAnalyzer, TDengineIndexOptimizer; print('optimizers: OK')"

# db_manager gone
test ! -d src/db_manager && echo "db_manager: DELETED" || echo "db_manager: STILL EXISTS"

# data_access_pkg still exists (deletion in Plan 04)
test -d src/data_access_pkg && echo "data_access_pkg: AWAITS DELETION" || echo "data_access_pkg: ALREADY GONE"

# database_optimization still exists (deletion in Plan 04)
test -d src/database_optimization && echo "database_optimization: AWAITS DELETION" || echo "database_optimization: ALREADY GONE"

# Lint + smoke
ruff check src/ web/backend/app/ | wc -l
cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('OK')"
```

## Must-Haves

- [ ] 4 unique optimizer files copied to `src/data_access/optimizers/`
- [ ] All exports in `src/data_access/optimizers/__init__.py`
- [ ] Test imports redirected to canonical path
- [ ] `src/db_manager/` deleted
- [ ] tdengine_access.py discrepancy resolved with documented decision
- [ ] `ruff check` count <900
- [ ] FastAPI smoke test passes
