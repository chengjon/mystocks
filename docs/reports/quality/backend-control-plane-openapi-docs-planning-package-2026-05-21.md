# Backend Control-Plane OpenAPI Docs Planning Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

- Date: 2026-05-21
- Status: D2.5 planning package prepared; no runtime or docs/API implementation authorized
- Parent issue: <https://github.com/chengjon/mystocks/issues/92>
- Track: D2.5 control-plane OpenAPI docs stabilization residual closeout
- Base HEAD: `b39b7b3ee07d9b8630feeba1b581d815a84a2ddb`
- Prepared at: `2026-05-21T04:32:05Z`

## Boundary

This package is planning and evidence only.

It does not modify backend route modules, does not change route registration,
does not change OpenAPI schema exposure, does not edit `docs/api/`, does not edit
frontend consumers, does not edit tests, does not create or modify OpenSpec
change/spec files, does not run PM2, and does not move issue `#92` or any
downstream child to `ready-for-agent`.

## Decision Question

What remains for control-plane OpenAPI documentation stabilization after the
health/status consolidation, route/OpenAPI refresh, D2.3 trading planning, and
D2.4 backup planning work?

Recommended answer for this package: treat the remaining work as a dedicated
control-plane documentation/probe governance candidate, not as route
implementation. The next action should standardize documentation taxonomy and
probe consumer evidence before any runtime route or OpenAPI exposure change.

## Why This Exists

D2.5 closes the residual planning gap for control-plane interfaces:

- platform liveness/readiness probes;
- service health and detailed health surfaces;
- status and metrics endpoints;
- OpenAPI/docs UI endpoints;
- runtime-only compatibility routes;
- probe consumers in CI, scripts, config, PM2, frontend smoke, and generated docs.

This is the documentation-stabilization counterpart to the earlier
`consolidate-backend-health-endpoints` and route/OpenAPI refresh evidence. It
does not archive or implement an OpenSpec change.

## Current Route Evidence Snapshot

The current FastAPI route table and `app.openapi()` snapshot were collected by
importing `app.main` with local placeholder environment variables.

| Evidence | Result |
|---|---|
| Current HEAD | `b39b7b3ee07d9b8630feeba1b581d815a84a2ddb` |
| App import smoke | `app.main` imported with placeholder local env |
| Runtime routes | `548` |
| OpenAPI paths | `500` |
| Broad control/status candidate routes | `128` |
| Broad control/status schema-exposed routes | `124` |
| Broad control/status hidden routes | `4` |
| Focused control-plane duplicate operationIds | `0` |
| Focused absent route | `/health/readiness` |

The broad count intentionally includes many business-domain `health`, `status`,
`metrics`, and `monitoring` endpoints. It is useful for documentation taxonomy,
but it is not a route mutation scope.

## Focused Control-Plane Taxonomy

| Class | Current route(s) | Schema exposure | Planning treatment |
|---|---|---|---|
| Platform liveness | `GET /health` | exposed | canonical platform liveness |
| Canonical readiness | `GET /health/ready` | exposed | canonical readiness |
| Compatibility readiness | `GET /api/health/ready` | exposed | compatibility readiness; keep consumer matrix before retirement discussion |
| Disallowed readiness alias | `/health/readiness` | absent | remains intentionally absent |
| System service health | `GET /api/health/services` | exposed | service-health contract surface |
| Detailed health | `GET /api/health/detailed` | exposed | diagnostic surface; not a platform liveness probe |
| Status summary | `GET /api/status` | exposed | status summary surface under metrics router |
| Metrics scrape | `GET /metrics` | one hidden runtime route plus one exposed exporter route | duplicate runtime path/method needs explicit docs taxonomy |
| API metrics | `GET /api/metrics`, `GET /api/metrics/health`, `GET /metrics/health`, `GET /metrics/list` | exposed | metrics/control-plane docs surface |
| API docs UI | `GET /api/docs`, `GET /api/redoc` | hidden | docs UI routes; not OpenAPI operations |
| OpenAPI schema | `GET/HEAD /openapi.json` | hidden | schema retrieval route; not part of generated operation set |
| Runtime compat redirect | `/api/strategy-mgmt/{path:path}` | hidden | runtime-only compatibility redirect; keep hidden from OpenAPI |
| Service-specific health | `/api/backup-recovery/health`, `/api/socketio-status` | exposed | service-specific status surfaces; classify separately from platform probes |

