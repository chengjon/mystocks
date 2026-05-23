# Backend Market Data Provider Design Packet

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-23

Status: design-packet-prepared-for-review

Workline: G2.25 market-data provider design

Base HEAD: `f97ca070853a77afc80c226d53948e805ba33c8e`

Parent evidence: PR `#164` merged the G2.24 broad service seam design packet at `f97ca070853a77afc80c226d53948e805ba33c8e`.

Boundary note: this packet classifies current market-data provider seams only. It
does not authorize backend source edits, test edits, route edits, OpenAPI
changes, OpenSpec changes, issue label movement, `ready-for-agent` movement,
PM2/runtime work, service consolidation, or a market-data implementation batch.

## Governance Boundary

This packet is evidence and design routing only. It exists because G2.24 found
that broad market/data/strategy service seams are too large to migrate as one
batch.

This packet does not authorize:

- backend source, route, test, OpenAPI, response-contract, PM2, or runtime changes
- OpenSpec proposal/spec creation or archive work
- issue label movement or ready-for-agent changes
- service consolidation between `MarketDataService` and `MarketDataServiceV2`
- dashboard/source-factory refactoring
- market-data adapter refactoring
- compatibility getter deletion, privatization, or rename

## Current-Head Evidence

Generated at: 2026-05-23T13:18:48+08:00

Current checkout:

- branch: `g2-25-market-data-provider-design`
- base branch: `origin/wip/root-dirty-20260403`
- HEAD: `f97ca0708 Merge pull request #164 from chengjon/g2-24-broad-service-seam-design`
- source guard before packet: no staged or unstaged source/test changes

## Provider Surfaces

| Surface | File | Current pattern | Consumers | Design classification |
|---|---|---|---|---|
| `MarketDataServiceV2` | `web/backend/app/services/market_data_service_v2.py` | module singleton `_market_data_service_v2` plus `get_market_data_service_v2()` | `market_v2.py` route functions and `dashboard_data_source.py` helper/class methods | Future route-provider candidate, but only after a separate implementation authorization |
| `MarketDataService` package getter | `web/backend/app/services/market_data_service/get_market_data_service.py` | module singleton `_market_data_service` plus `get_market_data_service()` | `market/market_data_request.py` FastAPI dependency parameters and `market_data_adapter.py` direct helper | Already partially route-DI-shaped; not the next implementation target |
| Integrated services accessor | `web/backend/app/services/__init__.py` | `get_integrated_services().market_data_service` accessor | no current direct text import consumers found | Do not conflate with the package getter |
| Dashboard market overview | `web/backend/app/api/dashboard_data_source.py` | class/helper methods call `get_market_data_service_v2()` directly | `RealBusinessDataSource._get_market_overview_data()` and `prewarm_dashboard_market_overview_cache()` | Separate dashboard/source-factory design, not ordinary route-provider DI |
| Market data adapter | `web/backend/app/services/market_data_adapter.py` | `_get_market_service()` calls package `get_market_data_service()` | service adapter internals | Separate adapter helper design, not route-surface DI |

## Current Consumers

### `MarketDataServiceV2`

`web/backend/app/services/market_data_service_v2.py` has 668 lines. The
constructor creates a database engine/sessionmaker and initializes the Eastmoney
adapter via `get_eastmoney_adapter()`.

Direct singleton getter:

- `_market_data_service_v2 = None`
- `get_market_data_service_v2() -> MarketDataServiceV2`

Route-surface consumers in `web/backend/app/api/market_v2.py`:

| Function | Current service method |
|---|---|
| `get_fund_flow` | `query_fund_flow` |
| `refresh_fund_flow` | `fetch_and_save_fund_flow` |
| `get_etf_list` | `query_etf_spot` |
| `refresh_etf_spot` | `fetch_and_save_etf_spot` |
| `get_lhb_detail` | `query_lhb_detail` |
| `refresh_lhb_detail` | `fetch_and_save_lhb_detail` |
| `get_sector_fund_flow` | `query_sector_fund_flow` |
| `refresh_sector_fund_flow` | `fetch_and_save_sector_fund_flow` |
| `get_stock_dividend` | `query_stock_dividend` |
| `refresh_stock_dividend` | `fetch_and_save_stock_dividend` |
| `get_stock_blocktrade` | `query_blocktrade` |
| `refresh_stock_blocktrade` | `fetch_and_save_blocktrade` |
| `refresh_all_market_data` | `fetch_and_save_fund_flow`, `fetch_and_save_etf_spot`, `fetch_and_save_sector_fund_flow`, `fetch_and_save_lhb_detail`, `fetch_and_save_blocktrade` |

Non-route helper consumers in `web/backend/app/api/dashboard_data_source.py`:

- `RealBusinessDataSource._get_market_overview_data()`
- `prewarm_dashboard_market_overview_cache()`

