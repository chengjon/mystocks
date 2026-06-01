# Backend Indicator Config Router Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a no-source route ownership decision package. It
does not edit backend source, tests, route contracts, docs/api artifacts,
frontend, config, scripts, OpenSpec changes/specs, PM2, or runtime state.

Status: for review in future PR `#464`.

## Summary

G2.311 follows PR `#463`, which merged G2.310 at
`67083d40808fea9963137e3e128c0c6cb0683e57`.

G2.310 established that all five `get_mysql_session()` calls selected by G2.309
live in `web/backend/app/api/indicators/create_indicator_config.py`, but that
module's router is not registered in the FastAPI app or OpenAPI schema.

Decision: retain the module as dormant route code for now, exclude it from the
active service lifecycle provider implementation queue, and do not register or
retire it from this package.

## Runtime Route Truth

`create_indicator_config.py` defines handlers for:

- `POST /configs`
- `GET /configs`
- `GET /configs/{config_id}`
- `PUT /configs/{config_id}`
- `DELETE /configs/{config_id}`

However, the active package export `web/backend/app/api/indicators/__init__.py`
exports `router` from `indicator_cache.py`, and `router_registry.py` registers
that `indicators.router`. The configuration CRUD router is therefore not part
of the current runtime route table.

Fresh app route-table smoke with non-secret test environment values recorded:

| Metric | Result |
|---|---:|
| Total FastAPI routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| Indicator-related routes | `13` |
| Registered `create_indicator_config.py` handlers | `0` |
| OpenAPI `/configs` CRUD paths from this module | `0` |

## Test Inventory

| Path | Finding |
|---|---|
| `tests/api/file_tests/test_indicators_api.py` | Contains fixture-based endpoint expectation tests for `/configs`; it does not prove FastAPI registration |
| `tests/ddd/test_architecture_validation.py` | Exercises domain `IndicatorConfig`, not route registration |
| `web/backend/tests/unit/services/indicators/test_indicator_registry.py` | Exercises indicator registry and metadata, not `create_indicator_config.py` runtime routing |

## Decision

Classify `web/backend/app/api/indicators/create_indicator_config.py` as a
retained dormant indicator-config router surface.

For the service lifecycle/provider queue:

- `get_mysql_session()` in this module is closed as an active provider candidate.
- No provider implementation authorization should be opened from G2.311.
- Future scans should exclude this dormant route module unless route governance
  explicitly reopens it.

For route/OpenAPI governance:

- Do not register the router from this package.
- Do not retire or delete the module from this package.
- A future route registration or retirement lane must be a separate decision
  package and, if source-affecting, must stop at human review.

Recommended next gate: G2.312 no-source service lifecycle residual candidate
refresh after dormant indicator-config exclusion.
