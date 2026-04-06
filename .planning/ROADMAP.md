# Roadmap: MyStocks Codebase Consolidation

> **使用说明**:
> 本文件是项目入口、工作流快照、规划工件或使用说明，不是当前共享规则、当前代码实现或当前运行状态的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码、主线任务系统与验证结果使用。
>
> 文内步骤、范围、状态或说明如未重新复核，应按其所属上下文理解，不得直接当作跨场景通用事实。


**Created:** 2026-04-06
**Revised:** 2026-04-06 (addressing review findings)
**Status:** Review draft — pending approval
**Granularity:** Coarse (4 phases)
**Execution:** Sequential (zero-breakage constraint)

---

## Global Execution Prerequisites

This file is an **approval-draft**. Execution begins only after user signs off.

### Canonical Truth Sources

Before any migration or deletion, the following single-source-of-truth declarations are locked:

| Concern | Canonical Location | All Others Converge To |
|---------|-------------------|----------------------|
| Data access layer | `src/data_access/` | `data_access_pkg/`, `database/`, `db_manager/`, `database_optimization/` all migrate into `src/data_access/` |
| API routes | `web/backend/app/api/` | `src/routes/` and `src/api/` redirect here, then delete |
| Frontend entry | **TBD** — must be verified via `index.html` + Vite config + PM2 startup before Phase 3 | All other `main-*.js/ts` variants archived after verification |
| Adapters (concrete) | `src/adapters/` | `src/interfaces/adapters/` deleted (no Protocol conversion — full deletion) |

### Root Shim Disposition Table

| Shim | Current Consumers | Disposition | Prerequisite | Verification |
|------|------------------|-------------|--------------|--------------|
| `core.py` | TBD (Phase 4 inventory) | Remove or deprecate | Verify all callers migrated | `grep -r "from core import\|import core\b" --include="*.py" --include="*.sh" --include="*.yml"` |
| `data_access.py` | TBD (Phase 4 inventory) | Remove or deprecate | Verify all callers use `src.data_access` | `grep -r "from data_access import\|import data_access\b"` |
| `monitoring.py` | TBD (Phase 4 inventory) | Remove or deprecate | Verify all callers use `src.monitoring` | `grep -r "from monitoring import\|import monitoring\b"` |
| `unified_manager.py` | Documented entry point per `ARCHITECTURE.md` | **Keep** (re-export is intentional) | N/A | `python -c "from unified_manager import MyStocksUnifiedManager"` |

> Shim disposition is finalized during Phase 4 after full caller inventory. "Remove" means delete file after redirecting all consumers. "Deprecate" means add deprecation warning but keep file. "Keep" means file is intentionally canonical.

---

## Phase 1: Python Lint Baseline

**Goal:** Eliminate the duplicate adapter layer and auto-fix ruff errors to establish a clean Python baseline. Frontend case-conflict merge moved to Phase 3 per research alignment.

**Requirements:** LINT-01, LINT-02, LINT-03

**Success Criteria:**
1. `ruff check src/ web/backend/app/ --statistics` reports <900 errors (from ~1,456; recalibrated per `.planning/phases/01-python-lint-baseline/01-RESEARCH.md` — 805 F821 require manual investigation, not auto-fixable)
2. `src/interfaces/adapters/` deleted — verified zero imports: `grep -r "from src.interfaces.adapters\|import src.interfaces.adapters" --include="*.py" src/ web/ tests/ scripts/` returns empty
3. Auto-fixable rules produce zero violations: `ruff check src/ web/backend/app/ --select F401,F841,W291,W293,E701` exits 0
4. FastAPI app starts: `python -c "from web.backend.app.main import app; print('OK')"`
5. No regressions: `pytest --tb=short` passes (same pass/fail count as before)

**Tasks:**
1. Grep for all imports of `src.interfaces.adapters` — document findings
2. If zero imports: delete `src/interfaces/adapters/` entirely
3. If imports exist: redirect to `src/adapters/` first, then delete
4. Run `ruff check --fix --select F401,F841,W291,W293,E701` on `src/` and `web/backend/app/`
5. Run full `ruff check` and document remaining errors
6. Run smoke tests (FastAPI import + pytest)

**Canonical refs:**
- `.planning/codebase/CONCERNS.md` — Issue #1 (P0)
- `.planning/research/PITFALLS.md` — P-02, P-07
- `architecture/STANDARDS.md` — Migration governance rules

---

## Phase 2: Dead Code Inventory & Removal

**Goal:** Identify, inventory, redirect callers, and remove dead code layers. **No deletion occurs until user approves a comprehensive DELETION-CANDIDATES.md with both grep evidence AND functional tree analysis.**

**Requirements:** DEAD-01, DEAD-02, DEAD-03, DEAD-04, DEAD-05, DEAD-06

### Sub-stage 2a: Caller Inventory & Functional Tree

**No code changes.** Only analysis and documentation.

