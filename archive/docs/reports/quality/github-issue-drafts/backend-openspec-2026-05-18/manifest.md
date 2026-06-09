# Backend OpenSpec GitHub Issue Draft Manifest

> Draft only. Do not run these commands until human approval accepts
> `docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md`.
> Replace `BLOCKED_BY_TODO` placeholders with real GitHub issue numbers after
> publishing blockers in order.

Repository: `chengjon/mystocks`

## Alignment Sources

```text
docs/reports/quality/cross-line-alignment-P3-impl-openspec-2026-05-18.md
docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md
docs/reports/quality/backend-openspec-issue14-triage-gate-2026-05-18.md
```

## Current Package Shape

| Category | Count | Body files |
|---|---:|---|
| Retained body files | 15 | All `01` through `15` bodies retained for audit continuity |
| Publishable commands | 3 | `01`, `14`, `15` |
| Audit-only / do-not-publish | 3 | `03`, `04`, `05` |
| Publication hold / reclassification | 2 | `08`, `09` |
| Superseded / merged | 7 | `02`, `06`, `07`, `10`, `11`, `12`, `13` |

## Publication Order

| Order | Draft body | Initial label | Notes |
|---:|---|---|---|
| 1 | `01-approve-orchestration.md` | `ready-for-human` | Approval gate; publish first |
| 2 | `14-build-shared-evidence-package.md` | `needs-triage` | Evidence-only bundle for C/E/F; can become `ready-for-agent` after issue 1 approval and placeholder replacement |
| 3 | `15-decide-post-approval-plan.md` | `ready-for-human` | HITL/design bundle for DI pilot, Core split, trading/backup follow-ups, and G residual-tail disposition |

## Draft Commands

```bash
gh issue create --repo chengjon/mystocks --title "[Backend OpenSpec] Approve orchestration and C/E/F/G proposal scope" --label ready-for-human --label enhancement --body-file docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/01-approve-orchestration.md

gh issue create --repo chengjon/mystocks --title "[Backend OpenSpec] Build shared C/E/F evidence package" --label needs-triage --label enhancement --body-file docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/14-build-shared-evidence-package.md

gh issue create --repo chengjon/mystocks --title "[Backend OpenSpec] Decide post-approval implementation plan and follow-up boundaries" --label ready-for-human --label enhancement --body-file docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/15-decide-post-approval-plan.md
```

Every publishable issue command carries exactly one state label and one category
label. The category label is `enhancement`.

## Already Resolved / Do Not Publish

| Draft body | Status | Evidence |
|---|---|---|
| `03-decide-announcement-router.md` | Already resolved; retained for audit only | P3-A1 decision record; `announcement/` package canonical; `announcement.py` deleted in `243d40a8a` |
| `04-decide-strategy-router.md` | Already resolved; retained for audit only | P3-A2 decision record; `strategy_management/` package canonical; 3-to-1 convergence in `1241c4b7e` |
| `05-decide-risk-router.md` | Already resolved; retained for audit only | P3-A3 decision record; `risk/` package canonical; orphan risk files deleted in `243d40a8a` |

## Publication Hold / Reclassification Required

| Draft body | Status | Evidence |
|---|---|---|
| `08-build-health-status-taxonomy.md` | Do not publish as originally drafted; G-line evidence covered the taxonomy/canonical-path prerequisite work | `b3bbf4314`, `cd1e4795b`, `docs/reports/quality/backend-health-status-implementation-boundary-2026-05-18.md`, `docs/reports/quality/backend-health-status-residual-blockers-2026-05-18.md` |
| `09-decide-health-status-canonical-paths.md` | Do not publish as originally drafted; canonical path decisions are already recorded in G tasks, while remaining work is residual verification | Same as above |

## Superseded / Merged Body Files

These bodies remain useful as source detail but must not be published directly.

| Draft body | Merged into |
|---|---|
| `02-refresh-route-openapi-evidence.md` | `14-build-shared-evidence-package.md` |
| `10-build-core-import-matrix.md` | `14-build-shared-evidence-package.md` |
| `11-build-singleton-lifecycle-inventory.md` | `14-build-shared-evidence-package.md` |
| `06-create-trading-route-followup-openspec.md` | `15-decide-post-approval-plan.md` |
| `07-create-backup-route-followup-openspec.md` | `15-decide-post-approval-plan.md` |
| `12-select-first-di-pilot.md` | `15-decide-post-approval-plan.md` |
| `13-draft-first-core-split-batch.md` | `15-decide-post-approval-plan.md` |

## Required Label Setup

The repository has GitHub default labels such as `enhancement`. The Matt Pocock
triage state labels were created and verified on 2026-05-18. The commands are
retained here for audit and replay if a label is missing:

```bash
gh label create needs-triage --repo chengjon/mystocks --description "Awaiting maintainer evaluation" --color FBCA04
gh label create needs-info --repo chengjon/mystocks --description "Waiting for more information from reporter" --color 0052CC
gh label create ready-for-agent --repo chengjon/mystocks --description "Fully specified, safe for AFK agent" --color 0E8A16
gh label create ready-for-human --repo chengjon/mystocks --description "Needs human judgment or implementation" --color B60205
```

## Post-Triage Agent Readiness

After issue 1 approval and placeholder replacement:

- Issue 14 can move to `ready-for-agent` only if it passes
  `docs/reports/quality/backend-openspec-issue14-triage-gate-2026-05-18.md`.
- Issue 15 should remain `ready-for-human` or `needs-triage` because it mixes
  DI pilot selection, first Core split design, trading/backup proposal strategy,
  and G residual-tail disposition.

## Post-Publish Edits

After publishing issue 1, update every body that says
`BLOCKED_BY_TODO: issue 1` in publishable bodies 14 and 15 with the real issue
number.

After publishing issue 14, update `BLOCKED_BY_TODO: shared evidence package` in
body 15 with the real issue number.

Do not publish audit-only bodies 03, 04, or 05. Do not publish held bodies 08 or
09 until they are explicitly reclassified. Do not publish superseded bodies 02,
06, 07, 10, 11, 12, or 13 directly.
