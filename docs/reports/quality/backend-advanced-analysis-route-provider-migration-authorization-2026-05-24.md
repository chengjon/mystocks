# Backend AdvancedAnalysis Route Provider Migration Authorization - 2026-05-24

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Status: review-ready.

Scope: G2.44 decision/authorization packet for a future
`AdvancedAnalysisService` route-provider migration.

Current HEAD: `1e137abb2a32b795c403a8a168a174ad86b7f693`.

Parent PR: `#183` merged G2.43 service candidate usefulness and ownership
triage at `1e137abb2a32b795c403a8a168a174ad86b7f693`.

Boundary note: this packet authorizes only a future implementation lane if
human review accepts it. This packet itself does not change backend source,
tests, route paths, OpenAPI schema, PM2/runtime state, OpenSpec changes, issue
labels, or compatibility getter behavior.

## Current Input State

G2.43 selected `AdvancedAnalysisService` as the best next authorization
candidate, not as an already authorized implementation target.

| Evidence | Current state | Interpretation |
|---|---|---|
| `web/backend/app/services/advanced_analysis_service.py` | `480` lines; defines `AdvancedAnalysisService`, module singleton `advanced_analysis_service`, and async `get_advanced_analysis_service()` | Active service module with compatibility surface |
| `get_advanced_analysis_service` | active text reference is definition-only | Do not delete here; future branch may preserve it as fallback |
| `web/backend/app/api/advanced_analysis_api.py` | `635` lines, `14` routes, `14` `AdvancedAnalysisService = Depends()` service parameters | Active route-provider migration candidate |
| GitNexus impact | `AdvancedAnalysisService` upstream impact returned `LOW`, direct=`0`, processes=`0` | Useful low graph risk, but not sufficient alone because text scan proves route usage |
| GitHub issue `#79` | `OPEN`, label `needs-triage` | Parent lifecycle DI backlog remains open |
| GitHub issue `#92` | `OPEN`, labels `enhancement`, `ready-for-human`, `ready-for-downstream` | Parent downstream decision context remains open |

An isolated G2.44 `app.main` / OpenAPI smoke was attempted, but the fresh
worktree lacks required runtime environment variables:

`POSTGRESQL_HOST`, `POSTGRESQL_USER`, `POSTGRESQL_PASSWORD`,
`JWT_SECRET_KEY`, `BACKEND_PORT`, and `BACKEND_BACKUP_PORT`.

This is recorded as an environment precondition, not as a runtime regression.
The future implementation branch must run the smoke in a configured backend
environment.

## Decision

Decision: approve, subject to human review, a future G2.45 implementation lane
that migrates only the `advanced_analysis_api.py` route dependency surface from
class-based `Depends()` construction to a dedicated route-provider dependency.

This decision does not authorize deleting `get_advanced_analysis_service()` or
the module-level `advanced_analysis_service` compatibility singleton.

The compatibility surface must remain available unless a later accepted packet
proves all of the following:

1. No active source, route, task, test, or docs/API consumer requires it.
2. Route tests prove equivalent behavior without it.
3. OpenAPI path, operation ID, and response contract drift remain zero.
4. GitNexus and text scans agree on the retirement blast radius.

## Future Allowed Write Scope

If this authorization packet is approved, a future implementation branch may
modify only:

1. `web/backend/app/services/advanced_analysis_service.py`
2. `web/backend/app/api/advanced_analysis_api.py`
3. `web/backend/tests/test_advanced_analysis_service_lifecycle_di.py`
4. `docs/reports/quality/backend-advanced-analysis-route-provider-migration-implementation-2026-05-24.md`
5. `.planning/codebase/generated/advanced-analysis-route-provider-migration-implementation-2026-05-24.json`
6. `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
7. `governance/mainline/task-cards/pr-185.yaml`

Any additional file requires a separate approval note before source edits.

## Future Implementation Shape

The future implementation should use the smallest route-provider seam:

- add an app-state key such as `ADVANCED_ANALYSIS_SERVICE_STATE_KEY`;
- add an installer such as
  `install_advanced_analysis_service(app, service=None)`;
- add a provider dependency such as
  `get_advanced_analysis_service_dependency(request: Request)`;
- make the provider prefer `request.app.state` when installed;
- keep `get_advanced_analysis_service()` and the module singleton as fallback
  compatibility surface;
- convert exactly the `14` `AdvancedAnalysisService = Depends()` route
  parameters to the new provider dependency;
- preserve route paths, HTTP methods, response models, status codes, and
  OpenAPI operation IDs;
- avoid changing advanced-analysis business logic, model schemas, response
  envelopes, logging behavior, or downstream `src.advanced_analysis` modules.

## Explicit Non-Goals

- No source edit in this authorization PR.
- No immediate G2.45 implementation without human review of this packet.
- No deletion or retirement of `get_advanced_analysis_service()`.
- No deletion or retirement of the module singleton `advanced_analysis_service`.
- No changes to `WencaiService`, `MarketDataService`, `UnifiedDataService`,
  `DataService`, `StrategyService`, or `TechnicalAnalysisService`.
- No route path, OpenAPI schema, response contract, docs/API, generated client,
  frontend, PM2, database, task, adapter, or external service behavior change.
- No OpenSpec change/spec/archive operation and no issue label movement.

## Required Future Gates

The future implementation branch must:

1. Run GitNexus context/impact for `AdvancedAnalysisService`,
   `get_advanced_analysis_service`, and the relevant route file before source
   edits. If any result is HIGH or CRITICAL, stop and return to review.
2. Add or update focused tests before implementation when feasible.
3. Implement the smallest provider seam that satisfies those tests.
4. Run focused pytest for
   `web/backend/tests/test_advanced_analysis_service_lifecycle_di.py`.
5. Run a representative guard that confirms route body direct
   `get_advanced_analysis_service()` calls remain `0`,
   `AdvancedAnalysisService = Depends()` becomes `0`, and the new provider
   dependency count becomes `14`.
6. Run `ruff check` and `black --check` on touched backend source/test files.
7. Run `app.main` import and targeted OpenAPI smoke in a configured backend
   environment, confirming OpenAPI paths remain `500`, duplicate operation IDs
   remain `0`, and advanced-analysis paths remain present.
8. Stage only the authorized paths and run GitNexus `detect_changes` on staged
   scope before committing.

## Future Verification Commands

The future implementation packet should use commands equivalent to:

```bash
pytest -o addopts= web/backend/tests/test_advanced_analysis_service_lifecycle_di.py -q -n 0 --tb=short --no-cov
ruff check web/backend/app/services/advanced_analysis_service.py web/backend/app/api/advanced_analysis_api.py web/backend/tests/test_advanced_analysis_service_lifecycle_di.py
black --check web/backend/app/services/advanced_analysis_service.py web/backend/app/api/advanced_analysis_api.py web/backend/tests/test_advanced_analysis_service_lifecycle_di.py
git diff --check
```

The app/OpenAPI smoke must be run from a configured backend environment with the
required environment variables available.

## Rollback Plan For Future Implementation

If the future implementation introduces a regression:

- revert the future implementation PR;
- restore the `14` route parameters to class-based
  `AdvancedAnalysisService = Depends()`;
- remove the new dedicated provider, installer, and state-key constant only if
  no later accepted lane has started to depend on them;
- keep `get_advanced_analysis_service()` compatibility getter available;
- keep this authorization packet as historical governance evidence unless the
  decision itself is explicitly superseded.

## Review Checklist

- [ ] The packet is accepted as authorization for a future implementation lane.
- [ ] The future write scope remains limited to the files listed above.
- [ ] Reviewers agree `get_advanced_analysis_service()` is preserved, not
      retired.
- [ ] Reviewers agree `AdvancedAnalysisService` route-provider migration is not
      coupled to `WencaiService`, `MarketDataService`, `UnifiedDataService`,
      `DataService`, `StrategyService`, or `TechnicalAnalysisService`.
- [ ] Reviewers agree future implementation must run configured app/OpenAPI
      smoke before completion.

## Next Gate

Human review of this G2.44 authorization packet.

If accepted, create a separate G2.45 implementation branch for
`AdvancedAnalysisService` route-provider migration. Source edits remain locked
until that branch is explicitly opened under this authorization.
