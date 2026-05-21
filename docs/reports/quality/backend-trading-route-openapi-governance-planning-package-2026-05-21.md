# Backend Trading Route OpenAPI Governance Planning Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

- Date: 2026-05-21
- Status: D2.3 planning package prepared; no route implementation authorized
- Parent issue: <https://github.com/chengjon/mystocks/issues/92>
- Track: D2.3 trading route ownership under unified route/OpenAPI governance
- Base HEAD: `c24f430167bbfc9cf573121f30d817b2c2db875b`
- Prepared at: `2026-05-21T03:21:58Z`

## Boundary

This package is planning and evidence only.

It does not modify backend route modules, does not change route registration,
does not change OpenAPI schema exposure, does not edit frontend consumers, does
not edit tests, does not create or modify OpenSpec change/spec files, does not
run PM2, and does not move issue `#92` or any downstream child to
`ready-for-agent`.

## Decision Question

Should trading route ownership be handled by the unified route/OpenAPI
governance lane instead of a standalone trading-only implementation lane?

Recommended answer for this package: yes, keep trading under unified
route/OpenAPI governance and require a separate approved proposal or
implementation issue before any route mutation.

## Why This Exists

Issue `#92` downstream splitting accepted three decisions:

- `TechnicalPatternDetectionService` is the first DI design pilot.
- trading route ownership folds into unified route/OpenAPI governance.
- backup route ownership remains a dedicated proposal candidate.

D2.3 records the trading decision as a planning package. It converts the
decision into a concrete route/OpenAPI evidence shape without approving route
edits.

## Current Route Evidence Snapshot

The 2026-05-18 domain-router reconciliation report counted `trading` as
`31` runtime routes and `31` schema-exposed routes. The refreshed D2.3 smoke
uses a broader trading candidate heuristic and should be treated as the current
planning snapshot for this package.

| Evidence | Result |
|---|---|
| Current HEAD | `c24f430167bbfc9cf573121f30d817b2c2db875b` |
| App import smoke | `app.main` imported with placeholder local env |
| Runtime routes | `548` |
| OpenAPI paths | `500` |
| Trading candidate routes | `41` |
| Trading schema-exposed routes | `41` |
| Trading schema path count | `32` |
| Trading duplicate operationIds | `0` |

The `31` to `41` difference is not evidence of a route deletion or route
creation by D2.3. It reflects a refreshed candidate scope that includes trade
execution tracking, runtime/status routes, v1 position/session surfaces, and one
trading-adjacent advanced-analysis route that still needs ownership
classification.

## Candidate Ownership Classes

| Class | Current endpoint modules | Planning treatment |
|---|---|---|
| Core trade package | `app.api.trade.routes`, `app.api.trade.execution_tracking_routes`, `app.api.trade.reconciliation_routes` | Candidate for canonical trading route ownership review |
| Runtime trading API | `app.api.trading_runtime` | Needs route/OpenAPI taxonomy before route mutation |
| Chart and widget API | `app.api.tradingview` | Fold into unified route/OpenAPI governance; do not handle as isolated trading cleanup |
| v1 trading API | `app.api.v1.trading.session`, `app.api.v1.trading.positions` | Needs path and consumer parity review |
| Trading-adjacent candidate | `app.api.advanced_analysis_api` | Needs explicit classification before being treated as trading-owned |

## Current Module And Prefix Snapshot

| Endpoint module | Routes | Schema exposed |
|---|---:|---:|
| `app.api.trade.routes` | 7 | 7 |
| `app.api.trade.execution_tracking_routes` | 3 | 3 |
| `app.api.trade.reconciliation_routes` | 5 | 5 |
| `app.api.trading_runtime` | 8 | 8 |
| `app.api.tradingview` | 6 | 6 |
| `app.api.v1.trading.session` | 5 | 5 |
| `app.api.v1.trading.positions` | 6 | 6 |
| `app.api.advanced_analysis_api` | 1 | 1 |

