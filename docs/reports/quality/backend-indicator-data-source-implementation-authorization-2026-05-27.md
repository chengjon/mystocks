# Backend Indicator/Data Source Implementation Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: Ready for review

Scope: G2.161 authorization package only. No backend source, test, route, OpenAPI, frontend, PM2, OpenSpec, config, script, issue-label, or runtime behavior change is performed in this package.

Boundary: this is a source-implementation authorization package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not perform implementation.

Parent: G2.160, PR `#313`, merged as `296957a12a6d1ce30919925e4637bd63bed5cc18`.

Current HEAD: `296957a12a6d1ce30919925e4637bd63bed5cc18`.

Prepared at: `2026-05-27T01:13:49+08:00`.

## Decision

Authorize the next gate as G2.162: Indicator/Data source implementation lane.

This authorization is conditional on review and merge of the G2.161 package. G2.161 does not itself authorize source edits in this PR.

G2.162 may remove direct application-body `get_data_service()` calls from the Indicator/Data consumer modules by introducing narrow consumer-local provider seams that preserve the public `get_data_service()` fallback. It must not delete, privatize, or change `web/backend/app/services/data_service.py::get_data_service`.

Reason:

- G2.159 identified the Indicator/Data getter seam as small enough for a future implementation lane, but blocked source work until the v1 indicator error-contract test was aligned.
- G2.160 aligned the v1 indicator regression test with the canonical `BusinessException` contract and merged as PR `#313`.
- Current HEAD focused tests pass after that alignment.
- GitNexus still classifies `get_data_service` as CRITICAL because it participates in Indicator/Data and Strategy flows, so the next source lane must be small, explicitly verified, and review-gated.

## GitNexus Evidence

| Symbol | Risk | Impacted | Direct callers | Processes | Notes |
|---|---:|---:|---:|---:|---|
| `get_data_service` | CRITICAL | 5 | 3 | 7 | Direct callers remain in Indicator/Data and Strategy indicator flows. |
| `calculate_indicators` | LOW | 0 | 0 | 0 | Public indicator calculation route surface. |
| `_calculate_single_indicator` | LOW | 3 | 1 | 0 | Helper used by single and batch calculation paths. |
| `calculate_single_request` | LOW | 2 | 1 | 0 | Intermediate helper. |
| `limited_calculate` | LOW | 1 | 1 | 0 | Batch-limiter helper. |

`get_data_service` d1 callers at current HEAD:

| File | Line | Surface |
|---|---:|---|
| `web/backend/app/api/indicators/indicator_cache.py` | 343 | `calculate_indicators` direct body call |
| `web/backend/app/api/indicators/indicator_cache.py` | 613 | `_calculate_single_indicator` direct body call |
| `web/backend/app/api/v1/strategy/indicators.py` | 201 | `get_technical_indicators` direct body call |

Affected process names reported by GitNexus include:

- `Calculate_indicators -> Warning`
- `Calculate_indicators -> _dataframe_to_ohlcv_arrays`
- `Get_technical_indicators -> ShouldAlwaysSelectNothing`
- `Get_technical_indicators -> GetAttributeNS`
- `Get_technical_indicators -> Strip`
- `Get_technical_indicators -> _locationObjectNavigate`
- `Get_technical_indicators -> ImplForWrapper`

## Current-Head Hit Classification

| Class | Count | Lines |
|---|---:|---|
| Service definition | 1 | `web/backend/app/services/data_service.py:466` |
| Application import sites | 2 | `indicator_cache.py:40`, `v1/strategy/indicators.py:17` |
| Application body calls | 3 | `indicator_cache.py:343`, `indicator_cache.py:613`, `v1/strategy/indicators.py:201` |
| Focused regression-test monkeypatches | 2 | `test_v1_indicators_regressions.py:42`, `test_v1_indicators_regressions.py:59` |
| Integration-test direct smoke calls | 2 | `test_integration_e2e.py:201`, `test_integration_e2e.py:235` |

Target G2.162 closure metric:

- Application body calls should move from `3` to `0`.
- The public service definition should remain present.
- Direct integration-test smoke calls may remain unless the G2.162 implementation package explicitly chooses and reviews a test-provider adjustment.

## Consumer Contract Matrix

