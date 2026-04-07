# Milestones

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

- STRU-03: 2 frontend entry files remain (verify-mount.js blocks main.js removal)
- STRU-04: Composables relocation deferred (15+ active imports would break)
- STRU-05: Archive removal needs 5 test files deleted first; demo/ is active code

### Archive

- [v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md) — full roadmap with phase details
- [v1.0-REQUIREMENTS.md](milestones/v1.0-REQUIREMENTS.md) — all 20 requirements with outcomes
