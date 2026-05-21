# Backend Control-Plane OpenAPI Docs Decision Package - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

## Status

- Status: decision package prepared for review
- OpenSpec change: `stabilize-backend-control-plane-openapi-docs`
- Parent decision issue: GitHub issue `#92`
- Current HEAD: `15db8ebf5a3d4776a97a1c79d613d644de87cf4c`
- Evidence generated at: `2026-05-21T17:46:41.562727Z`
- Execution mode: governance/evidence only

This package executes the D2.5 evidence tasks for control-plane OpenAPI
documentation stabilization. It refreshes route, OpenAPI, and probe-consumer
evidence, then turns that evidence into a documentation decision package for
human review.

It does not authorize or perform backend source edits, frontend edits, tests,
generated client changes, `docs/api` edits, route behavior changes, OpenAPI
schema or exposure changes, probe URL changes, PM2 commands, service restarts,
implementation issue creation, or movement of issue `#92` to `ready-for-agent`.

## Evidence Artifacts

| Artifact | Role | Notes |
|---|---|---|
| `.planning/codebase/generated/control-plane-openapi-docs-evidence-2026-05-22.json` | Current-head route/OpenAPI/probe evidence | Generated from `app.main` and `app.openapi()` with placeholder governance env; no server or PM2 process was started |
| `openspec/changes/stabilize-backend-control-plane-openapi-docs/tasks.md` | D2.5 task checklist | Updated only for evidence and decision-package tasks that are complete |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Steward tree | Updated to mark D2.5 as decision-package-prepared-for-review |

## Authorization Boundary

The evidence was collected with placeholder environment values needed for
importing the FastAPI application in a governance snapshot. No production
secret, service credential, runtime process, PM2 workflow, or external probe was
used.

The following remain explicitly out of scope:

- adding `/health/readiness`;
- retiring `/api/health/ready`;
- changing `/metrics` registration or schema exposure;
- exposing `/api/strategy-mgmt/{path:path}` in OpenAPI;
- modifying `/api/docs`, `/api/redoc`, or `/openapi.json` routes;
- editing `docs/api` before a reviewed documentation implementation packet;
- moving backup/recovery route ownership out of D2.4;
- moving PM2 stateful workflow execution out of D2.6;
- using this package as an implementation issue or code-change authorization.

## Freshness Gate

| Gate | Result | Evidence |
|---|---:|---|
| `app.main` import | Passed | `app_import_error=null` |
| FastAPI route table generation | Passed | `total_routes=548` |
| `app.openapi()` generation | Passed | `openapi_error=null` |
| OpenAPI path count | `500` | Based on current router registration and `include_in_schema` policy |
| OpenAPI operation count | `536` | Same snapshot as route table |
| OpenAPI schema count | `301` | Same snapshot as route table |
| Duplicate operationIds | `0` | `duplicate_operation_id_count=0` |
| OpenAPI warning count | `0` | `warning_count=0` |
| Focused control-plane duplicate operationIds | `0` | `focused_control_plane_duplicate_operation_id_count=0` |
| Stop condition | Not triggered | Import, route table, and OpenAPI generation all succeeded |

Route table summary:

| Metric | Count |
|---|---:|
| Runtime routes | `548` |
| Schema-visible routes | `536` |
| Hidden runtime routes | `12` |
| Endpoint modules | `99` |
| Duplicate runtime path/methods excluding HEAD/OPTIONS | `1` |

The only duplicate runtime path/method in this snapshot is `GET /metrics`:

| Path | Method | Runtime routes | Schema exposure |
|---|---|---:|---|
| `/metrics` | `GET` | `2` | one hidden `app.main.prometheus_metrics`, one schema-visible `app.api.prometheus_exporter.metrics` |

## Broad Candidate Note

The refreshed broad control/status heuristic reports:

| Metric | Count |
|---|---:|
| Broad control/status candidate routes | `144` |
| Broad schema-exposed candidate routes | `139` |
| Broad hidden runtime candidate routes | `5` |

Earlier planning evidence reported `128` broad candidates and `124`
schema-exposed candidates. The current D2.5 artifact intentionally uses a
broader governance heuristic that also captures docs/schema, prometheus, and
runtime compatibility surfaces. This broad count is a discovery aid, not a
route-mutation scope. The focused taxonomy below is the decision source for
this package.

## Focused Control-Plane Taxonomy

| Surface | Runtime state | OpenAPI state | Classification |
|---|---|---|---|
| `GET /health` | present, `1` route | exposed, `1` operation | platform liveness |
| `GET /health/ready` | present, `1` route | exposed, `1` operation | canonical readiness |
| `GET /api/health/ready` | present, `1` route | exposed, `1` operation | compatibility readiness |
| `/health/readiness` | absent | absent | intentionally absent; do not add without a later approved change |
| `GET /api/health/services` | present, `1` route | exposed, `1` operation | service-health contract surface |
| `GET /api/health/detailed` | present, `1` route | exposed, `1` operation | diagnostic health surface, not platform liveness |
| `GET /api/status` | present, `1` route | exposed, `1` operation | status summary |
| `GET /metrics` | present, `2` routes | one exposed operation plus one hidden runtime route | metrics scrape taxonomy item |
| `/api/docs` | present, `1` route | hidden from OpenAPI | docs UI surface |
| `/api/redoc` | present, `1` route | hidden from OpenAPI | docs UI surface |
| `/openapi.json` | present, `1` route with `GET`/`HEAD` | hidden from OpenAPI | schema retrieval surface |
| `/api/strategy-mgmt/{path:path}` | present, `1` runtime compat route | hidden from OpenAPI | runtime-only hidden compatibility route |

