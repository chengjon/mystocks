# Backend DataSourceFactory Stocks Route Migration Closeout - 2026-05-25

Workline: G2.75 closeout / current-head refresh

Current HEAD: `02518742fb1169ced7f2aa34daaff0dc9dc8b47b`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This closeout records current-head evidence for the merged G2.75
stocks DataSourceFactory route migration. It does not authorize backend source
edits, test edits, route path changes, OpenAPI exposure changes, response shape
changes, frontend edits, PM2/runtime operations, OpenSpec proposal publication,
issue-label changes, compatibility getter deletion, or the remaining `futures.py`
migration.

## Status

Ready for review.

PR `#226` has been merged at
`02518742fb1169ced7f2aa34daaff0dc9dc8b47b`. This closeout confirms the G2.75
stocks route migration remains valid on current HEAD.

## Current-Head Verification

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | 119 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | 4 passed |
| `ruff check web/backend/app/api/data/stocks.py web/backend/tests/test_health_route_conflicts.py` | passed |
| `black --check web/backend/app/api/data/stocks.py web/backend/tests/test_health_route_conflicts.py` | passed |
| OpenAPI smoke with `PYTHONPATH=web/backend` and root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |

The OpenAPI import captured 121 generic Python warnings, all sampled warnings
were existing datetime or Pydantic deprecation warnings. Duplicate operation ID
warnings remain 0.

Route/API direct factory refs:

| Metric | Current HEAD |
| --- | ---: |
| Total direct route/API `get_data_source_factory()` refs | 2 |
| `web/backend/app/api/data/stocks.py` direct refs | 0 |

Remaining direct route/API refs:

- `web/backend/app/api/data/futures.py:91`
- `web/backend/app/api/data/futures.py:114`

## GitHub And GitNexus

PR `#226` reached CLEAN before merge: 9 checks succeeded and 4 were skipped.

PR `#226` staged GitNexus detect_changes reported LOW risk, 30 changed symbols,
and 0 affected processes. No new GitNexus source-edit gate is required by this
docs/governance-only closeout.

## Decision

G2.75 implementation evidence remains valid at current HEAD. No additional
source change is authorized by this closeout.

## Next Gate

Human review / PR merge decision for this closeout. If accepted, prepare a
`futures.py` risk packet before any remaining DataSourceFactory route/API
migration. The remaining `futures.py` direct refs stay locked until that packet
is reviewed and accepted.
