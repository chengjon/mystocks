# Backend Service Lifecycle Remaining Getter Inventory Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: decision package for review
- Prepared at: `2026-05-27T22:01:42+08:00`
- Base HEAD checked: `720248521d705af067d0a2600710444e439d7605`
- Previous gate: G2.185 route dependency/provider governance decision
- Previous PR: `#338`, merged at `720248521d705af067d0a2600710444e439d7605`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`

Boundary note: this report is evidence and scheduling guidance only. It does not
authorize backend source edits, route signature changes, test edits, OpenSpec
proposal creation, issue label changes, provider deletion, or compatibility
getter retirement.

## Purpose

G2.185 closed the provider-governance ambiguity by classifying active FastAPI
dependency providers as retained route contracts. G2.186 refreshes the remaining
getter inventory after that decision so that provider functions, route-local
fallbacks, constructor fallbacks, package exports, public getter definitions,
and test-only references do not inflate the next implementation backlog.

## Scan Method

The scan covered:

- `web/backend/app/api`
- `web/backend/app/services`

The scanner counted direct `get_*(` calls and excluded:

- function definitions
- import statements
- FastAPI `Depends(...)` provider references
- names ending in `_dependency`
- method calls through object receivers
- comments and decorators

This keeps the result focused on route-body and service-body direct getter
usage. It is still an inventory, not an implementation authorization.

## Inventory Summary

| Metric | Count |
|---|---:|
| Python files scanned | 371 |
| Direct `get_*` names after exclusion | 111 |
| Direct `get_*` calls after exclusion | 296 |

| Bucket | Names | Calls | Disposition |
|---|---:|---:|---|
| Infra / control-plane / session accessors | 18 | 78 | Not service lifecycle source candidates |
| Factory / adapter / helper / root facade | 27 | 101 | Requires owner-specific facade or adapter decisions |
| Manual review residue | 44 | 50 | Must not become backlog automatically |
| Cache / messaging accessors | 3 | 12 | Cache/messaging lifecycle track, not generic service DI |
| Realtime / streaming track | 10 | 12 | Already governed by realtime streaming/socket track |
| Service singleton review | 10 | 43 | Candidate-level classification below |

## Service Singleton Review Candidates

| Getter | Direct calls | First location | GitNexus risk | Direct impact | Classification | Disposition |
|---|---:|---|---|---:|---|---|
| `get_data_quality_monitor` | 20 | `web/backend/app/api/data_quality.py:112` | HIGH | 20 | Data-quality and adapter cross-cutting track | Separate design/authorization package required; no G2.186 source lane |
| `get_integrated_services` | 7 | `web/backend/app/services/__init__.py:259` | MEDIUM | 7 | Root facade compatibility | Retain until a root facade compatibility retirement package exists |
| `get_unified_data_service` | 5 | `web/backend/app/services/unified_data_service.py:587` | MEDIUM | 5 | Root facade / service self-wrapper | Retain; not a route-body singleton implementation candidate |
| `get_prewarming_strategy` | 3 | `web/backend/app/api/_cache_prewarming_routes.py:118` | HIGH | 3 | Control-plane cache prewarming | Route/control-plane track; not a generic service lifecycle pilot |
| `get_data_service` | 2 | `web/backend/app/api/v1/strategy/indicators.py:30` | LOW | 2 | Indicator/data route-local provider fallback | Retain under provider governance unless later authorization changes it |
| `get_execution_tracking_evidence_service` | 2 | `web/backend/app/api/trade/execution_tracking_routes.py:364` | HIGH | 2 | Trade evidence route track | Separate trade/evidence authorization package required |
| `get_market_data_service_v2` | 1 | `web/backend/app/services/market_data_service_v2.py:673` | LOW | 1 | Constructor install fallback | Retain as installation fallback |
| `get_stop_loss_execution_service` | 1 | `web/backend/app/api/risk/stop_loss.py:51` | LOW | 0 | Risk stop-loss route service getter | Recommended next narrow authorization-package candidate |
| `get_stop_loss_history_service` | 1 | `web/backend/app/api/risk/stop_loss.py:44` | LOW | 1 | Risk stop-loss route service getter | Recommended next narrow authorization-package candidate |
| `get_tdx_service` | 1 | `web/backend/app/services/tdx_service.py:290` | LOW | 1 | Constructor install fallback | Retain; Dashboard/TDX route work remains separate |

## Decision

G2.186 does not open a backend source implementation lane.

The refreshed inventory shows that the largest remaining direct getter surfaces
are either cross-cutting, root-facade shaped, provider fallback shaped, or owned
by a different governance track. The only narrow next candidate is the stop-loss
risk route pair:

- `get_stop_loss_history_service`
- `get_stop_loss_execution_service`

The recommended next work item is:

`G2.187 risk stop-loss route service provider authorization package`

That package should remain design/authorization only until reviewed. It should
define the exact route file scope, tests, rollback plan, GitNexus pre-edit
checks, and route contract checks before any source edit is allowed.

## Blocked Actions

This package explicitly forbids:

- editing `web/backend/**`
- editing `src/**`
- editing tests
- deleting or renaming any getter
- treating `get_data_quality_monitor` as a quick source lane
- treating root facade getters as unused
- changing FastAPI provider behavior
- opening G2.187 source implementation before its authorization package is accepted

## Verification

- `gitnexus analyze --with-gitignore`
  - `62,963 nodes`
  - `146,095 edges`
  - `300 flows`
- Direct getter scanner:
  - files=`371`
  - direct names=`111`
  - direct calls=`296`
- GitNexus impact samples:
  - `get_data_quality_monitor`: HIGH, direct=`20`, processes=`2`
  - `get_integrated_services`: MEDIUM, direct=`7`
  - `get_unified_data_service`: MEDIUM, direct=`5`
  - `get_prewarming_strategy`: HIGH, direct=`3`, processes=`3`
  - `get_data_service`: LOW, direct=`2`
  - `get_execution_tracking_evidence_service`: HIGH, direct=`2`, processes=`3`
  - `get_stop_loss_history_service`: LOW, direct=`1`
  - `get_stop_loss_execution_service`: LOW, direct=`0`
  - `get_market_data_service_v2`: LOW, direct=`1`
  - `get_tdx_service`: LOW, direct=`1`

## Review Questions

- Should G2.187 focus on the stop-loss route pair as the next narrow
  authorization package?
- Should `get_data_quality_monitor` be deferred to a larger data-quality and
  adapter governance package?
- Should root facade compatibility retirement remain blocked behind a separate
  root-facade decision package?
