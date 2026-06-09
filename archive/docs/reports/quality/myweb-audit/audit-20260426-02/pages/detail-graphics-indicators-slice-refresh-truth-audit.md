# Page Audit: /detail/graphics/:symbol

## Scope
- Route: `/detail/graphics/:symbol`
- Canonical entry: `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`
- Batch: `detail-batch-04`

## Defect Summary
- The routed detail graphics page already kept its K-line primary snapshot visible when the detail route succeeded.
- But the sibling technical-indicators slice still collapsed into the generic empty-state copy `暂无技术指标结果。` whenever indicators failed before a current result existed.
- A later indicators refresh failure after prior success also cleared the previously verified indicators instead of retaining them with explicit stale-enrichment messaging.

## Repair
- Updated `KLineAnalysis.vue` so the routed owner now tracks `hasVerifiedIndicatorSnapshot` and `indicatorSliceError` page-locally.
- The indicators card now distinguishes:
  - first-load indicators failure: `技术指标暂不可用，当前仅显示趋势数据。`
  - later stale indicators retention: preserve the last verified indicators while showing stale-enrichment runtime messaging
- The routed runtime message now explains that the indicators slice partially failed while the K-line primary snapshot remains verified.
- Added owner regressions for both indicators first-load failure and `success -> indicators refresh fail`.
- Added routed Phase 1 matrix assertions for the same two paths on `/detail/graphics/:symbol`.

## Verification
- Owner regression:
  - `npx vitest run src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts` passed `5/5`
- Type check:
  - `timeout 180s npm run type-check` passed
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` listed the two new `/detail/graphics/:symbol` indicators-slice assertions
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - controlled first-load indicators failure now shows:
    - `POINTS: 2`
    - `REQ_ID: live-kline-success`
    - runtime copy `技术指标部分加载失败：...，当前仅显示已验证的K线趋势快照。`
    - indicators-card copy `技术指标暂不可用，当前仅显示趋势数据。`
  - controlled `success -> indicators refresh fail` now keeps:
    - visible `RSI 61.2 偏强`
    - runtime copy `技术指标部分加载失败：...，当前仍显示上次成功同步的技术指标快照。`
    - no fallback to `暂无技术指标结果。`

## Skill Feedback
- This batch introduced `myweb-audit v1.60`.
- New rule: when a canonical detail route keeps a primary snapshot visible but a sibling enrichment slice fails, the enrichment surface must not collapse into generic empty-state truth; it must either show first-load partial-failure copy or retain the last verified enrichment values with stale-enrichment messaging.
