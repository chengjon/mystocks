# Features Research: v1.1 Final Polish

**Researched:** 2026-04-08
**Focus:** What "done" looks like for each cleanup category

## Category: Lint Cleanup (F821)

### Table Stakes
- F821 undefined-name errors reduced significantly (791 → target <50 or all documented)
- Top-20 files fixed first (70%+ of errors concentrated in adapters/)

### Differentiators
- Categorize remaining F821s: fixable vs dead code vs intentional
- CI gate on new F821s to prevent regression

### Anti-features
- Do NOT auto-fix all F821s blindly — some are in dead code paths
- Do NOT add noqa comments — fix properly or delete dead code

### What "Done" Looks Like
- `ruff check --select F821` returns <50 errors (or documented)
- Top 20 files have zero F821 errors
- No runtime regressions

---

## Category: Frontend Entry Consolidation (STRU-03)

### Table Stakes
- Single entry point: main.js only

### What "Done" Looks Like
- Only 1 entry file in web/frontend/src/
- `npm run dev` and `npm run build` both work

---

## Category: Composables Migration (STRU-04)

### Table Stakes
- All composables in canonical location: `src/composables/`
- views/composables/ directory removed
- All ~30 consumer imports updated from `'./composables/X'` to `'@/composables/X'`

### What "Done" Looks Like
- `views/composables/` does not exist
- `vue-tsc --noEmit` passes
- `npm run build` succeeds

---

## Category: Archive Removal (STRU-05)

### Table Stakes
- views/converted.archive/ deleted (11 dead files)

### What "Done" Looks Like
- Directory does not exist
- No imports reference it (verified: zero found)
- Test suite passes

---

## Complexity Assessment

| Category | Complexity | Risk | Scope |
|----------|-----------|------|-------|
| F821 Resolution | Medium | Low | 62 files |
| Entry Consolidation | Low | Low | 2 files |
| Composables Migration | High | Medium | ~47 files |
| Archive Removal | Low | Low | 11 files |

---
*Features research complete: 2026-04-08*
