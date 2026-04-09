# Milestones

## v1.1 Final Polish (Shipped: 2026-04-09)

**Phases:** 3 | **Plans:** 5 | **Commits:** ~20 | **Timeline:** 2 days (Apr 8–9)

### Key Accomplishments

1. Established view-local composables as canonical pattern in STANDARDS.md; audited 2 extraction candidates, kept both view-local per evidence
2. Deleted views/converted.archive/ (11 files, 5,759 lines) and 5 exclusive test consumers; removed config exclusions
3. Rewrote main-standard.ts with all 7 production capabilities (icons, security, PWA, session restore, version negotiation, contract validation, debug instance)
4. Archived main.js to _entry-archive/; main-standard.ts confirmed as sole entry point
5. Deleted verify-mount.js and 6 dead router artifacts; created OpenSpec proposal with validated spec delta

### Known Gaps

- F821 ruff errors: 791 in 62 files — deferred to future milestone
- 6 pre-existing vitest failures (chart styles, type cleanup, system settings)

### Archive

- [v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md) — full roadmap with phase details
- [v1.1-REQUIREMENTS.md](milestones/v1.1-REQUIREMENTS.md) — all 10 requirements with outcomes
- [v1.1-MILESTONE-AUDIT.md](milestones/v1.1-MILESTONE-AUDIT.md) — milestone audit (passed)

---

## v1.0 Codebase Consolidation — SHIPPED 2026-04-08

**Phases:** 4 | **Plans:** 10 | **Commits:** ~54 | **Timeline:** 3 days (Apr 5–8)

### Key Accomplishments

1. Reduced ruff errors from 1,456 to 863 (41% reduction)
2. Deleted 34 dead files across 5 directories after 8-type sweep analysis
3. Merged frontend case-conflict directories (Charts→charts), archived 6 unused entry variants
4. Removed all 3 root-level shim files, added deprecation warnings to src/ re-exports
5. Renamed 32 part-files to semantic names, resolved _new.py files, removed src/calcu/
6. Documented Pinia store domain boundaries for overlapping pairs

### Known Gaps

- ~~STRU-03: 2 frontend entry files remain (verify-mount.js blocks main.js removal)~~ → Resolved in v1.1
- ~~STRU-04: Composables relocation deferred (15+ active imports would break)~~ → Resolved in v1.1
- ~~STRU-05: Archive removal needs 5 test files deleted first; demo/ is active code~~ → Resolved in v1.1

### Archive

- [v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md) — full roadmap with phase details
- [v1.0-REQUIREMENTS.md](milestones/v1.0-REQUIREMENTS.md) — all 20 requirements with outcomes
