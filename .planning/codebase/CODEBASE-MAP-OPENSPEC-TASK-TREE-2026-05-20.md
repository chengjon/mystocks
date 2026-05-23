# CODEBASE-MAP OpenSpec Task Tree

Status: Draft steward index for review
Date: 2026-05-20
Branch checked: `wip/root-dirty-20260403`
HEAD checked: `7b097fffd Record miniQMT authoritative-ready evidence alignment`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This document is a coordination and evidence index only. It does
not authorize source code changes, GitHub issue publication, OpenSpec proposal
publication, OpenSpec implementation, old `.planning/codebase/` document
replacement, production rollout, or promotion of external evidence into backend
truth.

## Purpose

This file is the steward index for the current CODEBASE-MAP architecture
remediation program. It keeps the relationship between the master execution
plan, the nine execution reports, OpenSpec branches, GitHub issues, and
verification artifacts visible in one place.

The steward index exists so future workers do not keep expanding the master
execution plan after every implementation batch. Completed work should update
the relevant OpenSpec `tasks.md`, this tree, and the codebase map evidence
index.

## Source Hierarchy

```text
Architecture baseline
└── .planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md
    ├── approved input baseline
    ├── current codebase facts
    ├── architecture risk candidates
    └── evidence links, not implementation authority

Master execution plan
└── docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md
    ├── total control plan for this remediation round
    ├── sequencing of gates, waves, evidence, and non-goals
    ├── source for OpenSpec branch decomposition
    └── not a replacement for individual OpenSpec changes

Execution evidence and decision reports
└── docs/reports/quality/*-2026-05-19.md
    ├── nine reports produced from the master plan
    ├── current factual evidence
    ├── closure records
    ├── decision records
    └── branch inputs, not standalone roadmaps

OpenSpec implementation and governance branches
└── openspec/changes/<change-id>/
    ├── concrete scoped branch tasks
    ├── spec deltas when behavior or governance changes
    ├── implementation gates after approval
    └── archive target after completion
```

## State Legend

| State | Meaning |
|---|---|
| `baseline` | Approved input or reference document; no implementation authority by itself. |
| `evidence-complete` | Evidence report exists and can be used as input. |
| `decision-only` | A decision or boundary was recorded; no implementation branch is currently authorized. |
| `proposed` | OpenSpec change exists and validates, but has not been approved for execution. |
| `candidate` | A likely future OpenSpec branch or work lane; it has not been created or approved. |
| `blocked` | Work must not proceed until the named gate is closed. |
| `ready-after-approval` | Work may proceed only after explicit human/OpenSpec approval. |
| `implemented` | Code or documentation work completed and verified. |
| `archived` | OpenSpec branch has been archived after accepted completion. |
| `contradiction-unresolved` | Two current evidence rows conflict at the same HEAD or cannot be ordered by freshness; dependent work is blocked until reconciliation is recorded. |

## Steward Tree

