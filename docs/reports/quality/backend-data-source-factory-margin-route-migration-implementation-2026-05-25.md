# Backend DataSourceFactory Margin Route Migration Implementation - 2026-05-25

Workline: G2.67 implementation packet

Current HEAD: `7b817debccfba1c82efc5a9c71f23f0b775434c0`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This document records one path-limited source implementation and
its evidence. It does not authorize route path changes, OpenAPI exposure
changes, response shape changes, frontend edits, PM2/runtime operations,
OpenSpec proposal publication, issue-label changes, or migration of any other
DataSourceFactory route consumer.

## Authorization

G2.66 selected `web/backend/app/api/data/margin.py` for this source packet after
PR `#213` merged at `7b817debccfba1c82efc5a9c71f23f0b775434c0`.

Allowed source scope:

- `web/backend/app/api/data/margin.py`
- `web/backend/tests/test_health_route_conflicts.py`

All other remaining DataSourceFactory route consumers stayed locked.

## Pre-Edit Gate

- `architecture/STANDARDS.md` relevant governance and migration sections were
  reviewed before source edits.
- GitNexus upstream impact for `web/backend/app/api/data/margin.py`:
  LOW, impacted count=`1`, direct=`1`, affected processes=`0`.
- GitNexus context was checked for:
  - `get_margin_account_info`
  - `get_margin_detail_sse`
  - `get_margin_detail_szse`
- All three route handlers had no incoming callers/processes and called
  `get_data_source_factory` before migration.

## TDD Evidence

Red:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_margin_routes_use_data_source_factory_dependency -q --no-cov --tb=short
1 failed
KeyError: 'factory'
```

Green:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_margin_routes_use_data_source_factory_dependency -q --no-cov --tb=short
1 passed
```

## Implementation

`web/backend/app/api/data/margin.py` now imports and uses:

- `DataSourceFactory`
- `get_data_source_factory_dependency`

The following handlers now receive `factory` via FastAPI `Depends`:

- `get_margin_account_info`
- `get_margin_detail_sse`
- `get_margin_detail_szse`

The function-local compatibility getter imports and awaits were removed from
those handlers. No route path, response model, response shape, OpenAPI exposure,
or compatibility getter definition was changed.

`web/backend/tests/test_health_route_conflicts.py` now imports `margin_module`
and asserts all three margin route handlers are wired to
`margin_module.get_data_source_factory_dependency`.

## Verification

- `web/backend/tests/test_health_route_conflicts.py`: `115 passed`
- `web/backend/tests/test_data_source_factory_lifecycle_di.py`: `4 passed`
- `ruff check` touched files: passed
- `black --check` touched files: `3 files would be left unchanged`
- `git diff --check`: no output
- Route guard:
  - total route/API direct factory refs: `13 -> 10`
  - `margin.py` direct factory refs: `3 -> 0`
  - provider dependency refs after migration: `8`
- OpenAPI smoke:
  - routes=`548`
  - paths=`500`
  - operation IDs=`536`
  - duplicate operation IDs=`0`
  - duplicate operation ID warnings=`0`
  - warning count=`121`
- GitNexus staged detect changes:
  - risk level=`low`
  - changed files=`6`
  - affected count=`0`
  - affected processes=`0`

Environment note: OpenAPI smoke used explicit non-secret test environment
placeholders because the isolated worktree has no `.env` file.

## Remaining Consumers

After this implementation, remaining direct route/API factory refs are `10`.
The still-locked candidates remain:

- `web/backend/app/api/data/kline.py`
- `web/backend/app/api/data/futures.py`
- `web/backend/app/api/data/lhb.py`
- `web/backend/app/api/data/stocks.py`
- `web/backend/app/api/market/market_data_request.py`

## Next Gate

Human review / PR merge decision. If accepted, run G2.67 closeout/current-head
refresh before selecting another DataSourceFactory route consumer.
