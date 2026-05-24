# Backend Data Source Factory Lifecycle DI Authorization - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.59 data-source factory lifecycle DI authorization

Base branch: `wip/root-dirty-20260403`

Current HEAD: `1880f0d1395e7c5594b70f3ba40478cff24f2d3a`

## Scope Boundary

G2.59 is a governance and authorization packet only.

This packet does not modify backend source code, tests, route paths, response
contracts, OpenAPI exposure, generated clients, OpenSpec files, issue labels,
runtime processes, or PM2 state.

The purpose is to decide whether `get_data_source_factory` is a suitable next
service lifecycle DI seam and to define the next gate before any source edit.

## Upstream Evidence

G2.58 selected `get_data_source_factory` as the next design-only seam after the
G2.57 GitNexus refresh.

Upstream accepted state:

- PR `#199` merged at `1880f0d1395e7c5594b70f3ba40478cff24f2d3a`.
- Ordinary provider-style rows were implemented or closed.
- `get_data_source_dependency` was classified as already provider-shaped with
  `3` dashboard route sites.
- `get_data_source_factory` remained the next candidate because it had `17`
  direct API call sites across `9` files.

## Current Evidence

Static current-head scan in this G2.59 worktree reports:

- API files scanned: `219`
- Direct `get_data_source_factory()` API calls: `17`
- API files containing direct calls: `9`

Consumer matrix:

| File | Calls | Lines |
|---|---:|---|
| `web/backend/app/api/data/financial.py` | 1 | `69` |
| `web/backend/app/api/data/futures.py` | 2 | `91`, `114` |
| `web/backend/app/api/data/kline.py` | 2 | `145`, `245` |
| `web/backend/app/api/data/lhb.py` | 2 | `90`, `115` |
| `web/backend/app/api/data/margin.py` | 3 | `104`, `128`, `150` |
| `web/backend/app/api/data/market.py` | 1 | `98` |
| `web/backend/app/api/data/stocks.py` | 2 | `269`, `371` |
| `web/backend/app/api/data_quality.py` | 2 | `58`, `369` |
| `web/backend/app/api/market/market_data_request.py` | 2 | `134`, `427` |

The canonical singleton surface remains:

- `web/backend/app/services/data_source_factory/data_source_factory.py`
- `_global_factory: Optional[DataSourceFactory] = None`
- `async def get_data_source_factory() -> DataSourceFactory`
- The getter creates `DataSourceFactory()`, awaits `initialize()`, and returns
  the module-level singleton.

## GitNexus Evidence

GitNexus was refreshed from a temporary non-linked checkout:

- Checkout: `.worktrees/g2-59-gitnexus-index-checkout`
- `.git` kind: `directory`
- HEAD: `1880f0d1395e`
- `gitnexus analyze` exit: `0`
- Nodes: `62624`
- Edges: `145803`
- Clusters: `3288`
- Flows: `300`

GitNexus context resolves `get_data_source_factory` to:

```text
web/backend/app/services/data_source_factory/data_source_factory.py
lines 294-300
```

Refreshed upstream impact remains high enough to forbid an opportunistic code
edit:

```text
risk=CRITICAL
impactedCount=22
direct=21
processes_affected=15
modules_affected=3
```

Direct incoming callers include:

- `web/backend/app/api/data_quality.py:get_sources_health`
- `web/backend/app/api/data_quality.py:get_system_status_overview`
- `web/backend/app/services/data_source_factory/data_source_factory.py:get_data_source`
- `web/backend/app/services/data_source_factory/data_source_factory.py:get_market_data`
- `web/backend/app/services/data_source_factory/data_source_factory.py:get_dashboard_data`
- `web/backend/app/services/data_source_factory/data_source_factory.py:get_technical_analysis_data`
- `web/backend/app/api/market/market_data_request.py:get_fund_flow`
- `web/backend/app/api/market/market_data_request.py:get_market_quotes`
- `web/backend/app/api/data/stocks.py:get_stocks_basic`
- `web/backend/app/api/data/stocks.py:search_stocks`
- `web/backend/app/api/data/market.py:get_market_overview`
- `web/backend/app/api/data/margin.py:get_margin_account_info`
- `web/backend/app/api/data/margin.py:get_margin_detail_sse`
- `web/backend/app/api/data/margin.py:get_margin_detail_szse`
- `web/backend/app/api/data/lhb.py:get_dragon_tiger_detail`
- `web/backend/app/api/data/lhb.py:get_dragon_tiger_institution_stats`
- `web/backend/app/api/data/kline.py:get_daily_kline`
- `web/backend/app/api/data/kline.py:get_intraday_data`
- `web/backend/app/api/data/futures.py:get_futures_index_daily`
- `web/backend/app/api/data/futures.py:get_futures_index_realtime`
- `web/backend/app/api/data/financial.py:get_financial_data`

Affected modules include `Data`, `Data_source_factory`, and `Api`.

## Decision

G2.59 authorizes no source implementation.

The seam is selected as the next planning target, but its CRITICAL blast radius
requires one more decomposition gate before source edits.

Recommended next gate:

1. Create G2.60 as a dedicated `get_data_source_factory` consumer-matrix and
   implementation-authorization packet.
2. Keep G2.60 source-free unless it is explicitly split into a separate
   implementation branch after review.
3. Decide whether the first implementation slice should only add an app-state
   provider seam while preserving all existing callers, or whether a very small
   route migration batch is safe.

## Future Implementation Candidate Scope

If G2.60 or a later reviewed packet authorizes code, the likely write scope is:

- `web/backend/app/services/data_source_factory/data_source_factory.py`
- A focused lifecycle DI test for the provider seam and fallback getter behavior
- A future implementation evidence report and mainline task card

Potential future service changes may include:

- Add a stable state key for `DataSourceFactory`.
- Add an installer that places a provided or initialized factory on `app.state`.
- Add a FastAPI dependency provider that reads the request app state.
- Preserve `get_data_source_factory()` as the compatibility getter.
- Preserve convenience functions such as `get_data_source`, `get_market_data`,
  `get_dashboard_data`, and `get_technical_analysis_data`.

Route migration must be a later explicit batch. The `17` direct API call sites
are not automatically authorized for bulk rewrite by this packet.

## Explicit Exclusions

This packet does not authorize:

- Editing `web/backend/app/api/**`.
- Editing `web/backend/app/services/data_source_factory/data_source_factory.py`.
- Removing or renaming `get_data_source_factory`.
- Removing `_global_factory`.
- Rewriting ambiguous same-name `get_data_source` surfaces.
- Migrating `get_postgres_async`, `get_config_manager`, repository getters, or
  unrelated service seams.
- Changing route paths, query parameters, response shapes, OpenAPI exposure, or
  operation IDs.
- Creating or modifying OpenSpec changes.
- Moving issue labels or declaring issue `#79` closed.

## Acceptance For The Next Source Packet

A future implementation packet must include:

- Fresh GitNexus impact and context before editing the service symbol.
- A current static consumer matrix for all `17` route/API call sites.
- A TDD plan that proves both app-state provider behavior and compatibility
  getter fallback behavior.
- Focused tests for at least one representative route consumer before any route
  migration.
- Ruff, formatting, app import, OpenAPI path count, and duplicate operation ID
  checks after implementation.
- `gitnexus_detect_changes(scope=staged)` before commit.

## Closeout

G2.59 converts the G2.58 next-lane selection into a concrete authorization
boundary.

The next step is human review of this packet. If accepted, open G2.60 as a
separate `get_data_source_factory` consumer-matrix / implementation-authorization
packet before any backend source edit.
