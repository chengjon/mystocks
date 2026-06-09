# B4.009-M2d SA-4 strategy/trade adapter boundary no-source audit

Date: 2026-06-09

Mode: `no-source`

HEAD: `70d6f02f6677e9bcfe498da19120a2c8072eda99`

Latest commit: `70d6f02f6 B4.009-M2c: standardize API mock test evidence`

GitNexus CLI status at audit start:

- Repository: `/opt/claude/mystocks_spec`
- Indexed commit: `70d6f02`
- Current commit: `70d6f02`
- Status: up-to-date

## Boundary

This audit only inventories SA-4 boundary risk. It does not edit, restore, stage, or commit source, tests, generated files, route files, or governance state.

Hard no-touch paths for this no-source pass:

- `web/frontend/src/utils/atrading.ts`
- `web/frontend/src/utils/strategy-adapters.ts`
- `web/frontend/src/utils/trade-adapters.ts`
- ST-HOLD rows from B4.006 and B4.002 deletion-retirement coupling
- B4.006 route-page domains and support files
- `marketKlineData`
- external held dirty files

## SA-4 Candidate Truth

M1 classified SA-4 as a high-risk source family because these are active strategy/trade support files:

| Path | Current status | Diff size | M1 text reference signal | Family risk |
| --- | --- | ---: | ---: | --- |
| `web/frontend/src/utils/atrading.ts` | modified | +1 / -1 | 3 | High |
| `web/frontend/src/utils/strategy-adapters.ts` | modified | +1 / -1 | 8 | High |
| `web/frontend/src/utils/trade-adapters.ts` | modified | +1 / -1 | 4 | High |

Current SA-4 diff content is limited to TODO metadata standardization:

| Path | Dirty hunk type |
| --- | --- |
| `atrading.ts` | Replaces `// TODO: 检查节假日` with `// TODO owner=frontend-platform issue=techdebt-expired-markers ttl=2026-06-30: 检查节假日` |
| `strategy-adapters.ts` | Replaces `// TODO: Fix type generation to include these types` with owner/issue/ttl metadata |
| `trade-adapters.ts` | Replaces `// TODO: Fix type generation to include these types` with owner/issue/ttl metadata |

No behavior, type shape, import, export, route, store, API contract, or adapter mapping change is currently present in the SA-4 dirty hunks.

## File Roles

### `atrading.ts`

Role: A-share trading utility layer.

Exports include:

- `PriceLimitStatus`
- `TradeDirection`
- price-limit detection and color helpers
- trading-day and settlement helpers
- commission, buy/sell cost, break-even, lot-size, and round-trip fee helpers

Direct import consumers found by static source scan:

- `web/frontend/src/components/market/composables/useProKLineChart.price-limits.ts`
- `web/frontend/src/components/market/composables/useProKLineChart.types.ts`
- `web/frontend/tests/unit/utils/atrading.test.ts`

GitNexus upstream summary:

- Risk: LOW
- Impacted count: 6
- Direct: 3
- Indexed processes affected: 0

Boundary note: despite being in SA-4, this file currently has more direct market/K-line utility exposure than strategy route exposure. It must stay isolated from `marketKlineData` and prior B4.004/B4.008 market work.

### `strategy-adapters.ts`

Role: strategy module API payload to frontend VM adapter layer.

Exports include:

- `StrategyAdapter`
- `StrategyListItemVM`
- `StrategyConfigVM`
- `BacktestResultVM`
- `BacktestMetricsVM`
- `TechnicalIndicatorVM`
- related strategy parameter and curve view models

Direct import consumers found by static source scan:

