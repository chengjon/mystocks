# Phase 6: Archive Cleanup - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-09
**Phase:** 06-archive-cleanup
**Areas discussed:** Test file disposition, Config reference cleanup, Deletion approval format, demo/ confirmation approach, Verification criteria, demo route truth source, File count fix, Commit strategy, Audit doc retention

---

## Test File Disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Delete all 5 outright | Tests guard dead code style patterns, no value for active code | |
| Review + extract before deleting | Check if any test logic could be repurposed for active views | ✓ |

**User's choice:** Review + extract before deleting
**Notes:** Planner/researcher decides whether to create new tests if useful patterns found. Two-step execution (tests first, then archive). No per-test deletion rationale needed.

---

## Config Reference Cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Clean up now | Remove converted.archive exclusions from tsconfig.json + stylelintignore | ✓ |
| Leave for later | Harmless dead references, future lint pass | |

**User's choice:** Clean up now
**Notes:** EXPLICIT BOUNDARY — only remove converted.archive references (tsconfig line 100, stylelintignore line 6). Do NOT touch demo exclusion (tsconfig line 108).

---

## Deletion Approval Format

| Option | Description | Selected |
|--------|-------------|----------|
| ARCHIVE-AUDIT.md sufficient | Already has full inventory + disposition | ✓ |
| Add to DELETION-CANDIDATES.md | Separate formal approval tracking | |

**User's choice:** ARCHIVE-AUDIT.md is sufficient

---

## demo/ Confirmation Approach

| Option | Description | Selected |
|--------|-------------|----------|
| REQUIREMENTS.md only | Update traceability table | |
| REQUIREMENTS.md + ARCHIVE-AUDIT.md | Update traceability + add confirmation note to audit doc | ✓ |
| REQUIREMENTS.md + demo/README.md | Update traceability + update demo README | |

**User's choice:** REQUIREMENTS.md + ARCHIVE-AUDIT.md
**Notes:** Append demo/ confirmation note to ARCHIVE-AUDIT.md citing directory evidence and router/index.js routes.

---

## Verification Criteria (from review)

| Option | Description | Selected |
|--------|-------------|----------|
| Full vitest run | Run complete test suite after each step | ✓ |
| Targeted: tests/unit/config only | Faster but narrower | |
| Build only, skip vitest | Tests being deleted can't fail | |

**User's choice:** Full vitest run
**Notes:** ARCH-04 requires test suite pass. Deleting test files justifies full run to catch unexpected side effects.

---

## demo Route Truth Source (from review)

| Option | Description | Selected |
|--------|-------------|----------|
| Document gap, defer to Phase 7 | demo routes in index.js but not index.ts. Phase 7 handles entry consolidation | ✓ |
| Add demo routes to index.ts now | Expands Phase 6 scope but closes gap | |

**User's choice:** Document gap, defer to Phase 7
**Notes:** HIGH finding — main-standard.ts imports index.ts which has ZERO demo routes. All demo routes only in index.js. This is a Phase 7 cross-cutting concern.

---

## Archive File Count Fix (from review)

| Option | Description | Selected |
|--------|-------------|----------|
| Fix header in this phase | Correct "10 vue + 2 SCSS" to "9 vue + 2 SCSS" | ✓ |
| Leave as-is | Header cosmetic, table and ROADMAP correct | |

**User's choice:** Fix header in this phase

---

## Commit Strategy (from review)

| Option | Description | Selected |
|--------|-------------|----------|
| 2 commits (matches 2-step) | Commit 1: tests + config + header fix. Commit 2: archive + traceability | ✓ |
| Single commit | Everything in one | |

**User's choice:** 2 commits

---

## Audit Doc Retention (from review)

| Option | Description | Selected |
|--------|-------------|----------|
| Keep and update | Append demo/ confirmation, keep as historical evidence | ✓ |
| Keep as-is | Don't modify | |

**User's choice:** Keep and update

---

## Claude's Discretion

- Exact test review methodology (which patterns to look for, what constitutes "useful")
- Verification command details (vitest flags, timeout settings)

## Deferred Ideas

- Adding demo routes to router/index.ts — Phase 7 (Entry Consolidation)
- Type debt remediation for views/demo/ tsconfig exclusion — separate concern
- Broader test suite cleanup or consolidation — out of scope
