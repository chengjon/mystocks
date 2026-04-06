# Phase 1: Python Lint Baseline - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Eliminate the duplicate adapter layer (`src/interfaces/adapters/`) and auto-fix ruff errors to establish a clean Python lint baseline. Pure Python scope — no frontend work. Target: reduce ruff errors from ~1,456 to <50.

</domain>

<decisions>
## Implementation Decisions

### Adapter Layer Disposition
- **D-01:** Delete `src/interfaces/adapters/` entirely — full deletion, no Protocol stub conversion
- **D-02:** Keep `src/interfaces/` root files (`data_source.py`, `refactored_interfaces.py`, `business_data_source.py`, `relational_data_source.py`, `timeseries_data_source.py`, `data_source_interface.py`) — these define `IDataSource` and other interfaces that real adapters import from
- **D-03:** Keep `src/interfaces/api/`, `src/interfaces/cli/`, `src/interfaces/websocket/` — other interface definitions, not duplicates
- **Evidence:** Only 2 imports found from `src.interfaces.adapters` — both are self-imports within the duplicate layer itself. Real adapters import from `src.interfaces.data_source` and `src.interfaces.refactored_interfaces`, NOT from `src.interfaces.adapters`

### Auto-Fix Scope
- **D-04:** Auto-fix safe ruff rules: F401 (unused-import), F841 (unused-variable), W291 (trailing-whitespace), W293 (blank-line-whitespace), E701 (multiple-statements) — total ~237 fixable errors
- **D-05:** Do NOT auto-fix F811 (redefined-while-unused), E722 (bare-except), F601 (multi-value-repeated-key), F823 (undefined-local) — these need manual review
- **D-06:** Do NOT auto-fix F403 (undefined-local-with-import-star) — needs manual review of wildcard imports

### Remaining F821 Strategy
- **D-07:** Deleting `src/interfaces/adapters/` eliminates ~1,000+ F821 errors (the duplicate layer with missing imports)
- **D-08:** Remaining F821 errors in real code (`src/adapters/`, `src/advanced_analysis/`, etc.) are NOT auto-fixable — each needs investigation
- **D-09:** Phase 1 goal is <50 ruff errors total, not zero. Remaining F821 errors beyond the adapter deletion should be documented but not all fixed in this phase

### Verification Approach
- **D-10:** After adapter deletion: `grep -r "from src.interfaces.adapters\|import src.interfaces.adapters" --include="*.py" src/ web/ tests/ scripts/` must return empty
- **D-11:** After auto-fix: `python -c "from web.backend.app.main import app; print('OK')"` must succeed
- **D-12:** After all changes: `pytest --tb=short` must pass (same pass/fail count as baseline)
- **D-13:** Baseline pytest pass/fail count to be captured before any changes

### Execution Order
- **D-14:** Step 1: Capture baseline (ruff count, pytest pass/fail count)
- **D-15:** Step 2: Delete `src/interfaces/adapters/` (verify zero external imports first)
- **D-16:** Step 3: Run `ruff check --fix --select F401,F841,W291,W293,E701`
- **D-17:** Step 4: Run full `ruff check` — document remaining errors
- **D-18:** Step 5: Run verification suite (import smoke test + pytest)

### Claude's Discretion
- Exact ruff version to use (as long as it's 0.11+)
- Whether to fix any remaining F821 errors individually during this phase
- How to handle backup files found in `src/interfaces/adapters/` (*.backup_* files)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 1 Scope
- `.planning/ROADMAP.md` §Phase 1 — Phase boundary, requirements, success criteria
- `.planning/REQUIREMENTS.md` §Lint Baseline — LINT-01, LINT-02, LINT-03
- `.planning/codebase/CONCERNS.md` — Issue #1 (P0: Duplicate adapters), #12 (Ruff breakdown)
- `.planning/research/PITFALLS.md` — P-02 (unsafe auto-fix), P-07 (hidden adapter dependents)
- `.planning/research/STACK.md` — Recommended cleanup tools and execution order

### Project Governance
- `architecture/STANDARDS.md` — Migration governance rules, deletion approval process

</canonical_refs>

<code_context>
## Existing Code Insights

### The Duplicate Layer
- `src/interfaces/adapters/` — 30+ files, exact copies of `src/adapters/` but missing all import statements
- Contains `.backup_*` files (2 found) — artifacts from previous edits
- Contains `test_*` files — test files mixed into source directory
- Only 2 self-imports exist, both within the duplicate layer itself

### The Real Interface Layer (KEEP)
- `src/interfaces/data_source.py` — defines `IDataSource` interface
- `src/interfaces/refactored_interfaces.py` — defines `IDataSource` (alternate)
- Real adapters import from these: `src/adapters/tushare_adapter.py`, `src/adapters/akshare/base.py`, `src/adapters/financial/*.py`, `src/adapters/tdx/*.py` (11 files total)

### Current Ruff Error Distribution
| Rule | Count | Fixable in Phase 1? |
|------|-------|-------------------|
| F821 (undefined-name) | 1,173 | Yes — delete adapters removes ~1,000+; remaining documented |
| W293 (blank-line-whitespace) | 95 | Yes — auto-fix |
| F841 (unused-variable) | 78 | Yes — auto-fix |
| W291 (trailing-whitespace) | 28 | Yes — auto-fix |
| F401 (unused-import) | 21 | Yes — auto-fix |
| F811 (redefined-while-unused) | 17 | No — manual review needed |
| E701 (multiple-statements) | 15 | Yes — auto-fix |
| E722 (bare-except) | 13 | No — manual review needed |
| F601, F823, F403, E741, F402 | 16 | No — manual review needed |

### Integration Points
- `src/adapters/` imports from `src/interfaces/data_source.py` — this dependency must be preserved
- `web/backend/app/` has its own ruff errors (mostly same categories)
- Tests in `tests/` are NOT checked by ruff currently (scoping decision for later)

</code_context>

<specifics>
## Specific Ideas

- Deleting `src/interfaces/adapters/` is the single highest-impact action — eliminates ~1,000+ errors at once
- After deletion, running `ruff check --fix` on safe rules will handle another ~237 errors
- Remaining ~200 errors (F811, E722, residual F821) are documentation items for later phases

</specifics>

<deferred>
## Deferred Ideas

- Fixing ALL ruff errors to zero — deferred to Phase 4 (Naming & Polish)
- Frontend case-conflict merge — Phase 3
- Reorganizing the 205-file backend API directory — out of scope entirely

</deferred>

---
*Phase: 01-python-lint-baseline*
*Context gathered: 2026-04-06*
