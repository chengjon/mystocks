# Backend DataSourceFactory Route Candidate Authorization - 2026-05-25

Workline: G2.66 authorization-only packet

Current HEAD: `d30f2c12d642fbc613689d85b39697999805bbb8`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This document is a governance evidence and authorization input
only. It does not authorize source code changes, GitHub issue publication,
OpenSpec proposal publication, OpenSpec implementation, production rollout, or
promotion of this candidate selection into backend runtime truth.

Boundary: this packet records current evidence and selects the next candidate.
It does not authorize or perform backend source edits. A separate G2.67
implementation branch is required before changing route code.

## Prior Gate

PR `#212` merged the G2.65 closeout for the `market.py` DataSourceFactory route
migration. The closeout confirmed:

- `market.py` direct `get_data_source_factory()` refs remain `0`
- total remaining route/API direct factory refs remain `13`
- health route conflict tests: `114 passed`
- DataSourceFactory lifecycle DI tests: `4 passed`
- OpenAPI smoke remains routes=`548`, paths=`500`, duplicate operation IDs=`0`

## Current Candidate Matrix

| Candidate | Direct refs | Routes | LOC | Ruff | Black | GitNexus upstream | Decision |
|---|---:|---:|---:|---|---|---|---|
| `web/backend/app/api/data/margin.py` | 3 | 3 | 155 | pass | unchanged | LOW/1 | Select for G2.67 |
| `web/backend/app/api/data/lhb.py` | 2 | 2 | 128 | pass | would reformat | LOW/1 | Defer behind margin; same-file formatting debt exists |
| `web/backend/app/api/market/market_data_request.py` | 2 | 11 | 645 | pass | unchanged | LOW/1 | Defer; broad route surface |
| `web/backend/app/api/data/kline.py` | 2 | 4 | 252 | E701 | would reformat | LOW/1 | Defer; style cleanup must be bundled if touched |
| `web/backend/app/api/data/stocks.py` | 2 | 5 | 417 | E701 | would reformat | LOW/1 | Defer; style cleanup and larger route surface |
| `web/backend/app/api/data/futures.py` | 2 | 2 | 123 | pass | would reformat | CRITICAL/91 | Defer until a narrower impact pass explains the file-level GitNexus result |

Selection rationale: `margin.py` is the cleanest next batch. It removes three
direct factory calls, has only three route handlers, has no current ruff/black
cleanup requirement, and has LOW/1 GitNexus upstream impact.

## Selected G2.67 Scope

If this packet is accepted, the next implementation packet may only touch:

- `web/backend/app/api/data/margin.py`
- `web/backend/tests/test_health_route_conflicts.py`

The implementation should migrate these handlers to
`get_data_source_factory_dependency`:

- `get_margin_account_info`
- `get_margin_detail_sse`
- `get_margin_detail_szse`

Expected route-guard result after G2.67 implementation:

- `margin.py` direct refs: `3` -> `0`
- total route/API direct refs: `13` -> `10`

## Locked Scope

This packet keeps the following locked:

- `web/backend/app/api/data/kline.py`
- `web/backend/app/api/data/futures.py`
- `web/backend/app/api/data/lhb.py`
- `web/backend/app/api/data/stocks.py`
- `web/backend/app/api/market/market_data_request.py`
- `web/frontend/**`
- `src/**`
- `openspec/changes/**`
- `docs/api/**`

No compatibility getter removal, OpenAPI contract edit, route path edit, frontend
consumer edit, PM2/runtime stateful gate, or issue-label change is authorized by
this packet.

## Required G2.67 Gates

Before source edits:

1. Read `architecture/STANDARDS.md`.
2. Run GitNexus impact/context for `margin.py` or the selected route handlers.
3. Add failing dependency-injection wiring assertions for all three margin route
   handlers.
4. Stop if any HIGH or CRITICAL risk appears.

Required verification:

- `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short`
- `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short`
- `ruff check web/backend/app/api/data/margin.py web/backend/tests/test_health_route_conflicts.py web/backend/app/services/data_source_factory/__init__.py`
- `black --check web/backend/app/api/data/margin.py web/backend/tests/test_health_route_conflicts.py web/backend/app/services/data_source_factory/__init__.py`
- OpenAPI smoke with routes, paths, operation IDs, and duplicate operation IDs
- route-guard direct-call count
- `gitnexus.detect_changes(scope=staged)`

## Current Evidence

- Current HEAD: `d30f2c12d642fbc613689d85b39697999805bbb8`
- Remaining direct refs: `13`
- Candidate tests:
  - `web/backend/tests/test_health_route_conflicts.py`: `114 passed`
  - `web/backend/tests/test_data_source_factory_lifecycle_di.py`: `4 passed`
- OpenAPI smoke: routes=`548`, paths=`500`, operation IDs=`536`, duplicate
  operation IDs=`0`, duplicate operation ID warnings=`0`, warning count=`121`
- Candidate lint:
  - `margin.py`: ruff clean, black unchanged
  - `kline.py` and `stocks.py`: existing E701 findings
  - `kline.py`, `futures.py`, `lhb.py`, and `stocks.py`: black would reformat
- Environment note: OpenAPI smoke used explicit non-secret test environment
  placeholders because the isolated worktree has no `.env` file.

## Review Gate

Human review / PR merge decision. If accepted, create G2.67 as a separate
path-limited `margin.py` implementation branch. This G2.66 packet itself
authorizes no backend source edit.
