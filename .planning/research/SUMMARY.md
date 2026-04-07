# Research Summary: v1.1 Final Polish

**Synthesized:** 2026-04-08

## Stack Additions
**None required.** All cleanup uses existing tooling (ruff, git, Vite, vue-tsc).

## Feature Table Stakes
1. **F821 errors**: Reduce from 791 to <50 (or all remaining documented)
2. **Archive removal**: Delete 11 dead files in views/converted.archive/ (zero imports)
3. **Entry consolidation**: Verify verify-mount.js status (may be partially done)
4. **Composables migration**: Move 17 files, update ~30 consumer imports

## Suggested Build Order (5 phases)
1. **Archive Removal** — easiest win, zero dependencies
2. **Entry Consolidation** — verify then act, small scope
3. **F821 Top-20** — 70%+ of errors in 20 files
4. **Composables Migration** — highest complexity, needs full attention
5. **F821 Long Tail** — remaining 42 files, routine cleanup

## Watch Out For
- **Dead code masquerading as F821**: Delete instead of fixing when function is unused
- **Name collisions**: views/composables/ files may clash with src/composables/ entries
- **GPU conditional imports**: 34 F821s in src/gpu/ need special handling
- **verify-mount.js already archived**: STRU-03 may be partially complete
- **Test files blocking archive**: 5 test files may reference converted.archive

## Risk Assessment
| Task | Risk | Mitigation |
|------|------|------------|
| F821 Top-20 | Low | Per-file fixes, ruff verification |
| F821 Long Tail | Low | Same approach, smaller batches |
| Entry Consolidation | Low | Already partially done |
| Composables Migration | Medium | 30+ consumers, per-file migration |
| Archive Removal | Low | Zero imports confirmed |

---
*Research synthesis complete: 2026-04-08*
