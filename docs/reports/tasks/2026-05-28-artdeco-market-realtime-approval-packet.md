# Approval Packet: `market/Realtime.vue` ArtDeco Pilot

Date: 2026-05-28

OpenSpec change: `add-artdeco-impeccable-design-gate`

Status: awaiting explicit implementation approval

## 1. Purpose

This approval packet summarizes the documentation-phase artifacts for the first ArtDeco Web design pilot. It is not an implementation report and does not authorize source-code edits by itself.

## 2. Documents for Review

- Design context audit: `docs/reports/tasks/2026-05-28-artdeco-design-context-audit.md`
- Page review checklist: `docs/reports/tasks/2026-05-28-artdeco-page-review-checklist.md`
- Realtime critique: `docs/reports/tasks/2026-05-28-artdeco-market-realtime-critique.md`
- Realtime shape brief: `docs/reports/tasks/2026-05-28-artdeco-market-realtime-shape-brief.md`
- OpenSpec proposal: `openspec/changes/add-artdeco-impeccable-design-gate/proposal.md`
- OpenSpec design: `openspec/changes/add-artdeco-impeccable-design-gate/design.md`
- OpenSpec tasks: `openspec/changes/add-artdeco-impeccable-design-gate/tasks.md`

## 3. Proposed Implementation Scope After Approval

Target:

- `web/frontend/src/views/market/Realtime.vue`

Allowed first slice:

- compact page header band
- single control row
- table-first primary work area
- distribution or breadth side panel
- explicit freshness, cache, stale, degraded, empty, loading, and error states
- touched-scope token cleanup only

## 4. Explicitly Out of Scope

- backend API contract changes
- route restructuring
- mobile redesign
- new charting library
- broad token migration
- global component extraction from this single page
- rewriting historical ArtDeco documents
- running `$impeccable extract` before a second consumer or approved extraction rationale exists

## 5. Approval Boundary

Implementation must not begin until the user explicitly approves the shape brief and scope.

Valid approval examples:

```text
批准实施 market/Realtime.vue shape brief
```

```text
同意按该 scope 执行 Realtime.vue ArtDeco pilot
```

```text
执行 market/Realtime.vue ArtDeco pilot，范围按 shape brief
```

Ambiguous continuation wording such as `继续` or `请继续` is not treated as source-code implementation approval.

## 6. Post-Approval Verification Commitments

After implementation, report:

- changed files
- structural syntax error status
- ArtDeco lint or targeted token check
- type-check result with baseline comparison
- actual E2E or smoke command, browser project, pass/fail/skip counts
- PM2 service status if service startup, build, type check, or E2E is involved
- screenshot or visual inspection notes if a browser run is performed
