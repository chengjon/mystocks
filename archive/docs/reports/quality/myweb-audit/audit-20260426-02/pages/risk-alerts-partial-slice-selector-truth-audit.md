# Page Audit: /risk/alerts partial slice selector truth

## Page
- Route: `/risk/alerts`
- Canonical entry: `web/frontend/src/views/risk/Alerts.vue`
- Audit focus: preserve a verified rules slice when alert records fail before the first full route snapshot exists

## Finding
- Severity: High
- Issue id: `risk-alerts-issue-17`
- Summary: the routed owner previously treated `alert-rules` and `alerts` as one global verified shell, so a first-load alerts failure hid a verified rules slice and rewrote the page back to `当前暂无已验证告警快照。`

## Repair
- Added separate verified snapshot ownership for rules and alert records inside the canonical owner.
- Bound hero `REQ_ID`, top-strip counts, `RULES / ALERTS` meta, runtime copy, and table empty states to slice-local verified truth instead of one route-global flag.
- Preserved the existing stale-refresh behavior for a fully verified alerts shell.

## Verification
- Owner regression: `npx vitest run src/views/risk/__tests__/Alerts.spec.ts`
- Routed matrix coverage: `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list`
- Controlled browser proof:
  - hero stays `REQ_ID: N/A / UNREAD: --`
  - content meta stays partial as `RULES: 2 / ALERTS: --`
  - top-strip stays partial as `2 / 2 / -- / --`
  - the verified rules table still shows `组合波动率约束`
  - the same browser proof shows `获取告警记录失败，当前告警记录暂不可用。`