```text
CODEBASE-MAP Architecture Remediation Program
├── A. Architecture Baseline
│   ├── Source: .planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md
│   ├── State: baseline
│   ├── Role: Current architecture fact and risk-candidate entry point
│   └── Next gate: Update only with linked evidence and current-head freshness
│
├── B. Master Execution Plan
│   ├── Source: docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md
│   ├── State: baseline
│   ├── Role: Total control plan for this remediation round
│   └── Next gate: Decompose into OpenSpec branches instead of expanding endlessly
│
├── C. OpenSpec Branch 1: sequence-backend-architecture-unblocks
│   ├── Source: openspec/changes/archive/2026-05-20-sequence-backend-architecture-unblocks/
│   ├── State: archived
│   ├── Role: First concrete branch extracted from the master plan and reports
│   ├── Scope C-shallow: Runtime unblock, schema shim closure, codebase-map
│   │                   consistency, and runtime evidence refresh
│   ├── Scope C-deep-prep: Singleton/service seam classification and proposal
│   │                     preparation only
│   └── Next gate: Use archived evidence as the accepted unblock baseline;
│                  continue new implementation only through a follow-up OpenSpec branch
│
├── D. Existing OpenSpec Branch: split-backend-core-modules-with-compatibility-wrappers
│   ├── Source: openspec/changes/archive/2026-05-21-split-backend-core-modules-with-compatibility-wrappers/
│   ├── State: archived-merged
│   ├── Role: Core helper split line
│   ├── Current fact: issue #83 shared C/E/F evidence accepted; Task 3.2
│   │                 explicitly disposed as complete for the current
│   │                 validation-helper package/wrapper scope
│   └── Next gate: Keep archived evidence as the completed baseline; any further
│                  Core split implementation still needs a separate concrete plan and approval
│
├── D2. Published Decision Issue: backend OpenSpec issue15
│   ├── Source: https://github.com/chengjon/mystocks/issues/92
│   ├── State: downstream-split-accepted
│   ├── Role: Human decision/design issue for post-approval implementation planning
│   ├── Current fact: issue #83 accepted and closed; Core split OpenSpec archived;
│   │                 issue #92 has `ready-for-downstream`, no `ready-for-agent`,
│   │                 and no implementation authority; downstream split is
│   │                 accepted in
│   │                 `backend-openspec-issue92-downstream-split-acceptance-2026-05-21.md`
│   └── Next gate: Human review of D2.1 `TechnicalPatternDetectionService`
│                  DI design packet; keep all downstream tracks
│                  decision/proposal-only until separate implementation
│                  approval exists
│
├── D2.1. Accepted DI Design Pilot: TechnicalPatternDetectionService
│   ├── Source evidence:
│   │   `backend-di-pilot-technical-pattern-detection-design-2026-05-21.md`
│   ├── State: design-packet-prepared
│   ├── Role: First DI lifecycle design pilot from issue `#92`
│   ├── Current fact: GitNexus impact is LOW with 0 affected symbols/processes;
│   │                 route consumer is `_technical_patterns_router.py`;
│   │                 implementation remains locked
│   └── Next gate: Human review of D2.1a implementation authorization package
│                  before creating any implementation issue or moving any issue
│                  to `ready-for-agent`
│
├── D2.1a. TechnicalPatternDetectionService DI Pilot Implementation Authorization
│   ├── Source evidence:
│   │   `docs/superpowers/plans/2026-05-21-d2-1a-technical-pattern-detection-di-pilot-implementation-authorization.md`
│   ├── State: implementation-authorization-consumed
│   ├── Role: Concrete implementation package for the first DI lifecycle pilot
│   ├── Current fact: planned write scope was limited to
│   │                 `web/backend/app/api/_technical_patterns_router.py` and
│   │                 `web/backend/tests/test_technical_patterns_router_regressions.py`;
│   │                 `TechnicalPatternDetectionService` internals remain
│   │                 unchanged; GitNexus impact is LOW for both the service
│   │                 class and `_detect_patterns_for_symbol`
│   └── Next gate: Completed by D2.1a.1; no additional D2.1a implementation
│                  authority remains. Any second DI pilot must start as a
│                  separate approved proposal or implementation child item
│
├── D2.1a.1. TechnicalPatternDetectionService DI OpenSpec Child Branch
│   ├── Source evidence:
│   │   `openspec/changes/inject-technical-pattern-detection-service-di/`
│   ├── State: implementation-and-governance-closed
│   ├── Role: Convert the D2.1a authorization plan into a separately
│   │         reviewable implementation child branch
│   ├── Current fact: Route-level DI implementation merged in PR `#112`
│   │                 (`80582643578d587ead81ccb3d23dcd2a52668dba`), and final
│   │                 OpenSpec checklist governance merged in PR `#113`
│   │                 (`c7e263b8fcdeea4fc952a86d64ac555ca6dde6ce`).
│   │                 `_technical_patterns_router.py`
│   │                 now exposes `get_technical_pattern_detection_service()`,
│   │                 `detect_patterns()` receives the service through
│   │                 `Depends`, and focused public-route tests use
│   │                 `app.dependency_overrides` with an async
│   │                 `detect_for_symbol(symbol, period)` service double.
│   │                 Verification evidence: TDD red confirmed missing provider;
│   │                 green suite reports route regression `9 passed`,
│   │                 service+route `19 passed`, ruff touched files passed,
│   │                 placeholder-env `app.main` import passed, OpenSpec strict
│   │                 validate passed; PR `#113` records task `5.3` evidence
│   │                 back to issue `#92`
│   └── Next gate: None for D2.1a. Keep issue `#92` as parent decision context;
│                  future service DI work returns to branch `G` and requires a
│                  new approved child proposal or implementation issue
│
├── D2.2. Core Validation Wrapper Retirement Readiness
│   ├── Source evidence:
│   │   `backend-core-validation-wrapper-retirement-readiness-2026-05-21.md`
│   ├── State: formally-closed-decision-package
│   ├── Role: Decide whether `app.core.validation_messages` can retire
│   ├── Current fact: D2.2a migrated active source consumers in `validators.py`
│   │                 and `error_codes.py` to `app.core.validation`; wrapper
│   │                 remains because D2.2c prepared a decision package, not a
│   │                 deletion implementation; D2.2 is closed as a planning /
│   │                 decision lane
│   └── Next gate: Move to D2.3 trading route/OpenAPI governance planning;
│                  wrapper deletion remains locked unless a separate D2.2d
│                  implementation batch is explicitly approved
│
├── D2.2a. Core Validation Active Source Consumer Migration
│   ├── Source evidence:
│   │   `backend-core-validation-active-source-migration-2026-05-21.md`
│   ├── State: implementation-complete
│   ├── Role: Move active source consumers to canonical `app.core.validation`
│   ├── Current fact: active source legacy imports excluding the wrapper are `0`;
│   │                 compatibility wrapper and compatibility test are retained
│   └── Next gate: Completed by D2.2b docs/API examples canonicalization;
│                  wrapper deletion remains a separate decision
│
├── D2.2b. Core Validation Docs/API Example Canonicalization
│   ├── Source evidence:
│   │   `backend-core-validation-docs-api-canonicalization-2026-05-21.md`
│   ├── State: implementation-complete
│   ├── Role: Move `docs/api/` examples to canonical `app.core.validation`
│   ├── Current fact: `docs/api/` legacy `validation_messages` references are
│   │                 `0`; no backend source, tests, OpenSpec, or wrapper files
│   │                 changed
│   └── Next gate: D2.2c wrapper-retirement decision or explicit long-term
│                  retention of `app.core.validation_messages`
│
├── D2.2c. Core Validation Wrapper Retirement / Retention Decision Package
│   ├── Source evidence:
│   │   `backend-core-validation-wrapper-retirement-decision-package-2026-05-21.md`
│   ├── State: closed-decision-package
│   ├── Role: Present wrapper-retirement vs long-term-retention options
│   ├── Current fact: active source imports and `docs/api/` legacy references are
│   │                 `0`; compatibility tests and historical/governance records
│   │                 still intentionally mention the wrapper path
│   └── Next gate: D2.2 is formally closed; wrapper deletion remains locked
│                  unless a separate D2.2d implementation batch is explicitly
│                  approved
│
├── D2.3. Trading Route/OpenAPI Governance Planning Package
│   ├── Source evidence:
│   │   `backend-trading-route-openapi-governance-planning-package-2026-05-21.md`
│   ├── State: decision-package-reviewed-accepted
│   ├── Role: Fold trading route ownership into unified route/OpenAPI governance
│   ├── Current fact: current smoke at HEAD `c24f43016` reports routes=`548`,
│   │                 OpenAPI paths=`500`, trading candidate routes=`41`
│   │                 (`40` trading-route candidates plus `1` unclassified
│   │                 trading-adjacent route),
│   │                 trading schema-exposed routes=`41`, trading schema paths=`35`,
│   │                 duplicate trading operationIds=`0`, and `/metrics` as the
│   │                 only duplicate runtime path/method; review verdict is
│   │                 `APPROVE`, with module-count traceability note absorbed
│   └── Next gate: If a later child lane is requested, create a separate
│                  approved plan with owner, write scope, tests, and rollback;
│                  no route mutation, OpenAPI schema/exposure change, docs/API
│                  edit, implementation issue, PM2 action, source edit, or test
│                  edit is authorized by this package alone
│
├── D2.4. Backup Route Ownership Planning Package
│   ├── Source evidence:
│   │   `backend-backup-route-ownership-planning-package-2026-05-21.md`
│   │   and
│   │   `backend-backup-route-ownership-decision-package-2026-05-22.md`
│   │   and
│   │   `backend-backup-route-ownership-decision-package-2026-05-22-review.md`
│   ├── State: decision-package-reviewed-accepted
│   ├── Role: Keep backup routes as a dedicated ownership proposal candidate
│   │         with explicit safety, security, consumer, OpenAPI, and rollback
│   │         evidence before backup route mutation
│   ├── Current fact: current evidence at HEAD `e6d576ccc` reports
│   │                 routes=`548`, OpenAPI paths=`500`, backup candidate
│   │                 routes=`13`, backup schema-exposed routes=`13`, backup
│   │                 OpenAPI operations=`13`, duplicate backup operationIds=`0`,
│   │                 seven ownership classes, and `cleanup_old_backups.py`
│   │                 owning both cleanup and backup-service health routes;
│   │                 review verdict is `APPROVE` with no issues found
│   └── Next gate: If a later backup route implementation lane is requested,
│                  create a separate approved packet with owner, exact write
│                  scope, tests, and rollback; no backup route, module, OpenAPI,
│                  docs/API, infrastructure, PM2, source, generated client, test
│                  mutation, or implementation issue is authorized by this
│                  package alone
│
├── D2.5. Control-Plane OpenAPI Docs Planning Package
│   ├── Source evidence:
│   │   `backend-control-plane-openapi-docs-planning-package-2026-05-21.md`
│   │   and
│   │   `backend-control-plane-openapi-docs-decision-package-2026-05-22.md`
│   │   and
│   │   `backend-control-plane-openapi-docs-decision-package-2026-05-22-review.md`
│   ├── State: decision-package-reviewed-accepted
│   ├── Role: Stabilize control-plane OpenAPI docs taxonomy, schema exposure,
│   │         runtime-only compatibility, and probe evidence before docs/API or
│   │         route mutation
│   ├── Current fact: current evidence at HEAD `15db8ebf5` reports
│   │                 routes=`548`, schema-visible routes=`536`, hidden runtime
│   │                 routes=`12`, OpenAPI paths=`500`, operations=`536`,
│   │                 schemas=`301`, broad control/status candidate routes=`144`,
│   │                 hidden focused docs/schema/control routes present,
│   │                 `/health/readiness` absent, duplicate focused
│   │                 operationIds=`0`, OpenAPI warnings=`0`, and `/metrics` as
│   │                 the control-plane duplicate runtime path/method to document;
│   │                 review verdict is `APPROVE` with no issues found
│   └── Next gate: If a later docs/API implementation lane is requested, create
│                  a separate approved packet with owner, target files, wording,
│                  checks, and rollback; no docs/API, route, OpenAPI
│                  schema/exposure, probe, PM2, source, generated client, test
│                  mutation, or implementation issue is authorized by this
│                  package alone
│
├── D2.6. PM2 Stateful Gate Approval Governance Package
│   ├── Source evidence:
│   │   `backend-pm2-stateful-gate-approval-governance-2026-05-21.md`,
│   │   `backend-pm2-stateful-gate-approval-decision-package-2026-05-22.md`,
│   │   `backend-pm2-stateful-gate-approval-decision-package-2026-05-22-review.md`
│   ├── State: decision-package-reviewed-accepted
│   ├── Role: Define approval strategy and required approval record fields for
│   │         future stateful PM2 gates, named equivalents, and read-only
│   │         sampling before any PM2 command is executed
│   ├── Current fact: health/status task `4.7` is already closed by
│   │                 `backend-health-status-pm2-gate-2026-05-18.md`;
│   │                 `run_pm2_integration_workflow.sh` remains stateful because
│   │                 it can run `pm2 stop all` and `pm2 delete all`; no PM2
│   │                 command was executed by D2.6; current HEAD `b35d016f8`
│   │                 confirms issue `#92` remains `OPEN` with
│   │                 `ready-for-human` and `ready-for-downstream`, and no
│   │                 `ready-for-agent`; review verdict is `APPROVE`, with the
│   │                 task-card suggestion satisfied by PR `#127`
│   └── Next gate: Closed as reviewed evidence; any future PM2 run still
│                  requires a narrow approval issue, issue comment, or approved
│                  runbook with command mode, service impact, rollback/restore,
│                  evidence destination, timeout, stop rule, and acceptance
│                  owner
│
├── D2 Closeout. Downstream Decision Rollup
│   ├── Source evidence:
│   │   `backend-openspec-issue92-downstream-rollup-closeout-2026-05-21.md`,
│   │   `backend-openspec-issue92-downstream-final-closeout-2026-05-22.md`,
│   │   `backend-openspec-issue92-downstream-final-closeout-2026-05-22-review-waiver.md`,
│   │   `backend-openspec-issue92-archive-readiness-2026-05-22.md`,
│   │   `backend-openspec-issue92-archive-readiness-2026-05-22-review.md`
│   ├── State: final-closeout-review-waived-for-archive-gate; archive-readiness-reviewed-accepted
│   ├── Role: Summarize D2.1-D2.6 as a complete downstream decision package
│   ├── Current fact: PRs `#96`-`#128` are merged; issue `#92` remains `OPEN`
│   │                 with `ready-for-human` and `ready-for-downstream`, but no
│   │                 `ready-for-agent`; D2.1a is closed end-to-end; D2.2 is
│   │                 closed as a decision lane; D2.3, D2.4, D2.5, and D2.6 are
│   │                 reviewed and accepted as governance/evidence packages
│   └── Next gate: Create a separate archive PR for the approved candidate
│                  changes, keep `#92` open as the parent index unless a human
│                  explicitly closes or relabels it, and continue to block all
│                  implementation work from this rollup
│
├── D2 Archive. Completed OpenSpec Changes
│   ├── Source evidence:
│   │   `backend-openspec-issue92-archive-execution-2026-05-22.md`,
│   │   `.planning/codebase/generated/issue92-openspec-archive-2026-05-22.json`
│   ├── State: archive-executed-prepared-for-pr-review
│   ├── Role: Move completed issue `#92` OpenSpec changes into archive and
│   │         apply their deltas to canonical specs
│   ├── Current fact: Five changes archived:
│   │                 `inject-technical-pattern-detection-service-di`,
│   │                 `refresh-backend-route-openapi-governance`,
│   │                 `define-backend-backup-route-ownership`,
│   │                 `stabilize-backend-control-plane-openapi-docs`, and
│   │                 `approve-backend-pm2-stateful-gate`; post-archive
│   │                 validation reports specs `32 passed, 0 failed` and
│   │                 changes `28 passed, 0 failed`; issue `#92` remains a
│   │                 parent decision issue and no implementation is authorized
│   └── Next gate: PR review / merge decision; after merge, comment archive
│                  result to issue `#92` and keep any future implementation in
│                  a separate approved child lane
│
├── D2 Parent Disposition. Issue `#92`
│   ├── Source evidence:
│   │   `backend-openspec-issue92-parent-disposition-2026-05-22.md`,
│   │   `.planning/codebase/generated/issue92-parent-disposition-2026-05-22.json`
│   ├── State: parent-index-retained
│   ├── Role: Keep issue `#92` as the parent downstream decision audit trail
│   │         after D2 final closeout, review waiver, archive readiness, and
│   │         OpenSpec archive have merged
│   ├── Current fact: issue `#92` remains `OPEN` with `enhancement`,
│   │                 `ready-for-human`, and `ready-for-downstream`; the
│   │                 `ready-for-agent` label remains absent; future
│   │                 implementation requires a new approved child lane with
│   │                 owner, exact write scope, current-head evidence,
│   │                 verification gates, rollback plan, and issue routing
│   └── Next gate: Human decision only if `#92` should be explicitly closed or
│                  relabelled; otherwise keep it open as parent context
│
├── G1. Adapter Lifecycle DI Triage And Reconciliation
│   ├── Source evidence:
│   │   `backend-next-child-lane-selection-2026-05-22.md`,
│   │   `.planning/codebase/generated/next-child-lane-selection-2026-05-22.json`,
│   │   `backend-adapter-lifecycle-di-triage-2026-05-22.md`,
│   │   `.planning/codebase/generated/adapter-lifecycle-di-triage-2026-05-22.json`,
│   │   `backend-adapter-lifecycle-di-disposition-2026-05-22.md`,
│   │   `.planning/codebase/generated/adapter-lifecycle-di-disposition-2026-05-22.json`,
│   │   `backend-adapter-lifecycle-di-closeout-acceptance-2026-05-22.md`,
│   │   `.planning/codebase/generated/adapter-lifecycle-di-closeout-acceptance-2026-05-22.json`
│   ├── State: closeout-acceptance-recorded
│   ├── Role: Reconcile and prepare issue `#78` adapter lifecycle DI
│   │         disposition without opening implementation authority
│   ├── Current fact: issue `#78` remains `OPEN` with `needs-triage`; issue
│   │                 `#79` remains `OPEN` with `needs-triage` and is still
│   │                 blocked by `#78`; five current adapter targets have
│   │                 provider/app-state/test evidence and no `_instance = None`;
│   │                 `realtime_mtm` has no current adapter file under
│   │                 `web/backend/app/adapters/`; five service/core files still
│   │                 require direct getter consumer classification before any
│   │                 future code migration; human maintainer accepted closing
│   │                 `#78` as reconciled governance evidence and routing
│   │                 remaining implementation concerns to separate approved
│   │                 child lanes
│   └── Next gate: After this closeout acceptance record merges, post the
│                  required issue `#78` closeout comment and close `#78`; then
│                  start issue `#79` service lifecycle DI design/triage only,
│                  without implementation authority or `ready-for-agent`
│                  movement
│
├── E. Candidate Branch: close-backend-schema-dual-directory
│   ├── Source evidence: backend-schema-dual-directory-closure-2026-05-19.md
│   ├── State: blocked
│   ├── Role: Migrate legacy app.schema consumers and decide shim retirement
│   └── Next gate: Prove canonical app.schemas exports and compatibility tests
│
├── F. Candidate Governance Track: refresh-backend-route-openapi-governance
│   ├── Source evidence: backend-api-flat-package-closure-records-2026-05-19.md;
│   │                 backend-route-openapi-probe-refresh-2026-05-20.md;
│   │                 backend-trading-route-openapi-governance-planning-package-2026-05-21.md
│   ├── State: decision-package-reviewed-accepted
│   ├── Role: Classify route table, OpenAPI, operationId, probe consumer,
│   │         trading ownership, control-plane, backup, compatibility-route,
│   │         and schema-exposure evidence before route mutation
│   └── Next gate: If a later child lane is requested, create a separate
│                  approved plan with owner, write scope, tests, and rollback;
│                  no backend source, route, OpenAPI, probe, docs/API, or test
│                  mutation is authorized by this package alone
│
├── G. Candidate Branch: define-backend-service-seams-and-singleton-pilots
│   ├── Source evidence:
│   │   `backend-singleton-lifecycle-routing-matrix-2026-05-19.md`,
│   │   `backend-service-lifecycle-di-design-triage-2026-05-22.md`,
│   │   `.planning/codebase/generated/service-lifecycle-di-design-triage-2026-05-22.json`,
│   │   `backend-service-lifecycle-di-candidate-classification-2026-05-22.md`,
│   │   `.planning/codebase/generated/service-lifecycle-di-candidate-classification-2026-05-22.json`,
│   │   `backend-email-service-lifecycle-di-implementation-authorization-2026-05-22.md`,
│   │   `.planning/codebase/generated/email-service-lifecycle-di-implementation-authorization-2026-05-22.json`,
│   │   `backend-email-service-lifecycle-di-implementation-2026-05-22.md`,
│   │   `backend-email-service-lifecycle-di-closeout-2026-05-22.md`,
│   │   `CODEBASE-MAP-STEWARD-TREE-RETROSPECTIVE-2026-05-22.md`,
│   │   `backend-service-lifecycle-di-second-candidate-selection-2026-05-22.md`,
│   │   `.planning/codebase/generated/service-lifecycle-di-second-candidate-selection-2026-05-22.json`,
│   │   `backend-announcement-service-lifecycle-di-implementation-authorization-2026-05-22.md`,
│   │   `.planning/codebase/generated/announcement-service-lifecycle-di-implementation-authorization-2026-05-22.json`,
│   │   `backend-announcement-service-lifecycle-di-implementation-2026-05-22.md`,
│   │   `backend-announcement-service-lifecycle-di-closeout-2026-05-22.md`,
│   │   `backend-service-lifecycle-di-third-candidate-selection-2026-05-22.md`,
│   │   `.planning/codebase/generated/service-lifecycle-di-third-candidate-selection-2026-05-22.json`,
│   │   `backend-watchlist-service-lifecycle-di-implementation-authorization-2026-05-22.md`,
│   │   `.planning/codebase/generated/watchlist-service-lifecycle-di-implementation-authorization-2026-05-22.json`,
│   │   `backend-watchlist-service-lifecycle-di-implementation-2026-05-22.md`,
│   │   `backend-watchlist-service-lifecycle-di-closeout-2026-05-23.md`,
│   │   `backend-watchlist-helper-cleanup-next-lane-decision-2026-05-23.md`,
│   │   `.planning/codebase/generated/watchlist-helper-cleanup-next-lane-decision-2026-05-23.json`,
│   │   `backend-watchlist-helper-cleanup-implementation-authorization-2026-05-23.md`,
│   │   `.planning/codebase/generated/watchlist-helper-cleanup-implementation-authorization-2026-05-23.json`,
│   │   `backend-watchlist-helper-cleanup-implementation-2026-05-23.md`,
│   │   `backend-service-lifecycle-di-candidate-refresh-2026-05-23.md`,
│   │   `.planning/codebase/generated/service-lifecycle-di-candidate-refresh-2026-05-23.json`,
│   │   `backend-stock-search-service-lifecycle-di-implementation-authorization-2026-05-23.md`,
│   │   `.planning/codebase/generated/stock-search-service-lifecycle-di-implementation-authorization-2026-05-23.json`,
│   │   `backend-stock-search-service-lifecycle-di-implementation-2026-05-23.md`,
│   │   `backend-stock-search-service-lifecycle-di-closeout-2026-05-23.md`,
│   │   `.planning/codebase/generated/stock-search-service-lifecycle-di-closeout-2026-05-23.json`,
│   │   `backend-service-lifecycle-di-next-lane-after-stock-search-2026-05-23.md`,
│   │   `.planning/codebase/generated/service-lifecycle-di-next-lane-after-stock-search-2026-05-23.json`,
│   │   `backend-service-lifecycle-di-candidate-refresh-after-stock-search-2026-05-23.md`,
│   │   `.planning/codebase/generated/service-lifecycle-di-candidate-refresh-after-stock-search-2026-05-23.json`,
│   │   `backend-stock-search-compatibility-getter-consumer-matrix-2026-05-23.md`,
│   │   `.planning/codebase/generated/stock-search-compatibility-getter-consumer-matrix-2026-05-23.json`,
│   │   `backend-broad-service-seam-design-2026-05-23.md`,
│   │   `.planning/codebase/generated/broad-service-seam-design-2026-05-23.json`
│   ├── State: broad-service-seam-design-prepared-for-review
│   ├── Role: Track issue `#79` service lifecycle DI candidate classification,
│   │         authorization, and first implementation pilot while preventing
│   │         unapproved expansion to additional services
│   ├── Current fact: issue `#78` is `CLOSED`; issue `#79` remains `OPEN` with
│   │                 `needs-triage`; current-head service scan covers 152
│   │                 service files, with broad singleton/getter heuristic hits
│   │                 in 104 files but this is not a backlog; corrected
│   │                 module-level singleton-variable scan finds 21 files;
│   │                 `tradingview_widget_service.py` is reference evidence,
│   │                 `technical_pattern_detection_service.py` is completed
│   │                 pilot evidence, and `email_service.py` is selected as the
│   │                 recommended first future implementation candidate; PR
│   │                 `#140` review was accepted by the human maintainer, and
│   │                 G2.2 now records exact future write scope, six
│   │                 `notification.py` callers, GitNexus pre-edit gates, test
│   │                 plan, rollback plan, and forbidden scope for
│   │                 `email_notification_service.py`; PR `#142` was reviewed,
│   │                 all checks completed successfully, and merged at
│   │                 `20657e6e86a3423b15c67b6a8d6e165fbaa47b72`; PR `#143`
│   │                 recorded closeout at
│   │                 `68da82084266ca7f9b7be9f5b55da7ac5e64fbd7`; G2.4
│   │                 retrospective records steward-tree lessons and current-head
│   │                 second-candidate evidence recommends
│   │                 `announcement_service.py` as the next authorization
│   │                 candidate over `watchlist_service.py`; PR `#144` merged at
│   │                 `f149534f8dd01802cf40cbe266223c51e4475a49`; G2.5 now
│   │                 records a future implementation authorization packet for
│   │                 `announcement_service.py`, limited to the announcement
│   │                 service, announcement routes, focused tests, and an
│   │                 implementation report/task card; PR `#145` merged at
│   │                 `e9d674c01edc5e701a0b3eca80b05f62dfc4986f`; G2.6 now
│   │                 implements that approved scope by adding an app-state
│   │                 provider seam to `announcement_service.py` and injecting
│   │                 `AnnouncementService` into 11 announcement route handlers;
│   │                 PR `#146` was approved by the human maintainer and merged
│   │                 at `517f47cb86aa32d32514d8588a653b08898f72c7`; G2.7
│   │                 records the merged result and confirms the closeout
│   │                 boundary; PR `#147` merged at
│   │                 `112487d96ad07ad3212c71e729395f2c8accfed1`; G2.8
│   │                 selects a route-surface-only `watchlist_service.py`
│   │                 authorization candidate while keeping watchlist adapter and
│   │                 data-layer helper calls as compatibility surfaces; PR
│   │                 `#148` merged at
│   │                 `ccc4982cd11b47996c6534f087b0c9cb3783877a`; G2.9 now
│   │                 records the route-surface-only implementation
│   │                 authorization packet for `watchlist_service.py`, limited to
│   │                 the service file, seven `watchlist.py` route handlers,
│   │                 focused tests, an implementation report, and a future task
│   │                 card while keeping adapter/data helper callers out of scope;
│   │                 PR `#149` merged at
│   │                 `bddb764c79355e6c0c366fdd9a28d64a685700bf`; G2.10 now
│   │                 implements that approved route-surface scope by adding an
│   │                 app-state provider seam to `watchlist_service.py` and
│   │                 injecting `WatchlistService` into seven `watchlist.py`
│   │                 group route handlers while preserving adapter/data helper
│   │                 compatibility callers; PR `#150` was approved by the human
│   │                 maintainer and merged at
│   │                 `b14ef8421d8ccd6dfd4a714b2a17d4e1ae971419`; G2.11 records
│   │                 the merged result and confirms the closeout boundary; PR
│   │                 `#151` merged at
│   │                 `3caeea24dafb02748c92d58b2809e893ce761d5e`; G2.12 now
│   │                 selects an adapter-aware watchlist helper cleanup
│   │                 authorization packet as the next lane instead of selecting
│   │                 a fourth route-surface service candidate immediately; PR
│   │                 `#152` merged at
│   │                 `0ccf1fc58d531cba8f64cc1031d53875e636a766`; G2.13 now
│   │                 records the future adapter-aware helper cleanup write scope,
│   │                 TDD gates, GitNexus gates, and rollback boundary; PR `#153`
│   │                 merged at
│   │                 `938682debb90a25392ca208e706d8388d06de786`; G2.14 now
│   │                 implements that scope by adding constructor-configured
│   │                 `watchlist_service_provider` seams to both watchlist adapter
│   │                 helper files while preserving default getter fallback and
│   │                 leaving route code unchanged; PR `#154` merged at
│   │                 `1dcb394a49a9d95e939b2119acc431b825954036`; G2.15 now
│   │                 records the closeout, current-head verification, and
│   │                 confirms no follow-up implementation is authorized; PR
│   │                 `#155` merged at
│   │                 `03c48f74d73f1de505470698966776f6624a0ec7`; G2.16
│   │                 selected current-head candidate refresh as the next service
│   │                 lifecycle DI governance lane, not source implementation; PR
│   │                 `#156` merged at
│   │                 `33e75acddf5c7c363a2e33ba4a3d01923b46edde`; G2.17 now
│   │                 refreshes the current-head service getter inventory and
│   │                 recommends only a future G2.18 `stock_search_service`
│   │                 authorization packet, with source edits still locked; PR
│   │                 `#157` merged at
│   │                 `0285d1cbc29b4622b3e39c9a171ba3b02691ed1b`; G2.18 now
│   │                 records the future `stock_search_service` route-surface DI
│   │                 write scope, six route-local getter callers, GitNexus
│   │                 pre-edit gates, TDD requirements, rollback plan, and
│   │                 forbidden scope; PR `#158` merged at
│   │                 `d63b18ab98417d9051dfbf177a975ac7470c96d3`; G2.19 now
│   │                 implements the approved route-surface DI scope by adding an
│   │                 app-state provider seam to `stock_search_service`, keeping
│   │                 `get_stock_search_service()` as compatibility fallback, and
│   │                 injecting `StockSearchService` into five stock-search route
│   │                 handlers plus the market `get_kline_data` fallback route;
│   │                 focused stock-search suite is green; PR `#159` was
│   │                 approved by the human maintainer and merged at
│   │                 `25db762ae6484ad4638baf0f8ab42b94a978a403`; G2.20 now
│   │                 records that merged result, preserves the compatibility
│   │                 getter boundary, and confirms no next service candidate is
│   │                 selected by this closeout; PR `#160` merged at
│   │                 `f8063b512fb7c3aabfabef9d80d05d1d682569b5`; G2.21 now
│   │                 selects a future G2.22 current-head candidate refresh
│   │                 before any further service DI source edit or
│   │                 compatibility getter cleanup; PR `#161` merged at
│   │                 `d2e799cd2c1cbeb00b70d5cf64897b7c8a8a3b11`; G2.22 now
│   │                 refreshes current-head service lifecycle candidates,
│   │                 records 152 service Python files, 42 broad heuristic hit
│   │                 files, 17 narrow candidate files, no direct next
│   │                 route-surface implementation candidate, and selects a
│   │                 future G2.23 stock-search compatibility getter cleanup
│   │                 authorization / consumer-matrix packet before any source
│   │                 edit; PR `#162` merged at
│   │                 `d186ce78ee0ad4017b36e3788a54533ce3a972df`; G2.23 now
│   │                 records the stock-search compatibility getter consumer
│   │                 matrix at current HEAD: two route files use only the
│   │                 dependency provider, route direct getter calls remain `0`,
│   │                 package exports and tests still intentionally cover
│   │                 `get_stock_search_service()`, and the getter is retained
│   │                 as active compatibility surface with no cleanup
│   │                 implementation authorized; PR `#163` merged at
│   │                 `18f5b43275bbd1fc7f53c739063da37c6a753b11`; G2.24 now
│   │                 records broad market/data/strategy service seam evidence at
│   │                 that HEAD, finds CRITICAL impact for
│   │                 `get_market_data_service_v2`, `get_data_service`,
│   │                 `get_strategy_service`, and `get_tdx_service`, records the
│   │                 `get_market_data_service` graph/text mismatch, rejects a
│   │                 mixed implementation batch, and selects a future G2.25
│   │                 market-data provider design packet before any source edit
│   └── Next gate: Human review of the G2.24 design packet; if accepted, create
│                  a separate G2.25 market-data provider design packet before
│                  any `market_data_service` or `market_data_service_v2`
│                  source edits
│
├── H. Decision-Only Track: CSRF composition root
│   ├── Source evidence: backend-csrf-composition-root-decision-2026-05-19.md
│   ├── State: decision-only
│   ├── Role: Record duplicate composition-policy boundary
│   └── Next gate: Do not extract shared CSRF module until test-factory exit criteria exist
│
├── I. Resolved Track: error-contract canonicalization
│   ├── Source evidence: backend-error-contract-completion-verification-2026-05-19.md
│   ├── State: evidence-complete
│   ├── Role: Keep #77 / P3-C5 resolved unless current HEAD contradicts it
│   └── Next gate: Historical-route follow-up only, not reopening the main migration
│
└── J. External Evidence Track: miniQMT
    ├── Source evidence: backend-external-evidence-alignment-2026-05-19.md
    ├── State: evidence-complete
    ├── Role: External evidence alignment only
    └── Next gate: Do not convert into backend blocker, promotion authority,
                   source cutover, or ClickHouse write approval
