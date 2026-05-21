# Backend OpenSpec Issue 92 Downstream Rollup Closeout

Date: 2026-05-21
Parent issue: `#92`
Track: D2 downstream decision rollup
Base HEAD: `cc62bb657127b83dffaa06617b3592457b24aabb`
Prepared at: `2026-05-21T05:03:20Z`
Aligned at: `2026-05-21T05:31:00Z`
Status: downstream decision package rollup prepared; review feedback absorbed; implementation remains locked

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Boundary

This rollup closes the D2 downstream planning sequence as a prepared decision
package. It does not authorize implementation.

It does not:

- Move issue `#92` or any child track to `ready-for-agent`.
- Create GitHub issues.
- Create OpenSpec changes or specs.
- Approve backend source edits.
- Approve route, OpenAPI, docs/API, frontend, test, PM2, script, or config changes.
- Retire compatibility wrappers.
- Execute PM2 gates.

## Issue 92 Current State

| Field | Current value |
|---|---|
| Issue | `#92` |
| Title | `[Backend OpenSpec] Decide post-approval implementation plan` |
| State | `OPEN` |
| Labels | `enhancement`, `ready-for-downstream`, `ready-for-human` |
| `ready-for-agent` | Absent |
| Role | Parent decision issue for downstream implementation planning |

## Review Alignment

The current review feedback found no factual discrepancies in the rollup's PR
chain, issue label state, base HEAD, or implementation boundary. It identified
one low-risk completeness issue: the D2.2 row used narrative labels instead of
explicit evidence filenames. That gap is addressed below by listing the four
D2.2 evidence files directly.

Additional cross-line project facts were supplied through
`docs/reports/quality/five-line-work-summary-2026-05-21.md` as review input.
At the time of this alignment that file was untracked in the root worktree, so
the relevant facts are copied into this report as supporting context rather
than treated as a tracked canonical evidence artifact.

## D2 Package Status

| Track | State | Evidence | Implementation authority |
|---|---|---|---|
| D2 acceptance | Accepted | `docs/reports/quality/backend-openspec-issue92-downstream-split-acceptance-2026-05-21.md`; PR `#96` | No implementation authority |
| D2.1 DI pilot design | Design packet prepared | `docs/reports/quality/backend-di-pilot-technical-pattern-detection-design-2026-05-21.md`; PR `#97` | No source edits; needs separate implementation approval |
| D2.2 wrapper readiness | Decision lane closed | `docs/reports/quality/backend-core-validation-wrapper-retirement-readiness-2026-05-21.md`; `docs/reports/quality/backend-core-validation-active-source-migration-2026-05-21.md`; `docs/reports/quality/backend-core-validation-docs-api-canonicalization-2026-05-21.md`; `docs/reports/quality/backend-core-validation-wrapper-retirement-decision-package-2026-05-21.md`; PRs `#98`-`#101` | Wrapper deletion locked unless D2.2d is separately approved |
| D2.3 trading route governance | Planning package prepared | `docs/reports/quality/backend-trading-route-openapi-governance-planning-package-2026-05-21.md`; PRs `#102` and `#103` | Route mutation locked |
| D2.4 backup route ownership | Planning package prepared | `docs/reports/quality/backend-backup-route-ownership-planning-package-2026-05-21.md`; PR `#104` | Backup route mutation locked |
| D2.5 control-plane OpenAPI docs | Planning package prepared | `docs/reports/quality/backend-control-plane-openapi-docs-planning-package-2026-05-21.md`; PR `#105` | docs/API or route mutation locked |
| D2.6 PM2 stateful gate approval | Approval governance package prepared | `docs/reports/quality/backend-pm2-stateful-gate-approval-governance-2026-05-21.md`; PR `#106` | PM2 execution locked unless separately approved |

## Cross-Line Support Facts

These facts support the D2 rollup but do not change its authorization boundary:

- `sequence-backend-architecture-unblocks` runtime unblock was reported valid
  at clean HEAD `f97f2eb57`: `app.main` routes=`548`, health collect-only
  `112 tests collected`, OpenAPI paths=`500`, operation IDs=`536`, duplicate
  operation IDs=`0`.
- That runtime evidence proves import, collect-only, and minimal OpenAPI smoke
  health only. It does not close PM2/backend runtime gate, Core Batch 2,
  endpoint retirement, or OpenSpec archive decisions.
- The stale `data_lineage` import blocker is no longer a reason to block the
  rollup. It was fixed on a separate implementation lane, outside issue `#83`
  evidence-only scope.
