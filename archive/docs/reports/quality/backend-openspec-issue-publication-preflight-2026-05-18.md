# Backend OpenSpec Issue Publication Preflight

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Preflight report only. At preflight time, this report did not execute any
> issue creation command.
> Later publication record: after explicit approval and runbook execution,
> issue 1 was created as `https://github.com/chengjon/mystocks/issues/80`.
> This preflight remains a pre-publication snapshot.

## Scope

Checked the draft GitHub issue publication package:

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/
```

Inputs:

- `docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md`
- 15 issue body files under the same directory; 3 are publishable, 3 are
  retained as already-resolved audit-only bodies, 2 G-line bodies are held for
  reclassification, and 7 older bodies are superseded by the compressed bodies
  14/15
- `docs/agents/issue-tracker.md`
- `docs/agents/triage-labels.md`
- `docs/reports/quality/cross-line-alignment-P3-impl-openspec-2026-05-18.md`

## Result

| Check | Result |
|---|---|
| Issue body file count | Pass: 15 retained, 3 publishable, 3 audit-only, 2 publication-hold, 7 superseded |
| `gh issue create` draft command count | Pass: 3 |
| Body file references in manifest | Pass: 0 missing |
| Labels | Pass: state labels `ready-for-human`, `needs-triage`; category label `enhancement` |
| Repository triage state labels | Pass: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human` created and verified |
| Premature `ready-for-agent` usage | Pass: none |
| Required body sections | Pass: all publishable bodies include What, Acceptance criteria, and Blocked by |
| Dependency placeholders | Pass: blockers use `BLOCKED_BY_TODO` where real issue IDs are not available |
| Publication order | Pass: issue 1 first, issue 14 second, issue 15 third; issues 03/04/05 are marked do-not-publish, issues 08/09 are held, and superseded bodies are not command targets |
| No-mutation boundaries | Pass: evidence/design issues state no implementation or mutation where required |

## Publication Safety Notes

- Do not run any manifest command until human approval records acceptance of
  `docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md`.
- Triage state labels now exist on `chengjon/mystocks`; see
  `docs/reports/quality/backend-openspec-label-setup-2026-05-18.md`.
- Publish issue 1 first.
- Do not publish `03-decide-announcement-router.md`,
  `04-decide-strategy-router.md`, or `05-decide-risk-router.md`; they were
  resolved by the P3 implementation line and are retained for audit only.
- Do not publish `08-build-health-status-taxonomy.md` or
  `09-decide-health-status-canonical-paths.md` as originally drafted; G-line
  evidence now covers their original scope and they require reclassification.
- Do not publish superseded bodies 02/06/07/10/11/12/13 directly; their scopes
  are merged into 14/15.
- Replace `BLOCKED_BY_TODO` placeholders with real GitHub issue numbers after
  publishing blockers.
- Keep all implementation work out of `ready-for-agent` until OpenSpec approval,
  evidence artifacts, consumer matrices, compatibility matrices, smoke commands,
  and rollback criteria are attached.

## Current Draft Package

| Draft | Initial label | Publication role |
|---|---|---|
| `01-approve-orchestration.md` | `ready-for-human` | Approval gate |
| `02-refresh-route-openapi-evidence.md` | none | Superseded; merged into 14 |
| `03-decide-announcement-router.md` | none | Audit-only; already resolved by P3-A1 / `243d40a8a` |
| `04-decide-strategy-router.md` | none | Audit-only; already resolved by P3-A2 / `1241c4b7e` |
| `05-decide-risk-router.md` | none | Audit-only; already resolved by P3-A3 / `243d40a8a` |
| `06-create-trading-route-followup-openspec.md` | none | Superseded; merged into 15 |
| `07-create-backup-route-followup-openspec.md` | none | Superseded; merged into 15 |
| `08-build-health-status-taxonomy.md` | none | Publication hold; G-line evidence superseded original taxonomy scope |
| `09-decide-health-status-canonical-paths.md` | none | Publication hold; G-line evidence superseded original canonical-path decision scope |
| `10-build-core-import-matrix.md` | none | Superseded; merged into 14 |
| `11-build-singleton-lifecycle-inventory.md` | none | Superseded; merged into 14 |
| `12-select-first-di-pilot.md` | none | Superseded; merged into 15 |
| `13-draft-first-core-split-batch.md` | none | Superseded; merged into 15 |
| `14-build-shared-evidence-package.md` | `needs-triage` | Publishable shared evidence package |
| `15-decide-post-approval-plan.md` | `ready-for-human` | Publishable HITL/design plan |
