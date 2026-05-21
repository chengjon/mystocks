# Backend DI Pilot: Technical Pattern Detection Design

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

- Date: 2026-05-21
- Status: design packet prepared
- Parent issue: <https://github.com/chengjon/mystocks/issues/92>
- Parent split acceptance: `docs/reports/quality/backend-openspec-issue92-downstream-split-acceptance-2026-05-21.md`
- Track: D2.1 `select-backend-technical-pattern-di-pilot`
- Base HEAD: `f95266cd5338480247a9730e5b273ff7bc072216`

## Boundary

This is a design packet only. It does not authorize backend implementation,
source edits, route mutation, test mutation, PM2 execution, or movement of any
issue to `ready-for-agent`.

Implementation must still be authorized by a separate concrete issue or
OpenSpec branch before any source file is edited.

## Candidate

| Field | Value |
|---|---|
| Service | `TechnicalPatternDetectionService` |
| Service file | `web/backend/app/services/technical_pattern_detection_service.py` |
| Route consumer | `web/backend/app/api/_technical_patterns_router.py` |
| Route direct construction | `_detect_patterns_for_symbol()` currently constructs `TechnicalPatternDetectionService()` directly |
| Focused tests | `web/backend/tests/test_technical_pattern_detection_service.py`; `web/backend/tests/test_technical_patterns_router_regressions.py` |
| GitNexus impact | `LOW`, `impactedCount=0`, `processes_affected=0` |

## Why This Pilot

`TechnicalPatternDetectionService` is a narrow service candidate with a single
route consumer and focused regression tests. It is a better first DI design
pilot than broader service candidates because it avoids the DB/session-backed,
external-client, cache/task-running, and process-level singleton buckets that
were intentionally kept out of generic lifecycle batches.

The goal is not to solve every service lifecycle problem. The goal is to define
one repeatable, reviewable pattern for:

- route-level provider naming;
- FastAPI test override mechanics;
- teardown discipline;
- rollback;
- evidence required before a future implementation issue can be marked
  `ready-for-agent`.

## Proposed Implementation Shape

The future implementation, if separately approved, should be limited to the
route helper and its focused tests.

Proposed provider shape:

```python
def get_technical_pattern_detection_service() -> TechnicalPatternDetectionService:
    return TechnicalPatternDetectionService()
```

Proposed route helper shape:

```python
async def _detect_patterns_for_symbol(
    symbol: str,
    period: str,
    service: TechnicalPatternDetectionService,
) -> list[PatternDetection]:
    return await service.detect_for_symbol(symbol=symbol, period=period)
```

The public route should receive the service through FastAPI dependency
injection. The implementation plan must choose the final import style and
signature in the concrete implementation issue, but it should preserve the
existing `UnifiedResponse[PatternDetectionData]` contract.

## Dependency Override Strategy

Use FastAPI `app.dependency_overrides` in route regression tests.

Required test fixture behavior:

- install an override for `get_technical_pattern_detection_service`;
- return a test double with an async `detect_for_symbol()` method;
- clear `app.dependency_overrides` in teardown;
- avoid module-level monkeypatching of `TechnicalPatternDetectionService` when
  exercising the public route.

## Teardown Artifact

The teardown artifact should be a pytest fixture local to the route regression
test module.

If the future implementation uses `app.state`, the fixture must also remove the
selected app-state key. This design packet does not recommend `app.state` for
the first pilot; provider construction is sufficient for the initial pattern.

## Rollback

Rollback path:

1. Revert the public route signature and helper signature to their previous
   direct-construction shape.
2. Restore `service = TechnicalPatternDetectionService()` inside
   `_detect_patterns_for_symbol()`.
3. Remove the provider override fixture from focused tests.
4. Keep service implementation code unchanged.

## Verification Required Before Implementation Approval

The concrete implementation issue or OpenSpec branch must name and run these
checks before it can be considered complete:

| Gate | Command |
|---|---|
| Import smoke | `PYTHONPATH=web/backend python -c "from app.api._technical_patterns_router import router; from app.services.technical_pattern_detection_service import TechnicalPatternDetectionService; print(router is not None, TechnicalPatternDetectionService.__name__)"` |
| Focused service tests | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_technical_pattern_detection_service.py -q --no-cov` |
| Focused route tests | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_technical_patterns_router_regressions.py -q --no-cov` |
| Lint touched files | `ruff check web/backend/app/api/_technical_patterns_router.py web/backend/app/services/technical_pattern_detection_service.py web/backend/tests/test_technical_patterns_router_regressions.py` |
| GitNexus pre-edit impact | `impact(target="TechnicalPatternDetectionService", direction="upstream")` and impact/context for `_technical_patterns_router.py` or the edited route helper before source edits |
| GitNexus pre-commit scope | `detect_changes(scope="staged")` after staging only the intended implementation batch |

## Non-Goals

- Do not migrate DB/session-backed services in this pilot.
- Do not introduce a global service container.
- Do not alter `PatternDetection`, `PatternDetectionData`, or
  `UnifiedResponse[PatternDetectionData]`.
- Do not change technical pattern algorithm behavior.
- Do not modify PM2 workflows.
- Do not mark any issue `ready-for-agent` from this design packet alone.

## Acceptance For This Design Packet

This packet is complete when:

- the candidate is recorded as `TechnicalPatternDetectionService`;
- dependency override, teardown, rollback, and verification gates are named;
- the steward tree records D2.1 as `design-packet-prepared`;
- issue `#92` is linked back to this design packet;
- implementation remains locked behind a separate approval.

