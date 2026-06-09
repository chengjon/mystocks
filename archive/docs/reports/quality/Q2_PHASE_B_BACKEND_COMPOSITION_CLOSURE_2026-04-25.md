# Q2 Phase B Backend Composition Closure Audit

Date: 2026-04-25
Scope: `plan-q2-optimization-closure-program` Phase B
Mode: single-CLI sequential audit

## Documents And Code Surfaces Examined
- `docs/reports/quality/MYSTOCKS_PHASE_EVALUATION_2026Q2.md`
- `docs/reports/quality/Q2_CLOSURE_PROGRAM_SPEC_REVIEW.md`
- `docs/reports/quality/Q2_PHASE_A_REALTIME_TRUTH_AUDIT_2026-04-25.md`
- `openspec/changes/plan-q2-optimization-closure-program/design.md`
- `openspec/changes/plan-q2-optimization-closure-program/tasks.md`
- `web/backend/app/main.py`
- `web/backend/app/app_factory.py`
- `web/backend/app/router_registry.py`
- `web/backend/app/api/register_routers.py`
- `web/backend/tests/test_csrf_protection.py`
- `web/backend/start_server.py`
- `web/backend/load_env.py`
- `web/backend/ecosystem.config.js`
- `web/backend/Dockerfile`
- `web/backend/docs/API_MIGRATION_GUIDE.md`

## Executive Summary
`web/backend/app/main.py` is the canonical runtime composition source-of-truth.

`web/backend/app/app_factory.py` should currently be classified as a compatibility-retained, test-oriented app factory rather than as a peer runtime assembly path. It is not merely a thin wrapper around `main.py`; it has drifted into a partially separate composition stack with different middleware, exception handling, and route/bootstrap behavior.

## Evidence For Canonical Runtime Truth
- Runtime and deployment commands consistently target `app.main:app`:
  - `web/backend/ecosystem.config.js`
  - `web/backend/Dockerfile`
  - `web/backend/start_server.py`
  - `web/backend/load_env.py`
  - `web/backend/start_backend.sh`
  - additional scripts under `scripts/` and `web/backend/`
- `web/backend/app/main.py` invokes `register_api_routes(app, ...)` and therefore acts as the actual assembled runtime application surface.

## Evidence For `app_factory.py` Current Role
- Observed direct code usage is test-heavy, especially in `web/backend/tests/test_csrf_protection.py`.
- No equivalent deployment evidence was found showing `create_app()` as the primary production or dev runtime target.
- `web/backend/docs/API_MIGRATION_GUIDE.md` still references `app_factory.py` as an initialization example, which indicates documentation lag rather than runtime truth.

## Composition Drift Findings

### 1. Exception handling stacks differ
- `main.py` uses `register_exception_handlers`
- `app_factory.py` uses `register_global_exception_handlers`
- This is not a trivial naming difference; it indicates two different exception pipelines are being maintained.

### 2. Middleware stacks differ
- `main.py` includes `PerformanceMiddleware`
- `app_factory.py` does not include the same runtime stack
- `app_factory.py` includes request logging middleware not mirrored the same way in `main.py`
- CSRF logic is similar in intent but not identical in exclusion and enforcement details

### 3. Lifecycle behavior differs
- `main.py` includes more runtime-specific startup behavior, such as:
  - readiness-related imports
  - monitoring async pool initialization
  - development-mode conditional DB continuation
  - realtime MTM initialization
- `app_factory.py` remains closer to a simplified boot sequence

### 4. Router/bootstrap truth differs
- `main.py` explicitly delegates route assembly to `router_registry.register_api_routes(...)`
- `app_factory.py` did not show the same central registry delegation in the inspected runtime path and instead keeps more local bootstrap concerns inline
- This increases the risk that test-created app instances diverge from actual runtime behavior

### 5. Shared concerns have duplicated implementations
- CSRF token management logic exists in both files with materially different behavior:
  - `main.py` adds Redis-backed persistence with fallback
  - `app_factory.py` keeps a simpler in-memory interpretation while tests import its `csrf_manager`
- This means the same named concern does not share a single implementation truth

## Classification Decision

### Canonical path
- `web/backend/app/main.py`
- Role: runtime application composition truth

### Non-canonical retained path
- `web/backend/app/app_factory.py`
- Current role: compatibility-retained / test-oriented factory
- Allowed short-term purpose:
  - test bootstrapping
  - compatibility for legacy docs or helper imports during transition

### Not currently supported as truth
- treating `app_factory.py` as a semantically equivalent composition wrapper around `main.py`
- treating both files as peer runtime entrypoints

## Closure Recommendation

### Recommended target state
`app_factory.py` should become one of the following, explicitly and not ambiguously:

1. a thin delegated wrapper over canonical runtime composition
2. a clearly scoped test factory with documented intentional deviations
3. a retired path after callers migrate

Current repo truth best supports option 2 in the immediate term, followed by option 1 or retirement in a later implementation wave.

### Immediate governance outcome
- mark `main.py` as canonical runtime composition truth
- mark `app_factory.py` as compatibility-retained test factory
- forbid future feature-bearing runtime divergence between the two paths

## Risks Found

### 1. Test/runtime mismatch risk
Because tests instantiate `create_app()` while production boots `main.py`, middleware behavior, exception format, lifecycle hooks, and route surfaces may diverge silently.

### 2. Documentation drift risk
Some guidance still references `app_factory.py` as the default initialization site, which can mislead future implementation work.

### 3. Duplicate maintenance risk
Shared platform concerns like CSRF, exception handling, and startup wiring are at risk of being fixed in one path and forgotten in the other.

## Recommended Next Steps
1. In the OpenSpec program, formalize `main.py` as canonical runtime composition truth.
2. Reclassify `app_factory.py` in design/tasks as compatibility-retained test factory.
3. In a later implementation wave, either delegate `app_factory.create_app()` to canonical composition assembly or reduce its scope to explicitly documented test-only concerns.
4. Update docs that still imply `app_factory.py` is the primary initialization truth.
