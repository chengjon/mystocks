# Backend Route / OpenAPI / Probe Refresh - 2026-05-20

> **历史文档说明**:
> 本文件是 `sequence-backend-architecture-unblocks` Task 5.x 的当前工作树证据记录。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: current-head evidence captured
- Change lane: `sequence-backend-architecture-unblocks`
- OpenSpec directory: `openspec/changes/sequence-backend-architecture-unblocks/`
- Task scope: 5.1 route table refresh, 5.2 OpenAPI snapshot refresh, 5.3 probe consumer matrix refresh
- HEAD: `7b097fffd`
- Branch: `wip/root-dirty-20260403`
- Working tree: dirty; artifacts are stale if route/helper/router/probe-consumer files change
- Code changes in this task: none

## Output Artifacts

| Artifact | Path | Summary |
|----------|------|---------|
| Route table | `.planning/codebase/generated/backend-route-table-2026-05-20.json` | `total_routes=548`, `include_in_schema_true=536`, `include_in_schema_false=12`, `endpoint_modules=98` |
| OpenAPI snapshot | `.planning/codebase/generated/route-openapi-snapshot-2026-05-20.json` | `openapi_path_count=500`, operations `536`, duplicate operationIds `0`, warnings `0`, component schemas `294` |
| Probe consumer matrix | `.planning/codebase/generated/probe-consumer-matrix-2026-05-20.json` | scanned files `5782`, hit files `188`, hit lines `611`; category counts: health `278`, openapi `276`, status `50`, `strategy_compat=8` |

## Route Table Finding

The route table refresh found one duplicate path/method pair excluding `HEAD`:

| Path | Method | Count | Endpoint details |
|------|--------|-------|------------------|
| `/metrics` | `GET` | 2 | `app.main.prometheus_metrics` with `include_in_schema=false`; `app.api.prometheus_exporter.metrics` with `include_in_schema=true` |

This is not an OpenAPI duplicate operationId problem because only the exporter route is schema-visible.
It should be handled as a control-plane endpoint taxonomy item, not as evidence that the runtime import
unblock or schema shim closure failed.

The `endpoint_modules=98` field is a route ownership breadth indicator: the 548 runtime routes are contributed
by 98 endpoint modules. It is not a pass/fail gate by itself, but it is useful context for later route
governance because ownership is broad and cannot be audited from a single router file.

## OpenAPI Snapshot Interpretation

The OpenAPI snapshot was generated through `app.openapi()` after the Task 2.x runtime unblock and Task 3.x
schema shim closure. The current snapshot reports:

- paths: `500`
- operations: `536`
- duplicate operationIds: `0`
- warning count captured during `app.openapi()`: `0`

The path count remains a snapshot value tied to current router registration and `include_in_schema` policy.
It must not be treated as a permanent baseline without the artifact timestamp and HEAD.

## Probe Matrix Scope

The probe matrix scans `.github/workflows/`, `config/`, `scripts/`, and root Docker / PM2 / package config
files for health, status, OpenAPI, and strategy compatibility URL patterns.

The matrix is an evidence index for future route governance. It is not an operational truth source and does
not authorize endpoint removal, probe rewiring, PM2 workflow execution, or backend source edits.

The `strategy_compat=8` value is the `category_counts.strategy_compat` key in the JSON artifact. It captures
strategy-management compatibility URL hits and should be interpreted as compatibility-surface evidence, not
as a directive to remove the runtime compatibility route.

## Review Absorption

The paired review file `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20-review.md`
was evaluated after this report was created.

| Review item | Disposition |
|-------------|-------------|
| OpenSpec change lane reported missing | Current worktree check shows `openspec/changes/sequence-backend-architecture-unblocks/` exists; this report now names the directory explicitly |
| `endpoint_modules=98` lacked explanation | Added the route ownership breadth note above |
| `strategy_compat=8` needed clearer artifact mapping | Clarified it as `category_counts.strategy_compat` in the probe matrix JSON |

## Next Gate

Task 5.x unblocks route/OpenAPI governance analysis. Before any endpoint retirement, route rename, schema
exposure change, or probe consumer rewrite, the next task must classify the refreshed findings under an
approved OpenSpec lane and keep control-plane endpoints separate from business API flow assumptions.
