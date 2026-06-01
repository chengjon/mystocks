# Backend Indicator Registry Factory Ownership Decision - G2.313

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review
- Prepared at: `2026-06-02T01:35:43+08:00`
- Base HEAD checked: `ac6b9faaf9cf7d2e04b29da08a2c28bce7d4fb18`
- Parent gate: G2.312 accepted / merged by PR `#465`
- Target: `web/backend/app/api/indicator_registry.py:get_factory`
- Source edit authority: none

Boundary note: this G2.313 package is no-source governance only. It does not authorize backend source edits, tests, route registration changes, route/OpenAPI contract edits, docs/api artifacts, frontend/config/script changes, PM2 commands, OpenSpec spec edits, or source retirement.

## Decision

`indicator_registry.py:get_factory` is an active route-local singleton factory helper. It is not dormant like `create_indicator_config.py:get_mysql_session`: the owning module is registered in FastAPI and exposed in OpenAPI.

G2.313 does not authorize implementation. The next allowed step is G2.314, a no-source provider authorization package for this exact route-local factory seam. If G2.314 is accepted, any future source implementation lane must stop at human review before merge.

## Evidence Snapshot

| Item | Value |
|---|---|
| Target file | `web/backend/app/api/indicator_registry.py` |
| Target symbol | `get_factory` at line 99 |
| Backing global | `_factory` |
| Factory class | `IndicatorFactory` |
| Direct route-body calls | 3 |
| Direct call lines | 159, 186, 201 |
| FastAPI route count | 548 |
| OpenAPI path count | 500 |
| Duplicate operation ID warnings | 0 |
| GitNexus CLI risk | LOW |
| GitNexus direct callers | 3 |
| GitNexus affected processes | 0 |

## Registered Route Surface

| Method | Path | Endpoint | Direct factory call |
|---|---|---|---|
| GET | `/api/indicator-registry/indicators` | `list_indicators` | line 159 |
| GET | `/api/indicator-registry/indicators/{indicator_id}` | `get_indicator_details` | line 186 |
| POST | `/api/indicator-registry/calculate` | `calculate_indicator` | line 201 |

## GitNexus Result

GitNexus MCP impact failed with `Transport closed`, so this package records the CLI fallback:

- Command: `npx gitnexus impact get_factory -r mystocks --direction upstream --summary-only`
- Target: `Function:web/backend/app/api/indicator_registry.py:get_factory`
- Risk: `LOW`
- Direct callers: `3`
- Affected processes: `0`
- Affected modules: `Api`
- Index state: stale index warning, `commits_behind=0`

## Test Inventory

No tests are edited by this package. Relevant test references for a future authorization package are:

- `web/backend/tests/test_data_quality_mock_configuration.py`
- `web/backend/tests/test_health_route_conflicts.py`
- `web/backend/tests/test_indicator_registry_v1.py`
- `web/backend/tests/test_indicators.py`
- `web/backend/tests/test_indicator_registry_route_provider.py`
- `web/backend/tests/unit/services/indicators/test_dependency.py`
- `web/backend/tests/unit/services/indicators/test_indicator_registry.py`
- `tests/file_level/core.py`
- `tests/api/test_indicator_registry_file.py`
- `tests/ai/test_data_analyzer/pattern_recognizer.py`
- `tests/api/file_tests/test_indicator_registry_api.py`
- `tests/api/file_tests/test_indicators_api.py`

`web/backend/tests/test_indicator_registry_route_provider.py` is a useful provider-governance precedent, but it covers `app.api.indicators.indicator_cache` and `app.services.indicator_registry`, not `app.api.indicator_registry.py:get_factory` directly.

## Authorization Boundary

G2.313 permits only this decision record and steward-tree updates. It does not permit:

- editing `web/backend/app/api/indicator_registry.py`
- adding or changing tests
- route registration changes
- OpenAPI artifact changes
- docs/api edits
- source retirement
- PM2 or runtime state changes

## Next Gate

Start G2.314 as a no-source `indicator_registry.get_factory` provider authorization package after PR `#466` is accepted / merged. G2.314 should define the exact implementation boundary, focused tests, rollback rule, and human-review stop rule for any future source PR.