## Focused Route Details

| Method | Path | Endpoint module | Endpoint name | include_in_schema |
|---|---|---|---|---|
| `GET` | `/health` | `app.main` | `health_check` | `true` |
| `GET` | `/health/ready` | `app.main` | `readiness_check` | `true` |
| `GET` | `/api/health/ready` | `app.main` | `readiness_check` | `true` |
| `GET` | `/api/health/services` | `app.api.health` | `check_system_health` | `true` |
| `GET` | `/api/health/detailed` | `app.api.health` | `detailed_health_check` | `true` |
| `GET` | `/api/status` | `app.api.metrics` | `basic_status` | `true` |
| `GET` | `/metrics` | `app.main` | `prometheus_metrics` | `false` |
| `GET` | `/metrics` | `app.api.prometheus_exporter` | `metrics` | `true` |
| `GET` | `/api/metrics` | `app.api.metrics` | `prometheus_metrics` | `true` |
| `GET` | `/metrics/health` | `app.api.prometheus_exporter` | `metrics_health` | `true` |
| `GET` | `/metrics/list` | `app.api.prometheus_exporter` | `metrics_list` | `true` |
| `GET` | `/api/metrics/health` | `app.api.metrics` | `health_check` | `true` |
| `GET` | `/api/docs` | `app.main` | `custom_swagger_ui_html` | `false` |
| `GET` | `/api/redoc` | `app.main` | `custom_redoc_html` | `false` |
| `GET/HEAD` | `/openapi.json` | `fastapi.applications` | `openapi` | `false` |
| `GET/POST/PUT/PATCH/DELETE` | `/api/strategy-mgmt/{path:path}` | `app.api._strategy_mgmt_compat` | `redirect_to_canonical` | `false` |
| `GET` | `/api/backup-recovery/health` | `app.api.backup_recovery_secure.cleanup_old_backups` | `backup_service_health` | `true` |
| `GET` | `/api/socketio-status` | `app.main` | `socketio_status` | `true` |

## Current Residual Findings

| Finding | Current fact | D2.5 treatment |
|---|---|---|
| `/health/readiness` | absent from runtime routes; only historical/governance text hits found | keep documented as intentionally absent |
| `/metrics` duplicate runtime path/method | `app.main` hidden route and `app.api.prometheus_exporter` exposed route both register `GET /metrics` | document as control-plane taxonomy item before any change |
| OpenAPI path count | `500` | snapshot tied to current router registration and `include_in_schema` policy |
| operationIds | focused control-plane duplicate operationIds `0` | no operationId remediation authorized by D2.5 |
| strategy compat wildcard | runtime route exists, `include_in_schema=false` | document as runtime-only hidden compat route |
| docs UI and schema routes | `/api/docs`, `/api/redoc`, `/openapi.json` hidden from operation schema | classify as docs/schema surfaces, not business API operations |

## Probe Consumer Matrix Snapshot

Tracked-file string scans found the following planning surface.

| Pattern | GitHub workflows | Config | Scripts | Backend source | Frontend source | Tests | Docs/governance | Other |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `/health/ready` | 7 files / 14 hits | 0 / 0 | 7 / 16 | 1 / 2 | 2 / 5 | 8 / 19 | 56 / 346 | 29 / 33 |
| `/api/health/ready` | 0 / 0 | 0 / 0 | 5 / 8 | 1 / 1 | 2 / 4 | 6 / 10 | 37 / 179 | 23 / 25 |
| `/api/health/services` | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 22 / 44 | 1 / 1 |
| `/health/readiness` | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 7 / 20 | 0 / 0 |
| `/metrics` | 1 / 10 | 18 / 71 | 22 / 63 | 12 / 20 | 8 / 10 | 57 / 115 | 166 / 570 | 28 / 88 |
| `/api/status` | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 8 / 12 | 1 / 1 |
| `/api/strategy-mgmt` | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 4 | 2 / 2 | 2 / 33 | 29 / 87 | 5 / 56 |
| `/openapi.json` | 1 / 1 | 0 / 0 | 3 / 4 | 5 / 10 | 0 / 0 | 9 / 20 | 165 / 235 | 28 / 37 |
| `/api/docs` | 1 / 2 | 0 / 0 | 12 / 18 | 4 / 15 | 1 / 1 | 7 / 7 | 57 / 94 | 26 / 36 |