```

## Evidence Mapping

| Report | Steward branch | Current disposition | Next gate |
|---|---|---|---|
| `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` | A | Baseline input; several historical snapshots require current-head labels. `raise HTTPException=191` is superseded by current zero evidence. `F821=604` is stale; ad-hoc review at HEAD `6530c88f3` counted `F821 total=757`, `src=0`, `backend-api=163`, with no formal artifact yet. | Keep as baseline, but update only through linked evidence and freshness metadata |
| `backend-openspec-issue83-runtime-triage-2026-05-19.md` | C | Superseded for current runtime state by Task 2.x implementation evidence; remains useful as pre-fix triage history | Keep as historical input only |
| `backend-sequence-unblocks-preimplementation-evidence-2026-05-20.md` | C | Task 1.x pre-implementation evidence complete at HEAD `7b097fffd`; superseded for runtime state by Task 2.x, but still records schema consumer and singleton freshness inputs | Use for schema and singleton follow-up context |
| `backend-sequence-runtime-unblock-implementation-2026-05-20.md` | C | Task 2.x runtime unblock complete: `app.main` imports with routes=`548`; `test_health_route_conflicts.py` `112 passed`; OpenAPI paths=`500`, duplicate operationIds=`0` | Proceed to schema shim closure and runtime route/OpenAPI evidence refresh |
| `backend-schema-shim-closure-implementation-2026-05-20.md` | E | Schema shim closure complete: 0 legacy `app.schema` consumers remain; canonical `app.schemas` exports are available; `test_validation_models.py` passed | Proceed to route/OpenAPI evidence refresh and decide shim retirement later |
| `backend-route-openapi-probe-refresh-2026-05-20.md` | F | Current route/OpenAPI/probe evidence captured: routes=`548`, OpenAPI paths=`500`, duplicate operationIds=`0`, probe hit files=`188`; one runtime duplicate path/method exists for `GET /metrics` | Classify `/metrics` under control-plane endpoint governance before any endpoint retirement or exposure change |
| `backend-route-openapi-probe-refresh-2026-05-20-review.md` | F | Review verified artifact numbers and `/metrics` taxonomy; requested clearer OpenSpec directory, endpoint module count, and `strategy_compat` mapping | Absorbed into the route/OpenAPI/probe report |
| `backend-service-seam-proposal-path-2026-05-20.md` | G | Service seam lane is proposal-only: current heuristic inventory has no implementation-ready clean pilot, and service directory is dirty | Create a separate OpenSpec proposal only after human approval and a clean candidate packet |
| `backend-service-seam-proposal-path-2026-05-20-review.md` | G | Review verified inventory numbers and routing strategy; requested OpenSpec directory clarification, corrected `separate_design_gate` examples, and scan-count comparability note | Absorbed into the service seam proposal-path report |
| `backend-sequence-unblocks-commit-readiness-2026-05-20.md` | C, E, F, G | Path-limited commit readiness recorded: current worktree has `1493` dirty entries, this line has `35` relevant entries, and review-input files remain optional | Human commit decision: two-commit split, single explicit-path commit, or further review |
| `backend-sequence-unblocks-commit-blocked-2026-05-20.md` | C, E, F, G | Single explicit-path commit attempt was blocked by `Backend Singleton None Guard` and then `UnifiedResponse Contract Guard`; no commit was created | Split or narrow the staged set, or open a separate approved route-contract implementation lane |
| `backend-sequence-runtime-unblock-clean-worktree-2026-05-20.md` | C | Isolated source worktree restores runtime import chain: `app.main` routes=`548`; `test_health_route_conflicts.py` `112 passed`; source commit remains blocked by `UnifiedResponse Contract Guard` with `27` errors across `4` route files | Open a separate route-contract OpenSpec lane before committing the source unblock |
| `backend-route-unified-response-contract-implementation-2026-05-20.md` | C, D | Dedicated route-contract implementation complete in isolated worktree: `27` UnifiedResponse guard errors reduced to `0`; previous singleton-none commit blocker also rechecked at `0` errors for changed backend API files | Approved with notes; next gate is deciding whether to push or merge commit `00101699b` |
| `backend-core-split-governance-reconciliation-2026-05-19.md` | D | Core Batch 2 remains blocked | Resolve Task 3.2 disposition and #83 evidence gate before Batch 2 |
| `backend-schema-dual-directory-closure-2026-05-19.md` | E | Schema closure is viable but not direct deletion | Prove `app.schemas` canonical exports and targeted compatibility tests |
| `backend-api-flat-package-closure-records-2026-05-19.md` | F | Closure criteria recorded; runtime diff blocked | Fix runtime import chain, then refresh route/OpenAPI evidence |
| `backend-singleton-lifecycle-routing-matrix-2026-05-19.md` | G | 111 singleton candidates, 0 low-risk pilot | Classify services, design interface/test-double strategy, then create a separate proposal |
| `backend-csrf-composition-root-decision-2026-05-19.md` | H | Decision-only; duplicate composition policy acknowledged | Define test-factory exit criteria before any implementation branch |
| `backend-external-evidence-alignment-2026-05-19.md` | J | External evidence only | Keep non-backend-blocking unless future approved plan changes that boundary |
| `codebase-map-freshness-2026-05-19.md` | A, B, C | Freshness rule established | Every future evidence entry records current-head, commit-scoped, or stale-aware status |
| `backend-error-contract-completion-verification-2026-05-19.md` | I | P3-C5 / #77 main migration resolved | Do not reopen old live-count backlog without current-head contradiction |
| `backend-technical-pattern-di-pilot-implementation-2026-05-21.md` | D2.1a.1 | First DI lifecycle pilot implementation merged in PR `#112`; route-level provider and dependency override test seam are in place | D2.1a implementation closed; do not infer a second DI pilot from this evidence |
| `inject-technical-pattern-detection-service-di` task `5.3` closeout | D2.1a.1 | Final OpenSpec checklist governance merged in PR `#113`; issue `#92` received implementation and final governance closeout comments | D2.1a is 100% closed; future DI work requires a new approved child lane |

| G2.1-G2.11 service lifecycle DI early lanes | G | Folded evidence mapping for the first service lifecycle sequence: G2.1 candidate classification, G2.2 email authorization, G2.3 email implementation, G2.4 steward-tree retrospective, G2.5 announcement authorization, G2.6 announcement implementation, G2.7 announcement closeout, G2.8 watchlist selection, G2.9 watchlist authorization, G2.10 watchlist implementation, and G2.11 watchlist closeout. Detailed per-step records remain in the Completed And Reviewed Ledger and G branch source-evidence list. | Superseded by G2.12 adapter-aware watchlist helper cleanup decision packet |
| `backend-watchlist-helper-cleanup-next-lane-decision-2026-05-23.md` | G | G2.12 decision packet merged: adapter-aware watchlist helper cleanup selected as the next authorization candidate; no source edits or OpenSpec changes were authorized | Superseded by G2.13 authorization packet for future implementation scope |
| `backend-watchlist-helper-cleanup-implementation-authorization-2026-05-23.md` | G | G2.13 implementation authorization packet merged: future write scope, tests, GitNexus gates, and rollback plan defined for adapter-aware watchlist helper cleanup | Superseded by G2.14 implementation evidence |
| `backend-watchlist-helper-cleanup-implementation-2026-05-23.md` | G | G2.14 implementation merged by PR `#154`: both watchlist adapter/helper files now accept constructor-configured provider seams; route code unchanged | Superseded by G2.15 closeout packet |
| `backend-watchlist-helper-cleanup-closeout-2026-05-23.md` | G | G2.15 closeout merged by PR `#155` at `03c48f74d73f1de505470698966776f6624a0ec7`: PR `#154` merge recorded, current-head verification rerun, and no follow-up implementation authorized | Superseded by G2.16 next-lane decision packet |
| `backend-service-lifecycle-di-next-lane-decision-2026-05-23.md` | G | G2.16 decision merged by PR `#156` at `33e75acddf5c7c363a2e33ba4a3d01923b46edde`: select G2.17 current-head candidate refresh before any further service lifecycle DI source edits | Superseded by G2.17 candidate refresh packet |
| `backend-service-lifecycle-di-candidate-refresh-2026-05-23.md` | G | G2.17 current-head refresh merged by PR `#157` at `0285d1cbc29b4622b3e39c9a171ba3b02691ed1b`: scanned 152 service Python files, identified 15 service getter files and 11 route-surface related getter files, recorded GitNexus risk, and recommends only a future G2.18 `stock_search_service` authorization packet | Superseded by G2.18 authorization packet |
| `backend-stock-search-service-lifecycle-di-implementation-authorization-2026-05-23.md` | G | G2.18 authorization merged by PR `#158` at `d63b18ab98417d9051dfbf177a975ac7470c96d3`: future write scope limited to `stock_search_service`, five stock-search route handlers, market `get_kline_data`, focused tests, implementation report, and task card | Superseded by G2.19 implementation evidence |
| `backend-stock-search-service-lifecycle-di-implementation-2026-05-23.md` | G | G2.19 implementation merged by PR `#159` at `25db762ae6484ad4638baf0f8ab42b94a978a403`: app-state provider seam added, compatibility getter preserved, six route-local stock-search service consumers injected, and focused stock-search tests passed | Superseded by G2.20 closeout packet |
| `backend-stock-search-service-lifecycle-di-closeout-2026-05-23.md` | G | G2.20 closeout merged by PR `#160` at `f8063b512fb7c3aabfabef9d80d05d1d682569b5`: PR `#159` merge recorded, post-merge route-surface scan shows `0` direct getter calls in the approved route files, and no follow-up implementation or next service candidate is authorized | Superseded by G2.21 next-lane decision packet |
| `backend-service-lifecycle-di-next-lane-after-stock-search-2026-05-23.md` | G | G2.21 decision merged by PR `#161` at `d2e799cd2c1cbeb00b70d5cf64897b7c8a8a3b11`: select G2.22 current-head candidate refresh before implementation or compatibility-getter cleanup | Superseded by G2.22 candidate refresh packet |
| `backend-service-lifecycle-di-candidate-refresh-after-stock-search-2026-05-23.md` | G | G2.22 current-head refresh merged by PR `#162` at `d186ce78ee0ad4017b36e3788a54533ce3a972df`: scanned 152 service Python files, recorded 42 broad heuristic hit files and 17 narrow service-lifecycle candidate files, found no safe direct next route-surface implementation candidate, and selected future G2.23 `stock_search_service` compatibility getter cleanup authorization / consumer-matrix packet | Superseded by G2.23 consumer matrix |
| `backend-stock-search-compatibility-getter-consumer-matrix-2026-05-23.md` | G | G2.23 consumer matrix prepared at `d186ce78ee0a`: route direct `get_stock_search_service()` calls remain `0`, route provider refs are `8`, package exports/tests still intentionally cover the compatibility getter, and cleanup implementation is not authorized | Human review; if accepted, retain the getter and create a separate broad market/data/strategy service seam design packet before source edits |
| `backend-broad-service-seam-design-2026-05-23.md` | G | G2.24 design packet prepared at `18f5b43275bb`: broad market/data/strategy seams are split into separate future design lanes; market/data/strategy/tdx representative getters show CRITICAL impact except `get_market_data_service`, which has a graph/text mismatch; no source implementation is authorized | Human review; if accepted, create G2.25 market-data provider design packet before any market data service source edits |

