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
- **D-01:** Complete caller inventory for each root shim FIRST (per ROADMAP.md sub-stage 4a step 1). Check: scripts/, Dockerfiles, docker-compose files, CI configs, and Python imports.
- **D-02:** After inventory, decide disposition per shim (Remove / Deprecate / Keep). The decision must be data-driven from the inventory results: zero-callers → Remove, few callers → Deprecate, many callers → Keep with documentation. Do NOT pre-decide disposition before inventory is complete.
- **D-03:** For shims marked Deprecate: add `warnings.warn("... is deprecated, use src....", DeprecationWarning)` + comment pointing to canonical `src.*` import path. Do NOT redirect callers or remove shims in this phase.

### Naming Conventions
- **D-04:** Rename `src/calcu/` → `src/calculators/` (git mv, update all imports)
- **D-05:** Rename `part{1,2,3}.py` files to semantic names based on actual contents — researcher/planner must read each file to determine the right name before renaming
- **D-06:** For `*_new.py` files: verify `_new` version is functionally complete, then rename to replace the canonical file and delete the old one (git mv for history)
  - `src/database/database_service_new.py` → replace `src/database/database_service.py` (same directory)
  - `src/advanced_analysis/decision_models/decision_models_analyzer_new.py` → replace `src/advanced_analysis/decision_models_analyzer.py` (WARNING: `_new` file is inside `decision_models/` subpackage but canonical target is in parent `advanced_analysis/` — requires move UP one directory, not a same-directory rename)
- **D-07:** Audit `baseStore.ts.bak` in `web/frontend/src/stores/` for consumers per DELETION-CANDIDATES pattern (architecture/STANDARDS.md:103 — requires both code-path grep AND functional-tree audit). Delete ONLY if both checks confirm zero consumers; otherwise document why it's retained

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
- **Root-level shims** (compatibility wrappers at repo root, NOT canonical implementations — these are the Phase 4 targets):
  - `core.py` (root) — re-exports from `src/core/`
  - `data_access.py` (root) — re-exports from `src/data_access/`
  - `monitoring.py` (root) — re-exports from `src/monitoring/`
- **src/ internal re-exports** (shims inside `src/` — separate from root shims, disposition may differ):
  - `src/core.py` — re-exports from `src/core/` (NOT the same as root `core.py`)
  - `src/data_access.py` — re-exports from `src/data_access/` (NOT the same as root `data_access.py`)
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
- **32 `part{1,2,3}.py` files across 11 modules** (not 6 in 2 — full inventory required for NAME-02):
  - `src/adapters/efinance_adapter/efinance_data_source_methods/part{1,2,3}.py`
  - `src/core/deduplication_strategy_methods/part{1,2,3}.py`
  - `src/data_sources/real/postgresql_relational/postgre_sql_relational_data_source_methods/part{1,2,3}.py`
  - `src/data_sources/real/tdengine_timeseries/t_dengine_time_series_data_source_methods/part{1,2}.py`
  - `src/governance/risk_management/calculators/gpu_calculator/gpu_risk_calculator_methods/part{1,2,3}.py`
  - `src/governance/risk_management/services/stop_loss_engine/stop_loss_engine_methods/part{1,2,3}.py`
  - `src/gpu/acceleration/feature_calculation_gpu/feature_calculation_gpu_methods/part{1,2,3}.py`
  - `src/gpu/acceleration/optimization_gpu_methods/part{1,2,3}.py`
  - `src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/part{1,2,3}.py`
  - `src/monitoring/monitoring_database_methods/part{1,2,3}.py`
  - `src/storage/database/database_manager/database_table_manager_methods/part{1,2,3}.py`
- 2 `*_new.py` files:
  - `src/database/database_service_new.py`
  - `src/advanced_analysis/decision_models/decision_models_analyzer_new.py` (canonical: `src/advanced_analysis/decision_models_analyzer.py` in parent package)
- Root-level shims: `core.py`, `data_access.py`, `monitoring.py` + src/ internal re-exports: `src/core.py`, `src/data_access.py`
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
