# Backend OpenSpec Issue Readiness Blueprint

> Superseded current-source note:
> This file is retained for audit history. The current compressed publication
> blueprint is
> `docs/reports/quality/backend-openspec-issue-readiness-blueprint-compressed-2026-05-18.md`.

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
| `openspec/changes/consolidate-backend-api-domain-routers/` | C proposal |
| `openspec/changes/consolidate-backend-health-endpoints/` | G proposal |
| `openspec/changes/migrate-backend-singletons-to-lifecycle-di/` | E proposal |
| `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/` | F proposal |
| `docs/reports/quality/cross-line-alignment-P3-impl-openspec-2026-05-18.md` | Cross-line status showing P3-resolved issue drafts and remaining publishable work |
| `docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md` | G-line progress sync; confirms G residual verification should not merge into issue 1 approval |

## Cross-Line Alignment Status

The original body set still contains 13 draft files for audit continuity. After
P3 and G-line implementation alignment, only 8 should be published as currently
written. Drafts 03, 04, and 05 are already resolved by P3 decision records and
implementation commits, so they are retained only as audit history. Drafts 08
and 09 are held for reclassification because G-line evidence superseded their
original health/status taxonomy and canonical-path scopes.

## Label Rule

Per `docs/agents/triage-labels.md`, no implementation issue in this blueprint
should be labeled `ready-for-agent` before OpenSpec approval and explicit
`Blocked by` links exist.

Use:

- `ready-for-human`: approval, decision, and canonical ownership issues.
- `needs-triage`: draft issues waiting for approval or dependency IDs.
- `ready-for-agent`: only after approval, dependencies are resolved, and the
  issue contains enough evidence, acceptance criteria, commands, and rollback
  instructions for an AFK agent.

## Dependency Order

```text
P0 approval gate
  -> shared route/OpenAPI evidence
      -> C post-P3 route/OpenAPI reconciliation
      -> G residual-tail reclassification
      -> trading follow-up proposal
      -> backup follow-up proposal
  -> F Core import compatibility matrix
      -> E shared-Core lifecycle safety
  -> E singleton/getter inventory
      -> E first low-risk pilot decision
```

## Draft Issue Set

### 1. HITL: Approve backend OpenSpec orchestration and C/E/F/G proposal scope

**Current label**: `ready-for-human`

**Post-approval label**: closed / approved reference, not `ready-for-agent`

**OpenSpec requirement**:

- `docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md`
- `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md`
- `docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md`
- C/E/F/G proposal directories under `openspec/changes/`

**What to decide**:

Approve, revise, or reject the orchestration artifact and four OpenSpec drafts
as proposal-level governance changes, acknowledging that P3 already resolved
the C announcement, strategy, and risk canonical-router decisions.

**Original acceptance criteria, now superseded by G-line evidence**:

- Human reviewer records approval or requested revisions.
- The approval record explicitly states that implementation is not unlocked.
- The approval record states that issue drafts 03, 04, and 05 are audit-only and
  should not be published as new HITL decision issues.
- The approval record accepts or revises the remaining C/E/F/G scope boundaries.
- The approval record states whether trading and backup need one follow-up
  proposal each or one shared route ownership proposal.

**Blocked by**: none

### 2. AFK-after-approval: Refresh shared route table and OpenAPI evidence

**Current label**: `needs-triage`

**Post-approval label**: `ready-for-agent` if issue #1 is approved and command
environment is available.

**OpenSpec requirement**:

- C tasks 1.2-1.5
- G tasks 1.2-1.5

**What to build**:

Regenerate or confirm the current local route baseline, prefix-expanded
full-path route table, and OpenAPI baseline used by C/G decisions after P3
implementation alignment.

**Original acceptance criteria, now superseded by G-line evidence**:

- `docs/reports/quality/generated/backend-fullpath-route-table.md` exists and
  records current branch / HEAD / summary.
- `docs/reports/quality/generated/backend-fullpath-route-table.json` exists.
- `docs/reports/quality/generated/openapi-before.json` exists, or the issue
  records why OpenAPI generation is blocked.
- Existing route table evidence is cited: 538 routes, 0 full-path duplicate
  groups, and 2 remaining orphan route files after the P3-D scanner fix.
- Existing OpenAPI baseline is cited: OpenAPI 3.1.0 with 501 paths.
- Post-P3 route/OpenAPI evidence is diffed against
  `docs/reports/quality/generated/openapi-before.json`, or the issue records
  why the baseline is already current.
- The issue summary classifies local decorator duplicates separately from
  final full-path duplicate conflicts.
- No route mutation is performed.

**Verification commands**:

```bash
cd web/backend && python ../../scripts/dev/backend_audit_fullpath_routes.py ../../docs/reports/quality/generated
python scripts/generate_openapi.py --output docs/reports/quality/generated/openapi-before.json
```

**Blocked by**: issue #1

### 3. HITL: Decide C announcement canonical router and compatibility path

**Current label**: none

**Post-approval label**: audit-only / do not publish

**OpenSpec requirement**:

- C tasks 2.1, 2.6, 2.7

