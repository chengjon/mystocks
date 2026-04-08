# Features Research: v1.1 Final Polish (Corrected)

**Researched:** 2026-04-08
**Corrected:** 2026-04-08 — aligned with v1.0 Phase 3 VERIFICATION.md

## Category: Lint Cleanup (F821)

### Table Stakes
- F821 errors reduced from 791 (62 files)
- Top-20 files fixed first (concentrated in adapters/)

### Anti-features
- Do NOT auto-fix blindly — some are in dead code paths (delete instead)
- Do NOT add noqa comments

### What "Done" Looks Like
- Significant F821 reduction, top-20 files clean, no runtime regressions

---

## Category: Entry Consolidation (STRU-03)

### Authoritative Context (from v1.0 Phase 3)
- **Canonical entry**: `main-standard.ts` — NOT `main.js`
- `main.js` exists only because `verify-mount.js` reads it
- `verify-mount.js` lives at `web/frontend/verify-mount.js` (NOT archived)
- 6 other entry variants were archived in v1.0; these 2 remain

### Table Stakes
- Resolve verify-mount.js disposition: update it to reference main-standard.ts, OR remove it
- Then archive main.js
- Result: single entry point (main-standard.ts)

### What "Done" Looks Like
- Only main-standard.ts as active entry
- main.js and verify-mount.js archived or removed
- `npm run dev` and `npm run build` both work

---

## Category: Composables (STRU-04)

### Authoritative Context (from v1.0 Phase 3)
- COMPOSABLES-AUDIT.md classifies 15/17 as "Keep view-local" (1 consumer each)
- Only 2 are extraction candidates
- Bulk relocation would break 15+ active imports
- v1.0 decision: deferred with audit evidence, needs re-scoping

### Table Stakes
- **Re-scope the requirement** based on audit evidence
- Options: (a) accept view-local pattern as canonical, (b) extract only 2 candidates, (c) per-file migration with full test coverage

### What "Done" Looks Like
- STRU-04 has a clear, evidence-based disposition (may be "accepted as-is" or "2 files migrated")

---

## Category: Archive Removal (STRU-05)

### Authoritative Context (from v1.0 Phase 3)
- `views/converted.archive/`: 0 runtime consumers, 5 test consumers block deletion
- `views/demo/`: ACTIVE code — 5 routes, 3+ views, 8+ tests — NOT removable
- DEMO-AUDIT.md proves demo/ is active; STRU-05 demo portion = not applicable

### Table Stakes
- Handle 5 test consumers for converted.archive/
- Mark demo/ removal as "not applicable"
- Delete converted.archive/ after test dependencies resolved

### What "Done" Looks Like
- views/converted.archive/ deleted
- views/demo/ confirmed as active code (no removal)
- All tests pass

---

## Complexity Assessment

| Category | Complexity | Risk | Notes |
|----------|-----------|------|-------|
| F821 Resolution | Medium | Low | Per-file, 62 files |
| Entry Consolidation | Low | Medium | Must not delete wrong entry |
| Composables Re-scoping | Low | Low | Decision task, not bulk migration |
| Archive Removal | Medium | Low | Must resolve 5 test deps first |

---
*Features research corrected: 2026-04-08*
