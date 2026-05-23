# Backend Broad Service Seam Design Packet

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-23

Status: design-packet-prepared-for-review

Workline: G2.24 broad market/data/strategy service seam design

Base HEAD: `18f5b43275bbd1fc7f53c739063da37c6a753b11`

Parent evidence: PR `#163` merged the G2.23 stock-search compatibility getter consumer matrix at `18f5b43275bbd1fc7f53c739063da37c6a753b11`.

Boundary note: this packet classifies current broad market/data/strategy service
seams only. It does not authorize backend source edits, test edits, route edits,
OpenAPI changes, OpenSpec changes, issue label movement, `ready-for-agent`
movement, PM2/runtime work, or any mixed service implementation batch.

## Governance Boundary

This packet is evidence and design routing only.

It does not authorize:

- backend source, route, test, OpenAPI, response-contract, PM2, or runtime changes
- OpenSpec proposal/spec creation or archive work
- issue label movement or ready-for-agent changes
- any mixed market/data/strategy implementation batch
- deletion, privatization, or compatibility-wrapper cleanup

The purpose is to decide how the next service lifecycle DI lane should be decomposed after stock-search route-surface DI and compatibility-getter retention were accepted.

## Current-Head Evidence

Generated at: 2026-05-23T12:01:41+08:00

Current checkout:

- branch: `g2-24-broad-service-seam-design`
- base branch: `origin/wip/root-dirty-20260403`
- HEAD: `18f5b4327 Merge pull request #163 from chengjon/g2-23-stock-search-compat-getter-matrix`
- source guard before packet: no staged or unstaged `web/backend`, `src`, or `tests` changes

OpenSpec context:

- `migrate-backend-singletons-to-lifecycle-di` is listed as complete.
- This packet does not create a new OpenSpec change. Any future implementation lane still requires a separate approved authorization packet or OpenSpec proposal when the chosen design changes architecture or behavior.

## Text-Scan Service Matrix

The text scan covered `web/backend/app` Python files at HEAD `18f5b43275bb`.

| Seam | Canonical service file | Service LOC | Text-hit files | Route files | Service files | Current route/service surface |
|---|---:|---:|---:|---:|---:|---|
| `market_data_service_v2` | `web/backend/app/services/market_data_service_v2.py` | 668 | 3 | 2 | 1 | `market_v2.py` has direct calls across market-data endpoints; `dashboard_data_source.py` uses it for market overview cache/data |
| `market_data_service` | `web/backend/app/services/market_data_service/get_market_data_service.py` | 33 | 8 | 3 | 5 | `market/market_data_request.py` already uses `Depends(get_market_data_service)`; package exports and adapter references also exist |
| `data_service` | `web/backend/app/services/data_service.py` | 472 | 5 | 4 | 1 | indicator, strategy helper, backtest helper, and health/control-plane surfaces call or wrap `get_data_service()` |
| `strategy_service` | `web/backend/app/services/strategy_service.py` | 461 | 5 | 1 | 3 | strategy route, strategy adapters, data adapters, and backtest task code all reference `get_strategy_service()` |
| `tdx_service` | `web/backend/app/services/tdx_service.py` | 280 | 3 | 2 | 1 | `tdx.py` already uses `Depends(get_tdx_service)`; `dashboard_data_source.py` still uses live-market helper calls |
| `enhanced_data_service` | `web/backend/app/services/data_service_enhanced.py` | 630 | 1 | 0 | 1 | exported singleton remains in service module; `v1/system/health.py` constructs `EnhancedDataService` through its own local helper rather than the exported getter |
| `technical_analysis_service` | `web/backend/app/services/technical_analysis_service.py` | 751 | 1 | 0 | 1 | no route-surface consumer found by this scan; large service-internal seam only |

The `market_data_service` row deliberately records both graph and text evidence. GitNexus reports `get_market_data_service` as LOW/0 upstream impact, while current text evidence shows active dependency-provider usage in `market/market_data_request.py`. Future design work must reconcile this graph/text mismatch before treating the getter as unused.

## GitNexus Impact Spot Checks

GitNexus impact was run against the current indexed repo for representative service accessors/classes.

