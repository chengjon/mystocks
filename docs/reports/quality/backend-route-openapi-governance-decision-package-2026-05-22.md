# Backend Route/OpenAPI Governance Decision Package - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

## Status

- Status: `decision-package-prepared-for-review`
- OpenSpec change: `refresh-backend-route-openapi-governance`
- Parent issue: <https://github.com/chengjon/mystocks/issues/92>
- Current HEAD: `c173bbc8d48d5e20ed5905d698ca39001237198a`
- Evidence generated at: `2026-05-21T17:02:48.078861Z`
- Execution mode: governance/evidence only
- Environment mode: placeholder env for `app.main` import and `app.openapi()`;
  no backend service startup, no PM2 command, and no runtime route mutation

## Authorization Boundary

This package executes the approved D2.3 governance/evidence checklist. It does
not authorize:

- Backend source edits
- Frontend source edits
- Test edits
- Generated client edits
- `docs/api/` edits
- Route path, method, router registration, or behavior changes
- OpenAPI schema, operationId, response contract, or `include_in_schema` changes
- Probe URL rewrites
- PM2 command execution or service restart/recreation
- Implementation issue creation
- Moving issue `#92` to `ready-for-agent`

## Evidence Artifacts

| Evidence | Artifact | Current-HEAD Summary |
|---|---|---|
| Route table | `.planning/codebase/generated/backend-route-table-2026-05-22.json` | routes=`548`, schema-visible=`536`, hidden runtime=`12`, endpoint modules=`99`, duplicate path/method excluding HEAD/OPTIONS=`1` |
| OpenAPI snapshot | `.planning/codebase/generated/route-openapi-snapshot-2026-05-22.json` | paths=`500`, operations=`536`, schemas=`301`, duplicate operationIds=`0`, warnings=`0` |
| Probe consumer matrix | `.planning/codebase/generated/probe-consumer-matrix-2026-05-22.json` | scanned files=`1415`, hit files=`185`, hit lines=`600`; roots are workflows/config/scripts/root Docker/PM2/package config |
| Route consumer contract matrix | `.planning/codebase/generated/route-consumer-contract-matrix-2026-05-22.json` | six D2.3 route groups summarized with consumers and future regression gates |

All artifacts include `git_head`, `generated_at`, and
`stale_if_head_mismatch=true`.

## Freshness Gate

| Gate | Result |
|---|---|
| `app.main` import | Passed under placeholder governance environment |
| Route table generation | Passed |
| `app.openapi()` generation | Passed |
| OpenAPI duplicate operationId warnings | `0` |
| Captured warning count | `0` |
| Stop condition triggered | No |

The app import printed informational startup logs and a GPU dependency fallback
warning (`Numba needs NumPy 2.2 or less. Got NumPy 2.4.`). This package treats
that warning as an environmental smoke note, not as D2.3 route governance
authorization or a route/OpenAPI blocker.

## Route/OpenAPI Snapshot

| Metric | Value |
|---|---:|
| Runtime routes | `548` |
| Schema-visible routes | `536` |
| Hidden runtime routes | `12` |
| Endpoint module count | `99` |
| OpenAPI paths | `500` |
| OpenAPI operations | `536` |
| Component schemas | `301` |
| Duplicate operationIds | `0` |
| OpenAPI warnings | `0` |

The only duplicate runtime path/method excluding `HEAD` and `OPTIONS` remains:

| Path | Method | Routes | Classification |
|---|---|---|---|
| `/metrics` | `GET` | `app.main.prometheus_metrics` hidden from schema; `app.api.prometheus_exporter.metrics` schema-visible | D2.5 control-plane taxonomy item; no runtime or schema change is authorized here |

## D2.3 Ownership Classification

| Class | Routes | Schema Exposed | Decision |
|---|---:|---:|---|
| Trading-owned | `40` | `40` | Keep under unified route/OpenAPI governance; no trading-only implementation lane from this package |
| Trading-adjacent unclassified | `1` | `1` | Keep `/api/v1/advanced-analysis/trading-signals` unclassified until a later accepted owner decision |
| Backup/recovery | N/A | N/A | D2.4 lane, outside D2.3 mutation scope |
| Health/status/docs/probe/control-plane | N/A | N/A | D2.5 lane, outside D2.3 mutation scope |
| PM2/stateful gates | N/A | N/A | D2.6 policy lane, outside D2.3 mutation scope |

### Module Counts

