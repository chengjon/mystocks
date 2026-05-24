# Backend DataSourceFactory Market Data Request Route Migration Closeout - 2026-05-25

Workline: G2.71 closeout / current-head refresh

Current HEAD: `7f10db172b99b0d9d85fc740ffb00fa535bd4071`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This document records a closeout/current-head refresh for one
already merged source implementation. It does not authorize backend source
edits, route path changes, OpenAPI exposure changes, response shape changes,
frontend edits, PM2/runtime operations, OpenSpec proposal publication,
issue-label changes, or migration of any other DataSourceFactory route
consumer.

## Status

Ready for review.

PR `#220` has been merged at
`7f10db172b99b0d9d85fc740ffb00fa535bd4071`. This closeout confirms the G2.71
market data request route migration remains valid on current HEAD.

## Current-Head Verification

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov` | 117 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov` | 4 passed |
| `ruff check web/backend/app/api/market/market_data_request.py web/backend/tests/test_health_route_conflicts.py` | passed |
| `black --check web/backend/app/api/market/market_data_request.py web/backend/tests/test_health_route_conflicts.py` | passed |
| OpenAPI smoke with `PYTHONPATH=web/backend` and root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |

Route/API direct factory refs:

| Metric | Current HEAD |
| --- | ---: |
| Total direct route/API `get_data_source_factory()` refs | 6 |
| `web/backend/app/api/market/market_data_request.py` direct refs | 0 |

Remaining consumers:

- `web/backend/app/api/data/kline.py` — 2 direct refs
- `web/backend/app/api/data/futures.py` — 2 direct refs
- `web/backend/app/api/data/stocks.py` — 2 direct refs

## GitNexus

| Target | Result |
| --- | --- |
| `web/backend/app/api/market/market_data_request.py` | LOW risk, 1 direct import impact, 0 affected processes |

## Decision

G2.71 implementation evidence remains valid at current HEAD. No additional
source change is authorized by this closeout.

## Next Gate

Human review / PR merge decision for this closeout. If accepted, create a
separate candidate authorization packet before any further DataSourceFactory
route migration. The remaining consumers stay locked until that packet is
reviewed.