## Completed And Reviewed Ledger

This ledger is updated after each completed step before moving to the next step.
“Reviewed” here means the current thread accepted the result based on recorded
evidence and governance gates. It does not replace a future path-limited commit
review, PR review, or OpenSpec archive review.

| Completed step | Steward branch | Completed capability | Review status | Evidence | Next step unlocked |
|---|---|---|---|---|---|
| `sequence-backend-architecture-unblocks` Task 1.x | C | Pre-implementation evidence captured for runtime blocker, schema consumers, and singleton freshness | Reviewed as historical/pre-fix input | `docs/reports/quality/backend-sequence-unblocks-preimplementation-evidence-2026-05-20.md` | Task 2.x runtime unblock |
| `sequence-backend-architecture-unblocks` Task 2.x | C | Runtime import chain restored; `app.main` imports; health route governance suite passes; OpenAPI smoke produces stable snapshot | Reviewed/pass in current thread: GitNexus impact LOW, intended-file ruff passed, `app.main` routes=`548`, `test_health_route_conflicts.py` `112 passed`, OpenSpec strict valid, markdown governance `0` errors, path-limited `git diff --check` passed | `docs/reports/quality/backend-sequence-runtime-unblock-implementation-2026-05-20.md`; `openspec/changes/sequence-backend-architecture-unblocks/tasks.md` | Task 3.x schema shim closure and Task 5.x route/OpenAPI refresh |
| `sequence-backend-architecture-unblocks` Task 8.8 | C | Clean worktree source unblock replay completed after governance-only commit | Reviewed/pass in current thread: import smoke routes=`548`; collection smoke `112 tests collected`; full health route suite `112 passed`; F821 current import-chain blockers removed, leaving 25 historical data/risk F821 outside this lane | `docs/reports/quality/backend-sequence-runtime-unblock-clean-worktree-2026-05-20.md` | Dedicated UnifiedResponse route-contract lane |
| Governance packet commit `9addc2458` | C, D | Path-limited governance docs captured the clean worktree replay, restored `sequence-backend-architecture-unblocks` proposal artifacts, and created the dedicated route-contract proposal | Reviewed/pass in current thread: staged files=`9`, source staged=`0`, markdown governance errors=`0`, both affected OpenSpec changes strict-valid, cached diff check passed, GitNexus staged risk=`low` | `9addc2458`; `canonicalize-backend-route-unified-response-contracts` proposal/tasks/spec; steward tree update | Human review of the route-contract proposal before implementation |
| `canonicalize-backend-route-unified-response-contracts` implementation | C, D | Four target route modules now declare canonical `UnifiedResponse[...]` contracts and direct model/list/dict success payloads are wrapped under `data`; post-review pre-push check reconciled dirty-worktree drift for the already committed `app.api.auth.get_current_active_user` compatibility export | `APPROVE_WITH_NOTES`: GitNexus impact LOW for four target files; guard baseline `27` errors now `0`; ruff issues `0`; `app.main` routes=`548`; health route suite `112 passed`; OpenAPI paths=`500`, operations=`536`, duplicate operationIds=`0`; singleton-none guard `0` errors. Follow-up auth export smoke confirms `get_current_active_user=True`; health route suite re-run `112 passed`. Notes recorded for `data_source_config.py` response-module runtime dependency mix, `monitoring_watchlists.py` module-level fallback state, and wide commit scope. | `00101699b`; pre-push drift check in current report; `docs/reports/quality/backend-route-unified-response-contract-implementation-2026-05-20.md`; `openspec/changes/canonicalize-backend-route-unified-response-contracts/tasks.md` | Push/merge isolated branch; track non-blocking notes as future candidates |
| PR `#85` publication for `sequence-route-contract-unblock` | C, D | Route-contract implementation branch published for review against `wip/root-dirty-20260403` | Clean detached worktree at `97af858e4`: `git status --short` empty; UnifiedResponse guard `errors=0`, `checked_routes=27`; singleton-none guard `errors=0`, `checked_files=18`; ruff `issues=0`; health route suite `112 passed`; OpenAPI paths=`500`, operations=`536`, duplicate operationIds=`0`; both affected OpenSpec changes strict-valid | `https://github.com/chengjon/mystocks/pull/85`; `97af858e4`; Graphiti episode `9836f180-20a4-4608-ae84-b8f8290e1034` | Human PR review / merge decision |
| PR `#85` base reconciliation | C, D, E | PR branch replayed `origin/wip/root-dirty-20260403` to clear GitHub `CONFLICTING` state while preserving route-contract behavior and newer base artifacts | Conflict files resolved; unmerged files=`0`; UnifiedResponse guard `errors=0`, `checked_routes=27`; singleton-none guard `errors=0`, `checked_files=9`; ruff `issues=0`; health route suite `112 passed`; OpenAPI paths=`500`, operations=`536`, duplicate operationIds=`0`; affected OpenSpec changes strict-valid; markdown governance and cached diff check passed; GitHub reports `mergeable=MERGEABLE` | `ce9c0c20f`; Graphiti episode `7c7d8dab-8db9-496d-858d-69c2a7b47b58` | Human PR review / merge decision |
| PR `#85` CI gate unblock | C, D, E | GitHub check failures triaged: mainline governance lacked `pr-85.yaml`, API contract OpenAPI generation lacked required `TDENGINE_*` env vars, backend logging imported undeclared `loguru`, CI exposed undeclared/unstable CPU ML plus `akshare`/`baostock` imports on the OpenAPI import path, and the documentation gate needed to respect hidden runtime-only routes plus OpenAPI 3.1 metadata-only Any schemas | Local precheck: YAML parsed for task card and workflow; CI-style OpenAPI generation passed with TDengine/PostgreSQL stub env; optional-ML fallback regression test now covers `cuml`/`sklearn` absence for anomaly dataclasses; API documentation validation passed `16/16`; health+documentation workflow command passed `128/128`; success example audit reports `JSON_SUCCESS_MISSING_EXAMPLES 0`; collector reports total/documented `536/536` and schema issues `0`; path diff check passed | `.github/workflows/api-contract-validation.yml`; `governance/mainline/task-cards/pr-85.yaml`; `web/backend/requirements.txt`; `src/advanced_analysis/anomaly/dataclasses.py`; `src/advanced_analysis/capital_flow_analyzer/_capital_flow_cluster_mixin.py`; `web/backend/app/api/gpu_monitoring.py`; `web/backend/tests/test_api_documentation_validation.py`; `tests/unit/advanced_analysis/test_anomaly_optional_ml_imports.py` | Resolve GitHub `Generate TypeScript Types` gate exposed by stricter generated frontend contracts |
| PR `#85` frontend generated type compatibility | D, E | The `Generate TypeScript Types` CI job surfaced frontend consumers that still relied on widened local assumptions after OpenAPI type regeneration; fixes stay limited to type compatibility and view-model adapters, not new UI behavior | Reviewed/pass in current thread: CI failure log identified five concrete TypeScript surfaces; GitNexus impact was LOW for the four frontend source files before edit; local Node 20 `vue-tsc --noEmit` passed; targeted frontend ESLint passed; PR task card now includes the exact frontend paths and a `frontend-generated-type-check` acceptance gate; GitHub PR head `40f33ffc` reached `MERGEABLE` / `CLEAN` with `Generate TypeScript Types` success | `web/frontend/src/views/IndicatorLibrary.vue`; `web/frontend/src/views/artdeco-pages/composables/useArtDecoTradingManagement.ts`; `web/frontend/src/views/artdeco-pages/portfolio-tabs/portfolioOverviewData.ts`; `web/frontend/src/views/trade/composables/useTradeReconciliation.ts`; `governance/mainline/task-cards/pr-85.yaml`; `https://github.com/chengjon/mystocks/pull/85` | Recheck CI after this steward-tree status update, then merge PR `#85` if still `CLEAN` |
| `sequence-backend-architecture-unblocks` Task 3.x | E | Schema validation models now live under canonical `app.schemas`; legacy `app.schema` remains a thin compatibility shim; direct legacy consumers are migrated | Reviewed/pass in current thread: GitNexus file impact LOW, schema ruff passed, `test_validation_models.py` `60 passed`, import smoke confirms `app.schemas`, `app.schemas.validation_models`, `app.schema`, and `app.schema.validation_models`; fresh scan reports `LEGACY_CONSUMERS=0` | `docs/reports/quality/backend-schema-shim-closure-implementation-2026-05-20.md`; `openspec/changes/sequence-backend-architecture-unblocks/tasks.md` | Task 4.x codebase-map consistency and Task 5.x route/OpenAPI evidence refresh |
| `sequence-backend-architecture-unblocks` Task 4.x | A, B, I | Codebase map and master execution plan no longer treat stale HTTPException counts or schema dual-directory status as current truth | Reviewed/pass in current thread: GH #77 currently `CLOSED`; current working-tree scan at HEAD `7b097fffd` reports fixed-field error-contract buckets all `0`; Evidence Artifact Index now distinguishes stale historical artifacts, current-head runtime/schema evidence, and commit-scoped evidence | `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md`; `docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md`; `openspec/changes/sequence-backend-architecture-unblocks/tasks.md` | Task 5.x route/OpenAPI evidence refresh |
| `sequence-backend-architecture-unblocks` Task 5.x | F | Current route table, OpenAPI snapshot, and probe consumer matrix regenerated after runtime import chain became healthy | Reviewed/pass in current thread: artifacts generated at HEAD `7b097fffd`; route table routes=`548`; OpenAPI paths=`500`, operations=`536`, duplicate operationIds=`0`, warnings=`0`; probe matrix scanned files=`5782`, hit files=`188`; duplicate runtime path/method limited to `GET /metrics` hidden+visible control-plane routes | `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20.md`; `.planning/codebase/generated/backend-route-table-2026-05-20.json`; `.planning/codebase/generated/route-openapi-snapshot-2026-05-20.json`; `.planning/codebase/generated/probe-consumer-matrix-2026-05-20.json` | Task 6.x singleton/service seam proposal path and route governance classification |
| `sequence-backend-architecture-unblocks` Task 6.x | G | Service singleton/lifecycle seam work remains proposal-only; current inventory classifies candidates but schedules no implementation batch | Reviewed/pass in current thread: service inventory artifact generated at HEAD `7b097fffd`; service directory dirty count `18`; heuristic buckets external-client wrapper `69`, DB/session-backed `24`, cache/task-running `17`, interface/test-double candidate needing review `28`, separate design gate `2`; no service code edited | `docs/reports/quality/backend-service-seam-proposal-path-2026-05-20.md`; `.planning/codebase/generated/service-singleton-inventory-2026-05-20.json` | Task 7.x verification and Task 8.x closure |
| `sequence-backend-architecture-unblocks` Task 7.x | C, E, F, G | Governance and targeted technical verification completed for the sequence branch artifacts | Reviewed/pass in current thread: path-limited `git diff --check` no output; generated JSON parse OK; added-file whitespace problems `0`; markdown governance `checked_files=10`, `errors=0`; OpenSpec strict valid; schema ruff passed; `test_validation_models.py` `60 passed` | `openspec/changes/sequence-backend-architecture-unblocks/tasks.md`; validation command outputs from current thread | Task 8.x closure |
| `sequence-backend-architecture-unblocks` Task 8.x | C, E, F, G | Runtime unblock, schema shim decision, route/OpenAPI/probe refresh, and service seam proposal split are recorded; broad implementation remains gated | Reviewed/pass in current thread: tasks.md now records 1.x through 8.x complete; no endpoint retirement, service migration, broad refactor, or OpenSpec archive performed | reports and artifacts listed above | Human review, path-limited commit decision, then OpenSpec archive decision if accepted |
| `sequence-backend-architecture-unblocks` Task 8.5 | F, G | Paired reviews for the Task 5.x and Task 6.x reports were evaluated and absorbed where technically correct | Reviewed/pass in current thread: OpenSpec directory exists in current worktree and is now named explicitly; route report explains `endpoint_modules=98` and `category_counts.strategy_compat`; service report corrects `separate_design_gate` to `StockSearchService` and `TechnicalPatternDetectionService` and explains `111` versus `140` scan-method difference | `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20-review.md`; `docs/reports/quality/backend-service-seam-proposal-path-2026-05-20-review.md`; updated target reports | Re-run markdown/OpenSpec validation, then human review / commit decision |
| `sequence-backend-architecture-unblocks` Task 8.6 | C, E, F, G | Path-limited commit readiness recorded without staging or committing | Reviewed/pass in current thread: commit boundary report separates runtime/schema source paths, governance/evidence paths, optional review-input files, and unrelated dirty worktree entries; no broad `git add` performed | `docs/reports/quality/backend-sequence-unblocks-commit-readiness-2026-05-20.md` | Human commit choice before any OpenSpec archive |
| PR `#85` merge | C, D | Route-contract implementation, CI stabilization, frontend generated-type compatibility fixes, and steward-tree review record were merged into `wip/root-dirty-20260403` | Reviewed/pass in current thread: final PR head `d55bb918a` reached `MERGEABLE` / `CLEAN`; non-skipped GitHub checks passed, including `Validate API Contracts`, `Generate TypeScript Types`, `Detect Breaking Changes`, `Generate Contract Validation Report`, `Mainline Governance Gate`, and `Directory Compliance Check`; merge commit is `9828cce774ca1a2e8e5043a44e15070c12a704fa` | `https://github.com/chengjon/mystocks/pull/85`; `9828cce774ca1a2e8e5043a44e15070c12a704fa`; Graphiti episode `2c1ca347-2c2e-4173-9c5a-a019fbd3acb4` | OpenSpec archive preparation for `sequence-backend-architecture-unblocks` and `canonicalize-backend-route-unified-response-contracts` |
| Post-PR `#85` OpenSpec archive preparation | C, D | Completed OpenSpec changes are moved from active change directories into archive directories and their deltas are applied to canonical specs | Review-ready: pre-archive strict validation passed for both changes; `openspec archive ... --yes` updated `01-unified-response-format` and `architecture-governance`; archive paths require forced staging because `.gitignore` ignores `openspec/changes/archive/` | `docs/reports/quality/backend-route-contract-pr85-post-merge-openspec-archive-2026-05-21.md`; `openspec/changes/archive/2026-05-20-canonicalize-backend-route-unified-response-contracts/`; `openspec/changes/archive/2026-05-20-sequence-backend-architecture-unblocks/`; `openspec/specs/01-unified-response-format/spec.md`; `openspec/specs/architecture-governance/spec.md` | Run post-archive OpenSpec and markdown validation, then publish the archive-only PR |
| PR `#86` OpenSpec archive merge | C, D | The completed route-contract and architecture-unblock OpenSpec branches are archived and their deltas are reflected in canonical specs on `wip/root-dirty-20260403` | Reviewed/pass in current thread: final PR head `6404c35f6` reached `MERGEABLE` / `CLEAN`; GitHub checks `Mainline Governance Gate` and `check-compliance` succeeded; `weekly-full-scan` skipped; merge commit is `5f48cca02505cbe5bdf3add89bf3336ab37faaa5` | `https://github.com/chengjon/mystocks/pull/86`; `5f48cca02505cbe5bdf3add89bf3336ab37faaa5`; Graphiti episode `c595a18a-8079-4be9-9be7-8295478ba970` | Next branch selection must start from the archived baseline, not from the retired active change directories |
| Issue `#83` shared C/E/F evidence package | D, E, F | Evidence package prepared for Core compatibility, singleton lifecycle, and route/OpenAPI governance without backend implementation mutation | Review-ready: current HEAD `5f48cca02`; route/OpenAPI smoke with placeholder required env produced `routes=548`, `openapi_paths=500`, `openapi_operations=536`, duplicate operationIds=`0`; validation message legacy/canonical identity smoke passed for six exports; singleton matrix remains `111` matched patterns and `0` low-risk pilot | `docs/reports/quality/backend-openspec-issue83-shared-evidence-package-2026-05-21.md`; GH issue `#83` | Human acceptance of issue `#83`; then decide issue15 consumption and OpenSpec task `3.2` disposition |
| PR `#87` issue `#83` evidence package merge | D, E, F | The shared C/E/F evidence package is now merged to `wip/root-dirty-20260403` and linked from issue `#83` for human acceptance | Reviewed/pass in current thread: final PR head `81aaab84e` reached `MERGEABLE` / `CLEAN`; GitHub checks `Mainline Governance Gate` and `check-compliance` succeeded; `weekly-full-scan` skipped; merge commit is `e938bea6b9a82ee8d3b675d342e192d1463bf3a3` | `https://github.com/chengjon/mystocks/pull/87`; `https://github.com/chengjon/mystocks/issues/83#issuecomment-4502586566`; Graphiti episode `9674bb73-9913-4e8e-8b2c-1ba19fe0c0c0` | Wait for human acceptance of issue `#83`; do not start Core Batch 2 or publish issue15 before that acceptance |
| Issue `#83` acceptance and Core task `3.2` disposition | D | Human acceptance of issue `#83` unblocks explicit Core task `3.2` disposition; the remaining split OpenSpec checklist item is marked complete for the current validation-helper package/wrapper scope | Review-ready: import smoke shows `app.core.validation` resolves to `validation/__init__.py` as a package; package and legacy wrapper exports are identity-equivalent for six validation-message symbols; targeted compat test reports `2 passed`; no backend source edits in this disposition step | `docs/reports/quality/backend-core-split-task3-2-disposition-2026-05-21.md`; `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md` | Archive the completed split Core OpenSpec change; keep future Core split work in a separate concrete plan |
| Post-PR `#89` Core split OpenSpec archive preparation | D | Completed `split-backend-core-modules-with-compatibility-wrappers` OpenSpec change is moved into archive and its deltas are applied to canonical specs | Review-ready: pre-archive strict validation passed; `openspec archive ... --yes` updated `architecture-governance` and `directory-governance`; post-archive `openspec validate --specs --strict --concurrency 1` reports `32 passed, 0 failed`; archive paths require forced staging because `.gitignore` ignores `openspec/changes/archive/` | `docs/reports/quality/backend-core-split-post-acceptance-openspec-archive-2026-05-21.md`; `openspec/changes/archive/2026-05-21-split-backend-core-modules-with-compatibility-wrappers/`; `openspec/specs/architecture-governance/spec.md`; `openspec/specs/directory-governance/spec.md` | Archive-only PR review and merge |
| PR `#90` Core split OpenSpec archive merge | D | The completed Core split OpenSpec change is archived and its deltas are reflected in canonical specs on `wip/root-dirty-20260403` | Reviewed/pass in current thread: final PR head `09fefbfcb` reached `MERGEABLE` / `CLEAN`; GitHub checks `Mainline Governance Gate` and `check-compliance` succeeded; `weekly-full-scan` skipped; merge commit is `fcc3949fe7a40052e727cbd608c746f660824b38` | `https://github.com/chengjon/mystocks/pull/90`; `openspec/changes/archive/2026-05-21-split-backend-core-modules-with-compatibility-wrappers/`; Graphiti episode `2da09150-9b02-4c43-b22a-843d643deef5` | Treat this OpenSpec branch as closed; any future Core split implementation needs a new concrete plan |
| Issue15 publication as GitHub issue `#92` | D2 | The previously blocked issue15 decision/design issue is now published for human decision after issue `#83` acceptance and Core split archive | Reviewed/pass in current thread: issue `#92` is `OPEN`; labels are exactly `enhancement`, `ready-for-human`; body contains `UNBLOCKED_BY`; body does not contain `BLOCKED_BY_TODO`; `ready-for-agent` label is absent | `https://github.com/chengjon/mystocks/issues/92`; `docs/reports/quality/backend-openspec-issue15-publication-status-2026-05-21.md`; Graphiti episode `1d858c24-68b3-4ee0-9f9b-4b870fdc6000` | Await human decision record; do not move issue `#92` to `ready-for-agent` before a concrete downstream implementation scope is approved |
| Issue `#92` approval for downstream decision work | D2 | Human maintainer approval recorded in the current review thread and commented on issue `#92`; downstream decision splitting may proceed | Reviewed/pass in current thread: issue `#92` remains `OPEN`; labels now include `enhancement`, `ready-for-human`, `ready-for-downstream`; `ready-for-agent` remains absent; approval comment is `https://github.com/chengjon/mystocks/issues/92#issuecomment-4503757722` | `docs/reports/quality/backend-openspec-issue92-approval-record-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Draft decision record / split downstream issues; no implementation issue may be moved to `ready-for-agent` before that decision record |
| Issue `#92` downstream decision split draft | D2 | Draft split prepared for human review: D2.1 DI pilot candidate, D2.2 Core validation wrapper-retirement readiness, D2.3 route governance, D2.4 backup route ownership, D2.5 control-plane OpenAPI docs, and D2.6 PM2 stateful gate approval | Review-ready draft only: issue `#92` remains `OPEN`; `ready-for-agent` remains absent; no backend, OpenSpec change, route, or test mutation is authorized by the draft | `docs/reports/quality/backend-openspec-issue92-downstream-decision-split-2026-05-21.md` | Human review and explicit acceptance or revision of the split before any child issue/proposal is created |
| Issue `#92` downstream split accepted | D2 | Human maintainer accepted the split in full: `TechnicalPatternDetectionService` is the first DI design pilot; trading route ownership folds into unified route/OpenAPI governance; backup route ownership becomes a dedicated proposal candidate with `cleanup_old_backups.py` owned by that lane | Reviewed/pass in current thread: acceptance remains decision/proposal-only and does not authorize backend implementation, route mutation, Core file movement, PM2 execution, or any `ready-for-agent` movement | `docs/reports/quality/backend-openspec-issue92-downstream-split-acceptance-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Draft D2.1 design packet for `TechnicalPatternDetectionService`; keep implementation locked behind separate approval |
| D2.1 `TechnicalPatternDetectionService` DI design packet | D2.1 | First DI design pilot packet prepared with provider shape, dependency override strategy, teardown artifact, rollback path, and implementation verification gates | Review-ready design only: GitNexus impact for `TechnicalPatternDetectionService` is LOW with 0 affected symbols/processes; no source, route, test, PM2, or OpenSpec mutation is authorized | `docs/reports/quality/backend-di-pilot-technical-pattern-detection-design-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Human review; if accepted, create a separate implementation issue or OpenSpec branch before source edits |
| D2.1a `TechnicalPatternDetectionService` DI pilot implementation authorization | D2.1a | Concrete implementation authorization plan prepared for the first DI pilot | Plan-only: future write scope is limited to `_technical_patterns_router.py` and `test_technical_patterns_router_regressions.py`; service internals, route path, response contract, OpenAPI schema, PM2, frontend, docs/API, and OpenSpec remain locked until separate implementation approval | `docs/superpowers/plans/2026-05-21-d2-1a-technical-pattern-detection-di-pilot-implementation-authorization.md`; `https://github.com/chengjon/mystocks/issues/92` | Human approval to create a separate D2.1a implementation issue or OpenSpec branch; do not move issue `#92` to `ready-for-agent` |
| D2.1a.1 `TechnicalPatternDetectionService` DI OpenSpec child branch | D2.1a.1 | Separate OpenSpec child branch implemented for the first DI implementation pilot | Route-level DI pilot is ready for review: provider injection added to `_technical_patterns_router.py`; focused public-route tests use dependency overrides and exact async `detect_for_symbol(symbol, period)` service double signature; route regression `9 passed`, service+route `19 passed`, ruff passed, placeholder-env `app.main` import passed, OpenSpec strict validate passed | `openspec/changes/inject-technical-pattern-detection-service-di/`; `openspec/changes/inject-technical-pattern-detection-service-di/proposal-review.md`; `docs/reports/quality/backend-technical-pattern-di-pilot-implementation-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | PR review / merge decision; after merge, comment the implementation result to issue `#92` while keeping `#92` as parent decision context |
| D2.2 Core validation wrapper retirement readiness | D2.2 | Readiness packet prepared for `app.core.validation_messages` retirement; deletion remains locked pending a separate wrapper-retirement decision | Review-ready readiness only: compatibility test passed `2 passed`; placeholder-env import smoke passed; active source blockers were later closed by D2.2a and docs/API examples were later closed by D2.2b | `docs/reports/quality/backend-core-validation-wrapper-retirement-readiness-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | D2.2c wrapper-retirement decision or explicit long-term retention; no wrapper deletion before that approval |
| D2.2a Core validation active source migration | D2.2a | Active source imports in `validators.py` and `error_codes.py` migrated from `app.core.validation_messages` to `app.core.validation`; wrapper retained | TDD red/green completed; boundary test `1 passed`; compatibility test `2 passed`; import smoke passed; app import smoke routes=`548`; collect-only smoke `112 tests collected`; ruff passed; active source legacy imports excluding wrapper=`0` | `docs/reports/quality/backend-core-validation-active-source-migration-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Completed by D2.2b docs/API examples canonicalization; wrapper deletion remains a separate decision |
| D2.2b Core validation docs/API example canonicalization | D2.2b | `docs/api/` examples now point to canonical `app.core.validation`; wrapper retained | Docs-only batch: pre-change `docs/api/` legacy reference count was `10`; post-change count is `0`; no backend source, tests, OpenSpec, route, PM2, or frontend files changed | `docs/reports/quality/backend-core-validation-docs-api-canonicalization-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | D2.2c wrapper-retirement decision or explicit retention; do not delete `app.core.validation_messages` from this batch |
| D2.2c Core validation wrapper retirement / retention decision package | D2.2c | Decision package prepared for whether to retain `app.core.validation_messages` long-term or approve a future deletion batch; D2.2 is formally closed as a decision lane | Evidence-only: wrapper exists; active source import consumers excluding wrapper=`0`; docs/API legacy references=`0`; compatibility test `2 passed`; boundary test `1 passed`; canonical and wrapper exports remain identity-equivalent; no backend source, tests, OpenSpec, route, PM2, or frontend files changed | `docs/reports/quality/backend-core-validation-wrapper-retirement-decision-package-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Move to D2.3; wrapper deletion remains locked unless a separate D2.2d deletion implementation batch is approved |
| D2.3 Trading route/OpenAPI governance planning package | D2.3 | Trading route ownership is folded into unified route/OpenAPI governance, not a standalone implementation lane | Planning/evidence only: current smoke at HEAD `c24f43016` reports routes=`548`, OpenAPI paths=`500`, trading candidate routes=`41` (`40` trading-route candidates plus `1` unclassified trading-adjacent route), schema-exposed=`41`, schema paths=`32`, duplicate trading operationIds=`0`; classification heuristic and consumer scan scope are recorded; no route, OpenAPI, source, frontend, test, PM2, or OpenSpec mutation is authorized | `docs/reports/quality/backend-trading-route-openapi-governance-planning-package-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Human review; if accepted, create a separate route/OpenAPI governance proposal or implementation issue before route mutation |
| D2.3 Route/OpenAPI governance OpenSpec proposal | D2.3/F | Explicit proposal created for unified backend route/OpenAPI governance after D2.3 planning acceptance | Proposal-only: `refresh-backend-route-openapi-governance` adds an architecture-governance gate requiring current-head route/OpenAPI/probe evidence, route ownership classification, runtime-vs-schema exposure classification, and separate D2.4/D2.5/D2.6 lane handling before mutation; no backend source, frontend source, tests, generated client, docs/API, route behavior, OpenAPI schema, probe URL, or PM2 changes are authorized | `openspec/changes/refresh-backend-route-openapi-governance/`; `docs/reports/quality/backend-route-openapi-governance-openspec-proposal-2026-05-21.md`; `governance/mainline/task-cards/pr-116.yaml` | Approved for governance/evidence task-list execution; no implementation or runtime mutation authorized |
| D2.3 Route/OpenAPI governance decision package | D2.3/F | Governance/evidence task list executed, reviewed, and accepted | Evidence-only: current HEAD `c173bbc8d` reports routes=`548`, schema-visible routes=`536`, hidden runtime routes=`12`, endpoint modules=`99`, OpenAPI paths=`500`, operations=`536`, schemas=`301`, duplicate operationIds=`0`, OpenAPI warnings=`0`, D2.3 trading candidate routes=`41`, and `/metrics` as the only duplicate runtime path/method; review verdict is `APPROVE`; no backend source, frontend source, tests, generated client, docs/API, route behavior, OpenAPI schema, probe URL, PM2, or implementation issue is authorized | `docs/reports/quality/backend-route-openapi-governance-decision-package-2026-05-22.md`; `docs/reports/quality/backend-route-openapi-governance-decision-package-2026-05-22-review.md`; `.planning/codebase/generated/backend-route-table-2026-05-22.json`; `.planning/codebase/generated/route-openapi-snapshot-2026-05-22.json`; `.planning/codebase/generated/probe-consumer-matrix-2026-05-22.json`; `.planning/codebase/generated/route-consumer-contract-matrix-2026-05-22.json` | Closed as reviewed evidence; any later route/OpenAPI child lane needs separate approval, owner, write scope, tests, and rollback |
| D2.4 Backup route ownership planning package | D2.4 | Backup route ownership remains a dedicated proposal candidate, not a trading or generic route cleanup lane | Planning/evidence only: current smoke at HEAD `553e71a90` reports routes=`548`, OpenAPI paths=`500`, backup candidate routes=`13`, schema-exposed=`13`, backup OpenAPI paths=`13`, backup operations=`13`, duplicate backup operationIds=`0`; `cleanup_old_backups.py` owns cleanup plus health routes; no route, OpenAPI, source, frontend, test, docs/API, PM2, or OpenSpec mutation is authorized | `docs/reports/quality/backend-backup-route-ownership-planning-package-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Human review; if accepted, create a separate backup route ownership proposal or implementation issue before backup route mutation |
| D2.4 Backup route ownership OpenSpec proposal | D2.4/F | Explicit proposal created for dedicated backup route ownership after D2.4 planning acceptance | Proposal-only: `define-backend-backup-route-ownership` adds an architecture-governance gate requiring current-head backup route/OpenAPI evidence, backup ownership class taxonomy, explicit `cleanup_old_backups.py` and `backup_service_health` ownership, security/permission/audit/rollback evidence, and separate D2.3/D2.5/D2.6 lane handling before mutation; no backend source, frontend source, tests, generated client, docs/API, route behavior, OpenAPI schema, infrastructure backup code, probe URL, or PM2 changes are authorized | `openspec/changes/define-backend-backup-route-ownership/`; `docs/reports/quality/backend-backup-route-ownership-openspec-proposal-2026-05-21.md`; `governance/mainline/task-cards/pr-118.yaml` | Approved for governance/evidence task-list execution; no implementation or runtime mutation authorized |
| D2.4 Backup route ownership decision package | D2.4/F | Governance/evidence task list executed, reviewed, and accepted | Evidence-only: current HEAD `e6d576ccc` reports routes=`548`, schema-visible routes=`536`, hidden runtime routes=`12`, OpenAPI paths=`500`, operations=`536`, schemas=`301`, backup candidate routes=`13`, backup schema-exposed routes=`13`, backup OpenAPI operations=`13`, backup duplicate operationIds=`0`, ownership classes=`7`, and `/api/backup-recovery/health` as backup-owned with D2.5 docs cross-reference; review verdict is `APPROVE`; no backend source, frontend source, tests, generated client, docs/API, route behavior, OpenAPI schema/exposure, probe URL, PM2, infrastructure backup implementation, or implementation issue is authorized | `docs/reports/quality/backend-backup-route-ownership-decision-package-2026-05-22.md`; `docs/reports/quality/backend-backup-route-ownership-decision-package-2026-05-22-review.md`; `.planning/codebase/generated/backup-route-ownership-evidence-2026-05-22.json`; `openspec/changes/define-backend-backup-route-ownership/tasks.md` | Closed as reviewed evidence; any future implementation lane needs separate approval, owner, exact write scope, tests, and rollback |
| D2.5 Control-plane OpenAPI docs planning package | D2.5 | Control-plane OpenAPI docs stabilization remains a dedicated documentation/probe governance lane | Planning/evidence only: current smoke at HEAD `b39b7b3ee` reports routes=`548`, OpenAPI paths=`500`, broad control/status candidate routes=`128`, focused duplicate operationIds=`0`, `/health/readiness` absent, `/api/strategy-mgmt/{path:path}` runtime-only hidden, and `/metrics` as the focused duplicate runtime path/method; no route, OpenAPI, docs/API, source, frontend, test, PM2, or OpenSpec mutation is authorized | `docs/reports/quality/backend-control-plane-openapi-docs-planning-package-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Human review; if accepted, create a separate control-plane OpenAPI docs proposal or documentation issue before docs/API or route mutation |
| D2.5 Control-plane OpenAPI docs OpenSpec proposal | D2.5/F | Explicit proposal created for control-plane OpenAPI documentation stabilization after D2.5 planning acceptance | Proposal-only: `stabilize-backend-control-plane-openapi-docs` adds an API documentation gate requiring current-head route/OpenAPI/probe evidence, health/readiness taxonomy, metrics/docs/schema surface classification, runtime-vs-schema exposure classification, and separate D2.3/D2.4/D2.6 lane handling before docs/API or route mutation; no backend source, frontend source, tests, generated client, docs/API, route behavior, OpenAPI schema, probe URL, or PM2 changes are authorized | `openspec/changes/stabilize-backend-control-plane-openapi-docs/`; `docs/reports/quality/backend-control-plane-openapi-docs-openspec-proposal-2026-05-21.md`; `governance/mainline/task-cards/pr-117.yaml` | Approved for governance/evidence task-list execution; no implementation or runtime mutation authorized |
| D2.5 Control-plane OpenAPI docs decision package | D2.5/F | Governance/evidence task list executed, reviewed, and accepted | Evidence-only: current HEAD `15db8ebf5` reports routes=`548`, schema-visible routes=`536`, hidden runtime routes=`12`, OpenAPI paths=`500`, operations=`536`, schemas=`301`, duplicate operationIds=`0`, OpenAPI warnings=`0`, broad control/status candidates=`144`, `/health/readiness` absent, `/api/strategy-mgmt/{path:path}` runtime-only hidden, and `/metrics` as the only duplicate runtime path/method; review verdict is `APPROVE`; no backend source, frontend source, tests, generated client, docs/API, route behavior, OpenAPI schema/exposure, probe URL, PM2, or implementation issue is authorized | `docs/reports/quality/backend-control-plane-openapi-docs-decision-package-2026-05-22.md`; `docs/reports/quality/backend-control-plane-openapi-docs-decision-package-2026-05-22-review.md`; `.planning/codebase/generated/control-plane-openapi-docs-evidence-2026-05-22.json`; `openspec/changes/stabilize-backend-control-plane-openapi-docs/tasks.md` | Closed as reviewed evidence; any future docs/API implementation lane needs separate approval, owner, exact target files, checks, and rollback |
| D2.6 PM2 stateful gate approval governance package | D2.6 | Future PM2 stateful gate execution requires explicit approval or an approved named equivalent; issue `#92` remains a decision issue, not an execution issue | Governance/evidence only: health/status task `4.7` is already closed by `backend-health-status-pm2-gate-2026-05-18.md`; `run_pm2_integration_workflow.sh` includes stateful `pm2 stop all` / `pm2 delete all`; no PM2 command, runtime code, route, OpenAPI, docs/API, frontend, test, or OpenSpec mutation is authorized | `docs/reports/quality/backend-pm2-stateful-gate-approval-governance-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Human review; create `approve-backend-pm2-stateful-gate` or a named-equivalent approval runbook only when a future workline needs a fresh PM2 run |
| D2.6 PM2 stateful gate approval OpenSpec proposal | D2.6 | Explicit proposal created for PM2 stateful gate approval policy after D2.6 governance-package acceptance | Proposal-only: `approve-backend-pm2-stateful-gate` adds an architecture-governance gate requiring explicit approval records before `gate`, `regression`, `all`, read-only PM2 sampling, or named-equivalent PM2 validation; no PM2 command, service restart, backend source, frontend source, tests, generated client, docs/API, route behavior, OpenAPI schema, probe URL, or movement of issue `#92` to `ready-for-agent` is authorized | `openspec/changes/approve-backend-pm2-stateful-gate/`; `docs/reports/quality/backend-pm2-stateful-gate-openspec-proposal-2026-05-21.md`; `governance/mainline/task-cards/pr-119.yaml` | Approved for governance/evidence task-list execution; no PM2 execution or runtime mutation authorized |
| D2.6 PM2 stateful gate approval decision package | D2.6 | PM2 stateful gate approval policy reviewed and accepted | Governance/evidence only: current HEAD `b35d016f8` confirms issue `#92` is `OPEN` with `ready-for-human` and `ready-for-downstream`, no `ready-for-agent`; static scan classifies `gate`, `regression`, and `all` as stateful workflows because `scripts/run_pm2_integration_workflow.sh` can run `pm2 stop all`, `pm2 delete all`, `pm2 start ecosystem.test.config.js`, and PM2-backed E2E; health/status task `4.7` remains closed by historical evidence; review verdict is `APPROVE`; non-blocking task-card suggestion was satisfied by PR `#127`; no PM2 command, service restart/recreation, source, frontend, tests, docs/API, route, OpenAPI, probe URL, generated client, or implementation issue is authorized | `docs/reports/quality/backend-pm2-stateful-gate-approval-decision-package-2026-05-22.md`; `docs/reports/quality/backend-pm2-stateful-gate-approval-decision-package-2026-05-22-review.md`; `.planning/codebase/generated/pm2-stateful-gate-approval-evidence-2026-05-22.json`; `openspec/changes/approve-backend-pm2-stateful-gate/tasks.md` | Closed as reviewed evidence; any future PM2 run must use a narrow approval issue, issue comment, or approved runbook naming exact command mode, service impact, rollback/restore, evidence destination, timeout, stop rule, and acceptance owner |
| D2 downstream decision rollup closeout | D2 closeout | D2.1-D2.6 downstream packages are summarized as a complete decision package; issue `#92` remains a parent decision issue | Rollup/evidence only: PRs `#96`-`#113` are merged; issue `#92` is `OPEN` with `ready-for-human` and `ready-for-downstream`; `ready-for-agent` remains absent; first recommended true implementation lane, D2.1a `TechnicalPatternDetectionService` DI pilot, is now closed end-to-end | `docs/reports/quality/backend-openspec-issue92-downstream-rollup-closeout-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92`; PRs `#112` and `#113` | Human decision whether to create the next concrete child issue or OpenSpec branch; this rollup does not authorize implementation |
| Issue `#92` downstream final closeout | D2 closeout | Final closeout accepted for archive-gate purposes by explicit review-thread waiver | Governance/evidence only: PRs `#96`-`#128` are merged; issue `#92` remains `OPEN` with `ready-for-human` and `ready-for-downstream`, and no `ready-for-agent`; D2.1a is implementation/governance closed; D2.2 is closed as a decision lane; D2.3-D2.6 are reviewed/accepted as evidence; waiver only unlocks the separate archive PR gate and does not authorize implementation or archive inside the closeout packet | `docs/reports/quality/backend-openspec-issue92-downstream-final-closeout-2026-05-22.md`; `docs/reports/quality/backend-openspec-issue92-downstream-final-closeout-2026-05-22-review-waiver.md`; `.planning/codebase/generated/issue92-downstream-final-closeout-2026-05-22.json`; PR `#129` | Prepare separate archive PR naming exact change IDs and running OpenSpec validation |
| Issue `#92` OpenSpec archive readiness | D2 archive-readiness | Completed issue `#92` OpenSpec changes evaluated for a future archive review | Governance/evidence only: `inject-technical-pattern-detection-service-di`, `refresh-backend-route-openapi-governance`, `define-backend-backup-route-ownership`, `stabilize-backend-control-plane-openapi-docs`, and `approve-backend-pm2-stateful-gate` show `Complete`; no `openspec archive` command was executed and no OpenSpec files were modified | `docs/reports/quality/backend-openspec-issue92-archive-readiness-2026-05-22.md`; `.planning/codebase/generated/issue92-openspec-archive-readiness-2026-05-22.json`; PR `#130` | Archive-readiness review closeout; still require final closeout review or explicit waiver before archive execution |
| Issue `#92` OpenSpec archive readiness review closeout | D2 archive-readiness | Archive readiness report reviewed and accepted | Reviewed/pass: review verdict is `APPROVE` with no issues found; all 5 candidate OpenSpec change directories exist and have complete task counts; issue `#92` remains `OPEN` with `enhancement`, `ready-for-human`, and `ready-for-downstream`, and no `ready-for-agent`; original pre-report HEAD `bbefed2aee4176936cd491128bb6a85aed2410d3`, report commit `36070d504`, and PR `#130` merge commit `9d0a0a2a3eb6f2bb0e9d3ee6ce10369adc153966` are recorded for commit-chain traceability; no archive execution or OpenSpec change/spec mutation is authorized | `docs/reports/quality/backend-openspec-issue92-archive-readiness-2026-05-22.md`; `docs/reports/quality/backend-openspec-issue92-archive-readiness-2026-05-22-review.md`; `.planning/codebase/generated/issue92-openspec-archive-readiness-2026-05-22.json` | Human review or explicit waiver of the final closeout, then create a separate archive PR naming exact change IDs and running OpenSpec validation |
| Issue `#92` final closeout review waiver | D2 closeout | Human maintainer approval in the current review thread recorded as waiver of a separate line-by-line final closeout review artifact | Governance/evidence only: waiver timestamp `2026-05-22T09:54:09+08:00`; issue `#92` remains `OPEN` with `enhancement`, `ready-for-human`, and `ready-for-downstream`, and no `ready-for-agent`; waiver only allows the next archive PR gate for the five named completed changes and does not authorize implementation, PM2 execution, source/test/docs/API/runtime changes, or issue movement | `docs/reports/quality/backend-openspec-issue92-downstream-final-closeout-2026-05-22-review-waiver.md`; `docs/reports/quality/backend-openspec-issue92-downstream-final-closeout-2026-05-22.md`; `.planning/codebase/generated/issue92-downstream-final-closeout-2026-05-22.json` | Create separate archive PR for the five approved candidate changes and run OpenSpec validation before and after archive |
| Issue `#92` OpenSpec archive execution | D2 archive | Five completed issue `#92` OpenSpec changes archived and their deltas applied to canonical specs | Archive-only: `inject-technical-pattern-detection-service-di`, `refresh-backend-route-openapi-governance`, `define-backend-backup-route-ownership`, `stabilize-backend-control-plane-openapi-docs`, and `approve-backend-pm2-stateful-gate` moved to `openspec/changes/archive/2026-05-22-*`; canonical specs updated in `architecture-governance` and `api-documentation`; post-archive validation `openspec validate --specs --strict` reports `32 passed, 0 failed`, and `openspec validate --changes --strict` reports `28 passed, 0 failed`; no source, test, docs/API, runtime, PM2, implementation issue, or issue `#92` label movement is authorized | `docs/reports/quality/backend-openspec-issue92-archive-execution-2026-05-22.md`; `.planning/codebase/generated/issue92-openspec-archive-2026-05-22.json`; `openspec/changes/archive/2026-05-22-*`; `openspec/specs/architecture-governance/spec.md`; `openspec/specs/api-documentation/spec.md` | PR review / merge decision, then issue `#92` archive result comment |
| Issue `#92` parent disposition | D2 parent-index | Keep issue `#92` open as the parent downstream decision index after D2 archive merge | Governance-only: issue `#92` remains `OPEN` with `enhancement`, `ready-for-human`, and `ready-for-downstream`; `ready-for-agent` remains absent; this records that #92 is audit context only and any future implementation must use a new approved child lane with owner, exact write scope, current-head evidence, verification gates, rollback plan, and issue routing | `docs/reports/quality/backend-openspec-issue92-parent-disposition-2026-05-22.md`; `.planning/codebase/generated/issue92-parent-disposition-2026-05-22.json`; PR `#134` | Keep open unless a human explicitly closes or relabels #92 |
| G1 adapter lifecycle DI child-lane selection | G1/#78 | Select issue `#78` adapter lifecycle DI triage and evidence reconciliation as the next candidate child lane | Governance-only: issue `#78` is `OPEN` with `needs-triage`; issue `#79` is `OPEN` with `needs-triage` and remains blocked by `#78`; no OpenSpec proposal, implementation issue, label change, source/test/runtime/PM2 change, or `ready-for-agent` movement is authorized | `docs/reports/quality/backend-next-child-lane-selection-2026-05-22.md`; `.planning/codebase/generated/next-child-lane-selection-2026-05-22.json` | Prepare separate G1 evidence/triage packet for `#78` with current-head adapter inventory, pilot reconciliation, exact future write scope, verification gates, and rollback |
| G1 adapter lifecycle DI triage packet | G1/#78 | Current-head issue `#78` evidence packet prepared for review | Governance/evidence only: issue `#78` remains `OPEN` with `needs-triage`; issue `#79` remains blocked; `eastmoney_adapter`, `eastmoney_enhanced`, `akshare_extension`, `tqlex_adapter`, and `cninfo_adapter` have provider/app-state/test evidence and no `_instance = None`; `realtime_mtm` has no current adapter file under `web/backend/app/adapters`; five service/core files require direct getter consumer classification before any future implementation | `docs/reports/quality/backend-adapter-lifecycle-di-triage-2026-05-22.md`; `.planning/codebase/generated/adapter-lifecycle-di-triage-2026-05-22.json`; PR `#136` | Human review; if accepted, decide whether to close `#78` as reconciled or create a separate implementation authorization with exact write scope |
| G1 adapter lifecycle DI disposition packet | G1/#78 | Issue `#78` closeout disposition prepared for review | Governance/evidence only: recommends closing `#78` as reconciled after human acceptance; does not close the issue, change labels, create implementation work, or move `#78`/`#79`/`#92` to `ready-for-agent`; remaining direct consumer cleanup, `realtime_mtm` ownership, and composition-root wiring are routed to separate child packets if needed | `docs/reports/quality/backend-adapter-lifecycle-di-disposition-2026-05-22.md`; `.planning/codebase/generated/adapter-lifecycle-di-disposition-2026-05-22.json`; PR `#137` | Human review; if accepted, post closeout/closing comment to `#78`, then begin `#79` service lifecycle design/triage without implementation authority |
| G1 adapter lifecycle DI closeout acceptance | G1/#78 | Human maintainer accepted issue `#78` disposition | Governance/closeout only: after this record merges, issue `#78` may be closed as reconciled governance evidence; remaining direct consumer cleanup, `realtime_mtm` identity, and composition-root wiring remain separate child-packet concerns; issue `#79` may start design/triage only after #78 closeout, and implementation remains locked | `docs/reports/quality/backend-adapter-lifecycle-di-closeout-acceptance-2026-05-22.md`; `.planning/codebase/generated/adapter-lifecycle-di-closeout-acceptance-2026-05-22.json`; PR `#138` | Post required closeout comment and close `#78`; then prepare issue `#79` service lifecycle DI design/triage packet |
| G2 service lifecycle DI design/triage | G2/#79 | Issue `#79` design/triage packet prepared after issue `#78` closeout | Governance/design only: issue `#78` is `CLOSED`; issue `#79` remains `OPEN` with `needs-triage`; 152 service files scanned; broad singleton/getter heuristic hit 104 files but is not a backlog; narrow signals are `_instance = None` in 4 files, `get_*service` in 16 files, one provider/app-state pattern, and one completed route-level DI pilot; no source/test/runtime/PM2/OpenSpec/label/`ready-for-agent` movement is authorized | `docs/reports/quality/backend-service-lifecycle-di-design-triage-2026-05-22.md`; `.planning/codebase/generated/service-lifecycle-di-design-triage-2026-05-22.json`; PR `#139` | Human review; next packet must select/classify candidates and define exact write scope before implementation |
| G2.1 service lifecycle DI candidate classification | G2.1/#79 | Candidate classification and first future pilot selection prepared | Governance/design only: corrected module-level singleton-variable scan finds 21 files; `tradingview_widget_service.py` is reference evidence, `technical_pattern_detection_service.py` is completed pilot evidence, and `email_service.py` is selected as the recommended first future implementation candidate; `strategy`, `tdx`, and `stock_search` are excluded by CRITICAL impact; `monitoring` and `technical_analysis` are excluded as large/cross-cutting; no source/test/runtime/PM2/OpenSpec/label/`ready-for-agent` movement is authorized | `docs/reports/quality/backend-service-lifecycle-di-candidate-classification-2026-05-22.md`; `.planning/codebase/generated/service-lifecycle-di-candidate-classification-2026-05-22.json`; PR `#140` | Human review; if accepted, prepare separate G2.2 `email_service.py` implementation authorization with exact write scope |
| D2.1a TechnicalPatternDetectionService DI implementation | D2.1a.1 | First service-tier route-level DI pilot merged; `_technical_patterns_router.py` now exposes `get_technical_pattern_detection_service()`, `detect_patterns()` receives the service through `Depends`, and focused route tests use `app.dependency_overrides` | Reviewed/pass in current thread: PR `#112` checks passed, merge commit `80582643578d587ead81ccb3d23dcd2a52668dba`; route regression `9 passed`; service+route `19 passed`; ruff passed; placeholder-env `app.main` import passed; OpenSpec strict valid; mainline scope gate passed; GitNexus compare low risk with `0` changed symbols and `0` affected processes | `https://github.com/chengjon/mystocks/pull/112`; `docs/reports/quality/backend-technical-pattern-di-pilot-implementation-2026-05-21.md`; `openspec/changes/inject-technical-pattern-detection-service-di/` | D2.1a final OpenSpec checklist governance closeout |
| D2.1a final OpenSpec checklist governance closeout | D2.1a.1 | OpenSpec task `5.3` marked complete with issue `#92` closeout comment evidence; D2.1a is closed from implementation plus checklist governance perspectives | Reviewed/pass in current thread: PR `#113` checks passed, merge commit `c7e263b8fcdeea4fc952a86d64ac555ca6dde6ce`; changed files limited to `tasks.md` and `pr-113.yaml`; mainline scope gate changed files=`2`, violations=`0`; GitNexus compare low risk with `0` changed symbols and `0` affected processes | `https://github.com/chengjon/mystocks/pull/113`; `https://github.com/chengjon/mystocks/issues/92#issuecomment-4508297089`; `openspec/changes/inject-technical-pattern-detection-service-di/tasks.md` | No further D2.1a work; select a new approved child lane before any additional implementation |
| D2.x OpenSpec proposal approvals recorded | D2.3-D2.6 | Human maintainer approval recorded for D2.3/D2.4/D2.5/D2.6 proposal task-list entry into governance/evidence execution | Approval-only: each change may execute its governance/evidence `tasks.md` checklist with current-head freshness; no backend source, frontend source, tests, generated client, docs/API edits, route behavior, OpenAPI schema/exposure, probe URL change, PM2 command execution, service restart/recreation, implementation issue creation, or movement of issue `#92` to `ready-for-agent` is authorized | `docs/reports/quality/backend-openspec-d2-proposal-approval-record-2026-05-22.md`; `governance/mainline/task-cards/pr-120.yaml` | Execute approved governance/evidence tasks and keep every downstream decision tied to refreshed evidence |

