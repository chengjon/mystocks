# MOCK Governance Alignment Patch Summary

Date: 2026-04-25

## Patch File

- `docs/reports/tasks/mock-governance-alignment-2026-04-25.patch`

## Scope

This patch contains only the files changed for the `align-mock-data-governance-with-verified-pages` OpenSpec implementation batch.

### Included Areas

- OpenSpec change artifacts
  - `openspec/changes/align-mock-data-governance-with-verified-pages/*`
- Mock governance docs
  - `docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md`
  - `docs/guides/mock-data/MOCK_GOVERNANCE_AUDIT_LEDGER.md`
- Frontend runtime/documentation alignment
  - `web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md`
  - `web/frontend/src/api/services/strategyService.ts`
  - `web/frontend/src/api/adapters/strategyAdapter.ts`
  - `web/frontend/src/api/adapters/marketAdapter.ts`
  - `web/frontend/src/composables/useStrategy.ts`
  - `web/frontend/src/api/mockApiClient.ts`
- Targeted tests
  - `web/frontend/src/api/__tests__/strategy.test.ts`
  - `web/frontend/src/api/adapters/marketAdapter.spec.ts`
  - `web/frontend/tests/unit/mockApiClient-strategy-routes.spec.ts`

## Key Outcomes

- Removed service-level `VITE_APP_MODE` switching from strategy service runtime behavior
- Kept `VITE_USE_MOCK_DATA` through shared `apiClient` as the active frontend mock-mode truth
- Removed adapter-layer silent mock fallback for strategy and market verified-path adapters
- Updated strategy detail consumer behavior to surface explicit failure instead of mock substitution
- Preserved explicit mock mode by adding `/v1/strategy/*` handlers to `mockApiClient`
- Added a page/layer governance audit ledger for mock usage classification

## Validation Performed

### OpenSpec

- `openspec validate align-mock-data-governance-with-verified-pages --strict`

### Frontend Tests

- `npm run test -- src/api/__tests__/strategy.test.ts src/api/adapters/marketAdapter.spec.ts src/api/services/__tests__/strategyService.msw.spec.ts src/composables/__tests__/useStrategy.spec.ts tests/unit/use-strategy.spec.ts tests/unit/config/console-log-cleanup-batch-21.spec.ts`
  - Result: `6` files passed, `38` tests passed
- `npm run test -- tests/unit/mockApiClient-strategy-routes.spec.ts`
  - Result: `1` file passed, `2` tests passed

## Suggested Commit Title

- `refactor[frontend-mock]: align verified pages with mock governance rules`

## Suggested Commit Body

- remove strategy service dual-truth runtime switching
- remove adapter silent mock fallback from verified paths
- keep explicit mock mode via VITE_USE_MOCK_DATA and shared apiClient
- add mock governance audit ledger and closeout evidence