**Aligned status**:

Already resolved by P3-A1 and commit `243d40a8a`. The `announcement/` package
is canonical and `announcement.py` has been deleted. Retain this section only as
historical context; do not publish a new GitHub issue for this decision.

**What to decide**:

Choose the canonical announcement router contract and compatibility path based
on route/OpenAPI evidence and consumer matrix.

**Acceptance criteria**:

- Decision record identifies canonical path, retained compatibility paths, and
  retirement candidates.
- Decision cites current route table and OpenAPI evidence.
- Consumer matrix covers backend imports, frontend calls, tests, scripts, and
  documentation-only references.
- Rollback trigger is named.

**Publication status**: do not publish; already resolved by P3.

### 4. HITL: Decide C strategy canonical router and mock compatibility

**Current label**: none

**Post-approval label**: audit-only / do not publish

**OpenSpec requirement**:

- C tasks 2.2, 2.6, 2.7

**Aligned status**:

Already resolved by P3-A2 and commit `1241c4b7e`. The
`strategy_management/` package is canonical and the route surface has converged.
Retain this section only as historical context; do not publish a new GitHub
issue for this decision.

**What to decide**:

Choose the canonical strategy router contract and define how
`strategy.py`, `strategy_mgmt.py`, `strategy_management.py`,
`strategy_management/`, and `strategy_list_mock.py` remain compatible or exit.

**Acceptance criteria**:

- Decision record names canonical strategy route surface.
- Mock router behavior is classified as production, development-only, or
  compatibility surface.
- Frontend/test consumers are classified.
- No flat module deletion is approved by this decision alone.

**Publication status**: do not publish; already resolved by P3.

### 5. HITL: Decide C risk canonical router and v31 compatibility

**Current label**: none

**Post-approval label**: audit-only / do not publish

**OpenSpec requirement**:

- C tasks 2.3, 2.6, 2.7

**Aligned status**:

Already resolved by P3-A3 and commit `243d40a8a`. The `risk/` package is
canonical and orphan risk files have been removed. Retain this section only as
historical context; do not publish a new GitHub issue for this decision.

**What to decide**:

Choose the canonical risk router contract and define how legacy risk surfaces
and v31 routes remain compatible.

**Acceptance criteria**:

- Decision record names canonical risk route surface.
- v31 compatibility is retained, retired, or mapped with explicit approval.
- Service consumers and frontend/test callers are classified.
- Rollback trigger is named.

**Publication status**: do not publish; already resolved by P3.

### 6. HITL: Create trading route ownership follow-up OpenSpec proposal

**Current label**: `needs-triage`

**Post-approval label**: `ready-for-human`

**OpenSpec requirement**:

- C tasks 1.9 and 2.4
- Orchestration blocking matrix: Trading router implementation

**What to decide**:

Create a separate proposal for `trading_runtime.py` versus
`trading_monitor.py` ownership, or intentionally fold it into a broader route
ownership proposal.

**Acceptance criteria**:

- Follow-up OpenSpec change ID is recorded.
- Proposal cites route table evidence for trading duplicate paths.
- Implementation remains blocked until the follow-up is approved.

**Blocked by**: issues #1 and #2

### 7. HITL: Create backup route ownership follow-up OpenSpec proposal

**Current label**: `needs-triage`

**Post-approval label**: `ready-for-human`

**OpenSpec requirement**:

- C tasks 1.9 and 2.5
- G tasks 2.6
- Orchestration blocking matrix: Backup router implementation

**What to decide**:

Create a separate proposal for `backup_recovery.py` versus
`backup_recovery_secure/` ownership and its security boundary.

**Acceptance criteria**:

- Follow-up OpenSpec change ID is recorded.
- Proposal cites route table evidence for backup duplicate paths.
- `backup_recovery_secure/cleanup_old_backups.py` is classified as domain
  route ownership, health/status taxonomy, or both with a clear owner.
- Implementation remains blocked until the follow-up is approved.

**Blocked by**: issues #1 and #2

### 8. Publication Hold: Build G health/status taxonomy and consumer matrix

**Current label**: none

**Post-approval label**: none until reclassified.

**OpenSpec requirement**:

- G tasks 1.6-1.8
- G tasks 2.1-2.7

**Current disposition**:

Do not publish this body as originally drafted. G-line evidence now records the
taxonomy/canonical-path work this issue was going to request.

If further tracking is needed, reclassify it into a residual-tail issue for the
remaining G blockers instead of rebuilding taxonomy:

- OpenAPI documentation/schema stabilization for `4.6`.
- PM2 workflow approval or named equivalent for `4.7`.

**Acceptance criteria**:

- Each health/status endpoint is classified as platform liveness/readiness,
  system service health, platform status, domain smoke/status,
  metrics/observability, adapter/database diagnostic, example, or embedded app.
- Consumer matrix lists active, compatibility, and documentation-only consumers.
- `/health/readiness` absence is confirmed unless intentionally added by later
  approval.
- P3-A5 taxonomy and the 52-route inventory are cited or superseded.
- The output identifies the canonical `/health` handler candidate and any
  compatibility aliases requiring HITL decision.
