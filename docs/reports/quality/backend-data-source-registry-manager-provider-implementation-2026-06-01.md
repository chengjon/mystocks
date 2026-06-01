# Backend Data Source Registry Manager Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: `G2.291`
- Status: review input for future PR `#444`
- Prepared at: `2026-06-01T11:08:00+08:00`
- Base HEAD: `e517163385e96a6c7115e14b77fb89819b4cead4`
- Parent: G2.290 provider authorization, PR `#443` merged at `e517163385e96a6c7115e14b77fb89819b4cead4`

Boundary note: this report records a path-limited backend source implementation
for review. It does not authorize auto-merge. Future PR `#444` must stop for
human review because it changes backend source/tests and the target has
GitNexus MEDIUM impact with one affected process.

## Scope

Allowed implementation paths:

- `web/backend/app/api/data_source_registry.py`
- `web/backend/tests/test_data_source_registry_manager_provider.py`
- `tests/unit/test_data_source_metrics_integration.py`

Allowed governance paths:

- `.planning/codebase/generated/data-source-registry-manager-provider-implementation-2026-06-01.json`
- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/steward-tree/evidence-index.md`
- `.planning/codebase/steward-tree/completed-ledger.md`
- `.planning/codebase/steward-tree/branch-register.md`
- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/steward-index.json`
- `docs/reports/quality/backend-data-source-registry-manager-provider-implementation-2026-06-01.md`
- `governance/mainline/task-cards/pr-444.yaml`

Forbidden scope:

- `web/backend/app/api/data_source_config.py`
- `src/core/data_source/**`
- `src/core/data_source_manager_v2.py`
- `docs/api/**`
- `web/frontend/**`
- `config/**`
- `scripts/**`
- `openspec/changes/**`
- `openspec/specs/**`
- PM2 or runtime state

## Implementation Result

G2.291 implements the G2.290-approved route-local provider shape:

- Added `get_data_source_registry_manager()`.
- Kept `get_manager()` as the backing compatibility / monkeypatch seam.
- Preserved fresh `DataSourceManagerV2()` construction semantics through `get_manager()`.
- Moved the seven active data-source registry handlers to dependency parameters backed by `Depends(get_data_source_registry_manager)`.
- Added `_resolve_data_source_registry_manager()` to preserve direct unit-call compatibility when tests invoke route handlers without FastAPI injection.
- Kept route paths, methods, response models, response metadata, OpenAPI exposure, operation IDs, `UnifiedResponse`, and error contract behavior unchanged.

Target handler set:

- `search_data_sources`
- `get_category_stats`
- `get_data_source`
- `update_data_source`
- `test_data_source`
- `health_check_data_source`
- `health_check_all_data_sources`

Post-implementation counts:

- Direct route-body `get_manager()` calls: `0`
- Provider backing `get_manager()` calls: `1`
- `Depends(get_data_source_registry_manager)` bindings: `7`
- Runtime routes: `548`
- OpenAPI paths: `500`
- Duplicate operation IDs: `0`
- Data-source runtime routes: `16`

## Test Notes

TDD evidence:

- Red: `web/backend/tests/test_data_source_registry_manager_provider.py` failed with `3` expected failures before implementation.
- Green: the same test file passed with `3 passed` after implementation.

Focused verification:

- `web/backend/tests/test_data_source_registry_manager_provider.py`
- `tests/api/file_tests/test_data_source_registry_api.py`
- `web/backend/tests/test_data_source_registry_error_contract.py`
- `web/backend/tests/test_data_source_auth_hardening.py`
- `tests/unit/test_data_source_metrics_integration.py`

Result: `34 passed in 11.95s`.

During focused verification, `tests/unit/test_data_source_metrics_integration.py`
was corrected inside the authorized test scope:

- use canonical `app.core.middleware.performance` imports instead of the
  parallel `web.backend.app...` import path, avoiding duplicate Prometheus
  metric registration in combined runs;
- assert the canonical `UnifiedResponse.data` model shape for the manual
  data-source test route.

## GitNexus

GitNexus MCP status:

- `context`: `Transport closed`
- `impact`: `Transport closed`

CLI fallback:

- Target: `Function:web/backend/app/api/data_source_registry.py:get_manager`
- Risk: `MEDIUM`
- Impacted symbols: `7`
- Direct callers: `7`
- Affected processes: `1`
- Affected modules: `1`
- Index status: stale warning

This confirms the source implementation PR must stop for human review.

## Verification

- `ruff check web/backend/app/api/data_source_registry.py web/backend/tests/test_data_source_registry_manager_provider.py tests/unit/test_data_source_metrics_integration.py`: all checks passed.
- Focused pytest command: `34 passed`.
- Route/OpenAPI smoke: `548` routes, `500` OpenAPI paths, duplicate operation IDs `0`, data-source runtime routes `16`.
- `openspec validate migrate-backend-singletons-to-lifecycle-di --strict`: valid; PostHog telemetry noise only.
- `git diff --check`: passed.

## Next Gate

If future PR `#444` is accepted and merged, start G2.292 as a no-source
provider closeout / residual refresh. G2.292 should confirm this lane is closed,
refresh remaining candidates, and select the next target without editing source.
