# Phase 10: Remaining F821 + Vitest Fixes - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Resolve final 11 F821 errors in 6 scattered Python files, then fix 7 vitest test failures (6 test files + 1 unhandled rejection). This is the last substantive work phase before gate verification (Phase 11).

Two distinct domains:
1. **Python F821** — mechanical import fixes following Phase 09 patterns
2. **Vitest** — NOT mechanical. Tests have semantically diverged from implementations. Requires test realignment to current canonical components.

</domain>

<decisions>
## Implementation Decisions

### F821 Fix Approach (carried from Phase 09)

- **D-01:** Use `try/except ImportError` with `*_AVAILABLE` boolean flag for optional third-party dependencies (Phase 09 D-01)
- **D-02:** ALL cross-module types imported from their canonical implementation location — no local stubs, no placeholder definitions (Phase 09 D-08)
- **D-03:** Minimal signature changes for non-mechanical errors; do NOT refactor structure (Phase 09 D-05/D-06)

### F821 File-Specific Decisions

- **D-04:** `src/alternative_data/_news_sentiment_service_helper.py` — import `NewsArticle` from its canonical definition. Used only in type annotations (`List["NewsArticle"]`).
- **D-05:** `src/alternative_data/news_sentiment_analyzer.py` — conditional `import torch` with `TORCH_AVAILABLE` flag (Phase 09 D-01 pattern). `torch` used at lines 404, 406 inside method body.
- **D-06:** `src/core/data_source/config_manager.py` — add `import yaml` at module level. Standard third-party import, not optional.
- **D-07:** `src/database/service/adapter_queries.py:384` — import `DatabaseService` from its canonical location. Used at module level for global singleton `db_service = DatabaseService()`.
- **D-08:** `src/storage/database/database_manager/database_table_manager_methods/close_all_connections.py` — import `DatabaseType` from canonical enum location. Used in 3 methods (`get_tdengine_connection`, `get_postgresql_connection`, `get_tdx_connection`).
- **D-09:** `src/governance/risk_management/services/alert_rule_engine.py:515,529` — **bug fix, not import.** Remove `f` prefix from f-strings. `threshold` is a template placeholder (see `"value": "{threshold}"` on adjacent lines), not a runtime variable. Change `f"VaR超过 {threshold}%"` → `"VaR超过 {threshold}%"`.

### Vitest Strategy

- **D-10:** Full test realignment — rewrite stale tests to match current canonical component implementations. NOT just mock patching.
- **D-11:** Chart test fixes are mechanical path updates: `src/components/Charts/` → `src/components/charts/` (from v1.0 case-conflict merge).
- **D-12:** ArtDeco system-tab tests require **semantic rewrite**, not mock fixes:
  - `ArtDecoSystemSettings.vue` is now a 235-byte thin wrapper re-exporting `@/views/system/Settings.vue`
  - `ArtDecoDataManagement.vue` is a thin wrapper re-exporting `@/views/system/DataSource.vue`
  - Tests must target the actual canonical components' APIs and rendered output
- **D-13:** Delete stale `ArtDecoDataManagementVm` interface (`toggleConfig`/`saveConfig` methods no longer exist)
- **D-14:** Add mock for `monitoringApi.getSystemGeneralSettings` — called by `Settings.vue:180` but currently unmocked (causes unhandled rejection)

### Plan Structure

- **D-15:** Three plans:
  - Plan 01: Python F821 clearance (11 errors, 6 files)
  - Plan 02: Chart config test path fixes (4 test files)
  - Plan 03: System settings/DataManagement test realignment (2 test files + unhandled error)

### Claude's Discretion

- Exact import ordering within groups
- Canonical source locations for `NewsArticle`, `DatabaseService`, `DatabaseType`
- Chart test: whether to update test paths or verify files exist at new locations first
- Per-file verification sequence

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 09 import patterns (mandatory reference)
- `.planning/phases/09-analysis-monitoring-gpu-f821/09-CONTEXT.md` — conditional import pattern (`*_AVAILABLE`), cross-module type import rules, minimal-change approach

### F821 target files
- `src/alternative_data/_news_sentiment_service_helper.py` — 2x `NewsArticle` undefined
- `src/alternative_data/news_sentiment_analyzer.py` — 2x `torch` undefined
- `src/core/data_source/config_manager.py` — 1x `yaml` undefined
- `src/database/service/adapter_queries.py` — 1x `DatabaseService` undefined
- `src/governance/risk_management/services/alert_rule_engine.py` — 2x `threshold` f-string bug
- `src/storage/database/database_manager/database_table_manager_methods/close_all_connections.py` — 3x `DatabaseType` undefined

### Vitest — wrapper component chain
- `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` — thin wrapper → `@/views/system/Settings.vue`
- `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue` — thin wrapper → `@/views/system/DataSource.vue`
- `web/frontend/src/views/system/Settings.vue` — canonical implementation, line 180 calls `monitoringApi.getSystemGeneralSettings`

### Vitest — failing test files
- `web/frontend/tests/unit/config/chart-component-style-normalization.spec.ts` — stale `Charts/` paths
- `web/frontend/tests/unit/config/chart-style-sources.spec.ts` — stale `Charts/` paths
- `web/frontend/tests/unit/config/charts-use-pro-kline-chart-types-cleanup.spec.ts` — stale `Charts/` paths
- `web/frontend/tests/unit/config/indicator-selector-types-cleanup.spec.ts` — stale `Charts/` paths
- `web/frontend/src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` — needs semantic rewrite
- `web/frontend/src/views/artdeco-pages/system-tabs/__tests__/ArtDecoDataManagement.spec.ts` — needs semantic rewrite

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 09's conditional import pattern — directly reusable for `torch` import
- `src/advanced_analysis/anomaly/dataclasses.py` — canonical example of `GPU_AVAILABLE`/`TORCH_AVAILABLE` pattern

### Established Patterns
- Wrapper components: ArtDeco pages re-export canonical `@/views/system/` implementations
- Chart component paths: lowercase `charts/` is canonical (v1.0 merged from `Charts/`)

### Integration Points
- `Settings.vue:180` calls `monitoringApi.getSystemGeneralSettings()` — must be mocked in tests
- `DataSource.vue` — canonical data management component (replaces old ArtDecoDataManagement logic)

</code_context>

<specifics>
## Specific Ideas

- `threshold` in `alert_rule_engine.py` is definitively a template placeholder — the adjacent `"value": "{threshold}"` confirms it's not a runtime variable
- Chart test path fix is purely `Charts/` → `charts/` (verified by ENOENT errors)
- ArtDecoDataManagement test's `vm.toggleConfig(0)` is dead — method never existed on `DataSource.vue`

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 10-remaining-f821-vitest-fixes*
*Context gathered: 2026-04-10*
