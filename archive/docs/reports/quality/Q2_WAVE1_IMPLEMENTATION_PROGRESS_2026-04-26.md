# Q2 Wave 1 Implementation Progress

Date: 2026-04-26
Wave: `Wave 1 / Backend Composition And Realtime Truth Convergence`
Mode: single-CLI execution
Related plan:
- `docs/reports/quality/Q2_WAVE1_BACKEND_REALTIME_CLOSURE_BATCH_PLAN_2026-04-25.md`

## Summary

Wave 1 implementation has started in a deliberately conservative mode.

The current implementation batch focuses on truth labeling and minimal drift containment. It does not yet attempt backend composition unification or realtime connection-manager consolidation.

## Batch Status

### Batch 1: Canonical Truth Labeling
Status: complete

Completed outcomes:
- high-signal docs no longer present `app_factory.py` as a peer runtime truth
- high-signal docs no longer present Socket.IO as the verified current public canonical transport
- canonical wording now consistently points to:
  - runtime composition truth: `app.main:app`
  - public canonical realtime transport: FastAPI WebSocket route family
  - `app_factory.py`: compatibility-retained / test-scoped factory
  - Socket.IO: compatibility-retained / non-canonical until verified runtime mount exists

Updated files:
- `web/backend/docs/API_MIGRATION_GUIDE.md`
- `docs/overview/IFLOW.md`
- `docs/overview/项目总览.md`

### Batch 2: Backend Composition Drift Containment
Status: complete

Completed outcomes:
- code-level role notes now explicitly distinguish canonical runtime entrypoint from compatibility-retained test factory
- runtime-truth metadata was added to both composition paths through `app.state`
- tests now contain an explicit compatibility-retained assertion for the `create_app()` path instead of relying only on narrative comments
- compatibility scope is now explicitly constrained with:
  - `bootstrap_scope = tests_and_legacy_bootstrap_only`
  - `runtime_divergence_policy = must_not_gain_new_runtime_only_behavior`
- compatibility-retained comments now mark:
  - Socket.IO status exposure in `app_factory.py` as non-canonical
  - router registration in `app_factory.py` as test/bootstrap-oriented rather than peer runtime assembly truth

Updated files:
- `web/backend/app/app_factory.py`
- `web/backend/app/main.py`
- `web/backend/tests/test_csrf_protection.py`

Deferred beyond Batch 2:
- any deeper shared assembly extraction
- any reduction of middleware or lifecycle drift
- any change to router registration structure

### Batch 3: Realtime Registry Alignment
Status: complete

Completed outcomes:
- high-signal API reference docs now explicitly distinguish:
  - canonical runtime truth: `app.main:app`
  - canonical public realtime transport: FastAPI WebSocket route family
  - Socket.IO status surfaces: compatibility-retained / non-canonical
- top-level overview wording no longer treats Socket.IO as the default public realtime truth
- API exploration and reference index docs now carry explicit Q2 closure notes so historical exploration content is not misread as current runtime truth
- the current high-signal overview/reference pass is complete without expanding into low-signal historical archive cleanup

Updated files:
- `web/backend/API_QUICK_REFERENCE.md`
- `web/backend/API_ARCHITECTURE_ANALYSIS.md`
- `web/backend/API_EXPLORATION_INDEX.md`
- `docs/overview/IFLOW.md`

Deferred beyond Batch 3:
- lower-signal historical docs may still mention older Socket.IO or SSE framing and should be treated as follow-up cleanup
- connection-manager consolidation remains deferred
- no realtime transport redesign is implied by this registry-alignment batch

### Batch 4: Follow-Up Debt Capture
Status: complete

Completed outcomes:
- unresolved Wave 1 items are now explicitly captured rather than left implicit
- Wave 1 now distinguishes between completed truth-locking work and deferred backend/realtime cleanup
- follow-up categories are explicitly recorded for:
  - connection-manager consolidation
  - `realtime_market.py` inconsistency repair
  - `app_factory.py` long-term disposition
  - Socket.IO future decision
  - deeper test/runtime drift reduction

Updated files:
- `docs/reports/quality/Q2_WAVE1_FOLLOWUP_DEBT_CAPTURE_2026-04-26.md`

## Risk Posture

`create_app` has already been confirmed as a HIGH upstream-impact symbol because it is called directly by the CSRF test suite.

For that reason, the current implementation intentionally avoids:
- changing route registration behavior
- changing middleware ordering
- changing CSRF logic
- changing lifecycle behavior

## Verification Notes

### Verified
- targeted doc review confirms the updated canonical wording in the edited high-signal documents
- the code diff remains narrow and limited to Wave 1 Batch 1 and Batch 2 surfaces

### Attempted But Environment-Limited
- `pytest web/backend/tests/test_csrf_protection.py -q`
- `pytest -n 0 web/backend/tests/test_csrf_protection.py -q`
- direct `python` import of `app.app_factory.create_app()`

Observed blocker:
- importing the backend settings chain in the current sandbox hits `PermissionError: [Errno 13] Permission denied: '.env'` at `web/backend/.env`

Interpretation:
- current validation is limited by environment access, not by an observed application failure introduced in this batch
- no failing test stack attributable to the code changes was obtained in this session

## Next Recommended Step

Wave 1 implementation may now be treated as closed at the truth-locking level.

Recommended continuation:
- move to Wave 2 ownership closure
- or open a separate approved cleanup batch if the team wants to reduce deferred Wave 1 backend/realtime debt before Wave 2