Documentation must preserve two distinct facts for
`/api/strategy-mgmt/{path:path}`: the runtime route still exists, and it remains
hidden from the OpenAPI schema. Schema removal must not be misread as runtime
deletion.

## Probe Consumer Matrix

The refreshed probe consumer scan covered workflows, config, scripts, frontend
source, backend and root tests, docs, Docker compose files, package config, and
PM2 config files.

| Metric | Count |
|---|---:|
| Scanned files | `6060` |
| Files with hits | `1121` |
| Hit lines | `5186` |

Category counts:

| Category | Hit lines |
|---|---:|
| `health` | `1976` |
| `readiness` | `169` |
| `status` | `582` |
| `metrics` | `665` |
| `openapi_docs` | `1644` |
| `strategy_compat` | `150` |

Consumer class counts:

| Consumer class | Hit lines |
|---|---:|
| `docs_governance` | `3602` |
| `frontend` | `86` |
| `ops_config_ci` | `253` |
| `scripts` | `364` |
| `tests` | `881` |

This scan is intentionally broad. It proves that control-plane documentation
changes need a consumer matrix before wording, examples, route exposure policy,
or probe retirement decisions are treated as safe.

## Documentation Decision Routing

| Topic | Routing decision |
|---|---|
| Liveness/readiness/service health/status docs | Eligible for a future docs/API wording package after this decision package is reviewed |
| `/health/readiness` | Keep documented as intentionally absent; no alias creation from this package |
| `/api/health/ready` | Keep documented as compatibility readiness; no retirement from this package |
| `/metrics` | Document hidden plus visible duplicate runtime path/method taxonomy; no registration or schema change |
| `/api/docs`, `/api/redoc`, `/openapi.json` | Treat as docs/schema surfaces, not business API operations |
| `/api/strategy-mgmt/{path:path}` | Treat as runtime-only hidden compatibility route; no schema exposure or deletion |
| Backup/recovery routes | Stay in D2.4 backup route ownership |
| Route/schema/operationId/response-contract changes | Stay in D2.3/F route/OpenAPI governance |
| PM2 stateful workflow execution | Stays in D2.6 PM2 stateful gate approval governance |

## Future Docs/API Implementation Packet

If the reviewed D2.5 package is accepted and a later docs/API lane is approved,
that later lane should be a small documentation implementation packet. The
editable docs/API target set for that future packet should be limited to the
following files unless a new review explicitly expands it:

| Future target file | Role | Current decision |
|---|---|---|
| `docs/api/API_ENDPOINT_DOCUMENTATION.md` | Primary endpoint wording and example surface | Eligible future edit target after review acceptance |
| `docs/api/SWAGGER_UI_GUIDE.md` | Docs UI, Redoc, and schema retrieval wording surface | Eligible future edit target after review acceptance |

The following docs/API artifacts were useful evidence inputs but should not be
hand-edited by the future wording packet:

| Reference artifact | Role | Current decision |
|---|---|---|
| `docs/api/openapi.json` | Historical/generated OpenAPI evidence | Reference only; do not hand-edit from D2.5 |
| `docs/api/openapi/market-data-api-full.json` | Historical/generated API evidence | Reference only; do not hand-edit from D2.5 |
| `docs/api/SWAGGER_ENDPOINTS_2025-11-30.json` | Historical swagger endpoint evidence | Reference only; do not hand-edit from D2.5 |
| `docs/api/API_ARCHITECTURE_DATA_2025-11-30.json` | Historical architecture evidence | Reference only; do not hand-edit from D2.5 |

The future packet should include:

- exact target files;
- exact wording categories for liveness, readiness, service health, diagnostic
  health, status, metrics, docs UI, OpenAPI schema, and runtime-only
  compatibility surfaces;
- examples that distinguish runtime presence from OpenAPI exposure;
- a consumer matrix excerpt for every changed endpoint family;
- verification commands for markdown governance and route/OpenAPI freshness;
- rollback instructions limited to documentation changes;
- non-goals repeating that no route, OpenAPI schema/exposure, probe URL, PM2,
  source, generated client, or test mutation is authorized.

This decision package selects the narrow future target set above, but it does
not edit those files and does not create the future implementation lane.

## Remaining Gates

- Human review of this D2.5 decision package.
- Steward tree update after review acceptance.
- Separate approved docs/API implementation lane, if the maintainer chooses to
  proceed.
- Separate D2.4 backup route ownership evidence execution.
- Separate D2.6 PM2 stateful gate approval policy execution.

## Verification Commands

The following commands are intended for the PR that records this package:

```bash
openspec validate stabilize-backend-control-plane-openapi-docs --strict
python scripts/compliance/markdown_governance_gate.py --root-dir . --format json \
  .planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md \
  docs/reports/quality/backend-control-plane-openapi-docs-decision-package-2026-05-22.md
git diff --cached --check
python governance/mainline/scripts/mainline_scope_gate.py \
  --task-card governance/mainline/task-cards/pr-123.yaml
```
