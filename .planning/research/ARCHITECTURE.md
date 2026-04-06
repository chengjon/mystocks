# Architecture Research: Safe Refactoring Order

**Researched:** 2026-04-06
**Architecture Type:** Layered (Frontend → FastAPI → Core → Data)

---

## Recommended Refactoring Order

The order matters because later steps depend on earlier ones completing cleanly.

### Phase 1: Lint Baseline (Unblocks everything)

**Goal:** Get ruff from 1,456 errors to <50 without changing any behavior.

**Step 1a: Resolve duplicate adapter layer**
- **Current**: `src/interfaces/adapters/` is a full copy of `src/adapters/` missing imports
- **Fix**: Delete `src/interfaces/adapters/` entirely OR convert to Protocol stubs
- **Decision needed**: Does anything import from `src.interfaces.adapters`?
- **Verification**: `grep -r "from src.interfaces.adapters" src/ web/` — if zero hits, safe to delete

**Step 1b: Auto-fix ruff safe rules**
- `ruff check --fix --select F401,F841,W291,W293,E701`
- This fixes ~46% of remaining errors automatically
- **Verification**: `ruff check src/ web/backend/app/ --statistics`

### Phase 2: Dead Code Removal (Reduces complexity)

**Goal:** Remove code that nothing uses.

**Step 2a: Remove dead route layers**
- Delete `src/routes/` (19 files) — verify no imports first
- Delete `src/api/` (5 files) — verify no imports first
- **Verification**: `grep -r "from src.routes\|from src.api\|import src.routes\|import src.api" src/ web/ tests/`
- **Safety**: If any imports found, redirect them to `web/backend/app/api/` equivalent

**Step 2b: Remove empty/dead directories**
- Delete `src/db_manager/` (empty shell)
- Delete `src/data_access_pkg/` (duplicate of `data_access/`)
- Delete `src/database_optimization/` (overlaps `database/`)
- **Verification**: grep for any imports before deletion

**Step 2c: Generate deletion list for user review**
- Write all proposed deletions to `DELETION-CANDIDATES.md`
- Wait for user approval before executing

### Phase 3: Structural Consolidation (Merges overlapping layers)

**Goal:** Single canonical location for each concern.

**Step 3a: Merge data access layers**
- Keep `src/data_access/` as canonical
- Move any unique files from `data_access_pkg/` and `database/` into it
- Update all imports
- **Verification**: `pytest` + `ruff check`

**Step 3b: Fix frontend case conflicts**
- Merge `Charts/` → `charts/`, `Common/` → `common/`, `Market/` → `market/`
- Update all import references
- **Verification**: `npx stylelint` + `npm run build`

**Step 3c: Clean frontend entry points**
- Keep only `main.js`
- Move variants to archive or delete (per user approval)

### Phase 4: Naming & Polish (Final cleanup)

**Goal:** Consistent naming, zero shims.

**Step 4a: Fix naming conventions**
- `src/calcu/` → merge into `src/utils/` or rename to `src/calculators/`
- `part1/part2/part3` files → semantic names or proper module extraction
- `*_new.py` → merge into canonical version
- `*.bak` / `*.backup` files → delete

**Step 4b: Resolve root-level shims**
- `core.py` → verify nothing imports from it, then delete
- `data_access.py` → verify, delete
- `monitoring.py` → verify, delete
- `unified_manager.py` → keep if it's the documented entry point

**Step 4c: Clean frontend structure**
- Move `views/composables/` → `src/composables/`
- Remove `views/converted.archive/`
- Remove `views/demo/` (or archive)
- Consolidate overlapping stores

## Import Safety Strategy

After each phase:

1. **Run `ruff check`** — ensures no undefined names
2. **Run `pytest`** — catches runtime import errors (limited by 0.16% coverage)
3. **Run `grep` verification** — explicitly check that removed modules aren't imported
4. **Manual review of deletion list** — user approves before deletion

## Phase Dependencies

```
Phase 1 (Lint Baseline)
  ├─→ Phase 2 (Dead Code) — needs clean import graph
  │     └─→ Phase 3 (Consolidation) — needs dead code removed
  │           └─→ Phase 4 (Polish) — needs structure settled
  └─→ Phase 3b (Frontend cases) — independent of Python phases
```

Frontend case conflicts (Phase 3b) can run in parallel with Phase 2 since it's a different layer.

---
*Research completed: 2026-04-06*
