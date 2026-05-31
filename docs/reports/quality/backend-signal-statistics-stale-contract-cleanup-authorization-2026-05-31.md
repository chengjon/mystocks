# G2.264 Signal Statistics Stale Contract Cleanup Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: review input
- Prepared at: `2026-05-31T10:43:44+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `795d2b9f50c3e483876f1b4ec484fbf9c1d9e513`
- Parent: G2.263 / PR `#416` merged at `795d2b9f50c3e483876f1b4ec484fbf9c1d9e513`
- Scope: no-source cleanup authorization for stale signal statistics contract artifacts

Boundary note: this document records a governance authorization package only. It does not authorize immediate edits to docs/api, tests, backend source, frontend, OpenSpec, PM2 state, route registration, provider injection, source retirement, or PR merges.

## Executive Authorization

G2.264 authorizes a future path-limited cleanup implementation lane: **G2.265 stale signal statistics contract cleanup implementation**.

G2.264 itself does not edit any stale artifact. It defines the exact future lane boundary so the next agent cannot reinterpret dormant route-shaped code as active runtime API truth.

Future G2.265 may touch only these paths:

- `docs/api/openapi.yaml`
- `docs/api/task_plan_signal_monitoring_phase2_extended.md`
- `docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md`
- `docs/architecture/DESIGN_METHODOLOGY_AND_TOOLCHAIN_ANALYSIS.md`
- `tests/unit/test_signal_monitoring_integration.py`

Future G2.265 must not edit `web/backend/app/api/signal_monitoring/get_signal_statistics.py`, register routes, inject providers, retire source, edit frontend, edit OpenSpec, or run PM2/stateful gates.

## Current Runtime Truth

| Field | Value |
|---|---:|
| Runtime routes | 548 |
| Current `app.openapi()` paths | 500 |
| Target OpenAPI paths | 0 |
| Duplicate operation IDs | 0 |

The stale references below are not current runtime OpenAPI truth.

## Authorized Artifact Matrix

| Artifact | Lines | `/api/signals/statistics` refs | `/api/signals/active` refs | strategy detailed health refs |
|---|---:|---:|---:|---:|
| `docs/api/openapi.yaml` | 249 | 1 | 1 | 0 |
| `docs/api/task_plan_signal_monitoring_phase2_extended.md` | 68 | 1 | 1 | 0 |
| `docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md` | 906 | 5 | 4 | 0 |
| `docs/architecture/DESIGN_METHODOLOGY_AND_TOOLCHAIN_ANALYSIS.md` | 1057 | 2 | 0 | 0 |
| `tests/unit/test_signal_monitoring_integration.py` | 662 | 1 | 1 | 0 |

## Future G2.265 Allowed Actions

- Remove or annotate stale `docs/api/openapi.yaml` entries for `/api/signals/statistics` and `/api/signals/active` if they remain absent from generated `app.openapi()`.
- Mark planning/design/operations references as historical, deferred, or non-runtime truth instead of current endpoint documentation.
- Update `tests/unit/test_signal_monitoring_integration.py` so dormant paths are not asserted as active runtime endpoints unless the assertion is explicitly historical/deferred.
- Keep all edits path-limited and line-focused around the stale endpoint references.

## Future G2.265 Forbidden Actions

- No `web/backend/**` source edits.
- No route registration or provider injection.
- No source retirement or archive.
- No frontend, config, script, OpenSpec, or PM2/runtime state changes.
- No broad rewrite of the authorized documents beyond stale contract references.

## Acceptance Criteria For Future G2.265

- Current `app.openapi()` remains the runtime truth source.
- If target paths remain absent from generated OpenAPI, docs/api must not present them as active runtime endpoints.
- Tests must not imply these dormant paths are active runtime routes unless explicitly marked historical/deferred.
- Duplicate operation IDs remain 0.
- Any cleanup report must state that source retirement and route registration remain separate future decisions.

## Verification Notes

Planned verification for this PR:

- markdown governance gate on changed Markdown files
- OpenSpec strict validation for `migrate-backend-singletons-to-lifecycle-di`
- mainline scope gate with this PR task card
- GitNexus detect-changes attempt, with CLI fallback if MCP transport remains unavailable
- `git diff --check`