| Path group | Routes | Schema exposed |
|---|---:|---:|
| `/api/v1/trade` | 15 | 15 |
| `/api/trading/status` | 1 | 1 |
| `/api/trading/start` | 1 | 1 |
| `/api/trading/stop` | 1 | 1 |
| `/api/trading/strategies` | 3 | 3 |
| `/api/trading/market` | 1 | 1 |
| `/api/trading/risk` | 1 | 1 |
| `/api/tradingview/chart` | 1 | 1 |
| `/api/tradingview/mini-chart` | 1 | 1 |
| `/api/tradingview/ticker-tape` | 1 | 1 |
| `/api/tradingview/market-overview` | 1 | 1 |
| `/api/tradingview/screener` | 1 | 1 |
| `/api/tradingview/symbol` | 1 | 1 |
| `/api/v1/trading` | 5 | 5 |
| `/api/v1/positions` | 6 | 6 |
| `/api/v1/advanced-analysis` | 1 | 1 |

## Consumer Matrix Snapshot

Tracked-file string scans for `/api/v1/trade`, `/api/trading`,
`/api/tradingview`, `/api/v1/trading`, and `/api/v1/positions` found the
following planning surface.

| Consumer class | Hit files | Hits | Planning impact |
|---|---:|---:|---|
| Backend source | 4 | 12 | `router_registry`, `VERSION_MAPPING`, and contract route references must be reviewed before route mutation |
| Frontend source | 15 | 66 | Frontend consumer contract parity is a hard future gate |
| Tests | 24 | 150 | Existing test expectations must be classified before route edits |
| Scripts | 4 | 24 | Operational and generated tooling references must be included in the consumer matrix |
| Docs and governance | 77 | 431 | Historical references must be separated from active consumers |
| Other tracked files | 14 | 19 | Needs review before implementation planning |

This matrix is intentionally a planning snapshot. It is not enough to authorize
route edits because it has not yet classified active runtime callers, historical
references, generated artifacts, or stale snapshots.

## Required Future Evidence Before Any Route Mutation

A future trading route implementation proposal or issue must include:

- current FastAPI route table with endpoint module, method, path, and
  `include_in_schema`;
- current `app.openapi()` snapshot with path count, operation count, warnings,
  and duplicate operationId check;
- path-prefix taxonomy for `/api/v1/trade`, `/api/trading`,
  `/api/tradingview`, `/api/v1/trading`, and `/api/v1/positions`;
- `router_registry`, `VERSION_MAPPING`, and `docs/FUNCTION_TREE.md` status;
- frontend, backend, test, script, PM2, Docker, CI, and docs consumer matrix;
- contract parity matrix covering path, query parameters, response shape,
  caller parser expectations, OpenAPI examples, and minimal regression tests;
- explicit treatment for trading-adjacent routes such as
  `/api/v1/advanced-analysis/trading-signals`;
- include-in-schema exposure policy and compatibility route policy;
- rollback and compatibility strategy for any renamed, hidden, or retired route.

## Governance Recommendation

Trading route ownership should stay under the unified route/OpenAPI governance
parent, currently referred to by the candidate branch name
`refresh-backend-route-openapi-governance`.

D2.3 should not create a trading-only implementation lane. The next approved
unit should be either:

- an evidence-only OpenSpec proposal that formalizes route/OpenAPI governance
  requirements; or
- a separate implementation issue after route/OpenAPI evidence and consumer
  parity are accepted by a human reviewer.

Backup route ownership remains outside D2.3 and should continue as its own D2.4
candidate because backup routes have different ownership, security, and
operational boundaries.

## Explicit Non-Authorizations

D2.3 does not authorize:

- moving any route module;
- renaming or retiring any path;
- changing `include_in_schema`;
- changing operationIds;
- editing `web/backend/app/api/**`;
- editing `web/frontend/**`;
- editing tests or fixtures;
- opening a broad route implementation issue;
- moving issue `#92` or any downstream item to `ready-for-agent`.

## Next Gate

Human review of this D2.3 package.

If accepted, the maintainer should decide whether to create a separate
route/OpenAPI governance OpenSpec proposal or a narrower implementation issue.
Until that decision exists, route behavior remains locked.
