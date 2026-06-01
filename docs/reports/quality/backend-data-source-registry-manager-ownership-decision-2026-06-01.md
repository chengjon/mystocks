# Backend Data Source Registry Manager Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: G2.289
- Status: for review in future PR `#442`
- Prepared at: `2026-06-01T09:22:30+08:00`
- Base HEAD checked: `75ce550ceaf9f77b7659193b9cbd3c9ab2181c37`
- Parent gate: G2.288, PR `#441`, merged at `75ce550ceaf9f77b7659193b9cbd3c9ab2181c37`

Boundary note: G2.289 is a no-source ownership / route-provider decision package.
It does not authorize backend source edits, tests, route registration changes,
route/OpenAPI contract changes, docs/api artifacts, frontend, config, scripts,
OpenSpec changes, PM2 commands, runtime state changes, or source retirement.

## Current Surface

`web/backend/app/api/data_source_registry.py:get_manager` is currently a
module-local helper:

- definition: lines `61-65`
- current shape: returns a fresh `DataSourceManagerV2()` instance
- backing class: `src.core.data_source.base.DataSourceManagerV2`
- router prefix: `/api/v1/data-sources`
- active route-body direct calls: `7`
- current FastAPI `Depends(get_manager)` or explicit provider bindings: `0`

Active route-body consumers:

| Handler | Method | Path |
|---|---|---|
| `search_data_sources` | GET | `/api/v1/data-sources/` |
| `get_category_stats` | GET | `/api/v1/data-sources/categories` |
| `get_data_source` | GET | `/api/v1/data-sources/{endpoint_name}` |
| `update_data_source` | PUT | `/api/v1/data-sources/{endpoint_name}` |
| `test_data_source` | POST | `/api/v1/data-sources/{endpoint_name}/test` |
| `health_check_data_source` | POST | `/api/v1/data-sources/{endpoint_name}/health-check` |
| `health_check_all_data_sources` | POST | `/api/v1/data-sources/health-check/all` |

## Route / OpenAPI Evidence

Fresh app import and OpenAPI smoke with repo `.env` loaded into the subprocess
recorded:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- duplicate operation IDs: `0`
- `data_source_registry.py` runtime route count: `7`
- data-source registry paths remain present under `/api/v1/data-sources`
- sibling data-source config paths also remain present under `/api/v1/data-sources/config`

The environment values used for app import were not written to artifacts.

## GitNexus Evidence

GitNexus MCP remains unavailable for this session:

- `context`: `Transport closed`
- `impact`: `Transport closed`

CLI fallback evidence for
`Function:web/backend/app/api/data_source_registry.py:get_manager`:

- risk: `MEDIUM`
- impacted symbols: `7`
- direct callers: `7`
- affected processes: `1`
- affected modules: `1`
- affected process: `test_data_source`
- index status: stale warning

Because this target has MEDIUM impact and one affected process, this PR must
stop for human review under the limited autopilot rules.

## Consumer Contract Notes

Focused consumer/test surfaces observed:

- `tests/api/file_tests/test_data_source_registry_api.py`
- `web/backend/tests/test_data_source_registry_error_contract.py`
- `web/backend/tests/test_data_source_auth_hardening.py`
- `tests/unit/test_data_source_metrics_integration.py`
- `web/backend/tests/test_health_route_conflicts.py`
- `web/backend/tests/test_runtime_logging_wave2.py`

Existing tests patch the module-level `get_manager` helper directly in at least
two places, so a future implementation must preserve the monkeypatch seam unless
a separate compatibility-retirement gate explicitly changes that contract.

`DataSourceManagerV2` loads database/YAML-backed registry data and currently
keeps synchronous APIs. The first provider implementation must preserve
per-request construction semantics and must not introduce a process-level
singleton or async conversion as part of this route-provider lane.

## Decision

Classify `get_manager` as a bounded active data-source registry route helper
owned by `web/backend/app/api/data_source_registry.py`.

This is not:

- app-wide singleton lifecycle implementation
- shared service facade retirement
- route registration or OpenAPI exposure work
- data-source registry schema migration
- compatibility wrapper retirement

Recommended next gate after human acceptance:

- G2.290 no-source `data_source_registry.get_manager` provider authorization package

G2.289 must not be used as source implementation authorization. A later G2.290
authorization package should define the exact implementation envelope before any
source lane starts.

## Future Authorization Guardrails

If G2.289 is accepted, G2.290 should decide whether to authorize a path-limited
implementation with these constraints:

- keep `get_manager` as a compatibility/backing seam unless explicitly retired
- add or select an explicit route-local dependency provider for `DataSourceManagerV2`
- move only the seven active route handlers to dependency parameters
- preserve route paths, methods, response models, response metadata, OpenAPI exposure, auth behavior, `UnifiedResponse` behavior, and current error-contract shape
- preserve per-request construction semantics; do not introduce a process-level singleton
- do not edit `DataSourceManagerV2` internals, data-source config routes, docs/api artifacts, frontend, config, scripts, OpenSpec, PM2, or runtime state

Future tests should include a new focused provider regression plus the current
data-source registry API/error/auth/metrics surfaces listed above.

## Artifacts

- `.planning/codebase/generated/data-source-registry-manager-ownership-decision-2026-06-01.json`
- `docs/reports/quality/backend-data-source-registry-manager-ownership-decision-2026-06-01.md`
- `governance/mainline/task-cards/pr-442.yaml`
