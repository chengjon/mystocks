# B4.009 frontend state/API support preflight

Date: 2026-06-06
Branch: `wip/root-dirty-20260403`
Mode: `no-source`

## Governance boundary

This node inventories frontend state/API/support dirty items only. It does not edit, restore, stage, or commit frontend source, styles, tests, resources, or generated files.

Primary references:

- `architecture/STANDARDS.md`
- `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`
- `docs/reports/worklogs/claude-auto/b4-001-frontend-route-ui-dirty-atlas-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-002-frontend-deletion-candidate-inventory-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-003-route-header-residue-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-004-data-market-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-005-system-risk-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-006-strategy-trade-route-package-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-007-artdeco-root-legacy-route-truth-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-008-shared-ui-component-preflight-2026-06-06.md`

Fixed isolation list excluded from this package:

- B4.002 deletion-retirement items.
- B4.003 route-header group.
- B4.004 data/market.
- B4.005 system/risk.
- B4.006 strategy/trade, including ST-HOLD high-lock items.
- B4.007 ArtDeco/root legacy route-truth rows already archived.
- B4.008 shared UI/component rows already archived.

Stale OPENDOG evidence remains non-blocking for this no-source inventory. Later source-authorized or deletion-retirement work must refresh evidence or explicitly accept the stale caveat.

## Scan method

Read-only checks:

- Parse `git status --short -- web/frontend`.
- Extract archived `web/frontend/**` paths from B4.002-B4.008 reports and exclude them from this pass.
- Match remaining dirty paths against state/API/support patterns:
  - `web/frontend/src/api/**`
  - `web/frontend/src/stores/**`
  - `web/frontend/src/services/**`
  - `web/frontend/src/types/**`
  - `web/frontend/src/utils/**`
  - `web/frontend/src/config/**`
  - `web/frontend/src/mock/**` and `web/frontend/src/mocks/**`
  - support tests whose paths include API, store, service, contract, mock, utils, or state evidence.

Important result: after applying the fixed B4.002-B4.008 exclusions, there are no remaining dirty `src/api`, `src/stores`, `src/services`, `src/types`, `src/config`, `src/mock`, or `src/mocks` source paths in this package. B4.009 therefore reduces to test evidence that references API/mock/utils support behavior.

## Summary

| Bucket | Count | Status | Risk | Notes |
| --- | ---: | --- | --- | --- |
| `support-test-evidence` | 5 | modified | Medium | API/mock/utils related test evidence only; pair with later source-authorized decisions if accepted. |

Total B4.009 candidates: 5.

Risk distribution:

| Risk | Count | Reason |
| --- | ---: | --- |
| High | 0 | No remaining source API/store/service/type contract dirty paths after exclusions. |
| Medium | 5 | Modified tests can encode support behavior expectations but do not change runtime source in this no-source pass. |
| Low | 0 | No pure documentation-only support candidate in this package. |

## Candidate rows

| Path | Status | Bucket | Risk | Notes |
| --- | --- | --- | --- | --- |
| `web/frontend/tests/api/mockApiClient.spec.ts` | modified | `support-test-evidence` | Medium | Mock API client behavior evidence. |
| `web/frontend/tests/e2e/api-integration.spec.ts` | modified | `support-test-evidence` | Medium | API integration E2E evidence; do not mix with Playwright config/tooling cleanup. |
| `web/frontend/tests/unit/utils/indexedDB.spec.ts` | modified | `support-test-evidence` | Medium | IndexedDB support utility evidence. |
| `web/frontend/tests/unit/utils/indicators-extended.test.ts` | modified | `support-test-evidence` | Medium | Indicator utility extended behavior evidence. |
| `web/frontend/tests/unit/utils/indicators.test.ts` | modified | `support-test-evidence` | Medium | Indicator utility baseline behavior evidence. |

## Proposed package order

| Package | Rows | Authority needed later | Recommendation |
| --- | ---: | --- | --- |
| SA-1 api/mock support evidence | 2 | source-authorized test package | Pair `mockApiClient.spec.ts` and `api-integration.spec.ts` only after API/mock runtime truth is named. |
| SA-2 utility support evidence | 3 | source-authorized test package | Pair IndexedDB and indicator tests with the relevant utility source review. |

Do not stage these rows directly from B4.009. They are evidence rows, not acceptance of test behavior or runtime source changes.

## Out-of-scope carry-forward

The remaining dirty frontend rows after B4.002-B4.008 exclusions are not state/API support candidates by this pass. They include tooling/config/static/governance surfaces such as frontend package metadata, Playwright config, public manifest/service worker, scripts, generic ArtDeco/style tests, `.omc` state, and frontend-local worklogs. These should be handled by a later tooling/config/static-governance preflight instead of being mixed into B4.009.

## Verification performed

Read-only checks only:

- Frontend dirty status parse.
- Fixed B4.002-B4.008 exclusion filtering.
- State/API/support pattern classification.
- Risk and package classification.

Not run:

- Frontend build
- Frontend type check
- Vitest
- Playwright/E2E
- PM2 service checks

Reason: B4.009 is a no-source preflight and does not modify or accept frontend source/test changes.
