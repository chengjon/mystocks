> **历史文档说明**:
> This design records the approved D2.1a implementation shape for review. It
> does not authorize backend source edits, test edits, issue state changes, PM2
> execution, or `ready-for-agent` movement until explicitly approved for
> implementation.

## Context

The technical-pattern route currently constructs
`TechnicalPatternDetectionService` directly inside its route-local helper. That
keeps the implementation simple, but it makes the first service-tier DI pilot
hard to validate using FastAPI's dependency override surface.

D2.1 selected `TechnicalPatternDetectionService` because its current impact is
low and its direct route consumer is narrow. D2.1a then prepared the concrete
implementation authorization plan and limited future writes to the technical
patterns route module and its focused route regression tests.

## Goals

- Replace the route-local direct service construction with an injectable
  FastAPI dependency provider.
- Keep `TechnicalPatternDetectionService` internals unchanged.
- Preserve the existing route path, response shape, status behavior, OpenAPI
  schema intent, and public technical-pattern functionality.
- Establish a reusable route-level test override pattern for later service DI
  pilots.

## Non-Goals

- No `app.state` or lifespan ownership for this stateless pilot.
- No refactor of `DataSourceFactory`, chart detector loading, pattern models, or
  response schemas.
- No route path, tag, operationId, or OpenAPI exposure change.
- No PM2, frontend, docs/API, broader route governance, or batch singleton
  migration.
- No movement of issue `#92` to `ready-for-agent`.

## Decisions

### Decision: Route-local provider first

The implementation SHOULD add a small route-local provider:

```python
def get_technical_pattern_detection_service() -> TechnicalPatternDetectionService:
    return TechnicalPatternDetectionService()
```

This keeps the pilot near the only known route consumer and avoids introducing a
new shared service registry before a service-tier DI pattern has been proven.

### Decision: Public route receives the dependency

The public route handler SHOULD receive the service through FastAPI `Depends`.
The existing private helper SHOULD accept the service as an argument instead of
constructing it directly.

This keeps the route's public behavior unchanged while making route tests able
to replace the service through `app.dependency_overrides`.

### Decision: Test doubles use dependency overrides

Focused route tests SHOULD use a small async service double through
`app.dependency_overrides`. Tests that exercise the public route SHOULD NOT rely
on monkeypatching `TechnicalPatternDetectionService.detect_for_symbol` as the
primary verification path for this pilot.

### Decision: No lifecycle expansion for the pilot

The pilot is route-level DI only. Because the selected service has no approved
stateful initialization or teardown scope in this batch, the implementation
SHOULD NOT add lifespan, `app.state`, caching, singleton registries, or teardown
artifacts. The closeout evidence SHOULD record that no stateful lifecycle owner
was introduced.

## Implementation Notes

The approved implementation sequence should follow the D2.1a plan:

1. Confirm this OpenSpec change and any child implementation issue are approved.
2. Re-run GitNexus impact/context for `TechnicalPatternDetectionService` and
   `_detect_patterns_for_symbol` before source edits.
3. Add a failing route-level dependency override test.
4. Add the provider and inject it into the route handler.
5. Convert focused public-route tests to dependency overrides.
6. Run focused backend tests, ruff on touched files, OpenSpec validation, and
   GitNexus staged change detection before commit.

## Rollback

Rollback is intentionally small:

- Remove the route-local provider.
- Restore direct `TechnicalPatternDetectionService()` construction inside the
  existing helper.
- Revert the helper and route signatures.
- Remove the dependency override test fixture.
- Keep `TechnicalPatternDetectionService` internals unchanged.
