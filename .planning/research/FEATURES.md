# Features Research: Clean Codebase Patterns

**Researched:** 2026-04-06
**Project Type:** Brownfield cleanup (Python + Vue 3 monorepo)

---

## Table Stakes (Must Have)

These are non-negotiable for a "clean" codebase:

### Single Source of Truth
- **One canonical adapter layer**: `src/adapters/` is the implementation. If `src/interfaces/adapters/` exists, it must be Protocol/ABC only (signatures, no implementations).
- **One data access layer**: Merge `data_access/`, `data_access_pkg/`, `database/`, `db_manager/` into a single `src/data_access/`.
- **One route location**: All FastAPI routes in `web/backend/app/api/`. No routes in `src/`.
- **One frontend entry**: `main.js` only. No variants.

### Naming Consistency
- **Python**: `snake_case` for modules/dirs, no truncated names (`calcu/` → proper name or merge), no `*_new.py` / `*_backup` files in source tree.
- **Vue**: `kebab-case` for component directories, no case-conflict pairs (`Charts/` + `charts/`).
- **No part1/part2/part3 splits**: Semantic naming or extract to proper modules.

### Zero Lint Errors
- **Python**: `ruff check` passes with 0 errors.
- **Frontend**: `stylelint` passes with 0 errors.
- **TypeScript**: `vue-tsc --noEmit` passes.

### No Dead Code in Source Tree
- No `.backup` files, no `*_new.py` variants, no `converted.archive/` directories.
- Demo files not referenced by routes or tests should be removed.
- Empty directories (`db_manager/` with only `__init__.py`) should be deleted.

## Differentiators (Nice-to-Have)

### Structure Quality
- **Flat API directory reorganization**: Group 205 backend API files into subdirectories by domain (market/, portfolio/, trading/, monitoring/, etc.)
- **Store domain clarity**: Each Pinia store covers exactly one domain concern (no `market.ts` + `marketData.ts` overlap)
- **Composable relocation**: `views/composables/` → `src/composables/`

### Import Hygiene
- **Absolute imports only**: No root-level shims with bare imports
- **No circular dependencies**: Verified via import graph analysis
- **Re-export shims minimized**: Keep backward compat only if external consumers exist

## Anti-Features (Deliberately NOT Doing)

| Anti-Feature | Why Not |
|-------------|---------|
| Adding new abstractions | Cleanup should reduce complexity, not add layers |
| Refactoring working business logic | If it works, don't touch it — only fix structure |
| Changing API contracts | Routes consolidation is location only, not signature changes |
| Adding new test frameworks | Fix existing tests, don't add frameworks |
| Implementing design patterns | No new patterns — remove broken ones |
| Mobile/responsive support | Desktop-only per project constraints |
| Performance optimization | Not a goal unless caused by duplicate code paths |

## Dependencies Between Cleanup Tasks

```
1. Fix duplicate adapters (P0)
   └─→ Unblocks: ruff error count drops from 1,456 to ~300

2. Auto-fix ruff errors (P0)
   └─→ Depends on: #1 (adapters fixed first)
   └─→ Unblocks: clean baseline for structural work

3. Merge data access layers (P1)
   └─→ Depends on: #2 (clean imports first)
   └─→ Unblocks: root shim cleanup

4. Consolidate routes (P1)
   └─→ Independent of #3 (different architectural layer)

5. Fix frontend case conflicts (P0)
   └─→ Independent of all Python work

6. Clean frontend structure (P2)
   └─→ Depends on: #5 (case conflicts fixed first)

7. Fix root shims (P2)
   └─→ Depends on: #3 (data access consolidated first)

8. Fix naming (P2)
   └─→ Independent (can run anytime after #1)
```

---
*Research completed: 2026-04-06*