- No route mutation is performed.

**Blocked by**: reclassification decision.

### 9. Publication Hold: Decide G canonical health/status paths and compatibility timing

**Current label**: none

**Post-approval label**: none until reclassified.

**OpenSpec requirement**:

- G tasks 2.1-2.7

**Current disposition**:

Do not publish this body as originally drafted. G tasks `2.1-2.7` already record
canonical liveness, readiness, services health, status taxonomy, domain
smoke/status separation, backup ownership deferral, and rollback trigger
decisions.

**Acceptance criteria**:

- Decision record names canonical liveness, readiness, services health, and
  status paths.
- Compatibility paths and deprecation timing are explicit.
- PM2/monitoring/CI/frontend/test consumers are preserved or migration is
  explicitly approved.
- Rollback trigger per endpoint category is named.

**Blocked by**: reclassification decision.

### 10. AFK-after-approval: Build F Core import compatibility matrix

**Current label**: `needs-triage`

**Post-approval label**: `ready-for-agent` if issue #1 is approved and no file
movement is included.

**OpenSpec requirement**:

- F tasks 1.2-1.6
- F tasks 2.1-2.6

**What to build**:

Produce the Core import compatibility matrix with old import path, canonical
target path, wrapper/re-export strategy, lifecycle owner, monkeypatch consumers,
and rollback path.

**Acceptance criteria**:

- Matrix covers high-risk Core paths including database, cache, security,
  socketio, and logger.
- Lifecycle-owned Core modules are identified and linked to E coordination.
- `app.core.logger` remains canonical.
- No file movement is performed.

**Blocked by**: issue #1

### 11. AFK-after-approval: Build E singleton/getter lifecycle inventory

**Current label**: `needs-triage`

**Post-approval label**: `ready-for-agent` if issue #1 is approved and no
lifecycle mutation is included.

**OpenSpec requirement**:

- E tasks 1.2-1.6

**What to build**:

Generate singleton/getter inventory, classify candidates by lifecycle class, and
mark candidates blocked by F import compatibility.

Reuse or explicitly supersede the P3-A4 singleton lifecycle inventory before
creating new E evidence.

**Acceptance criteria**:

- Singleton baseline artifact is generated or refreshed.
- Getter inventory artifact is generated.
- Existing P3-A4 lifecycle inventory is cited or superseded.
- Candidates are classified as stateless helper, heavy service, adapter
  factory, cache-backed service, connection-backed service, or compatibility
  getter.
- Shared-Core candidates are marked blocked by F matrix.
- No lifecycle mutation is performed.

**Verification commands**:

```bash
python scripts/dev/backend_audit_baseline.py docs/reports/quality/generated
rg -n "^def get_\\w+\\(" web/backend/app > docs/reports/quality/generated/backend-getter-inventory.txt
```

**Blocked by**: issue #1

### 12. HITL: Select E first low-risk DI pilot

**Current label**: `needs-triage`

**Post-approval label**: `ready-for-human`

**OpenSpec requirement**:

- E tasks 2.1-2.5

**What to decide**:

Select exactly one low-risk representative DI pilot and define override,
teardown, compatibility getter, rollback, and verification expectations.

**Acceptance criteria**:

- Only one pilot candidate is selected.
- If the pilot touches Core modules, F matrix dependency is resolved.
- Dependency override strategy is named.
- Teardown artifact type is named.
- Rollback path is named.

**Blocked by**: issues #10 and #11

### 13. AFK-after-approval: Draft first F low-risk Core split batch

**Current label**: `needs-triage`

**Post-approval label**: `ready-for-agent` only if issue #10 is complete and
the batch is evidence/design-only. Code movement remains separate.

**OpenSpec requirement**:

- F tasks 3.1-3.4
- F tasks 4.1-4.5

**What to build**:

Draft the first Core split batch from non-lifecycle-owned pure helpers, including
import smoke, targeted test scope, PM2 smoke, and rollback notes.

**Acceptance criteria**:

- Batch contains only one Core domain or a small pure-helper group.
- No lifecycle-owned module is included.
- Import smoke includes `from app.core.logger import logger`.
- PM2/backend smoke command is named.
- Rollback path is named.
- This issue does not move files unless a later implementation issue explicitly
  approves that movement.

**Blocked by**: issues #1 and #10

## Publishing Guidance

Publish issues only after issue #1 records approval or requested revisions.

Draft body files and `gh issue create` command examples are available in:

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md
```

Do not run those commands until approval is recorded and `BLOCKED_BY_TODO`
placeholders are replaced with real issue numbers.

Authoritative publication order is the manifest command order:

1. Issue #1.
2. Issue #2.
3. Issue #8.
4. Issue #9.
5. Issues #10 and #11.
6. Issue #12.
7. Issue #13.
8. Issues #6 and #7.
9. Skip audit-only issue bodies #3, #4, and #5 unless a human explicitly asks
   for historical tracking issues.
10. Later implementation issues only after their decision records and evidence
   artifacts are accepted.
