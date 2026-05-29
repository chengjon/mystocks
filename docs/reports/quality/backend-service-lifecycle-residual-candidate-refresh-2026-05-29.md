# Backend Service Lifecycle Residual Candidate Refresh

> **历史总结说明**: 本报告记录 `G2.231` 在当前 HEAD 上的治理刷新结果，不代表新的源码实现授权。若需确认当前实现事实，请优先以当前代码、`architecture/STANDARDS.md`、根目录 `AGENTS.md`、OpenSpec 状态和最近一次实际验证结果为准。

## Status

- G2: `G2.231`
- Status: candidate refresh for review
- Branch: `g2-231-service-lifecycle-residual-candidate-refresh`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `2652d59b02dedaecd4ac05a2f95fce8ab4ae2e3c`
- Source edit authority: none

Boundary note: this package refreshes service lifecycle residual candidates only.
It does not authorize backend source edits, tests edits, OpenSpec proposal/spec
creation, route behavior changes, PM2 commands, or GitHub issue label changes.

## Parent State

PR `#383` merged G2.230 at
`2652d59b02dedaecd4ac05a2f95fce8ab4ae2e3c`. The cache prewarming route DI
surface is closed at current HEAD:

| Evidence | Value |
|---|---:|
| Route-body direct `get_prewarming_strategy()` calls | 0 |
| `Depends(get_prewarming_strategy)` uses | 3 |
| Typed `prewarming_strategy` parameters | 3 |

G2.231 therefore does not reopen cache prewarming source. Its job is to refresh
the next service lifecycle residual candidate queue.

## Current-HEAD Residual Scan

Service-suffix route getter scan:

| Symbol | Current classification | Evidence |
|---|---|---|
| `get_data_service` | Retained indicator/data provider fallback | 2 provider-return sites; GitNexus impact LOW |
| `get_strategy_service` | Strategy high-risk provider seam | 1 provider-return site; GitNexus impact CRITICAL |
| `get_stop_loss_history_service` | Closed by G2.188/G2.189; retained as provider backing getter | route-local provider helper initialization remains |
| `get_stop_loss_execution_service` | Closed by G2.188/G2.189; retained as provider backing getter | route-local provider helper initialization remains |

Broader non-method `get_*()` scan found `62` API groups. Most are object
methods, utility functions, or already-governed route/provider seams. The top
service-lifecycle candidates are:

| Rank | Candidate | Active evidence | GitNexus | Disposition |
|---:|---|---|---|---|
| 1 | `get_config_manager` | 9 active route-body calls in `web/backend/app/api/data_source_config.py`; 8 legacy `data_source_config.old.py` calls are false positives because the old file is not registered | HIGH, 9 direct callers, 3 affected processes | Select G2.232 no-source decision / authorization |
| 2 | `get_calculator_factory` | 8 route calls in monitoring portfolio routes | HIGH | Defer; domain-specific monitoring portfolio seam |
| 3 | `get_mock_data_manager` | 8 route calls across six API areas | CRITICAL | Defer; cross-domain mock/runtime seam |
| 4 | `get_monitoring_db` | 12 apparent route calls across risk and strategy helpers | ambiguous | Defer; multiple definitions require ownership classification |

## Decision

Select G2.232 as a no-source data-source config manager provider seam decision /
authorization package.

G2.232 should:

- classify the active `data_source_config.py` `get_config_manager()` route-body
  calls
- separate registered route truth from `data_source_config.old.py` false
  positives
- decide whether a later source lane may inject a route/provider dependency
- keep `_data_source_config_responses.py` runtime dependency exports in scope as
  evidence, not as an immediate code target
- forbid source edits until the decision / authorization package is reviewed

## Non-Goals

- Do not edit `web/backend/app/api/data_source_config.py` from G2.231.
- Do not edit `_data_source_config_responses.py` from G2.231.
- Do not reopen cache prewarming source work.
- Do not reopen stop-loss provider work without current-HEAD contradiction
  evidence.
- Do not convert `get_strategy_service` or `get_mock_data_manager` directly into
  a source lane from this refresh.
- Do not create or change OpenSpec proposals/specs from this refresh.

## Evidence Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/service-lifecycle-residual-candidate-refresh-2026-05-29.json` | Machine-readable G2.231 scan and decision evidence |
| `docs/reports/quality/backend-service-lifecycle-residual-candidate-refresh-2026-05-29.md` | Human-readable G2.231 report |
| `governance/mainline/task-cards/pr-384.yaml` | Mainline governance scope card |
