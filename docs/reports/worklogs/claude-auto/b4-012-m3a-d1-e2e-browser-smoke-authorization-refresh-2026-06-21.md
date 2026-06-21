# B4.012-M3a-D1 E2E Browser Smoke Authorization Refresh

Date: 2026-06-21
Repository: `/opt/claude/mystocks_spec`
Baseline HEAD: `34cb5748321a2f952ef17f2a38afe0b3de4f56bb`
Mode: no-source authorization refresh

## Scope

This review refreshes the D1 authorization package after the D parent was restored to `decision-prepared`.

The immediate target is only:

- `b4-012-m3a-d1-e2e-browser-smoke-authorization`

This package prepares authorization metadata only. It does not authorize implementation, does not edit tests, does not edit source/runtime, does not run or claim E2E acceptance, and does not accept any untracked frontend test provenance.

## Parent Gate Truth

- `b4-012-m3a-d-e2e-frontend-tests-split` is `decision-prepared`.
- `b4-012-m3a-d1-e2e-browser-smoke-authorization` is `blocked` with unblock target `authorization-prepared`.
- D1 may be restored to `authorization-prepared` because the B4.013 runtime-first blocker has been removed and the D parent now has fresh evidence.
- Restoring D1 to `authorization-prepared` is not implementation approval. The next gate remains explicit user approval for source/test edits.

## Allowed Implementation Paths For Future Approval

If a later source/test implementation package is explicitly approved, D1 should be limited to:

- `tests/e2e/specs/auth-optimized.spec.ts`
- `tests/e2e/specs/dashboard.spec.ts`
- `tests/e2e/test_fund_flow.py`
- `tests/e2e/test_login.py`
- `tests/e2e/test_risk.py`
- `tests/e2e/test_web_e2e.py`
- `docs/reports/worklogs/claude-auto/b4-012-m3a-d1-e2e-browser-smoke-closeout-2026-06-21.md`

## Forbidden Boundaries

D1 must not touch:

- `src/**`
- `web/frontend/src/**`
- `web/frontend/tests/**`
- `web/backend/**`
- `tests/dashboard/**`
- `tests/prototype/**`
- `tests/performance/**`
- `tests/data_sources/**`
- `openspec/**`
- `/opt/claude/openstock/**`
- ST-HOLD
- `marketKlineData`
- `web/frontend/src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts`
- `web/frontend/tests/unit/config/trading-style-normalization.spec.ts`
- generated/tooling artifacts
- untracked frontend test provenance
- external dirty files

## Fresh Dirty Surface

Current D1 candidate surface:

| Group | Count | Notes |
| --- | ---: | --- |
| `tests/e2e/**` dirty entries | 6 | Exactly the D1 tracked browser/business-smoke candidate set. |
| Tracked D1 candidates | 6 | All six allowed test files are currently tracked dirty. |
| Untracked D1 candidates | 0 | No untracked path belongs to D1. |
| Frontend test dirty entries outside D1 | 22 | Four tracked and eighteen untracked frontend test entries remain outside this authorization. |
| `marketKlineData` hotspot | 1 | Dirty but explicitly forbidden for D1. |
| `trading-style-normalization.spec.ts` hotspot | 1 | Dirty but explicitly forbidden for D1. |

Allowed candidate status:

- `tests/e2e/specs/auth-optimized.spec.ts`: tracked dirty
- `tests/e2e/specs/dashboard.spec.ts`: tracked dirty
- `tests/e2e/test_fund_flow.py`: tracked dirty
- `tests/e2e/test_login.py`: tracked dirty
- `tests/e2e/test_risk.py`: tracked dirty
- `tests/e2e/test_web_e2e.py`: tracked dirty

Runtime context for later verification:

- `mystocks-backend`: online, service URL `http://localhost:8020`
- `mystocks-frontend`: online, service URL `http://localhost:3020`

This is context only. No E2E pass/fail result is claimed in this no-source authorization refresh.

## Future Implementation Acceptance Gates

A later D1 implementation package should pass or explicitly document an environment-blocked skip for:

- `git diff --cached --check`
- Python syntax check for the four Python E2E files
- TypeScript/Playwright syntax or list check for the two Playwright specs
- focused pytest for Python E2E files when environment dependencies are available
- PM2-backed browser smoke command selected by the implementation scope
- GitNexus `verify-staged` and `detect-changes`, risk low
- OPENDOG verification fresh with no new failures
- staged files limited to the allowed D1 paths

## Decision

D1 can move from `blocked` to `authorization-prepared` with refreshed evidence and a refreshed task card.

This decision does not approve implementation. It only prepares the exact future implementation boundary so the next user approval can be narrow, auditable, and isolated from frontend source dirty files, OpenStock/provider work, and unrelated residual test families.
