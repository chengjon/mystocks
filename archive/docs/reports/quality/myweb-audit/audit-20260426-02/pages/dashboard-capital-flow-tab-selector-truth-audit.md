# Dashboard Capital-Flow Tab Selector Truth Audit

- Route: `/dashboard`
- Canonical entry: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- Batch: `dashboard-batch-09`
- Skill rule applied: `myweb-audit v1.71` with existing `v1.68` selector-scoped verified-snapshot truth

## Problem

The dashboard already exposed a local capital-flow tab selector:

- `1日`
- `3日`
- `5日`

But the route still kept one global `capitalFlowData` array and one route-local degraded-state string. That meant the same mounted `/dashboard` instance could switch from a verified `1day` tab to `3day` while `3day` had no verified snapshot yet, and the old `1day` rows would continue rendering under the new active tab shell.

## Repair

The dashboard owner now:

- captures the request tab at fetch start instead of reading live `activeFlowTab` again at resolve time
- stores verified capital-flow rows by tab
- scopes degraded-state copy by tab
- renders visible capital-flow rows and heatmap inputs from the active tab's own verified snapshot only
- shows pending skeletons instead of old rows when a newly requested tab has no verified snapshot yet

## Verification

- `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts`
- `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list`
- targeted Playwright-library verification with system `google-chrome`

Controlled live proof confirmed:

- initial `/dashboard` state shows verified `1day` rows including `贵州茅台` and `宁德时代`
- after the same mounted route switches to active `3日` while the `3day` ranking request is still unresolved, the card no longer shows the old `1day` rows
- the unresolved `3day` path also does not misreport `资金流向持续排名暂不可用`
