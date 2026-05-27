# Backend Risk Stop-Loss Route Provider Implementation - G2.188

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation PR review candidate
- Prepared at: `2026-05-27T23:02:44+08:00`
- Branch: `g2-188-risk-stop-loss-provider-implementation`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `2d3b9c7e3ff30c81a19d51e66c32d2c06c1e1c4a`
- Parent authorization: G2.187, PR `#340`, merged at `2d3b9c7e3ff30c81a19d51e66c32d2c06c1e1c4a`

Boundary note: this implementation is limited to the stop-loss route provider
lane authorized by G2.187. It does not delete or rename src-level stop-loss
service getters, change other risk routes, alter frontend code, create OpenSpec
changes, or fix unrelated alerts / legacy compatibility router baselines.

## Implementation

G2.188 moves the stop-loss route pair from route-body service resolver calls to
route-local FastAPI provider parameters:

| Surface | Before | After |
|---|---|---|
| History service routes | `history_service = _resolve_history_service()` inside endpoint body | `history_service: Any = Depends(get_stop_loss_history_service_provider)` |
| Execution service routes | `execution_service = _resolve_execution_service()` inside endpoint body | `execution_service: Any = Depends(get_stop_loss_execution_service_provider)` |
| Direct test invocation | endpoint resolved service internally | `_resolve_direct_call_dependency(...)` preserves direct-call fallback |

Injected endpoints:

| Provider | Endpoints |
|---|---|
| `get_stop_loss_history_service_provider` | `get_stop_loss_performance`, `get_stop_loss_recommendations` |
| `get_stop_loss_execution_service_provider` | `add_stop_loss_position`, `update_stop_loss_price`, `remove_stop_loss_position`, `get_stop_loss_status`, `get_stop_loss_overview`, `batch_update_stop_loss_prices` |

Preserved public contract:

- Route paths and HTTP methods remain unchanged.
- `response_model=Dict[str, Any]` declarations remain unchanged.
- OpenAPI examples remain unchanged.
- Dependency parameters do not leak into OpenAPI route parameters.
- The src-level getters remain canonical compatibility entrypoints.
- Existing route-local exception behavior is preserved.

## GitNexus Pre-Edit Impact

| Symbol | Risk | Impacted | Direct | Processes |
|---|---:|---:|---:|---:|
| `get_stop_loss_history_service` | LOW | 3 | 1 | 0 |
| `get_stop_loss_execution_service` | LOW | 0 | 0 | 0 |
| `_resolve_history_service` | LOW | 2 | 2 | 0 |
| `_resolve_execution_service` | MEDIUM | 6 | 6 | 0 |
| 8 stop-loss route endpoint symbols | LOW | 0 | 0 | 0 |

The only MEDIUM item is `_resolve_execution_service`, and its direct callers are
the six stop-loss execution endpoints that this lane explicitly covers.

## TDD Evidence

Red test:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_risk_runtime_bootstrap_regressions.py -q -k stop_loss --tb=short --disable-warnings --no-cov
2 failed, 3 passed, 5 deselected
```

Expected red failures:

- `get_stop_loss_performance() got an unexpected keyword argument 'history_service'`
- `add_stop_loss_position() got an unexpected keyword argument 'execution_service'`

Green tests:

| Command | Result |
|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_risk_runtime_bootstrap_regressions.py -q -k stop_loss --tb=short --disable-warnings --no-cov` | `5 passed, 5 deselected` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_stop_loss_route_regressions.py -q --tb=short --disable-warnings --no-cov` | `2 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= tests/unit/contract/test_risk_router_runtime_import.py::test_app_main_registers_canonical_risk_router_without_loading_compat_shim -q --tb=short --disable-warnings --no-cov` | `1 passed` |

## OpenAPI Smoke

Command used minimal local environment values only to import `app.main` and
generate `app.openapi()`.

| Metric | Value |
|---|---:|
| OpenAPI paths | 500 |
| Stop-loss paths | 10 |
| Dependency parameters leaked into schema | 0 |

## Quality Gates

| Gate | Result |
|---|---|
| `ruff check web/backend/app/api/risk/stop_loss.py web/backend/tests/test_risk_runtime_bootstrap_regressions.py web/backend/tests/test_stop_loss_route_regressions.py tests/unit/contract/test_risk_router_runtime_import.py` | Passed |
| `git diff --check` | Passed |

## Known Out-Of-Scope Baseline Failures

These failures were observed but are outside the G2.188 authorized stop-loss
provider scope:

| Command | Observed result | Reason |
|---|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_risk_runtime_bootstrap_regressions.py -q --tb=short --disable-warnings --no-cov` | `4 failed, 6 passed` | Alerts route resolver baseline failures on `_resolve_notification_manager`, `_resolve_rule_engine`, and `_resolve_runtime_alert_service` |
| `PYTHONPATH=web/backend pytest -o addopts= tests/unit/contract/test_risk_router_runtime_import.py -q --tb=short --disable-warnings --no-cov` | One legacy compatibility import test fails when included | `app.api.risk_management` compatibility module is absent at current HEAD |

These are not fixed in this lane because G2.187 authorized only stop-loss route
service provider injection.

## Next Gate

Review the G2.188 implementation PR. If accepted, merge it and open a
path-limited closeout / candidate-refresh governance packet. Do not expand this
PR into alerts resolver fixes, legacy compatibility router restoration, src-level
getter deletion, or other risk route provider migrations.
