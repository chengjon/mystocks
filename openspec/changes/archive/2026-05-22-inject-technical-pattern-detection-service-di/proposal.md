# Change: Inject TechnicalPatternDetectionService Through FastAPI DI

> **历史文档说明**:
> This OpenSpec change is a child implementation proposal for review. It does
> not authorize backend source edits, test edits, issue state changes, PM2
> execution, or `ready-for-agent` movement until explicitly approved for
> implementation.

## Why

Issue `#92` accepted `TechnicalPatternDetectionService` as the first backend
service-tier DI pilot. The D2.1 and D2.1a planning artifacts narrowed the
implementation seam to the technical-pattern route, but implementation remains
locked until a separate child OpenSpec branch or implementation issue exists.

This change creates that child OpenSpec branch without authorizing broad service
refactors. It converts the existing planning decision into a small, reviewable
implementation scope.

## What Changes

- Add a route-local FastAPI provider for `TechnicalPatternDetectionService`.
- Inject that provider into the existing technical-pattern route handler.
- Update the focused route regression tests to use `app.dependency_overrides`
  with a service test double.
- Keep the route path, response contract, OpenAPI schema, service internals,
  `DataSourceFactory`, chart detector loading, PM2 gates, frontend, and docs/API
  unchanged.
- Preserve rollback by restoring direct construction inside the existing route
  helper and removing the route-level provider override test.

## Impact

- Affected specs: `architecture-governance`
- Planned affected code after approval:
  - `web/backend/app/api/_technical_patterns_router.py`
  - `web/backend/tests/test_technical_patterns_router_regressions.py`
- Read-only verification context:
  - `web/backend/app/services/technical_pattern_detection_service.py`
  - `web/backend/tests/test_technical_pattern_detection_service.py`
  - `docs/reports/quality/backend-di-pilot-technical-pattern-detection-design-2026-05-21.md`
  - `docs/superpowers/plans/2026-05-21-d2-1a-technical-pattern-detection-di-pilot-implementation-authorization.md`

## Source Evidence

- Issue `#92`: parent downstream decision rollup; remains a decision issue.
- PR `#109`: D2.1a implementation authorization plan merged as
  `44e2f4bad04ee4237b0179bfa21f2ab27402df7e`.
- D2.1 design packet:
  `docs/reports/quality/backend-di-pilot-technical-pattern-detection-design-2026-05-21.md`.
- D2.1a plan:
  `docs/superpowers/plans/2026-05-21-d2-1a-technical-pattern-detection-di-pilot-implementation-authorization.md`.
- Proposal review:
  `openspec/changes/inject-technical-pattern-detection-service-di/proposal-review.md`.

## Approval Boundary

This proposal defines the child implementation scope. Backend source and test
edits MUST NOT begin until this change is reviewed and explicitly approved for
implementation. Issue `#92` MUST remain the parent decision rollup and MUST NOT
be moved to `ready-for-agent` as the implementation vehicle.
