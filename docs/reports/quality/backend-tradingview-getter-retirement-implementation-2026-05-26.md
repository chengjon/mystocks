# Backend TradingView Getter Retirement Implementation - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.103 TradingView getter-retirement implementation
Status: ready for review

## Purpose

Implement the G2.102 authorization by retiring only the unused public
compatibility getter `get_tradingview_service`.

This implementation preserves `TradingViewWidgetService`,
`install_tradingview_service`, `close_tradingview_service`, and
`get_tradingview_service_dependency`. It does not change TradingView routes,
response models, OpenAPI exposure, frontend files, PM2 state, OpenSpec files, or
GitHub issue labels.

## Change Summary

| Path | Change |
|---|---|
| `web/backend/app/services/tradingview_widget_service.py` | Removed only `get_tradingview_service` and private `_tradingview_service` singleton state; changed `install_tradingview_service` fallback to direct `TradingViewWidgetService()` construction |
| `web/backend/tests/test_tradingview_service_lifecycle_di.py` | Updated lifecycle DI fallback coverage to prove default service construction without the public getter; added focused absence assertions for the retired getter/private singleton while preserving lifecycle helper checks |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Recorded G2.102 acceptance and G2.103 implementation state |
| `.planning/codebase/generated/tradingview-getter-retirement-implementation-2026-05-26.json` | Added generated implementation evidence |
| `governance/mainline/task-cards/pr-256.yaml` | Added implementation task-card gate |

## TDD Evidence

| Step | Command | Result |
|---|---|---|
| Red | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_tradingview_service_lifecycle_di.py -q --no-cov --tb=short` | `1 failed, 7 passed`; failure proved `get_tradingview_service` still existed |
| Green | Same focused command after source edit and assertion refinement | `8 passed in 1.43s` |

The assertion refinement narrowed the private-state check from the broad
substring `_tradingview_service` to concrete singleton-state signals
`_tradingview_service =` and `global _tradingview_service`, because helper names
such as `install_tradingview_service` legitimately contain that substring.

## Post-Change Reference Scan

| Signal | Value |
|---|---:|
| `get_tradingview_service` app refs | `0` |
| `get_tradingview_service` route/API refs | `0` |
| `get_tradingview_service` test refs | `3` |
| `get_tradingview_service` package export refs | `0` |
| `_tradingview_service` app refs | `0` |
| `_tradingview_service` route/API refs | `0` |
| `_tradingview_service` test refs | `2` |
| `TradingViewWidgetService` app refs | `13` |
| `TradingViewWidgetService` route/API refs | `7` |
| `TradingViewWidgetService` test refs | `1` |
| `install_tradingview_service` app refs | `4` |
| `install_tradingview_service` test refs | `4` |
| `get_tradingview_service_dependency` app refs | `8` |
| `get_tradingview_service_dependency` route/API refs | `7` |
| `get_tradingview_service_dependency` test refs | `3` |

Remaining `get_tradingview_service` and `_tradingview_service` references are
focused absence assertions in
`web/backend/tests/test_tradingview_service_lifecycle_di.py`.

`TradingViewWidgetService` and `get_tradingview_service_dependency` remain
active through `web/backend/app/api/tradingview.py`.

## Verification Evidence

| Check | Result |
|---|---|
| Pre-edit GitNexus impact | `get_tradingview_service`: LOW, impacted count `1`, direct `1`, affected processes `0` |
| Focused pytest | `8 passed in 1.08s` |
| Health route conflicts | `120 passed in 93.05s` |
| Ruff touched paths | `All checks passed!` |
| Black touched paths | final check passed; `2 files would be left unchanged` |
| OpenAPI smoke | schema-only with non-sensitive placeholder env; routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

The OpenAPI smoke used non-sensitive local placeholder environment variables for
schema generation and did not run PM2 or authorize runtime promotion.

## Boundary

This implementation does not:

- delete, rename, or migrate `TradingViewWidgetService`;
- delete `install_tradingview_service`, `close_tradingview_service`, or
  `get_tradingview_service_dependency`;
- change `web/backend/app/api/tradingview.py`;
- change routes, response models, response shapes, or OpenAPI exposure;
- change frontend files, generated clients, PM2 state, OpenSpec files, or
  GitHub issue labels.

## Next Gate

Human review / PR merge decision for this implementation packet.

If accepted, create G2.104 as a closeout packet before selecting another service
lifecycle lane.
