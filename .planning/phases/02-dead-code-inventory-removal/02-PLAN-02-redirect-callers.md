---
wave: 2
depends_on:
  - 02-PLAN-01-inventory.md
files_modified:
  - src/database/services/database_service.py
  - tests/api_contract_tests.py
  - scripts/cicd_pipeline.sh
  - scripts/dev/quality_gate/fix_test_imports.py
  - scripts/dev/project/update_imports.py
  - scripts/dev/fix_test_imports.py
autonomous: true
requirements_addressed:
  - DEAD-01
  - DEAD-02
  - DEAD-04
---

# Plan 02: Caller Redirection

**Objective:** Redirect all known callers of `src/routes/`, `src/api/`, and `src/db_manager/` to their canonical equivalents. No deletions yet — only import path updates.

## Tasks

<task id="1">
<objective>
Redirect production caller: database_service.py → canonical route import
</objective>

<read_first>
- src/database/services/database_service.py (specifically line 155)
- web/backend/app/api/ — find the canonical equivalent of wencai_routes functions
</read_first>

<action>
In `src/database/services/database_service.py` at line 155:

Current:
```python
from src.routes.wencai_routes import execute_custom_query, get_query_results
```

1. First verify what `execute_custom_query` and `get_query_results` do in `src/routes/wencai_routes.py`
2. Find their canonical equivalent in `web/backend/app/api/` — search:
   ```bash
   grep -rn "def execute_custom_query\|def get_query_results" --include="*.py" web/backend/
   ```
3. If canonical equivalent exists, replace the import:
   ```python
   from web.backend.app.api.[module] import execute_custom_query, get_query_results
   ```
4. If NO canonical equivalent exists, the import is dead — check if `execute_custom_query` and `get_query_results` are actually used in this file:
   ```bash
   grep -n "execute_custom_query\|get_query_results" src/database/services/database_service.py
   ```
   If not used, delete the import line entirely (per D-04: mark with comment if needed).
5. Run `ruff check src/database/services/database_service.py` to verify no new errors.
</action>

<acceptance_criteria>
- `src/database/services/database_service.py` no longer imports from `src.routes.wencai_routes`
- `ruff check src/database/services/database_service.py` shows no new F821 errors
- If functions are unused, import line is removed (not commented out)
</acceptance_criteria>
</task>

<task id="2">
<objective>
Redirect test caller: api_contract_tests.py → canonical type imports
</objective>

<read_first>
- tests/api_contract_tests.py (specifically lines 21-23)
- src/api/types/ — verify what types are exported
- web/backend/app/ — search for canonical type definitions
</read_first>

<action>
In `tests/api_contract_tests.py` at lines 21-23:

Current:
```python
from src.api.types.common import APIResponse
from src.api.types.market import MarketOverview, MarketOverviewData
from src.api.types.strategy import BacktestRequest, BacktestResponse, StrategyInfo
```

1. Verify `src/api/types/` directory exists and contains these modules:
   ```bash
   ls -la src/api/types/ 2>/dev/null
   ```
2. Search for canonical equivalents:
   ```bash
   grep -rn "class APIResponse\|class MarketOverview\|class BacktestRequest\|class BacktestResponse\|class StrategyInfo" --include="*.py" web/backend/ src/
   ```
3. If types are ONLY defined in `src/api/types/`, they need to be moved to a canonical location first (probably `src/domain/` or `web/backend/app/schemas/`).
4. If types exist elsewhere, update imports to canonical location.
5. If types are ONLY used in this test and nowhere in production, add `@pytest.mark.skip` with reason `"Types from dead src/api/ layer — needs migration"` per D-04.
6. Run `ruff check tests/api_contract_tests.py` to verify.
</action>

<acceptance_criteria>
- `tests/api_contract_tests.py` no longer imports from `src.api.types.*` (or test is skipped with reason)
- No new ruff errors introduced
</acceptance_criteria>
</task>

<task id="3">
<objective>
Redirect CI/CD reference: cicd_pipeline.sh
</objective>

<read_first>
- scripts/cicd_pipeline.sh (specifically line 184)
</read_first>

<action>
In `scripts/cicd_pipeline.sh` at line 184:

Current: `from src.routes import *`

1. Read surrounding context (lines 175-195) to understand what this smoke test checks
2. Replace with canonical import check:
   ```python
   from web.backend.app.api import router  # or whatever the canonical entry is
   ```
3. If the check is obsolete (just verifying routes exist, and web/backend/ has its own), replace with:
   ```python
   from web.backend.app.main import app  # canonical FastAPI app
   ```
