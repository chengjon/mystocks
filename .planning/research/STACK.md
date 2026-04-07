# Stack Research: v1.1 Final Polish

**Researched:** 2026-04-08
**Focus:** Tooling for F821 resolution, entry consolidation, composables migration, archive cleanup

## Summary

No new dependencies needed. All cleanup tasks use existing tooling.

## Tooling

### F821 Resolution
- **ruff** (current version): `ruff check --select F821 --fix` for auto-fixable cases
- **Manual review**: Most F821 are missing imports — need human judgment for correct module

### Frontend Entry Consolidation
- **Vite** (existing): Entry point configured in `vite.config.js`

### Composables Migration
- **git mv**: Move files preserving history
- **grep/ast-grep**: Find all import references to update

### Archive Removal
- **git rm**: Delete dead files

## What NOT to Add
- No new linters, formatters, or analysis tools
- No codemods — composables migration needs manual per-consumer updates
- No automated F821 fixers — most require understanding context

## Integration Points
- F821 fixes touch 62 files across `src/adapters/`, `src/monitoring/`, `src/gpu/`, `web/backend/`
- Composables migration touches 17 files + ~30 consumer views
- Archive removal is isolated (zero imports found)

---
*Stack research complete: 2026-04-08*
