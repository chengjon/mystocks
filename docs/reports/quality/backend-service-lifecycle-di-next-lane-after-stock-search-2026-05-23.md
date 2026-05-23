# Backend Service Lifecycle DI Next-Lane After Stock Search - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: decision-packet-prepared-for-review
- Workline: G2.21 service lifecycle DI next-lane decision after stock-search closeout
- Base HEAD: `f8063b512fb7`
- Parent issue: [#79](https://github.com/chengjon/mystocks/issues/79)
- Parent decision issue: [#92](https://github.com/chengjon/mystocks/issues/92)
- Recorded at: `2026-05-23T10:24:32+08:00`

## Governance Boundary

This packet is governance-only. It chooses the next service lifecycle DI
planning lane after the merged stock-search implementation and closeout.

It does not authorize backend source edits, tests, route/OpenAPI changes,
compatibility getter deletion, issue label movement, OpenSpec changes, PM2
execution, runtime process changes, docs/API changes, generated clients, or
frontend work.

## Input State

| Item | Current state | Evidence |
|---|---|---|
| PR `#159` | `MERGED` | `25db762ae6484ad4638baf0f8ab42b94a978a403` |
| PR `#160` | `MERGED` | `f8063b512fb7c3aabfabef9d80d05d1d682569b5` |
| Issue `#79` | `OPEN`, `needs-triage` | Live GitHub status checked at this worktree |
| Issue `#92` | `OPEN`, `enhancement`, `ready-for-human`, `ready-for-downstream` | Live GitHub status checked at this worktree |
| Completed route-surface DI pilots in this sequence | `email_service.py`, `announcement_service.py`, `watchlist_service.py`, `stock_search_service.py` | G2.2-G2.20 reports and merged PRs |
| Reference service DI pattern | `tradingview_widget_service.py` | Existing reference/provider pattern |
| Watchlist adapter-aware helper cleanup | Complete | PRs `#152`-`#155` |
| Stock-search compatibility getter | Preserved | G2.20 closeout; direct route-local calls removed from approved route files |

## Current-Head Quick Scan

This packet ran a lightweight current-head scan at `f8063b512fb7` to determine
whether the next step can safely be a direct implementation authorization. It
cannot.

| Metric | Value |
|---|---:|
| Service Python files scanned | 152 |
| Files with getter/singleton/provider signal | 20 |
| Completed or reference provider-pattern files | 5 |
| Remaining getter/singleton signal files needing classification | 15 |

Completed or reference provider-pattern files:

- `web/backend/app/services/email_service.py`
- `web/backend/app/services/announcement_service.py`
- `web/backend/app/services/watchlist_service.py`
- `web/backend/app/services/stock_search_service/stock_search_service.py`
- `web/backend/app/services/tradingview_widget_service.py`

Remaining files requiring fresh classification before any authorization:

- `web/backend/app/services/market_data_service_v2.py`
- `web/backend/app/services/email_notification_service.py`
- `web/backend/app/services/unified_data_service.py`
- `web/backend/app/services/websocket_service.py`
- `web/backend/app/services/market_data_service/get_market_data_service.py`
- `web/backend/app/services/technical_analysis_service.py`
- `web/backend/app/services/realtime_streaming_service.py`
- `web/backend/app/services/tdx_service.py`
- `web/backend/app/services/data_service_enhanced.py`
- `web/backend/app/services/__init__.py`
- `web/backend/app/services/advanced_analysis_service.py`
- `web/backend/app/services/data_service.py`
- `web/backend/app/services/monitoring_service.py`
- `web/backend/app/services/wencai_service.py`
- `web/backend/app/services/strategy_service.py`

## Stock-Search Compatibility Getter Boundary

The stock-search implementation removed direct route-local
`get_stock_search_service()` calls from the approved route files, but the
compatibility getter remains intentionally present.

Current reference categories:

| Category | Current observation | Disposition |
|---|---|---|
| Service package exports/body | Getter and dependency provider remain in `stock_search_service` package | Expected compatibility surface |
| Approved route files | `0` direct getter calls; dependency-provider references remain | Completed G2.19 route-surface migration |
| Tests | Runtime regression tests still call the compatibility getter | Do not delete without a separate compatibility-cleanup packet |

Therefore, a compatibility getter cleanup is not safe as an automatic next step.
It needs its own consumer matrix, test update plan, GitNexus impact evidence,
and rollback boundary if selected later.

## Decision

Select **G2.22 current-head service lifecycle DI candidate refresh** as the next
service lifecycle DI lane.

G2.21 does not select a concrete implementation candidate. It deliberately
chooses a refresh packet because the prior G2.17 candidate pool was consumed by
G2.18-G2.20, and the remaining service getter/singleton surface contains broad
market, data, strategy, notification, websocket, monitoring, and registry
signals that require current-head classification.

## Required G2.22 Scope

The next packet should:

1. regenerate current service getter/singleton/provider inventory from HEAD;
2. classify every hit into completed, reference pattern, route-surface candidate,
   adapter/data/helper candidate, registry/integrated seam, external/live-data
   seam, process-level singleton, false positive, or hold;
3. scan current route/API consumers for each candidate getter;
4. scan tests and non-route consumers before recommending compatibility getter
   cleanup;
5. run GitNexus impact/context for any recommended candidate symbol before
   authorizing future source edits;
6. recommend exactly one next action:
   - prepare a concrete implementation authorization for one candidate,
   - prepare a compatibility getter cleanup authorization,
   - pause G2 and return to another architecture lane, or
   - perform another evidence-only refinement if candidate risk is still too
     high.

## Explicit Non-Goals

- No backend source or test edits.
- No compatibility getter deletion.
- No route path, request model, response shape, OpenAPI exposure, generated
  client, frontend, or docs/API changes.
- No PM2 or runtime process action.
- No issue label changes and no `ready-for-agent` movement.
- No OpenSpec proposal, change, spec modification, or archive action.
- No direct selection of the next service implementation candidate in this
  packet.

## Next Gate

Human review of this G2.21 decision packet.

If accepted, create a separate G2.22 current-head candidate refresh packet. G2.22
may gather evidence and recommend a later action, but it must not edit source
unless a subsequent implementation authorization packet is explicitly accepted.
