# Backend Technical Pattern DI Pilot Implementation

> **历史文档说明**:
> This report records the D2.1a implementation evidence for review. It is not a
> new source of runtime truth, does not authorize broader service DI migration,
> and does not move issue `#92` to `ready-for-agent`.

## Summary

D2.1a implemented the first service-tier route-level DI pilot for
`TechnicalPatternDetectionService`.

The implementation is intentionally narrow:

- Added a route-local FastAPI provider:
  `get_technical_pattern_detection_service()`.
- Injected that provider into the existing technical pattern route handler.
- Updated `_detect_patterns_for_symbol()` to receive the service dependency
  instead of constructing it directly.
- Converted focused public-route tests to `app.dependency_overrides` with an
  async service double whose `detect_for_symbol(symbol, period)` signature
  matches the production service method.

No route path, response contract, OpenAPI exposure policy, service internals,
`DataSourceFactory`, chart detector loading, PM2 workflow, frontend file, or
`docs/api/` artifact was changed.

## Changed Files

- `web/backend/app/api/_technical_patterns_router.py`
- `web/backend/tests/test_technical_patterns_router_regressions.py`
- `openspec/changes/inject-technical-pattern-detection-service-di/tasks.md`
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `docs/FUNCTION_TREE.md`
- `governance/function-tree/catalog.yaml`
- `docs/reports/quality/backend-technical-pattern-di-pilot-implementation-2026-05-21.md`
- `governance/mainline/task-cards/pr-112.yaml`

## Pre-Edit Impact

GitNexus impact/context was run before source edits:

- `TechnicalPatternDetectionService`
  - risk: `LOW`
  - impacted count: `0`
  - affected processes: `0`
- `_detect_patterns_for_symbol`
  - risk: `LOW`
  - impacted count: `1`
  - direct caller: `detect_patterns`
  - affected processes: `0`
- `web/backend/app/api/_technical_patterns_router.py`
  - risk: `LOW`
  - direct importer: `web/backend/app/api/technical_analysis.py`

An additional exact-context lookup for
`web/backend/app/api/_technical_patterns_router.py::detect_patterns` showed no
incoming graph callers and outgoing calls only to `_normalize_pattern_period`
and `_detect_patterns_for_symbol`.

## Baseline

Focused route regression baseline before implementation:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_technical_patterns_router_regressions.py -q --no-cov
8 passed in 2.13s
```

Bare `app.main` import without environment placeholders failed on required
configuration, not on the D2.1a route import path:

```text
missing: POSTGRESQL_HOST, POSTGRESQL_USER, POSTGRESQL_PASSWORD,
JWT_SECRET_KEY, BACKEND_PORT, BACKEND_BACKUP_PORT
```

Placeholder-env import smoke passed before and after implementation:

```text
env POSTGRESQL_HOST=localhost POSTGRESQL_USER=test POSTGRESQL_PASSWORD=test \
  JWT_SECRET_KEY=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
  BACKEND_PORT=8888 BACKEND_BACKUP_PORT=8889 \
  PYTHONPATH=web/backend python -c "import app.main; print('app_main_import=ok')"
app_main_import=ok
```

## TDD Evidence

Red test added first:

```text
PYTHONPATH=web/backend pytest -o addopts= \
  web/backend/tests/test_technical_patterns_router_regressions.py::test_detect_patterns_uses_dependency_override_service \
  -q --no-cov
FAILED ... AttributeError: module 'app.api._technical_patterns_router' has no
attribute 'get_technical_pattern_detection_service'
```

After implementation, the same test passed:

```text
1 passed in 1.76s
```

The full focused route regression suite passed:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_technical_patterns_router_regressions.py -q --no-cov
9 passed in 1.80s
```

## Verification

Focused service and route verification:

```text
PYTHONPATH=web/backend pytest -o addopts= \
  web/backend/tests/test_technical_pattern_detection_service.py \
  web/backend/tests/test_technical_patterns_router_regressions.py \
  -q --no-cov
19 passed in 1.84s
```

Ruff on touched backend files:

```text
PYTHONPATH=web/backend python -m ruff check \
  web/backend/app/api/_technical_patterns_router.py \
  web/backend/tests/test_technical_patterns_router_regressions.py
All checks passed!
```

OpenSpec strict validation:

```text
openspec validate inject-technical-pattern-detection-service-di --strict
Change 'inject-technical-pattern-detection-service-di' is valid
```

Runtime import smoke with placeholder environment values:

```text
PYTHONPATH=web/backend POSTGRESQL_HOST=localhost POSTGRESQL_USER=test \
  POSTGRESQL_PASSWORD=test JWT_SECRET_KEY=test-secret-key-for-import-smoke-only-1234567890 \
  BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 \
  python -c 'import app.main; print("app_main_import=ok")'
app_main_import=ok
```

GitNexus staged detect after staging the approved file set:

```text
scope: staged/compare
changed_files: 8 after function-tree documentation synchronization
risk_level: low
changed_symbols: 0
affected_processes: 0
```

Function-tree synchronization:

- `governance/function-tree/catalog.yaml` now maps
  `web/backend/app/api/_technical_patterns_router.py` and
  `web/backend/tests/test_technical_patterns_router_regressions.py` under
  `domain-02-node-03`.
- `docs/FUNCTION_TREE.md` mirrors the same technical-pattern route companion and
  focused regression test entry.

Postcommit governance gates:

```text
git diff a79aeab99c74342499e341ea92ea2c85a2aea6af..HEAD --check
pass

python scripts/compliance/markdown_governance_gate.py --root-dir . --format json \
  .planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md \
  docs/FUNCTION_TREE.md \
  docs/reports/quality/backend-technical-pattern-di-pilot-implementation-2026-05-21.md \
  openspec/changes/inject-technical-pattern-detection-service-di/tasks.md
errors: 0

python governance/mainline/scripts/mainline_scope_gate.py \
  --task-card governance/mainline/task-cards/pr-112.yaml \
  --base-sha a79aeab99c74342499e341ea92ea2c85a2aea6af \
  --head-sha HEAD \
  --report /tmp/pr-112-mainline-postcommit.json \
  --fail-on-empty-diff
pass: true; changed_files: 8; violations: 0
```

## Boundary

This implementation closes only the D2.1a route-level DI pilot. It does not:

- authorize a second service DI pilot;
- add `app.state`, lifespan, singleton registry, or teardown ownership;
- change `TechnicalPatternDetectionService` internals;
- change route path, tags, operationId, OpenAPI schema exposure, or response
  model;
- change function-tree taxonomy beyond registering the existing technical
  pattern route companion and focused regression test under domain-02-node-03;
- move issue `#92` to `ready-for-agent`;
- change PM2, frontend, docs/API, scripts, config, or service behavior outside
  the approved route seam.
