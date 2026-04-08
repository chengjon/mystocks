# Stack Research: v1.1 Final Polish (Corrected)

**Researched:** 2026-04-08
**Corrected:** 2026-04-08 — aligned with v1.0 Phase 3 VERIFICATION.md

## Summary

No new dependencies. All cleanup uses existing tooling.

## Tooling

### F821 Resolution
- **ruff**: `ruff check --select F821 --fix` for auto-fixable; manual for most
- No new tools needed

### Entry Consolidation (STRU-03)
- **Vite** (existing): entry configured in `vite.config.js`
- **Key fact from v1.0**: canonical entry is `main-standard.ts`, NOT `main.js`
- `main.js` retained because `verify-mount.js` (at `web/frontend/verify-mount.js`) reads it
- Resolution: update verify-mount.js → main-standard.ts, OR remove verify-mount.js, then archive main.js

### Composables (STRU-04)
- **Key fact from v1.0**: 15/17 composables are view-local (1 consumer each, relative import from sibling view)
- Only 2 are extraction candidates for `src/composables/`
- Bulk relocation is NOT the correct approach — would break 15+ active imports
- Need to re-scope: accept view-local as canonical pattern, or extract only the 2 candidates

### Archive Removal (STRU-05)
- **Key fact from v1.0**: `views/converted.archive/` has 5 test consumers blocking deletion
- `views/demo/` is ACTIVE code (5 routes, 3+ views, 8+ tests) — NOT removable
- STRU-05 demo portion should be marked "not applicable"

## What NOT to Add
- No new tools, codemods, or automated fixers

---
*Stack research corrected: 2026-04-08*
