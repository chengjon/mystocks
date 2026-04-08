# Research Summary: v1.1 Final Polish (Corrected)

**Synthesized:** 2026-04-08
**Corrected:** 2026-04-08 — aligned with v1.0 Phase 3 VERIFICATION.md

## Stack Additions
None. All cleanup uses existing tooling.

## Corrected Feature Assessment

### F821 Resolution (LINT-05)
- 791 errors across 62 files, concentrated in adapters/
- Top 20 files = 70%+ of errors
- Standard per-file fix approach

### Entry Consolidation (STRU-03)
- Canonical entry = `main-standard.ts` (NOT main.js)
- `main.js` retained because `verify-mount.js` reads it
- Resolution: handle verify-mount.js, then archive main.js

### Composables (STRU-04)
- 15/17 composables are view-local — correctly co-located with their single consumer
- Only 2 are extraction candidates
- Bulk migration is harmful — requirement needs re-scoping based on audit evidence

### Archive Removal (STRU-05)
- `views/converted.archive/`: removable after resolving 5 test consumers
- `views/demo/`: ACTIVE code — NOT removable (5 routes, 3+ views, 8+ tests)

## Suggested Build Order (5 phases)
1. **Composables Re-scoping** — decision task, sets scope clarity
2. **Archive Removal** — resolve 5 test deps, delete converted.archive/
3. **Entry Consolidation** — resolve verify-mount.js, archive main.js
4. **F821 Top-20** — concentrated wins
5. **F821 Long Tail** — remaining 42 files

## Watch Out For
- **Getting v1.0 facts wrong**: biggest risk is re-litigating resolved decisions
- **Entry direction**: main-standard.ts is canonical, NOT main.js
- **Composables**: bulk migration breaks 15+ imports, view-local is valid
- **demo/**: active code, do not touch

---
*Research summary corrected: 2026-04-08*
