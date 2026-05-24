# Backend DataSourceFactory Margin Route Migration Closeout - 2026-05-25

Workline: G2.67 closeout/current-head refresh

Current HEAD: `3f1a737a5cc62f0424951931581e410d1dd14975`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This document records closeout evidence only. It does not
authorize source code changes, route/OpenAPI changes, frontend changes,
runtime/PM2 operations, OpenSpec publication, issue-label changes, or selection
of the next DataSourceFactory route consumer without a separate authorization
packet.

## Merged Implementation

PR `#214` merged G2.67 at
`3f1a737a5cc62f0424951931581e410d1dd14975`.

Merged result:

- `get_margin_account_info`
- `get_margin_detail_sse`
- `get_margin_detail_szse`

now receive `DataSourceFactory` through
`Depends(get_data_source_factory_dependency)`.

## Current-Head Verification

- `web/backend/tests/test_health_route_conflicts.py`: `115 passed`
- `web/backend/tests/test_data_source_factory_lifecycle_di.py`: `4 passed`
- `ruff check` touched files: passed
- `black --check` touched files: `3 files would be left unchanged`
- route guard:
  - total route/API direct factory refs=`10`
  - `margin.py` direct factory refs=`0`
  - provider dependency refs=`8`
- OpenAPI smoke:
  - routes=`548`
  - paths=`500`
  - operation IDs=`536`
  - duplicate operation IDs=`0`
  - duplicate operation ID warnings=`0`
  - warning count=`121`
- GitNexus:
  - `margin.py` upstream impact=`LOW/1`
  - `web/backend/app/services/data_source_factory/__init__.py` upstream impact=`LOW/0`

GitNexus note: `get_data_source_factory_dependency` was not directly addressable
by current symbol lookup in this closeout pass, so the package file impact was
used as the provider-side closeout check.

Environment note: OpenAPI smoke used explicit non-secret test environment
placeholders because the isolated worktree has no `.env` file.

## Remaining Route Consumers

Remaining direct route/API factory refs: `10`.

Remaining locked candidates:

- `web/backend/app/api/data/kline.py`
- `web/backend/app/api/data/futures.py`
- `web/backend/app/api/data/lhb.py`
- `web/backend/app/api/data/stocks.py`
- `web/backend/app/api/market/market_data_request.py`

## Next Gate

Create a separate G2.68 authorization-only candidate comparison packet before
any next DataSourceFactory route consumer edit. This closeout does not select or
authorize the next source file.
