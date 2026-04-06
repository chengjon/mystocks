---
phase: 01-python-lint-baseline
wave: 1
depends_on: []
files_modified:
  - src/interfaces/adapters/ (DELETE ENTIRE DIRECTORY)
  - src/**/*.py (auto-fix whitespace/unused-variable)
  - web/backend/app/**/*.py (auto-fix whitespace/unused-variable)
requirements_addressed:
  - LINT-01
  - LINT-02
  - LINT-03
autonomous: true
---

# Plan 01: Delete Duplicate Adapters + Auto-Fix Ruff

**Objective:** Eliminate `src/interfaces/adapters/` and auto-fix safe ruff rules to reduce errors from ~1,456 to <900.

**Note on target adjustment:** ROADMAP specifies <50 errors. Research (01-RESEARCH.md) proves this is not achievable — only 378 of 1,173 F821 errors are in the duplicate layer (not ~1,000+ as estimated). Adjusted target: <900 (~40% reduction). Remaining F821 errors are in real code and need manual investigation in future phases.

---

<task id="1">
<objective>Capture baseline measurements before any changes</objective>

<read_first>
- .planning/phases/01-python-lint-baseline/01-CONTEXT.md
- .planning/phases/01-python-lint-baseline/01-RESEARCH.md
</read_first>

<action>
1. Run `ruff check src/ web/backend/app/ --statistics > .planning/phases/01-python-lint-baseline/baseline-ruff.txt 2>&1`
2. Run `ruff check src/ web/backend/app/ --select F821,F401,F841,F811,W291,W293,E701,E722 --statistics >> .planning/phases/01-python-lint-baseline/baseline-ruff.txt 2>&1`
3. Run `pytest --co -q 2>&1 | tail -3 > .planning/phases/01-python-lint-baseline/baseline-pytest.txt`
4. Record expected values: ~1,456 ruff errors, ~1,694 pytest tests collected, 5 collection errors
</action>

<acceptance_criteria>
- File `.planning/phases/01-python-lint-baseline/baseline-ruff.txt` exists and contains `1173 F821` and `1456` total error lines
- File `.planning/phases/01-python-lint-baseline/baseline-pytest.txt` exists and contains `1694 tests collected`
- Both files committed to git
</acceptance_criteria>
</task>

<task id="2">
<objective>Verify zero external imports of src.interfaces.adapters, then delete the directory</objective>

<read_first>
- .planning/phases/01-python-lint-baseline/01-CONTEXT.md (D-01, D-02, D-03, D-10)
- .planning/phases/01-python-lint-baseline/01-RESEARCH.md (Dimension 7)
</read_first>

<action>
1. Run verification grep: `grep -r "from src.interfaces.adapters\|import src.interfaces.adapters" --include="*.py" src/ web/ tests/ scripts/`
2. Confirm output contains ONLY self-imports (2 lines from within `src/interfaces/adapters/` itself):
   - `src/interfaces/adapters/financial_adapter_example.py:from src.interfaces.adapters.financial import FinancialDataSource`
   - `src/interfaces/adapters/test_financial_adapter.py:from src.interfaces.adapters.financial import FinancialDataSource`
3. If any EXTERNAL imports found (outside `src/interfaces/adapters/`): STOP and report — do not delete.
4. If only self-imports: delete the entire directory: `rm -rf src/interfaces/adapters/`
5. Verify deletion: `test ! -d src/interfaces/adapters/ && echo "DELETED OK"`
6. Verify grep returns empty post-deletion: `grep -r "from src.interfaces.adapters\|import src.interfaces.adapters" --include="*.py" src/ web/ tests/ scripts/` (must return empty)
7. Commit: `git add -A src/interfaces/adapters/ && git commit -m "refactor: delete duplicate adapter layer src/interfaces/adapters/"`
</action>

<acceptance_criteria>
- `test -d src/interfaces/adapters/` returns non-zero (directory does not exist)
- `grep -r "from src.interfaces.adapters\|import src.interfaces.adapters" --include="*.py" src/ web/ tests/ scripts/` returns empty output
- Git commit exists with message containing "delete duplicate adapter layer"
- `src/interfaces/data_source.py` still exists (NOT deleted)
- `src/interfaces/refactored_interfaces.py` still exists (NOT deleted)
- `src/interfaces/api/` directory still exists (NOT deleted)
</acceptance_criteria>
</task>

<task id="3">
<objective>Auto-fix whitespace and unused-variable ruff rules</objective>

