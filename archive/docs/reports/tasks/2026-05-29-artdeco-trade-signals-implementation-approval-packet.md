# Implementation Approval Packet: `trade/Signals.vue` ArtDeco Signal Trust Desk

> Date: 2026-05-29
> Target route: `/trade/signals`
> Target component: `web/frontend/src/views/trade/Signals.vue`
> Status: awaiting explicit approval.
> Boundary: no route changes, no API contract changes, no shared component extraction.

## 1. Why This Packet Exists

The shape brief is complete, but `architecture/STANDARDS.md` requires explicit user approval before code changes:

```text
只有在用户明确回复“批准”、“同意”或“执行”后，方可启动代码修改。
```

This packet converts the approved-design candidate into a small implementation plan and TDD acceptance checklist without touching source code.

## 2. Approved-Shape Candidate

Shape brief:

```text
docs/reports/tasks/2026-05-29-artdeco-trade-signals-shape-brief.md
```

Design direction:

```text
compact route header -> signal review lens -> signal trust strip -> primary signal list -> secondary evidence panels
```

Primary goal:

- make signal data trust visible before the user acts
- keep the live signal list dominant
- preserve current API and route behavior
- add stable route-local verification hooks

## 3. Implementation Scope After Approval

Allowed local files:

| File | Intended work |
|---|---|
| `web/frontend/src/views/trade/Signals.vue` | local layout/state/copy/style updates only |
| `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts` | targeted `Trade-Signals` route assertions |
| optional `docs/reports/tasks/2026-05-29-artdeco-trade-signals-implementation-report.md` | implementation evidence |

Implementation must stay local to the route.

## 4. Explicit Non-Scope

Do not modify:

- `web/frontend/src/router/index.ts`
- `web/backend/app/api/**`
- `docs/api/**`
- `web/frontend/src/api/**`
- `web/frontend/src/components/**`
- `web/frontend/src/views/artdeco-pages/**`
- OpenSpec specs / changes
- shared ArtDeco components

Do not change:

- `/trade/signals` route definition
- `/api/v1/trade/signals` contract
- response shape
- route metadata
- component ownership of `ArtDecoTradingSignals`
- component ownership of `ArtDecoTradingSignalsControls`

## 5. Existing Coverage Baseline

Existing `phase3-mainline-matrix.spec.ts` already covers:

- `Trade-Signals renders mocked signal execution workspace`
- `Trade-Signals keeps honest pending provenance while the first signal payload is still unresolved`
- `Trade-Signals keeps unavailable provenance when the first signal payload fails before any verified snapshot exists`
- `Trade-Signals keeps the last verified request id and signal rows when a manual refresh fails`

The current tests assert important honesty rules:

- no fake stat changes
- no fake quality percentages
- pending state does not claim real data
- unavailable first-load data remains unavailable
- stale refresh failure keeps the last verified request ID and rows

## 6. TDD Plan

### RED 1: Route-Level Data-Test Surface

Add failing E2E assertions for stable hooks:

- `trade-signals-page`
- `trade-signals-header`
- `trade-signals-review-lens`
- `trade-signals-trust-strip`
- `trade-signals-list`
- `trade-signals-refresh`

Expected first failure:

- selectors are absent because `Signals.vue` currently has `0` `data-test` hooks.

### RED 2: Signal Trust Strip States

Add failing E2E assertions that the trust strip exposes:

- verified state after successful payload
- pending state during unresolved first load
- unavailable state after first-load failure
- stale/degraded state after refresh failure with prior data

Expected first failure:

- trust strip does not exist as a dedicated route-level surface.

### RED 3: Review Lens Behavior

Add failing E2E assertions for route-visible review lens buttons:

- `全部`
- `买入`
- `卖出`
- `观望`
- `高置信度`

Expected first failure:

- current filtering is delegated to existing controls and has no route-level ArtDeco review-lens surface / data-test contract.

### RED 4: Desktop-Only Layout Cleanup

Add a static or token/lint check only if the approved scope includes layout cleanup:

- `Signals.vue` should not contain `@media (width <= 75rem)`
- `Signals.vue` should not contain `@media (width <= 48rem)`

Expected first failure:

- both rules exist today.

This check should be skipped if the user does not approve `@media` cleanup in the implementation scope.

## 7. Minimal GREEN Strategy

To pass the tests with minimal changes:

1. Add local `data-test` hooks to existing route surfaces.
2. Add a compact trust strip below the review/header area using existing computed state:
   - `dataSource`
   - `loading`
   - `staleError`
   - `effectiveError`
   - `displayRequestId`
   - `displayProcessTime`
   - `displayVisibleCount`
   - `signalFilterLabel`
3. Expose the existing filter set as a route-level review lens without changing API behavior.
4. Keep `ArtDecoTradingSignals` rendering intact.
5. Keep `ArtDecoTradingSignalsControls` only if needed for current behavior; do not move it.
6. Demote secondary panels visually after the list.
7. Remove desktop-incompatible `@media` rules only if approved.

## 8. Verification Gate After Implementation

Required commands after craft:

```bash
cd web/frontend
npx eslint src/views/trade/Signals.vue
node scripts/check-artdeco-tokens.js --target-file src/views/trade/Signals.vue
npm run type-check -- --pretty false
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Signals" --project=chromium
npx impeccable --json src/views/trade/Signals.vue
```

Required status report:

- structural syntax errors: must be `0`
- type-check result: exact command and result
- ArtDeco token check: pass/fail
- E2E: exact browser project, passed/failed/skipped count
- PM2 status only if services are started or affected
- clear statement that no route/API/shared component files were modified

## 9. Approval Options

Implementation should start only after one of these explicit approvals:

```text
批准实施 trade/Signals.vue shape brief
```

or:

```text
同意执行 trade/Signals.vue craft
```

Optional scope modifier:

```text
批准实施，并包含 @media 清理
```

If approval does not include `@media` cleanup, implementation should leave responsive rules untouched and only document them as residual debt.

## 10. Current Recommendation

Recommended approval wording:

```text
批准实施 trade/Signals.vue shape brief，并包含 @media 清理；继续保持不改路由、不改 API 合同、不抽共享组件。
```

This is the smallest implementation path that closes the critique's P0/P1 design gaps without changing contracts or component ownership.
