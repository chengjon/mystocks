# Backend Route Dependency Provider Governance Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Task: G2.185 route dependency/provider governance residual decision
Branch: `g2-185-route-dependency-provider-governance-decision`
Base: `wip/root-dirty-20260403`
Current HEAD: `b54e7d043720a8c8bc67ad96f4f7eaad0b23ceba`
Created: 2026-05-27

Boundary: this is a governance decision package only. It does not edit backend
source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2
workflows, OpenSpec state, GitHub issue labels, or service getter/provider
implementations. It does not authorize implementation.

## Purpose

G2.184 selected route dependency/provider governance as the next decision target
after Strategy getter residuals closed by PR `#336` and G2.184 merged by PR
`#337`.

This package classifies the provider residuals so future agents do not treat
active FastAPI dependency providers as removable singleton getter debt.

## Parent State

| Input | State |
|---|---|
| PR `#337` | merged into `wip/root-dirty-20260403` |
| Merge commit | `b54e7d043720a8c8bc67ad96f4f7eaad0b23ceba` |
| Parent evidence | `docs/reports/quality/backend-next-nonstrategy-service-getter-candidate-decision-2026-05-27.md` |
| Parent generated artifact | `.planning/codebase/generated/next-nonstrategy-service-getter-candidate-decision-2026-05-27.json` |

## Evidence Collection

GitNexus was refreshed in this worktree:

```text
gitnexus analyze --with-gitignore
Repository indexed successfully
62,959 nodes | 146,096 edges | 3287 clusters | 300 flows
```

Important caveat: GitNexus upstream impact is useful for normal symbol blast
radius. It does not fully model FastAPI `Depends(...)` route consumers as graph
callers. For provider governance, the static route/provider scan is the consumer
truth.

## Provider Inventory

Scope: `web/backend/app/api`, `web/backend/app/services`, and
`web/backend/app/core` at HEAD `b54e7d043720a8c8bc67ad96f4f7eaad0b23ceba`.

| Provider | Tokens | Depends sites | Owner surface | Classification | Decision |
|---|---:|---:|---|---|---|
| `get_data_source_factory_dependency` | 30 | 18 | `web/backend/app/services/data_source_factory/data_source_factory.py` | active cross-domain service-level FastAPI provider | retain |
| `get_market_data_service_v2_dependency` | 18 | 14 | `web/backend/app/services/market_data_service_v2.py` | active service-level FastAPI provider | retain |
| `get_market_data_service_dependency` | 16 | 7 | `web/backend/app/services/market_data_service/get_market_data_service.py` | active service-level FastAPI provider | retain |
| `get_advanced_analysis_service_dependency` | 16 | 14 | `web/backend/app/services/advanced_analysis_service.py` | active service-level FastAPI provider | retain |
| `get_announcement_service_dependency` | 13 | 11 | `web/backend/app/services/announcement_service.py` | active service-level FastAPI provider | retain |
| `get_stock_search_service_dependency` | 11 | 6 | `web/backend/app/services/stock_search_service/stock_search_service.py` | active service-level FastAPI provider | retain |
| `get_watchlist_service_dependency` | 9 | 7 | `web/backend/app/services/watchlist_service.py` | active service-level FastAPI provider | retain |
| `get_email_service_dependency` | 8 | 6 | `web/backend/app/services/email_service.py` | active service-level FastAPI provider | retain |
| `get_tradingview_service_dependency` | 8 | 6 | `web/backend/app/services/tradingview_widget_service.py` | active service-level FastAPI provider | retain |
| `get_tdx_service_dependency` | 7 | 5 | `web/backend/app/services/tdx_service.py` | active service-level FastAPI provider | retain |
| `get_indicator_registry_dependency` | 5 | 2 | `web/backend/app/services/indicator_registry.py` | active service-level FastAPI provider | retain |

## Route-Local And Constructor Providers

| Provider / getter | Tokens | Depends sites | Surface | Classification | Decision |
|---|---:|---:|---|---|---|
| `get_strategy_service_dependency` | 4 | 3 | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | retained route-local provider fallback | retain under G2.182/G2.183 closure |
| `get_indicator_data_service` | 4 | 2 | `web/backend/app/api/indicators/indicator_cache.py` | route-local provider fallback over public `DataService` getter | retain |
| `get_strategy_indicator_data_service` | 3 | 1 | `web/backend/app/api/v1/strategy/indicators.py` | route-local provider fallback over public `DataService` getter | retain |
| `get_data_source_dependency` | 5 | 3 | dashboard routes | dashboard route-local data-source provider | retain |
| `get_streaming_service` | 25 | n/a | realtime/socket constructor fallback and public getter | public compatibility getter plus constructor fallback consumers | retain; realtime/socket subtrack remains closed |