| G2.12 watchlist helper cleanup next-lane decision | G | Selected adapter-aware watchlist helper cleanup authorization as the next service lifecycle DI lane after G2.11 closeout | Reviewed and merged by PR `#152` at `0ccf1fc58d531cba8f64cc1031d53875e636a766`; no backend source, test, OpenSpec, issue label, route, OpenAPI, or runtime change authorized | `docs/reports/quality/backend-watchlist-helper-cleanup-next-lane-decision-2026-05-23.md`; `.planning/codebase/generated/watchlist-helper-cleanup-next-lane-decision-2026-05-23.json` | Superseded by G2.13 authorization packet |
| G2.13 watchlist helper cleanup implementation authorization | G | Exact future write scope, TDD plan, GitNexus gates, and rollback boundary prepared for adapter-aware watchlist helper cleanup | Reviewed and merged by PR `#153` at `938682debb90a25392ca208e706d8388d06de786`; no backend source, test, OpenSpec, issue label, route, OpenAPI, or runtime change authorized by that PR | `docs/reports/quality/backend-watchlist-helper-cleanup-implementation-authorization-2026-05-23.md`; `.planning/codebase/generated/watchlist-helper-cleanup-implementation-authorization-2026-05-23.json` | Superseded by G2.14 implementation evidence |
| G2.14 watchlist helper cleanup implementation | G | Adapter-aware provider seam implemented for both watchlist helper adapter files with focused TDD coverage | Reviewed and merged by PR `#154` at `1dcb394a49a9d95e939b2119acc431b825954036`: red `4 failed, 2 passed`; green focused helper `6 passed`; route DI regression `3 passed`; logging regression `3 passed`; ruff passed; OpenAPI smoke `routes=548`, `paths=500`, `duplicate_operation_ids=0`; Mainline Governance Gate and check-compliance passed | `docs/reports/quality/backend-watchlist-helper-cleanup-implementation-2026-05-23.md`; `web/backend/tests/test_watchlist_helper_lifecycle_di.py`; https://github.com/chengjon/mystocks/pull/154 | Superseded by G2.15 closeout packet |
| G2.15 watchlist helper cleanup closeout | G | Adapter-aware watchlist helper cleanup completion recorded after PR `#154` merge | Reviewed and merged by PR `#155` at `03c48f74d73f1de505470698966776f6624a0ec7`: current-head helper tests `6 passed`; route DI regression `3 passed`; logging regression `3 passed`; ruff passed; OpenAPI smoke `routes=548`, `paths=500`, `duplicate_operation_ids=0`; no source, route, OpenAPI, OpenSpec, frontend, config, PM2, issue-label, or runtime change authorized | `docs/reports/quality/backend-watchlist-helper-cleanup-closeout-2026-05-23.md`; `.planning/codebase/generated/watchlist-helper-cleanup-closeout-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/155 | Superseded by G2.16 next-lane decision packet |
| G2.16 service lifecycle DI next-lane decision | G/#79 | Select current-head candidate refresh as the next service lifecycle DI governance lane | Reviewed and merged by PR `#156` at `33e75acddf5c7c363a2e33ba4a3d01923b46edde`: prior low/medium candidate queue is consumed (`email_service.py`, `announcement_service.py`, `watchlist_service.py`), watchlist helper seam is closed, issue `#79` remains `OPEN` with `needs-triage`, and no fourth implementation target or adapter cleanup is authorized | `docs/reports/quality/backend-service-lifecycle-di-next-lane-decision-2026-05-23.md`; `.planning/codebase/generated/service-lifecycle-di-next-lane-decision-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/156 | Superseded by G2.17 candidate refresh packet |
| G2.17 service lifecycle DI candidate refresh | G/#79 | Refresh current-head service lifecycle DI candidate inventory before selecting another implementation lane | Reviewed and merged by PR `#157` at `0285d1cbc29b4622b3e39c9a171ba3b02691ed1b`: `stock_search_service` is the only recommended future authorization candidate, and source edits remain locked until G2.18 | `docs/reports/quality/backend-service-lifecycle-di-candidate-refresh-2026-05-23.md`; `.planning/codebase/generated/service-lifecycle-di-candidate-refresh-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/157 | Superseded by G2.18 authorization packet |
| G2.18 stock search service lifecycle DI authorization | G/#79 | Exact future write scope, TDD plan, GitNexus gates, and rollback boundary prepared for route-surface-only `stock_search_service` DI | Reviewed and merged by PR `#158` at `d63b18ab98417d9051dfbf177a975ac7470c96d3`: scope limited to the service package, five stock-search route handlers, market `get_kline_data`, focused tests, implementation report, and task card | `docs/reports/quality/backend-stock-search-service-lifecycle-di-implementation-authorization-2026-05-23.md`; `.planning/codebase/generated/stock-search-service-lifecycle-di-implementation-authorization-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/158 | Superseded by G2.19 implementation evidence |
| G2.19 stock search service lifecycle DI implementation | G/#79 | Route-surface-only `stock_search_service` DI implemented and merged | Reviewed and merged by PR `#159` at `25db762ae6484ad4638baf0f8ab42b94a978a403`: focused pytest `31 passed`, ruff and black passed, app/OpenAPI smoke `routes=548`, `paths=500`, GitNexus HIGH was expected for the authorized route surface, and GitHub contract/governance checks passed | `docs/reports/quality/backend-stock-search-service-lifecycle-di-implementation-2026-05-23.md`; `web/backend/tests/test_stock_search_service_lifecycle_di.py`; https://github.com/chengjon/mystocks/pull/159 | Superseded by G2.20 closeout packet |
| G2.20 stock search service lifecycle DI closeout | G/#79 | Closeout records PR `#159` merge result and route-surface scan | Reviewed and merged by PR `#160` at `f8063b512fb7c3aabfabef9d80d05d1d682569b5`: no backend source/test/runtime/OpenSpec/issue-label changes; post-merge scan shows `0` direct `get_stock_search_service()` calls in approved route files and preserves the compatibility getter boundary; no next service candidate selected | `docs/reports/quality/backend-stock-search-service-lifecycle-di-closeout-2026-05-23.md`; `.planning/codebase/generated/stock-search-service-lifecycle-di-closeout-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/160 | Superseded by G2.21 next-lane decision packet |
| G2.21 service lifecycle DI next-lane after stock-search | G/#79 | Select current-head candidate refresh as the next service lifecycle DI governance lane | Reviewed and merged by PR `#161` at `d2e799cd2c1cbeb00b70d5cf64897b7c8a8a3b11`: current-head quick scan at `f8063b512fb7` shows remaining getter/singleton/provider signal files require classification; no source, test, route, OpenAPI, OpenSpec, issue-label, runtime, PM2, compatibility getter cleanup, or next implementation candidate is authorized | `docs/reports/quality/backend-service-lifecycle-di-next-lane-after-stock-search-2026-05-23.md`; `.planning/codebase/generated/service-lifecycle-di-next-lane-after-stock-search-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/161 | Superseded by G2.22 current-head candidate refresh |
| G2.22 service lifecycle DI candidate refresh after stock-search | G/#79 | Refresh current-head service lifecycle candidates after stock-search route-surface DI | Reviewed and merged by PR `#162` at `d186ce78ee0ad4017b36e3788a54533ce3a972df`: scanned 152 service files, recorded 42 broad heuristic hit files and 17 narrow candidate files, selected G2.23 stock-search compatibility getter consumer matrix, and kept source edits locked | `docs/reports/quality/backend-service-lifecycle-di-candidate-refresh-after-stock-search-2026-05-23.md`; `.planning/codebase/generated/service-lifecycle-di-candidate-refresh-after-stock-search-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/162 | Superseded by G2.23 consumer matrix |
| G2.23 stock-search compatibility getter consumer matrix | G/#79 | Decide whether `get_stock_search_service()` cleanup is authorized after route-surface DI | Review-ready: route direct getter calls remain `0`; route provider refs are `8`; tests and package exports still intentionally cover compatibility getter, installer, state key, and provider behavior; no source/test/route cleanup implementation is authorized | `docs/reports/quality/backend-stock-search-compatibility-getter-consumer-matrix-2026-05-23.md`; `.planning/codebase/generated/stock-search-compatibility-getter-consumer-matrix-2026-05-23.json` | Human review; if accepted, retain the getter and open a separate broad service seam design packet before source edits |
| G2.24 broad service seam design | G/#79 | Decompose broad market/data/strategy service seams before selecting another implementation lane | Review-ready: PR `#163` merged at `18f5b43275bbd1fc7f53c739063da37c6a753b11`; current-head text scan covers `market_data_service_v2`, `market_data_service`, `data_service`, `strategy_service`, `tdx_service`, `enhanced_data_service`, and `technical_analysis_service`; GitNexus spot checks classify most broad seams as CRITICAL and select no mixed implementation batch | `docs/reports/quality/backend-broad-service-seam-design-2026-05-23.md`; `.planning/codebase/generated/broad-service-seam-design-2026-05-23.json` | Human review; if accepted, create G2.25 market-data provider design packet before source edits |

