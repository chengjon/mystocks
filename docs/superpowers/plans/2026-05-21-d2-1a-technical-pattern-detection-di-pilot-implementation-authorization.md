# D2.1a Technical Pattern Detection DI Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-21
Parent issue: `#92`
Track: D2.1a `TechnicalPatternDetectionService` DI pilot
Base HEAD: `5ffc9fdfe845b511fe39294b06b063dd469c71df`
Status: implementation authorization plan prepared; implementation remains locked until separately approved

## Authorization Boundary

This plan is a concrete implementation package, not implementation approval by
itself. It may be executed only after a human maintainer explicitly approves a
separate D2.1a implementation issue or OpenSpec branch and marks that child item
ready for agent work.

This plan does not authorize:

- editing backend source from issue `#92` directly;
- moving issue `#92` to `ready-for-agent`;
- creating or editing OpenSpec changes/specs in this PR;
- expanding beyond `TechnicalPatternDetectionService` route-level dependency injection;
- modifying PM2, scripts, frontend, `docs/api`, route paths, response models, schemas, or pattern-detection algorithms.

## Current Evidence

| Item | Current fact |
|---|---|
| Service class | `web/backend/app/services/technical_pattern_detection_service.py::TechnicalPatternDetectionService` |
| Route consumer | `web/backend/app/api/_technical_patterns_router.py` |
| Current route seam | `_detect_patterns_for_symbol()` directly constructs `TechnicalPatternDetectionService()` |
| Public route | `detect_patterns()` calls `_detect_patterns_for_symbol()` and returns `UnifiedResponse[PatternDetectionData]` |
| Focused service tests | `web/backend/tests/test_technical_pattern_detection_service.py` |
| Focused route tests | `web/backend/tests/test_technical_patterns_router_regressions.py` |
| GitNexus service impact | `LOW`, `impactedCount=0`, `processes_affected=0` |
| GitNexus helper impact | `_detect_patterns_for_symbol` is `LOW`, direct caller is `detect_patterns()` only |

## Future Write Scope

Allowed implementation files after approval:

- `web/backend/app/api/_technical_patterns_router.py`
- `web/backend/tests/test_technical_patterns_router_regressions.py`

Read-only or verification-only files:

- `web/backend/app/services/technical_pattern_detection_service.py`
- `web/backend/tests/test_technical_pattern_detection_service.py`
- `docs/reports/quality/backend-di-pilot-technical-pattern-detection-design-2026-05-21.md`

Do not modify these in D2.1a unless a new approval explicitly expands scope:

- `web/backend/app/services/technical_pattern_detection_service.py`
- `web/backend/app/api/_technical_patterns_models.py`
- `web/backend/app/core/responses.py`
- `web/backend/app/core/exceptions.py`
- PM2, scripts, config, frontend, `docs/api`, and OpenSpec files

## Target Shape

The implementation should add a route-local provider:

```python
def get_technical_pattern_detection_service() -> TechnicalPatternDetectionService:
    return TechnicalPatternDetectionService()
```

It should pass the service into the private helper:

```python
async def _detect_patterns_for_symbol(
    symbol: str,
    period: str,
    service: TechnicalPatternDetectionService,
) -> list[PatternDetection]:
    return await service.detect_for_symbol(symbol=symbol, period=period)
```

The public route should receive the service through FastAPI dependency injection:

```python
service: TechnicalPatternDetectionService = Depends(get_technical_pattern_detection_service)
```

This pilot is route-level DI only. It must not refactor the internals of
`TechnicalPatternDetectionService`, `DataSourceFactory`, or the chart pattern
detector loader.

## Task 0: Implementation Gate

- [ ] Confirm a separate D2.1a implementation issue or OpenSpec branch exists.
- [ ] Confirm that child item, not issue `#92`, is approved for implementation.
- [ ] Confirm the child item names this plan and the exact allowed write scope.
- [ ] Confirm the child item includes rollback criteria and verification commands.
- [ ] Stop if any of the above is missing.