<read_first>
- .planning/phases/01-python-lint-baseline/01-RESEARCH.md (Dimension 1 — tool compatibility)
- .planning/phases/01-python-lint-baseline/01-CONTEXT.md (D-04, D-05)
</read_first>

<action>
1. Run ruff auto-fix with unsafe-fixes flag (ruff 0.9.10 requires this for W293, F841, W291):
   ```
   ruff check src/ web/backend/app/ --fix --unsafe-fixes --select W293,F841,W291
   ```
   Expected: 201 fixes (95 W293 + 78 F841 + 28 W291)
2. Verify fix results: `ruff check src/ web/backend/app/ --select W293,F841,W291 --statistics`
   Expected: zero output (all fixed)
3. Stage and commit: `git add -A && git commit -m "style: auto-fix W293, F841, W291 ruff errors (201 fixes)"`
</action>

<acceptance_criteria>
- `ruff check src/ web/backend/app/ --select W293,F841,W291` exits with code 0 (zero violations)
- Git commit exists with message containing "auto-fix W293, F841, W291"
- No F821 or other errors introduced by the fixes (spot-check with `ruff check src/ web/backend/app/ --select F821 --statistics`)
</acceptance_criteria>
</task>

<task id="4">
<objective>Document remaining ruff errors and generate verification report</objective>

<read_first>
- .planning/phases/01-python-lint-baseline/baseline-ruff.txt
- .planning/phases/01-python-lint-baseline/01-RESEARCH.md (Dimension 3 — post-cleanup projection)
</read_first>

<action>
1. Run full ruff check: `ruff check src/ web/backend/app/ --statistics > .planning/phases/01-python-lint-baseline/post-cleanup-ruff.txt 2>&1`
2. Run ruff check with details for remaining F821: `ruff check src/ web/backend/app/ --select F821 2>&1 | sed 's/:.*$//' | sort | uniq -c | sort -rn | head -30 >> .planning/phases/01-python-lint-baseline/post-cleanup-ruff.txt`
3. Compare baseline vs post-cleanup totals and write summary
4. Run pytest: `pytest --tb=short 2>&1 | tail -10 > .planning/phases/01-python-lint-baseline/post-cleanup-pytest.txt`
   Note: expect same 5 collection errors as baseline — these are pre-existing
5. Run import check for preserved interfaces:
   `python -c "from src.interfaces.data_source import IDataSource; print('IDataSource OK')" 2>&1`
6. Write verification report to `.planning/phases/01-python-lint-baseline/01-VERIFICATION.md`
7. Commit all: `git add .planning/phases/01-python-lint-baseline/ && git commit -m "docs: Phase 1 verification report and post-cleanup metrics"`
</action>

<acceptance_criteria>
- File `.planning/phases/01-python-lint-baseline/post-cleanup-ruff.txt` exists with total error count <900
- File `.planning/phases/01-python-lint-baseline/01-VERIFICATION.md` exists with:
  - Baseline error count (~1,456)
  - Post-cleanup error count (<900)
  - Top F821 source files listed
  - Pytest pass/fail count matches baseline (same 5 collection errors)
- `python -c "from src.interfaces.data_source import IDataSource"` succeeds
- Git commit exists
</acceptance_criteria>
</task>

---

## Verification

<must_haves>
- `src/interfaces/adapters/` does not exist on disk
- `grep -r "from src.interfaces.adapters" --include="*.py" src/ web/ tests/ scripts/` returns empty
- `ruff check src/ web/backend/app/ --select W293,F841,W291` exits 0
- `python -c "from src.interfaces.data_source import IDataSource; print('OK')"` succeeds
- Pytest collection count unchanged (1694 tests, 5 errors)
- Total ruff errors reduced from ~1,456 to <900
</must_haves>

<success_criteria_mapping>
- SC-1 (ruff <50): ADJUSTED to <900 per research findings — F821 in real code cannot be resolved this phase
- SC-2 (adapters deleted): Met by task 2
- SC-3 (auto-fixable zero violations): PARTIALLY met — W293, F841, W291 fixed; F401 and E701 are NOT auto-fixable by ruff 0.9.10
- SC-4 (FastAPI starts): Pre-existing import error (`get_socketio_manager`) blocks this — not caused by Phase 1. Alternative: verify `src.interfaces.data_source.IDataSource` import succeeds
- SC-5 (no regressions): Met by task 4 — pytest baseline comparison
</success_criteria_mapping>

---
