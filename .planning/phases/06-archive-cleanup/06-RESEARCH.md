# Phase 6: Archive Cleanup - Research

**Created:** 2026-04-09
**Phase:** 06-archive-cleanup

## Summary

Phase 6 is a straightforward deletion task with clear scope and low risk. The `views/converted.archive/` directory contains 11 dead files (9 vue + 2 SCSS) with zero runtime consumers. Five test files exclusively reference these dead files. Two config exclusion entries (`tsconfig.json`, `.stylelintignore`) reference the archive directory. The `views/demo/` directory is confirmed active code and cannot be removed.

---

## File Inventory

### Archive directory (11 files to delete)

| # | File | Test Consumer |
|---|------|---------------|
| 1 | `web/frontend/src/views/converted.archive/backtest-management.vue` | converted-archive-backtest-style-source.spec.ts |
| 2 | `web/frontend/src/views/converted.archive/dashboard.vue` | converted-archive-dashboard-style-source.spec.ts |
| 3 | `web/frontend/src/views/converted.archive/data-analysis.vue` | converted-archive-shared-style-template.spec.ts |
| 4 | `web/frontend/src/views/converted.archive/market-data.vue` | converted-archive-market-data-style-source.spec.ts |
| 5 | `web/frontend/src/views/converted.archive/market-quotes.vue` | none |
| 6 | `web/frontend/src/views/converted.archive/risk-management.vue` | converted-archive-shared-style-template.spec.ts |
| 7 | `web/frontend/src/views/converted.archive/setting.vue` | none |
| 8 | `web/frontend/src/views/converted.archive/stock-management.vue` | converted-archive-shared-style-template.spec.ts |
| 9 | `web/frontend/src/views/converted.archive/trading-management.vue` | converted-archive-trading-management-style-source.spec.ts |
| 10 | `web/frontend/src/views/converted.archive/styles/market-data.scss` | converted-archive-market-data-style-source.spec.ts |
| 11 | `web/frontend/src/views/converted.archive/styles/market-quotes.scss` | none |

### Test consumers (5 files to delete)

| # | Test File | What It Tests | References |
|---|-----------|---------------|------------|
| 1 | `tests/unit/config/converted-archive-backtest-style-source.spec.ts` | Style patterns in backtest-management.vue | 1 vue file |
| 2 | `tests/unit/config/converted-archive-dashboard-style-source.spec.ts` | Style patterns in dashboard.vue | 1 vue file |
| 3 | `tests/unit/config/converted-archive-market-data-style-source.spec.ts` | Style patterns in market-data.vue + market-data.scss | 1 vue + 1 scss |
| 4 | `tests/unit/config/converted-archive-shared-style-template.spec.ts` | @use template compliance across 3 files | data-analysis.vue, risk-management.vue, stock-management.vue |
| 5 | `tests/unit/config/converted-archive-trading-management-style-source.spec.ts` | Style patterns in trading-management.vue | 1 vue file |

All 5 tests validate style patterns in dead code — no reusable test logic for active views.

### Config references (2 entries to remove)

| Config File | Line | Entry | Action |
|-------------|------|-------|--------|
| `web/frontend/tsconfig.json` | 100 | `"src/views/converted.archive/**/*", // 归档文件，不进行类型检查` | Remove line |
| `web/frontend/.stylelintignore` | 6 | `**/converted.archive/**` | Remove line |

### Other references (documentation only, no action needed)

- `architecture/STANDARDS.md` — mentions `converted.archive/` as example of temporary naming convention
- `scripts/dev/tools/generate_large_file_splitting_inventory.sh` — excludes archive directory from inventory; reference becomes harmless after deletion
- Various `docs/reports/` and `openspec/changes/` — historical references, no code impact
- `web/frontend/ARCHIVE-AUDIT.md` — kept as audit evidence (not deleted)

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Dangling import in active code | LOW | Grep confirms zero runtime consumers |
| Test suite breaks after test deletion | LOW | Deleted tests only test dead code; remaining tests unaffected |
| Build breaks after config change | LOW | Removing exclusion from tsconfig is safe because archive files will be gone; `vue-tsc --noEmit` won't scan deleted files |
| Accidental deletion of demo/ code | NONE | Explicit boundary: only converted.archive, never demo |
| Git history references become stale docs | NONE | Historical docs remain accurate as-of their creation date |

**Overall risk: LOW.** This is a deletion-only task with clear scope boundaries.

---

## Dependencies and Ordering

**Strict ordering required:**

1. **Step 1** — Delete 5 test files + fix ARCHIVE-AUDIT.md header
   - Tests must go first because deleting archive while tests exist would cause test failures
   - Fix header from "10 vue files" to "9 vue files"
   - Verify: `vitest run` passes

2. **Step 2** — Delete archive directory + config cleanup + traceability updates
   - Archive deletion after tests are gone
   - Config cleanup must be atomic with archive deletion (not before) to prevent `vue-tsc` from scanning still-existing archive files
   - Update REQUIREMENTS.md traceability (ARCH-01 through ARCH-04)
   - Update STATE.md
   - Append demo/ confirmation to ARCHIVE-AUDIT.md
   - Verify: `npm run build` + `vitest run` pass

**Cannot be parallelized** — Step 2 depends on Step 1 completing successfully.

---

## Key Technical Decisions for Planner

1. **No reusable test patterns** — All 5 test files validate style compliance in dead code. No patterns should be migrated to active view tests.

2. **Two-commit strategy** — Matches the two-step approach (D-11). Each commit leaves the system in a verifiable state.

3. **Config cleanup timing** — Remove tsconfig.json and .stylelintignore exclusions ONLY in Step 2, atomically with archive directory deletion (D-04). Removing earlier would break `npm run build`.

4. **Demo boundary** — Do NOT touch `demo` exclusion in tsconfig.json (line 108). Demo/ is active code with routes and consumers (D-05, D-07).

5. **Route truth deferred** — Whether demo routes are reachable depends on which router entry point Phase 7 consolidates to. Phase 6 only confirms demo/ directory cannot be safely deleted (D-08).

6. **ARCHIVE-AUDIT.md kept** — Serves as historical audit evidence and deletion approval record (D-06).

---

## Validation Approach

After each step:
```bash
cd web/frontend && npx vitest run          # Full test suite
cd web/frontend && npm run build           # Build verification
```

After Step 2, additionally verify:
```bash
grep -r "converted.archive" web/frontend/src/ web/frontend/tests/  # Zero results
grep "converted.archive" web/frontend/tsconfig.json                 # Zero results
grep "converted.archive" web/frontend/.stylelintignore              # Zero results
ls web/frontend/src/views/converted.archive/                        # No such file or directory
```

---

## RESEARCH COMPLETE
