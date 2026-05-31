# G2.265 Signal Statistics Stale Contract Cleanup Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: review input
- Prepared at: `2026-05-31T10:58:01+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `fe1927818309efb2c1de3a9c1e1128e9b456053e`
- Parent: G2.264 / PR `#417` merged at `fe1927818309efb2c1de3a9c1e1128e9b456053e`
- Scope: path-limited stale signal statistics contract cleanup implementation

Boundary note: this report records a path-limited docs/test cleanup implementation. It does not authorize backend source edits, route registration, provider injection, source retirement, frontend changes, OpenSpec changes, PM2 commands, or PR merges.

## What Changed

G2.265 cleaned stale contract artifacts for dormant signal-statistics endpoints while keeping runtime behavior unchanged.

Touched authorized paths only:

- `docs/api/openapi.yaml`
- `docs/api/task_plan_signal_monitoring_phase2_extended.md`
- `docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md`
- `docs/architecture/DESIGN_METHODOLOGY_AND_TOOLCHAIN_ANALYSIS.md`
- `tests/unit/test_signal_monitoring_integration.py`

No `web/backend/**`, frontend, OpenSpec, config, script, route registration, provider injection, source retirement, or PM2/runtime state change was made.

## Runtime Truth

| Field | Value |
|---|---:|
| Runtime routes | 548 |
| Current `app.openapi()` paths | 500 |
| Target OpenAPI paths | 0 |
| Duplicate operation IDs | 0 |

The target endpoints remain dormant. This cleanup only makes docs/tests stop presenting them as active runtime endpoints.

## Cleanup Result

| Artifact | Cleanup |
|---|---|
| `docs/api/openapi.yaml` | Removed stale active path blocks for the dormant signal statistics endpoints from the hand-maintained snapshot. |
| `docs/api/task_plan_signal_monitoring_phase2_extended.md` | Marked the Phase 2.4 endpoints as historical/deferred and not current `app.openapi()` truth. |
| `docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md` | Marked signal statistics endpoint references as historical/deferred examples or plans, not runtime contract. |
| `docs/architecture/DESIGN_METHODOLOGY_AND_TOOLCHAIN_ANALYSIS.md` | Marked the example and test snippet as historical/deferred and changed the illustrative assertion to current 404 behavior. |
| `tests/unit/test_signal_monitoring_integration.py` | Changed two tests from active `200` assertions to explicit dormant-route `404` assertions. |

## Reference Counts After Cleanup

| Artifact | `/api/signals/statistics` | `/api/signals/active` | Strategy detailed health |
|---|---:|---:|---:|
| `docs/api/openapi.yaml` | 0 | 0 | 0 |
| `docs/api/task_plan_signal_monitoring_phase2_extended.md` | 1 | 1 | 0 |
| `docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md` | 5 | 4 | 0 |
| `docs/architecture/DESIGN_METHODOLOGY_AND_TOOLCHAIN_ANALYSIS.md` | 3 | 0 | 0 |
| `tests/unit/test_signal_monitoring_integration.py` | 1 | 1 | 0 |

Remaining references outside `docs/api/openapi.yaml` are intentionally retained as historical/deferred references or explicit dormant-route tests.

## Red / Green Evidence

Before cleanup:

- `test_signal_statistics_endpoint` failed because runtime returned `404` while the stale test expected `200`.
- `test_active_signals_endpoint` failed because runtime returned `404` while the stale test expected `200`.

After cleanup:

- `tests/unit/test_signal_monitoring_integration.py::TestSignalMonitoringAPI::test_signal_statistics_endpoint`: passed.
- `tests/unit/test_signal_monitoring_integration.py::TestSignalMonitoringAPI::test_active_signals_endpoint`: passed.

## Verification

Completed before PR:

- Targeted stale endpoint tests: `2 passed`
- `docs/api/openapi.yaml` YAML parse: passed
- Runtime OpenAPI smoke: routes `548`, paths `500`, target OpenAPI paths `0`, duplicate operation IDs `0`
- Markdown governance gate: planned for this PR
- OpenSpec strict validation: planned for this PR
- Mainline scope gate: planned for this PR
- GitNexus detect-changes: planned, with CLI fallback if MCP remains unavailable

## Next Gate

Start G2.266 as a no-source signal statistics dormant contract closeout / residual refresh.

G2.266 should verify this cleanup stayed path-limited and decide whether the broader service lifecycle queue should return to a provider candidate, a dormant-route archive decision, or another route/OpenAPI ownership gate.
