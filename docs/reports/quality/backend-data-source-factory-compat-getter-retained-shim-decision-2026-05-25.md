# Backend DataSourceFactory Compatibility Getter Retained-Shim Decision - 2026-05-25

Workline: G2.79 decision-only compatibility API governance

Current HEAD: `b3aefed2648a3ec19dede187e4ca04a096dd0a7c`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This decision packet records the current status of the
`get_data_source_factory()` compatibility getter after the G2.78 futures route
migration. It does not authorize backend source edits, test edits, route path
changes, OpenAPI exposure changes, response shape changes, frontend edits,
PM2/runtime operations, OpenSpec proposal publication, issue-label changes,
compatibility getter deletion, package export removal, or retained-shim
retirement.

## Status

Ready for review.

## Decision

Retain `get_data_source_factory()` as a compatibility shim for now.

The route/API direct consumer migration is closed: current textual scan reports
0 direct `get_data_source_factory()` calls under `web/backend/app/api`. That is
not the same as deletion readiness. The function remains package-exported and is
still used by service-internal convenience helpers and the dependency fallback
path in `web/backend/app/services/data_source_factory/data_source_factory.py`.

## Evidence

| Metric | Current HEAD |
| --- | ---: |
| Route/API direct `get_data_source_factory()` calls | 0 |
| Exact Python `get_data_source_factory()` parenthesized refs | 10 |
| Function definitions | 1 |
| Package export lines | 2 |
| Service-internal parenthesized refs | 6 |

Key locations:

| Location | Role |
| --- | --- |
| `web/backend/app/services/data_source_factory/data_source_factory.py:300` | compatibility getter definition |
| `web/backend/app/services/data_source_factory/data_source_factory.py:310` | dependency fallback uses the getter when app state has no factory |
| `web/backend/app/services/data_source_factory/data_source_factory.py:324` | `get_data_source` convenience helper fallback |
| `web/backend/app/services/data_source_factory/data_source_factory.py:330` | `get_market_data` convenience helper fallback |
| `web/backend/app/services/data_source_factory/data_source_factory.py:336` | `get_dashboard_data` convenience helper fallback |
| `web/backend/app/services/data_source_factory/data_source_factory.py:342` | `get_technical_analysis_data` convenience helper fallback |
| `web/backend/app/services/data_source_factory/__init__.py:12` | package re-export |
| `web/backend/app/services/data_source_factory/__init__.py:31` | package `__all__` export |
| `web/backend/tests/test_data_source_factory_lifecycle_di.py:70` | explicit compatibility getter test |

GitNexus impact against the current index reports CRITICAL risk, 22 impacted
symbols, 21 direct dependents, and 12 affected processes. The graph still lists
historical route handlers that textual current-head scans show as migrated, so
the impact result should be treated as a high-risk/stale-index warning and not
as deletion authorization.

## Verification

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov` | 4 passed |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov` | 120 passed |
| OpenAPI smoke with `PYTHONPATH=web/backend` and root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |

The OpenAPI import captured 121 generic Python warnings. Duplicate operation ID
warnings remain 0.

## Required Preconditions Before Any Future Retirement

Any future removal or export retirement needs a separate authorization packet
and must include:

1. Fresh GitNexus reanalysis or an explicit stale-index waiver.
2. Current textual scan confirming route/API direct calls remain 0.
3. A service-internal helper migration plan for `get_data_source`,
   `get_market_data`, `get_dashboard_data`, and
   `get_technical_analysis_data`.
4. A package export compatibility decision for
   `web/backend/app/services/data_source_factory/__init__.py`.
5. TDD red/green coverage proving external compatibility behavior is either
   preserved or intentionally retired.
6. OpenAPI smoke and route-conflict regression checks after implementation.

## Next Gate

Human review / PR merge decision for this retained-shim decision packet. If
accepted, the next source-capable step must be a separate retirement
authorization packet; this packet itself keeps the compatibility getter in
place.