- `web/frontend/src/api/dataAdapter.ts`
- `web/frontend/src/api/strategy.ts`
- `web/frontend/src/composables/strategy/useStrategyCrossTabContext.ts`
- `web/frontend/src/composables/useStrategy.shared.ts`
- `web/frontend/src/composables/useStrategy.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- `web/frontend/tests/unit/strategy-adapter-utils.spec.ts`

GitNexus upstream summary:

- Risk: MEDIUM
- Impacted count: 40
- Direct: 7
- Depth 2: 18
- Depth 3: 15
- Indexed processes affected: 0

Direct GitNexus d=1 callers:

- `web/frontend/tests/unit/strategy-adapter-utils.spec.ts`
- `web/frontend/src/composables/useStrategy.ts`
- `web/frontend/src/composables/useStrategy.shared.ts`
- `web/frontend/src/api/strategy.ts`
- `web/frontend/src/api/dataAdapter.ts`
- `web/frontend/src/composables/strategy/useStrategyCrossTabContext.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`

Boundary note: this is the main M2d risk center. It touches active strategy API/composable/view surfaces and must not be batched with B4.006 route-page work or ST-HOLD rows.

### `trade-adapters.ts`

Role: trade management API payload to frontend VM adapter layer.

Exports include:

- `TradeAdapter`
- `AccountOverviewVM`
- `AssetAllocationVM`
- `OrderVM`
- `PositionVM`
- `TradeVM`
- `TradeHistoryVM`

Direct import consumers found by static source scan:

- `web/frontend/src/api/dataAdapter.ts`
- `web/frontend/src/api/trade.ts`
- `web/frontend/src/composables/useTrading.ts`

Type re-export consumers are also present through `dataAdapter.ts`.

GitNexus upstream summary:

- Risk: LOW
- Impacted count: 17
- Direct: 3
- Indexed processes affected: 0

Boundary note: this file is active trade API support. Even comment-only changes should be gated through trade-focused tests and PM2 business smoke because `api/trade.ts` and `useTrading.ts` are active route support surfaces.

## B4.006 / ST-HOLD Boundary

B4.006 preflight established these strategy/trade route truths:

Canonical strategy routes include:

- `/strategy/repo`
- `/strategy/parameters`
- `/strategy/signals`
- `/strategy/backtest`
- `/strategy/gpu`
- `/strategy/opt`
- `/strategy/pos`

Canonical trade routes include:

- `/trade/positions`
- `/trade/terminal`
- `/trade/execution`
- `/trade/signals`
- `/trade/portfolio`
- `/trade/history`
- `/trade/reconciliation`

B4.006 high-risk hold queue remains separate from SA-4 and must not be included in M2d:

| Path | Status in B4.006 | Hold reason |
| --- | --- | --- |
| `web/frontend/src/views/BacktestWizard.vue` | modified | Coupled to deleted `useBacktestWizard.ts` / `BacktestWizard.scss` line |
| `web/frontend/src/views/__tests__/BacktestWizard.spec.ts` | untracked | Test for deletion-coupled root legacy page |
| `web/frontend/src/views/strategy/BatchScan.vue` | modified | Coupled to deleted `strategy/styles/BatchScan.scss` |
| `web/frontend/src/views/strategy/ResultsQuery.vue` | modified | Coupled to deleted `strategy/styles/ResultsQuery.scss` |
| `web/frontend/src/views/strategy/SingleRun.vue` | modified | Coupled to deleted `strategy/styles/SingleRun.scss` |
| `web/frontend/src/views/strategy/StatsAnalysis.vue` | modified | Coupled to deleted `strategy/styles/StatsAnalysis.scss` |

B4.006 hold disposition:

- Hold until B4.002 deletion-retirement package decides whether the deleted style/composable assets are accepted, restored, or archived.
- Do not stage these files together with ordinary strategy/trade route work.

Current status confirms this queue still exists in the working tree. Therefore M2d source authorization must explicitly exclude all route-page and deletion-coupled rows.

## Additional Adjacent Dirty Exclusions

Current adjacent dirty rows found during M2d boundary review:

- `web/frontend/src/views/strategy/BatchScan.vue`
- `web/frontend/src/views/strategy/ResultsQuery.vue`
- `web/frontend/src/views/strategy/SingleRun.vue`
- `web/frontend/src/views/strategy/StatsAnalysis.vue`
- `web/frontend/src/views/strategy/StrategyList.vue`
- `web/frontend/src/views/strategy/__tests__/`
- `web/frontend/src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts`
- `web/frontend/src/layouts/archive/BaseLayout.vue`
- `.governance/programs/artdeco-web-design-governance/cards/ai-batch-shape-readiness.yaml`

These are not part of M2d.

## Risk Assessment

| Risk item | Assessment | Source-stage response |
| --- | --- | --- |
| Current dirty hunk behavior risk | Low | Comment-only TODO owner/ttl metadata; no runtime shape change |
| File ownership/runtime risk | Medium/High | Files feed active strategy/trade/market support paths |
| `strategy-adapters.ts` blast radius | Medium | 7 direct import consumers; 40 total upstream impact |
| `trade-adapters.ts` blast radius | Low to Medium | Active trade API/composable support despite lower GitNexus risk |
| `atrading.ts` blast radius | Low to Medium | Active K-line price-limit helper and unit-tested trading utilities |
| ST-HOLD/B4.006 collision | High if mixed | Do not stage route-page, deletion-coupled, ST-HOLD, or marketKlineData rows |
| Test coverage risk | Manageable | Existing focused unit tests cover atrading and strategy adapters; type cleanup tests cover strategy/trade adapters; business smoke covers active route continuity |

## Recommended Source Authorization Shape

If source authorization is approved, authorize only this minimal M2d-A package:

Allowed source files:

- `web/frontend/src/utils/atrading.ts`
- `web/frontend/src/utils/strategy-adapters.ts`
- `web/frontend/src/utils/trade-adapters.ts`

Allowed action:

- Accept the existing TODO metadata standardization only.
- No function body edits.
- No import/export/type/interface shape edits.
- No adapter mapping, fallback, API endpoint, route, store, composable, or view edits.

Explicit non-goals:

- Do not edit B4.006 route-page files.
- Do not edit ST-HOLD / deletion-coupled hold queue.
- Do not edit `marketKlineData`.
- Do not edit `BaseLayout.vue`.
- Do not edit data view fallback tests, strategy route tests, or governance cards.
- Do not clean adjacent comments or formatting.

Required gates for source stage:

1. GitNexus impact on all three files before staging.
2. Focused unit tests:
   - `npm run test -- tests/unit/utils/atrading.test.ts tests/unit/strategy-adapter-utils.spec.ts tests/unit/config/trade-adapters-types-cleanup.spec.ts tests/unit/config/strategy-adapters-types-cleanup.spec.ts`
3. `npm run type-check`
4. `npm run test:unit:stable`
5. PM2 business smoke E2E:
   - `PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke`
6. OPENDOG verification freshness check.
7. Exact staging only:
   - the three allowed source files and no tests unless a focused test must be repaired for this package.
8. `git diff --cached --check`
9. GitNexus staged detect / `verify-staged`
10. Post-commit GitNexus analyze/status

## Decision

No source authorization is active yet.

This no-source audit supports a narrow M2d-A source authorization for comment-only TODO metadata standardization across the three SA-4 files. It does not support behavioral edits, route-page edits, adapter contract edits, ST-HOLD edits, or mixed batching with any B4.006/deletion-coupled rows.