## OpenSpec Branch Register

| Change ID | State | Parent source | Primary evidence | Scope | Next action |
|---|---|---|---|---|---|
| `sequence-backend-architecture-unblocks` | `archived-merged` | Master execution plan | Runtime triage, schema closure, freshness, singleton matrix, error-contract verification | First gate branch for runtime unblock and evidence refresh | Archived by PR `#86`; future work must use the archived evidence as baseline and open a follow-up branch for new implementation |
| `canonicalize-backend-route-unified-response-contracts` | `archived-merged` | `sequence-backend-architecture-unblocks` Task 8.8 | UnifiedResponse contract guard blocker: 27 errors across 4 changed route files now reduced to 0 | Dedicated route-contract migration for `data_quality.py`, `indicator_cache.py`, `signal_history_response.py`, and `technical_analysis.py`; implementation merged via PR `#85` | Archived by PR `#86`; keep implementation notes as follow-up candidates, not blockers |
| `split-backend-core-modules-with-compatibility-wrappers` | `archived-merged` | Existing OpenSpec line | Core split reconciliation | Core helper split continuation | Archived by PR `#90`; future Core split work requires a new concrete implementation plan and approval |
| `github-issue-92-backend-openspec-issue15` | `parent-index-retained` | Current review-thread approval, issue `#83` acceptance, downstream split draft, human split acceptance, D2.1-D2.6 rollup, D2.3-D2.6 reviewed evidence packages, final closeout waiver, archive-readiness review, OpenSpec archive, and parent disposition artifact | Post-approval downstream decision boundary | Decision/design issue only; no implementation work | Keep issue `#92` open as parent context unless a human explicitly closes or relabels it; future implementation requires a new approved child lane |
| `select-backend-technical-pattern-di-pilot` | `design-packet-prepared` | Issue `#92` downstream split acceptance | First DI lifecycle pilot design packet | Provider shape, dependency override strategy, teardown, rollback, and verification gates for `TechnicalPatternDetectionService` | Human review before creating any implementation issue or OpenSpec branch |
| `inject-technical-pattern-detection-service-di` | `implementation-ready-for-review` | D2.1 design packet, D2.1a authorization plan, proposal review, and implementation evidence | First implementation child branch for `TechnicalPatternDetectionService` DI pilot | Route-local provider, FastAPI dependency override test seam, rollback, and focused verification for `_technical_patterns_router.py` | PR review / merge decision; do not broaden to a second service DI pilot in this branch |
| `decide-backend-core-validation-wrapper-retirement` | `active-source-migration-complete` | Issue `#92` downstream split acceptance and validation helper split archive | Core validation compatibility wrapper retirement readiness and staged migration | D2.2a active source migration is complete; docs/API examples and compatibility-test conversion remain separate gates | D2.2b docs/API examples canonicalization or explicit waiver; wrapper deletion remains blocked |
| `define-backend-backup-route-ownership` | `decision-package-reviewed-accepted` | Issue `#92` downstream split acceptance, D2.4 planning package, D2.3 route governance proposal, D2.5 control-plane docs proposal, and D2.4 review artifact | Reviewed backup route ownership decision package with current-head backup route/OpenAPI evidence, ownership taxonomy, cleanup and backup-service health ownership, safety/security matrix, consumer matrix, and rollback routing | Backup, recovery, scheduler, integrity, cleanup, health, safety, security, consumer, OpenAPI, and rollback ownership gates | Closed as reviewed evidence; no implementation lane without a later approved child packet |
| `stabilize-backend-control-plane-openapi-docs` | `decision-package-reviewed-accepted` | Issue `#92` downstream split acceptance, D2.5 planning package, route/OpenAPI/probe refresh, D2.3 route governance proposal, and D2.5 review artifact | Reviewed control-plane docs/probe decision package with current-head route/OpenAPI/probe evidence, health/readiness taxonomy, OpenAPI docs UI/schema routes, metrics/status probes, and runtime-only compat redirects | Documentation/probe governance for liveness, readiness, service health, detailed health, status, metrics, docs UI, OpenAPI schema, runtime-only compat redirects, and intentionally absent aliases | Closed as reviewed evidence; no docs/API or implementation lane without a later approved child packet |
| `approve-backend-pm2-stateful-gate` | `decision-package-reviewed-accepted` | Issue `#92` downstream split acceptance, D2.6 approval-governance package, historical health/status PM2 evidence, and D2.6 review artifact | Reviewed PM2 stateful workflow approval strategy and named-equivalent rules | Approval records for `run_pm2_integration_workflow.sh` modes, stateful service mutation, rollback, evidence artifact routing, read-only sampling, and named equivalents | Closed as reviewed evidence; future PM2 execution requires a separate narrow approval issue, issue comment, or approved runbook |
| `close-backend-schema-dual-directory` | `candidate` | Master execution plan | Schema dual-directory closure | Schema exports, consumer migration, shim retirement decision | Create only after `sequence-backend-architecture-unblocks` schema tasks are accepted |
| `refresh-backend-route-openapi-governance` | `decision-package-reviewed-accepted` | Master execution plan, route/OpenAPI/probe refresh, D2.3 planning package, proposal approval record, and review artifact | Decision package accepted with current-head route table, OpenAPI, probe matrix, trading ownership, runtime-vs-schema, and consumer contract evidence | Route table, OpenAPI, operationId, probe matrix, trading ownership, control-plane, backup, compatibility, and schema-exposure classification; no route/OpenAPI/source/docs/API/PM2 mutation | Closed as reviewed evidence; do not open implementation lanes without a separate accepted child plan |
| `define-backend-service-seams-and-singleton-pilots` | `candidate` | Master execution plan | Singleton lifecycle routing matrix | Service seam definition, interface/test-double pilot strategy | Create as a design proposal after complete classification |

