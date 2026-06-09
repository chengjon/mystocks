## What to decide

Approve, revise, or reject the backend OpenSpec orchestration artifact and the
C/E/F/G proposal-level governance changes.

## Context

- Approval packet: `docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md`
- Orchestration: `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md`
- Cross-line alignment: `docs/reports/quality/cross-line-alignment-P3-impl-openspec-2026-05-18.md`
- G-line publication impact: `docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md`
- Compressed publication manifest: `docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md`
- C: `openspec/changes/consolidate-backend-api-domain-routers/`
- G: `openspec/changes/consolidate-backend-health-endpoints/`
- E: `openspec/changes/migrate-backend-singletons-to-lifecycle-di/`
- F: `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/`

## Cross-line alignment

The P3 implementation line has already made and implemented the C
announcement, strategy, and risk canonical-router decisions:

- Announcement: `announcement/` package canonical; `announcement.py` deleted in
  `243d40a8a`.
- Strategy: `strategy_management/` package canonical; strategy router
  convergence in `1241c4b7e`.
- Risk: `risk/` package canonical; orphan risk files deleted in `243d40a8a`.

This issue should no longer ask humans to re-decide those three C router
ownership questions. Approval scope is now limited to:

- accepting the orchestration artifact as the governance coordination source;
- reconciling OpenSpec C with already-completed P3 work instead of
  re-implementing it;
- approving remaining E/F/G governance scope;
- deciding whether trading and backup need separate follow-up OpenSpec
  proposals or one shared route ownership proposal.

## Acceptance criteria

- Human reviewer records approval or requested revisions.
- Approval record states implementation is not unlocked by this issue.
- Approval record acknowledges the P3-resolved C announcement/strategy/risk
  decisions and states they must not be republished as new HITL decision issues.
- Approval record accepts or revises the remaining C/E/F/G scope boundaries.
- Approval record states whether trading and backup need one follow-up proposal
  each or one shared route ownership proposal.
- Approval record acknowledges that original issue drafts 08/09 are on
  publication hold pending reclassification because G-line evidence superseded
  their taxonomy/canonical-path scopes.
- Approval record acknowledges the compressed publication shape: 3 publishable
  issues, 3 audit-only bodies, 2 publication-hold bodies, and 7 superseded
  merged source bodies.

## Verification

```bash
openspec validate consolidate-backend-api-domain-routers --strict
openspec validate consolidate-backend-health-endpoints --strict
openspec validate migrate-backend-singletons-to-lifecycle-di --strict
openspec validate split-backend-core-modules-with-compatibility-wrappers --strict
```

## Blocked by

None.
