# Archive Audit: views/converted.archive/

**Created:** 2026-04-07
**Phase:** 03-structural-consolidation (Plan 03-02, Task 5)
**Revised:** 2026-04-07 (review findings: enumerate individual SCSS files)

## Inventory (9 vue files + 2 SCSS files)

| # | File | Runtime Consumers | Test Consumers |
|---|------|-------------------|----------------|
| 1 | backtest-management.vue | 0 | 1 spec (converted-archive-backtest-style-source) |
| 2 | dashboard.vue | 0 | 1 spec (converted-archive-dashboard-style-source) |
| 3 | data-analysis.vue | 0 | 1 spec (converted-archive-shared-style-template) |
| 4 | market-data.vue | 0 | 1 spec (converted-archive-market-data-style-source) |
| 5 | market-quotes.vue | 0 | 0 |
| 6 | risk-management.vue | 0 | 1 spec (converted-archive-shared-style-template) |
| 7 | setting.vue | 0 | 0 |
| 8 | stock-management.vue | 0 | 1 spec (converted-archive-shared-style-template) |
| 9 | trading-management.vue | 0 | 1 spec (converted-archive-trading-management-style-source) |
| 10 | styles/market-data.scss | 0 | 1 spec (converted-archive-market-data-style-source) |
| 11 | styles/market-quotes.scss | 0 | 0 |

## Test Consumer Detail

| Test File | What It Tests | Tests Functionality or Style? |
|-----------|---------------|------------------------------|
| converted-archive-backtest-style-source.spec.ts | Reads backtest-management.vue, checks style patterns | Style source |
| converted-archive-dashboard-style-source.spec.ts | Reads dashboard.vue, checks style patterns | Style source |
| converted-archive-market-data-style-source.spec.ts | Reads market-data.vue + styles/market-data.scss | Style source |
| converted-archive-shared-style-template.spec.ts | Reads 3 archive files, checks @use template compliance | Style template |
| converted-archive-trading-management-style-source.spec.ts | Reads trading-management.vue, checks style patterns | Style source |

## Disposition Recommendations

| File | Recommendation | Reason |
|------|---------------|--------|
| All 10 vue + 2 SCSS | **Remove tests + delete archive** | Zero runtime consumers. All tests validate style patterns in files that have no runtime purpose. Tests guard dead code. |

**Safe path:** Delete the 5 test files first, then delete `views/converted.archive/` entirely.

**Risk:** Low — no runtime code imports these files. Only test infrastructure references them.

**STRU-05 status (archive portion):** Can proceed after removing 5 test files. Test files are: `tests/unit/config/converted-archive-*.spec.ts` (5 files).

---

## Post-Deletion Confirmation (2026-04-09)

### views/converted.archive/ — DELETED

All 11 files removed. Zero runtime consumers existed. Config exclusions removed from:
- tsconfig.json (line 100)
- .stylelintignore (line 6)

### views/demo/ — CONFIRMED ACTIVE (Not Applicable for Removal)

Per DEMO-AUDIT.md evidence and ARCH-03 disposition:
- Has direct consumers (views importing from demo subdirectories), composables, styles
- 8+ test files reference demo/ views
- Route truth unresolved: router/index.js (legacy) has 6 demo routes; router/index.ts (active via main-standard.ts) has none
- Phase 6 does NOT assert demo routes are "active" — only that the directory cannot be safely deleted
- Route truth is a Phase 7 cross-cutting concern (D-08)

**STRU-05 demo portion: Not Applicable.** views/demo/ directory cannot be safely deleted.
