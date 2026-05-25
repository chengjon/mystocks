# Backend EnhancedDataService Getter Retirement Implementation - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.99 EnhancedDataService getter-retirement implementation
Status: ready for review

## Purpose

Implement the G2.98 authorization by retiring only the unused public
compatibility getter `get_enhanced_data_service`.

This implementation preserves `EnhancedDataService` and does not change system
health routes, response models, OpenAPI exposure, frontend files, PM2 state,
OpenSpec files, or GitHub issue labels.

## Change Summary

| Path | Change |
|---|---|
| `web/backend/app/services/data_service_enhanced.py` | Removed only `get_enhanced_data_service` and its private `_enhanced_data_service` singleton state; kept `EnhancedDataService` intact; changed the module-local `__main__` smoke call to construct `EnhancedDataService()` directly |
| `web/backend/tests/test_enhanced_data_service_getter_retirement.py` | Added focused regression coverage for public getter absence, class importability, and private singleton-state removal |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Recorded G2.98 acceptance and G2.99 implementation state |
| `.planning/codebase/generated/enhanced-data-service-getter-retirement-implementation-2026-05-25.json` | Added generated implementation evidence |
| `governance/mainline/task-cards/pr-252.yaml` | Added implementation task-card gate |

## TDD Evidence

| Step | Command | Result |
|---|---|---|
| Red | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_enhanced_data_service_getter_retirement.py -q --no-cov --tb=short` | `2 failed, 1 passed`; failures proved `get_enhanced_data_service` and `_enhanced_data_service` still existed |
| Green | Same focused command after source edit | `3 passed in 1.82s` |

## Post-Change Reference Scan

| Signal | Value |
|---|---:|
| `get_enhanced_data_service` app refs | `0` |
| `get_enhanced_data_service` route/API refs | `0` |
| `get_enhanced_data_service` test refs | `2` |
| `get_enhanced_data_service` package export refs | `0` |
| `_enhanced_data_service` app refs | `0` |
| `_enhanced_data_service` route/API refs | `0` |
| `_enhanced_data_service` test refs | `1` |
| `EnhancedDataService` app refs | `8` |
| `EnhancedDataService` route/API refs | `4` |
| `EnhancedDataService` test refs | `1` |

Remaining `get_enhanced_data_service` and `_enhanced_data_service` references
are focused absence assertions in
`web/backend/tests/test_enhanced_data_service_getter_retirement.py`.

`EnhancedDataService` remains active through direct class usage in
`web/backend/app/api/v1/system/health.py`.

## Verification Evidence

| Check | Result |
|---|---|
| Pre-edit GitNexus impact | `get_enhanced_data_service`: LOW, impacted count `3`, direct `1`, affected processes `0` |
| Focused pytest | `3 passed` |
| Health route conflicts | `120 passed in 72.40s` |
| Ruff touched paths | `All checks passed!` |
| Black check touched paths | `2 files would be left unchanged` |
| OpenAPI smoke | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |
| GitNexus staged detect | LOW risk, changed files=`6`, affected count=`0`, affected processes=`0` |

The OpenAPI smoke used non-sensitive local placeholder environment variables and
did not run PM2 or authorize runtime promotion.

GitNexus marked multiple `data_service_enhanced.py` symbols as modified due to
the structured diff around the retired tail getter. No affected execution flows
were detected.

## Boundary

This implementation does not:

- delete, rename, or migrate `EnhancedDataService`;
- change `web/backend/app/api/v1/system/health.py`;
- change routes, response models, response shapes, or OpenAPI exposure;
- change frontend files, generated clients, PM2 state, OpenSpec files, or
  GitHub issue labels.

## Next Gate

Human review / PR merge decision for this implementation packet.

If accepted, create G2.100 as a closeout packet before selecting another service
lifecycle lane.
