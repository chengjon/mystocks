# B4.004 data/market route package preflight

Date: 2026-06-06
Mode: `no-source`
Scope: data/market regular route dirty inventory after B4.002 and B4.003 exclusions

## Governance boundary

This node inventories data/market regular route dirty items only. It does not edit, restore, stage, or commit frontend source, tests, styles, or assets.

Primary references:

- `docs/reports/worklogs/claude-auto/b4-001-frontend-route-ui-dirty-atlas-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-002-frontend-deletion-candidate-inventory-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-003-route-header-residue-preflight-2026-06-06.md`
- `docs/guides/frontend-structure.md`
- `web/frontend/src/router/index.ts`

## Hard exclusions applied

The following items are explicitly excluded from B4.004 package candidates:

- `web/frontend/src/views/data/FundFlow.vue`
  - Route-header专项; isolated by B4.003.
- `web/frontend/src/views/market/LHB.vue`
  - Deferred to later Vue slimming; isolated by B4.003.
- All 28 deleted frontend entries from B4.002.
  - Deletion-retirement candidates only.
- 3 route-header evidence residue tests from B4.003:
  - `web/frontend/tests/unit/views/data-concept-refresh-fallback.spec.ts`
  - `web/frontend/tests/unit/views/data-industry-refresh-fallback.spec.ts`
  - `web/frontend/tests/unit/views/data-fund-flow-partial-state.spec.ts`

Stale OPENDOG caveat remains inherited from B4.001-B4.003:

- Stale evidence does not block this no-source inventory.
- Any later source-authorized package must refresh OPENDOG verification evidence or explicitly accept the stale-evidence caveat in that package report.

## Scan method

Read-only checks:

- Parsed targeted `git status --porcelain=v1 -uall` for:
  - `web/frontend/src/views/data`
  - `web/frontend/src/views/market`
  - `web/frontend/tests/unit/views`
  - selected data/market E2E test paths
- Removed hard exclusions before B4.004 classification.
- Used router truth for canonical active route mapping.
- Parsed current `web/frontend/src` import declarations for source dependency signals.

No build, type-check, Vitest, E2E, PM2, or source mutation was performed.

## Summary

Targeted dirty rows after hard exclusions:

- B4.004-related rows classified: `34`
- Source package candidates: `26`
- Continue-hold rows: `4`
- Out-of-scope rows for B4.005+ / B4.006: `4`

Classification:

| Class | Count | Disposition |
| --- | ---: | --- |
| `ordinary-data-market` | 20 | Candidate for normal data/market package planning. |
| `noncanonical-market-view-review` | 6 | Needs route-truth decision before source edits; not imported by current canonical router. |
| `fund-flow-coupled-hold` | 2 | Hold with FundFlow route-header line, despite not being in the hard exclusion list. |
| `lhb-coupled-hold` | 1 | Hold with deferred LHB slimming line. |
| `broad-e2e-test-hold` | 1 | Broad route matrix test; do not use as focused data/market package evidence without review. |
| `out-of-scope-B4.005plus` | 4 | Belongs to system/risk/trade route preflight, not B4.004. |

Risk split:

| Risk | Count | Meaning |
| --- | ---: | --- |
| High | 4 | Hold items coupled to isolated route-header/LHB/broad E2E scope. |
| Medium | 14 | Source page/support or canonical-adjacent tests needing route/dependency review. |
| Low | 16 | Test-only or lower-coupling data/market evidence candidates. |

## Hold queue

These are not B4.004 source package candidates:

| Path | Reason | Next authority |
| --- | --- | --- |
| `web/frontend/src/views/data/__tests__/FundFlow.spec.ts` | Coupled to isolated FundFlow route. | FundFlow route-header package only. |
| `web/frontend/src/views/data/fundFlowPageData.ts` | Imported by FundFlow-related source; coupled to excluded FundFlow route support. | FundFlow route-header or explicit FundFlow support package after review. |
| `web/frontend/src/views/market/__tests__/LHB.spec.ts` | Coupled to explicitly deferred `LHB.vue`. | Later LHB Vue slimming package. |
| `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts` | Broad route matrix test; not focused data/market acceptance evidence. | Test preflight / B4.010 unless explicitly pulled into a focused package. |

