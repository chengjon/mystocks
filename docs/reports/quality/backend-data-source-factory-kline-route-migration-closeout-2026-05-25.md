# Backend DataSourceFactory Kline Route Migration Closeout - 2026-05-25

Workline: G2.73 closeout / current-head refresh

Current HEAD: `6ece7f1367d3e4c1fcd881bc5596ec37942c79e4`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This closeout records current-head evidence for the merged G2.73
kline DataSourceFactory route migration. It does not authorize backend source
edits, test edits, route path changes, OpenAPI exposure changes, response shape
changes, frontend edits, PM2/runtime operations, OpenSpec proposal publication,
issue-label changes, compatibility getter deletion, or next-consumer selection.

## Status

Ready for review.

PR `#223` has been merged at
`6ece7f1367d3e4c1fcd881bc5596ec37942c79e4`. This closeout confirms the G2.73
kline route migration remains valid on current HEAD.

## Current-Head Verification

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | 118 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | 4 passed |
| `ruff check web/backend/app/api/data/kline.py web/backend/tests/test_health_route_conflicts.py` | passed |
| `black --check web/backend/app/api/data/kline.py web/backend/tests/test_health_route_conflicts.py` | passed |
| OpenAPI smoke with `PYTHONPATH=web/backend` and root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |

Route/API direct factory refs:

| Metric | Current HEAD |
| --- | ---: |
| Total direct route/API `get_data_source_factory()` refs | 4 |
| `web/backend/app/api/data/kline.py` direct refs | 0 |

Remaining direct route/API refs:

- `web/backend/app/api/data/stocks.py:269`
- `web/backend/app/api/data/stocks.py:371`
- `web/backend/app/api/data/futures.py:91`
- `web/backend/app/api/data/futures.py:114`

## GitNexus

`web/backend/app/api/data/kline.py`: LOW/1, 0 affected processes.

## Decision

G2.73 implementation evidence remains valid at current HEAD. No additional
source change is authorized by this closeout.

## Next Gate

Human review / PR merge decision for this closeout. If accepted, create the next
candidate authorization packet before any further DataSourceFactory route
migration. `stocks.py` and `futures.py` remain locked until then.
