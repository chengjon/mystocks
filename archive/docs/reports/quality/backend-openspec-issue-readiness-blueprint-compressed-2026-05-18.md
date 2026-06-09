# Backend OpenSpec Issue Readiness Blueprint Compressed

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Planning artifact only. This file does not create GitHub Issues and does not
> approve implementation. Use it after human approval to publish issues in
> dependency order with explicit `Blocked by` references.

## Inputs

| Input | Purpose |
|---|---|
| `docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md` | Approval entry point |
| `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md` | Cross-change dependencies and allowed parallel batches |
| `docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md` | G-line progress sync and publication-hold decision for 08/09 |
| `docs/reports/quality/backend-openspec-issue14-triage-gate-2026-05-18.md` | Gate for moving issue 14 from `needs-triage` to `ready-for-agent` |
| `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` | Adopted input baseline for issue 15 / future proposal planning; not part of the issue 1 publication gate |
| `docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md` | Current 3-command publication manifest |
| `openspec/changes/consolidate-backend-api-domain-routers/` | C proposal |
| `openspec/changes/consolidate-backend-health-endpoints/` | G proposal |
| `openspec/changes/migrate-backend-singletons-to-lifecycle-di/` | E proposal |
| `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/` | F proposal |

## Current Package Shape

The body directory retains 15 draft files for audit continuity.

| Category | Count | Bodies |
|---|---:|---|
| Publishable | 3 | `01`, `14`, `15` |
| Audit-only / do-not-publish | 3 | `03`, `04`, `05` |
| Publication hold / reclassification | 2 | `08`, `09` |
| Superseded / merged source bodies | 7 | `02`, `06`, `07`, `10`, `11`, `12`, `13` |

## Dependency Order

```text
1 approval gate
  -> 14 shared C/E/F evidence package
      -> 15 post-approval plan and follow-up boundaries
```

Held G bodies 08/09 are outside this order until reclassified.

## Publishable Issue Set

### 1. HITL: Approve backend OpenSpec orchestration and C/E/F/G proposal scope

**Current label**: `ready-for-human`

**Post-approval label**: closed / approved reference, not `ready-for-agent`

**Body file**:

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/01-approve-orchestration.md
```

**What to decide**:

Approve, revise, or reject the orchestration artifact and four OpenSpec drafts
as proposal-level governance changes, acknowledging:

- P3 already resolved the C announcement, strategy, and risk canonical-router
  decisions.
- G-line evidence superseded original issue drafts 08/09.
- The current publishable package is compressed to 3 issues.
- Backend implementation remains locked.

**Blocked by**: none.

### 14. AFK-after-approval: Build shared C/E/F evidence package

**Current label**: `needs-triage`

**Post-approval label**: `ready-for-agent` only after issue 1 approval,
placeholder replacement, and triage confirmation that the issue remains
evidence-only under
`docs/reports/quality/backend-openspec-issue14-triage-gate-2026-05-18.md`.

**Body file**:

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/14-build-shared-evidence-package.md
```

**Merged source bodies**:

- `02-refresh-route-openapi-evidence.md`
- `10-build-core-import-matrix.md`
- `11-build-singleton-lifecycle-inventory.md`

**What to build**:

Build one shared evidence package for C/E/F:

- Route table and OpenAPI evidence for C.
- Core import compatibility matrix for F.
- Singleton/getter lifecycle inventory for E.

**Blocked by**: issue 1 approval.

### 15. HITL/design: Decide post-approval implementation plan and follow-up boundaries

**Current label**: `ready-for-human`

**Post-approval label**: keep as `ready-for-human` or `needs-triage`; this is
not a pure AFK-agent evidence issue.

**Body file**:

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/15-decide-post-approval-plan.md
```

**Merged source bodies**:

- `06-create-trading-route-followup-openspec.md`
- `07-create-backup-route-followup-openspec.md`
- `12-select-first-di-pilot.md`
- `13-draft-first-core-split-batch.md`

**Held source bodies for G residual-tail reclassification**:

- `08-build-health-status-taxonomy.md`
- `09-decide-health-status-canonical-paths.md`

**What to decide**:

- Select exactly one low-risk DI pilot.
- Draft the first low-risk Core split batch.
- Decide trading route ownership follow-up proposal strategy.
- Decide backup route ownership follow-up proposal strategy.
- Decide whether held G drafts 08/09 should be replaced by residual-tail issues
  for OpenAPI documentation stabilization and PM2 workflow approval.
- Decide whether issue 15 should remain one aggregated decision/design issue or
  be split into smaller follow-up decision issues before execution.
- Classify adopted codebase-map concerns as issue 14 evidence, issue 15
  decisions, future separate proposal candidates, or quality-debt lanes.

**Blocked by**: issue 1 approval and shared evidence package.

## Non-Publishable Bodies

### Audit-only / already resolved

| Body | Status |
|---|---|
| `03-decide-announcement-router.md` | P3-resolved; do not publish |
| `04-decide-strategy-router.md` | P3-resolved; do not publish |
| `05-decide-risk-router.md` | P3-resolved; do not publish |

### Publication hold

| Body | Status |
|---|---|
| `08-build-health-status-taxonomy.md` | G-line evidence superseded original scope; reclassify before publishing |
| `09-decide-health-status-canonical-paths.md` | G-line evidence superseded original scope; reclassify before publishing |

### Superseded / merged

| Body | Merged into |
|---|---|
| `02-refresh-route-openapi-evidence.md` | `14-build-shared-evidence-package.md` |
| `10-build-core-import-matrix.md` | `14-build-shared-evidence-package.md` |
| `11-build-singleton-lifecycle-inventory.md` | `14-build-shared-evidence-package.md` |
| `06-create-trading-route-followup-openspec.md` | `15-decide-post-approval-plan.md` |
| `07-create-backup-route-followup-openspec.md` | `15-decide-post-approval-plan.md` |
| `12-select-first-di-pilot.md` | `15-decide-post-approval-plan.md` |
| `13-draft-first-core-split-batch.md` | `15-decide-post-approval-plan.md` |
