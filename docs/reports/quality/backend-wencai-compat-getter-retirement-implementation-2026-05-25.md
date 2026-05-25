# Backend Wencai Compatibility Getter Retirement Implementation - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.95 Wencai getter-retirement implementation
Status: ready for review

## Purpose

Implement the G2.94 authorization by retiring only the unused public
compatibility getter `get_wencai_service`.

## Change Summary

| Path | Change |
|---|---|
| `web/backend/app/services/wencai_service.py` | Removed only `get_wencai_service`; kept `WencaiService` intact |
| `web/backend/tests/test_wencai_service_getter_retirement.py` | Added focused regression coverage for public getter absence and `WencaiService` class availability |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Recorded G2.94 acceptance and G2.95 implementation state |
| `.planning/codebase/generated/wencai-compat-getter-retirement-implementation-2026-05-25.json` | Added generated evidence snapshot |
| `governance/mainline/task-cards/pr-248.yaml` | Added implementation task-card gate |

## TDD Evidence

| Step | Command | Result |
|---|---|---|
| Red | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_wencai_service_getter_retirement.py -q --no-cov --tb=short` | `1 failed, 1 passed`; failure was `hasattr(wencai_service_module, "get_wencai_service")` |
| Green | Same focused command after source edit | `2 passed in 1.49s` |
| Green rerun | Same focused command after verification batch | `2 passed in 1.63s` |

## Post-Change Reference Scan

| Signal | Value |
|---|---:|
| `get_wencai_service` app refs | `0` |
| `get_wencai_service` route/API refs | `0` |
| `get_wencai_service` test refs | `1` |
| `get_wencai_service` package export refs | `0` |
| `WencaiService` app refs | `16` |
| `WencaiService` route/API refs | `9` |
| `WencaiService` test refs | `1` |

The remaining `get_wencai_service` test reference is the focused absence
assertion.

## Verification Evidence

| Check | Result |
|---|---|
| Pre-edit GitNexus impact | `get_wencai_service`: LOW, impacted count `0`, direct callers `0`, affected processes `0`, affected modules `0` |
| Focused pytest | `2 passed` |
| Health route conflicts | `120 passed in 73.74s` |
| Ruff touched paths | `All checks passed!` |
| Black check touched paths | `2 files would be left unchanged` |
| OpenAPI smoke | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |
| GitNexus staged detect | LOW risk, changed files=`6`, affected count=`0`, affected processes=`0` |

The OpenAPI smoke used non-sensitive local placeholder environment variables and
did not run PM2 or authorize runtime promotion.

## Boundary

This implementation does not:

- delete or rename `WencaiService`;
- change `web/backend/app/api/wencai.py`;
- change `web/backend/app/tasks/wencai_tasks.py`;
- change `src/database/services/database_service.py`;
- change routes, response models, response shapes, or OpenAPI exposure;
- change frontend files, generated clients, PM2 state, OpenSpec files, or
  GitHub issue labels.

## Next Gate

Human review / PR merge decision for this implementation packet.

If accepted, create G2.96 as a closeout packet before selecting another service
lifecycle lane.