## Task 1: Pre-Edit Impact And Baseline

- [ ] Run GitNexus impact before editing:

```bash
gitnexus impact --target TechnicalPatternDetectionService --direction upstream
gitnexus impact --target _detect_patterns_for_symbol --direction upstream
```

- [ ] Expected current result:
  - `TechnicalPatternDetectionService`: LOW, 0 affected symbols/processes.
  - `_detect_patterns_for_symbol`: LOW, direct caller `detect_patterns()`.

- [ ] Run baseline import smoke:

```bash
PYTHONPATH=web/backend python -c "from app.api._technical_patterns_router import router; from app.services.technical_pattern_detection_service import TechnicalPatternDetectionService; print(router is not None, TechnicalPatternDetectionService.__name__)"
```

- [ ] Run focused baseline tests:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_technical_pattern_detection_service.py -q --no-cov
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_technical_patterns_router_regressions.py -q --no-cov
```

## Task 2: Add A Failing Route-Level DI Test

- [ ] Edit `web/backend/tests/test_technical_patterns_router_regressions.py`.
- [ ] Add a small async service double near the top of the file:

```python
class _PatternServiceDouble:
    def __init__(self, detections=None, error: Exception | None = None):
        self.detections = [] if detections is None else detections
        self.error = error
        self.calls = []

    async def detect_for_symbol(self, symbol: str, period: str):
        self.calls.append((symbol, period))
        if self.error is not None:
            raise self.error
        return self.detections
```

- [ ] Add a helper fixture or helper function that installs the dependency override and clears it after use:

```python
def _build_client_with_pattern_service(module, service):
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[module.get_technical_pattern_detection_service] = lambda: service
    return app, TestClient(app)
