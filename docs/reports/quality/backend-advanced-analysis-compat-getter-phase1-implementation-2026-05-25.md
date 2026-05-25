# Backend AdvancedAnalysis Compatibility Getter Phase 1 Implementation - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.88 AdvancedAnalysis compatibility getter Phase 1 implementation

Status: ready for review

## Scope

This packet implements the G2.87 authorization accepted in PR `#240`.

Allowed source/test files:

- `web/backend/app/services/advanced_analysis_service.py`
- `web/backend/tests/test_advanced_analysis_service_lifecycle_di.py`

Governance evidence files:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/advanced-analysis-compat-getter-phase1-implementation-2026-05-25.json`
- `docs/reports/quality/backend-advanced-analysis-compat-getter-phase1-implementation-2026-05-25.md`
- `governance/mainline/task-cards/pr-241.yaml`

No route/API, OpenAPI exposure, frontend, PM2/runtime, OpenSpec, GitHub issue
label, or public API contract change is made here.

## Implementation Summary

The implementation keeps the public compatibility getter and decouples the
FastAPI dependency-provider fallback from it:

- add `_get_or_create_advanced_analysis_service()`;
- keep `get_advanced_analysis_service()` as a Phase 1 public compatibility
  wrapper;
- keep `get_advanced_analysis_service_dependency()`;
- retarget `get_advanced_analysis_service_dependency()` fallback to the private
  initializer;
- update focused lifecycle coverage to prove the provider fallback no longer
  calls the public compatibility getter.

## TDD Evidence

RED before implementation:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_advanced_analysis_service_lifecycle_di.py::test_advanced_analysis_service_dependency_fallback_uses_private_initializer -q --no-cov --tb=short
```

Result:

```text
1 failed
AssertionError: provider fallback must not call the public compatibility getter
```

GREEN after implementation:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_advanced_analysis_service_lifecycle_di.py -q --no-cov --tb=short
```

Result:

```text
4 passed in 3.90s
```

## GitNexus Evidence

GitNexus was refreshed for the G2.88 worktree before source edits:

```text
gitnexus analyze
```

Pre-edit impact checks:

| Target | Risk | Impact |
|---|---:|---|
| `get_advanced_analysis_service` | LOW | 1 direct impacted symbol: `get_advanced_analysis_service_dependency` |
| `get_advanced_analysis_service_dependency` | LOW | 0 impacted symbols |

Pre-edit context confirmed that `get_advanced_analysis_service_dependency()`
called `get_advanced_analysis_service()` directly before this change.

## Reference Scan

After implementation:

| Metric | Value |
|---|---:|
| Exact public getter hits in scoped production/test scan | 1 |
| Exact public getter production scope | definition only |
| Route/API direct public getter hits | 0 |
| Private initializer hits | 3 |
| Dependency-provider refs | 19 |

The single remaining exact public getter hit is the public compatibility getter
definition itself. This PR does not delete, rename, or privatize that public
getter.

## Verification

| Gate | Result |
|---|---|
| Focused lifecycle tests | `4 passed in 3.90s` |
| `test_health_route_conflicts.py` | `120 passed in 76.56s` |
| Ruff touched backend files | passed |
| Black check touched backend files | passed |
| OpenAPI smoke | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, warnings=`0` |

OpenAPI smoke loaded the root `.env` and imported `app.main`.

## Boundary

This is Phase 1 service-internal decoupling only.

The following remain out of scope:

- deleting or renaming `get_advanced_analysis_service()`;
- removing `get_advanced_analysis_service_dependency()`;
- changing route paths, response models, response shapes, or OpenAPI exposure;
- changing frontend clients or generated clients;
- running PM2 stateful gates;
- modifying OpenSpec changes/specs;
- changing GitHub issue labels or readiness state.

## Rollback

Revert this PR as one unit. Rollback restores the provider fallback direct call
to public `get_advanced_analysis_service()` and removes the private initializer
plus the focused test expectation.

## Next Gate

If this packet is accepted, prepare a closeout / candidate-refresh governance
packet before any further AdvancedAnalysis getter retirement decision.
