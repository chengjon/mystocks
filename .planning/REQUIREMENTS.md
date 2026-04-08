# Requirements: MyStocks Codebase Consolidation — v1.1

**Defined:** 2026-04-08
**Core Value:** Every file has exactly one canonical location, every import resolves cleanly, zero lint errors.

## v1.1 Requirements

### Entry Consolidation

- [ ] **ENTRY-01**: verify-mount.js disposition resolved (updated to reference main-standard.ts, or removed with justification)
- [ ] **ENTRY-02**: main.js archived after verify-mount.js no longer depends on it
- [ ] **ENTRY-03**: Single active entry point confirmed (main-standard.ts only), `npm run dev` and `npm run build` both succeed

### Composables Re-scoping

- [ ] **COMP-01**: COMPOSABLES-AUDIT.md reviewed and disposition decided for each of the 2 extraction candidates
- [ ] **COMP-02**: View-local pattern (15/17 composables) accepted as canonical and documented; only the 2 extraction candidates may be migrated
- [ ] **COMP-03**: Any extracted composables placed in src/composables/ with all consumer imports updated, `vue-tsc --noEmit` passes

### Archive Removal

- [ ] **ARCH-01**: 5 test consumers of views/converted.archive/ identified, updated or removed
- [ ] **ARCH-02**: views/converted.archive/ directory deleted (11 files removed)
- [ ] **ARCH-03**: views/demo/ confirmed as active code and marked "not applicable" for removal in REQUIREMENTS.md traceability
- [ ] **ARCH-04**: Test suite passes after archive removal, no dangling references

## Out of Scope

| Feature | Reason |
|---------|--------|
| F821 resolution | Deferred to future milestone — 791 errors, 62 files, separate focus needed |
| Bulk composable migration | v1.0 audit proves 15/17 are view-local; bulk move breaks 15+ imports |
| views/demo/ removal | Active code: 5 routes, 3+ views, 8+ tests — not dead code |
| New feature development | This is cleanup only |
| Mobile/responsive changes | Desktop-only per project constraints |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| COMP-01 | Phase 5 | Pending |
| COMP-02 | Phase 5 | Pending |
| COMP-03 | Phase 5 | Pending |
| ARCH-01 | Phase 6 | Pending |
| ARCH-02 | Phase 6 | Pending |
| ARCH-03 | Phase 6 | Pending |
| ARCH-04 | Phase 6 | Pending |
| ENTRY-01 | Phase 7 | Pending |
| ENTRY-02 | Phase 7 | Pending |
| ENTRY-03 | Phase 7 | Pending |

**Coverage:**
- v1.1 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-08*
*Last updated: 2026-04-08 after v1.1 requirement definition*
