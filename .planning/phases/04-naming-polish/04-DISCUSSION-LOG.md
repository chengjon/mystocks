# Phase 4: Naming & Polish - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-07
**Phase:** 04-naming-polish
**Areas discussed:** Shim disposition, Naming conventions, Store domains

---

## Shim Disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Audit-then-remove | Delete shims only if zero callers after redirecting all imports | |
| Deprecate-in-place | Add warnings.warn() to each shim, keep for one release cycle | ✓ |
| Keep as-is | Document shims as intentional re-export points | |

**User's choice:** Deprecate-in-place
**Follow-up:** Deprecate now, remove later — do NOT redirect callers or remove shims in this phase

---

## Naming Conventions — calcu/ rename

| Option | Description | Selected |
|--------|-------------|----------|
| src/calculators/ | Natural semantic name for calculation utilities | ✓ |
| Merge into src/utils/ | Simpler tree but may dilute utils/ scope | |
| Domain-specific name | e.g. src/block_calculators/ | |

**User's choice:** src/calculators/

---

## Naming Conventions — part files

| Option | Description | Selected |
|--------|-------------|----------|
| Semantic names | Rename based on actual contents (e.g. _queries.py, _mutations.py) | ✓ |
| Merge into parent | All 3 parts into __init__.py or single file | |
| Single _methods.py | One file per module | |

**User's choice:** Semantic names (researcher/planner must read contents first)

---

## Naming Conventions — *_new.py files

| Option | Description | Selected |
|--------|-------------|----------|
| Replace canonical | Verify _new is complete, rename to replace old, delete old | ✓ |
| Document both | Keep both, document why | |
| Delete _new.py | Delete if canonical is adequate | |

**User's choice:** Replace canonical (2 files: database_service_new.py, decision_models_analyzer_new.py)

---

## Store Domains

| Option | Description | Selected |
|--------|-------------|----------|
| Document boundaries | Write domain boundary comments, note merge candidates | ✓ |
| Merge overlapping pairs | Merge market→marketData, trading→tradingData | |
| Cleanup backup only | Just delete .bak file | |

**User's choice:** Document boundaries — do NOT merge in this phase

---

## Claude's Discretion

- Exact semantic names for part{1,2,3}.py files
- Deprecation warning wording
- Whether to add STORES.md overview or just inline comments

## Deferred Ideas

- Root shim removal (after deprecation cycle)
- Store merging (if overlap confirmed)
- Phase 3 deferred items (STRU-03/04/05)