These dashboard consumers are intentionally not part of the recommended first
implementation authorization because they are not ordinary FastAPI route
dependency parameters.

### `MarketDataService`

`web/backend/app/services/market_data_service/get_market_data_service.py` has 33
lines and returns the package `MarketDataService` singleton. The concrete class
is assembled through `market_data_service_methods` mixins:

- `part1.py`: 669 lines, `MarketDataServiceCoreMixin`
- `part2.py`: 135 lines, `MarketDataServiceFetchAndSaveMixin`
- `part3.py`: 43 lines, `MarketDataServiceChipRaceQueryMixin`

The core mixin constructor creates a database engine/sessionmaker, initializes
Akshare and TQLEX adapters, and initializes cache integration.

Route consumers in `web/backend/app/api/market/market_data_request.py` already
use `Depends(get_market_data_service)`:

| Function | Current service method |
|---|---|
| `refresh_fund_flow` | `fetch_and_save_fund_flow` |
| `get_etf_list` | `query_etf_spot` |
| `refresh_etf_data` | `fetch_and_save_etf_spot` |
| `get_chip_race` | `query_chip_race` |
| `refresh_chip_race` | `fetch_and_save_chip_race` |
| `get_lhb_detail` | `query_lhb_detail` |
| `refresh_lhb_detail` | `fetch_and_save_lhb_detail` |

Additional service-layer consumer:

- `web/backend/app/services/market_data_adapter.py::_get_market_service()`

## GitNexus Evidence

| Target | Risk | Impacted count | Direct callers | Processes affected | Modules affected | Notes |
|---|---:|---:|---:|---:|---:|---|
| `get_market_data_service_v2` | CRITICAL | 18 | 15 | 6 | 2 | GitNexus and text scan agree this is a broad route/dashboard surface |
| `get_market_data_service` | LOW | 0 | 0 | 0 | 0 | GitNexus undercounts FastAPI dependency-parameter consumers; text scan is authoritative for current active route usage |

GitNexus context for `get_market_data_service` is ambiguous:

- `web/backend/app/services/market_data_service/get_market_data_service.py:get_market_data_service`
- `web/backend/app/services/__init__.py:get_market_data_service`

The integrated-services accessor in `web/backend/app/services/__init__.py` has no
current direct text import consumers in `web/backend/app`. It must not be
conflated with the package getter imported by `market/market_data_request.py`.

## Design Decision

Do not consolidate `MarketDataService` and `MarketDataServiceV2`.

Reasons:

- They have different construction dependencies.
- They expose overlapping but not identical method surfaces.
- They are tied to different API ownership surfaces: `/api/v1/market` versus `/api/v2/market`.
- `market_data_request.py` already uses FastAPI dependency parameters, while `market_v2.py` still uses direct singleton calls.
- Dashboard market overview uses `MarketDataServiceV2` from helper/class methods, not from normal route dependency injection.

The provider-governance target is standardizing access shape, not merging service
classes.

## Recommended Next Lane

Create a separate `G2.26 MarketDataServiceV2 route-provider implementation authorization` packet.

That future authorization packet should be governance-only and should decide the
exact code scope before implementation. The recommended candidate scope is:

- `web/backend/app/services/market_data_service_v2.py`
- `web/backend/app/api/market_v2.py`
- a focused market-v2 route dependency override test file
- implementation evidence report
- PR task card

Recommended future behavior, if authorized later:

- keep `get_market_data_service_v2()` as compatibility fallback
- add a state key, installer, and FastAPI dependency provider following the
  route-level pattern already used by the stock-search lane
- inject `MarketDataServiceV2` into `market_v2.py` route handlers through
  `Depends(...)`
- leave route paths, response shape, OpenAPI operation IDs, and service methods
  unchanged

Explicit exclusions for the first implementation authorization:

- no `dashboard_data_source.py` mutation
- no `market_data_adapter.py` mutation
- no `market_data_service` package/provider rewrite
- no service consolidation
- no route path or OpenAPI schema exposure change
- no docs/API/generated-client/frontend/PM2 changes

## Future Separate Lanes

After the `MarketDataServiceV2` route-provider authorization and implementation
are reviewed, separate packets may be considered for:

- dashboard market overview/source-factory provider design
- `MarketDataService` package provider/app-state normalization
- `market_data_adapter.py` helper seam
- legacy route/API ownership reconciliation between market v1 and v2

None of those are authorized by this packet.

## Verification Plan For This Packet

This packet should be accepted only if:

- markdown governance passes for this report and the steward tree
- generated JSON evidence parses
- mainline scope gate passes with only the allowed governance paths
- git diff checks pass
- source guard remains empty for `web/backend`, `web/frontend`, `src`, `tests`, and `openspec`
- staged GitNexus detect-changes shows no runtime/source blast radius
