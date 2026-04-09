# Phase 6: Archive Cleanup - Context

**Gathered:** 2026-04-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Remove `views/converted.archive/` (9 vue files + 2 SCSS files) after handling its 5 test consumers. Confirm `views/demo/` is active code and mark demo/ removal as "not applicable" in traceability. Clean up config references to the deleted archive. Leave the system building and tests passing.

</domain>

<decisions>
## Implementation Decisions

### Test file disposition
- **D-01:** Review the 5 `converted-archive-*.spec.ts` test files for reusable logic (e.g., style template compliance patterns) before deleting. If useful patterns exist for active views, planner may create replacement tests. If not, proceed to straight deletion.
- **D-02:** Two-step execution: Step 1 deletes 5 test files + fixes ARCHIVE-AUDIT.md header. Step 2 deletes archive directory + removes config exclusions + updates traceability. This matches the 2-commit strategy.
- **D-03:** No per-test deletion rationale needed — ARCHIVE-AUDIT.md already documents why each test is safe to remove.

### Config reference cleanup
- **D-04:** Remove `converted.archive` exclusion from `tsconfig.json` (line 100) and `.stylelintignore` (line 6) as part of Step 2 (atomic with archive directory deletion). **Why not Step 1:** `npm run build` runs `vue-tsc --noEmit`; removing the exclusion while archive files still exist would re-introduce them into type checking and break the build.
- **D-05:** **EXPLICIT BOUNDARY:** Only remove `converted.archive` references. Do NOT touch `demo` exclusion in `tsconfig.json` (line 108). This is archive cleanup only, not type debt remediation.

### Deletion approval
- **D-06:** `web/frontend/ARCHIVE-AUDIT.md` is the review-before-delete document — no separate DELETION-CANDIDATES entry needed.

### demo/ confirmation
- **D-07:** `views/demo/` cannot be safely deleted — it has direct consumers (views importing from demo subdirectories), composables, styles, and test references (`tests/all-pages-accessibility.spec.ts`, `tests/menu-configuration.spec.js`, plus 3 style-source specs). ARCH-03 marks demo/ removal as "not applicable". Update REQUIREMENTS.md traceability and append note to ARCHIVE-AUDIT.md.
- **D-08:** **Route truth unresolved:** `router/index.js` has 6 demo routes but `router/index.ts` (the active entry point via `main-standard.ts`) has none. Whether demo is reachable at runtime depends on which router entry point Phase 7 consolidates to. Phase 6 does NOT assert demo routes are "active" — only that the directory cannot be safely deleted. Route truth is a Phase 7 cross-cutting concern.

### Verification
- **D-09:** Verification after each step: `npm run build` + full `vitest run` (not just targeted subset). ARCH-04 requires full test suite pass, and deleting test files justifies a full run to catch unexpected side effects.

### Housekeeping
- **D-10:** Fix ARCHIVE-AUDIT.md header from "10 vue files + 2 SCSS files" to "9 vue files + 2 SCSS files" — actual count is 9 vue + 2 SCSS = 11 total. ROADMAP/REQUIREMENTS correctly say 11 files.

### Git commit strategy
- **D-11:** Two commits matching the two-step approach:
  - Commit 1: Delete 5 test files + fix ARCHIVE-AUDIT.md header
  - Commit 2: Delete `views/converted.archive/` (11 files) + remove tsconfig.json exclusion + remove .stylelintignore exclusion + update REQUIREMENTS.md traceability + update STATE.md + append demo/ confirmation to ARCHIVE-AUDIT.md

### Claude's Discretion
- Exact test review methodology (which patterns to look for, what constitutes "useful")
- Verification command details (vitest flags, timeout settings)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Audit evidence
- `web/frontend/ARCHIVE-AUDIT.md` — Full inventory of archive files, test consumer analysis, disposition recommendations. Serves as review-before-delete document per PROJECT.md convention.
- `web/frontend/DEMO-AUDIT.md` — Demo directory audit: routes, consumers, test coverage. Evidence that demo/ is active code.
- `web/frontend/COMPOSABLES-AUDIT.md` — Composable audit (Phase 5 context, relevant for demo/composables/ reference).

### Config files to modify
- `web/frontend/tsconfig.json` §100 — `converted.archive` exclusion line to remove
- `web/frontend/.stylelintignore` §6 — `converted.archive` exclusion line to remove

### Planning artifacts
- `.planning/ROADMAP.md` §Phase 6 — Phase scope, requirements, success criteria
- `.planning/REQUIREMENTS.md` §ARCH-01 through ARCH-04 — Acceptance criteria
- `.planning/STATE.md` — Current project state

### Entry point context (Phase 7 cross-cutting)
- `web/frontend/src/main-standard.ts` — Active entry point, imports `router/index.ts`
- `web/frontend/src/router/index.ts` — Active router (no demo routes)
- `web/frontend/src/router/index.js` — Legacy router (has 6 demo routes)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ARCHIVE-AUDIT.md`: Already contains full file inventory, test consumer mapping, and disposition recommendations. No need to rediscover this.
- `DEMO-AUDIT.md`: Already contains route mapping, consumer analysis, and risk assessment for demo/.

### Established Patterns
- Two-step deletion: test consumers first, then dead code directory (established in Phase 3 structural consolidation)
- Review-before-delete: audit MD document serves as approval record (established in v1.0 DEAD-06)
- Config cleanup paired with deletion: remove exclusion entries when deleting excluded code

### Integration Points
- `tests/unit/config/` — Location of all 5 archive test files
- `views/converted.archive/styles/` — Contains 2 SCSS files also referenced by tests
- `router/index.ts` — Active router, must NOT be modified in this phase (demo routes gap is Phase 7 scope)
- `router/index.js` — Legacy router with demo routes, read-only reference for this phase

</code_context>

<specifics>
## Specific Ideas

- ARCHIVE-AUDIT.md should be kept as historical audit evidence, not deleted with the archive
- demo/ confirmation note should cite directory evidence (views, composables, styles) and test references, while noting route truth is unresolved and deferred to Phase 7

</specifics>

<deferred>
## Deferred Ideas

- Adding demo routes to `router/index.ts` — Phase 7 (Entry Consolidation) scope
- Type debt remediation for `views/demo/` tsconfig exclusion — separate concern, not this phase
- Broader test suite cleanup or consolidation — out of scope

</deferred>

---

*Phase: 06-archive-cleanup*
*Context gathered: 2026-04-09*
