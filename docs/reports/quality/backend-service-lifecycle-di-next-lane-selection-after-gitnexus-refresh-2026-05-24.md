# Backend Service Lifecycle DI Next Lane Selection After GitNexus Refresh - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Generated at: `2026-05-24T19:22:00+08:00`

Workline: G2.58 service lifecycle DI next-lane selection after G2.57
GitNexus refresh.

Base branch: `wip/root-dirty-20260403`

Current HEAD: `5dbb0ca0c387`

## Status

G2.58 is a decision-only next-lane selection packet.

It does not authorize backend source edits, route changes, OpenAPI changes,
compatibility getter cleanup, issue label changes, or implementation work. Its
only purpose is to decide which seam should receive the next separate design or
authorization packet.

## Upstream Evidence

| Workline | PR | State | Commit | Notes |
| --- | --- | --- | --- | --- |
| G2.57 | `#198` | `MERGED` | `5dbb0ca0c387dafb313e9b5f2674f3023da65962` | Non-linked GitNexus refresh closed the stale-graph blocker for `IndicatorRegistry` provider symbols |

## Current Refresh Evidence

A fresh non-linked GitNexus refresh was run at current HEAD for this selection
packet:

```text
checkout_head=5dbb0ca0c387
git_dot_kind=directory
gitnexus_analyze_exit=0
Repository indexed successfully (65.4s)
62,621 nodes | 145,801 edges | 3287 clusters | 300 flows
```

Static current-head scan in the G2.58 governance worktree reports:

| Metric | Value |
| --- | ---: |
| API files scanned | `219` |
| Service files scanned | `152` |
| Route `Depends(...)` sites | `353` |
| Provider-style route dependency sites | `81` |
| Getter-style route dependency sites | `272` |

## Provider Group Classification

| Provider dependency | Sites | Files | Classification |
| --- | ---: | ---: | --- |
| `get_advanced_analysis_service_dependency` | `14` | `1` | Implemented / closed in prior G2 lane |
| `get_market_data_service_v2_dependency` | `14` | `2` | Implemented / closed in prior G2 lane |
| `get_announcement_service_dependency` | `11` | `1` | Implemented / closed in prior G2 lane |
| `get_market_data_service_dependency` | `7` | `1` | Implemented / closed in prior G2 lane |
| `get_watchlist_service_dependency` | `7` | `1` | Implemented / closed in prior G2 lane |
| `get_email_service_dependency` | `6` | `1` | Implemented / closed in prior G2 lane |
| `get_stock_search_service_dependency` | `6` | `2` | Implemented / closed in prior G2 lane |
| `get_tradingview_service_dependency` | `6` | `1` | Implemented / closed in prior G2 lane |
| `get_tdx_service_dependency` | `5` | `1` | Implemented / closed in prior G2 lane |
| `get_indicator_registry_dependency` | `2` | `1` | Implemented / closed by G2.54-G2.57 |
| `get_data_source_dependency` | `3` | `1` | Already provider-shaped; needs closeout/design review, not direct implementation |

The ordinary route-provider implementation queue should not select another
source edit directly from this table. The only unclassified provider row,
`get_data_source_dependency`, already wraps `get_market_data_service_v2_dependency`
and is used by three `dashboard.py` handlers.

## Remaining Service-Like Seams

| Surface | Evidence | Risk / disposition |
| --- | --- | --- |
| `get_data_source_factory` | `17` direct API call sites across `9` files | GitNexus upstream impact is `CRITICAL`; select next design packet only |
| `get_postgres_async` | `22` direct call sites across `8` API files | Infrastructure/data-access seam; not ordinary service DI |
| `get_data_source` | `20` direct call sites across `4` API files | Ambiguous same-name surface; requires domain separation before edits |
| `get_config_manager` | `17` direct call sites across active and historical API files | Ambiguous config ownership seam; not selected for immediate DI |
| Repository getters such as `get_strategy_repository` | Route/persistence boundary | Needs repository governance, not service lifecycle provider migration |

## Selected Next Lane

G2.58 selects `get_data_source_factory` as the next design-only seam.

This is not a source implementation target. The next packet should be a
dedicated G2.59 design/authorization candidate for the data-source factory
direct-call seam.

Selection rationale:

- It is the largest remaining service-like direct-call seam with concrete route
  consumers.
- GitNexus can resolve the symbol in the refreshed graph.
- GitNexus upstream impact is `CRITICAL`, with `22` impacted symbols, `21`
  direct dependents, `15` affected processes, and `3` affected modules.
- Because of that blast radius, direct implementation would be unsafe without a
  narrower design packet.

## GitNexus Evidence For Selected Seam

GitNexus context for `get_data_source_factory` resolves to:

```text
web/backend/app/services/data_source_factory/data_source_factory.py
startLine=294
endLine=300
```

GitNexus upstream impact:

```text
risk=CRITICAL
impactedCount=22
direct=21
processes_affected=15
modules_affected=3
```

Affected modules include `Data`, `Data_source_factory`, and `Api`.

## Required G2.59 Boundaries

The next G2.59 packet must remain design/authorization-only unless explicitly
approved later. It should include:

1. Exact consumer matrix for the `17` API direct-call sites.
2. Split between route-local dependency injection, service package provider,
   and factory lifecycle ownership.
3. Explicit exclusion or separate handling for `get_postgres_async`,
   `get_config_manager`, repository getters, and same-name `get_data_source`
   surfaces.
4. Pre-edit GitNexus impact commands for each selected symbol.
5. TDD plan and rollback boundary before any backend source edit.

## Decision

G2.58 closes candidate selection for the next service lifecycle DI planning
step:

- Do not start source implementation from this packet.
- Do not treat `get_data_source_dependency` as a missing provider migration.
- Prepare G2.59 as a dedicated `get_data_source_factory` design /
  implementation-authorization candidate.

## Next Gate

Human review this G2.58 packet / PR. If accepted, create a separate G2.59
design/authorization packet for `get_data_source_factory`; source edits remain
locked until that later packet is reviewed and approved.
