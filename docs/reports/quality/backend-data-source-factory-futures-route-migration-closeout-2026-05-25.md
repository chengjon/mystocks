# Backend DataSourceFactory Futures Route Migration Closeout - 2026-05-25

Workline: G2.78 closeout / current-head refresh

Current HEAD: `e7a2a436b157dc32d5675e89e4f8c16505b07629`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This closeout records current-head evidence for the merged G2.78
futures DataSourceFactory route migration. It does not authorize backend source
edits, test edits, route path changes, OpenAPI exposure changes, response shape
changes, frontend edits, PM2/runtime operations, OpenSpec proposal publication,
issue-label changes, compatibility getter deletion, or retained-shim retirement.

## Status

Ready for review.

PR `#230` has been merged at
`e7a2a436b157dc32d5675e89e4f8c16505b07629`. This closeout confirms the G2.78
futures route migration remains valid on current HEAD.

## Current-Head Verification

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov` | 120 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov` | 4 passed |
| `ruff check web/backend/app/api/data/futures.py web/backend/tests/test_health_route_conflicts.py` | passed |
| `black --check web/backend/app/api/data/futures.py web/backend/tests/test_health_route_conflicts.py` | passed |
| OpenAPI smoke with `PYTHONPATH=web/backend` and root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |

The OpenAPI import captured 121 generic Python warnings. Duplicate operation ID
warnings remain 0.

Route/API direct factory refs:

| Metric | Current HEAD |
| --- | ---: |
| Total direct route/API `get_data_source_factory()` refs | 0 |
| `web/backend/app/api/data/futures.py` direct refs | 0 |

Remaining direct route/API refs:

- None.

## GitHub And GitNexus

PR `#230` reached CLEAN before merge: 9 checks succeeded and 4 were skipped.

PR `#230` staged GitNexus detect_changes reported LOW risk, 0 changed symbols,
and 0 affected processes after documentation artifacts were staged. No new
GitNexus source-edit gate is required by this docs/governance-only closeout.

## Decision

G2.78 implementation evidence remains valid at current HEAD. The route/API
direct `get_data_source_factory()` consumer migration is closed for the scanned
`web/backend/app/api` scope.

No additional source change is authorized by this closeout.

## Next Gate

Human review / PR merge decision for this closeout. If accepted, prepare a
separate compatibility getter retirement / retained-shim decision packet before
any `get_data_source_factory()` compatibility API removal, service package export
change, or downstream consumer rewrite.
