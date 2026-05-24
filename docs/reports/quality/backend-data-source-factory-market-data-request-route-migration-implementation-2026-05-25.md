# Backend DataSourceFactory Market Data Request Route Migration Implementation - 2026-05-25

Workline: G2.71 implementation packet

Current HEAD: `9060b455b7559ce21bc6f27975cce058be52cb96`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This document records one path-limited source implementation and
its evidence. It does not authorize route path changes, OpenAPI exposure
changes, response shape changes, frontend edits, PM2/runtime operations,
OpenSpec proposal publication, issue-label changes, or migration of any other
DataSourceFactory route consumer.

## Status

Ready for review.

This is the G2.71 implementation packet authorized by the G2.70
`market_data_request.py` candidate selection.

## Pre-Edit Evidence

| Target | Result |
| --- | --- |
| `web/backend/app/api/market/market_data_request.py` | GitNexus LOW/1, 0 affected processes |
| `get_market_quotes` | GitNexus LOW/0 |
| `get_fund_flow` | Name ambiguous in GitNexus impact; path-specific context reported no incoming refs |

Baseline verification:

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov` | 116 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov` | 4 passed |
| `ruff check web/backend/app/api/market/market_data_request.py` | passed |
| `black --check web/backend/app/api/market/market_data_request.py` | passed |

## TDD Evidence

Red test:

```text
pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_market_data_request_routes_use_data_source_factory_dependency -q --no-cov --tb=short
```

Result: failed as expected with `KeyError: 'factory'`.

Green test:

```text
pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_market_data_request_routes_use_data_source_factory_dependency -q --no-cov --tb=short
```

Result: `1 passed`.

## Implementation

Migrated route handlers:

- `get_fund_flow`
- `get_market_quotes`

Both handlers now receive:

```python
factory: DataSourceFactory = Depends(get_data_source_factory_dependency)
```

The route-local `from app.services.data_source_factory import get_data_source_factory`
imports and `await get_data_source_factory()` calls were removed from both
handlers. Compatibility surfaces remain intact:

- `get_data_source_factory()`
- `_global_factory`
- `get_data_source_factory_dependency`

## Verification

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov` | 117 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov` | 4 passed |
| `ruff check web/backend/app/api/market/market_data_request.py web/backend/tests/test_health_route_conflicts.py` | passed |
| `black --check web/backend/app/api/market/market_data_request.py web/backend/tests/test_health_route_conflicts.py` | passed |
| OpenAPI smoke with `PYTHONPATH=web/backend` and root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |
| staged GitNexus `detect_changes(scope=staged)` | HIGH, 36 changed symbols, 6 affected processes |

Route/API direct factory refs:

| Metric | Before | After |
| --- | ---: | ---: |
| Total direct route/API `get_data_source_factory()` refs | 8 | 6 |
| `web/backend/app/api/market/market_data_request.py` direct refs | 2 | 0 |

Remaining route consumers stay locked for future authorization:

- `web/backend/app/api/data/kline.py`
- `web/backend/app/api/data/futures.py`
- `web/backend/app/api/data/stocks.py`

Staged GitNexus reports HIGH because the parser attributed the
`market_data_request.py` file edit broadly and listed same-file functions plus
`get_kline_data` processes as changed. The reviewed staged diff is limited to
one import, the `get_fund_flow` and `get_market_quotes` dependency parameters,
removal of their two route-local getter calls, and one focused test. There is
no `get_kline_data` hunk in `git diff --cached`.

## Boundary

This packet does not authorize:

- route path, response model, response shape, or OpenAPI exposure changes
- frontend edits
- runtime/PM2 stateful gates
- OpenSpec changes
- issue label changes
- `get_data_source_factory()` or `_global_factory` deletion
- migration of `kline.py`, `futures.py`, `stocks.py`, or any other consumer

## Next Gate

Human review / PR merge decision for G2.71. After merge, create a separate
closeout/current-head refresh before any additional DataSourceFactory route
migration.
