# Backend AdvancedAnalysis Route Provider Migration Implementation - 2026-05-24

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Status: review-ready.

Current HEAD before commit: `22b617733e29c9a441e88cb1da2ce0a5d8be98cc`.

Parent authorization: PR `#184`, merged at
`22b617733e29c9a441e88cb1da2ce0a5d8be98cc`.

## Decision Boundary

This implementation follows the G2.44 authorization boundary. It changes only:

- `web/backend/app/services/advanced_analysis_service.py`
- `web/backend/app/api/advanced_analysis_api.py`
- `web/backend/tests/test_advanced_analysis_service_lifecycle_di.py`
- this implementation report
- generated implementation evidence JSON
- steward tree
- task card

It does not change route paths, response models, OpenAPI exposure, docs/API,
frontend, PM2/runtime process state, OpenSpec files, issue labels, unrelated
service seams, or compatibility getter behavior.

## Implementation Summary

Implemented the smallest app-state backed route provider seam:

- added `ADVANCED_ANALYSIS_SERVICE_STATE_KEY`;
- added `install_advanced_analysis_service(app, service=None)`;
- added async `get_advanced_analysis_service_dependency(request)`;
- preserved `advanced_analysis_service` module singleton;
- preserved async `get_advanced_analysis_service()` compatibility getter;
- converted all `14` `advanced_analysis_api.py` service parameters from
  class-based `Depends()` to `Depends(get_advanced_analysis_service_dependency)`.

## TDD Evidence

Red run before implementation:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_advanced_analysis_service_lifecycle_di.py -q -n 0 --tb=short --no-cov
```

Result:

- `4 failed`
- expected missing symbols:
  - `get_advanced_analysis_service_dependency`
  - `ADVANCED_ANALYSIS_SERVICE_STATE_KEY`
  - `install_advanced_analysis_service`
- route dependency still pointed to class-based `Depends()`

Green run after implementation and formatting:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_advanced_analysis_service_lifecycle_di.py -q -n 0 --tb=short --no-cov
```

Result:

- `4 passed in 4.25s`

## Guard Evidence

Route dependency guard:

```json
{
  "class_depends": 0,
  "provider_depends": 14,
  "direct_getter_calls": 0,
  "state_key": true,
  "install": true,
  "provider": true,
  "compat_getter": true
}
```

Current file metrics:

```json
{
  "service_lines": 505,
  "api_lines": 637,
  "test_lines": 83,
  "routes": 14,
  "class_depends": 0,
  "provider_depends": 14,
  "direct_getter_calls": 0,
  "has_state_key": true,
  "has_installer": true,
  "has_provider": true,
  "has_compat_getter": true
}
```

## App And OpenAPI Smoke

Initial isolated smoke without repository root on `PYTHONPATH` failed because
`src` imports were not resolvable. Re-run with both `web/backend` and repository
root on `PYTHONPATH`, plus required runtime environment variables, passed:

```json
{
  "routes": 548,
  "paths": 500,
  "operation_ids": 536,
  "duplicate_operation_ids": 0,
  "advanced_paths": 14,
  "warnings": 0
}
```

Observed non-blocking import-time warnings/logs were existing optional runtime
environment facts, including GPU dependency fallback and mock-data fallback.

## Static Verification

```bash
ruff check web/backend/app/services/advanced_analysis_service.py web/backend/app/api/advanced_analysis_api.py web/backend/tests/test_advanced_analysis_service_lifecycle_di.py
black --check web/backend/app/services/advanced_analysis_service.py web/backend/app/api/advanced_analysis_api.py web/backend/tests/test_advanced_analysis_service_lifecycle_di.py
```

Results:

- `ruff`: `All checks passed!`
- `black --check`: `3 files would be left unchanged`

## GitNexus Evidence

Pre-edit:

- `AdvancedAnalysisService` context: found at
  `web/backend/app/services/advanced_analysis_service.py`, lines `24-468`
- `AdvancedAnalysisService` upstream impact: LOW, impacted=`0`
- `get_advanced_analysis_service` context: found at
  `web/backend/app/services/advanced_analysis_service.py`, lines `475-478`
- `get_advanced_analysis_service` upstream impact: LOW, impacted=`0`
- `web/backend/app/api/advanced_analysis_api.py` upstream impact: LOW,
  impacted=`0`

Text scan remained the deciding route evidence because GitNexus reported no
incoming graph edges while `advanced_analysis_api.py` had `14` active
class-based route dependency sites before implementation.

Staged scope:

- changed files: `7`
- changed symbols: `40`
- affected count: `0`
- affected processes: `0`
- risk level: `low`

## Rollback

Rollback is a single PR revert. Reverting restores the `14` route dependencies
to class-based `AdvancedAnalysisService = Depends()` and removes the new
app-state dependency provider while preserving the pre-existing compatibility
getter and module singleton behavior.

## Next Gate

Human review of this G2.45 implementation PR.

If accepted and merged, run a separate G2.46 closeout/current-head candidate
refresh before selecting another service lifecycle DI implementation lane.
