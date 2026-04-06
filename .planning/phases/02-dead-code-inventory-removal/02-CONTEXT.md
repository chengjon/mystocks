# Phase 2: Dead Code Inventory & Removal - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Identify, inventory, redirect callers, and remove five dead code layers: `src/routes/` (19 files), `src/api/` (5 files), `src/data_access_pkg/` (5 files), `src/db_manager/` (empty shell), `src/database_optimization/` (5 files). No deletion occurs until user approves a comprehensive DELETION-CANDIDATES.md with grep evidence AND functional tree analysis.

</domain>

<decisions>
## Implementation Decisions

### Caller Redirection Policy
- **D-01:** Redirect ALL callers — production code, tests, and dev scripts. No "leave broken" items.
- **D-02:** Fix broken tests immediately — don't defer to a later phase.
- **D-03:** Update dev script imports (`scripts/dev/fix_test_imports.py`, `scripts/dev/quality_gate/fix_test_imports.py`, `scripts/dev/project/update_imports.py`) to point to canonical locations.
- **D-04:** If a test imports from a dead-code target and the canonical replacement exists, redirect the import. If no replacement exists, mark the test as `@pytest.mark.skip` with a reason note.

### Merge Conflict Resolution
- **D-05:** Canonical `src/data_access/` always wins when files overlap.
- **D-06:** Only copy files from `src/data_access_pkg/` and `src/database_optimization/` that do NOT already exist in `src/data_access/`.
- **D-07:** If a file exists in both canonical and dead layer, do NOT diff or merge content — canonical is authoritative.

### DELETION-CANDIDATES Format
- **D-08:** One table per target directory (5 tables total).
- **D-09:** Each table row: file path, functional purpose, all callers (file:line), keep/delete recommendation, redirect target.
- **D-10:** Include grep evidence as inline command output (not just "grep returned X results").
- **D-11:** Include functional tree showing what each module does.

### Commit Granularity
- **D-12:** One commit per sub-stage:
  - Commit 1 (Sub-stage 2a): DELETION-CANDIDATES.md inventory document
  - Commit 2 (Sub-stage 2b+2c): Caller redirections + merge of overlapping layers
  - Commit 3 (Sub-stage 2d): Approved deletions of dead directories
- **D-13:** Each commit message references the sub-stage and lists affected targets.

### Caller Inventory Evidence (pre-discussion scout)
- **D-14:** Pre-discussion scout found these callers (to be verified during sub-stage 2a):

| Target | Production Callers | Test/Script Callers |
|--------|-------------------|---------------------|
| `src/routes/` | `src/database/services/database_service.py` | self-imports + `fix_test_imports.py` |
| `src/api/` | None | `tests/api_contract_tests.py`, `fix_test_imports.py` |
| `src/data_access_pkg/` | Self-imports only | None |
| `src/database_optimization/` | None | `test_performance_monitor.py`, `test_database_optimization.py` |
| `src/db_manager/` | None | `update_imports.py`, `fix_test_imports.py` |

### Claude's Discretion
- Exact grep commands used for caller inventory (as long as they cover static, string, and dynamic imports)
- Whether to run `ruff check` after each individual redirect or batch them
- How to handle circular import risks during merge (if any surface)
- Whether to create backup tags before deletion commits

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 2 Scope
- `.planning/ROADMAP.md` §Phase 2 — Phase boundary, requirements, sub-stages, success criteria
- `.planning/REQUIREMENTS.md` §Dead Code Removal — DEAD-01 through DEAD-06
- `.planning/codebase/CONCERNS.md` — Issues #3 (overlapping data access), #4 (routes in wrong layer)

### Project Governance
- `architecture/STANDARDS.md` — Deletion governance rules (lines 103-111), migration governance
- `.planning/research/PITFALLS.md` — P-01 (import chains), P-06 (false-positive dead code)

### Prior Phase Context
- `.planning/phases/01-python-lint-baseline/01-CONTEXT.md` — D-01 (full deletion pattern established)

</canonical_refs>

<code_context>
## Existing Code Insights

### Deletion Targets (5 directories)

1. **`src/routes/`** — 19 files, mock-era route definitions from before web/backend/ consolidation
   - Contains `check_use_mock_data.py` in each sub-route (legacy mock switching)
   - Sub-directories: `monitoring_routes/`, `stocks_routes/`, `technical_routes/`
   - 1 production caller: `src/database/services/database_service.py`

2. **`src/api/`** — 5 files, alternative route layer
   - `alert_history_routes.py`, `datasource/` (subdir), `governance/` (subdir)
   - Test-only callers

3. **`src/data_access_pkg/`** — 5 files, duplicate data access package
   - `postgresql_access.py`, `tdengine_access.py`, `interface.py`, `_postgresql_access_query_mixin.py`
   - Overlaps with canonical `src/data_access/` (14 files)

4. **`src/db_manager/`** — 1 file (`__init__.py` only), empty shell
   - No production callers

5. **`src/database_optimization/`** — 5 files, optimization utilities
   - `performance_monitor.py`, `postgresql_index_optimizer.py`, `slow_query_analyzer.py`, `tdengine_index_optimizer.py`
   - Test-only callers

### Canonical Data Access Layer (KEEP)
- `src/data_access/` — 14 files (TDengine, PostgreSQL, factory, interfaces)
- This is the authoritative location per ROADMAP.md Canonical Truth Sources table

### Established Patterns (from Phase 1)
- Full deletion (not Protocol conversion) is the established pattern for duplicate layers
- Grep evidence required before deletion — "zero imports" proof
- `ruff check` + `pytest` after each batch of changes
- FastAPI smoke test after all changes

### Integration Points
- Production callers redirect to `web/backend/app/api/*` equivalents
- Data access callers redirect to `src/data_access/*` equivalents
- Dev scripts in `scripts/dev/` need import updates

</code_context>

<specifics>
## Specific Ideas

- DELETION-CANDIDATES.md must be written as a review document for user approval before any deletion
- Sub-stage 2a is ANALYSIS ONLY — no code changes
- `src/db_manager/` is almost certainly safe to delete immediately (only `__init__.py`)
- `src/data_access_pkg/` has only self-imports — very low risk merge

</specifics>

<deferred>
## Deferred Ideas

- Fixing ALL ruff errors to zero — Phase 4 (Naming & Polish)
- Frontend case-conflict merge — Phase 3
- Backend API directory reorganization (205-file split) — out of scope entirely
- Test quality improvements — separate initiative

</deferred>

---
*Phase: 02-dead-code-inventory-removal*
*Context gathered: 2026-04-06*
