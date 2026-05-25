# Backend DataSourceFactory Futures Route Migration Risk Packet - 2026-05-25

Workline: G2.76 risk packet / final route consumer decision

Current HEAD: `53f365b55b37a03334ea25f083c8ef453fbb2db8`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This packet is decision-only. It does not authorize backend
source edits, test edits, route path changes, OpenAPI exposure changes, response
shape changes, frontend edits, PM2/runtime operations, OpenSpec proposal
publication, issue-label changes, compatibility getter deletion, or a
`futures.py` implementation.

## Status

Ready for review.

G2.75 closeout was merged in PR `#227`. The only remaining route/API direct
`get_data_source_factory()` calls are now in `web/backend/app/api/data/futures.py`.

## Current-Head Evidence

Route/API direct factory refs:

| Metric | Current HEAD |
| --- | ---: |
| Total direct route/API `get_data_source_factory()` refs | 2 |
| `web/backend/app/api/data/futures.py` direct refs | 2 |
| Other route/API direct refs | 0 |

Remaining direct refs:

- `web/backend/app/api/data/futures.py:91`
- `web/backend/app/api/data/futures.py:114`

`futures.py` shape:

| Fact | Value |
| --- | --- |
| LOC | 123 |
| Route handlers | `get_futures_index_daily`, `get_futures_index_realtime` |
| Runtime paths | `GET /api/v1/data/futures/index/daily`, `GET /api/v1/data/futures/index/realtime` |
| OpenAPI schema exposure | both included |
| Direct factory pattern | function-local import plus `await get_data_source_factory()` |
| `ruff check web/backend/app/api/data/futures.py` | passed |
| `black --check web/backend/app/api/data/futures.py` | would reformat |
| `black --diff web/backend/app/api/data/futures.py` | 2 hunks; 6 added diff lines; 2 removed diff lines |

OpenAPI and focused tests:

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_futures_index_endpoints_have_docs_examples_and_error_responses -q --no-cov --tb=short` | 1 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | 4 passed |
| OpenAPI route table with root `.env` loaded | 548 routes, 500 paths |
| Futures OpenAPI operation IDs | `get_futures_index_daily_api_v1_data_futures_index_daily_get`, `get_futures_index_realtime_api_v1_data_futures_index_realtime_get` |
| Duplicate operation ID warnings | 0 |

## GitNexus Risk

Default `gitnexus analyze` failed in this Git worktree because `.git` is a
worktree pointer file and GitNexus attempted to create `.git/info`. Running
`gitnexus analyze --no-gitignore --no-register` exited 0 with `Already up to
date`.

Risk readings:

| Target | Result | Interpretation |
| --- | --- | --- |
| `web/backend/app/api/data/futures.py` file-level upstream impact | HIGH, impactedCount 141, direct 27, processes affected 0 | Treat as a risk signal from file-level import fan-out. Do not use this as implementation approval. |
| Exact route-handler incoming callers via Cypher | 0 | The two functions are FastAPI route entrypoints rather than ordinary call-chain functions. |
| Exact route-handler outgoing calls via Cypher | both call `get_data_source_factory` | Confirms the migration surface is two route handlers. |

The file-level HIGH result is why this packet exists. The next implementation
must stay path-limited and must not fold in compatibility getter deletion,
response contract edits, or broad route governance changes.

## Decision Recommendation

Approve a future G2.77 path-limited implementation authorization packet for
`web/backend/app/api/data/futures.py` only.

The future implementation packet should authorize only:

1. Add a TDD guard that proves both futures route handlers expose a `factory`
   dependency wired to `get_data_source_factory_dependency`.
2. Add `DataSourceFactory` / `get_data_source_factory_dependency` imports in
   `futures.py`.
3. Add a `factory: DataSourceFactory = Depends(get_data_source_factory_dependency)`
   parameter to both route handlers.
4. Remove the two function-local `get_data_source_factory` imports and awaits.
5. Normalize same-file `futures.py` black formatting only if included in the
   authorized implementation diff.

## Required Future Verification

The future G2.77 implementation must rerun:

- TDD red before any source edit.
- Focused futures dependency-injection test.
- Full `web/backend/tests/test_health_route_conflicts.py`.
- `web/backend/tests/test_data_source_factory_lifecycle_di.py`.
- `ruff check web/backend/app/api/data/futures.py web/backend/tests/test_health_route_conflicts.py`.
- `black --check web/backend/app/api/data/futures.py web/backend/tests/test_health_route_conflicts.py`.
- OpenAPI smoke with route/path/operation ID duplicate checks.
- Direct route/API factory ref scan, expected `2 -> 0`.
- Staged GitNexus detect_changes.
- Post-commit mainline scope gate.

## Next Gate

Human review / PR merge decision for this risk packet. If accepted, create a
separate G2.77 path-limited implementation authorization packet for `futures.py`.
