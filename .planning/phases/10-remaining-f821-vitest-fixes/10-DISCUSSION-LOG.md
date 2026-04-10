# Phase 10: Remaining F821 + Vitest Fixes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-10
**Phase:** 10-remaining-f821-vitest-fixes
**Areas discussed:** F821 analysis, Vitest strategy, Plan structure

---

## F821 Analysis

11 errors across 6 files. 10 are mechanical missing imports, 1 is a bug (f-string template placeholder).

| Option | Description | Selected |
|--------|-------------|----------|
| All mechanical imports | Fix with standard patterns from Phase 09 | ✓ |
| threshold f-string bug | Remove f-prefix — threshold is template placeholder, not variable | ✓ |

**Notes:** Phase 09 decisions (D-01 conditional imports, D-08 canonical locations) carry forward directly.

---

## Vitest Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Full realignment | Rewrite stale tests to match current canonical components | ✓ |
| Minimal mock patch | Only add missing mocks, leave assertions as-is | |
| Delete stale tests | Remove wrapper component tests entirely | |

**Notes:** User identified that the vitest situation is NOT just mock coverage. Two components (ArtDecoSystemSettings, ArtDecoDataManagement) are now thin wrappers re-exporting canonical Settings.vue/DataSource.vue. Tests assert old ArtDeco-specific text and call methods that no longer exist.

---

## Plan Structure

| Option | Description | Selected |
|--------|-------------|----------|
| 3 plans | F821 clearance / Chart paths / System settings realignment | ✓ |
| 2 plans | F821 / All vitest combined | |
| 1 combined plan | Everything together | |

**Notes:** Separating mechanical F821 from semantic test realignment gives cleaner verification gates.

---

## Claude's Discretion

- Exact import ordering within groups
- Canonical source locations for NewsArticle, DatabaseService, DatabaseType
- Whether to update chart test paths or verify file existence first
- Per-file verification sequence

## Deferred Ideas

None — discussion stayed within phase scope.