| Endpoint Module | Routes |
|---|---:|
| `app.api.trade.routes` | `7` |
| `app.api.trade.execution_tracking_routes` | `3` |
| `app.api.trade.reconciliation_routes` | `5` |
| `app.api.trading_runtime` | `8` |
| `app.api.tradingview` | `6` |
| `app.api.v1.trading.session` | `5` |
| `app.api.v1.trading.positions` | `6` |
| `app.api.advanced_analysis_api` | `1` |

### Path Group Counts

| Path Group | Routes | OpenAPI Operations | Ownership |
|---|---:|---:|---|
| `/api/v1/trade` | `15` | `15` | trading-owned |
| `/api/trading` | `8` | `8` | trading-owned |
| `/api/tradingview` | `6` | `6` | trading-owned |
| `/api/v1/trading` | `5` | `5` | trading-owned |
| `/api/v1/positions` | `6` | `6` | trading-owned |
| `/api/v1/advanced-analysis/trading-signals` | `1` | `1` | trading-adjacent-unclassified |

All D2.3 candidate routes are currently schema-visible. No runtime-only hidden
D2.3 trading shim was found in this snapshot.

## Probe Consumer Matrix

Probe scan roots were limited to `.github/workflows/`, `config/`, `scripts/`,
and root Docker/PM2/package config files. The broader frontend/test/docs
consumer contract matrix is kept separate.

| Category | Hit Lines |
|---|---:|
| `health` | `262` |
| `metrics` | `140` |
| `openapi_docs` | `144` |
| `status` | `28` |
| `trading` | `26` |
| `backup` | `0` |
| `strategy_compat` | `0` |

| Consumer Class | Hit Lines |
|---|---:|
| `config` | `187` |
| `github_workflows` | `40` |
| `scripts` | `373` |

This matrix is evidence for future route/probe governance. It is not an
operational truth source and does not authorize endpoint removal, probe rewiring,
or PM2 execution.

## Consumer Contract Matrix

The route consumer contract matrix records current group-level consumers. It is
not a parser-level guarantee. Each future implementation lane must inspect caller
parser expectations, OpenAPI examples, query/path/body parameters, and response
shape before changing any route.

| Route Group | Frontend Files | Test Files | Script Files | Ops/CI Files | Docs/Governance Files | Minimum Future Gate |
|---|---:|---:|---:|---:|---:|---|
| `/api/v1/trade` | `4` | `4` | `2` | `0` | `27` | contract parity review before mutation |
| `/api/trading` | `11` | `11` | `3` | `0` | `40` | contract parity review before mutation |
| `/api/tradingview` | `0` | `3` | `0` | `0` | `13` | contract parity review before mutation |
| `/api/v1/trading` | `0` | `1` | `0` | `0` | `10` | contract parity review before mutation |
| `/api/v1/positions` | `0` | `3` | `0` | `0` | `6` | contract parity review before mutation |
| `/api/v1/advanced-analysis/trading-signals` | `1` | `0` | `1` | `1` | `2` | owner decision plus contract parity review before mutation |

Minimum regression checks for any later route implementation lane:

- `app.main` import
- FastAPI route table diff
- `app.openapi()` duplicate operationId check
- Targeted frontend/test consumer parser review
- Contract parity test for path/query/body/response before route mutation

## Decision Routing

| Candidate | Route/OpenAPI Governance Decision |
|---|---|
| Trading-owned groups | Evidence accepted as D2.3 classification input; no action or mutation from this package |
| `/api/v1/advanced-analysis/trading-signals` | Keep trading-adjacent and unclassified; future owner decision required |
| `/metrics` duplicate runtime path/method | Route to D2.5 control-plane docs/taxonomy; no runtime or schema change here |
| Backup/recovery surfaces | Route to D2.4 backup ownership lane |
| Health/readiness/status/docs/probe surfaces | Route to D2.5 control-plane OpenAPI docs stabilization lane |
| PM2/stateful workflow evidence | Route to D2.6 PM2 stateful gate approval policy |
| Compatibility route/schema exposure decisions | Require separate accepted decision with runtime-vs-schema distinction |

## OpenSpec Task Status

Completed in this package:

- Evidence freshness gate
- Route ownership classification
- Consumer contract matrix
- Runtime-vs-schema exposure distinction for D2.3 candidates
- Decision package creation
- Explicit no-implementation boundary

Still pending:

- Human review of this decision package
- Steward tree update after review acceptance
- Any implementation lane, write scope, tests, or rollback plan for future route
  changes

## Next Gate

Review this package. If accepted, record the review result in the steward tree
and only then decide whether any separate child lane is needed. Do not create
implementation issues or edit source from this package alone.
