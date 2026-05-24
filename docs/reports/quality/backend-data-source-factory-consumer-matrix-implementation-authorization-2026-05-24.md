# Backend Data Source Factory Consumer Matrix And Implementation Authorization - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.60 data-source factory consumer matrix / implementation authorization

Base branch: `wip/root-dirty-20260403`

Current HEAD: `265f38e53bddfa3a925f14cfbc5080b00dce26e6`

## Scope Boundary

G2.60 is a governance and implementation-authorization packet only.

This packet does not modify backend source code, tests, route paths, response
contracts, OpenAPI exposure, generated clients, OpenSpec files, issue labels,
runtime processes, or PM2 state.

Its purpose is to split the `get_data_source_factory` seam into executable
batches and authorize the first future implementation branch only if this packet
is accepted.

## Upstream State

G2.59 was merged by PR `#200` at
`265f38e53bddfa3a925f14cfbc5080b00dce26e6`.

Accepted G2.59 facts:

- `get_data_source_factory` resolves to
  `web/backend/app/services/data_source_factory/data_source_factory.py:294-300`.
- Static API direct calls: `17` across `9` files.
- GitNexus upstream impact: `CRITICAL`, with `22` impacted symbols, `21`
  direct callers, `15` affected processes, and `3` affected modules.
- No source implementation was authorized by G2.59.

## Current Evidence

Static current-head scan in the G2.60 worktree reports:

- API files scanned: `219`
- Direct `get_data_source_factory()` API calls: `17`
- API files containing direct calls: `9`

Consumer matrix:

| File | Calls | Lines | Proposed disposition |
|---|---:|---|---|
| `web/backend/app/api/data/financial.py` | 1 | `69` | later domain route batch |
| `web/backend/app/api/data/futures.py` | 2 | `91`, `114` | later domain route batch |
| `web/backend/app/api/data/kline.py` | 2 | `145`, `245` | later domain route batch |
| `web/backend/app/api/data/lhb.py` | 2 | `90`, `115` | later domain route batch |
| `web/backend/app/api/data/margin.py` | 3 | `104`, `128`, `150` | later domain route batch |
| `web/backend/app/api/data/market.py` | 1 | `98` | later domain route batch |
| `web/backend/app/api/data/stocks.py` | 2 | `269`, `371` | later domain route batch |
| `web/backend/app/api/data_quality.py` | 2 | `58`, `369` | first route migration candidate after provider closeout |
| `web/backend/app/api/market/market_data_request.py` | 2 | `134`, `427` | later market route batch |

Service-internal compatibility callers remain in:

- `get_data_source`
- `get_market_data`
- `get_dashboard_data`
- `get_technical_analysis_data`

These are compatibility or convenience functions, not deletion candidates.

## GitNexus Evidence

GitNexus was refreshed from a temporary non-linked checkout:

- Checkout: `.worktrees/g2-60-gitnexus-index-checkout`
- `.git` kind: `directory`
- HEAD: `265f38e53bdd`
- `gitnexus analyze` exit: `0`
- Nodes: `62628`
- Edges: `145797`
- Clusters: `3291`
- Flows: `300`

GitNexus context resolves `get_data_source_factory` to:

```text
web/backend/app/services/data_source_factory/data_source_factory.py
lines 294-300
```

Refreshed upstream impact:

```text
risk=CRITICAL
impactedCount=22
direct=21
processes_affected=15
modules_affected=3
```

The direct incoming callers are the same route/service surfaces recorded in
G2.59. Affected modules are `Data`, `Data_source_factory`, and `Api`.

## Existing Test Surface

The current checkout already has data-source factory and route-adjacent tests
that should inform future TDD:

- `web/backend/tests/test_data_source_factory.py`
- `web/backend/tests/_test_data_source_factory_convenience.py`
- `web/backend/tests/_test_data_source_factory_management.py`
- `web/backend/tests/_test_data_source_factory_sources.py`
- `web/backend/tests/_test_data_source_factory_support.py`
- `web/backend/tests/test_data_source_manager_regressions.py`
- `web/backend/tests/test_data_stocks_runtime_fallback.py`
- `tests/backend/test_data_api_regression.py`
- `web/backend/tests/test_market_api_integration.py`

## Batch Decision

Because the seam is `CRITICAL`, route migration must not be the first
implementation step.

G2.60 selects a two-level decomposition:

1. G2.61a: provider seam only, no route migration.
2. G2.61b or later: route migration batches only after G2.61a closeout proves
   provider behavior and fallback compatibility.

## Authorized Future G2.61a Scope

If this packet is accepted, the next source branch may implement only the
provider seam.

Allowed future write scope for G2.61a:

- `web/backend/app/services/data_source_factory/data_source_factory.py`
- `web/backend/tests/test_data_source_factory_lifecycle_di.py`
- `docs/reports/quality/backend-data-source-factory-provider-seam-implementation-2026-05-24.md`
- `governance/mainline/task-cards/pr-202.yaml`

Allowed future service changes:

- Add a stable state key for `DataSourceFactory`.
- Add an installer that can place a provided or initialized factory on
  `app.state`.
- Add a FastAPI dependency provider that returns the app-state factory when
  present and preserves fallback behavior when absent.
- Preserve `get_data_source_factory()` as the public compatibility getter.
- Preserve `_global_factory`.
- Preserve service-internal convenience functions.

Explicit G2.61a non-goals:

- No edits under `web/backend/app/api/**`.
- No route dependency rewiring.
- No route path, query parameter, response shape, OpenAPI exposure, or operation
  ID change.
- No compatibility getter cleanup.
- No `get_postgres_async`, `get_config_manager`, repository getter, or
  ambiguous same-name `get_data_source` migration.
- No startup/runtime process, PM2, or issue-label change.

## Future Route Migration Order

After G2.61a is implemented, merged, and closed out, route migration should be
split as separate reviewed packets.

Recommended order:

1. G2.61b: `web/backend/app/api/data_quality.py`, `2` calls, first route
   migration candidate.
2. Later data-domain batches:
   `financial.py`, `futures.py`, `kline.py`, `lhb.py`, `margin.py`,
   `market.py`, and `stocks.py`.
3. Later market route batch:
   `web/backend/app/api/market/market_data_request.py`.

Each route batch must rerun the static consumer matrix, OpenAPI path count,
duplicate operation ID check, focused route tests, and GitNexus staged-scope
check before commit.

## Future G2.61a TDD Plan

Before implementation, write failing focused tests for:

- Installing a provided `DataSourceFactory` on app state.
- Dependency provider returning the installed factory.
- Dependency provider preserving fallback behavior when app state is missing.
- Existing `get_data_source_factory()` compatibility getter still returning an
  initialized factory.
- Convenience functions still delegating through the compatibility getter.

Minimum green checks for G2.61a:

- `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov`
- `pytest -o addopts= web/backend/tests/test_data_source_factory.py -q --no-cov`
- Ruff on touched backend source/test files.
- App import smoke.
- OpenAPI smoke: path count and duplicate operation ID count.
- `gitnexus_detect_changes(scope=staged)`.

## Decision

G2.60 authorizes the future G2.61a provider-seam implementation boundary only
after human review / PR acceptance of this packet.

It does not authorize route migration. The `17` direct API call sites remain
locked until a later route-specific packet is reviewed and accepted.

## Next Gate

Human review this G2.60 packet / PR.

If accepted, create a separate G2.61a implementation branch for the provider
seam only. That branch must start with GitNexus impact/context for
`get_data_source_factory` and must stop if the refreshed risk differs from the
authorized CRITICAL route/provider seam described here.