## Out-of-scope rows

These were seen in the targeted unit-view test sweep but belong outside B4.004:

| Path | Destination |
| --- | --- |
| `web/frontend/tests/unit/views/risk-center-template-retention.spec.ts` | B4.005 system/risk preflight. |
| `web/frontend/tests/unit/views/risk-wrapper-retention.spec.ts` | B4.005 system/risk preflight. |
| `web/frontend/tests/unit/views/system-wrapper-retention.spec.ts` | B4.005 system/risk preflight. |
| `web/frontend/tests/unit/views/trade-wrapper-retention.spec.ts` | B4.006 strategy/trade preflight. |

## Data candidates

| Path | Status | Risk | Dependency signal | Proposed package |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/data/Advanced.vue` | modified | Medium | Canonical route `/data/advanced`; imported by router and tests. | `DM-1 data-advanced canonical route` |
| `web/frontend/src/views/data/__tests__/Advanced.spec.ts` | untracked | Low | Test for `Advanced.vue`. | `DM-1 data-advanced canonical route` |
| `web/frontend/tests/unit/views/data-advanced-cutover.spec.ts` | modified | Low | Data advanced route evidence. | `DM-1 data-advanced canonical route` |
| `web/frontend/tests/unit/views/data-advanced-screening-truth.spec.ts` | untracked | Low | Data advanced screening truth evidence. | `DM-1 data-advanced canonical route` |
| `web/frontend/tests/unit/views/data-indicator-details.spec.ts` | untracked | Low | Data indicator/details evidence. | `DM-1` or separate data test-only package |
| `web/frontend/src/views/data/__tests__/Concepts.spec.ts` | untracked | Medium | Test for completed/clean `/data/concepts` route. | Test-only evidence review |
| `web/frontend/src/views/data/__tests__/Industry.spec.ts` | untracked | Medium | Test for completed/clean `/data/industry` route. | Test-only evidence review |

Notes:

- `FundFlow.vue` is excluded by hard rule.
- `FundFlow.spec.ts` and `fundFlowPageData.ts` are held because they are coupled to the excluded FundFlow line.
- `Concepts.vue` and `Industry.vue` themselves are clean after the route-header line; their untracked tests should be reviewed as evidence/test-only items before staging.

## Market candidates

### Shared/support candidates

| Path | Status | Risk | Dependency signal | Proposed package |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/market/dragonTigerData.ts` | modified | Medium | Imported by ArtDeco market-data tab bridge. | `DM-2 market support data modules` |
| `web/frontend/src/views/market/__node_tests__/dragonTigerData.test.ts` | untracked | Low | Node test for dragonTiger support module. | `DM-2 market support data modules` |
| `web/frontend/src/views/market/marketKlineData.ts` | modified | Medium | Imported by multiple ArtDeco/analysis surfaces. | `DM-2 market support data modules` |
| `web/frontend/src/views/market/__node_tests__/marketKlineData.test.ts` | untracked | Low | Node test for market K-line support module. | `DM-2 market support data modules` |
| `web/frontend/src/views/market/composables/useTechnical.ts` | modified | Medium | Technical-analysis support; route-adjacent to completed `/market/technical`. | `DM-2 market support data modules` |
| `web/frontend/src/views/market/__tests__/Technical.spec.ts` | untracked | Medium | Test for completed/clean `/market/technical` route. | `DM-2` or test-only evidence review |

### Noncanonical market view review

These modified Vue pages are under `web/frontend/src/views/market/**` but are not current canonical router imports according to `web/frontend/src/router/index.ts`.