- The route/OpenAPI evidence after that unblock reported runtime routes=`548`,
  runtime unique paths=`511`, schema-visible routes=`536`, hidden runtime
  routes=`12`, endpoint modules=`98`, OpenAPI paths=`500`, OpenAPI
  operations=`536`, duplicate operation IDs=`0`, and OpenAPI warnings=`0`.
- The remaining `GET /metrics` duplicate runtime path/method is already
  classified as a control-plane taxonomy item, not as an OpenAPI duplicate
  operationId or deletion authorization.
- miniQMT external evidence has advanced through raw/candidate acceptance,
  validated-forward validator/preview/apply, manual promote to validated, and
  authoritative-ready. It still does not authorize source cutover, Quantix
  ClickHouse writes, backend promotion, or production application.

## Merged PR Chain

| PR | Merge commit | Purpose |
|---|---|---|
| `#96` | `f95266cd5338` | Record issue `#92` downstream split acceptance |
| `#97` | `458acb27888b` | Draft `TechnicalPatternDetectionService` DI pilot design |
| `#98` | `ac6c209cc525` | Draft Core validation wrapper retirement readiness |
| `#99` | `c54c17e30e0a` | Migrate active source imports to canonical `app.core.validation` |
| `#100` | `7d4e86d71e2f` | Canonicalize validation examples under `docs/api/` |
| `#101` | `c24f430167bb` | Prepare Core validation wrapper retirement / retention decision package |
| `#102` | `1b8ac1c16060` | Prepare D2.3 trading route governance planning package |
| `#103` | `553e71a90c83` | Clarify D2.3 review notes |
| `#104` | `b39b7b3ee07d` | Prepare D2.4 backup route ownership planning package |
| `#105` | `ca215767b4bb` | Prepare D2.5 control-plane OpenAPI docs planning package |
| `#106` | `ae6ffd685cf6` | Prepare D2.6 PM2 stateful gate approval governance |

## Decision Inventory

| Decision | Current result | Next gate |
|---|---|---|
| First DI pilot | `TechnicalPatternDetectionService` selected as design pilot | Human review of D2.1 packet, then create a separate implementation issue or OpenSpec branch if approved |
| Core validation wrapper | Active source and docs/API consumers are canonicalized; wrapper remains | Choose long-term retention or a separate D2.2d deletion implementation batch |
| Trading routes | Fold into unified route/OpenAPI governance | Create explicit route/OpenAPI governance proposal before route mutation |
| Backup routes | Keep as dedicated route ownership proposal candidate | Create explicit backup route ownership proposal before backup route mutation |
| Control-plane docs | Keep as dedicated documentation/probe governance lane | Create explicit control-plane docs proposal before docs/API or route mutation |
| PM2 gates | Future PM2 execution needs explicit approval or named equivalent | Create a small approval issue or runbook only when a future lane needs fresh PM2 evidence |

## What Is Ready

The D2 downstream decision package is ready for human selection of the first
true implementation lane.

Recommended first implementation candidate:

1. D2.1a `TechnicalPatternDetectionService` DI pilot implementation.

Reason:

- It is already the accepted first DI design pilot.
- It has a narrow service and route consumer surface.
- It should produce reusable lifecycle DI rules before larger singleton/service migrations.

Alternative future lanes remain valid but should not be opened implicitly:

- D2.2d Core validation wrapper deletion.
- Unified route/OpenAPI governance proposal.
- Backup route ownership proposal.
- Control-plane OpenAPI docs stabilization proposal.
- PM2 stateful gate approval issue, only when fresh PM2 execution is actually needed.

## What Remains Locked

- No downstream work is `ready-for-agent` from this rollup alone.
- No OpenSpec proposal is created by this rollup.
- No source changes are authorized by this rollup.
- No compatibility wrapper deletion is authorized by this rollup.
- No route or OpenAPI mutation is authorized by this rollup.
- No PM2 execution is authorized by this rollup.

## Recommended Closeout Statement for Issue 92

Issue `#92` can now be treated as having a complete downstream decision package.

Suggested next human decision:

1. Approve D2.1a as the first concrete implementation lane.
2. Keep the other lanes as future explicit proposals or issues.
3. Move only the newly created D2.1a implementation issue, not issue `#92`, to `ready-for-agent` after its own scope, tests, rollback, and GitNexus impact gates are written.

## Verification for This Rollup

Expected verification is document/governance only:

- Markdown governance gate on this report and the steward task tree.
- YAML parse for the PR task card.
- `git diff --check`.
- Mainline scope gate for the task card.
- GitNexus staged change detection before commit.