## Dependency and Freshness Matrix

| Branch | Depends On | Last Freshened HEAD | Freshness note |
|---|---|---|---|
| A. Architecture Baseline | Current evidence artifacts | `7b097fffd` | Baseline contains stale historical snapshots; newer evidence must be linked instead of silently replacing history |
| B. Master Execution Plan | Architecture baseline and cross-line reports | `7b097fffd` | Control plan; update only when governance flow changes |
| C. `sequence-backend-architecture-unblocks` | Human approval, current runtime blocker verification | `7b097fffd` | Tasks 1.x through 8.x complete; runtime blocker closed, schema shim closure implemented, route/OpenAPI/probe evidence refreshed, service seam proposal path recorded |
| D. Core split continuation | Task 3.2 disposition, #83 evidence acceptance, runtime evidence refresh | `7b097fffd` | Batch 2 remains blocked |
| E. Schema dual-directory closure | `app.schema` consumer scan and `app.schemas` export proof | `7b097fffd` | Task 3.x complete; root checkout now has 0 legacy `app.schema` consumers and canonical exports are live |
| F. Route/OpenAPI governance | Healthy `app.main` import chain, current-head evidence refresh, and accepted D2.3/D2.4/D2.5 reviews | `e6d576ccc` | D2.3 route/OpenAPI decision package, D2.4 backup route ownership decision package, and D2.5 control-plane docs decision package are reviewed and accepted as evidence; D2.6 PM2 lane remains separate; no backup, docs/API, route mutation, OpenAPI exposure change, probe URL change, or PM2 approval decision is authorized by this evidence alone |
| D2. Issue 92 downstream governance | Issue `#92`, D2.1a-D2.6 evidence, PR range review, final closeout waiver, archive readiness review, OpenSpec archive, and parent disposition | `c1e3de55` | PRs `#96`-`#133` are merged; D2.1a implementation/governance is closed, D2.2 decision lane is closed, D2.3-D2.6 are reviewed/accepted as evidence, five completed OpenSpec changes are archived, and issue `#92` remains open without `ready-for-agent` as parent decision index |
| D2 parent disposition | Issue `#92` post-archive state | `c1e3de55` | Keep issue `#92` open as parent context unless a human explicitly closes or relabels it; all future implementation work needs a new approved child lane |
| G1 adapter lifecycle DI selection | Issue `#78` and issue `#79` dependency state | `c45eaa9c` | Select `#78` adapter lifecycle DI triage/reconciliation as next candidate child lane; no implementation or OpenSpec proposal is authorized until a separate G1 evidence packet is accepted |
| G1 adapter lifecycle DI triage | Current-head adapter provider/app-state/test evidence and direct getter consumer scan | `2dbca6986` | Five adapter targets have provider/app-state/test evidence and no `_instance = None`; `realtime_mtm` is not proven as a current adapter target; five service/core consumers require classification; no implementation, label movement, OpenSpec proposal, source/test/runtime/PM2 mutation, or issue `#78`/`#79`/`#92` `ready-for-agent` movement is authorized |
| G1 adapter lifecycle DI disposition | Merged triage packet and issue `#78` current state | `299f0aa7` | Recommend closing `#78` as reconciled after human acceptance; keep all remaining implementation concerns in separate approved child packets; `#79` may only start service lifecycle design/triage after the `#78` disposition is accepted |
| G1 adapter lifecycle DI closeout acceptance | Human acceptance of `#78` disposition in current review thread | `b71ac809` | Closeout accepted: after record merge, post required closeout comment and close `#78`; begin `#79` service lifecycle DI design/triage only after #78 is closed; no implementation or `ready-for-agent` movement is authorized |
| G2 service lifecycle DI design/triage | Issue `#78` closed state and current-head service scan | `9be035fd` | #79 can begin design/triage only: scan recorded 152 service files, 104 broad heuristic hits, 4 `_instance = None` files, 16 service getter files, one provider/app-state pattern, and one completed route-level DI pilot; next step is candidate classification/pilot authorization, not implementation |
| G2.1 service lifecycle DI candidate classification | Corrected module singleton scan and GitNexus impact comparison | `ecc39139` | 21 module-level singleton-variable files classified; `email_service.py` selected as first future pilot candidate with `EmailService` LOW impact and file-disambiguated `get_email_service` MEDIUM impact; source edits remain locked behind separate G2.2 implementation authorization |
| G2.2 email service DI authorization | `email_service.py` implementation authorization | `35e9b2b3d` | PR `#141` merged; future source lane was authorized only for `email_service.py`, six `notification.py` consumers, focused tests, report, and task card |
| G2.3 email service DI implementation | First service lifecycle DI source pilot | `20657e6e` | PR `#142` merged after human approval; `email_service.py` now provides app.state dependency provider, six `notification.py` email routes inject `EmailService`, focused tests passed, GitHub contract/mainline checks passed, and `email_notification_service.py` remains untouched |
| G2.4 service lifecycle steward retrospective | First-pilot evidence review and second-candidate selection | `f149534f` | PR `#144` merged; steward-tree operating lessons recorded; `announcement_service.py` selected over `watchlist_service.py` as next authorization candidate, with source edits still locked behind a separate authorization packet |
| G2.5 announcement service DI authorization | `announcement_service.py` implementation authorization | `e9d674c0` | PR `#145` merged; future source lane was authorized only for `announcement_service.py`, announcement routes, focused tests, implementation report, and task card |
| G2.6 announcement service DI implementation | Second service lifecycle DI source pilot | `517f47cb` | PR `#146` merged after human approval; `announcement_service.py` now provides app.state dependency provider, 11 announcement route handlers inject `AnnouncementService`, focused tests passed, and watchlist/adapter/data-layer files remain untouched |
| G2.7 announcement service DI closeout | Merged implementation closeout | `112487d9` | PR `#147` merged; `announcement_service.py` is recorded as merged-and-reviewed, and third-candidate work may only begin as a new selection/authorization packet |
| G2.8 third service DI candidate selection | Post-closeout candidate split decision | `ccc4982c` | PR `#148` merged; selection accepted: recommend only a route-surface `watchlist_service.py` authorization packet and keep watchlist adapter/data-layer helper callers out of scope unless a separate adapter-aware packet is accepted |
| G2.9 watchlist service DI authorization | Route-surface-only `watchlist_service.py` implementation authorization | `bddb764c` | PR `#149` merged; future source lane authorized only `watchlist_service.py`, seven `watchlist.py` route handlers, focused tests, implementation report, future task card, and steward-tree evidence; adapter/data helper migration remains out of scope |
| G2.10 watchlist service DI implementation | Third route-surface service lifecycle DI source pilot | `b14ef842` | PR `#150` merged after human approval; `watchlist_service.py` now exposes an app-state provider dependency, seven `watchlist.py` group route handlers inject `WatchlistService`, focused tests and GitHub checks passed, and watchlist adapter/data helper files remain untouched |
| G2.11 watchlist service DI closeout | Merged implementation closeout | `b14ef842` | Closeout recorded: `watchlist_service.py` is recorded as merged-and-reviewed; next service lifecycle DI movement requires a separate fourth-candidate, adapter-aware cleanup, or pause/resume decision packet |

