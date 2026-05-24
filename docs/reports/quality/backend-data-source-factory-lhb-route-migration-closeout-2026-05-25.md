# Backend DataSourceFactory LHB Route Migration Closeout - 2026-05-25

Workline: G2.69 closeout / current-head refresh

Current HEAD: `d25803e93494b7115795a1922a84386b9daffb27`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This document records a closeout/current-head refresh for one
already merged source implementation. It does not authorize backend source
edits, route path changes, OpenAPI exposure changes, response shape changes,
frontend edits, PM2/runtime operations, OpenSpec proposal publication,
issue-label changes, or migration of any other DataSourceFactory route
consumer.

## Status

Ready for review.

PR `#217` has been merged at
`d25803e93494b7115795a1922a84386b9daffb27`. This closeout confirms the
G2.69 LHB route migration remains valid on current HEAD and records the next
gate.

## Current-Head Verification

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov` | 116 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov` | 4 passed |
| `ruff check web/backend/app/api/data/lhb.py web/backend/tests/test_health_route_conflicts.py` | passed |
| `black --check web/backend/app/api/data/lhb.py web/backend/tests/test_health_route_conflicts.py` | passed |
| OpenAPI smoke with `PYTHONPATH=web/backend` and root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |

Route/API direct factory refs:

| Metric | Current HEAD |
| --- | ---: |
| Total direct route/API `get_data_source_factory()` refs | 8 |
| `web/backend/app/api/data/lhb.py` direct refs | 0 |

Remaining data route consumers:

- `web/backend/app/api/data/kline.py` — 2 direct refs
- `web/backend/app/api/data/futures.py` — 2 direct refs
- `web/backend/app/api/data/stocks.py` — 2 direct refs

## GitNexus

| Target | Result |
| --- | --- |
| `web/backend/app/api/data/lhb.py` | LOW risk, 1 direct import impact, 0 affected processes |
| `web/backend/app/services/data_source_factory` | package target lookup not indexed in this check |

The provider package lookup miss is recorded as tool/indexing scope, not as a
code contradiction. The closeout does not depend on changing provider package
code.

## Decision

G2.69 implementation evidence remains valid at current HEAD. No additional
source change is authorized by this closeout.

## Next Gate

Human review / PR merge decision for this closeout. If accepted, create a
separate G2.70 candidate authorization packet before any further
DataSourceFactory route migration. Remaining candidates stay locked until that
authorization packet is reviewed.
