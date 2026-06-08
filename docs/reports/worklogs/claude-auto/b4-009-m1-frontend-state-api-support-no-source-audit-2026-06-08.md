# B4.009-M1 Frontend State/API Support No-Source Audit

Date: 2026-06-08

Branch: `wip/root-dirty-20260403`

Audit HEAD: `64411dba119ebdedcda2f8e67c6d62f49783da6b`

FUNCTION_TREE node: `.governance/programs/artdeco-web-design-governance/cards/b4-frontend-state-api-support-truth.yaml`

Status: `evidence-prepared`

## Boundary

B4.007 and B4.008 are closed and sealed. This B4.009-M1 pass does not reopen route truth, root legacy archive work, shared UI/component packages, or any generated drift handled by those lines.

This is a no-source audit. It does not edit, restore, stage, or commit frontend source, tests, generated declarations, styles, route files, assets, or backend/API contracts. Any later source or test mutation requires a separate source-authorized M2 package.

Fixed exclusions:

- ST-HOLD.
- `marketKlineData`.
- B4.007 ArtDeco/root legacy route truth and archive packages.
- B4.008 shared UI/component packages.
- External held dirty file: `web/frontend/src/layouts/archive/BaseLayout.vue`.
- Backend/API contracts and unrelated dirty files.

## Inputs

- Prior preflight: `docs/reports/worklogs/claude-auto/b4-009-frontend-state-api-support-preflight-2026-06-06.md`.
- Closed B4.007 final report: `docs/reports/worklogs/claude-auto/b4-007-final-closeout-2026-06-08.md`.
- Closed B4.008 M3 report: `docs/reports/worklogs/claude-auto/b4-008-m3-shared-ui-component-full-validation-closeout-2026-06-08.md`.
- `architecture/STANDARDS.md`.
- `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`.
- Current targeted dirty status parse for `web/frontend`.
- Current text-reference scan for state/API/support candidate paths.
- GitNexus and OPENDOG advisory checks.

## Current Scan Summary

Fresh scan result at audit HEAD:

| Scope | Count | Notes |
| --- | ---: | --- |
| Total dirty entries | 1097 | Whole worktree still contains unrelated historical dirty rows. |
| Frontend dirty entries | 110 | `84` modified, `26` untracked. |
| Staged entries | 0 | Staging area was empty before this M1 evidence package. |
| B4.009 candidates | 16 | State/API/support paths only after fixed exclusions. |
| External held dirty | 1 | `web/frontend/src/layouts/archive/BaseLayout.vue`; not part of B4.009. |

The old 2026-06-06 B4.009 preflight is stale in one important way: it concluded that no runtime state/API/support source paths remained after B4.002-B4.008 exclusions. Current truth is different. B4.009 now contains both runtime support files and test evidence, so M2 must be split by family and risk.

## Family Matrix

| Family | Source paths | Test paths | Risk | M1 disposition |
| --- | ---: | ---: | --- | --- |
| SA-1 API/mock support evidence | 0 | 3 | Medium | Test-only package; do not mix with runtime store/service repairs. |
| SA-2 state stores + store tests | 2 | 1 | High | Highest priority because stores are active runtime state surfaces. |
| SA-3 data utility/service support | 3 | 4 | Medium | Pair utility/service source with matching unit evidence. |
| SA-4 strategy/trade adapter boundary | 3 | 0 | High | Separate high-lock package; requires B4.006/ST-HOLD boundary review before source authorization. |

Total candidates: 16.

Risk distribution:

| Risk | Count | Reason |
| --- | ---: | --- |
| High | 5 | Active store and cross-domain strategy/trade adapter source files. |
| Medium | 11 | API/mock tests, data utility/service source with focused tests, and new support test anchors. |
| Low | 0 | No pure documentation-only support candidate in this package. |

## Candidate Rows

