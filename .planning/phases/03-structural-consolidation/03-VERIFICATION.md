# Plan Verification Report — Phase 3

**Checker:** plan-phase manual verification
**Date:** 2026-04-07
**Plans verified:** 03-01-PLAN.md, 03-02-PLAN.md

---

## Goal-Backward Analysis

### Phase 3 Goal (from ROADMAP.md)
Establish single canonical locations for frontend components, verify data access consolidation, audit and consolidate frontend entry points, and audit dead frontend artifacts.

### Does Plan 03-01 achieve its stated goal?
**YES.** Case-conflict merge + entry audit + variant archive covers sub-stages 3a, 3b, and 3d-i. All 6 tasks have specific read-first, action, and acceptance criteria blocks. Two-step git mv workaround documented for WSL2 case-sensitivity.

### Does Plan 03-02 achieve its stated goal?
**YES.** Data access verification + frontend audit documentation covers sub-stages 3c, 3d-ii, 3d-iii, 3d-iv. Produces audit artifacts (COMPOSABLES-AUDIT.md, ARCHIVE-AUDIT.md, DEMO-AUDIT.md) with grep evidence per CONTEXT.md D-14.

---

## Requirements Coverage

| Req | Description | Plan Coverage | Status |
|-----|-------------|---------------|--------|
| LINT-04 | Case-conflict dirs merged to lowercase | 03-01 Tasks 2-4 | ✅ Covered |
| STRU-01 | Single data access layer | 03-02 Tasks 1-3 | ✅ Covered (verification) |
| STRU-02 | All imports updated | 03-01 Tasks 2-4 + 03-02 Task 1 | ✅ Covered |
| STRU-03 | Single frontend entry point | 03-01 Tasks 1+5 (doc + archive, 2 files remain) | 🔶 Partial |
| STRU-04 | views/composables/ relocated | 03-02 Task 4 (audit evidence only) | 🔴 Not completed |
| STRU-05 | views/converted.archive/ + views/demo/ removed | 03-02 Tasks 5-6 (audit evidence only) | 🔴 Not completed |

### Deferred Requirements Justification

**STRU-04** (composables relocation): CONTEXT.md D-11 revised to "AUDIT before any move" after discovering MIGRATION_PROGRESS.md classifies 15/17 files as "Keep view-local". Bulk move would break 15+ relative imports. Plan 03-02 Task 4 produces the grep evidence needed for a future informed decision.

**STRU-05** (archive + demo removal): CONTEXT.md D-12/D-13 revised to "AUDIT before deletion" after discovering active consumers (6 demo routes, 8+ Vitest specs, OpenStockDemo.vue). Premature deletion would break tests and active pages. Plan 03-02 Tasks 5-6 produce consumer inventories with disposition recommendations.

Both deferrals follow the DELETION-CANDIDATES pattern established in Phase 2 and comply with `architecture/STANDARDS.md:103` functional tree analysis requirement.

---

## ROADMAP Success Criteria Coverage

| # | Criterion | Plan | Task |
|---|-----------|------|------|
| 1 | Frontend entry truth documented | 03-01 | Task 1 (ENTRY-TRUTH.md) |
| 2 | No case-conflict dirs remain | 03-01 | Tasks 2-4 + acceptance criteria |
| 3 | npm run build succeeds | 03-01 | Task 6 |
| 4 | stylelint passes (zero errors) | 03-01 | Task 6 |
| 5 | src/data_access/ is sole layer | 03-02 | Tasks 1-2 |
| 6 | FastAPI starts | 03-02 | Task 3 |

---

## Gaps Found

### Gap 1: views/monitoring/ classification (ROADMAP sub-stage 3d item 3)
**Severity:** LOW — not a REQUIREMENTS.md tracked item, but ROADMAP §3d item 3 mentions classifying `views/monitoring/`
**Recommendation:** Add to Plan 03-02 as an optional Task 7b, or defer to Phase 4

### Gap 2: STRU-03 only partially met — two entry files remain
**Severity:** HIGH — requirement says "exactly one entry point" but main-standard.ts + main.js both remain in src/
**Root cause:** main.js cannot be removed because verify-mount.js reads it. Task 1 only produces documentation; Task 5 archives 6 others but does not converge to one.
**Recommendation:** Wave 3 must either update verify-mount.js to reference main-standard.ts (or remove verify-mount.js), then archive main.js. Only then does STRU-03 pass.

### Gap 3: STRU-04 and STRU-05 not completed — audit-only
**Severity:** HIGH — requirements say "relocated" and "removed", plans only produce audit evidence
**Recommendation:** Wave 3 plan needed after audit results are available. REQUIREMENTS.md traceability must be updated to reflect two-step approach (audit → then act).

---

## CONTEXT.md Decision Coverage

| Decision | Plan Coverage |
|----------|---------------|
| D-01 to D-06 (case merge) | 03-01 Tasks 2-4 |
| D-07 to D-09 (entry audit) | 03-01 Tasks 1, 5 |
| D-10 (rename if needed) | N/A — not renaming, keeping main-standard.ts |
| D-11 (composables audit) | 03-02 Task 4 |
| D-12 (archive audit) | 03-02 Task 5 |
| D-13 (demo audit) | 03-02 Task 6 |
| D-14 (DELETION-CANDIDATES pattern) | 03-02 Tasks 4-6 |
| D-15 to D-17 (data access verify) | 03-02 Tasks 1-3 |
| D-18 to D-20 (ordering) | Plans sequenced correctly |
| D-21 to D-22 (verification) | 03-01 Task 6, 03-02 Task 7 |

---

## Verdict

**CONDITIONAL — plans are executable but do not complete Phase 3 requirements.**

Plans 03-01 and 03-02 are well-structured and safe to execute. However, 3 of 6 Phase 3 requirements (STRU-03, STRU-04, STRU-05) will remain incomplete after both waves finish:

- **STRU-03**: Two entry files remain (main-standard.ts + main.js). Convergence blocked by verify-mount.js consumer.
- **STRU-04**: Audit-only, no relocation. Bulk move would break 15+ relative imports per MIGRATION_PROGRESS.md.
- **STRU-05**: Audit-only, no removal. Both directories have active consumers (routes, views, tests).

The deferrals are justified per CONTEXT.md revised decisions and `architecture/STANDARDS.md:103` deletion governance. However, downstream execution agents must NOT interpret "CONDITIONAL" as "all requirements met."

**Required follow-up:** After Waves 1+2 complete, a Wave 3 plan must address:
1. verify-mount.js disposition → unblock STRU-03 convergence
2. COMPOSABLES-AUDIT.md evidence → informed STRU-04 decision
3. ARCHIVE-AUDIT.md + DEMO-AUDIT.md evidence → informed STRU-05 decision

**Recommended next step:** Execute Plan 03-01, then Plan 03-02, then create Wave 3 plan using audit evidence to close STRU-03/04/05.
