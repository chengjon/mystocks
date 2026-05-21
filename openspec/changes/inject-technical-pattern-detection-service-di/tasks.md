> **历史文档说明**:
> These tasks are the proposed execution checklist for the D2.1a child change.
> They MUST remain unchecked and unexecuted until this change is explicitly
> approved for implementation and a separate child execution item is authorized.

## 0. Approval Gate

- [ ] 0.1 Confirm this OpenSpec change is explicitly approved for
      implementation.
- [ ] 0.2 Confirm a separate D2.1a child issue or approved implementation
      record exists for execution.
- [ ] 0.3 Confirm issue `#92` remains the parent decision rollup and is not used
      as the `ready-for-agent` implementation vehicle.
- [ ] 0.4 Confirm the only planned write scope is:
      `web/backend/app/api/_technical_patterns_router.py` and
      `web/backend/tests/test_technical_patterns_router_regressions.py`.

## 1. Pre-Edit Baseline

- [ ] 1.1 Run GitNexus impact/context for
      `TechnicalPatternDetectionService`.
- [ ] 1.2 Run GitNexus impact/context for `_detect_patterns_for_symbol`.
- [ ] 1.3 Record current `app.main` import smoke result.
- [ ] 1.4 Run the current focused route regression tests before editing:
      `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_technical_patterns_router_regressions.py -q --no-cov`.

## 2. TDD Red

- [ ] 2.1 Add a route-level test double with async `detect_for_symbol`.
- [ ] 2.1a Confirm the test double's async `detect_for_symbol` signature
      exactly matches the production service method signature used by the route
      seam, including `symbol` and `period`.
- [ ] 2.2 Add a public-route test that installs the double through
      `app.dependency_overrides`.
- [ ] 2.3 Run the focused route test and confirm it fails for the expected
      reason before implementation.

## 3. Implementation

- [ ] 3.1 Add `Depends` to `_technical_patterns_router.py`.
- [ ] 3.2 Add route-local
      `get_technical_pattern_detection_service()`.
- [ ] 3.3 Update `_detect_patterns_for_symbol` to receive a service argument.
- [ ] 3.4 Update the public route handler to receive the service through
      `Depends(get_technical_pattern_detection_service)` and pass it to the
      helper.
- [ ] 3.5 Convert focused public-route tests to dependency overrides and remove
      public-route reliance on class-method monkeypatching for this seam.

## 4. Verification

- [ ] 4.1 Run:
      `PYTHONPATH=web/backend python -c "import app.main; print('ok')"`.
- [ ] 4.2 Run:
      `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_technical_pattern_detection_service.py web/backend/tests/test_technical_patterns_router_regressions.py -q --no-cov`.
- [ ] 4.3 Run ruff on touched backend files.
- [ ] 4.4 Run `openspec validate inject-technical-pattern-detection-service-di --strict`.
- [ ] 4.5 Stage only approved files and run GitNexus staged detect changes.

## 5. Closeout

- [ ] 5.1 Record implementation evidence with exact commands and results.
- [ ] 5.2 Update the steward tree node for D2.1a after review/merge.
- [ ] 5.3 Comment the implementation result back to issue `#92`, keeping `#92`
      as parent decision context rather than the executable issue.
