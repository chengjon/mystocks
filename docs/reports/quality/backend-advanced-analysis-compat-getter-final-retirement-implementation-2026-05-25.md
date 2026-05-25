# Backend AdvancedAnalysis Compatibility Getter Final Retirement Implementation - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.91 AdvancedAnalysis public compatibility getter final-retirement
implementation

Status: ready for review

## Scope

This packet implements the G2.90 authorization accepted in PR `#243`.

Allowed source/test files:

- `web/backend/app/services/advanced_analysis_service.py`
- `web/backend/tests/test_advanced_analysis_service_lifecycle_di.py`

Governance evidence files:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/advanced-analysis-compat-getter-final-retirement-implementation-2026-05-25.json`
- `docs/reports/quality/backend-advanced-analysis-compat-getter-final-retirement-implementation-2026-05-25.md`
- `governance/mainline/task-cards/pr-244.yaml`

No route/API, OpenAPI exposure, frontend, PM2/runtime, OpenSpec, GitHub issue
label, or public API contract change is made here.

## Implementation Summary

The implementation retires the final public AdvancedAnalysis compatibility
getter:

- delete public `get_advanced_analysis_service()`;
- keep `_get_or_create_advanced_analysis_service()`;
- keep `get_advanced_analysis_service_dependency()`;
- keep `install_advanced_analysis_service()`;
- keep `ADVANCED_ANALYSIS_SERVICE_STATE_KEY`;
- update focused lifecycle tests so they no longer monkeypatch the removed public
  getter.

## TDD Evidence

RED before implementation:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_advanced_analysis_service_lifecycle_di.py::test_public_advanced_analysis_service_getter_is_retired -q --no-cov --tb=short
```

Result:

```text
1 failed
AssertionError: assert not True
```

GREEN after implementation:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_advanced_analysis_service_lifecycle_di.py -q --no-cov --tb=short
```

Result:

```text
5 passed in 3.78s
```

## GitNexus Evidence

GitNexus was refreshed for the G2.91 worktree before source edits:

```text
gitnexus analyze --with-gitignore
```

Pre-edit impact checks:

| Target | Risk | Impact |
|---|---:|---:|
| `get_advanced_analysis_service` | LOW | 0 impacted symbols / 0 affected processes |

Pre-edit context showed `get_advanced_analysis_service()` as a public wrapper
that only called `_get_or_create_advanced_analysis_service()`.

## Reference Scan

After implementation:

| Metric | Value |
|---|---:|
| Exact public getter call hits | 0 |
| Route/API direct public getter call hits | 0 |
| Package export hits | 0 |
| Private initializer hits | 2 |
| Dependency-provider refs | 19 |

The only remaining public getter text is the focused test assertion string that
proves `get_advanced_analysis_service` is absent.

## Verification

| Gate | Result |
|---|---|
| Focused lifecycle tests | `5 passed in 3.78s` |
| `test_health_route_conflicts.py` | `120 passed in 76.54s` |
| Ruff touched backend files | passed |
| Black check touched backend files | passed |
| OpenAPI smoke | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, warnings=`0` |

OpenAPI smoke loaded the root `.env` and imported `app.main`.

## Boundary

This is final-retirement implementation for the AdvancedAnalysis public
compatibility getter only.

The following remain out of scope:

- route/API edits;
- route path, response model, response shape, or OpenAPI exposure changes;
- frontend or generated client edits;
- PM2/runtime execution;
- OpenSpec changes/spec updates;
- GitHub issue label changes;
- deleting `_get_or_create_advanced_analysis_service()`;
- removing `get_advanced_analysis_service_dependency()`;
- removing `install_advanced_analysis_service()`.

## Rollback

Revert this PR as one unit. Rollback restores the public
`get_advanced_analysis_service()` wrapper and prior focused lifecycle test
expectations.

## Next Gate

If this packet is accepted, prepare a closeout / next-candidate refresh before
starting any other service getter retirement lane.