4. Verify the script runs: `bash -n scripts/cicd_pipeline.sh` (syntax check)
</action>

<acceptance_criteria>
- `scripts/cicd_pipeline.sh` no longer references `src.routes`
- Script passes bash syntax check
</acceptance_criteria>
</task>

<task id="4">
<objective>
Clean up dev script import mapping rules for dead targets
</objective>

<read_first>
- scripts/dev/quality_gate/fix_test_imports.py (lines around 41-46)
- scripts/dev/project/update_imports.py (lines around 16-27)
- scripts/dev/fix_test_imports.py (lines around 8-29)
</read_first>

<action>
These scripts contain import-mapping dictionaries. They map old import patterns to `src.routes.*`, `src.api.*`, `src.db_manager.*` patterns.

For `scripts/dev/quality_gate/fix_test_imports.py`:
- Line 41: `'from routes.': 'from src.routes.'` — REMOVE this mapping rule (or comment out with `# DEPRECATED: src/routes/ deleted in Phase 2`)
- Line 42: `'from api.': 'from src.api.'` — REMOVE this mapping rule
- Line 46: `'from database_optimization.': 'from src.database_optimization.'` — UPDATE to `'from database_optimization.': 'from src.data_access.optimizers.'`

For `scripts/dev/project/update_imports.py`:
- Lines 16, 27: `"from db_manager"` / `"import db_manager"` mappings — REMOVE or update to point to `src.storage.database`

For `scripts/dev/fix_test_imports.py`:
- Lines 8, 28-29: db_manager patterns — REMOVE or update to `src.storage.database`
- Line 32: `'from db_manager.': 'from src.db_manager.'` — REMOVE or update

Also check and update `scripts/dev/quality_gate/fix_test_imports.py` line 8 for the same pattern.

Run `ruff check scripts/dev/` after all changes.
</action>

<acceptance_criteria>
- No dev script maps to `src.routes`, `src.api`, or `src.db_manager` as import targets
- database_optimization mappings redirect to `src.data_access.optimizers`
- `ruff check scripts/dev/` shows no new errors
</acceptance_criteria>
</task>

<task id="5">
<objective>
Run verification after all redirections
</objective>

<read_first>
- All modified files from tasks 1-4
</read_first>

<action>
Run verification suite:
```bash
# Lint check
ruff check src/ web/backend/app/ | wc -l

# Verify no remaining imports to dead targets (production code only)
grep -rn "from src\.routes\b\|import src\.routes\b" --include="*.py" src/ web/ | grep -v "src/routes/" | grep -v "__pycache__"
grep -rn "from src\.api\b\|import src\.api\b" --include="*.py" src/ web/ | grep -v "src/api/" | grep -v "__pycache__"
grep -rn "from src\.db_manager\b\|import src\.db_manager\b" --include="*.py" src/ web/ | grep -v "src/db_manager/" | grep -v "__pycache__"

# FastAPI smoke test
cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('OK')"

# Run tests
pytest --tb=short -q 2>&1 | tail -5
```
</action>

<acceptance_criteria>
- `ruff check` count still <900
- Zero production imports of `src.routes.*`, `src.api.*`, `src.db_manager.*` outside the target directories themselves
- FastAPI smoke test prints "OK"
- `pytest` pass/fail count unchanged from Phase 1 baseline
</acceptance_criteria>
</task>

---

## Verification

```bash
# Zero external callers remaining for routes/api/db_manager
! grep -rn "from src\.routes\b\|import src\.routes\b" --include="*.py" src/ web/ | grep -v "src/routes/" | grep -vq . && echo "routes: CLEAN" || echo "routes: CALLERS REMAIN"
! grep -rn "from src\.api\b\|import src\.api\b" --include="*.py" src/ web/ | grep -v "src/api/" | grep -vq . && echo "api: CLEAN" || echo "api: CALLERS REMAIN"
! grep -rn "from src\.db_manager\b\|import src\.db_manager\b" --include="*.py" src/ web/ | grep -v "src/db_manager/" | grep -vq . && echo "db_manager: CLEAN" || echo "db_manager: CALLERS REMAIN"
```

## Must-Haves

- [ ] Zero production callers of `src.routes.*` outside src/routes/ itself
- [ ] Zero production callers of `src.api.*` outside src/api/ itself
- [ ] Zero production callers of `src.db_manager.*` outside src/db_manager/ itself
- [ ] `ruff check` count <900
- [ ] FastAPI smoke test passes
- [ ] Dev script mapping rules updated (not pointing to dead layers)
