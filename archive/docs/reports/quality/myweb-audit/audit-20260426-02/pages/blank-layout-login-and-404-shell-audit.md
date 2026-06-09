# Blank Layout Login And 404 Shell Audit

## Scope
- `/login`
- `/:pathMatch(.*)*`

## Route Truth
- `/login` canonical entry: `web/frontend/src/views/Login.vue`
- `404` canonical entry: `web/frontend/src/views/NotFound.vue`
- both routes remain `meta.layout = Blank`

## Findings
- `/login`
  - no route-local repair required in this mini batch
  - shell remains isolated from shared request badges, stats strips, and default ArtDeco workbench chrome
- `404`
  - repaired one route-truth gap: the recovery button now uses canonical `HOME_ROUTE_PATH` instead of a raw `/` push

## Lightweight Verification Policy
- layout isolation only
- no selector or stale-route contamination between `/login` and `404`
- no snapshot-fallback chrome such as request badges or stats strips
- targeted type-check confirmation
- basic Playwright smoke only

## Evidence
- source guard confirms blank shell routes stay under `.app-shell[data-layout="blank"]`
- source guard confirms `/login` and `404` contain no `REQ_ID`, `TRACE_ID`, or `ArtDecoStatCard` chrome
- Playwright smoke confirms:
  - `/login` loads in the blank shell with no readiness banner and no stats strip
  - same-tab navigation to an unmatched route removes the login card and shows the 404 card
  - clicking `返回首页` on the 404 shell lands on the authenticated home redirect path and resolves to `/login?redirect=/dashboard` for unauthenticated sessions