```

- [ ] Any test that calls this helper must clear `app.dependency_overrides` in `finally`.

- [ ] Add a failing test proving the public route uses the dependency override:

```python
def test_detect_patterns_uses_dependency_override_service():
    module = _import_patterns_router_module()
    service = _PatternServiceDouble()
    app, client = _build_client_with_pattern_service(module, service)

    try:
        response = client.get("/patterns/600519.SH", params={"period": "weekly"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert service.calls == [("600519.SH", "weekly")]
    payload = response.json()["data"]
    assert payload["symbol"] == "600519.SH"
    assert payload["period"] == "weekly"
    assert payload["status"] == "empty"
```

- [ ] Run only the new test and confirm it fails because `get_technical_pattern_detection_service` is not present yet:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_technical_patterns_router_regressions.py::test_detect_patterns_uses_dependency_override_service -q --no-cov
```

## Task 3: Implement Route-Level Provider Injection

- [ ] Edit `web/backend/app/api/_technical_patterns_router.py`.
- [ ] Add `Depends` to the FastAPI import:

```python
from fastapi import APIRouter, Depends, Path, Query, status
```

- [ ] Add the provider after constants and before helper functions:

```python
def get_technical_pattern_detection_service() -> TechnicalPatternDetectionService:
    return TechnicalPatternDetectionService()
```

- [ ] Change `_detect_patterns_for_symbol()` to accept the service:

```python
async def _detect_patterns_for_symbol(
    symbol: str,
    period: str,
    service: TechnicalPatternDetectionService,
) -> list[PatternDetection]:
    try:
        return await service.detect_for_symbol(symbol=symbol, period=period)
    except BusinessException:
        raise
    except Exception as exc:
        logger.warning(
            "technical_pattern_detection_failed",
            extra={"symbol": symbol, "period": period, "error": str(exc)},
        )
        raise BusinessException(
            message="Pattern analysis unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from exc
```

- [ ] Change the public route signature to receive the dependency:

```python
async def detect_patterns(
    symbol: str = Path(..., description="Stock symbol, e.g. 600519.SH"),
    period: str = Query("daily", description="K-line period", enum=SUPPORTED_PATTERN_PERIODS),
    service: TechnicalPatternDetectionService = Depends(get_technical_pattern_detection_service),
) -> UnifiedResponse[PatternDetectionData]:
```

- [ ] Pass the service into the helper:

```python
detections = await _detect_patterns_for_symbol(
    symbol=normalized_symbol,
    period=normalized_period,
    service=service,
)
```

- [ ] Keep route path, response model, response shape, error message, and OpenAPI period enum unchanged.

## Task 4: Convert Focused Route Tests To Dependency Overrides

- [ ] Update direct route-function tests to pass an explicit service double:

```python
service = _PatternServiceDouble()
response = asyncio.run(module.detect_patterns(symbol="600519.SH", period="weekly", service=service))
```

- [ ] Replace public-route monkeypatching with dependency overrides for route tests.

- [ ] In failure test, replace class monkeypatching with a failing service double:

```python
service = _PatternServiceDouble(error=RuntimeError("synthetic detector outage"))
app, client = _build_client_with_pattern_service(module, service)
```

- [ ] Keep helper-level monkeypatching only where the test intentionally exercises helper behavior, not public route dependency behavior.

- [ ] Ensure every `app.dependency_overrides` write is cleared in teardown or `finally`.

## Task 5: Run Focused Verification

- [ ] Run import smoke:

```bash
PYTHONPATH=web/backend python -c "from app.api._technical_patterns_router import router; from app.services.technical_pattern_detection_service import TechnicalPatternDetectionService; print(router is not None, TechnicalPatternDetectionService.__name__)"
```

- [ ] Run focused service tests:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_technical_pattern_detection_service.py -q --no-cov
```

- [ ] Run focused route tests:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_technical_patterns_router_regressions.py -q --no-cov
```

- [ ] Run lint on touched files:

```bash
ruff check web/backend/app/api/_technical_patterns_router.py web/backend/tests/test_technical_patterns_router_regressions.py
```

- [ ] If the service file remains untouched, do not include it in the staged implementation diff. It may still be linted as a read-only verification target if desired.

## Task 6: Pre-Commit Scope Gate

- [ ] Stage only the implementation files:

```bash
git add web/backend/app/api/_technical_patterns_router.py web/backend/tests/test_technical_patterns_router_regressions.py
```

- [ ] Run whitespace check:

```bash
git diff --cached --check
```

- [ ] Run GitNexus staged scope check:

```bash
gitnexus detect-changes --scope staged
```

- [ ] Stop if staged scope includes unrelated files.

## Rollback

Rollback is intentionally narrow:

1. Restore `_detect_patterns_for_symbol()` to direct `TechnicalPatternDetectionService()` construction.
2. Remove `Depends` import and `get_technical_pattern_detection_service()`.
3. Restore route tests to their pre-DI helper/class monkeypatch style.
4. Do not modify `TechnicalPatternDetectionService` internals during rollback.

## Acceptance Criteria

Implementation is complete only when:

- public route behavior remains unchanged;
- `UnifiedResponse[PatternDetectionData]` contract remains unchanged;
- OpenAPI period enum remains `daily`, `weekly`, `monthly`;
- route tests use `app.dependency_overrides` for the public-route service seam;
- dependency overrides are cleared after tests;
- focused service tests pass;
- focused route tests pass;
- lint passes for touched files;
- GitNexus staged detect reports only the intended implementation scope.

## Explicit Non-Goals

- Do not migrate DB/session-backed services.
- Do not introduce a global container or service registry.
- Do not use `app.state` for this first pilot unless a new approval expands scope.
- Do not refactor `DataSourceFactory`.
- Do not change pattern detection algorithms.
- Do not change route paths, response models, schemas, status codes, or docs/API examples.
- Do not run PM2 gates from this implementation issue unless a separate D2.6 approval exists.
- Do not treat this plan as approval to move issue `#92` to `ready-for-agent`.
