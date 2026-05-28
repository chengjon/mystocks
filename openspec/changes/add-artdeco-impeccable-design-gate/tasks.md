## 1. Design Documentation Gate

- [x] 1.1 Run `$impeccable document` to refresh or report the current implemented ArtDeco visual system.
- [x] 1.2 Review the resulting `DESIGN.md` changes or design-context findings against current route truth and style-layer truth.
- [x] 1.3 Compare findings against the eight ArtDeco source documents listed in `design.md`.
- [x] 1.4 Record P0 to P3 documentation and design optimization findings.
- [x] 1.5 Produce or update a page review checklist for ArtDeco route audits.

## 2. Pilot Page Critique and Shape

- [x] 2.1 Run `$impeccable critique web/frontend/src/views/market/Realtime.vue`.
- [x] 2.2 Save critique findings to `docs/reports/tasks/2026-05-28-artdeco-market-realtime-critique.md`.
- [x] 2.3 Convert priority critique findings into a draft `$impeccable shape web/frontend/src/views/market/Realtime.vue` brief for approval.
- [x] 2.4 Save the shape brief as the design document for approval.
- [x] 2.5 Confirm the shape brief includes page structure, information priority, controls, runtime states, token usage, and verification expectations.

## 3. Approval Gate

- [x] 3.1 Present the design documents, critique report, shape brief, and proposed implementation scope for approval.
- [x] 3.2 Do not modify Vue, TypeScript, SCSS, tokens, routes, components, or composables before explicit approval.
- [x] 3.3 Record the approval wording and approved scope before implementation begins.

Approval record:

- Date: 2026-05-28
- User wording: `批准实施 market/Realtime.vue shape brief`
- Approved target: `web/frontend/src/views/market/Realtime.vue`
- Approved scope: compact page header band, single control row, table-first primary work area, explicit freshness/cache/stale/error states, and touched-scope token cleanup.

## 4. Post-Approval Implementation

- [x] 4.1 Run `$impeccable craft web/frontend/src/views/market/Realtime.vue` only after approval.
- [x] 4.2 Keep implementation bounded to the approved scope, initially targeting the header band, control row, primary market work area, runtime states, and token cleanup in touched scope.
- [x] 4.3 Run `$impeccable audit web/frontend/src/views/market/Realtime.vue`.
- [x] 4.4 Run `$impeccable polish web/frontend/src/views/market/Realtime.vue`.
- [x] 4.5 Skip `$impeccable extract web/frontend/src/views/market/Realtime.vue` because this first pilot has not yet proven a second consumer or approved extraction rationale.

## 5. Verification

- [x] 5.1 Validate this OpenSpec change with `openspec validate add-artdeco-impeccable-design-gate --strict`.
- [x] 5.2 For documentation-only phases, verify that no frontend source files were modified by this documentation batch.
- [x] 5.3 For post-approval implementation phases, report structural syntax errors, type-check baseline comparison, PM2 service status when required, actual E2E or smoke command results, and ArtDeco lint results.

Note: the worktree contains pre-existing `web/frontend/**` dirty files. This documentation batch added or updated only OpenSpec and `docs/reports/tasks/**` artifacts.

Implementation report: `docs/reports/tasks/2026-05-28-artdeco-market-realtime-implementation-report.md`
