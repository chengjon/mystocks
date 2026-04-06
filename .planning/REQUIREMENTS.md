# Requirements: MyStocks Codebase Consolidation

**Defined:** 2026-04-06
**Core Value:** Every file has exactly one canonical location, every import resolves cleanly, zero lint errors.

## v1 Requirements

### Lint Baseline

- [ ] **LINT-01**: Duplicate adapter layer (`src/interfaces/adapters/`) is eliminated — deleted or converted to Protocol stubs
- [ ] **LINT-02**: Ruff check passes with <50 errors on `src/` and `web/backend/app/` (from current ~1,456)
- [ ] **LINT-03**: Auto-fixable ruff rules (F401, F841, W291, W293, E701) produce zero violations
- [ ] **LINT-04**: Frontend case-conflict directories merged into lowercase canonical names

### Dead Code Removal

- [ ] **DEAD-01**: `src/routes/` (19 files) removed — verified zero imports before deletion
- [ ] **DEAD-02**: `src/api/` (5 files) removed — verified zero imports before deletion
- [ ] **DEAD-03**: `src/data_access_pkg/` merged into canonical `src/data_access/`
- [ ] **DEAD-04**: `src/db_manager/` (empty shell) removed
- [ ] **DEAD-05**: `src/database_optimization/` merged into `src/database/`
- [ ] **DEAD-06**: All proposed deletions listed in a review document for user approval before execution

### Structural Consolidation

- [ ] **STRU-01**: Single canonical data access layer in `src/data_access/` — all others removed
- [ ] **STRU-02**: All import paths updated to point to canonical locations
- [ ] **STRU-03**: Frontend has exactly one entry point (`main.js`) — all variants removed or archived
- [ ] **STRU-04**: `views/composables/` relocated to `src/composables/`
- [ ] **STRU-05**: `views/converted.archive/` and `views/demo/` removed from source tree

### Naming & Polish

- [ ] **NAME-01**: `src/calcu/` renamed to semantic name or merged into existing module
- [ ] **NAME-02**: All `part1/part2/part3` mechanical splits replaced with semantic names
- [ ] **NAME-03**: All `*_new.py` files merged into canonical version or deleted
- [ ] **NAME-04**: Root-level shim files (`core.py`, `data_access.py`, `monitoring.py`) verified safe, removed or deprecated
- [ ] **NAME-05**: Frontend store domain boundaries clarified — no overlapping concerns (`market.ts` vs `marketData.ts`)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Mock data relocation | Keep as-is — useful for testing, not blocking anything |
| New feature development | This is cleanup only |
| Performance optimization | Out of scope unless caused by duplicate code paths |
| Mobile/responsive adaptation | Desktop-only per project constraints |
| API contract changes | Route consolidation is location only, not signature changes |
| Test framework changes | Fix existing tests, don't add frameworks |
| Backend API directory reorganization | 205-file split into subdirs is a separate initiative |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| LINT-01 | Phase 1 | Pending |
| LINT-02 | Phase 1 | Pending |
| LINT-03 | Phase 1 | Pending |
| LINT-04 | Phase 1 | Pending |
| DEAD-01 | Phase 2 | Pending |
| DEAD-02 | Phase 2 | Pending |
| DEAD-03 | Phase 2 | Pending |
| DEAD-04 | Phase 2 | Pending |
| DEAD-05 | Phase 2 | Pending |
| DEAD-06 | Phase 2 | Pending |
| STRU-01 | Phase 3 | Pending |
| STRU-02 | Phase 3 | Pending |
| STRU-03 | Phase 3 | Pending |
| STRU-04 | Phase 3 | Pending |
| STRU-05 | Phase 3 | Pending |
| NAME-01 | Phase 4 | Pending |
| NAME-02 | Phase 4 | Pending |
| NAME-03 | Phase 4 | Pending |
| NAME-04 | Phase 4 | Pending |
| NAME-05 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0

---
*Requirements defined: 2026-04-06*
*Last updated: 2026-04-06 after initial definition*