| Consumer | Current getter use | Contract to preserve |
|---|---|---|
| `calculate_indicators` | direct body call at `indicator_cache.py:343` | `UnifiedResponse[Dict]`, `create_success_response`, request validation, OHLCV retrieval, cache/accounting behavior, `InvalidDateRangeError -> ValidationException`, `StockDataNotFoundError -> NotFoundException`, `BusinessException` propagation |
| `_calculate_single_indicator` | direct body call at `indicator_cache.py:613` | result dict shape, symbol/date semantics, `calculate_single_request`, `limited_calculate`, and `calculate_indicators_batch` behavior |
| `get_technical_indicators` | direct body call at `strategy/indicators.py:201` | indicator normalization, `get_daily_ohlcv` behavior, pagination payload, unsupported indicator `BusinessException 400`, missing data `BusinessException 404`, generic fetch failure `BusinessException 503` |

## Baseline Verification

| Check | Result |
|---|---|
| `test_v1_indicators_regressions.py` | `2 passed in 1.94s` |
| `test_indicator_registry_route_provider.py` | `2 passed in 2.08s` |
| `test_health_route_conflicts.py --collect-only` | `120 tests collected in 17.21s` |
| Static checkout summary | branch `g2-161-indicator-data-implementation-authorization`, HEAD `296957a12a6d`, status clean before edits |

The first relative-path test attempt failed because context-mode executes from a temporary cwd. The absolute-path rerun is the authoritative baseline evidence.

## G2.162 Authorized Scope

Allowed application source paths:

- `web/backend/app/api/indicators/indicator_cache.py`
- `web/backend/app/api/v1/strategy/indicators.py`

Allowed focused test paths:

- `web/backend/tests/test_v1_indicators_regressions.py`
- `web/backend/tests/test_indicator_registry_route_provider.py`
- `web/backend/tests/test_integration_e2e.py`, only if the direct service smoke needs a reviewed provider-seam adjustment
- `web/backend/tests/test_health_route_conflicts.py`, only for import/collection verification or a reviewed route-contract assertion update caused by the authorized source files

Allowed governance paths:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/*indicator-data*2026-05-27*.json`
- `docs/reports/quality/*indicator-data*2026-05-27*.md`
- `governance/mainline/task-cards/pr-*.yaml`

Recommended implementation direction:

- Introduce narrow module-local provider seams in the consuming modules.
- Preserve fallback behavior through the existing public `get_data_service()` function.
- Prefer dependency injection at the consumer edge over changing the shared service singleton implementation.
- Keep route paths, response models, OpenAPI exposure, and error contracts unchanged.

## G2.162 Forbidden Scope

G2.162 must not:

- edit `web/backend/app/services/data_service.py`;
- delete, privatize, rename, or change `get_data_service()`;
- edit Strategy adapter internals;
- edit root facade compatibility surfaces;
- change route paths, response models, OpenAPI exposure, tags, operation IDs, or endpoint examples unless a reviewer explicitly expands scope;
- edit frontend files, PM2 workflows, deployment config, scripts, or issue labels;
- mix this Indicator/Data source lane with Dashboard/TDX, realtime streaming/socket, backup route ownership, or route dependency/provider governance work.

## Required G2.162 Gates

Before source edits:

- Refresh branch state and confirm the implementation worktree contains PR `#313`.
- Run GitNexus impact for `get_data_service` and each direct caller to be edited.
- Stop and return to review if any new HIGH or CRITICAL dependency appears outside the Indicator/Data scope already recorded here.

During implementation:

- Use a minimal red/green loop around the focused indicator tests.
- Keep application-body `get_data_service()` call count moving from `3` to `0`.
- Preserve all consumer contracts listed above.

Before commit:

- `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_v1_indicators_regressions.py -q --no-cov --tb=short`
- `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_indicator_registry_route_provider.py -q --no-cov --tb=short`
- `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov`
- `ruff check` for every touched backend source and test file.
- JSON/YAML parse for generated artifacts and task card.
- Markdown governance for touched Markdown files.
- `git diff --check`.
- Staged GitNexus detect-changes.
- Mainline scope gate for the future PR task card.

## Rollback

If G2.162 causes route/API drift, error-contract drift, or broader service lifecycle impact, revert the implementation PR. The public `get_data_service()` function and current route contracts must remain available, so rollback should be a normal source revert rather than a compatibility-restoration project.

## Next Gate

Review this package. If accepted and merged, start G2.162 as the narrow Indicator/Data source implementation lane. Do not start source edits from G2.161 itself.