## Update Protocol

When a branch is implemented or a gate changes, update these artifacts in this
order:

Continuous Task C1 is the steward freshness loop. It may run without code edits
and covers: rechecking branch/HEAD, labeling affected rows as current-head,
commit-scoped, or stale-aware, checking whether GitHub/OpenSpec states changed,
and recording whether a contradiction requires reconciliation.

1. Update the relevant `openspec/changes/<change-id>/tasks.md` checklist.
2. Add or update the verification report under `docs/reports/quality/`.
3. Update this steward tree row with state, evidence artifact, HEAD, and next gate.
4. Check for evidence contradictions before updating baseline language:
   - If artifacts were measured at different HEADs, mark the older artifact as stale-aware rather than treating the pair as a live conflict.
   - If artifacts were measured at the same HEAD but disagree, mark affected rows as `contradiction-unresolved`.
   - Create a targeted reconciliation task or report before unblocking any dependent branch.
5. Update `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` Evidence Artifact Index if the evidence changes the architecture baseline.
6. Run `openspec validate <change-id> --strict` for affected OpenSpec changes.
7. Run markdown governance and `git diff --check` for edited docs.
8. Only after accepted completion, archive the OpenSpec branch through the normal OpenSpec archive workflow.

## Current Next Gates

| Priority | Gate | Owner lane | Status |
|---|---|---|---|
| P0 | Decide push/merge path for `00101699b` | Human/OpenSpec governance | Implementation reviewed as `APPROVE_WITH_NOTES`; commit exists only in isolated worktree branch `sequence-route-contract-unblock` |
| P1 | Track non-blocking review notes | Future governance lanes | `data_source_config.py` response-module runtime dependency mix, `monitoring_watchlists.py` lifecycle/concurrency concern, and wide unblock commit scope are follow-up candidates, not blockers |
| P0 | Keep broad architecture refactor frozen until runtime import chain is healthy | Runtime unblock lane | Runtime import chain healthy; broad refactor still frozen behind later gates |
| P1 | Execute runtime unblock only after approval | `sequence-backend-architecture-unblocks` | Complete; evidence report recorded |
| P1 | Reconcile schema shim closure after runtime unblock | `sequence-backend-architecture-unblocks` then future schema branch | Complete; next gate is route/OpenAPI evidence refresh and later shim-retirement decision |
| P1 | Refresh route/OpenAPI/probe evidence after runtime unblock | `sequence-backend-architecture-unblocks` | Complete; next gate is control-plane route governance classification, including `GET /metrics` duplicate path/method |
| P1 | Keep Core Batch 2 blocked until Task 3.2 and #83 evidence gates are explicit | Core split lane | Blocked |
| P2 | Review G2.24 broad service seam design packet | Future service seam lane | PR `#163` merged; G2.24 is review-ready and selects a future G2.25 market-data provider design packet before any market/data/strategy source edits |
| P2 | Keep CSRF and miniQMT tracks decision/evidence-only | Decision and external evidence lanes | No implementation branch |

## Deferred Items

These CODEBASE-MAP findings remain valid planning inputs, but they belong to
later remediation rounds and must not be folded into
`sequence-backend-architecture-unblocks`:

- F821 cleanup outside the current unblock branch.
- Coverage configuration conflict review.
- Frontend `.bak` file cleanup.
- `part*.py` / split-file cleanup.
- `src/README.md` freshness review.
- `views/` and `composables/` frontend classification follow-up.

## Steward Review Checklist

- [ ] The master execution plan remains the total control plan and is not
      replaced by this file.
- [ ] Each execution report maps to exactly one primary steward branch.
- [ ] Every OpenSpec branch has a parent source, evidence source, state, and next
      gate.
- [ ] Runtime unblock tasks are separated from broad architecture refactors.
- [ ] Schema directory retirement is blocked until compatibility exports and
      tests are proven.
- [ ] Singleton lifecycle work starts from classification and interface/test-double
      strategy, not from a random pilot.
- [ ] Resolved error-contract migration is not reopened without current-head
      contradiction.
- [ ] External miniQMT evidence remains external and non-backend-blocking.