1. For each deletion target, run comprehensive import analysis:
   - Static imports: `grep -r "from src.routes\|import src.routes\|from src.api\b\|import src.api\b" --include="*.py" src/ web/ tests/ scripts/`
   - String references: `grep -r "src\.routes\|src\.api\|src\.routes\.\|src\.api\." --include="*.py" --include="*.sh" --include="*.yml" --include="*.yaml" --include="*.toml" .`
   - Dynamic imports: `grep -r "importlib\|__import__\|import_module" --include="*.py" src/ web/ tests/ scripts/`
2. Check CI/CD scripts: `grep -r "src.routes\|src.api\|src\.routes\|src\.api" .github/ scripts/ config/`
3. For each target directory, document functional node ownership in DELETION-CANDIDATES.md:
   - Module path
   - Functional purpose (what it does)
   - Current status (active/dead/legacy)
   - All known callers (with file:line references)
   - Keep/delete recommendation
   - If delete: redirection plan (where callers should point instead)
   - If keep: reason why
   - Verification command

**Output:** `DELETION-CANDIDATES.md` with complete analysis for user review.

### Sub-stage 2b: Caller Redirection

After user reviews DELETION-CANDIDATES.md:
1. For each approved deletion, redirect all callers to canonical locations
2. Redirect `src.routes.*` imports → `web.backend.app.api.*` equivalents
3. Redirect `src.api.*` imports → `web.backend.app.api.*` equivalents
4. Run `ruff check` after each redirect to verify no new errors
5. Run `pytest` after all redirects

### Sub-stage 2c: Merge Overlapping Layers

1. Merge unique files from `src/data_access_pkg/` into `src/data_access/` (canonical)
2. Merge unique files from `src/database_optimization/` into `src/data_access/` (canonical — NOT `src/database/`)
3. Delete `src/db_manager/` (empty shell, verify first)
4. Update all imports to point to `src/data_access/`
5. Run `ruff check` + `pytest` after each merge

### Sub-stage 2d: Approved Deletion

**Only after sub-stages 2a-2c complete and user approves:**
1. Delete `src/routes/` (19 files)
2. Delete `src/api/` (5 files)
3. Delete `src/data_access_pkg/` (now empty after merge)
4. Delete `src/database_optimization/` (now empty after merge)
5. Delete `src/db_manager/`
6. Run full verification suite

**Success Criteria:**
1. `DELETION-CANDIDATES.md` exists with grep evidence + functional tree + disposition for each target
2. User has reviewed and approved the deletion list
3. `src/routes/`, `src/api/`, `src/data_access_pkg/`, `src/db_manager/`, `src/database_optimization/` all removed
4. `ruff check src/ web/backend/app/` still <50 errors (no new errors)
5. `python -c "from web.backend.app.main import app; print('OK')"` passes
6. `pytest --tb=short` passes (same pass/fail count)

**Canonical refs:**
- `.planning/codebase/CONCERNS.md` — Issues #3, #4
- `.planning/research/PITFALLS.md` — P-01, P-06
- `architecture/STANDARDS.md` — Deletion governance rules (lines 103-111)

---

## Phase 3: Structural Consolidation

**Goal:** Establish single canonical locations for frontend entry and composables. Merge frontend case-conflict directories. Remove dead frontend directories.

**Requirements:** LINT-04, STRU-01, STRU-02, STRU-03, STRU-04, STRU-05

### Sub-stage 3a: Frontend Entry Verification (before any changes)

1. Check actual loaded entry: `cat web/frontend/index.html | grep -E "src/|script"`
2. Check Vite config: `cat web/frontend/vite.config.js | grep -E "entry|input|main"`
3. Check PM2 config: `grep -r "main\|entry\|frontend" ecosystem.config.js 2>/dev/null || echo "no PM2 config"`
4. Document current actual entry point(s)
5. Declare canonical entry based on evidence (not assumption)

### Sub-stage 3b: Case-Conflict Directory Merge

1. List case-conflict pairs: `git ls-files web/frontend/src/components/ | sort`
2. For each pair (Charts/charts, Common/common, Market/market):
   - Inventory imports for both cases
   - Merge uppercase into lowercase (Vue convention)
   - Update all import references
3. Verify: `cd web/frontend && npm run build`
4. Verify: `cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"`

### Sub-stage 3c: Data Access Consolidation

1. Verify `src/data_access/` is sole data access layer (Phase 2 should have merged others)
2. Verify all imports point to `src/data_access/`
3. Run: `python -c "from web.backend.app.main import app; print('OK')"`

### Sub-stage 3d: Frontend Cleanup

1. After 3a identifies canonical entry: archive all other `main-*.js/ts` variants
2. Move `views/composables/` contents to `src/composables/` (update imports)
3. Remove `views/converted.archive/`
4. Remove `views/demo/`
5. Verify: `cd web/frontend && npm run build`