| Path | Status | Risk | Paired test | Proposed package |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/market/Auction.vue` | modified | Medium | `web/frontend/src/views/market/__tests__/Auction.spec.ts` | `DM-3 noncanonical market view truth review` |
| `web/frontend/src/views/market/CapitalFlow.vue` | modified | Medium | `web/frontend/src/views/market/__tests__/CapitalFlow.spec.ts` | `DM-3 noncanonical market view truth review` |
| `web/frontend/src/views/market/Concepts.vue` | modified | Medium | `web/frontend/src/views/market/__tests__/Concepts.spec.ts` | `DM-3 noncanonical market view truth review` |
| `web/frontend/src/views/market/Etf.vue` | modified | Medium | `web/frontend/src/views/market/__tests__/Etf.spec.ts` | `DM-3 noncanonical market view truth review` |
| `web/frontend/src/views/market/MarketDataView.vue` | modified | Medium | `web/frontend/src/views/market/__tests__/MarketDataView.spec.ts` | `DM-3 noncanonical market view truth review` |
| `web/frontend/src/views/market/Tdx.vue` | modified | Medium | `web/frontend/src/views/market/__tests__/Tdx.spec.ts` | `DM-3 noncanonical market view truth review` |

Additional market test-only row:

- `web/frontend/src/views/market/__tests__/Realtime.spec.ts`
  - Low risk.
  - Current `/market/realtime` route page itself was not dirty in this targeted scan.
  - Treat as test-only evidence unless paired with a later route page package.

Notes:

- `LHB.vue` and `LHB.spec.ts` are excluded/held.
- `useTdx.ts` and `Tdx.scss` remain B4.002 deletion-retirement candidates and are not B4.004 package inputs.
- `Tdx.vue` must not be staged together with deleted TDX support files unless a later deletion-retirement package explicitly authorizes that boundary.

## Proposed package order

1. `DM-1 data-advanced canonical route`
   - Candidate files: `Advanced.vue`, `Advanced.spec.ts`, data-advanced unit evidence, and possibly `data-indicator-details.spec.ts`.
   - Risk: Medium.
   - Gate: source-authorized route package, GitNexus impact before editing, focused unit/component tests, route config check.

2. `DM-2 market support data modules`
   - Candidate files: `dragonTigerData.ts`, `marketKlineData.ts`, `useTechnical.ts`, and paired node/unit tests.
   - Risk: Medium because support modules are imported by ArtDeco/analysis surfaces.
   - Gate: import/dependency review, focused node/unit tests, no route-header/LHB/FundFlow files.

3. `DM-3 noncanonical market view truth review`
   - Candidate files: six modified noncanonical market Vue pages and their tests.
   - Risk: Medium.
   - Gate: route-truth decision first. Do not source-authorize as active route work until the package decides whether these are legacy wrappers, test fixtures, or candidate pages for another route truth line.

4. `DM-4 data/market test-only evidence`
   - Candidate files: clean-route tests such as `Concepts.spec.ts`, `Industry.spec.ts`, `Technical.spec.ts`, `Realtime.spec.ts`.
   - Risk: Low to medium.
   - Gate: test-authorized package or pair with the matching source package only if source is actually touched.

## B4.005 handoff

B4.005 should start system/risk route package preflight / no-source.

Carry forward to B4.005:

- `web/frontend/tests/unit/views/risk-center-template-retention.spec.ts`
- `web/frontend/tests/unit/views/risk-wrapper-retention.spec.ts`
- `web/frontend/tests/unit/views/system-wrapper-retention.spec.ts`

Do not carry into B4.005:

- FundFlow route-header items.
- LHB deferred items.
- B4.002 deletion-retirement candidates.
- B4.004 data/market ordinary package candidates.
- `trade-wrapper-retention.spec.ts`, which belongs with B4.006 strategy/trade preflight.

## Verification performed

Read-only checks only:

- Targeted dirty status parse.
- Hard-exclusion removal.
- Router truth mapping.
- Import declaration dependency scan for current `web/frontend/src`.
- Risk and package classification.

Not run:

- Frontend build
- Frontend type check
- Vitest
- Playwright/E2E
- PM2 service checks

Reason: B4.004 is a no-source preflight and does not modify or accept frontend source/test changes.
