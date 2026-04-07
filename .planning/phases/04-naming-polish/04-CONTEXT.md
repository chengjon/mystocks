# Phase 4: Naming & Polish - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix naming conventions (truncated names, mechanical splits, `_new.py` files), finalize root shim disposition, and clarify Pinia store domain boundaries. This is the final polish phase — no new capabilities, only naming and organizational cleanup.

</domain>

<decisions>
## Implementation Decisions

### Root Shim Disposition
- **D-01:** Deprecate-in-place — add `warnings.warn(DeprecationWarning, "...")` to each root shim (core.py, data_access.py, monitoring.py)
- **D-02:** Do NOT redirect callers or remove shims in this phase. Mark for removal in a future cleanup cycle.
- **D-03:** Add a comment in each shim file pointing to the canonical `src.*` import path

### Naming Conventions
- **D-04:** Rename `src/calcu/` → `src/calculators/` (git mv, update all imports)
- **D-05:** Rename `part{1,2,3}.py` files to semantic names based on actual contents — researcher/planner must read each file to determine the right name before renaming
- **D-06:** For `*_new.py` files: verify `_new` version is functionally complete, then rename to replace the canonical file and delete the old one (git mv for history)
  - `src/database/database_service_new.py` → replace `database_service.py`
  - `src/advanced_analysis/decision_models/decision_models_analyzer_new.py` → replace `decision_models_analyzer.py`
- **D-07:** Delete `baseStore.ts.bak` from `web/frontend/src/stores/`

### Store Domain Clarification
- **D-08:** Document boundaries for overlapping store pairs (market.ts vs marketData.ts, trading.ts vs tradingData.ts) — do NOT merge
- **D-09:** For each store, write a domain boundary comment at the top of the file describing what state/actions it owns
- **D-10:** If one store is clearly a subset of another with zero unique state/actions, note it as a merge candidate for a future phase — do not merge in this phase

### Claude's Discretion
- Exact semantic names for part{1,2,3}.py files (must be based on actual file contents)
- Exact deprecation warning wording
- Whether to add a STORES.md overview doc or just inline comments

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Naming conventions
- `architecture/STANDARDS.md` — Naming conventions, migration governance, file size limits
- `.planning/codebase/CONCERNS.md` — Issues #8, #9, #11 (naming concerns)
- `.planning/research/PITFALLS.md` — P-04 (root shim callers include scripts, Dockerfiles, compose files)

### Root shims
- `.planning/ROADMAP.md` — Global Execution Prerequisites > Root Shim Disposition Table
- `src/core.py`, `data_access.py`, `monitoring.py` — current shim implementations
- `scripts/dev/project/update_imports.py` — references shim import patterns
- `scripts/dev/fix_test_imports.py` — references shim import patterns

### Store domains
- `web/frontend/src/stores/` — all Pinia store files
- `web/frontend/src/stores/market.ts` and `marketData.ts` — overlapping pair
- `web/frontend/src/stores/trading.ts` and `tradingData.ts` — overlapping pair

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/dev/project/update_imports.py` — already has import redirect patterns for core/data_access/monitoring shims
- `scripts/dev/fix_test_imports.py` — test import migration patterns

### Established Patterns
- Phase 3 used two-step `git mv` for WSL2 case-sensitivity — same approach for calcu/ → calculators/
- DELETION-CANDIDATES pattern: audit before any deletion, grep evidence required per `architecture/STANDARDS.md:103`

### Integration Points
- Root shims referenced by Dockerfiles, docker-compose, and CI configs (per PITFALLS P-04)
- `src/calcu/` imports need updating across entire codebase after rename
- Store files are consumed by views via `import { useXxxStore } from '@/stores/xxx'`

### Current State
- `src/calcu/`: 1 block/ subdir + readme.md (truncated name)
- 6 `part{1,2,3}.py` files in 2 modules:
  - `src/monitoring/monitoring_database_methods/part{1,2,3}.py`
  - `src/core/deduplication_strategy_methods/part{1,2,3}.py`
- 2 `*_new.py` files:
  - `src/database/database_service_new.py`
  - `src/advanced_analysis/decision_models/decision_models_analyzer_new.py`
- 3 root shims: core.py (548 bytes), data_access.py (285 bytes), monitoring.py (520 bytes)
- 20+ Pinia stores in `web/frontend/src/stores/`
- 1 stale backup: `baseStore.ts.bak`

</code_context>

<specifics>
## Specific Ideas

- No specific requirements — follow established patterns from prior phases

</specifics>

<deferred>
## Deferred Ideas

- Root shim removal (after deprecation cycle) — future cleanup
- Store merging (if documented boundaries reveal true overlap) — future phase
- Phase 3 deferred items (STRU-03/04/05) — separate Wave 3 follow-up

</deferred>

---

*Phase: 04-naming-polish*
*Context gathered: 2026-04-07*