**Success Criteria:**
1. Frontend entry truth source documented and verified (via index.html + Vite + PM2 evidence)
2. No case-conflict directories remain: `cd web/frontend && git ls-files src/components/ | sort` shows no duplicate names
3. `cd web/frontend && npm run build` succeeds
4. `cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"` passes
5. `src/data_access/` is sole data access layer — verified by: `ls src/data_access_pkg/ src/db_manager/ src/database_optimization/ 2>&1 | grep "No such file"`
6. FastAPI starts: `python -c "from web.backend.app.main import app; print('OK')"`

**Risk notes:**
- Case-conflict merge affects import paths — must update all references
- Frontend entry verification must happen BEFORE any entry point changes
- If route/layout changes involved: must run `scripts/run_e2e_pm2.sh` per STANDARDS.md:58-60

**Canonical refs:**
- `.planning/codebase/ARCHITECTURE.md` — Data flow, entry points
- `.planning/codebase/STRUCTURE.md` — Current directory structure
- `.planning/research/ARCHITECTURE.md` — Safe refactoring order
- `.planning/research/PITFALLS.md` — P-03
- `architecture/STANDARDS.md` — Code organization rules

---

## Phase 4: Naming & Polish

**Goal:** Fix naming conventions, finalize root shim disposition, clarify store domains.

**Requirements:** NAME-01, NAME-02, NAME-03, NAME-04, NAME-05

### Sub-stage 4a: Root Shim Finalization

1. Complete caller inventory for each shim (update disposition table from Global Prerequisites)
2. For each shim marked "Remove": redirect callers to `src.*` imports, then delete
3. For each shim marked "Deprecate": add `warnings.warn("... is deprecated, use src....")`, keep file
4. For "Keep": document as intentional in `ARCHITECTURE.md`
5. Verify: `python -c "from web.backend.app.main import app; print('OK')"`

### Sub-stage 4b: Naming Cleanup

1. Rename `src/calcu/` → semantic name (merge into `src/utils/` or rename to `src/calculators/`)
2. Replace `part1/part2/part3` files with semantic names
3. Merge or delete `*_new.py` files
4. Delete `*.bak`, `*.backup` files from source tree

### Sub-stage 4c: Store Domain Clarification

1. Inventory all Pinia stores: `ls web/frontend/src/stores/`
2. For overlapping pairs (`market.ts` + `marketData.ts`, `trading.ts` + `tradingData.ts`):
   - Document domain boundary for each
   - Merge or document why both exist
3. Verify: `cd web/frontend && npm run build`

**Success Criteria:**
1. No truncated directory names: `ls src/ | grep -E "^.{1,5}$"` returns only intentional short names
2. No `*_new.py` files: `find src/ -name "*_new.py" -o -name "*_backup*" -o -name "*.bak"` returns empty
3. Root shim disposition table fully populated — each shim has final status (Keep/Remove/Deprecate)
4. Store domains documented — each store has a clear single responsibility
5. `ruff check src/ web/backend/app/` = 0 errors (stretch) or <20
6. `cd web/frontend && npm run build` succeeds
7. `cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"` passes

**Risk notes:**
- Root shim callers include scripts, Dockerfiles, compose files — check all (PITFALLS P-04)
- Store merge affects runtime state — verify in browser after changes

**Canonical refs:**
- `.planning/codebase/CONCERNS.md` — Issues #8, #9, #11
- `.planning/research/PITFALLS.md` — P-04
- `architecture/STANDARDS.md` — Naming conventions, migration governance

---

## Phase Summary

| # | Phase | Goal | Requirements | Risk |
|---|-------|------|--------------|------|
| 1 | Python Lint Baseline | Fix adapters + auto-fix ruff | LINT-01..03 | Medium (P-07) |
| 2 | Dead Code Inventory & Removal | Inventory → redirect → approve → delete | DEAD-01..06 | High (P-01, P-06) |
| 3 | Structural Consolidation | Case conflicts + frontend entry + data access | LINT-04, STRU-01..05 | Medium (P-03, P-05) |
| 4 | Naming & Polish | Consistent naming, shim disposition, store domains | NAME-01..05 | Low-Medium (P-04) |

**Total:** 4 phases | 20 requirements | 100% covered

---

## Verification Gate Template

Every phase gate must report:

```
## Phase N Verification Report

**Date:** [date]
**Phase:** [name]

### Commands Run
- `ruff check src/ web/backend/app/ --statistics` → [result]
- `cd web/frontend && npm run build` → [result]
- `cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"` → [result]
- `python -c "from web.backend.app.main import app; print('OK')"` → [result]
- `pytest --tb=short` → [result] (pass/fail count)

### Route/Layout Changes
- [ ] If routes or layouts changed: `scripts/run_e2e_pm2.sh` executed
- PM2 status: [output]
- Service URL: [url]
- E2E results: [summary]

### Success Criteria
- [ ] SC-1: [met/not met]
- [ ] SC-2: [met/not met]
...
```

---
*Roadmap created: 2026-04-06*
*Revised: 2026-04-06 after review — addressed findings #1-#6*
