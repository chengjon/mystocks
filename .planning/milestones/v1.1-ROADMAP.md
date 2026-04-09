# Roadmap: v1.1 Final Polish

**Created:** 2026-04-08
**Milestone:** v1.1 Final Polish
**Starting Phase:** 5 (continues from v1.0 Phase 4)

---

## Overview

3 phases covering 10 requirements across 3 categories. All deferred structural items from v1.0 resolved with evidence-based dispositions.

**Build order rationale:** Composables re-scoping first (decision task clarifies scope), then archive removal (clean slate), then entry consolidation (smallest scope, highest precision needed).

---

## Phase 5: Composables Disposition

**Goal:** Resolve STRU-04 by making evidence-based decisions on composable file locations, accepting view-local as canonical pattern, and extracting only the 2 vetted candidates.

### Requirements

COMP-01, COMP-02, COMP-03

### Success Criteria

1. COMPOSABLES-AUDIT.md reviewed; each of the 2 extraction candidates has a documented disposition (extract or keep view-local)
2. View-local pattern documented as canonical for 15/17 composables (co-located with single consumer = idiomatic Vue)
3. Any extracted composables live in src/composables/ with all consumer imports updated
4. `vue-tsc --noEmit` passes after any extractions
5. `npm run build` succeeds

### Approach

- Read COMPOSABLES-AUDIT.md for the 2 extraction candidate details
- For each candidate: evaluate extraction benefit vs risk, document decision
- For accepted extractions: move file, update consumer imports, verify build
- Document view-local pattern as project convention

---

## Phase 6: Archive Cleanup

**Goal:** Resolve STRU-05 by removing views/converted.archive/ after handling its 5 test consumers; confirm demo/ is active and not removable.

### Requirements

ARCH-01, ARCH-02, ARCH-03, ARCH-04

### Success Criteria

1. All 5 test consumers of views/converted.archive/ identified with file paths and import lines
2. Test consumers updated to remove archive references (or tests deleted if testing archived code only)
3. views/converted.archive/ directory deleted (11 files)
4. views/demo/ confirmed as active code; traceability updated to mark demo/ removal as "not applicable"
5. `npm run build` and test suite pass with no dangling references

### Approach

- Grep test files for converted.archive references
- Update or remove tests that reference archived views
- Delete views/converted.archive/ via git rm
- Document demo/ as active code (not dead) in traceability
- Run full build + test verification

---

## Phase 7: Entry Consolidation

**Goal:** Resolve STRU-03 by handling verify-mount.js disposition, archiving main.js, and confirming main-standard.ts as sole entry point.

### Requirements

ENTRY-01, ENTRY-02, ENTRY-03

### Success Criteria

1. verify-mount.js disposition resolved (updated to reference main-standard.ts, or removed with documented justification)
2. main.js archived (moved to _entry-archive/ or deleted)
3. main-standard.ts confirmed as sole active entry point
4. `npm run dev` starts successfully (dev server startup verified)
5. `npm run build` succeeds

### Approach

- Read verify-mount.js to understand its runtime role
- Read main.js to understand its relationship with verify-mount.js
- Decide: update verify-mount.js to use main-standard.ts, or remove verify-mount.js entirely
- Archive main.js after verify-mount.js no longer depends on it
- Verify dev server + build + hot-reload all work

---

## Phase Summary

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 5 | Composables Disposition | Resolve STRU-04 with evidence-based decisions | Complete    | 2026-04-08 |
| 6 | Archive Cleanup | Remove converted.archive/, confirm demo/ active | ARCH-01, ARCH-02, ARCH-03, ARCH-04 | 5 |
| 7 | Entry Consolidation | Single entry point (main-standard.ts) | ENTRY-01, ENTRY-02, ENTRY-03 | 5 |

**Coverage:** 10/10 requirements mapped ✓

---
*Roadmap created: 2026-04-08*
