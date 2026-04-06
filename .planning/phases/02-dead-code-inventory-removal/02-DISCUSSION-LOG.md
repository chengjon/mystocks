# Phase 2: Dead Code Inventory & Removal - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-06
**Phase:** 02-dead-code-inventory-removal
**Areas discussed:** Test/Script caller policy, Merge conflict resolution, DELETION-CANDIDATES format, Commit granularity

---

## Test/Script Caller Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Redirect all + fix tests | Redirect production callers, update test imports too, delete broken tests if the feature is gone | ✓ |
| Redirect prod only, document rest | Redirect production callers only. Mark test/script references in DELETION-CANDIDATES.md | |
| Redirect prod, delete rest with no fix | Only redirect callers for directories that have production importers | |

**User's choice:** Redirect all + fix tests (recommended)
**Notes:** Also chose to update dev script imports (not leave them as-is). If no canonical replacement exists for a test import, mark test as `@pytest.mark.skip`.

---

## Merge Conflict Resolution

| Option | Description | Selected |
|--------|-------------|----------|
| Canonical wins, copy-only-new | src/data_access/ wins, only copy files that don't exist there | ✓ |
| Manual diff per file | Compare each file pair, merge unique functions/classes | |
| Redirect-only, no merge | Just redirect imports, delete dead layers without merging | |

**User's choice:** Canonical wins, copy-only-new (recommended)
**Notes:** No diffing — if canonical has a file, it's authoritative.

---

## DELETION-CANDIDATES Format

| Option | Description | Selected |
|--------|-------------|----------|
| Table-per-target | One table per target directory (5 tables). Compact, scannable | ✓ |
| Full-per-file detail | One section per file (30+ sections). Exhaustive | |
| Summary + appendix | Single summary table + detailed appendix | |

**User's choice:** Table-per-target (recommended)
**Notes:** Must include grep evidence as inline command output and functional tree per module.

---

## Commit Granularity

| Option | Description | Selected |
|--------|-------------|----------|
| Per sub-stage (3 commits) | Inventory doc, redirects+merge, deletions | ✓ |
| Per target (5 commits) | One per deletion target | |
| Single commit | Everything in one commit | |

**User's choice:** Per sub-stage (recommended)
**Notes:** 3 commits: (1) DELETION-CANDIDATES.md, (2) redirects + merge, (3) deletions.

---

## Claude's Discretion

- Exact grep commands for caller inventory
- Whether to run ruff check per redirect or batched
- Backup tag strategy before deletion
- Circular import handling during merge

## Deferred Ideas

- None — discussion stayed within phase scope
