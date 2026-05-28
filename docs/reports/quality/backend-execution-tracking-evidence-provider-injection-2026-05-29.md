# Backend Execution Tracking Evidence Provider Injection - 2026-05-29

> **历史文档说明**: 本文件是 G2.221 执行证据快照，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Branch: `g2-221-execution-tracking-evidence-provider-injection`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `3d2dc3e8204388cc157c23df59f584a3efb268fe`
- Prepared at: `2026-05-29T02:42:26+08:00`
- Parent authorization: G2.220 / PR `#373`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source authority in this package: path-limited

## Authorized Scope

| Path | Role |
|---|---|
| `web/backend/app/api/trade/execution_tracking_routes.py` | Authorized route/provider implementation path |
| `web/backend/tests/test_trade_execution_tracking_routes.py` | Authorized focused test path |
| `.planning/codebase/generated/execution-tracking-evidence-provider-injection-2026-05-29.json` | Machine-readable G2.221 evidence |
| `docs/reports/quality/backend-execution-tracking-evidence-provider-injection-2026-05-29.md` | Human-readable G2.221 report |
| `governance/mainline/task-cards/pr-374.yaml` | Mainline governance task card |
| `.planning/codebase/steward-tree/*` | Steward-tree state updates |

No other backend source, frontend, config, scripts, OpenSpec, `docs/api/`, or FUNCTION_TREE files are authorized by this package.

## GitNexus Impact

Pre-edit impact for `get_execution_tracking_evidence_service`:

| Metric | Value |
|---|---:|
| Risk | HIGH |
| Direct callers | 2 |
| Impacted symbols | 2 |
| Affected processes | 3 |
| Affected module | Trade |

D1 callers are `_load_execution_records` and `get_execution_tracking_detail`. This matches the G2.220 authorization boundary and is why G2.221 remains path-limited.

## TDD Evidence

RED:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_trade_execution_tracking_routes.py::test_execution_tracking_routes_can_use_dependency_overridden_miniqmt_evidence_service -q --no-cov --tb=short
```

Result: `1 failed`. The dependency override did not reach the route body, so the list response had no fake evidence item.

GREEN:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_trade_execution_tracking_routes.py::test_execution_tracking_routes_can_use_dependency_overridden_miniqmt_evidence_service -q --no-cov --tb=short
```

Result: `1 passed`.

## Implementation

G2.221 keeps `get_execution_tracking_evidence_service` as the default provider factory and moves its use to explicit FastAPI dependency injection.

| Area | Change |
|---|---|
| Route import | Add `Depends` from FastAPI |
| `_load_execution_records` | Accept `evidence_service: ExecutionTrackingEvidenceService` |
| Bridge evidence loading | Use the injected `evidence_service.load_records(...)` |
| List route | Add `Depends(get_execution_tracking_evidence_service)` |
| Detail route | Add `Depends(get_execution_tracking_evidence_service)` |
| Focused test | Use `app.dependency_overrides` instead of monkeypatching the provider helper |

Line evidence after implementation:

| Evidence | Line |
|---|---:|
| `Depends` import | `execution_tracking_routes.py:8` |
| `_load_execution_records` injected parameter | `execution_tracking_routes.py:337` |
| Injected `load_records` call | `execution_tracking_routes.py:365` |
| List route dependency | `execution_tracking_routes.py:448` |
| Detail route dependency | `execution_tracking_routes.py:544` |
| Test client dependency override support | `test_trade_execution_tracking_routes.py:23` |
| Dependency override usage | `test_trade_execution_tracking_routes.py:96` |

## Contract Invariants

- No route path changes.
- No `response_model` changes.
- No `UnifiedResponse` envelope changes.
- No request schema changes.
- No miniQMT evidence semantic changes.
- No `broker_state` or bridge evidence interpretation changes.
- `trigger_external_execution` remains out of scope.

## Verification

| Check | Result |
|---|---|
| Focused suite | `web/backend/tests/test_trade_execution_tracking_routes.py`: `4 passed in 3.11s` |
| Ruff | `All checks passed!` |
| app.main/OpenAPI smoke | passed with transient runtime environment |
| OpenAPI route count | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| OpenAPI warnings | `0` |
| Direct provider route-body calls | `0` |

The app.main/OpenAPI smoke used transient environment values only. Secret values
were not persisted in repository files or recorded in this report.

## Next Gate

If PR `#374` is accepted, start G2.222 as a no-source closeout and residual refresh:

- confirm current-head residual state for `get_execution_tracking_evidence_service`
- verify the focused route tests and smoke remain valid
- decide whether the execution tracking provider seam is closed or needs a follow-up