## GitNexus Impact Cross-Check

The following provider symbols were checked after the G2.185 index refresh:

| Target | GitNexus result | G2.185 interpretation |
|---|---|---|
| `get_data_source_factory_dependency` | LOW, impacted `0` | Graph consumer count does not override active static `Depends(...)` sites. |
| `get_market_data_service_v2_dependency` | LOW, impacted `0` | Retain as active route provider. |
| `get_market_data_service_dependency` | LOW, impacted `0` | Retain as active route provider. |
| `get_advanced_analysis_service_dependency` | LOW, impacted `0` | Retain as active route provider. |
| `get_tdx_service_dependency` | LOW, impacted `0` | Retain as active route provider. |
| `get_strategy_service_dependency` | LOW, impacted `0` | Retain as route-local provider fallback. |
| `get_indicator_registry_dependency` | LOW, impacted `0` | Retain as active route provider. |
| `get_stock_search_service_dependency` | LOW, impacted `0` | Retain as active route provider. |

## Decision

Do not open a backend source implementation lane from G2.185.

Classify the current provider residuals as retained route/provider contracts:

1. FastAPI dependency/provider functions are active route contracts, not
   singleton-retirement candidates.
2. Public `get_*_service` compatibility getters remain valid fallback
   entrypoints unless a later compatibility-retirement package explicitly
   authorizes changing them.
3. Route-local providers may remain route-local when they intentionally
   encapsulate route-specific fallback behavior.
4. GitNexus impact `0` does not imply deletability for provider functions,
   because static route decorators and `Depends(...)` sites are the consumer
   truth.
5. Future provider edits require route-level override tests and OpenAPI/route
   smoke when route signatures or exposure can change.

## Next Gate

Select the next work item as:

```text
G2.186 service lifecycle remaining getter inventory refresh after provider governance
```

G2.186 should remain governance-only unless it finds a real direct
route-body/service-body getter candidate and a separate authorization package is
approved.

Minimum requirements:

1. Rescan all service getter and provider tokens after accepting G2.185.
2. Exclude retained route dependency providers, route-local provider fallbacks,
   constructor fallbacks, package exports, public compatibility getter
   definitions, and test-only references from implementation-candidate counts.
3. Report only remaining direct route-body or service-body singleton getter calls
   that are not provider-governed.
4. If no direct implementation candidates remain, prepare a service lifecycle DI
   closeout or queue-slimming decision package.
5. If a candidate remains, require a separate authorization package before
   source edits.

## Not Authorized

G2.185 does not authorize:

- backend source edits
- backend test edits
- frontend edits
- route/API/OpenAPI exposure changes
- PM2 commands
- OpenSpec change creation or spec edits
- GitHub issue label changes
- deleting, renaming, moving, or privatizing provider functions
- deleting, renaming, moving, or privatizing public compatibility getters
- starting a new implementation lane before G2.186 or a later authorization
  package is reviewed and approved

## Steward Tree Updates

This package updates the split steward tree, not the archived single-file task
tree:

- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/steward-tree/steward-index.json`
- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/tracks/route-openapi-governance.md`
- `.planning/codebase/steward-tree/branch-register.md`
- `.planning/codebase/steward-tree/evidence-index.md`
- `.planning/codebase/steward-tree/completed-ledger.md`

## Verification Plan

Required checks for this governance-only package:

```bash
python -m json.tool .planning/codebase/generated/route-dependency-provider-governance-decision-2026-05-27.json >/dev/null
python -m json.tool .planning/codebase/steward-tree/steward-index.json >/dev/null
python - <<'PY'
import yaml
with open("governance/mainline/task-cards/pr-338.yaml", encoding="utf-8") as f:
    yaml.safe_load(f)
PY
python scripts/compliance/markdown_governance_gate.py --root-dir . --format json \
  .planning/codebase/steward-tree/current-next-gates.md \
  .planning/codebase/steward-tree/tracks/service-lifecycle-di.md \
  .planning/codebase/steward-tree/tracks/route-openapi-governance.md \
  .planning/codebase/steward-tree/branch-register.md \
  .planning/codebase/steward-tree/evidence-index.md \
  .planning/codebase/steward-tree/completed-ledger.md \
  docs/reports/quality/backend-route-dependency-provider-governance-decision-2026-05-27.md
openspec validate migrate-backend-singletons-to-lifecycle-di --strict
git diff --check
```

## Next Gate

Review G2.185. If accepted, start G2.186 as a service lifecycle remaining getter
inventory refresh after provider governance.

Do not start a backend source lane from G2.185.
