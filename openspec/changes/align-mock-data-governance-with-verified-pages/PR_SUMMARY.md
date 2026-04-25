# PR Summary

Commit:

- `6fc910be4` `frontend: align mock governance with verified pages`

Title:

- `frontend: align mock governance with verified pages`

## Summary

- Align verified-page runtime behavior with the documented mock governance rules.
- Remove silent mock fallback from verified-path strategy and market adapter flows.
- Remove legacy `VITE_APP_MODE` service-layer endpoint switching from strategy runtime behavior.
- Keep explicit mock mode on `VITE_USE_MOCK_DATA` through the shared frontend client path.
- Add OpenSpec change artifacts, closeout evidence, archive-readiness notes, and a page-level mock governance audit ledger.

## Included Files

- `docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md`
- `docs/guides/mock-data/MOCK_GOVERNANCE_AUDIT_LEDGER.md`
- `openspec/changes/align-mock-data-governance-with-verified-pages/ARCHIVE_READY.md`
- `openspec/changes/align-mock-data-governance-with-verified-pages/CLOSEOUT.md`
- `openspec/changes/align-mock-data-governance-with-verified-pages/design.md`
- `openspec/changes/align-mock-data-governance-with-verified-pages/proposal.md`
- `openspec/changes/align-mock-data-governance-with-verified-pages/specs/api-integration/spec.md`
- `openspec/changes/align-mock-data-governance-with-verified-pages/tasks.md`
- `web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md`
- `web/frontend/src/api/__tests__/strategy.test.ts`
- `web/frontend/src/api/adapters/marketAdapter.spec.ts`
- `web/frontend/src/api/adapters/marketAdapter.ts`
- `web/frontend/src/api/adapters/strategyAdapter.ts`
- `web/frontend/src/api/mockApiClient.ts`
- `web/frontend/src/api/services/strategyService.ts`
- `web/frontend/src/composables/useStrategy.ts`
- `web/frontend/tests/unit/mockApiClient-strategy-routes.spec.ts`

## Validation

- `openspec validate align-mock-data-governance-with-verified-pages --strict`
- `npm run test -- src/api/__tests__/strategy.test.ts src/api/adapters/marketAdapter.spec.ts src/api/services/__tests__/strategyService.msw.spec.ts src/composables/__tests__/useStrategy.spec.ts tests/unit/use-strategy.spec.ts tests/unit/config/console-log-cleanup-batch-21.spec.ts tests/unit/mockApiClient-strategy-routes.spec.ts`
- `gitnexus_detect_changes(scope:"staged")` before commit: `risk_level=low`

## Merge Notes

- This change is implementation-complete and committed.
- OpenSpec archive should wait until the corresponding runtime change is merged/deployed.
- Unrelated frontend auth/routing changes were intentionally excluded from this commit.
