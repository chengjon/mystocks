# B4.012-M3a-D E2E and frontend tests no-source split

Date: 2026-06-14
Mode: no-source split audit, no test/source/runtime cleanup authorization
Parent gate: `b4-012-m3a-tests-residual-domain-audit`

## Scope

This audit splits the E2E/frontend/UI test dirty domain into narrower future packages.

Included:

- tracked Playwright/browser smoke specs under `tests/e2e/**`
- tracked dashboard/UI-adjacent helper tests under `tests/dashboard/**`

Explicitly excluded:

- API route/dashboard tests already routed through M3a-B1/B2
- backend risk tests already routed through M3a-B3
- prototype acceptance E2E, which needs integration/prototype review before preservation
- runtime/performance frontend gate tests, which belong to M3a-E and M3a-U if untracked
- untracked contract E2E, which belongs to M3a-U provenance review
- any source, runtime, OpenSpec, OpenStock, deletion, restore, or staging action

## Current Dirty Summary

Measured from `git status --porcelain=v1 -- tests` on 2026-06-14.

Refined M3a-D tracked candidate count: 8.

Tracked E2E/browser candidates:

- `tests/e2e/specs/auth-optimized.spec.ts`
- `tests/e2e/specs/dashboard.spec.ts`
- `tests/e2e/test_fund_flow.py`
- `tests/e2e/test_login.py`
- `tests/e2e/test_risk.py`
- `tests/e2e/test_web_e2e.py`

Tracked dashboard/UI-adjacent candidates:

- `tests/dashboard/test_dashboard/create_dashboard_templates.py`
- `tests/dashboard/test_dashboard/dashboard_widget_type.py`

## Boundary Findings

The broad frontend/UI name scan found additional paths, but they are not accepted into D:

- API overlap remains in M3a-B1/B2:
  - `tests/api/file_tests/test_governance_dashboard_api.py`
  - `tests/api/file_tests/test_trade_routes_api.py`
- backend risk overlap remains in M3a-B3:
  - `tests/backend/test_risk_management_core.py`
  - `tests/backend/test_risk_management_regression.py`
- runtime/performance governance remains in M3a-E:
  - `tests/performance/test_build_runtime_quality_summary.py`
  - `tests/performance/test_collect_frontend_runtime_gate.py`
- prototype acceptance path needs separate integration/prototype review:
  - `tests/prototype/test_phase_0_e2e.py`
- untracked contract E2E remains in M3a-U:
  - `tests/integration/contract/test_contract_validation_e2e.py`

## Suggested Follow-Up Packages

1. `B4.012-M3a-D1 E2E browser smoke authorization prep`
   - Candidate scope: `tests/e2e/**`.
   - Gate: frontend route/runtime environment review.

2. `B4.012-M3a-D2 dashboard UI-adjacent test authorization prep`
   - Candidate scope: tracked `tests/dashboard/**` UI helper tests.
   - Gate: dashboard view/helper truth review.

3. `B4.012-M3a-DX prototype E2E disposition review`
   - Candidate scope: `tests/prototype/test_phase_0_e2e.py`.
   - Gate: prototype ownership and acceptance-test boundary review.

## Non-Goals

- No test edits.
- No frontend/source/runtime/API/backend/OpenSpec/OpenStock edits.
- No test deletion, restore, or untracked staging.
- No acceptance of UI route or runtime behavior changes.

## Required Gates For This Audit Package

- exact staged allowlist of governance/report files only
- `git diff --cached --check`
- Function Tree validation
- GitNexus staged verification
- GitNexus staged detect-changes
- OPENDOG blocker check
- post-commit GitNexus index refresh

## Current Status

`source_edits_authorized: false`

This no-source split does not authorize E2E/frontend test implementation.