| Family | Path | Status | Diff size | Reference signal | Risk |
| --- | --- | --- | --- | ---: | --- |
| SA-1 | `web/frontend/src/mock/__tests__/backtestWorkbenchMock.spec.ts` | modified | +19 / -1 | 2 | Medium |
| SA-1 | `web/frontend/tests/api/mockApiClient.spec.ts` | modified | +18 / -0 | 7 | Medium |
| SA-1 | `web/frontend/tests/e2e/api-integration.spec.ts` | modified | +11 / -7 | 0 | Medium |
| SA-2 | `web/frontend/src/stores/apiStores.ts` | modified | +1 / -1 | 12+ | High |
| SA-2 | `web/frontend/src/stores/marketData.ts` | modified | +1 / -1 | 12+ | High |
| SA-2 | `web/frontend/src/stores/__tests__/marketData.spec.ts` | untracked | 80 lines | 12+ | Medium |
| SA-3 | `web/frontend/src/services/indicatorService.ts` | modified | +37 / -8 | 4 | Medium |
| SA-3 | `web/frontend/src/utils/adapters.ts` | modified | +1 / -1 | 12+ | Medium |
| SA-3 | `web/frontend/src/utils/indexedDB.ts` | modified | +70 / -1 | 5 | Medium |
| SA-3 | `web/frontend/tests/unit/utils/indexedDB.spec.ts` | modified | +71 / -2 | 5 | Medium |
| SA-3 | `web/frontend/tests/unit/utils/indicators-extended.test.ts` | modified | +15 / -5 | 3 | Medium |
| SA-3 | `web/frontend/tests/unit/utils/indicators.test.ts` | modified | +15 / -5 | 12+ | Medium |
| SA-3 | `web/frontend/tests/unit/views/data-fund-flow-partial-state.spec.ts` | untracked | 118 lines | 0 | Medium |
| SA-4 | `web/frontend/src/utils/atrading.ts` | modified | +1 / -1 | 3 | High |
| SA-4 | `web/frontend/src/utils/strategy-adapters.ts` | modified | +1 / -1 | 8 | High |
| SA-4 | `web/frontend/src/utils/trade-adapters.ts` | modified | +1 / -1 | 4 | High |

Text-reference counts are risk signals from current repository text search, not a full import graph.

## GitNexus Signals

GitNexus MCP with repo alias `mystocks` was fresh at audit time:

- Indexed commit: `64411dba119ebdedcda2f8e67c6d62f49783da6b`.
- Current commit: `64411dba119ebdedcda2f8e67c6d62f49783da6b`.
- Stale: `false`.

`detect_changes(scope=all)` reported whole-worktree risk `high`:

- Changed files: 664.
- Changed symbols: 1915.
- Affected processes: 6.

This is a whole dirty-tree signal, not a B4.009 staged-package signal. It reinforces that B4.009 M2 must use exact path staging, staged GitNexus detection, and post-commit analyze for each source-authorized package.

## OPENDOG Signals

OPENDOG advisory verification was available:

- Verification status: `fresh`.
- Failing runs: `0`.
- Cleanup blockers: `0`.
- Refactor blockers: `0`.
- Cleanup/refactor gate: allowed with `caution`.

Caveats:

- OPENDOG recommends establishing a snapshot baseline before over-interpreting unused/hotspot guidance.
- Latest lint evidence is stale/advisory.
- Some recorded pass evidence used pipeline commands whose exit codes may be masked.
- OPENDOG remains advisory and does not replace Git, GitNexus, type-check, unit tests, E2E, or explicit source authorization.

## Recommended Execution Order

1. B4.009-M2a: SA-2 state stores + store tests.
   - Paths: `apiStores.ts`, `marketData.ts`, `src/stores/__tests__/marketData.spec.ts`.
   - Reason: active runtime stores with broad route/view/test references.
   - Gate emphasis: GitNexus impact for store symbols, `npm run type-check`, focused store unit tests, stable unit suite, PM2 business smoke.
2. B4.009-M2b: SA-3 data utility/service support.
   - Paths: `indicatorService.ts`, `adapters.ts`, `indexedDB.ts`, IndexedDB/indicator/data fund-flow tests.
   - Reason: utility/service support surface with matching unit evidence.
   - Gate emphasis: utility unit tests, data-route focused tests, type-check, business smoke if active data routes are affected.
3. B4.009-M2c: SA-1 API/mock support evidence.
   - Paths: mock/backtest API support tests and API integration E2E evidence.
   - Reason: test-only support package; keep separate from runtime source.
   - Gate emphasis: focused API/mock unit tests plus API integration E2E.
4. B4.009-M2d: SA-4 strategy/trade adapter boundary.
   - Paths: `atrading.ts`, `strategy-adapters.ts`, `trade-adapters.ts`.
   - Reason: cross-domain source files intersect strategy/trade support and must be isolated from B4.006/ST-HOLD.
   - Gate emphasis: explicit source authorization, B4.006/ST-HOLD boundary review, exact path impact, strategy/trade focused tests, PM2 smoke.

## M2 Gate Expectations

Each later source-authorized package must:

- Stage only the approved family paths.
- Run GitNexus impact before editing mapped symbols, then staged detection before commit.
- Run `git diff --check` on the exact staged paths.
- Run `npm run type-check`.
- Run focused unit coverage for the package.
- Run PM2-backed business smoke when active stores/routes/adapters are touched.
- Refresh OPENDOG verification after native checks when practical.
- Refresh GitNexus post-commit.

No deletion, archive movement, route/menu modification, generated declaration update, ST-HOLD change, `marketKlineData` change, B4.007/B4.008 mutation, or external dirty-file staging is authorized by this M1 report.

## M1 Conclusion

B4.009-M1 is ready for review as a no-source audit.

Recommended next authorization target: B4.009-M2a SA-2 state stores + store tests, because it is the highest-impact state/API support family and should be stabilized before API/mock or utility evidence packages.