These are file/hit counts, not active-consumer counts. A future docs
standardization batch must classify active runtime consumers, historical
references, generated snapshots, stale reports, and examples separately.

## Prior Evidence To Preserve

| Evidence | Role in D2.5 |
|---|---|
| `backend-health-status-implementation-boundary-2026-05-18.md` | records approved health/readiness taxonomy and intentionally absent `/health/readiness` |
| `backend-health-status-openapi-stabilization-2026-05-18.md` | records OpenAPI path count `500`, duplicate operationId warnings `0`, and hidden strategy compat wildcard |
| `backend-health-status-pm2-gate-2026-05-18.md` | records approved PM2 gate evidence and successful live probes |
| `backend-route-openapi-probe-refresh-2026-05-20.md` | records current-head route table, OpenAPI snapshot, probe matrix, and `/metrics` duplicate runtime path/method |
| `backend-route-openapi-probe-refresh-2026-05-20-review.md` | confirms `/metrics` duplicate is a control-plane taxonomy item and not an OpenAPI duplicate operationId issue |

## Required Future Evidence Before Any Docs/API Or Runtime Change

A future control-plane docs implementation proposal or issue must include:

- current FastAPI route table with endpoint module, method, path, and
  `include_in_schema`;
- current `app.openapi()` snapshot with path count, operation count, warnings,
  and duplicate operationId check;
- probe consumer matrix covering GitHub workflows, config, scripts, PM2,
  Docker/Kubernetes, frontend smoke, tests, docs, and generated artifacts;
- explicit taxonomy for liveness, readiness, service health, detailed health,
  status summary, metrics scrape, docs UI, schema retrieval, and runtime-only
  compatibility redirects;
- docs/API artifact freshness check before editing any docs/API generated file;
- decision on whether docs should describe `/metrics` as hidden+visible duplicate
  runtime path, or whether a future runtime proposal should remove one side;
- decision on whether `/api/health/services` and `/api/health/detailed` are
  public contract docs or internal diagnostic docs;
- no route rename, alias addition, or `include_in_schema` change without a
  separate approved implementation lane.

## Governance Recommendation

Control-plane OpenAPI docs stabilization should remain a dedicated planning
candidate, currently referred to by the future candidate name
`stabilize-backend-control-plane-openapi-docs`.

No git branch, GitHub issue, or OpenSpec change with that name exists or is
required by this D2.5 package. If future implementation begins, the actual git
branch, OpenSpec change-id, and issue identifier must be created and recorded at
that time.

D2.5 should not be folded into D2.3 trading route planning or D2.4 backup route
ownership. It is a cross-cutting documentation/probe governance lane.

## Explicit Non-Authorizations

D2.5 does not authorize:

- adding `/health/readiness`;
- retiring `/api/health/ready`;
- changing `/metrics` runtime registration;
- changing `include_in_schema`;
- changing operationIds;
- editing `web/backend/app/**`;
- editing `web/frontend/**`;
- editing tests or fixtures;
- editing `docs/api/**`;
- creating or archiving OpenSpec changes;
- running PM2 stateful gates;
- moving issue `#92` or any downstream item to `ready-for-agent`.

## Next Gate

Human review of this D2.5 package.

If accepted, the maintainer should decide whether to create a separate
control-plane OpenAPI docs stabilization OpenSpec proposal or a narrower
documentation implementation issue. Until that decision exists, control-plane
route behavior and docs/API artifacts remain locked.
