# Backend DataSourceFactory Kline Route Migration Implementation - 2026-05-25

Workline: G2.73 implementation packet

Base HEAD: `68ff82a9257fb7bee7bbb7aefe4c7a82c4cb76af`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This implementation follows the G2.72 authorization packet and
changes only `web/backend/app/api/data/kline.py`, the focused route dependency
test, and governance evidence files. It does not change route paths, response
models, response shapes, OpenAPI exposure policy, frontend code, runtime/PM2
state, OpenSpec state, issue labels, or DataSourceFactory compatibility getter
surfaces.

## Status

Ready for review.

PR `#222` merged the G2.72 authorization packet at
`68ff82a9257fb7bee7bbb7aefe4c7a82c4cb76af`, selecting
`web/backend/app/api/data/kline.py` for this path-limited implementation.

## Pre-Edit Evidence

| Target | Result |
| --- | --- |
| `web/backend/app/api/data/kline.py` | GitNexus LOW/1, 0 affected processes |
| `get_intraday_data` | GitNexus LOW/0 |
| `get_daily_kline` | Name ambiguous in GitNexus impact; path-specific context/cypher reported one in-file caller, `get_kline`, and no affected execution processes |

Baseline verification from G2.72:

| Check | Result |
| --- | --- |
| `web/backend/tests/test_health_route_conflicts.py` | 117 passed |
| `web/backend/tests/test_data_source_factory_lifecycle_di.py` | 4 passed |
| Route/API direct `await get_data_source_factory()` refs | total `6`, `kline.py` `2` |
| OpenAPI smoke | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |

## TDD Evidence

Red test:

```text
pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_kline_routes_use_data_source_factory_dependency -q --no-cov --tb=short
```

Result: failed as expected with `KeyError: 'factory'`.

Green test:

```text
pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_kline_routes_use_data_source_factory_dependency -q --no-cov --tb=short
```

Result: `1 passed`.

## Implementation

Changed `web/backend/app/api/data/kline.py`:

- Added `DataSourceFactory` and `get_data_source_factory_dependency` import.
- Migrated `get_daily_kline` from route-local `await get_data_source_factory()`
  to `factory: DataSourceFactory = Depends(get_data_source_factory_dependency)`.
- Migrated `get_kline` to accept the same dependency and pass the factory into
  `get_daily_kline`.
- Migrated `get_intraday_data` from route-local `await get_data_source_factory()`
  to the same dependency.
- Normalized same-file `E701` and black formatting debt in `kline.py`, as
  explicitly allowed by G2.72.

Changed `web/backend/tests/test_health_route_conflicts.py`:

- Added `test_kline_routes_use_data_source_factory_dependency`.

## Verification

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_kline_routes_use_data_source_factory_dependency -q --no-cov --tb=short` | 1 passed |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | 118 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | 4 passed |
| `ruff check web/backend/app/api/data/kline.py web/backend/tests/test_health_route_conflicts.py` | passed |
| `black --check web/backend/app/api/data/kline.py web/backend/tests/test_health_route_conflicts.py` | passed |
| OpenAPI smoke with `PYTHONPATH=web/backend` and root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |
| staged GitNexus `detect_changes(scope=staged)` | low risk, 26 changed symbols, 0 affected processes |

Route/API direct factory refs:

| Metric | Before | After |
| --- | ---: | ---: |
| Total direct route/API `get_data_source_factory()` refs | 6 | 4 |
| `web/backend/app/api/data/kline.py` direct refs | 2 | 0 |

Remaining route consumers stay locked for future authorization:

- `web/backend/app/api/data/stocks.py`
- `web/backend/app/api/data/futures.py`

GitNexus reports 26 changed symbols because black normalization and the shared
test file cause broad same-file symbol attribution. The staged risk level is
`low`, and no affected execution processes are reported.

## Boundary

This PR does not authorize:

- route path changes
- response model or response shape changes
- OpenAPI exposure changes
- frontend edits
- runtime/PM2 operations
- OpenSpec changes
- issue-label changes
- DataSourceFactory compatibility getter deletion
- `stocks.py` or `futures.py` migration
- formatting outside `kline.py` and the focused test file

## Next Gate

Human review / PR merge decision for G2.73. If accepted, create a closeout /
current-head refresh before selecting another DataSourceFactory route consumer.