| Target | File | Risk | Impacted count | Direct callers | Processes affected | Modules affected | Design implication |
|---|---|---:|---:|---:|---:|---:|---|
| `get_market_data_service_v2` | `web/backend/app/services/market_data_service_v2.py` | CRITICAL | 18 | 15 | 6 | 2 | Direct route cluster; requires a separate provider-design packet before source edits |
| `get_market_data_service` | `web/backend/app/services/market_data_service/get_market_data_service.py` | LOW | 0 | 0 | 0 | 0 | Graph/text mismatch; do not infer deletion or no-op status |
| `get_data_service` | `web/backend/app/services/data_service.py` | CRITICAL | 5 | 3 | 7 | 2 | Indicator/backtest/strategy-data seam; not a route-only DI pilot |
| `get_strategy_service` | `web/backend/app/services/strategy_service.py` | CRITICAL | 13 | 6 | 0 | 5 | Crosses route, adapter, data-adapter, and task surfaces; needs adapter/task seam design |
| `get_tdx_service` | `web/backend/app/services/tdx_service.py` | CRITICAL | 6 | 2 | 5 | 1 | Live-market dashboard path and existing dependency-provider route path must be handled separately |
| `get_enhanced_data_service` | `web/backend/app/services/data_service_enhanced.py` | LOW | 3 | 1 | 0 | 0 | Control-plane/system-health adjacent; do not mix with business route batches |
| `TechnicalAnalysisService` | `web/backend/app/services/technical_analysis_service.py` | LOW | 0 | 0 | 0 | 0 | No route-surface consumer found; hold for service-internal test seam later |

High/critical results are expected here because this packet samples broad seams. They are not implementation failures; they are why the next lane must stay design-first.

## Design Classification

### Market Data V2

`market_data_service_v2` is the broadest current route-surface cluster in this scan. `market_v2.py` performs direct getter calls across fund-flow, ETF, LHB, sector fund flow, dividend, block-trade, and refresh-all endpoints. `dashboard_data_source.py` also uses the same service for market overview data and prewarm logic.

Classification: future provider-design candidate, not an immediate source edit.

### Market Data Package Getter

`market_data_service` is already partially shaped like the route-level DI pattern used by earlier G2 lanes because `market/market_data_request.py` uses `Depends(get_market_data_service)`. It also appears in package exports and adapter/service references.

Classification: provider standardization and graph/text reconciliation candidate.

### TDX Live Market

`tdx.py` already injects `TdxService` through `Depends(get_tdx_service)`, but `dashboard_data_source.py` still uses live-market helper flows. The dashboard path is tied to market-overview summary behavior and should not be folded into a generic service batch.

Classification: separate live-market/control-plane-adjacent provider design.

### Data Service

`data_service` spans indicator cache, strategy indicator helpers, analysis/backtest helpers, and health/control-plane code. A direct route-level migration would mix API endpoint dependencies, strategy runtime helpers, and calculation/test-double concerns.

Classification: data-provider/test-double interface design before implementation.

### Strategy Service

`strategy_service` spans `strategy_management` route code, strategy adapter modules, data adapter modules, and backtest task code. The direct route call count understates the seam because non-route consumers are part of the same lifecycle contract.

Classification: adapter/task seam design before implementation.

### Enhanced Data Service

The exported `get_enhanced_data_service()` exists, but `v1/system/health.py` constructs `EnhancedDataService` through a local `_get_data_service()` helper. This is a control-plane/system-health concern rather than a normal business route provider candidate.

Classification: control-plane provider design, not ordinary route-surface DI.

### Technical Analysis Service

No route-surface consumer was found by the scan. The service is large enough to deserve later service-internal seam work, but it is not the next route-level DI candidate.

Classification: hold.

## Decision

No broad market/data/strategy source implementation is authorized by G2.24.

No single mixed migration should be opened from this packet. The sampled seams cross different ownership and verification boundaries:

- market route provider pattern
- dashboard/live-market data path
- indicator/backtest data-provider seam
- strategy adapter/task seam
- control-plane health/provider seam
- service-internal technical-analysis seam

The next recommended child lane is:

`G2.25 market-data provider design packet`

Scope of the recommended G2.25 packet:

- governance and evidence only
- reconcile `market_data_service` graph/text mismatch
- decide whether `market_data_service` and `market_data_service_v2` should share one provider pattern or remain separate
- list exact future route/function write candidates
- define focused tests, rollback boundary, and GitNexus pre-edit gates
- avoid source edits until the G2.25 packet is reviewed and a later implementation authorization explicitly opens code scope

Future lanes after G2.25 should be separate:

- TDX live-market provider design
- data/indicator/backtest provider interface design
- strategy adapter/task seam design
- control-plane/system-health provider design
- service-internal technical-analysis seam design

## Verification Plan For This Packet

This packet should be accepted only if:

- markdown governance passes for this report and the steward tree
- generated JSON evidence parses
- mainline scope gate passes with only the allowed governance paths
- git diff checks pass
- source guard remains empty for `web/backend`, `src`, and `tests`
- staged GitNexus detect-changes shows no runtime/source blast radius
