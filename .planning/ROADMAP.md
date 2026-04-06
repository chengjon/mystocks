# Roadmap: MyStocks Codebase Consolidation

**Created:** 2026-04-06
**Granularity:** Coarse (4 phases)
**Execution:** Sequential (zero-breakage constraint)

---

## Phase 1: Lint Baseline

**Goal:** Eliminate the duplicate adapter layer and auto-fix ruff errors to establish a clean baseline for structural work. Merge frontend case-conflict directories.

**Requirements:** LINT-01, LINT-02, LINT-03, LINT-04

**Success Criteria:**
1. `ruff check src/ web/backend/app/` reports <50 errors (from ~1,456)
2. `src/interfaces/adapters/` no longer exists (deleted or converted to Protocol stubs)
3. Frontend has no case-conflict directories (Charts→charts, Common→common, Market→market)
4. `npm run build` succeeds after case-conflict merge
5. All existing functionality works (no regressions)

**Canonical refs:**
- `.planning/codebase/CONCERNS.md` — Issues #1 (P0) and #2 (P0)
- `.planning/research/PITFALLS.md` — P-02, P-07

---

## Phase 2: Dead Code Removal

**Goal:** Remove dead code layers (src/routes/, src/api/, empty directories) and generate a comprehensive deletion list for user review. All deletions require user approval.

**Requirements:** DEAD-01, DEAD-02, DEAD-03, DEAD-04, DEAD-05, DEAD-06

**Success Criteria:**
1. Deletion candidates documented in `DELETION-CANDIDATES.md` with grep evidence for each
2. `src/routes/` removed (after user approval + verification of zero imports)
3. `src/api/` removed (after user approval + verification of zero imports)
4. `src/db_manager/` removed
5. `src/data_access_pkg/` merged into `src/data_access/`
6. `src/database_optimization/` merged into `src/database/`
7. `ruff check` still <50 errors (no new errors introduced)

**Canonical refs:**
- `.planning/codebase/CONCERNS.md` — Issues #3, #4
- `.planning/research/PITFALLS.md` — P-01, P-06
- `architecture/STANDARDS.md` — Migration/deletion governance rules

**Risk notes:**
- User approval gate before any deletion (DEAD-06)
- Low test coverage (0.16%) — rely on grep verification + import smoke tests
- Dynamic imports possible — check string references, not just import statements

---

## Phase 3: Structural Consolidation

**Goal:** Establish single canonical locations for data access, frontend entry, and composables. Remove dead frontend directories.

**Requirements:** STRU-01, STRU-02, STRU-03, STRU-04, STRU-05

**Success Criteria:**
1. `src/data_access/` is the sole data access layer — all imports updated
2. Frontend has exactly one `main.js` entry point — variants archived
3. `views/composables/` contents relocated to `src/composables/`
4. `views/converted.archive/` and `views/demo/` removed
5. `ruff check` + `npm run build` + `stylelint` all pass
6. FastAPI app starts successfully: `python -c "from web.backend.app.main import app"`

**Canonical refs:**
- `.planning/codebase/ARCHITECTURE.md` — Data flow, entry points
- `.planning/codebase/STRUCTURE.md` — Current directory structure
- `.planning/research/ARCHITECTURE.md` — Safe refactoring order
- `architecture/STANDARDS.md` — Code organization rules

**Risk notes:**
- Data access merge must preserve connection pool patterns (PITFALLS P-05)
- Frontend entry cleanup may affect build tooling config (vite.config.js)

---

## Phase 4: Naming & Polish

**Goal:** Fix naming conventions, resolve root-level shims, and clarify store domains. Final cleanup pass.

**Requirements:** NAME-01, NAME-02, NAME-03, NAME-04, NAME-05

**Success Criteria:**
1. `src/calcu/` renamed or merged (no truncated names remain)
2. All `part1/part2/part3` files replaced with semantic names
3. All `*_new.py` files merged or deleted
4. Root-level shims verified safe — removed, deprecated, or documented as intentional
5. Frontend store domains clarified — overlapping stores merged or documented
6. `ruff check` = 0 errors (stretch goal) or <20
7. `npm run build` + `stylelint` pass with zero errors

**Canonical refs:**
- `.planning/codebase/CONCERNS.md` — Issues #8, #9, #11
- `.planning/research/PITFALLS.md` — P-04
- `architecture/STANDARDS.md` — Naming conventions

**Risk notes:**
- Root shim removal requires checking Dockerfile, docker-compose, scripts (PITFALLS P-04)
- Store merge affects runtime state — test carefully

---

## Phase Summary

| # | Phase | Goal | Requirements | Risk |
|---|-------|------|--------------|------|
| 1 | Lint Baseline | Fix adapters + ruff + case conflicts | LINT-01..04 | Medium (P-07) |
| 2 | Dead Code Removal | Remove dead layers with user approval | DEAD-01..06 | High (P-01, P-06) |
| 3 | Structural Consolidation | Single canonical locations | STRU-01..05 | Medium (P-05) |
| 4 | Naming & Polish | Consistent naming, zero shims | NAME-01..05 | Low (P-04) |

**Total:** 4 phases | 20 requirements | 100% covered

---
*Roadmap created: 2026-04-06*
