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
│   │   `.planning/codebase/generated/broad-service-seam-design-2026-05-23.json`,
│   │   `backend-market-data-provider-design-2026-05-23.md`,
│   │   `.planning/codebase/generated/market-data-provider-design-2026-05-23.json`,
│   │   `backend-market-data-service-v2-route-provider-implementation-authorization-2026-05-23.md`,
│   │   `.planning/codebase/generated/market-data-service-v2-route-provider-implementation-authorization-2026-05-23.json`,
│   │   `backend-market-data-service-v2-route-provider-implementation-2026-05-23.md`,
│   │   `backend-market-data-service-v2-route-provider-closeout-2026-05-23.md`,
│   │   `.planning/codebase/generated/market-data-service-v2-route-provider-closeout-2026-05-23.json`,
│   │   `backend-service-lifecycle-di-candidate-refresh-after-market-data-v2-2026-05-23.md`,
│   │   `.planning/codebase/generated/service-lifecycle-di-candidate-refresh-after-market-data-v2-2026-05-23.json`,
│   │   `backend-market-data-service-v2-compatibility-getter-consumer-matrix-2026-05-23.md`,
│   │   `.planning/codebase/generated/market-data-service-v2-compatibility-getter-consumer-matrix-2026-05-23.json`
│   ├── State: service-lifecycle-next-lane-selection-prepared-for-review
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
│   │                 market-data provider design packet before any source edit;
│   │                 PR `#164` merged at
│   │                 `f97ca070853a77afc80c226d53948e805ba33c8e`; G2.25 now
│   │                 records that `market_v2.py` has 13 direct
│   │                 `get_market_data_service_v2()` route calls,
│   │                 `dashboard_data_source.py` has 2 non-route helper calls,
│   │                 `market/market_data_request.py` already uses
│   │                 `Depends(get_market_data_service)` in 7 route handlers,
│   │                 and the `app.services.__init__` integrated-services
│   │                 accessor must not be conflated with the package getter;
│   │                 G2.25 rejects service consolidation and selects a future
│   │                 G2.26 `MarketDataServiceV2` route-provider implementation
│   │                 authorization packet before source edits; PR `#165`
│   │                 merged at
│   │                 `46507955f77a3166491bd4510c56ef034b6ff1cb`; G2.26 now
│   │                 records exact future write scope for
│   │                 `market_data_service_v2.py`, `market_v2.py`, focused
│   │                 lifecycle tests, implementation evidence, and a future
│   │                 task card, while explicitly excluding
│   │                 `dashboard_data_source.py`, `market_data_adapter.py`, the
│   │                 `market_data_service` package, services `__init__`,
│   │                 service consolidation, and route/OpenAPI behavior changes;
│   │                 no source edit is authorized in this packet; PR `#166`
│   │                 merged at
│   │                 `76a1e271fa602e692553acf2760f100ca88030aa`; G2.27 now
│   │                 implements the approved route-provider seam by adding an
│   │                 app-state provider to `market_data_service_v2.py` and
│   │                 injecting `MarketDataServiceV2` into the 13 authorized
│   │                 `market_v2.py` route handlers while preserving the
│   │                 compatibility getter and leaving the 2
│   │                 `dashboard_data_source.py` helper callers unchanged; PR
│   │                 `#167` merged at
│   │                 `8120f01a7022472b604f525ac9af2a517150c39b`; G2.28 now
│   │                 records the post-merge closeout, confirms `market_v2.py`
│   │                 route direct getter calls remain `0`, 13 route handlers
│   │                 use the provider dependency, dashboard helper callers
│   │                 remain `2`, and OpenAPI stays at paths=`500`,
│   │                 `/api/v2/market` paths=`13`, duplicate operationIds=`0`;
│   │                 PR `#168` merged at
│   │                 `e79029ff99e8c3ee674d07efd8b1601e7deb32e0`; G2.29 now
│   │                 refreshes current-head service lifecycle candidates,
│   │                 records 152 service files, 20 narrow candidate files, 5
│   │                 completed route-surface DI seams, and selects only a
│   │                 future G2.30 `MarketDataServiceV2` compatibility getter /
│   │                 dashboard helper consumer matrix packet before any source
│   │                 edit; PR `#169` merged at
│   │                 `04e2f7038386dbea1b8fc8bdcb24dd91dc7e9bb1`; G2.30 now
│   │                 classifies the `MarketDataServiceV2` compatibility getter
│   │                 as active dashboard-helper compatibility surface, keeps
│   │                 route direct getter calls at `0`, records 2 dashboard
│   │                 helper calls, and selects only a future G2.31 dashboard
│   │                 helper provider migration authorization packet before any
│   │                 source edit; PR `#170` merged at
│   │                 `f87cb60afd399e16db0142c3eaaa7ab24c3a1ab1`; G2.31 now
│   │                 authorizes only a future dashboard helper provider
│   │                 migration branch, scoped to provider-fed
│   │                 `RealBusinessDataSource`, `dashboard.py` dependency use,
│   │                 startup prewarm service passing, and focused tests, while
│   │                 keeping `get_market_data_service_v2()` public and active;
│   │                 PR `#171` merged at
│   │                 `0b838356e51e11f2ad27f9d3c898583611520622`; G2.32 now
│   │                 implements the approved dashboard helper provider
│   │                 migration: `dashboard_data_source.py` helper direct getter
│   │                 calls are `0`, `dashboard.py` route-body
│   │                 `get_data_source()` calls are `0`, startup prewarm passes
│   │                 the installed app-state service, and
│   │                 `get_market_data_service_v2()` remains public fallback;
│   │                 PR `#172` merged at
│   │                 `40a396fabcbafcc527d4d15af1eb81034a645d87`; G2.33 now
│   │                 refreshes service lifecycle DI candidates at current
│   │                 HEAD, confirms candidate counts remain `152` service
│   │                 files and `20` candidate files, records
│   │                 `MarketDataServiceV2` direct route/helper calls at `0`,
│   │                 and identifies only a future decision-only TDX dashboard
│   │                 helper provider authorization packet before source edits;
│   │                 PR `#173` merged at
│   │                 `78dafc38546ca9d45a1ed4bb3e5c2db24b9978b1`; G2.34 now
│   │                 records the TDX dashboard helper provider authorization
│   │                 boundary: `dashboard_data_source.py` has 2 direct
│   │                 `get_tdx_service()` helper calls, `tdx.py` already uses
│   │                 FastAPI dependency wiring, and any implementation must be
│   │                 a later G2.35 branch after human review; G2.35 now
│   │                 implements the approved TDX dashboard helper provider
│   │                 migration: `dashboard_data_source.py` direct
│   │                 `get_tdx_service()` helper calls are `0`,
│   │                 `get_tdx_service()` remains public fallback, startup
│   │                 prewarm passes the installed app-state TDX service, and
│   │                 focused authorized tests report `133 passed`; PR `#175`
│   │                 merged at
│   │                 `efbc02db5100a4927476a4c8eb2c4cd4533a352f`; G2.36
│   │                 closeout merged by PR `#176` at
│   │                 `6e940a7a5596b4256f63fec888c589777456d36a`; G2.37 now
│   │                 refreshes current-head service lifecycle DI candidates:
│   │                 scans `152` service files and `18` candidate/signal
│   │                 files, confirms direct dashboard helper TDX getter calls
│   │                 remain `0`, records private `_get_tdx_service()` helper
│   │                 calls at `3` and `/api/tdx` `Depends(get_tdx_service)`
│   │                 sites at `5`, keeps source edits locked, and selects only
│   │                 a decision-only G2.38 TDX route dependency consumer
│   │                 matrix before any compatibility getter cleanup; G2.37
│   │                 merged by PR `#177` at
│   │                 `f0f761ffb7d848b8e9a8e5a492ab82f763870086`; G2.38 now
│   │                 records `/api/v1/tdx` as five active public route
│   │                 dependency consumers, distinguishes `/api/ml/tdx` as
│   │                 unrelated local `TdxDataService()` usage, and keeps
│   │                 `get_tdx_service()` active with no source edits; G2.38
│   │                 merged by PR `#178` at
│   │                 `30c78a22dce5879396dfd5c7760cc61161377528`; G2.39
│   │                 authorized only a future `/api/v1/tdx` route-provider
│   │                 migration scope: `tdx_service.py`, `api/tdx.py`, focused
│   │                 lifecycle DI tests, implementation evidence, and a future
│   │                 task card; `get_tdx_service()` remains active; G2.40 now
│   │                 implements that scope by adding
│   │                 `TDX_SERVICE_STATE_KEY` and
│   │                 `get_tdx_service_dependency`, converting the five
│   │                 `/api/v1/tdx` dependencies to the provider, keeping
│   │                 OpenAPI paths at `500`, duplicate operation IDs at `0`,
│   │                 and focused lifecycle DI tests at `4 passed`; G2.40
│   │                 merged by PR `#180` at
│   │                 `86b0ec43c037729b28df51c40484196175c96c6e`; G2.41 now
│   │                 records the post-merge closeout: PR `#180` is `MERGED`,
│   │                 focused TDX lifecycle DI tests are `4 passed`, route
│   │                 dependency counts are legacy=`0` and provider=`5`, and
│   │                 OpenAPI remains paths=`500` with duplicate operation
│   │                 IDs=`0`; G2.41 merged by PR `#181` at
│   │                 `41b0d4db7f2c644cea9abf1ddd4112e695325dcc`; G2.42
│   │                 records the current-head candidate refresh: service files
│   │                 scanned=`152`, narrow candidate/signal files=`21`,
│   │                 completed route-provider seams=`7`, TDX legacy route
│   │                 dependency sites=`0`, TDX provider sites=`5`, OpenAPI
│   │                 paths=`500`, and duplicate operation IDs=`0`; PR `#182`
│   │                 merged at
│   │                 `f7c6fdf5fd57cff14ef6d11f1d18fd6591a22dc5`; G2.43 now
│   │                 records candidate usefulness and ownership triage:
│   │                 `AdvancedAnalysisService` is an active route class
│   │                 dependency with a definition-only compatibility getter,
│   │                 `WencaiService` is an active DB/session-backed direct
│   │                 constructor service, `get_market_data_service` remains an
│   │                 active route dependency, and `UnifiedDataService` remains
│   │                 a broad data seam; no implementation target is authorized;
│   │                 PR `#183` merged at
│   │                 `1e137abb2a32b795c403a8a168a174ad86b7f693`; G2.44 now
│   │                 records the future `AdvancedAnalysisService` route-provider
│   │                 migration authorization boundary, including allowed future
│   │                 files, pre-edit GitNexus gates, route dependency count
│   │                 guards, configured app/OpenAPI smoke requirement, and
│   │                 compatibility preservation for
│   │                 `get_advanced_analysis_service()`; PR `#184` merged at
│   │                 `22b617733e29c9a441e88cb1da2ce0a5d8be98cc`; G2.45 now
│   │                 implements the provider seam, preserves the compatibility
│   │                 getter and module singleton, converts `14`
│   │                 `advanced_analysis_api.py` service dependencies to
│   │                 `get_advanced_analysis_service_dependency`, and keeps
│   │                 OpenAPI paths=`500` with duplicate operation IDs=`0`;
│   │                 PR `#185` merged at
│   │                 `059638b573c6f2586537973e2a4b396f0ce156d7`; G2.46 now
│   │                 records current-head closeout and candidate refresh:
│   │                 `AdvancedAnalysisService` route class dependency sites=`0`,
│   │                 provider sites=`14`, direct compatibility getter route
│   │                 calls=`0`, focused test result=`4 passed`, OpenAPI
│   │                 paths=`500`, duplicate operation IDs=`0`, completed
│   │                 provider modules=`8`, route provider dependency
│   │                 files=`11`, and route provider dependency sites=`72`;
│   │                 no next implementation target is authorized; PR `#186`
│   │                 merged at
│   │                 `e09e6db4a6a85dc392c20a737e729bb6f123804d`; G2.47 now
│   │                 records current-head candidate selection: service files
│   │                 scanned=`152`, API files scanned=`219`, provider
│   │                 modules=`8`, route provider dependency sites=`72`,
│   │                 route class dependency sites=`0`, route getter
│   │                 dependency sites=`277`, and selected
│   │                 `get_market_data_service` only as the next consumer
│   │                 matrix / authorization candidate packet; broad or
│   │                 external-client seams remain excluded; PR `#188` merged
│   │                 at
│   │                 `0dce9ca97cd043f898039176394eb5076c353cf5`; G2.48 now
│   │                 records the exact `get_market_data_service` route
│   │                 dependency consumer matrix: seven `/api/v1/market`
│   │                 route handlers in `market/market_data_request.py`,
│   │                 package-level compatibility getter retained,
│   │                 `market_data_adapter.py` excluded, configured OpenAPI
│   │                 smoke routes=`548`, paths=`500`, duplicate operation
│   │                 IDs=`0`, and `test_market_api_integration.py`
│   │                 result=`18 passed`; PR `#189` merged at
│   │                 `7daf74ce0c3210defc2ad283583a335037daa500`; G2.49 now
│   │                 implements the provider seam, preserves
│   │                 `get_market_data_service()`, converts exactly seven
│   │                 `/api/v1/market` route dependencies to
│   │                 `get_market_data_service_dependency`, leaves
│   │                 `market_data_adapter.py` and
│   │                 `web/backend/app/services/__init__.py` unchanged, and
│   │                 records focused lifecycle tests=`5 passed`,
│   │                 market integration tests=`18 passed`, route guard
│   │                 old=`0` / new=`7`, OpenAPI paths=`500`, duplicate
│   │                 operation IDs=`0`; PR `#190` merged at
│   │                 `33163197b59893372d5d1d68af53acbfbbb0f613`; G2.50
│   │                 now records current-head closeout: legacy market route
│   │                 dependency sites=`0`, provider sites=`7`, provider
│   │                 import present=`true`, focused lifecycle tests=`5
│   │                 passed`, market integration tests=`18 passed`, OpenAPI
│   │                 paths=`500`, duplicate operation IDs=`0`, route
│   │                 provider dependency files=`11`, and route provider
│   │                 dependency sites=`79`; PR `#191` merged at
│   │                 `047f483dd70a5234ca3a128342511a56779194d3`; G2.51
│   │                 now records current-head candidate refresh: service files
│   │                 scanned=`152`, API files scanned=`219`, provider
│   │                 functions=`8`, route provider dependency sites=`79`,
│   │                 route getter dependency sites=`270`, OpenAPI paths=`500`,
│   │                 duplicate operation IDs=`0`, and no ordinary
│   │                 route-provider implementation target is selected; PR
│   │                 `#192` merged at
│   │                 `363324bf31a89b797789403c55dbe3ca854bc7d6`; G2.52
│   │                 records `IndicatorRegistry` provider design: two
│   │                 same-name registry getters exist, flat API registry direct
│   │                 callers=`3`, package registry production callers=`3`,
│   │                 OpenAPI paths=`500`, duplicate operation IDs=`0`, and no
│   │                 source implementation target is authorized; PR `#193`
│   │                 merged at
│   │                 `ec3dc2920886eb24e963a33488bd2e945e98e6c9`; G2.53
│   │                 records the flat API registry consumer matrix: selected
│   │                 indicator cache routes=`6`, direct registry route
│   │                 consumers=`2`, service constructor consumer=`1`,
│   │                 OpenAPI paths=`500`, duplicate operation IDs=`0`, and
│   │                 collect-only checks=`16+112+29`; PR `#194` merged at
│   │                 `71510bb02a845ec529c8c04f3a7288ca86b87b9c`; G2.54
│   │                 implements the flat API registry route provider:
│   │                 provider surface=`3`, converted route handlers=`2`,
│   │                 compatibility getter preserved, package registry and
│   │                 `IndicatorCalculator` excluded, focused TDD=`2 passed`,
│   │                 OpenAPI paths=`500`, duplicate operation IDs=`0`; PR
│   │                 `#195` merged at
│   │                 `5b12a3c08cac3558c56af615ff14c05913d96f72`; G2.55 now
│   │                 records closeout evidence: route direct getter refs=`0`,
│   │                 provider dependency route sites=`2`, focused tests=`2+1`
│   │                 passed, OpenAPI paths=`500`, duplicate operation IDs=`0`,
│   │                 GitNexus index stale for new provider symbols; PR `#196`
│   │                 merged at
│   │                 `1fc4a4c7a86cf464dedb742612c052b911d4ef5f`; G2.56 now
│   │                 records current-head candidate refresh after the
│   │                 `IndicatorRegistry` provider: service files scanned=`152`,
│   │                 API files scanned=`219`, provider state keys=`10`,
│   │                 provider functions=`20`, provider dependency sites=`81`,
│   │                 route getter dependency sites=`272`, route direct
│   │                 `get_indicator_registry()` refs=`0`, provider dependency
│   │                 route sites=`2`, OpenAPI paths=`500`, duplicate operation
│   │                 IDs=`0`, and no source implementation target is authorized;
│   │                 GitNexus refresh failed in the linked worktree with
│   │                 `ENOTDIR .git/info`, so static current-head scans and
│   │                 runtime/OpenAPI smoke are authoritative for this packet;
│   │                 PR `#197` merged at
│   │                 `3469a43855ef81d238e1a92745126fcb321b1af7`; G2.57 now
│   │                 records non-linked GitNexus refresh success at the same
│   │                 HEAD: `.git` kind=`directory`, analyze exit=`0`,
│   │                 nodes=`62623`, edges=`145799`, flows=`300`, repo
│   │                 `g2-57-gitnexus-index-checkout` state=`ready`, and
│   │                 `get_indicator_registry_dependency` plus
│   │                 `install_indicator_registry` resolve in the refreshed graph;
│   │                 upstream impact for `get_indicator_registry_dependency`
│   │                 is `LOW` with impacted count=`0`; route dependency counts
│   │                 still require static FastAPI `Depends(...)` scans because
│   │                 the refreshed graph does not model those route sites as
│   │                 incoming call edges; PR `#198` merged at
│   │                 `5dbb0ca0c387dafb313e9b5f2674f3023da65962`; G2.58 now
│   │                 records next-lane selection at the same HEAD: ordinary
│   │                 provider dependency rows are implemented/closed except
│   │                 `get_data_source_dependency`, which is already
│   │                 provider-shaped with `3` dashboard route sites; the next
│   │                 design-only seam is `get_data_source_factory`, with `17`
│   │                 direct API call sites across `9` files and refreshed
│   │                 GitNexus upstream impact `CRITICAL` (`22` impacted, `21`
│   │                 direct, `15` processes, `3` modules); PR `#199` merged at
│   │                 `1880f0d1395e7c5594b70f3ba40478cff24f2d3a`; G2.59 now
│   │                 records a dedicated authorization packet for
│   │                 `get_data_source_factory`: non-linked GitNexus analyze
│   │                 exit=`0`, nodes=`62624`, edges=`145803`, flows=`300`,
│   │                 symbol lines=`294-300`, static API scan remains `17`
│   │                 direct calls across `9` files, and upstream impact remains
│   │                 `CRITICAL` (`22` impacted, `21` direct, `15` processes,
│   │                 `3` modules); no source implementation is authorized by
│   │                 G2.59; PR `#200` merged at
│   │                 `265f38e53bddfa3a925f14cfbc5080b00dce26e6`; G2.60 now
│   │                 records the consumer matrix and future implementation
│   │                 boundary: static API scan still reports `17` direct calls
│   │                 across `9` files, non-linked GitNexus analyze exit=`0`,
│   │                 nodes=`62628`, edges=`145797`, flows=`300`, and upstream
│   │                 impact remains `CRITICAL`; the selected next source batch
│   │                 is G2.61a provider-seam-only with `0` route calls migrated
│   │                 and all route/API consumer rewrites locked for later
│   │                 packets; PR `#201` merged at
│   │                 `ae6ba4e43b1470b524110fe506929df675bd8b93`; G2.61a now
│   │                 implements that provider seam only: adds
│   │                 `DATA_SOURCE_FACTORY_STATE_KEY`,
│   │                 `install_data_source_factory`, and
│   │                 `get_data_source_factory_dependency`, preserves
│   │                 `get_data_source_factory()` plus `_global_factory`, keeps
│   │                 route direct calls=`17`, route dependency refs=`0`, TDD
│   │                 red=`3 failed, 1 passed`, focused green=`4 passed`,
│   │                 existing factory tests=`38 passed`, app/OpenAPI smoke
│   │                 routes=`548`, paths=`500`, duplicate operation IDs=`0`;
│   │                 PR `#202` merged at
│   │                 `0aadb27801c86e97e65ffdb4426276e1bd14c352`; G2.61a
│   │                 closeout now records current-head provider evidence:
│   │                 focused tests=`4 passed`, existing factory tests=`38`
│   │                 passed, runtime fallback=`1 passed`, route direct calls
│   │                 remain `17`, provider dependency API refs remain `0`,
│   │                 OpenAPI paths=`500`, duplicate operation IDs=`0`, and
│   │                 refreshed GitNexus resolves both new provider symbols with
│   │                 LOW upstream impact and `0` callers
│   │                 PR `#203` merged at
│   │                 `ee2c74f3c8e1c4f690d2a1737db29c97c39a54d2`; G2.61b now
│   │                 records the first route-migration authorization packet:
│   │                 `data_quality.py` has direct factory calls at lines `58`
│   │                 and `369`, package `__init__.py` exports the legacy getter
│   │                 but not the provider dependency, focused provider tests
│   │                 pass `4`, existing factory tests pass `38`,
│   │                 data-quality mock configuration tests pass `2`, and
│   │                 app/OpenAPI smoke remains routes=`548`, paths=`500`,
│   │                 duplicate operation IDs=`0`
│   │                 PR `#204` merged at
│   │                 `52a2aaa57150db834bcef3a526a4b78e37ac438a`; G2.61c now
│   │                 implements the approved first route migration:
│   │                 `data_quality.py` direct calls move from `2` to `0`,
│   │                 total API direct calls move from `17` to `15`, package
│   │                 `__init__.py` re-exports
│   │                 `get_data_source_factory_dependency`, focused route tests
│   │                 pass `4`, provider tests pass `4`, existing factory tests
│   │                 pass `38`, and app/OpenAPI smoke remains routes=`548`,
│   │                 paths=`500`, duplicate operation IDs=`0`
│   │                 PR `#205` merged at
│   │                 `b9d0bb31a72d362dc67a38dcd719578de56af739`; G2.61c
│   │                 closeout confirms current-head stability: data-quality
│   │                 focused tests=`4 passed`, provider tests=`4 passed`,
│   │                 factory tests=`38 passed`, route direct calls remain `15`,
│   │                 `data_quality.py` direct refs remain `0`, OpenAPI paths
│   │                 remain `500`, duplicate operation IDs remain `0`, and
│   │                 refreshed GitNexus at `b9d0bb31a` keeps edited symbols at
│   │                 LOW upstream impact with `0` callers
│   │                 PR `#206` merged at
│   │                 `fcc438de0965f80af7d485525fb494511976595b`; G2.62 now
│   │                 selects the next one-call consumer: `financial.py` has one
│   │                 direct call at line `69` in one route function, while
│   │                 `market.py` has one direct call but a broader four-route
│   │                 file surface; no source edit is included
│   │                 PR `#207` merged at
│   │                 `7c1b8fce44b3931c44ac5398e12f5715a28833e3`; G2.63 now
│   │                 implements the approved `financial.py` migration:
│   │                 `financial.py` direct calls move from `1` to `0`, total
│   │                 API direct calls move from `15` to `14`, focused health
│   │                 route conflict tests pass `113`, provider tests pass `4`,
│   │                 and app/OpenAPI smoke remains routes=`548`, paths=`500`,
│   │                 duplicate operation IDs=`0`
│   │                 PR `#208` merged at
│   │                 `229cd7fe0a21cb9bf7b9079d07e9551baaf0a4c7`; G2.63
│   │                 closeout confirms current-head stability: health route
│   │                 conflict tests=`113 passed`, provider tests=`4 passed`,
│   │                 route direct calls remain `14`, `financial.py` direct refs
│   │                 remain `0`, OpenAPI paths remain `500`, duplicate
│   │                 operation IDs remain `0`, and refreshed GitNexus at
│   │                 `229cd7fe0` reports `financial.py` LOW/1 and provider
│   │                 dependency LOW/0
│   │                 PR `#209` merged at
│   │                 `cfb98f079c488c7e33c270e44342408a0e10db44`; G2.64 now
│   │                 authorizes the next route candidate: `market.py` has one
│   │                 direct call at line `98` in `get_market_overview`, the file
│   │                 has four route handlers, current direct API calls remain
│   │                 `14`, provider dependency refs remain `5`, health route
│   │                 conflict tests pass `113`, provider tests pass `4`,
│   │                 OpenAPI remains paths=`500` with duplicate operation IDs=`0`,
│   │                 and candidate style baseline records existing `market.py`
│   │                 E701/black debt that a future same-file implementation must
│   │                 normalize
│   │                 PR `#210` merged at
│   │                 `20a7b67f1898506586e7858840d0ae058461fe93`; G2.65 now
│   │                 implements the approved `market.py` migration:
│   │                 `market.py` direct calls move from `1` to `0`, total API
│   │                 direct calls move from `14` to `13`, health route conflict
│   │                 tests pass `114`, provider tests pass `4`, touched-file
│   │                 ruff/black pass, and app/OpenAPI smoke remains routes=`548`,
│   │                 paths=`500`, duplicate operation IDs=`0`
│   │                 PR `#211` merged at
│   │                 `277fdd412b2bbf68b64c5186fee943dc50080480`; G2.65
│   │                 closeout confirms current-head stability: health route
│   │                 conflict tests=`114 passed`, provider tests=`4 passed`,
│   │                 route direct calls remain `13`, `market.py` direct refs
│   │                 remain `0`, OpenAPI paths remain `500`, duplicate
│   │                 operation IDs remain `0`, and refreshed GitNexus at
│   │                 `277fdd412` reports `market.py` LOW/1 and provider
│   │                 dependency LOW/0
│   ├── G2.66 DataSourceFactory route candidate authorization
│   │   ├── State: ready for review; PR `#213` candidate packet
│   │   ├── Evidence: `backend-data-source-factory-route-candidate-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `d30f2c12d642fbc613689d85b39697999805bbb8`
│   │   ├── Result: compares the remaining six route/API consumers and selects
│   │   │          `web/backend/app/api/data/margin.py` for a future G2.67
│   │   │          implementation because it has LOW/1 GitNexus impact, ruff
│   │   │          clean, black unchanged, three route handlers, and three direct
│   │   │          factory refs that can move from `3` to `0`
│   │   └── Boundary: authorization-only; no source edit, route contract edit,
│   │                compatibility getter removal, frontend edit, PM2/runtime
│   │                gate, or issue-label change is authorized
│   ├── G2.67 Margin DataSourceFactory route migration
│   │   ├── State: ready for review; PR `#214` implementation packet
│   │   ├── Evidence: `backend-data-source-factory-margin-route-migration-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `7b817debccfba1c82efc5a9c71f23f0b775434c0`
│   │   ├── Result: migrates `get_margin_account_info`,
│   │   │          `get_margin_detail_sse`, and `get_margin_detail_szse` from
│   │   │          direct `get_data_source_factory()` calls to
│   │   │          `Depends(get_data_source_factory_dependency)`; total route/API
│   │   │          direct refs move `13 -> 10`, `margin.py` direct refs move
│   │   │          `3 -> 0`, health route conflict tests move to `115 passed`,
│   │   │          provider tests remain `4 passed`, OpenAPI paths remain `500`,
│   │   │          and duplicate operation IDs remain `0`
│   │   └── Boundary: no route path, response model, response shape, OpenAPI,
│   │                frontend, runtime/PM2, OpenSpec, issue-label, or other
│   │                DataSourceFactory consumer change
│   ├── G2.67 Closeout / current-head refresh
│   │   ├── State: ready for review; PR `#215` closeout packet
│   │   ├── Evidence: `backend-data-source-factory-margin-route-migration-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `3f1a737a5cc62f0424951931581e410d1dd14975`
│   │   ├── Result: confirms PR `#214` merged, health route conflict tests
│   │   │          remain `115 passed`, provider tests remain `4 passed`,
│   │   │          route direct refs remain `10`, `margin.py` direct refs remain
│   │   │          `0`, OpenAPI paths remain `500`, duplicate operation IDs remain
│   │   │          `0`, and GitNexus reports `margin.py` LOW/1 plus provider
│   │   │          package LOW/0
│   │   └── Boundary: closeout-only; no source edit or next consumer selection
│   ├── G2.68 DataSourceFactory route candidate authorization
│   │   ├── State: accepted; PR `#216` merged at
│   │   │          `a76f6dbdc700738e4d07977ae3808f75b2103fe3`
│   │   ├── Evidence: `backend-data-source-factory-lhb-route-migration-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `d5a0ef78718a070180be0428573530081945c943`
│   │   ├── Result: compares the remaining five route/API consumers and selects
│   │   │          `web/backend/app/api/data/lhb.py` for future G2.69 because it
│   │   │          has LOW/1 GitNexus impact, ruff clean, two route handlers, and
│   │   │          two direct refs that can move from `2` to `0`; same-file black
│   │   │          normalization is allowed only inside the future authorized
│   │   │          implementation if black reformats `lhb.py`
│   │   └── Boundary: authorization-only; no source edit, route contract edit,
│   │                compatibility getter removal, frontend edit, PM2/runtime
│   │                gate, or issue-label change is authorized
│   ├── G2.69 LHB DataSourceFactory route migration
│   │   ├── State: accepted; PR `#217` merged at
│   │   │          `d25803e93494b7115795a1922a84386b9daffb27`
│   │   ├── Evidence: `backend-data-source-factory-lhb-route-migration-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `a76f6dbdc700738e4d07977ae3808f75b2103fe3`
│   │   ├── Result: migrates `get_dragon_tiger_detail` and
│   │   │          `get_dragon_tiger_institution_stats` from direct
│   │   │          `get_data_source_factory()` calls to
│   │   │          `Depends(get_data_source_factory_dependency)`; total route/API
│   │   │          direct refs move `10 -> 8`, `lhb.py` direct refs move
│   │   │          `2 -> 0`, health route conflict tests move to `116 passed`,
│   │   │          provider tests remain `4 passed`, OpenAPI paths remain `500`,
│   │   │          and duplicate operation IDs remain `0`
│   │   └── Boundary: no route path, response model, response shape, OpenAPI,
│   │                frontend, runtime/PM2, OpenSpec, issue-label, compatibility
│   │                getter deletion, or other DataSourceFactory consumer change
│   ├── G2.69 Closeout / current-head refresh
│   │   ├── State: accepted; PR `#218` merged at
│   │   │          `2670dba0661d9744372e834035027ac4de106fd0`
│   │   ├── Evidence: `backend-data-source-factory-lhb-route-migration-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `d25803e93494b7115795a1922a84386b9daffb27`
│   │   ├── Result: confirms PR `#217` merged, health route conflict tests
│   │   │          remain `116 passed`, provider tests remain `4 passed`,
│   │   │          route direct refs remain `8`, `lhb.py` direct refs remain
│   │   │          `0`, OpenAPI paths remain `500`, duplicate operation IDs
│   │   │          remain `0`, and GitNexus reports `lhb.py` LOW/1
│   │   └── Boundary: closeout-only; no source edit or next consumer selection
│   ├── G2.70 DataSourceFactory route candidate authorization
│   │   ├── State: accepted; PR `#219` merged at
│   │   │          `9060b455b7559ce21bc6f27975cce058be52cb96`
│   │   ├── Evidence: `backend-data-source-factory-market-data-request-route-migration-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `2670dba0661d9744372e834035027ac4de106fd0`
│   │   ├── Result: compares the remaining four route/API consumers and selects
│   │   │          `web/backend/app/api/market/market_data_request.py` for future
│   │   │          G2.71 because it is the only remaining candidate with ruff
│   │   │          pass, black pass, GitNexus LOW/1, and exactly two direct refs
│   │   │          that can move from `2` to `0`; expected total direct refs move
│   │   │          `8 -> 6`
│   │   └── Boundary: authorization-only; no source edit, route contract edit,
│   │                compatibility getter removal, frontend edit, PM2/runtime
│   │                gate, OpenSpec change, or issue-label change is authorized
│   ├── G2.71 Market data request DataSourceFactory route migration
│   │   ├── State: accepted; PR `#220` merged at
│   │   │          `7f10db172b99b0d9d85fc740ffb00fa535bd4071`
│   │   ├── Evidence: `backend-data-source-factory-market-data-request-route-migration-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `9060b455b7559ce21bc6f27975cce058be52cb96`
│   │   ├── Result: migrates `get_fund_flow` and `get_market_quotes` from
│   │   │          direct `get_data_source_factory()` calls to
│   │   │          `Depends(get_data_source_factory_dependency)`; total route/API
│   │   │          direct refs move `8 -> 6`,
│   │   │          `market_data_request.py` direct refs move `2 -> 0`, health
│   │   │          route conflict tests move to `117 passed`, provider tests
│   │   │          remain `4 passed`, OpenAPI paths remain `500`, and duplicate
│   │   │          operation IDs remain `0`
│   │   └── Boundary: no route path, response model, response shape, OpenAPI,
│   │                frontend, runtime/PM2, OpenSpec, issue-label, compatibility
│   │                getter deletion, or other DataSourceFactory consumer change
│   ├── G2.71 Closeout / current-head refresh
│   │   ├── State: accepted; PR `#221` merged at
│   │   │          `f4e3db66effa63ce37c94ad0f2b687a606ff8396`
│   │   ├── Evidence: `backend-data-source-factory-market-data-request-route-migration-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `7f10db172b99b0d9d85fc740ffb00fa535bd4071`
│   │   ├── Result: confirms PR `#220` merged, health route conflict tests
│   │   │          remain `117 passed`, provider tests remain `4 passed`,
│   │   │          route direct refs remain `6`, `market_data_request.py`
│   │   │          direct refs remain `0`, OpenAPI paths remain `500`,
│   │   │          duplicate operation IDs remain `0`, and GitNexus reports
│   │   │          `market_data_request.py` LOW/1
│   │   └── Boundary: closeout-only; no source edit or next consumer selection
│   ├── G2.72 DataSourceFactory route candidate authorization
│   │   ├── State: accepted; PR `#222` merged at
│   │   │          `68ff82a9257fb7bee7bbb7aefe4c7a82c4cb76af`
│   │   ├── Evidence: `backend-data-source-factory-kline-route-migration-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `f4e3db66effa63ce37c94ad0f2b687a606ff8396`
│   │   ├── Result: compares the remaining three route/API consumers and selects
│   │   │          `web/backend/app/api/data/kline.py` for future G2.73 because
│   │   │          it has GitNexus LOW/1, four routes, two direct refs, and only
│   │   │          two same-file E701 findings; expected total direct refs move
│   │   │          `6 -> 4`, while `kline.py` direct refs move `2 -> 0`
│   │   └── Boundary: authorization-only; no source edit, route contract edit,
│   │                compatibility getter removal, frontend edit, PM2/runtime
│   │                gate, OpenSpec change, or issue-label change is authorized;
│   │                a future G2.73 may normalize same-file E701/black style in
│   │                `kline.py` only if the implementation diff requires it
│   ├── G2.73 Kline DataSourceFactory route migration
│   │   ├── State: accepted; PR `#223` merged at
│   │   │          `6ece7f1367d3e4c1fcd881bc5596ec37942c79e4`
│   │   ├── Evidence: `backend-data-source-factory-kline-route-migration-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `68ff82a9257fb7bee7bbb7aefe4c7a82c4cb76af`
│   │   ├── Result: migrates `get_daily_kline`, `get_kline`, and
│   │   │          `get_intraday_data` from direct `get_data_source_factory()`
│   │   │          calls to `Depends(get_data_source_factory_dependency)`;
│   │   │          total route/API direct refs move `6 -> 4`, `kline.py` direct
│   │   │          refs move `2 -> 0`, health route conflict tests move to
│   │   │          `118 passed`, provider tests remain `4 passed`, OpenAPI paths
│   │   │          remain `500`, duplicate operation IDs remain `0`, and staged
│   │   │          GitNexus reports low risk / 0 affected processes
│   │   └── Boundary: no route path, response model, response shape, OpenAPI,
│   │                frontend, runtime/PM2, OpenSpec, issue-label, compatibility
│   │                getter deletion, `stocks.py`, `futures.py`, or broad
│   │                formatting cleanup outside `kline.py` and the focused test
│   ├── G2.73 Closeout / current-head refresh
│   │   ├── State: accepted; PR `#224` merged at
│   │   │          `f7d370cd91f3c28a6f11fdbcb42b8241cfd43be6`
│   │   ├── Evidence: `backend-data-source-factory-kline-route-migration-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `6ece7f1367d3e4c1fcd881bc5596ec37942c79e4`
│   │   ├── Result: confirms PR `#223` merged, health route conflict tests
│   │   │          remain `118 passed`, provider tests remain `4 passed`,
│   │   │          route direct refs remain `4`, `kline.py` direct refs remain
│   │   │          `0`, OpenAPI paths remain `500`, duplicate operation IDs
│   │   │          remain `0`, and GitNexus reports `kline.py` LOW/1
│   │   └── Boundary: closeout-only; no source edit or next consumer selection
│   ├── G2.74 DataSourceFactory route candidate authorization
│   │   ├── State: accepted; PR `#225` merged at
│   │   │          `2a04b019965801084822e132c99690f97f8299b5`
│   │   ├── Evidence: `backend-data-source-factory-stocks-route-migration-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `f7d370cd91f3c28a6f11fdbcb42b8241cfd43be6`
│   │   ├── Result: compares the remaining two route/API consumers and selects
│   │   │          `web/backend/app/api/data/stocks.py` for future G2.75 because
│   │   │          it is the only LOW-risk remaining candidate; expected total
│   │   │          direct refs move `4 -> 2`, while `stocks.py` direct refs move
│   │   │          `2 -> 0`; same-file E701/black debt is explicitly scoped
│   │   └── Boundary: authorization-only; no source edit, route contract edit,
│   │                compatibility getter removal, frontend edit, PM2/runtime
│   │                gate, OpenSpec change, or issue-label change is authorized;
│   │                a future G2.75 may normalize same-file E701/black style in
│   │                `stocks.py` only if the implementation diff requires it
│   ├── G2.75 Stocks DataSourceFactory route migration
│   │   ├── State: accepted; PR `#226` merged at
│   │   │          `02518742fb1169ced7f2aa34daaff0dc9dc8b47b`
│   │   ├── Evidence: `backend-data-source-factory-stocks-route-migration-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `2a04b019965801084822e132c99690f97f8299b5`
│   │   ├── Result: migrates `get_stocks_basic` and `search_stocks` from direct
│   │   │          `get_data_source_factory()` calls to
│   │   │          `Depends(get_data_source_factory_dependency)`; total route/API
│   │   │          direct refs move `4 -> 2`, `stocks.py` direct refs move
│   │   │          `2 -> 0`, health route conflict tests move to `119 passed`,
│   │   │          provider tests remain `4 passed`, OpenAPI paths remain `500`,
│   │   │          duplicate operation IDs remain `0`, and staged GitNexus
│   │   │          reports low risk / 0 affected processes
│   │   └── Boundary: no route path, response model, response shape, OpenAPI,
│   │                frontend, runtime/PM2, OpenSpec, issue-label, compatibility
│   │                getter deletion, `futures.py`, or broad formatting cleanup
│   │                outside `stocks.py` and the focused test
│   ├── G2.75 Closeout / current-head refresh
│   │   ├── State: accepted; PR `#227` merged at
│   │   │          `53f365b55b37a03334ea25f083c8ef453fbb2db8`
│   │   ├── Evidence: `backend-data-source-factory-stocks-route-migration-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `02518742fb1169ced7f2aa34daaff0dc9dc8b47b`
│   │   ├── Result: records PR `#226` merge, confirms health route conflict tests
│   │   │          remain `119 passed`, provider tests remain `4 passed`,
│   │   │          route direct refs remain `2`, `stocks.py` direct refs remain
│   │   │          `0`, OpenAPI paths remain `500`, duplicate operation IDs
│   │   │          remain `0`, and the only remaining direct route/API refs are
│   │   │          `web/backend/app/api/data/futures.py:91` and `:114`
│   │   └── Boundary: closeout-only; no source edit, compatibility getter
│   │                deletion, `futures.py` migration, or implementation
│   │                authorization
│   ├── G2.76 Futures DataSourceFactory route migration risk packet
│   │   ├── State: accepted; PR `#228` merged at
│   │   │          `5fab3e8f6b0ebfb660f0cae1010cd59dfb30f039`
│   │   ├── Evidence: `backend-data-source-factory-futures-route-migration-risk-packet-2026-05-25.md`
│   │   ├── Current HEAD: `53f365b55b37a03334ea25f083c8ef453fbb2db8`
│   │   ├── Result: confirms `futures.py` owns the final two direct route/API
│   │   │          `get_data_source_factory()` refs at lines `91` and `114`;
│   │   │          records two OpenAPI-visible futures endpoints, ruff pass,
│   │   │          black reformat debt, focused futures docs guard `1 passed`,
│   │   │          provider tests `4 passed`, file-level GitNexus HIGH risk,
│   │   │          and exact route-handler caller count `0`
│   │   └── Boundary: decision-only; no source edit, route contract edit,
│   │                compatibility getter deletion, OpenSpec change, or issue
│   │                label change; recommends a future G2.77 path-limited
│   │                implementation authorization packet if accepted
│   ├── G2.77 Futures DataSourceFactory implementation authorization
│   │   ├── State: accepted; PR `#229` merged at
│   │   │          `5169da563b883fe0d883b25a09ed0d599952df0d`
│   │   ├── Evidence: `backend-data-source-factory-futures-route-migration-implementation-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `5fab3e8f6b0ebfb660f0cae1010cd59dfb30f039`
│   │   ├── Result: authorizes a future G2.78 implementation to edit only
│   │   │          `web/backend/app/api/data/futures.py` and
│   │   │          `web/backend/tests/test_health_route_conflicts.py`, using TDD
│   │   │          to move the final direct route/API factory refs `2 -> 0`
│   │   └── Boundary: authorization-only; no source edit in this packet, no
│   │                route contract edit, OpenSpec change, issue-label change,
│   │                runtime/PM2 action, compatibility getter deletion, or
│   │                formatting outside `futures.py`
│   ├── G2.78 Futures DataSourceFactory route migration
│   │   ├── State: accepted; PR `#230` merged at
│   │   │          `e7a2a436b157dc32d5675e89e4f8c16505b07629`
│   │   ├── Evidence: `backend-data-source-factory-futures-route-migration-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `e7a2a436b157dc32d5675e89e4f8c16505b07629`
│   │   ├── Result: migrates `get_futures_index_daily` and
│   │   │          `get_futures_index_realtime` to
│   │   │          `Depends(get_data_source_factory_dependency)`, removes the
│   │   │          final two route/API direct `get_data_source_factory()` calls,
│   │   │          moves direct refs `2 -> 0`, health tests to `120 passed`,
│   │   │          provider tests stay `4 passed`, OpenAPI paths stay `500`, and
│   │   │          duplicate operation IDs stay `0`
│   │   └── Boundary: no route path, response model, response shape, OpenAPI,
│   │                frontend, runtime/PM2, OpenSpec, issue-label,
│   │                compatibility getter deletion, other route consumer, or
│   │                formatting outside `futures.py`
│   ├── G2.78 Closeout / current-head refresh
│   │   ├── State: accepted; PR `#231` merged at
│   │   │          `b3aefed2648a3ec19dede187e4ca04a096dd0a7c`
│   │   ├── Evidence: `backend-data-source-factory-futures-route-migration-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `b3aefed2648a3ec19dede187e4ca04a096dd0a7c`
│   │   ├── Result: records PR `#230` merge, confirms health route conflict tests
│   │   │          pass `120`, provider lifecycle tests pass `4`, ruff and black
│   │   │          pass for `futures.py` plus the health test, OpenAPI remains
│   │   │          routes=`548`, paths=`500`, duplicate operation IDs=`0`, and
│   │   │          total route/API direct factory refs remain `0`
│   │   └── Boundary: no source, test, route path, response model, response
│   │                shape, OpenAPI exposure, frontend, runtime/PM2, OpenSpec,
│   │                issue-label, compatibility getter deletion, or retained-shim
│   │                retirement change is authorized
│   ├── G2.79 DataSourceFactory compatibility getter retained-shim decision
│   │   ├── State: accepted; PR `#232` merged at
│   │   │          `ac0fa318aa30262092d00219de18bd670bab26b2`
│   │   ├── Evidence: `backend-data-source-factory-compat-getter-retained-shim-decision-2026-05-25.md`
│   │   ├── Current HEAD: `ac0fa318aa30262092d00219de18bd670bab26b2`
│   │   ├── Result: decides to retain `get_data_source_factory()` for now:
│   │   │          route/API direct calls are `0`, but the compatibility getter
│   │   │          remains package-exported, is covered by lifecycle tests, and
│   │   │          is still used by service-internal helper fallback paths;
│   │   │          current GitNexus impact reports CRITICAL and must be treated
│   │   │          as a high-risk/stale-index warning, not deletion approval
│   │   └── Boundary: no source, test, route path, response model, response
│   │                shape, OpenAPI exposure, frontend, runtime/PM2, OpenSpec,
│   │                issue-label, compatibility getter deletion, package export
│   │                removal, or retained-shim retirement change is authorized
│   ├── G2.80 DataSourceFactory compatibility getter retirement authorization
│   │   ├── State: accepted; PR `#233` merged at
│   │   │          `b922db6b672f1084dcefb9ecba953b780ac8dbe3`
│   │   ├── Evidence: `backend-data-source-factory-compat-getter-retirement-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `b922db6b672f1084dcefb9ecba953b780ac8dbe3`
│   │   ├── Result: authorizes only a future G2.81 Phase 1 service-internal
│   │   │          decoupling step: internal helper fallback paths may stop
│   │   │          calling public `get_data_source_factory()`, while the public
│   │   │          getter and package exports must remain; route/API direct calls
│   │   │          are still `0`, focused lifecycle tests pass `4`, health route
│   │   │          conflicts pass `120`, and OpenAPI remains paths=`500` with
│   │   │          duplicate operation IDs=`0`
│   │   └── Boundary: this packet makes no source changes and does not authorize
│   │                public getter deletion, package export removal, route/API
│   │                edits, OpenAPI exposure changes, frontend changes,
│   │                runtime/PM2 changes, OpenSpec changes, or issue-label changes
│   ├── G2.81 DataSourceFactory compatibility getter retirement Phase 1 implementation
│   │   ├── State: accepted; PR `#234` merged at
│   │   │          `c176b9e71dd0fe4fb9df65c1f2c82631a45cfc3d`
│   │   ├── Evidence: `backend-data-source-factory-compat-getter-retirement-phase1-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `c176b9e71dd0fe4fb9df65c1f2c82631a45cfc3d`
│   │   ├── Result: introduces private `_get_or_create_data_source_factory()`,
│   │   │          keeps public `get_data_source_factory()` as a compatibility
│   │   │          wrapper, decouples service-internal helper fallback calls from
│   │   │          the public getter, keeps package exports unchanged, moves
│   │   │          service helper public getter calls to `0`, keeps route/API
│   │   │          direct calls at `0`, expands lifecycle tests to `5 passed`,
│   │   │          keeps health route conflicts at `120 passed`, and keeps
│   │   │          OpenAPI paths=`500` with duplicate operation IDs=`0`
│   │   └── Boundary: no public getter deletion, package export removal, route/API
│   │                edit, OpenAPI exposure change, frontend change, runtime/PM2
│   │                change, OpenSpec change, or issue-label change is authorized
│   ├── G2.82 DataSourceFactory compatibility getter retirement Phase 1 closeout
│   │   ├── State: accepted; PR `#235` merged at
│   │   │          `075768a56ea78f11796387d25fe33eed04668c6f`
│   │   ├── Evidence: `backend-data-source-factory-compat-getter-retirement-phase1-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `075768a56ea78f11796387d25fe33eed04668c6f`
│   │   ├── Result: records PR `#234` merge, confirms lifecycle tests
│   │   │          pass `5`, health route conflicts pass `120`, OpenAPI remains
│   │   │          routes=`548`, paths=`500`, duplicate operation IDs=`0`,
│   │   │          route/API direct public getter calls stay `0`, service helper
│   │   │          public getter calls stay `0`, and package export mentions stay `4`
│   │   └── Boundary: governance-only closeout; no source, test, public getter
│   │                deletion, package export removal, route/API, OpenAPI,
│   │                frontend, runtime/PM2, OpenSpec, or issue-label change is
│   │                authorized
│   ├── G2.83 DataSourceFactory compatibility getter final retirement authorization
│   │   ├── State: accepted; PR `#236` merged at
│   │   │          `5de71a8847a45efd0628b184baff985a9dd3b180`
│   │   ├── Evidence: `backend-data-source-factory-compat-getter-final-retirement-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `5de71a8847a45efd0628b184baff985a9dd3b180`
│   │   ├── Result: precise scan shows production exact public getter hits are
│   │   │          limited to the definition and package exports, route/API
│   │   │          production consumers are `0`, package export lines are `2`,
│   │   │          lifecycle tests pass `5`, stocks runtime fallback passes `1`,
│   │   │          and remaining public getter patch points are test-only; future
│   │   │          G2.84 may remove the public getter and package exports only
│   │   │          under the listed source/test scope
│   │   └── Boundary: authorization-only; no source, test, public getter deletion,
│   │                package export removal, route/API, OpenAPI, frontend,
│   │                runtime/PM2, OpenSpec, or issue-label change is made here
│   ├── G2.84 DataSourceFactory compatibility getter final retirement implementation
│   │   ├── State: accepted; PR `#237` merged at
│   │   │          `f31720ec3a891607eec3ce29b27ad1bc80be0a43`
│   │   ├── Evidence: `backend-data-source-factory-compat-getter-final-retirement-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `f31720ec3a891607eec3ce29b27ad1bc80be0a43`
│   │   ├── Result: removes public `get_data_source_factory()` and its package
│   │   │          export, keeps `get_data_source_factory_dependency` and
│   │   │          `_get_or_create_data_source_factory`, moves production exact
│   │   │          public getter hits to `0`, package export lines to `0`, patch
│   │   │          points to `0`, keeps lifecycle tests at `5 passed`, stocks
│   │   │          runtime fallback at `1 passed`, market API integration at
│   │   │          `18 passed`, health route conflicts at `120 passed`, and
│   │   │          OpenAPI paths=`500` with duplicate operation IDs=`0`
│   │   └── Boundary: no route/API, OpenAPI, frontend, runtime/PM2, OpenSpec,
│   │                issue-label, dependency provider removal, private initializer
│   │                removal, or unrelated historical-route test-debt fix is made
│   ├── G2.85 DataSourceFactory compatibility getter final retirement closeout
│   │   ├── State: accepted; PR `#238` merged at
│   │   │          `ed033a45552a22b6ce4027a04029ea0764d191cf`
│   │   ├── Evidence: `backend-data-source-factory-compat-getter-final-retirement-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `ed033a45552a22b6ce4027a04029ea0764d191cf`
│   │   ├── Result: confirms PR `#237` merged, production exact public getter
│   │   │          hits remain `0`, package export lines remain `0`, route/API
│   │   │          public getter hits remain `0`, lifecycle tests pass `5`,
│   │   │          health route conflicts pass `120`, touched-path ruff passes,
│   │   │          and OpenAPI remains paths=`500` with duplicate operation IDs=`0`
│   │   └── Boundary: closeout-only; no source, test, route/API, OpenAPI,
│   │                frontend, runtime/PM2, OpenSpec, dependency provider,
│   │                private initializer, or issue-label change is made here
│   ├── G2.86 Service lifecycle next-lane decision after DataSourceFactory
│   │   ├── State: accepted; PR `#239` merged at
│   │   │          `a20c92eef786ee816d0a8c171641c292ba2455f8`
│   │   ├── Evidence: `backend-service-lifecycle-di-next-lane-after-data-source-factory-2026-05-25.md`
│   │   ├── Current HEAD: `a20c92eef786ee816d0a8c171641c292ba2455f8`
│   │   ├── Result: selects `AdvancedAnalysisService` compatibility getter
│   │   │          Phase 1 service-internal decoupling as the next authorization
│   │   │          candidate only; current-head exact production getter hits are
│   │   │          definition plus provider fallback only, route/API direct hits
│   │   │          are `0`, GitNexus impact is LOW / `0`, lifecycle tests pass
│   │   │          `4`, health route conflicts pass `120`, and OpenAPI remains
│   │   │          paths=`500` with duplicate operation IDs=`0`
│   │   └── Boundary: decision-only; no source, test, route/API, OpenAPI,
│   │                frontend, runtime/PM2, OpenSpec, public getter deletion,
│   │                dependency provider removal, private initializer addition,
│   │                or issue-label change is made here
│   ├── G2.87 AdvancedAnalysis compatibility getter Phase 1 authorization
│   │   ├── State: accepted; PR `#240` merged at
│   │   │          `55861bb10d19dfafe9ff5e100f583069dcdbc2a9`
│   │   ├── Evidence: `backend-advanced-analysis-compat-getter-phase1-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `55861bb10d19dfafe9ff5e100f583069dcdbc2a9`
│   │   ├── Result: authorizes only a future G2.88 Phase 1 implementation that
│   │   │          may add a private async initializer, retarget
│   │   │          `get_advanced_analysis_service_dependency()` fallback away
│   │   │          from public `get_advanced_analysis_service()`, and update
│   │   │          focused lifecycle tests; current-head evidence remains route/API
│   │   │          direct public getter hits=`0`, GitNexus impact LOW / `0`,
│   │   │          lifecycle tests `4 passed`, health route conflicts `120 passed`,
│   │   │          and OpenAPI paths=`500`, duplicate operation IDs=`0`
│   │   └── Boundary: authorization-only; no source, test, route/API, OpenAPI,
│   │                frontend, runtime/PM2, OpenSpec, public getter deletion,
│   │                dependency provider removal, or issue-label change is made
│   ├── G2.88 AdvancedAnalysis compatibility getter Phase 1 implementation
│   │   ├── State: accepted; PR `#241` merged at
│   │   │          `33c3d34dc00caa8b347e90d66084c1d001559186`
│   │   ├── Evidence: `backend-advanced-analysis-compat-getter-phase1-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `33c3d34dc00caa8b347e90d66084c1d001559186`
│   │   ├── Result: adds private `_get_or_create_advanced_analysis_service()`,
│   │   │          keeps public `get_advanced_analysis_service()` as a Phase 1
│   │   │          compatibility wrapper, retargets
│   │   │          `get_advanced_analysis_service_dependency()` fallback away
│   │   │          from the public getter, and proves the fallback via TDD red /
│   │   │          green lifecycle coverage; post-change scan shows route/API
│   │   │          public getter hits=`0`, exact public getter production hits are
│   │   │          definition-only, lifecycle tests `4 passed`, health route
│   │   │          conflicts `120 passed`, and OpenAPI remains paths=`500` with
│   │   │          duplicate operation IDs=`0`
│   │   └── Boundary: source-capable but limited to the service module, focused
│   │                lifecycle test, governance report, generated artifact,
│   │                task card, and steward-tree update; no public getter
│   │                deletion, route/API, OpenAPI exposure, frontend, PM2,
│   │                OpenSpec, or issue-label change is made here
│   ├── G2.89 AdvancedAnalysis compatibility getter Phase 1 closeout / candidate refresh
│   │   ├── State: accepted; PR `#242` merged at
│   │   │          `7b6d81aaad7af8279cbb7304903a88987682e579`
│   │   ├── Evidence: `backend-advanced-analysis-compat-getter-phase1-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `7b6d81aaad7af8279cbb7304903a88987682e579`
│   │   ├── Result: records PR `#241` merge, confirms exact public getter
│   │   │          production hits are definition-only, route/API public getter
│   │   │          hits=`0`, package export hits=`0`, private initializer hits=`3`,
│   │   │          dependency-provider refs=`19`, lifecycle tests `4 passed`,
│   │   │          health route conflicts `120 passed`, and OpenAPI remains
│   │   │          paths=`500` with duplicate operation IDs=`0`
│   │   └── Boundary: closeout / candidate-refresh only; no source, test,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                public getter deletion, or issue-label change is made here
│   ├── G2.90 AdvancedAnalysis public compatibility getter final-retirement authorization
│   │   ├── State: accepted; PR `#243` merged at
│   │   │          `db5ebd408f0d89c012e8c3e0ea23361e7836a53f`
│   │   ├── Evidence: `backend-advanced-analysis-compat-getter-final-retirement-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `db5ebd408f0d89c012e8c3e0ea23361e7836a53f`
│   │   ├── Result: authorizes only a future G2.91 source branch to remove
│   │   │          public `get_advanced_analysis_service()` after TDD red/green;
│   │   │          current-head evidence shows GitNexus impact LOW / `0`,
│   │   │          exact public getter production hits are definition-only,
│   │   │          route/API public getter hits=`0`, package export hits=`0`,
│   │   │          lifecycle tests `4 passed`, health route conflicts
│   │   │          `120 passed`, and OpenAPI remains paths=`500` with duplicate
│   │   │          operation IDs=`0`
│   │   └── Boundary: authorization-only; no source, test, route/API, OpenAPI
│   │                exposure, frontend, PM2, OpenSpec, public getter deletion,
│   │                or issue-label change is made here
│   ├── G2.91 AdvancedAnalysis public compatibility getter final-retirement implementation
│   │   ├── State: accepted; PR `#244` merged at
│   │   │          `1ebd0aeaf3f21fbaefd570955ca89b571207c18a`
│   │   ├── Evidence: `backend-advanced-analysis-compat-getter-final-retirement-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `1ebd0aeaf3f21fbaefd570955ca89b571207c18a`
│   │   ├── Result: removes public `get_advanced_analysis_service()`, keeps
│   │   │          `_get_or_create_advanced_analysis_service()` and
│   │   │          `get_advanced_analysis_service_dependency()`, updates focused
│   │   │          lifecycle tests via TDD red/green, leaves route/API public
│   │   │          getter hits=`0`, package export hits=`0`, exact public getter
│   │   │          call hits=`0`, lifecycle tests `5 passed`, health route
│   │   │          conflicts `120 passed`, and OpenAPI remains paths=`500` with
│   │   │          duplicate operation IDs=`0`
│   │   └── Boundary: source-capable but limited to the service module, focused
│   │                lifecycle test, governance report, generated artifact,
│   │                task card, and steward-tree update; no route/API, OpenAPI
│   │                exposure, frontend, PM2, OpenSpec, or issue-label change is
│   │                made here
│   ├── G2.92 AdvancedAnalysis public compatibility getter final-retirement closeout
│   │   ├── State: accepted; PR `#245` merged at
│   │   │          `0d98e77257372ba9a92dfda40b2c42343b89e92f`
│   │   ├── Evidence: `backend-advanced-analysis-compat-getter-final-retirement-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `0d98e77257372ba9a92dfda40b2c42343b89e92f`
│   │   ├── Result: records PR `#244` merge and closes the AdvancedAnalysis
│   │   │          public compatibility getter lane; current-head evidence shows
│   │   │          exact public getter symbol mentions are test assertion only,
│   │   │          route/API public mentions=`0`, package export mentions=`0`,
│   │   │          private initializer hits=`2`, dependency-provider refs=`19`,
│   │   │          lifecycle tests `5 passed`, health route conflicts
│   │   │          `120 passed`, and OpenAPI remains paths=`500` with duplicate
│   │   │          operation IDs=`0`
│   │   └── Boundary: closeout-only; no source, test, route/API, OpenAPI
│   │                exposure, frontend, PM2, OpenSpec, getter deletion, or
│   │                issue-label change is made here
│   ├── G2.93 Service lifecycle candidate refresh after AdvancedAnalysis
│   │   ├── State: accepted; PR `#246` merged at
│   │   │          `d8e1d14440d4db21a43b8dd50586f0deef383081`
│   │   ├── Evidence: `backend-service-lifecycle-candidate-refresh-after-advanced-analysis-2026-05-25.md`
│   │   ├── Current HEAD: `d8e1d14440d4db21a43b8dd50586f0deef383081`
│   │   ├── Result: records PR `#245` merge, refreshes service getter
│   │   │          candidates at current HEAD, scans `152` service files,
│   │   │          `575` app files, and `219` API files, finds `23` getter
│   │   │          definitions under this packet's scanner, and selects
│   │   │          `get_wencai_service` as the next future authorization
│   │   │          candidate only; its current references are definition-only
│   │   │          in app code with route/API hits=`0`, test hits=`0`,
│   │   │          package export hits=`0`, and GitNexus impact LOW / `0`
│   │   └── Boundary: candidate-refresh only; no source, test, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter
│   │                deletion, or issue-label change is made here
│   ├── G2.94 Wencai getter-retirement authorization
│   │   ├── State: accepted; PR `#247` merged at
│   │   │          `228a94d3ac0d77d421379ea37a4a328bd6975389`
│   │   ├── Evidence: `backend-wencai-compat-getter-retirement-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `228a94d3ac0d77d421379ea37a4a328bd6975389`
│   │   ├── Result: authorizes only a future G2.95 implementation branch to
│   │   │          remove `get_wencai_service` from
│   │   │          `web/backend/app/services/wencai_service.py` after TDD
│   │   │          red/green; current evidence shows `get_wencai_service`
│   │   │          refs app=`1`, route/API=`0`, tests=`0`, package exports=`0`,
│   │   │          GitNexus impact LOW / `0`, while `WencaiService` remains
│   │   │          active through direct class usage and is not a deletion target
│   │   └── Boundary: authorization-only; no source, test, route/API, OpenAPI
│   │                exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                `WencaiService` deletion, or issue-label change is made here
│   ├── G2.95 Wencai getter-retirement implementation
│   │   ├── State: accepted; PR `#248` merged at
│   │   │          `689d619c715ec521a3f5c1d967b0fc8eeb798293`
│   │   ├── Evidence: `backend-wencai-compat-getter-retirement-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `689d619c715ec521a3f5c1d967b0fc8eeb798293`
│   │   ├── Result: removes only `get_wencai_service` from
│   │   │          `web/backend/app/services/wencai_service.py`, adds focused
│   │   │          retirement regression coverage, and keeps `WencaiService`
│   │   │          importable and active; TDD red confirmed `1 failed,
│   │   │          1 passed`, green focused test `2 passed`, health route
│   │   │          conflicts `120 passed`, ruff passed, black check passed,
│   │   │          OpenAPI smoke routes=`548`, paths=`500`, duplicate
│   │   │          operation IDs=`0`, and post-change app/API/package
│   │   │          refs for `get_wencai_service` are `0`
│   │   └── Boundary: source-capable but limited to `wencai_service.py`,
│   │                `test_wencai_service_getter_retirement.py`, governance
│   │                report, generated artifact, task card, and steward-tree
│   │                update; no route/API, OpenAPI exposure, frontend, PM2,
│   │                OpenSpec, `WencaiService` deletion, or issue-label change
│   │                is made here
│   ├── G2.96 Wencai getter-retirement closeout
│   │   ├── State: accepted; PR `#249` merged at
│   │   │          `c0aa9731503f3f8d8c9017ed787745ddaf6a5aab`
│   │   ├── Evidence: `backend-wencai-compat-getter-retirement-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `c0aa9731503f3f8d8c9017ed787745ddaf6a5aab`
│   │   ├── Result: records PR `#248` merge and closes the Wencai public
│   │   │          compatibility getter lane; current-head scan shows
│   │   │          `get_wencai_service` refs app=`0`, route/API=`0`,
│   │   │          tests=`1` absence assertion, package exports=`0`,
│   │   │          `WencaiService` remains active with app refs=`16` and
│   │   │          route/API refs=`9`, focused test `2 passed`, and health
│   │   │          route conflicts `120 passed`
│   │   └── Boundary: closeout-only; no source, test, route/API, OpenAPI
│   │                exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                `WencaiService` deletion, or issue-label change is made here
│   ├── G2.97 Service lifecycle candidate refresh after Wencai
│   │   ├── State: accepted; PR `#250` merged at
│   │   │          `dfb1dce27c0501b7eb855e478e68b82db4959d9d`
│   │   ├── Evidence: `backend-service-lifecycle-candidate-refresh-after-wencai-2026-05-25.md`
│   │   ├── Current HEAD: `dfb1dce27c0501b7eb855e478e68b82db4959d9d`
│   │   ├── Result: records PR `#249` merge, refreshes service getter
│   │   │          candidates at current HEAD, scans `152` service files,
│   │   │          `575` app files, `219` API files, and `1007` test files,
│   │   │          finds `22` getter definitions and `5` candidate-like
│   │   │          definitions, confirms `get_wencai_service` is no longer a
│   │   │          service getter definition, and selects
│   │   │          `get_enhanced_data_service` as a future G2.98 authorization
│   │   │          candidate only; GitNexus impact is LOW / `3`, with no
│   │   │          affected processes
│   │   └── Boundary: candidate-refresh only; no source, test, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter
│   │                deletion, or issue-label change is made here
│   ├── G2.98 EnhancedDataService getter-retirement authorization
│   │   ├── State: accepted; PR `#251` merged at
│   │   │          `8fb6db0e13018d83eef7e0deca02106104c06160`
│   │   ├── Evidence: `backend-enhanced-data-service-getter-retirement-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `8fb6db0e13018d83eef7e0deca02106104c06160`
│   │   ├── Result: authorizes only a future G2.99 implementation branch to
│   │   │          retire `get_enhanced_data_service` from
│   │   │          `web/backend/app/services/data_service_enhanced.py` after
│   │   │          TDD red/green; current evidence shows getter refs app=`1`
│   │   │          file, route/API=`0`, focused tests=`0`, package exports=`0`,
│   │   │          with one module-local `__main__` smoke call, while
│   │   │          `EnhancedDataService` remains active through direct class
│   │   │          usage in `web/backend/app/api/v1/system/health.py`;
│   │   │          GitNexus impact is LOW / `3`, with no affected processes
│   │   └── Boundary: authorization-only; no source, test, route/API, OpenAPI
│   │                exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                `EnhancedDataService` deletion, or issue-label change is
│   │                made here
│   ├── G2.99 EnhancedDataService getter-retirement implementation
│   │   ├── State: accepted; PR `#252` merged at
│   │   │          `e3bb781d8a92bc8e59a31a6d99d3d9a54f3d14b6`
│   │   ├── Evidence: `backend-enhanced-data-service-getter-retirement-implementation-2026-05-25.md`
│   │   ├── Current HEAD: `e3bb781d8a92bc8e59a31a6d99d3d9a54f3d14b6`
│   │   ├── Result: removes only `get_enhanced_data_service` and its private
│   │   │          `_enhanced_data_service` singleton state, updates the
│   │   │          module-local `__main__` smoke call to construct
│   │   │          `EnhancedDataService()` directly, and adds focused regression
│   │   │          coverage; TDD red was `2 failed, 1 passed`, green is
│   │   │          `3 passed`, health route conflicts are `120 passed`, and
│   │   │          OpenAPI smoke remains routes=`548`, paths=`500`,
│   │   │          operation IDs=`536`, duplicate operation IDs=`0`
│   │   └── Boundary: source-capable but getter-retirement-only; no route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                `EnhancedDataService` deletion, or issue-label change is
│   │                made here
│   ├── G2.100 EnhancedDataService getter-retirement closeout
│   │   ├── State: accepted; PR `#253` merged at
│   │   │          `d7be7e6e8bb0ad3bcf62b9420bc5da5d7941054e`
│   │   ├── Evidence: `backend-enhanced-data-service-getter-retirement-closeout-2026-05-25.md`
│   │   ├── Current HEAD: `d7be7e6e8bb0ad3bcf62b9420bc5da5d7941054e`
│   │   ├── Result: records PR `#252` merge and closes the
│   │   │          EnhancedDataService public compatibility getter lane;
│   │   │          current-head scan shows `get_enhanced_data_service` app refs
│   │   │          `0`, route/API refs `0`, tests `2` absence assertions,
│   │   │          package exports `0`, `_enhanced_data_service` app refs `0`,
│   │   │          and `EnhancedDataService` remains active with app refs `8`
│   │   │          and route/API refs `4`; focused test `3 passed`, health
│   │   │          route conflicts `120 passed`
│   │   └── Boundary: closeout-only; no source, test, route/API, OpenAPI
│   │                exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                `EnhancedDataService` deletion, or issue-label change is
│   │                made here
│   ├── G2.101 Service lifecycle candidate refresh after EnhancedDataService
│   │   ├── State: accepted; PR `#254` merged at
│   │   │          `c8eae46c738fff199100cf4e02015a9ade887eee`
│   │   ├── Evidence: `backend-service-lifecycle-candidate-refresh-after-enhanced-data-service-2026-05-25.md`
│   │   ├── Current HEAD: `c8eae46c738fff199100cf4e02015a9ade887eee`
│   │   ├── Result: records PR `#253` merge, refreshes service getter
│   │   │          candidates at current HEAD, scans `152` service files,
│   │   │          `575` app files, `219` API files, and `1008` test files,
│   │   │          finds `18` getter definitions and `4` candidate-like
│   │   │          definitions, confirms `get_enhanced_data_service` is no
│   │   │          longer a service getter definition, and selects
│   │   │          `get_tradingview_service` as a future G2.102 authorization
│   │   │          candidate only; GitNexus impact is LOW / `1`, with no
│   │   │          affected processes
│   │   └── Boundary: candidate-refresh only; no source, test, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter
│   │                deletion, or issue-label change is made here
│   ├── G2.102 TradingView getter-retirement authorization
│   │   ├── State: accepted; PR `#255` merged at
│   │   │          `a0cfa4f35125bb0475b1d98c4225a4321c18de1c`
│   │   ├── Evidence: `backend-tradingview-getter-retirement-authorization-2026-05-25.md`
│   │   ├── Current HEAD: `a0cfa4f35125bb0475b1d98c4225a4321c18de1c`
│   │   ├── Result: authorizes only a future G2.103 implementation branch to
│   │   │          retire `get_tradingview_service` from
│   │   │          `web/backend/app/services/tradingview_widget_service.py`
│   │   │          after TDD red/green; current evidence shows getter refs
│   │   │          app=`2`, route/API=`0`, tests=`2`, package exports=`0`,
│   │   │          with `install_tradingview_service` as the only direct graph
│   │   │          caller; GitNexus impact is LOW / `1`, with no affected
│   │   │          processes
│   │   └── Boundary: authorization-only; no source, test, route/API, OpenAPI
│   │                exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                `TradingViewWidgetService` deletion, or issue-label change
│   │                is made here
│   ├── G2.103 TradingView getter-retirement implementation
│   │   ├── State: accepted; PR `#256` merged at
│   │   │          `81cd6191c178f8a443e8f3b303e47c2583fc4402`
│   │   ├── Evidence: `backend-tradingview-getter-retirement-implementation-2026-05-26.md`
│   │   ├── Base HEAD: `a0cfa4f35125bb0475b1d98c4225a4321c18de1c`
│   │   ├── Result: removes only `get_tradingview_service` and the private
│   │   │          `_tradingview_service` singleton state, changes
│   │   │          `install_tradingview_service` fallback to direct
│   │   │          `TradingViewWidgetService()` construction, and updates
│   │   │          lifecycle DI coverage; TDD red was `1 failed, 7 passed`,
│   │   │          green is `8 passed`, health route conflicts are
│   │   │          `120 passed`, and schema-only OpenAPI smoke with
│   │   │          non-sensitive placeholder env remains routes=`548`,
│   │   │          paths=`500`, operation IDs=`536`, duplicate operation
│   │   │          IDs=`0`
│   │   └── Boundary: source-capable but getter-retirement-only; no route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                `TradingViewWidgetService` deletion, lifecycle helper
│   │                deletion, or issue-label change is made here
│   ├── G2.104 TradingView getter-retirement closeout
│   │   ├── State: accepted; PR `#257` merged at
│   │   │          `750fa311eb716ff54c577748e5658329736632b4`
│   │   ├── Evidence: `backend-tradingview-getter-retirement-closeout-2026-05-26.md`
│   │   ├── Current HEAD: `81cd6191c178f8a443e8f3b303e47c2583fc4402`
│   │   ├── Result: records PR `#256` merge and closes the
│   │   │          TradingView public compatibility getter lane; current-head
│   │   │          scan shows `get_tradingview_service` app refs=`0`,
│   │   │          route/API refs=`0`, test refs=`3`, package export refs=`0`,
│   │   │          and `_tradingview_service` app refs=`0`, route/API refs=`0`,
│   │   │          test refs=`2`, package export refs=`0`; focused lifecycle
│   │   │          tests are `8 passed` and health route conflicts are
│   │   │          `120 passed`
│   │   └── Boundary: closeout-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, service class
│   │                deletion, lifecycle helper deletion, or issue-label change
│   │                is made here
│   ├── G2.105 Service lifecycle candidate refresh after TradingView
│   │   ├── State: accepted; PR `#258` merged at
│   │   │          `9ac90c14acd14b851bf49271f48fba30c8b10e41`
│   │   ├── Evidence: `backend-service-lifecycle-candidate-refresh-after-tradingview-2026-05-26.md`
│   │   ├── Current HEAD: `750fa311eb716ff54c577748e5658329736632b4`
│   │   ├── Result: scan covers service files=`152`, backend app files=`575`,
│   │   │          API files=`219`, test files=`1008`, getter definitions=`17`,
│   │   │          candidate-like definitions=`3`, holds=`14`; the remaining
│   │   │          candidate-like rows are `get_announcement_service` as an
│   │   │          already-completed hold and two duplicate logical
│   │   │          `get_email_service` rows, so no direct source implementation
│   │   │          lane is selected here
│   │   └── Boundary: candidate-refresh-only; no backend source/test edit,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                getter deletion, service migration, or issue-label change
│   │                is made here
│   ├── G2.106 Email duplicate getter ownership decision
│   │   ├── State: accepted; PR `#259` merged at
│   │   │          `6e10c496a4e3c68c21b93a2ddfec09ef74f1aa30`
│   │   ├── Evidence: `backend-email-duplicate-getter-ownership-decision-2026-05-26.md`
│   │   ├── Current HEAD: `9ac90c14acd14b851bf49271f48fba30c8b10e41`
│   │   ├── Decision: treat `web/backend/app/services/email_service.py` as the
│   │   │          route-backed `EmailService` lifecycle owner and
│   │   │          `web/backend/app/services/email_notification_service.py` as a
│   │   │          separate legacy/helper notification owner; do not collapse the
│   │   │          duplicate `get_email_service` rows into one source edit
│   │   ├── Result: current text scan shows combined `get_email_service` app
│   │   │          refs=`3`, route/API refs=`0`, tests=`3`, while
│   │   │          `get_email_service_dependency` remains active with app refs=`8`,
│   │   │          route/API refs=`7`, tests=`3`; GitNexus impact for
│   │   │          `email_service.py:get_email_service` is MEDIUM / `6`, and
│   │   │          `email_notification_service.py:get_email_service` has no
│   │   │          incoming graph callers
│   │   └── Boundary: decision-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                service migration, or issue-label change is made here
│   ├── G2.107 EmailNotificationService getter-retirement authorization
│   │   ├── State: accepted; PR `#260` merged at
│   │   │          `d120d6d28d391daeb9e3d6accbd2b9ee0acfe931`
│   │   ├── Evidence: `backend-email-notification-getter-retirement-authorization-2026-05-26.md`
│   │   ├── Current HEAD: `6e10c496a4e3c68c21b93a2ddfec09ef74f1aa30`
│   │   ├── Decision: authorize only a future G2.108 implementation branch to
│   │   │          retire `web/backend/app/services/email_notification_service.py`
│   │   │          module-level `_email_service` and `get_email_service`; preserve
│   │   │          `EmailNotificationService` and do not touch route-backed
│   │   │          `web/backend/app/services/email_service.py`
│   │   ├── Result: file-path GitNexus context shows
│   │   │          `email_notification_service.py:get_email_service` has no
│   │   │          incoming graph callers or process participation; exact text
│   │   │          scan shows route/API uses remain on
│   │   │          `email_service.py:get_email_service_dependency`; bare
│   │   │          `get_email_service` impact resolves to the route-backed
│   │   │          `email_service.py` symbol and must not be used as the sole
│   │   │          future implementation gate
│   │   └── Boundary: authorization-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                service migration, or issue-label change is made here
│   ├── G2.108 EmailNotificationService getter-retirement implementation
│   │   ├── State: accepted; PR `#261` merged at
│   │   │          `9cb643dbcd78bae76afc8201dad65b6f431a801c`
│   │   ├── Evidence: `backend-email-notification-getter-retirement-implementation-2026-05-26.md`
│   │   ├── Current HEAD: `d120d6d28d391daeb9e3d6accbd2b9ee0acfe931`
│   │   ├── Result: removes only
│   │   │          `email_notification_service.py:_email_service` and
│   │   │          `email_notification_service.py:get_email_service`; preserves
│   │   │          `EmailNotificationService`, keeps route-backed
│   │   │          `email_service.py:get_email_service_dependency` untouched,
│   │   │          and leaves notification routes with `0` direct
│   │   │          `email_notification_service` refs
│   │   ├── Verification: TDD red `1 failed`, focused green `5 passed`,
│   │   │          health route conflicts `120 passed`, touched-file ruff passed,
│   │   │          black check passed, exact post-change scan shows target getter
│   │   │          refs=`0` and target singleton refs=`0`
│   │   └── Boundary: source-capable but narrow; no `email_service.py`,
│   │                `notification.py`, route/API, OpenAPI exposure, frontend,
│   │                PM2, OpenSpec, service consolidation, class deletion, or
│   │                issue-label change is made here
│   ├── G2.109 EmailNotificationService getter-retirement closeout
│   │   ├── State: accepted; PR `#262` merged at
│   │   │          `ae6d2f287ddb8d71119ce52ef4ebaf00d64dc7b5`
│   │   ├── Evidence: `backend-email-notification-getter-retirement-closeout-2026-05-26.md`
│   │   ├── Current HEAD: `9cb643dbcd78bae76afc8201dad65b6f431a801c`
│   │   ├── Result: records PR `#261` merge, confirms
│   │   │          `email_notification_service.py:get_email_service` refs=`0`,
│   │   │          `email_notification_service.py:_email_service` refs=`0`,
│   │   │          route/API direct `email_notification_service` refs=`0`, and
│   │   │          preserves `EmailNotificationService` plus route-backed
│   │   │          `email_service.py:get_email_service_dependency`
│   │   ├── Verification: focused tests `5 passed`, health route conflicts
│   │   │          `120 passed`, touched-target ruff passed, black check passed
│   │   └── Boundary: closeout-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, service
│   │                consolidation, class deletion, getter deletion, or
│   │                issue-label change is made here
│   ├── G2.110 Service lifecycle candidate refresh after EmailNotificationService
│   │   ├── State: accepted; PR `#263` merged at
│   │   │          `c4abd4e8c4705f07a7d86e13c2090d30575e95e9`
│   │   ├── Evidence: `backend-service-lifecycle-candidate-refresh-after-email-notification-2026-05-26.md`
│   │   ├── Current HEAD: `ae6d2f287ddb8d71119ce52ef4ebaf00d64dc7b5`
│   │   ├── Result: current scan covers service files=`152`, backend app files=`575`,
│   │   │          API files=`219`, backend test files=`199`, all test files=`1211`,
│   │   │          getter definitions=`16`, candidate-like definitions=`9`; the
│   │   │          retired `email_notification_service.py:get_email_service` no
│   │   │          longer appears as a candidate
│   │   ├── Decision: select `web/backend/app/services/market_data_service/get_market_data_service.py`
│   │   │          `get_market_data_service` as the next authorization candidate
│   │   │          only; GitNexus impact is LOW / `0`, route/API direct refs=`0`,
│   │   │          while streaming, TDX, data, strategy, stock search, watchlist,
│   │   │          email, and announcement candidates remain holds
│   │   └── Boundary: candidate-refresh-only; no backend source/test edit,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                getter deletion, service migration, or issue-label change
│   │                is made here
│   ├── G2.111 MarketDataService getter-retirement authorization
│   │   ├── State: accepted; PR `#264` merged at
│   │   │          `88a8ae4e50ca29c21580db2e0c3f33c0a303ad2d`
│   │   ├── Evidence: `backend-market-data-service-getter-retirement-authorization-2026-05-26.md`
│   │   ├── Current HEAD: `c4abd4e8c4705f07a7d86e13c2090d30575e95e9`
│   │   ├── Decision: authorize only a future G2.112 implementation branch to
│   │   │          retire the package-level
│   │   │          `market_data_service/get_market_data_service.py`
│   │   │          `_market_data_service` and `get_market_data_service` surface,
│   │   │          while preserving `MarketDataService`, `install_market_data_service`,
│   │   │          and `get_market_data_service_dependency`
│   │   ├── Result: GitNexus impact is LOW / `0`; direct API refs=`0`, but
│   │   │          app refs exist in `market_data_adapter.py` and package exports,
│   │   │          so the future implementation must include adapter/package
│   │   │          cleanup and focused tests rather than deleting the getter alone
│   │   └── Boundary: authorization-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                service migration, or issue-label change is made here
│   ├── G2.112 MarketDataService getter-retirement implementation
│   │   ├── State: accepted; PR `#265` merged at
│   │   │          `b5ca0c5fcf65de77e7bf336091c4ae3f220019ef`
│   │   ├── Evidence: `backend-market-data-service-getter-retirement-implementation-2026-05-26.md`
│   │   ├── Current HEAD: `88a8ae4e50ca29c21580db2e0c3f33c0a303ad2d`
│   │   ├── Change: retired package-level
│   │   │          `market_data_service/get_market_data_service.py`
│   │   │          `_market_data_service` and `get_market_data_service`, removed
│   │   │          the package export, and retargeted `market_data_adapter.py`
│   │   │          to an adapter-local `MarketDataService` lazy instance
│   │   ├── Preservation: `MarketDataService`, `install_market_data_service`,
│   │   │          `get_market_data_service_dependency`, route/API contracts,
│   │   │          OpenAPI exposure, PM2, OpenSpec, frontend, and root-level
│   │   │          `web/backend/app/services/__init__.py:get_market_data_service`
│   │   │          remain unchanged
│   │   ├── Verification: TDD red produced `2 failed`; focused tests
│   │   │          `7 passed`; health route conflicts `120 passed`; touched-file
│   │   │          ruff and black passed; `app.main` import passes when required
│   │   │          environment variables are supplied
│   │   └── Boundary: implementation-only for the authorized package getter;
│   │                no route/API, OpenAPI, frontend, PM2, OpenSpec,
│   │                root-level services getter, service consolidation, or
│   │                issue-label change is made here
│   ├── G2.113 MarketDataService getter-retirement closeout/current-head refresh
│   │   ├── State: accepted; PR `#266` merged at
│   │   │          `18af895af5fd09c1dff832b6f8bc968227711a28`
│   │   ├── Evidence: `backend-market-data-service-getter-retirement-closeout-2026-05-26.md`
│   │   ├── Current HEAD: `b5ca0c5fcf65de77e7bf336091c4ae3f220019ef`
│   │   ├── Result: current scan covers backend app/test Python files=`775`;
│   │   │          package-level getter definitions=`0`, target singleton tokens=`0`,
│   │   │          package getter imports=`0`, adapter getter calls=`0`, and
│   │   │          root-level `web/backend/app/services/__init__.py:get_market_data_service`
│   │   │          remains preserved
│   │   ├── Verification: focused market-data tests `7 passed`; health route
│   │   │          conflicts `120 passed`
│   │   └── Boundary: closeout-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                service consolidation, candidate selection, or issue-label
│   │                change is made here
│   ├── G2.114 Service lifecycle candidate refresh after MarketDataService
│   │   ├── State: accepted; PR `#267` merged at
│   │   │          `3d0b72b68114effc9ba76aa3bea2d64edca15216`
│   │   ├── Evidence: `backend-service-lifecycle-candidate-refresh-after-market-data-2026-05-26.md`
│   │   ├── Current HEAD: `18af895af5fd09c1dff832b6f8bc968227711a28`
│   │   ├── Result: current scan covers service files=`152`, backend app
│   │   │          files=`575`, API files=`219`, backend test files=`200`,
│   │   │          service getter definitions=`15`, and candidate-like
│   │   │          definitions=`8`; the retired package-level
│   │   │          `market_data_service:get_market_data_service` no longer
│   │   │          appears as a candidate
│   │   ├── Decision: no LOW-risk direct implementation candidate is selected
│   │   │          from this refresh; remaining candidates are route-backed,
│   │   │          adapter-backed, Socket.IO-backed, dashboard-backed, task-backed,
│   │   │          or process-affected and require strategy/authorization before
│   │   │          source edits
│   │   └── Boundary: candidate-refresh-only; no backend source/test edit,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                getter deletion, service migration, or issue-label change
│   │                is made here
│   ├── G2.115 Service lifecycle strategy re-triage
│   │   ├── State: accepted; PR `#268` merged at
│   │   │          `dabe473f5d2616cfeda6c41ceeecee1bc5c57fb6`
│   │   ├── Evidence: `backend-service-lifecycle-strategy-retriage-2026-05-26.md`
│   │   ├── Current HEAD: `3d0b72b68114effc9ba76aa3bea2d64edca15216`
│   │   ├── Decision: split the remaining 8 candidates into strategy lanes:
│   │   │          medium route-backed candidates need an exact consumer matrix,
│   │   │          adapter-backed candidates need adapter/route ownership evidence,
│   │   │          Socket.IO/dashboard/task/process candidates stay on hold until
│   │   │          dedicated runtime or process evidence exists
│   │   ├── Next packet: create G2.116 exact consumer matrix for the medium
│   │   │          route-backed candidates
│   │   │          `get_announcement_service`, `get_email_service`, and
│   │   │          `get_watchlist_service`; do not authorize implementation yet
│   │   └── Boundary: strategy-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                implementation authorization, or issue-label change is made here
│   ├── G2.116 Medium route-backed exact consumer matrix
│   │   ├── State: accepted; PR `#269` merged at
│   │   │          `618820c89888887a7352999e32ec4285ccad836a`
│   │   ├── Evidence: `backend-medium-route-backed-service-consumer-matrix-2026-05-26.md`
│   │   ├── Current HEAD: `dabe473f5d2616cfeda6c41ceeecee1bc5c57fb6`
│   │   ├── Result: `get_announcement_service` has no direct API/adapter
│   │   │          getter consumers; routes use `get_announcement_service_dependency`
│   │   │          in 11 handlers; `get_email_service` is also route-dependency
│   │   │          backed but remains behind announcement; `get_watchlist_service`
│   │   │          still has 2 adapter files directly importing/calling the getter
│   │   ├── Decision: select `get_announcement_service` only as the next
│   │   │          authorization-candidate packet; do not authorize implementation
│   │   │          or source edits in this matrix
│   │   └── Boundary: evidence-matrix-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                implementation authorization, or issue-label change is made here
│   ├── G2.117 AnnouncementService getter-retirement authorization
│   │   ├── State: accepted; PR `#270` merged at
│   │   │          `ca1ad8da694f0174b5a80d414cc624d05865ec8f`
│   │   ├── Evidence: `backend-announcement-service-getter-retirement-authorization-2026-05-26.md`
│   │   ├── Current HEAD: `618820c89888887a7352999e32ec4285ccad836a`
│   │   ├── Decision: authorize only a future G2.118 implementation branch to
│   │   │          retire `announcement_service.py` `_announcement_service` and
│   │   │          `get_announcement_service`, while preserving
│   │   │          `AnnouncementService`, `install_announcement_service`,
│   │   │          `get_announcement_service_dependency`, announcement routes,
│   │   │          and OpenAPI exposure
│   │   ├── Evidence note: exact text scan has no API/adapter direct getter
│   │   │          consumers, but GitNexus graph still reports 11 route callers;
│   │   │          future implementation must verify route dependency behavior with
│   │   │          focused tests and exact post-change scans
│   │   └── Boundary: authorization-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                service migration, or issue-label change is made here
│   ├── G2.118 AnnouncementService getter-retirement implementation
│   │   ├── State: accepted; PR `#271` merged at
│   │   │          `4a2a21272deff876bc9fb5f1058c0682a7f4b5de`
│   │   ├── Evidence: `backend-announcement-service-getter-retirement-implementation-2026-05-26.md`
│   │   ├── Current HEAD: `ca1ad8da694f0174b5a80d414cc624d05865ec8f`
│   │   ├── Result: removes only `announcement_service.py`
│   │   │          `_announcement_service` and `get_announcement_service`,
│   │   │          changes the installer fallback to construct
│   │   │          `AnnouncementService()` directly, and updates focused
│   │   │          lifecycle coverage to patch the class seam instead of the
│   │   │          retired getter
│   │   ├── Verification: TDD red `1 failed`, focused green `4 passed`,
│   │   │          health route conflicts `120 passed`, touched-file ruff and
│   │   │          black checks passed; exact scan reports target getter
│   │   │          definitions=`0`, target singleton tokens=`0`, API direct
│   │   │          getter refs=`0`, route dependency handlers preserved=`11`
│   │   └── Boundary: source-capable but limited to `announcement_service.py`,
│   │                `test_announcement_service_lifecycle_di.py`,
│   │                `test_announcement_service_getter_retirement.py`,
│   │                governance report, generated artifact, task card, and
│   │                steward-tree update; no route/API, OpenAPI exposure,
│   │                frontend, PM2, OpenSpec, `AnnouncementService` deletion,
│   │                dependency deletion, or issue-label change is made here
│   ├── G2.119 AnnouncementService getter-retirement closeout
│   │   ├── State: accepted; PR `#272` merged at
│   │   │          `550ce654219385afa65fc4fbfaf6129b2d2a4ca3`
│   │   ├── Evidence: `backend-announcement-service-getter-retirement-closeout-2026-05-26.md`
│   │   ├── Current HEAD: `4a2a21272deff876bc9fb5f1058c0682a7f4b5de`
│   │   ├── Result: records PR `#271` merge and closes the AnnouncementService
│   │   │          getter-retirement implementation lane; current-head scan
│   │   │          confirms target getter definitions=`0`, target singleton
│   │   │          tokens=`0`, API direct getter refs=`0`, route dependency
│   │   │          handlers preserved=`11`, and focused route-dependency
│   │   │          regression coverage remains green
│   │   ├── Verification: focused tests `4 passed`, health route conflicts
│   │   │          `120 passed`, current-head exact scan files=`776`
│   │   └── Boundary: closeout-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                implementation authorization, or issue-label change is made here
│   ├── G2.120 Service lifecycle candidate refresh after AnnouncementService
│   │   ├── State: accepted; PR `#273` merged at
│   │   │          `1f117e1c7aa0333b6c0de272d697043f59f56bc9`
│   │   ├── Evidence: `backend-service-lifecycle-candidate-refresh-after-announcement-2026-05-26.md`
│   │   ├── Current HEAD: `550ce654219385afa65fc4fbfaf6129b2d2a4ca3`
│   │   ├── Result: current text scan confirms service files=`152`,
│   │   │          backend app files=`575`, API files=`219`, backend test
│   │   │          files=`201`, getter definitions=`14`, and module-lazy
│   │   │          candidates=`7`; `get_announcement_service` remains retired
│   │   │          in text scan and is removed from the active candidate pool
│   │   ├── Decision: select `get_email_service` as the next authorization
│   │   │          candidate because exact text scan shows no API or adapter
│   │   │          direct getter refs and notification routes use
│   │   │          `get_email_service_dependency`; hold `get_watchlist_service`
│   │   │          because two adapter files still import/call the getter
│   │   ├── Evidence note: GitNexus MCP still resolves retired
│   │   │          `get_announcement_service` graph callers after analyze, so
│   │   │          this packet treats exact current-head text scan as the
│   │   │          retirement truth and does not reopen the announcement lane
│   │   └── Boundary: candidate-refresh-only; no backend source/test edit,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                getter deletion, implementation authorization, or
│   │                issue-label change is made here
│   ├── G2.121 EmailService getter-retirement authorization
│   │   ├── State: accepted; PR `#274` merged at
│   │   │          `5b944a53a8a6f960ec1420cfd2a885c364d97bf3`
│   │   ├── Evidence: `backend-email-service-getter-retirement-authorization-2026-05-26.md`
│   │   ├── Current HEAD: `1f117e1c7aa0333b6c0de272d697043f59f56bc9`
│   │   ├── Result: authorizes only a future G2.122 implementation branch to
│   │   │          retire `email_service.py` `_email_service` and
│   │   │          `get_email_service`, while preserving `EmailService`,
│   │   │          `install_email_service`, `get_email_service_dependency`,
│   │   │          notification routes, and OpenAPI exposure
│   │   ├── Evidence note: exact scan shows direct API getter refs=`0`,
│   │   │          direct adapter getter refs=`0`, route dependency handlers=`6`,
│   │   │          and GitNexus impact MEDIUM / `6` with affected processes=`0`;
│   │   │          future implementation may update only the listed service and
│   │   │          focused tests after TDD red
│   │   └── Boundary: authorization-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                implementation, or issue-label change is made here
│   ├── G2.122 EmailService getter-retirement implementation
│   │   ├── State: accepted; PR `#275` merged at
│   │   │          `22021dc8e4faf5b2f206878fbd50bf553635ffc3`
│   │   ├── Evidence: `backend-email-service-getter-retirement-implementation-2026-05-26.md`
│   │   ├── Current HEAD: `5b944a53a8a6f960ec1420cfd2a885c364d97bf3`
│   │   ├── Result: removes only `email_service.py` `_email_service` and
│   │   │          `get_email_service`, changes the installer fallback to
│   │   │          construct `EmailService()` directly, removes obsolete fake
│   │   │          getter exposure from focused tests, and adds retirement
│   │   │          regression coverage
│   │   ├── Verification: TDD red `1 failed`, focused green `7 passed`,
│   │   │          health route conflicts `120 passed`, touched-file ruff and
│   │   │          black checks passed; exact scan reports target getter
│   │   │          definitions=`0`, target singleton tokens=`0`, app/API
│   │   │          direct getter refs=`0`, and route dependency handlers=`6`
│   │   └── Boundary: source-capable but limited to `email_service.py`,
│   │                `test_email_service_lifecycle_di.py`,
│   │                `test_notification_logging.py`,
│   │                `test_email_service_getter_retirement.py`, governance
│   │                report, generated artifact, task card, and steward-tree
│   │                update; no route/API, OpenAPI exposure, frontend, PM2,
│   │                OpenSpec, `EmailService` deletion, dependency deletion,
│   │                or issue-label change is made here
│   ├── G2.123 EmailService getter-retirement closeout
│   │   ├── State: accepted; PR `#276` merged at
│   │   │          `0b761555dd96865e571f7c9ebc1959b8254f52ef`
│   │   ├── Evidence: `backend-email-service-getter-retirement-closeout-2026-05-26.md`
│   │   ├── Current HEAD: `22021dc8e4faf5b2f206878fbd50bf553635ffc3`
│   │   ├── Result: records PR `#275` as merged, verifies current-head
│   │   │          getter-retirement state, and closes the EmailService getter
│   │   │          retirement lane as implementation-complete pending review
│   │   ├── Verification: parent PR `#275` state=`MERGED`, focused tests
│   │   │          `7 passed`, health route conflicts `120 passed`, exact scan
│   │   │          reports target getter definitions=`0`, target singleton
│   │   │          variable tokens=`0`, app/API direct getter refs=`0`, and
│   │   │          route dependency handlers=`6`
│   │   └── Boundary: closeout-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                implementation authorization, next-lane authorization, or
│   │                issue-label change is made here
│   ├── G2.124 Service lifecycle candidate refresh after EmailService
│   │   ├── State: accepted; PR `#277` merged at
│   │   │          `4ce4abf60fec2719644d9f64cd657bb0b7d3c8c5`
│   │   ├── Evidence: `backend-service-lifecycle-candidate-refresh-after-email-2026-05-26.md`
│   │   ├── Current HEAD: `0b761555dd96865e571f7c9ebc1959b8254f52ef`
│   │   ├── Result: refreshes the getter candidate pool after EmailService
│   │   │          retirement; confirms AnnouncementService and EmailService
│   │   │          getter definitions and singleton variables remain absent
│   │   ├── Candidate note: no low-risk direct implementation candidate is
│   │   │          selected here; `get_stock_search_service` is the next
│   │   │          authorization candidate only because text scan shows no API
│   │   │          or adapter direct getter calls, but GitNexus impact is
│   │   │          CRITICAL and must be explicitly accepted before any source edit
│   │   ├── Hold notes: `get_watchlist_service` remains held behind service
│   │   │          adapter seams; `get_market_data_service` requires symbol
│   │   │          disambiguation because text scan and GitNexus impact disagree;
│   │   │          `get_tdx_service`, `get_data_service`, `get_strategy_service`,
│   │   │          and `get_streaming_service` remain high/critical-risk lanes
│   │   └── Boundary: candidate-refresh-only; no backend source/test edit,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                getter deletion, implementation authorization, or
│   │                issue-label change is made here
│   ├── G2.125 StockSearchService getter-retirement authorization
│   │   ├── State: accepted; PR `#278` merged at
│   │   │          `d2f5a952740db94c382534b0810ba11588660132`
│   │   ├── Evidence: `backend-stock-search-service-getter-retirement-authorization-2026-05-26.md`
│   │   ├── Current HEAD: `4ce4abf60fec2719644d9f64cd657bb0b7d3c8c5`
│   │   ├── Result: authorizes only a future G2.126 implementation branch to
│   │   │          retire `stock_search_service.py` `_stock_search_service` and
│   │   │          `get_stock_search_service`, while preserving
│   │   │          `StockSearchService`, `install_stock_search_service`,
│   │   │          `get_stock_search_service_dependency`, route paths, response
│   │   │          contracts, and OpenAPI exposure
│   │   ├── Risk note: GitNexus impact is CRITICAL with impacted count=`6` and
│   │   │          affected processes=`11`; future implementation must update
│   │   │          d=1 route/test acceptance criteria before source edit
│   │   ├── Evidence note: text scan shows API direct getter calls=`0`, route
│   │   │          dependency handlers=`6`, service self-calls=`2`, and existing
│   │   │          P0 regression tests still assert the retired singleton/getter
│   │   │          behavior and must be rewritten during implementation
│   │   └── Boundary: authorization-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                implementation, or issue-label change is made here
│   ├── G2.126 StockSearchService getter-retirement authorization amendment
│   │   ├── State: accepted; PR `#279` merged at
│   │   │          `d23a4cf1de28972f3880495cce659540064b2576`
│   │   ├── Evidence: `backend-stock-search-service-getter-retirement-authorization-amendment-2026-05-26.md`
│   │   ├── Current HEAD: `d2f5a952740db94c382534b0810ba11588660132`
│   │   ├── Result: amends the future implementation scope before source work:
│   │   │          `stock_search_service/__init__.py` must also be allowed
│   │   │          because it re-exports `get_stock_search_service` in both the
│   │   │          import list and `__all__`
│   │   ├── Evidence: package re-export has legacy import at line `9` and
│   │   │          legacy `__all__` entry at line `20`; lifecycle baseline
│   │   │          `4 passed`, health route conflicts `120 passed`
│   │   └── Boundary: amendment-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                implementation, or issue-label change is made here
│   ├── G2.127 StockSearchService getter-retirement implementation
│   │   ├── State: accepted; PR `#280` merged at
│   │   │          `edf6c2673c6b38b614e43bb78b0ace8696990777`
│   │   ├── Evidence: `backend-stock-search-service-getter-retirement-implementation-2026-05-26.md`
│   │   ├── Current HEAD: `d23a4cf1de28972f3880495cce659540064b2576`
│   │   ├── Result: removes `stock_search_service.py` `_stock_search_service`
│   │   │          and `get_stock_search_service`, removes package re-export,
│   │   │          changes installer fallback to construct `StockSearchService()`,
│   │   │          updates legacy tests, and adds retirement regression coverage
│   │   ├── Verification: TDD red `1 failed`, focused green `12 passed`, health
│   │   │          route conflicts `120 passed`, touched-file ruff and black
│   │   │          checks passed, package import smoke passed; exact scan reports
│   │   │          target getter definitions=`0`, target singleton tokens=`0`,
│   │   │          package re-export=`0`, app/API/test direct getter calls=`0`,
│   │   │          and route dependency handlers=`6`
│   │   └── Boundary: source-capable but limited to stock search service module,
│   │                package re-export, focused tests, governance report,
│   │                generated artifact, task card, and steward-tree update; no
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                `StockSearchService` deletion, dependency deletion, or
│   │                issue-label change is made here
│   ├── G2.128 StockSearchService getter-retirement closeout
│   │   ├── State: accepted; PR `#281` merged at
│   │   │          `dbef525d9b539674d69f75fde59b372d52298913`
│   │   ├── Evidence: `backend-stock-search-service-getter-retirement-closeout-2026-05-26.md`
│   │   ├── Current HEAD: `edf6c2673c6b38b614e43bb78b0ace8696990777`
│   │   ├── Result: records PR `#280` as merged and verifies current-head
│   │   │          StockSearchService getter-retirement state
│   │   ├── Verification: parent PR `#280` state=`MERGED`, focused tests
│   │   │          `12 passed`, health route conflicts `120 passed`, exact scan
│   │   │          reports getter=`0`, singleton=`0`, package re-export=`0`,
│   │   │          app/API/test direct getter calls=`0`, route dependency
│   │   │          handlers=`6`
│   │   └── Boundary: closeout-only; no backend source/test edit, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, getter deletion,
│   │                implementation authorization, next-lane authorization, or
│   │                issue-label change is made here
│   ├── G2.129 Service lifecycle candidate refresh after StockSearchService
│   │   ├── State: accepted; PR `#282` merged at
│   │   │          `cc32d0c2ba52cf7a9669ec1e9976740a84fd5be9`
│   │   ├── Evidence: `backend-service-lifecycle-di-candidate-refresh-after-stock-search-2026-05-26.md`
│   │   ├── Current HEAD: `dbef525d9b539674d69f75fde59b372d52298913`
│   │   ├── Result: refreshes the remaining service getter pool after
│   │   │          StockSearchService closeout; no direct implementation
│   │   │          candidate is selected
│   │   ├── Verification: service files=`152`, backend app files=`575`,
│   │   │          API files=`219`, tests=`203`, getter definitions=`12`;
│   │   │          Announcement/Email/StockSearch retired getter definitions
│   │   │          and singleton tokens remain `0`
│   │   ├── Candidate decision: `get_watchlist_service` is selected only as a
│   │   │          future authorization-candidate lane because GitNexus reports
│   │   │          MEDIUM risk / impacted=`15` / direct=`9` / processes=`0`,
│   │   │          while adapter fallback seams and seven route dependency
│   │   │          handlers still require explicit authorization scope
│   │   ├── Holds: `get_market_data_service` remains held for graph/text symbol
│   │   │          disambiguation; `get_tdx_service`, `get_data_service`,
│   │   │          `get_strategy_service`, and `get_streaming_service` remain
│   │   │          high-risk design lanes
│   │   └── Boundary: candidate-refresh-only; no backend source/test edit,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                getter deletion, implementation authorization, or
│   │                issue-label change is made here
│   ├── G2.130 WatchlistService getter-retirement authorization
│   │   ├── State: accepted; PR `#283` merged at
│   │   │          `35dcc90cd9a242e8906107a01abf1649d77737ea`
│   │   ├── Evidence: `backend-watchlist-service-getter-retirement-authorization-2026-05-26.md`
│   │   ├── Current HEAD: `cc32d0c2ba52cf7a9669ec1e9976740a84fd5be9`
│   │   ├── Result: authorizes only a future implementation branch to retire
│   │   │          `watchlist_service.py` `get_watchlist_service` and
│   │   │          `_watchlist_service`, while preserving `WatchlistService`,
│   │   │          `install_watchlist_service`,
│   │   │          `get_watchlist_service_dependency`, route paths, response
│   │   │          contracts, and OpenAPI exposure
│   │   ├── Verification: baseline focused watchlist tests `9 passed`;
│   │   │          current scan shows getter definitions=`1`, singleton
│   │   │          tokens=`74`, app/API direct getter calls=`0`, route
│   │   │          dependency handlers=`7`, adapter fallback files=`2`,
│   │   │          tests with getter refs=`4`
│   │   ├── Risk note: GitNexus impact is MEDIUM with impacted=`15`,
│   │   │          direct=`9`, processes=`0`; future implementation must cover
│   │   │          two adapter fallback helpers and seven route dependency
│   │   │          handlers in acceptance criteria
│   │   └── Boundary: authorization-only; no backend source/test edit,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                getter deletion, implementation, or issue-label change is
│   │                made here
│   ├── G2.131 WatchlistService getter-retirement implementation
│   │   ├── State: accepted and merged by PR `#284`
│   │   ├── Evidence: `backend-watchlist-service-getter-retirement-implementation-2026-05-26.md`
│   │   ├── Merge commit: `ccadd5e0560c4fa1fab7fae130a8b64e624352bc`
│   │   ├── Result: removes `watchlist_service.py` `get_watchlist_service`
│   │   │          and module-level `_watchlist_service`, removes both adapter
│   │   │          fallback imports/calls, and preserves `WatchlistService`,
│   │   │          `install_watchlist_service`,
│   │   │          `get_watchlist_service_dependency`, route paths, response
│   │   │          contracts, and OpenAPI exposure
│   │   ├── Verification: TDD red `2 failed, 1 passed`, focused watchlist
│   │   │          tests `28 passed`, health route conflicts `120 passed`,
│   │   │          touched-file ruff passed, black check passed, import smoke
│   │   │          passed; exact scan reports service getter definitions=`0`,
│   │   │          service singleton assignments=`0`, adapter fallback
│   │   │          imports=`0`, adapter public getter calls=`0`, app/API
│   │   │          public getter calls=`0`, route dependency handlers=`7`
│   │   └── Boundary: source-capable but limited to WatchlistService lifecycle
│   │                module, two watchlist adapter fallback helpers, focused
│   │                tests, governance report, generated artifact, task card,
│   │                and steward-tree update; no route/API, OpenAPI exposure,
│   │                frontend, PM2, OpenSpec, service class deletion, route
│   │                dependency deletion, or issue-label change is made here
│   ├── G2.132 WatchlistService getter-retirement closeout
│   │   ├── State: accepted and merged by PR `#285`
│   │   ├── Evidence: `backend-watchlist-service-getter-retirement-closeout-2026-05-26.md`
│   │   ├── Merge commit: `f0e0e37726140499b2e6b25cdad96739fc8f5462`
│   │   ├── Result: records PR `#284` as merged and closes the
│   │   │          WatchlistService getter-retirement lane without changing
│   │   │          runtime source, tests, route paths, response contracts, or
│   │   │          OpenAPI exposure
│   │   ├── Verification: parent PR state `MERGED`; focused watchlist tests
│   │   │          `28 passed`; health route conflicts `120 passed`; exact
│   │   │          scan reports service getter definitions=`0`, service
│   │   │          singleton assignments=`0`, adapter fallback imports=`0`,
│   │   │          adapter public getter calls=`0`, app/API public getter
│   │   │          calls=`0`, route dependency handlers=`7`
│   │   └── Boundary: closeout-only; no source/test edit, runtime behavior,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                service symbol deletion, route dependency deletion, or
│   │                issue-label change is made here
│   ├── G2.133 Service lifecycle candidate refresh after WatchlistService
│   │   ├── State: accepted and merged by PR `#286`
│   │   ├── Evidence: `backend-service-lifecycle-di-candidate-refresh-after-watchlist-2026-05-26.md`
│   │   ├── Merge commit: `bc2d2a891787484b7fc65dd8fec61e19d66345bf`
│   │   ├── Result: confirms Announcement/Email/StockSearch/Watchlist retired
│   │   │          public getter definitions remain `0`, scans service files
│   │   │          `152`, app files `575`, API files `219`, tests `204`,
│   │   │          and remaining service getter definitions `11`
│   │   ├── Candidate decision: no direct implementation lane selected;
│   │   │          six LOW graph-risk candidates are shared
│   │   │          `IntegratedServices` facade getters in
│   │   │          `web/backend/app/services/__init__.py`; `get_market_data_service`
│   │   │          remains held for graph/text symbol disambiguation; `get_tdx_service`,
│   │   │          `get_data_service`, `get_strategy_service`, and
│   │   │          `get_streaming_service` remain held at HIGH/CRITICAL risk
│   │   └── Boundary: refresh-only; no source/test edit, IntegratedServices
│   │                facade deletion, route/API, OpenAPI exposure, frontend,
│   │                PM2, OpenSpec, implementation authorization, or issue-label
│   │                change is made here
│   ├── G2.134 IntegratedServices facade getter ownership decision
│   │   ├── State: accepted and merged by PR `#287`
│   │   ├── Evidence: `backend-integrated-services-facade-getter-ownership-decision-2026-05-26.md`
│   │   ├── Merge commit: `65498c4565db877ee187f9ceb6dd140b7e4db7fd`
│   │   ├── Decision: treat `web/backend/app/services/__init__.py` getters
│   │   │          as a shared IntegratedServices compatibility facade owned
│   │   │          by the composition root, not as independent route-surface
│   │   │          singleton getters
│   │   ├── Result: retain `get_integrated_services` and
│   │   │          `get_market_data_service`; mark only
│   │   │          `get_trading_data_service`, `get_analysis_data_service`,
│   │   │          `get_data_api_service`, `get_database_service`,
│   │   │          `get_websocket_service`, and `get_cache_service` as eligible
│   │   │          for a future unused-facade retirement authorization packet;
│   │   │          risk helper facades are out of the current service-getter queue
│   │   └── Boundary: decision-only; no source/test edit, facade deletion,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                implementation authorization, or issue-label change is
│   │                made here
│   ├── G2.135 Unused IntegratedServices service-facade getter retirement authorization
│   │   ├── State: accepted and merged by PR `#288`
│   │   ├── Evidence: `backend-unused-integrated-services-facade-getter-retirement-authorization-2026-05-26.md`
│   │   ├── Merge commit: `4aaa5a88eafa6d43df383a083c15642e88205e4d`
│   │   ├── Authorization: future source lane may remove only
│   │   │          `get_trading_data_service`, `get_analysis_data_service`,
│   │   │          `get_data_api_service`, `get_database_service`,
│   │   │          `get_websocket_service`, and `get_cache_service` from
│   │   │          `web/backend/app/services/__init__.py`, with one focused
│   │   │          test file and standard implementation evidence
│   │   ├── Locked scope: `get_integrated_services`, `get_market_data_service`,
│   │   │          risk helper facades, route/API, OpenAPI, PM2, frontend,
│   │   │          OpenSpec, issue labels, and HIGH/CRITICAL service getters
│   │   │          remain out of scope
│   │   └── Boundary: authorization-only; no source/test edit, facade deletion,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                implementation, or issue-label change is made here
│   ├── G2.136 Unused IntegratedServices service-facade getter retirement implementation
│   │   ├── State: accepted and merged by PR `#289`
│   │   ├── Evidence: `backend-unused-integrated-services-facade-getter-retirement-implementation-2026-05-26.md`
│   │   ├── Merge commit: `541a225b5cbc90807d8cc7af20d0ffd42b07fd2d`
│   │   ├── Result: removes only `get_trading_data_service`,
│   │   │          `get_analysis_data_service`, `get_data_api_service`,
│   │   │          `get_database_service`, `get_websocket_service`, and
│   │   │          `get_cache_service` from `web/backend/app/services/__init__.py`
│   │   │          and adds focused regression coverage
│   │   ├── Preserved scope: `get_integrated_services`,
│   │   │          `get_market_data_service`, all risk helper facades, route/API,
│   │   │          OpenAPI, PM2, frontend, OpenSpec, and issue labels remain
│   │   │          unchanged
│   │   ├── Verification: pre-edit GitNexus impact LOW / impacted `0` for all
│   │   │          six removed symbols; TDD red `1 failed, 1 passed`; focused
│   │   │          test `2 passed`; import smoke reports removed absent and
│   │   │          locked callable; exact scan reports removed definitions=`0`
│   │   │          and locked definitions=`1`; Ruff and Black passed
│   │   └── Boundary: source-capable but limited to one service facade module,
│   │                one focused test, report, generated artifact, task card,
│   │                and steward-tree update
│   ├── G2.137 Unused IntegratedServices service-facade getter retirement closeout
│   │   ├── State: accepted and merged by PR `#290`
│   │   ├── Evidence: `backend-unused-integrated-services-facade-getter-retirement-closeout-2026-05-26.md`
│   │   ├── Merge commit: `090c0c30a7ac64c75e30febce1b3f6e4d20eee1c`
│   │   ├── Result: records PR `#289` as merged and closes the unused
│   │   │          IntegratedServices service-facade getter retirement lane
│   │   │          without changing runtime source, tests, route paths,
│   │   │          response contracts, or OpenAPI exposure
│   │   ├── Verification: parent PR state `MERGED`; focused closeout test
│   │   │          `2 passed`; import smoke reports removed absent and locked
│   │   │          callable; exact scan reports retired definitions=`0` and
│   │   │          locked definitions=`1`
│   │   └── Boundary: closeout-only; no source/test edit, runtime behavior,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                implementation, or issue-label change is made here
│   ├── G2.138 Service lifecycle candidate refresh after IntegratedServices facade retirement
│   │   ├── State: accepted and merged by PR `#291`
│   │   ├── Evidence: `backend-service-lifecycle-candidate-refresh-after-integrated-facade-retirement-2026-05-26.md`
│   │   ├── Merge commit: `2d51cbd52bc37dae2ae5f59855bcdb70d41f169c`
│   │   ├── Result: refreshes the remaining service lifecycle DI candidate
│   │   │          pool after G2.137 closeout and selects only a future
│   │   │          authorization candidate, not an implementation lane
│   │   ├── Verification: service files=`152`, backend app files=`575`,
│   │   │          API files=`219`, tests=`205`, service getter
│   │   │          definitions=`54`, root facade getters=`7`, FastAPI
│   │   │          dependency/provider getters=`9`; retired IntegratedServices
│   │   │          facade definitions remain `0` and locked facade definitions
│   │   │          remain `1`
│   │   ├── Candidate decision: select `get_backtest_engine` /
│   │   │          `_backtest_engine` only for a future authorization package;
│   │   │          GitNexus impact is LOW with impacted=`0`, direct=`0`,
│   │   │          processes=`0`, and exact text scan finds no backend code
│   │   │          caller outside the defining service file
│   │   ├── Holds: `get_tdx_service` remains CRITICAL with impacted=`6`,
│   │   │          direct=`2`, processes=`5`; `get_data_service`,
│   │   │          `get_strategy_service`, `get_streaming_service`,
│   │   │          root/risk facades, and active FastAPI dependency/provider
│   │   │          seams remain out of scope
│   │   └── Boundary: candidate-refresh-only; no backend source/test edit,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                getter deletion, implementation authorization, or
│   │                issue-label change is made here
│   ├── G2.139 BacktestEngine singleton/getter retirement authorization
│   │   ├── State: accepted and merged by PR `#292`
│   │   ├── Evidence: `backend-backtest-engine-getter-retirement-authorization-2026-05-26.md`
│   │   ├── Merge commit: `0f78609e25898181ea5653edc7350efc03a3bb9b`
│   │   ├── Result: authorizes only a future narrow implementation lane to
│   │   │          retire `_backtest_engine` and `get_backtest_engine` from
│   │   │          `web/backend/app/services/backtest_engine.py`
│   │   ├── Preserved scope: `BacktestConfig`, `BacktestResult`,
│   │   │          `BacktestEngine`, all BacktestEngine methods, route/API,
│   │   │          OpenAPI exposure, frontend, PM2, OpenSpec, issue labels,
│   │   │          and unrelated service lifecycle candidates remain out of
│   │   │          scope
│   │   ├── Verification: GitNexus impact for `get_backtest_engine` is LOW
│   │   │          with impacted=`0`, direct=`0`, processes=`0`; exact scan
│   │   │          shows `BacktestEngine` definition=`1`, getter definition=`1`,
│   │   │          `_backtest_engine` token count=`5`, and backend code
│   │   │          references only in the defining service file; import smoke
│   │   │          confirms class/config/result/getter importability
│   │   └── Boundary: authorization-only; no backend source/test edit,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                getter deletion, implementation, or issue-label change is
│   │                made here
│   ├── G2.140 BacktestEngine singleton/getter retirement implementation
│   │   ├── State: accepted and merged by PR `#293`
│   │   ├── Evidence: `backend-backtest-engine-getter-retirement-implementation-2026-05-26.md`
│   │   ├── Merge commit: `62cf56cc8736c3784f8b7cc9ac5cc21a52d39423`
│   │   ├── Result: removes only `_backtest_engine` and
│   │   │          `get_backtest_engine` from
│   │   │          `web/backend/app/services/backtest_engine.py` and adds a
│   │   │          focused regression test
│   │   ├── Preserved scope: `BacktestConfig`, `BacktestResult`,
│   │   │          `BacktestEngine`, existing BacktestEngine methods,
│   │   │          route/API, OpenAPI exposure, frontend, PM2, OpenSpec, issue
│   │   │          labels, and unrelated service lifecycle candidates remain
│   │   │          unchanged
│   │   ├── Verification: pre-edit GitNexus impact LOW / impacted=`0`;
│   │   │          TDD red `1 failed, 1 passed`; focused green `2 passed`;
│   │   │          exact scan reports getter definition=`0` and singleton
│   │   │          token count=`0`; import smoke confirms preserved types and
│   │   │          removed legacy surfaces; Ruff and Black passed
│   │   └── Boundary: source-capable but limited to one backend service file,
│   │                one focused test, report, generated artifact, task card,
│   │                and steward-tree update
│   ├── G2.141 BacktestEngine singleton/getter retirement closeout
│   │   ├── State: accepted and merged by PR `#294`
│   │   ├── Evidence: `backend-backtest-engine-getter-retirement-closeout-2026-05-26.md`
│   │   ├── Merge commit: `32d0cfb1e02d1207301e632b44a94e74efdddf69`
│   │   ├── Result: records PR `#293` as merged and closes the
│   │   │          BacktestEngine singleton/getter retirement lane without
│   │   │          changing runtime source, tests, route paths, response
│   │   │          contracts, or OpenAPI exposure
│   │   ├── Verification: parent PR state `MERGED`; focused closeout test
│   │   │          `2 passed`; exact scan reports getter definition=`0`,
│   │   │          singleton token count=`0`, and `BacktestEngine`
│   │   │          definition=`1`; import smoke confirms preserved types and
│   │   │          removed legacy surfaces
│   │   └── Boundary: closeout-only; no source/test edit, runtime behavior,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                implementation, or issue-label change is made here
│   ├── G2.142 Service lifecycle candidate refresh after BacktestEngine
│   │   ├── State: accepted and merged by PR `#295`
│   │   ├── Evidence: `backend-service-lifecycle-candidate-refresh-after-backtest-2026-05-26.md`
│   │   ├── Current HEAD: `32d0cfb1e02d1207301e632b44a94e74efdddf69`
│   │   ├── Merge commit: `c11dfb858200aaed46beee50c15e022c86408b54`
│   │   ├── Result: refreshes the remaining service lifecycle DI candidate
│   │   │          pool after BacktestEngine closeout and selects no direct
│   │   │          implementation candidate
│   │   ├── Verification: service files=`152`, backend app files=`575`,
│   │   │          API files=`219`, tests=`206`, service getter
│   │   │          definitions=`53`, root facade getters=`7`, FastAPI
│   │   │          dependency/provider getters=`9`, zero-external-reference
│   │   │          getters=`0`; BacktestEngine retired tokens remain `0`
│   │   ├── High-risk holds: `get_tdx_service` CRITICAL impacted=`6`,
│   │   │          `get_data_service` CRITICAL impacted=`5`,
│   │   │          `get_strategy_service` CRITICAL impacted=`13`, and
│   │   │          `get_streaming_service` HIGH impacted=`9`; these require
│   │   │          design decomposition before implementation authorization
│   │   └── Boundary: candidate-refresh-only; no backend source/test edit,
│   │                route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │                getter deletion, implementation authorization, or
│   │                issue-label change is made here
│   ├── G2.143 High-risk service getter strategy decision package
│   │   ├── State: accepted and merged by PR `#296`
│   │   ├── Evidence: `backend-high-risk-service-getter-strategy-decision-2026-05-26.md`
│   │   ├── Current HEAD: `c11dfb858200aaed46beee50c15e022c86408b54`
│   │   ├── Merge commit: `4b361b6c73972ad3b3d9b02bc0488946c5271882`
│   │   ├── Result: splits the exhausted low-risk service getter queue into
│   │   │          six explicit tracks: Dashboard/TDX, Indicator/Data,
│   │   │          Strategy adapter, Realtime streaming/socket, root facade
│   │   │          compatibility, and route dependency/provider governance
│   │   ├── Verification: parent PR `#295` is merged; service files=`152`,
│   │   │          backend app files=`575`, API files=`219`, tests=`206`,
│   │   │          service getter definitions=`53`, zero-external-reference
│   │   │          getters=`0`; GitNexus keeps `get_tdx_service`,
│   │   │          `get_data_service`, and `get_strategy_service` at
│   │   │          CRITICAL and `get_streaming_service` at HIGH
│   │   ├── Decision: no direct source lane is selected; recommend a separate
│   │   │          Realtime streaming/socket authorization package as the
│   │   │          first downstream design track because it is HIGH rather
│   │   │          than CRITICAL and has no current process-flow participation
│   │   └── Boundary: design-decision-only; no backend source/test edit,
│   │                getter deletion, route/API, OpenAPI exposure, frontend,
│   │                PM2, OpenSpec, implementation authorization, or
│   │                issue-label change is made here
│   ├── G2.144 Realtime streaming/socket authorization package
│   │   ├── State: accepted and merged by PR `#297`
│   │   ├── Evidence: `backend-realtime-streaming-socket-authorization-package-2026-05-26.md`
│   │   ├── Parent: G2.143 accepted and merged by PR `#296`
│   │   ├── Current HEAD: `4b361b6c73972ad3b3d9b02bc0488946c5271882`
│   │   ├── Merge commit: `3c27963c86bc095f7f28129d5b47d9257367a31f`
│   │   ├── Result: defines the smallest first implementation candidate for
│   │   │          the realtime streaming/socket track as Socket.IO manager
│   │   │          consumer-injection only, with no getter deletion
│   │   ├── Verification: GitNexus impact for `get_streaming_service` remains
│   │   │          HIGH with impacted=`9`, direct=`9`, processes=`0`;
│   │   │          source shape scan finds `socketio_manager.py` has `9`
│   │   │          `get_streaming_service` tokens, while
│   │   │          `aggregation_streaming_bridge.py` already accepts optional
│   │   │          `streaming_service` and is not in the first source lane
│   │   ├── Authorization if approved: G2.145 may edit only
│   │   │          `web/backend/app/core/socketio_manager.py` plus focused
│   │   │          socket manager tests and governance artifacts to replace
│   │   │          repeated direct getter use with a manager-level injected
│   │   │          streaming dependency
│   │   └── Boundary: authorization-only; no backend source/test edit,
│   │                getter deletion, route/API, OpenAPI exposure, frontend,
│   │                PM2, OpenSpec, implementation, or issue-label change is
│   │                made here
│   ├── G2.145 Realtime socket manager consumer-injection implementation
│   │   ├── State: accepted and merged by PR `#298`
│   │   ├── Evidence: `backend-realtime-socket-manager-consumer-injection-implementation-2026-05-26.md`
│   │   ├── Parent: G2.144 accepted and merged by PR `#297`
│   │   ├── Current HEAD: `3c27963c86bc095f7f28129d5b47d9257367a31f`
│   │   ├── Merge commit: `fd04b30d6ff597209be0e923dd62d2cf1b38ee82`
│   │   ├── Result: adds a manager-level `streaming_service` dependency to
│   │   │          `MySocketIOManager`; Socket.IO namespace and manager
│   │   │          streaming consumers use that injected dependency instead of
│   │   │          repeated direct handler-level `get_streaming_service` calls
│   │   ├── Verification: pre-edit GitNexus impact records
│   │   │          `get_streaming_service` HIGH impacted=`9`, direct=`9`,
│   │   │          processes=`0`, and `MySocketIOManager` LOW impacted=`0`;
│   │   │          TDD red `2 failed`, focused green `2 passed`; Ruff and
│   │   │          Black passed; token scan reports `get_streaming_service`
│   │   │          total refs=`2` and handler-level refs=`0`
│   │   ├── Baseline blockers: existing `test_socketio_manager.py` and
│   │   │          `test_socketio_streaming_integration.py` still import
│   │   │          absent `get_socketio_manager` / `reset_socketio_manager`;
│   │   │          `test_realtime_streaming_service.py` has a pre-existing
│   │   │          naive/aware datetime assertion failure outside this lane
│   │   └── Boundary: source-capable but limited to `socketio_manager.py`,
│   │                one focused test, report, generated artifact, task card,
│   │                and steward-tree update; no getter deletion,
│   │                `realtime_streaming_service.py` edit,
│   │                `aggregation_streaming_bridge.py` edit, route/API,
│   │                OpenAPI, frontend, PM2, OpenSpec, or issue-label change
│   │                is made here
│   ├── G2.146 Realtime socket manager consumer-injection closeout
│   │   ├── State: accepted and merged by PR `#299`
│   │   ├── Evidence: `backend-realtime-socket-manager-consumer-injection-closeout-2026-05-26.md`
│   │   ├── Parent: G2.145 accepted and merged by PR `#298`
│   │   ├── Current HEAD: `fd04b30d6ff597209be0e923dd62d2cf1b38ee82`
│   │   ├── Merge commit: `e42f4b11524da98cbf22f45807459f8984c9ebed`
│   │   ├── Result: verifies the merged Socket.IO manager consumer-injection
│   │   │          lane and closes it without opening another source edit
│   │   ├── Verification: PR `#298` is merged; focused
│   │   │          `test_realtime_socket_manager_streaming_dependency.py`
│   │   │          reports `2 passed`; token scan reports
│   │   │          `get_streaming_service` total refs=`2` and
│   │   │          handler-level refs=`0`
│   │   ├── Baseline blockers confirmed: `test_socketio_manager.py` still
│   │   │          imports absent `get_socketio_manager`,
│   │   │          `test_socketio_streaming_integration.py` still imports
│   │   │          absent `reset_socketio_manager`, and
│   │   │          `test_realtime_streaming_service.py` still has a
│   │   │          naive/aware datetime comparison failure
│   │   └── Boundary: closeout-only; no backend source/test edit,
│   │                getter deletion, route/API, OpenAPI exposure, frontend,
│   │                PM2, OpenSpec, issue-label change, or new
│   │                implementation authorization is made here
│   ├── G2.147 Realtime socket baseline blocker routing decision
│   │   ├── State: accepted and merged by PR `#300`
│   │   ├── Evidence: `backend-realtime-socket-baseline-blocker-routing-decision-2026-05-26.md`
│   │   ├── Parent: G2.146 accepted and merged by PR `#299`
│   │   ├── Current HEAD: `e42f4b11524da98cbf22f45807459f8984c9ebed`
│   │   ├── Result: routes remaining realtime/socket blockers into two
│   │   │          independent future decision tracks instead of reopening
│   │   │          G2.145 or expanding G2.146 closeout
│   │   ├── Verification: focused
│   │   │          `test_realtime_socket_manager_streaming_dependency.py`
│   │   │          still reports `2 passed`; source scan finds
│   │   │          `socketio_manager.py` has `0` `get_socketio_manager` and
│   │   │          `0` `reset_socketio_manager` tokens, while legacy tests
│   │   │          still reference those names; realtime streaming service
│   │   │          test still reports `42 passed, 1 failed`
│   │   ├── Decision: split next work into G2.148 Socket.IO legacy export
│   │   │          contract authorization and G2.149 realtime datetime test
│   │   │          debt authorization; no source/test edit is authorized here
│   │   └── Boundary: decision-only; no backend source/test edit, getter
│   │                deletion, route/API, OpenAPI exposure, frontend, PM2,
│   │                OpenSpec, issue-label change, or implementation
│   │                authorization is made here
│   ├── G2.148 Socket.IO legacy export contract authorization
│   │   ├── State: accepted and merged by PR `#301`
│   │   ├── Evidence: `backend-socketio-legacy-export-contract-authorization-2026-05-26.md`
│   │   ├── Parent: G2.147 accepted and merged by PR `#300`
│   │   ├── Current HEAD: `3b1d67ceb52a5c3ccbbbafb534895c6a70aa6d2e`
│   │   ├── Result: routes the legacy Socket.IO export collection blocker to
│   │   │          a future test-only import-alignment lane instead of
│   │   │          restoring exports from `socketio_manager.py`
│   │   ├── Verification: focused
│   │   │          `test_realtime_socket_manager_streaming_dependency.py`
│   │   │          reports `2 passed`; collect-only still fails for
│   │   │          `test_socketio_manager.py` on missing
│   │   │          `get_socketio_manager` and for
│   │   │          `test_socketio_streaming_integration.py` on missing
│   │   │          `reset_socketio_manager`
│   │   ├── Decision: canonical helper path is
│   │   │          `app.core._socketio_manager_singleton`; runtime composition
│   │   │          already imports from that helper, so the next lane should
│   │   │          align stale test imports rather than widen
│   │   │          `app.core.socketio_manager`
│   │   └── Boundary: decision-only; no backend source/test edit, helper
│   │                alias restoration, realtime datetime fix, route/API,
│   │                OpenAPI exposure, frontend, PM2, OpenSpec, issue-label
│   │                change, or implementation work is performed here
│   ├── G2.150 Socket.IO test import alignment
│   │   ├── State: accepted and merged by PR `#302`
│   │   ├── Evidence: `backend-socketio-test-import-alignment-2026-05-26.md`
│   │   ├── Parent: G2.148 accepted and merged by PR `#301`
│   │   ├── Current HEAD: `deb182e7f3ba7e50d0cc982c51248826e522dacd`
│   │   ├── Result: aligns stale Socket.IO test imports to
│   │   │          `app.core._socketio_manager_singleton` without widening
│   │   │          `app.core.socketio_manager`
│   │   ├── Verification: red collect-only failures reproduced for missing
│   │   │          `get_socketio_manager` and `reset_socketio_manager`; after
│   │   │          alignment, `test_socketio_manager.py` collects `26` tests,
│   │   │          `test_socketio_streaming_integration.py` collects `20`
│   │   │          tests, focused consumer-injection regression reports
│   │   │          `2 passed`, ruff touched tests reports
│   │   │          `All checks passed`, and `test_socketio_manager.py`
│   │   │          reports `26 passed`
│   │   ├── Newly exposed debt:
│   │   │          `test_socketio_streaming_integration.py` full suite now
│   │   │          reaches behavior assertions and reports `1 failed, 19
│   │   │          passed` for `test_exception_during_subscription`; this is
│   │   │          routed outside G2.150
│   │   └── Boundary: test-only; no backend runtime source edit, helper alias
│   │              restoration, realtime datetime fix, route/API, OpenAPI
│   │              exposure, frontend, PM2, OpenSpec, issue-label change, or
│   │              GitHub issue state change is performed here
│   ├── G2.151 Socket.IO stream-error emission triage
│   │   ├── State: accepted and merged by PR `#303`
│   │   ├── Evidence: `backend-socketio-stream-error-emission-triage-2026-05-26.md`
│   │   ├── Parent: G2.150 accepted and merged by PR `#302`
│   │   ├── Current HEAD: `34bb3873149aee0b2e4cd06e63a45484a33a068f`
│   │   ├── Result: classifies the newly exposed
│   │   │          `test_exception_during_subscription` failure as test
│   │   │          patch-target drift after Socket.IO manager consumer
│   │   │          injection, not as proven runtime error-emission breakage
│   │   ├── Verification: single-test reproduction still fails on missing
│   │   │          `stream_error`; diagnostic with stale
│   │   │          `app.core.socketio_manager.get_streaming_service` patch
│   │   │          emits `stream_subscribed`, while diagnostic patching
│   │   │          `manager.streaming_service.subscribe` emits
│   │   │          `stream_error`
│   │   ├── Decision: authorize a future G2.152 test-only patch-target
│   │   │          alignment lane; do not edit runtime source or widen
│   │   │          `socketio_manager.py`
│   │   └── Boundary: triage-only; no backend source/test edit, helper alias
│   │              restoration, realtime datetime fix, route/API, OpenAPI
│   │              exposure, frontend, PM2, OpenSpec, issue-label change, or
│   │              GitHub issue state change is performed here
│   ├── G2.152 Socket.IO stream-error test patch-target alignment
│   │   ├── State: accepted and merged by PR `#304`
│   │   ├── Evidence: `backend-socketio-stream-error-test-patch-alignment-2026-05-26.md`
│   │   ├── Parent: G2.151 accepted and merged by PR `#303`
│   │   ├── Current HEAD: `9288c3a7cdb8428c5ef984b9ba79e7e8fb2135dc`
│   │   ├── Result: aligns
│   │   │          `test_exception_during_subscription` to patch
│   │   │          `manager.streaming_service.subscribe`, matching the
│   │   │          current Socket.IO manager-level streaming dependency
│   │   ├── Verification: red single-test failure reproduced before edit;
│   │   │          after alignment, the single test reports `1 passed`,
│   │   │          `test_socketio_streaming_integration.py` reports
│   │   │          `20 passed`, `test_socketio_manager.py` reports
│   │   │          `26 passed, 1 warning`, consumer-injection focused
│   │   │          regression reports `2 passed`, and touched-test ruff
│   │   │          reports `All checks passed`
│   │   └── Boundary: test-only; no backend runtime source edit, helper alias
│   │              restoration, realtime datetime fix, route/API, OpenAPI
│   │              exposure, frontend, PM2, OpenSpec, issue-label change, or
│   │              GitHub issue state change is performed here
│   ├── G2.149 Realtime streaming datetime test authorization
│   │   ├── State: accepted and merged by PR `#305`
│   │   ├── Evidence: `backend-realtime-streaming-datetime-test-authorization-2026-05-26.md`
│   │   ├── Parent: G2.152 accepted and merged by PR `#304`
│   │   ├── Merge commit: `58bdc319c3ca00819b6b4fe7fefa59a5a321ba9d`
│   │   ├── Result: classifies
│   │   │          `test_realtime_streaming_service.py::TestStreamSubscriber::test_subscriber_update_activity`
│   │   │          as a realtime streaming timestamp contract
│   │   │          inconsistency, not a Socket.IO failure
│   │   ├── Verification: focused realtime streaming service suite reports
│   │   │          `1 failed, 42 passed`; diagnostic shows initial
│   │   │          `StreamSubscriber.subscribed_at` has `tzinfo=None` from
│   │   │          `datetime.utcnow`, while `update_activity()` assigns
│   │   │          `datetime.now(timezone.utc)` with `tzinfo=UTC`
│   │   ├── Decision: authorize a future G2.153 source plus focused-test lane
│   │   │          for timezone-aware realtime streaming timestamps, covering
│   │   │          `StreamSubscriber.subscribed_at` and reviewing
│   │   │          `StreamData.created_at`
│   │   └── Boundary: authorization-only; no backend source/test edit,
│   │              Socket.IO change, realtime timestamp implementation,
│   │              route/API, OpenAPI exposure, frontend, PM2, OpenSpec,
│   │              issue-label change, or GitHub issue state change is
│   │              performed here
│   ├── G2.153 Realtime streaming timezone-aware timestamps
│   │   ├── State: accepted and merged by PR `#306`
│   │   ├── Evidence: `backend-realtime-streaming-timezone-aware-timestamps-2026-05-26.md`
│   │   ├── Generated: `realtime-streaming-timezone-aware-timestamps-2026-05-26.json`
│   │   ├── Parent: G2.149 accepted and merged by PR `#305`
│   │   ├── Merge commit: `bc795386313b40c4d87602fd80a09ad2d275f9d4`
│   │   ├── Scope: source plus focused-test implementation limited to
│   │   │          `realtime_streaming_service.py` and
│   │   │          `test_realtime_streaming_service.py`
│   │   ├── Result: introduces `_utc_now()` and uses it for
│   │   │          `StreamSubscriber.subscribed_at` and
│   │   │          `StreamData.created_at`, making realtime streaming
│   │   │          dataclass defaults timezone-aware UTC timestamps
│   │   ├── Verification: TDD red `1 failed, 42 passed`, explicit
│   │   │          timezone assertion red `3 failed, 40 passed`, focused
│   │   │          green `43 passed`, Socket.IO streaming regression
│   │   │          `20 passed`, Socket.IO manager regression
│   │   │          `26 passed, 1 warning`, consumer-injection regression
│   │   │          `2 passed`, and touched-file ruff reports
│   │   │          `All checks passed`
│   │   ├── GitNexus: pre-edit impact for `StreamSubscriber` and
│   │   │          `StreamData` reports LOW risk and impacted count `0`
│   │   └── Boundary: no Socket.IO manager source edit, route/API,
│   │              OpenAPI exposure, frontend, PM2, OpenSpec, config,
│   │              script, compatibility wrapper deletion, issue-label
│   │              change, or GitHub issue state change is performed here
│   ├── G2.154 Realtime/socket subtrack closeout
│   │   ├── State: ready for review
│   │   ├── Evidence: `backend-realtime-socket-subtrack-closeout-2026-05-26.md`
│   │   ├── Generated: `realtime-socket-subtrack-closeout-2026-05-26.json`
│   │   ├── Parent: G2.153 accepted and merged by PR `#306`
│   │   ├── Current HEAD: `bc795386313b40c4d87602fd80a09ad2d275f9d4`
│   │   ├── Result: closes the dedicated realtime/socket subtrack for now
│   │   │          after PRs `#297` through `#306` completed the authorized
│   │   │          manager-level injection, legacy export/test import
│   │   │          alignment, stream-error patch-target alignment, and
│   │   │          timezone-aware realtime streaming timestamp fix
│   │   ├── Verification: merged-base focused regression across
│   │   │          `test_realtime_streaming_service.py`,
│   │   │          `test_socketio_streaming_integration.py`,
│   │   │          `test_socketio_manager.py`, and
│   │   │          `test_realtime_socket_manager_streaming_dependency.py`
│   │   │          reports `91 passed, 1 warning`; static token scan reports
│   │   │          `datetime.utcnow=0` on the realtime/socket source surfaces
│   │   │          checked for this closeout
│   │   ├── Decision: do not open another realtime/socket source lane from
│   │   │          this closeout; return to the broader G2 high-risk service
│   │   │          getter queue for a separate next-track decision or
│   │   │          authorization package
│   │   └── Boundary: closeout-only; no backend source/test edit, route/API,
│   │              OpenAPI exposure, frontend, PM2, OpenSpec, config,
│   │              script, compatibility wrapper deletion, issue-label
│   │              change, or GitHub issue state change is performed here
│   └── Next gate: review G2.154; if accepted, select the next high-risk
│                  service getter track through a separate decision or
│                  authorization package before any new source lane starts
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
| `backend-data-source-factory-lhb-route-migration-implementation-2026-05-25.md` | G | G2.69 implementation packet prepared at `a76f6dbdc`: LHB route handlers now use `get_data_source_factory_dependency`, total route/API factory refs move `10 -> 8`, and `lhb.py` refs move `2 -> 0` | Human review / PR merge decision; if accepted, create closeout/current-head refresh before selecting another DataSourceFactory route consumer |
| `backend-data-source-factory-lhb-route-migration-closeout-2026-05-25.md` | G | G2.69 closeout packet prepared at `d25803e93`: PR `#217` merge recorded, health tests remain `116 passed`, provider tests remain `4 passed`, total refs remain `8`, and `lhb.py` remains `0` | Human review / PR merge decision; if accepted, create G2.70 candidate authorization before further route migration |
| `backend-data-source-factory-market-data-request-route-migration-authorization-2026-05-25.md` | G | G2.70 candidate packet prepared at `2670dba06`: selects `market_data_request.py` as the next route/API factory migration candidate; it is the only remaining ruff/black/GitNexus LOW candidate and can move total refs `8 -> 6` | Human review / PR merge decision; if accepted, create G2.71 path-limited implementation branch |
| `backend-data-source-factory-market-data-request-route-migration-implementation-2026-05-25.md` | G | G2.71 implementation packet prepared at `9060b455`: market data request route handlers now use `get_data_source_factory_dependency`, total route/API factory refs move `8 -> 6`, and `market_data_request.py` refs move `2 -> 0` | Human review / PR merge decision; if accepted, create closeout/current-head refresh before selecting another DataSourceFactory route consumer |
| `backend-data-source-factory-market-data-request-route-migration-closeout-2026-05-25.md` | G | G2.71 closeout packet prepared at `7f10db17`: PR `#220` merge recorded, health tests remain `117 passed`, provider tests remain `4 passed`, total refs remain `6`, and `market_data_request.py` remains `0` | Human review / PR merge decision; if accepted, create the next candidate authorization packet |
| `backend-data-source-factory-kline-route-migration-authorization-2026-05-25.md` | G | G2.72 candidate packet prepared at `f4e3db66`: selects `kline.py` as the next route/API factory migration candidate; it has GitNexus LOW/1, four routes, two direct refs, and scoped same-file E701/black debt, and can move total refs `6 -> 4` | Human review / PR merge decision; if accepted, create G2.73 path-limited implementation branch for `kline.py` only |
| `backend-data-source-factory-kline-route-migration-implementation-2026-05-25.md` | G | G2.73 implementation packet prepared at `68ff82a9`: kline route handlers now use `get_data_source_factory_dependency`, total route/API factory refs move `6 -> 4`, and `kline.py` refs move `2 -> 0` | Human review / PR merge decision; if accepted, create closeout/current-head refresh before selecting another DataSourceFactory route consumer |
| `backend-data-source-factory-kline-route-migration-closeout-2026-05-25.md` | G | G2.73 closeout packet prepared at `6ece7f13`: PR `#223` merge recorded, health tests remain `118 passed`, provider tests remain `4 passed`, total refs remain `4`, and `kline.py` remains `0` | Human review / PR merge decision; if accepted, create the next candidate authorization packet |
| `backend-data-source-factory-stocks-route-migration-authorization-2026-05-25.md` | G | G2.74 candidate packet prepared at `f7d370cd`: selects `stocks.py` as the next route/API factory migration candidate; it is the only remaining LOW-risk candidate and can move total refs `4 -> 2` | Human review / PR merge decision; if accepted, create G2.75 path-limited implementation branch for `stocks.py` only |
| `backend-data-source-factory-stocks-route-migration-implementation-2026-05-25.md` | G | G2.75 implementation packet prepared at `2a04b019`: stocks route handlers now use `get_data_source_factory_dependency`, total route/API factory refs move `4 -> 2`, and `stocks.py` refs move `2 -> 0` | Human review / PR merge decision; if accepted, create closeout/current-head refresh before preparing the futures.py risk packet |
| `backend-data-source-factory-stocks-route-migration-closeout-2026-05-25.md` | G | G2.75 closeout packet prepared at `02518742f`: PR `#226` merge recorded, health tests remain `119 passed`, provider tests remain `4 passed`, total refs remain `2`, `stocks.py` remains `0`, and remaining direct refs are only `futures.py:91` and `futures.py:114` | Human review / PR merge decision; if accepted, prepare a `futures.py` risk packet before any remaining DataSourceFactory route/API migration |
| `backend-data-source-factory-futures-route-migration-risk-packet-2026-05-25.md` | G | G2.76 risk packet prepared at `53f365b55`: confirms `futures.py` owns the final two direct route/API factory refs, records file-level GitNexus HIGH risk with exact endpoint caller count 0, and recommends a separate G2.77 path-limited implementation authorization before any source edit | Human review / PR merge decision; if accepted, create G2.77 implementation authorization for `futures.py` only |
| `backend-data-source-factory-futures-route-migration-implementation-authorization-2026-05-25.md` | G | G2.77 authorization packet prepared at `5fab3e8f`: future G2.78 may edit only `futures.py` and `test_health_route_conflicts.py`, must run TDD red/green, must keep route/OpenAPI/response/frontend/runtime/OpenSpec/issue-label/compatibility-getter scope locked, and is expected to move final route/API factory refs `2 -> 0` | Human review / PR merge decision; if accepted, create G2.78 path-limited implementation branch |
| `backend-data-source-factory-futures-route-migration-implementation-2026-05-25.md` | G | G2.78 implementation packet prepared at `5169da56`: futures route handlers now use `get_data_source_factory_dependency`, direct route/API factory refs move `2 -> 0`, health route conflicts pass `120`, provider tests pass `4`, OpenAPI paths remain `500`, and compatibility getter remains unchanged | Human review / PR merge decision; if accepted, create closeout/current-head refresh before compatibility getter retirement or retained-shim decision |
| `backend-data-source-factory-futures-route-migration-closeout-2026-05-25.md` | G | G2.78 closeout packet prepared at `e7a2a436`: PR `#230` merge recorded, health tests remain `120 passed`, provider tests remain `4 passed`, total route/API direct factory refs remain `0`, OpenAPI paths remain `500`, and compatibility getter remains unchanged | Human review / PR merge decision; if accepted, prepare a separate compatibility getter retirement / retained-shim decision packet |
| `backend-data-source-factory-compat-getter-retained-shim-decision-2026-05-25.md` | G | G2.79 decision packet prepared at `b3aefed2`: route/API direct `get_data_source_factory()` calls are `0`, but the compatibility getter remains package-exported, lifecycle-tested, and used by service-internal helper fallback paths; decision is retain shim for now | Human review / PR merge decision; if accepted, create a separate source-capable retirement authorization packet before any compatibility API removal |
| `backend-data-source-factory-compat-getter-retirement-authorization-2026-05-25.md` | G | G2.80 authorization packet accepted in PR `#233` at `b922db6b`: authorizes only a future G2.81 Phase 1 service-internal decoupling step; public getter and package exports must remain, route/API direct calls stay `0`, lifecycle tests pass `4`, health route conflicts pass `120`, and OpenAPI paths remain `500` | G2.81 implementation branch may perform Phase 1 service-internal decoupling only |
| `backend-data-source-factory-compat-getter-retirement-phase1-implementation-2026-05-25.md` | G | G2.81 implementation packet accepted in PR `#234` at `c176b9e`: adds private `_get_or_create_data_source_factory()`, keeps public `get_data_source_factory()` and package exports, removes service helper public getter calls, expands lifecycle tests to `5 passed`, keeps health route conflicts at `120 passed`, and keeps OpenAPI paths=`500` with duplicate operation IDs=`0` | Create closeout/current-head refresh before any public getter or package export retirement decision |
| `backend-data-source-factory-compat-getter-retirement-phase1-closeout-2026-05-25.md` | G | G2.82 closeout packet accepted in PR `#235` at `075768a`: records PR `#234` merge, reconfirms lifecycle tests `5 passed`, health route conflicts `120 passed`, OpenAPI routes=`548` paths=`500` duplicate operation IDs=`0`, route/API direct public getter calls=`0`, service helper public getter calls=`0`, and package export mentions=`4` | Separate source-capable authorization packet required before any public getter or package export retirement decision |
| `backend-data-source-factory-compat-getter-final-retirement-authorization-2026-05-25.md` | G | G2.83 authorization packet accepted in PR `#236` at `5de71a8`: precise scan shows production public getter hits are definition plus package exports only, route/API production consumers=`0`, package export lines=`2`, lifecycle tests `5 passed`, stocks runtime fallback `1 passed`, GitNexus impact remains CRITICAL/stale-aware, and market/data regression public getter patch points have existing unrelated failures recorded | G2.84 source implementation may remove the public getter and package exports only inside the authorized file scope |
| `backend-data-source-factory-compat-getter-final-retirement-implementation-2026-05-25.md` | G | G2.84 implementation packet prepared at `5de71a8`: removes public `get_data_source_factory()` and package exports, keeps `get_data_source_factory_dependency` plus `_get_or_create_data_source_factory`, moves production public getter hits=`0`, package export lines=`0`, patch points=`0`, lifecycle tests `5 passed`, stocks runtime fallback `1 passed`, market API integration `18 passed`, health route conflicts `120 passed`, OpenAPI paths=`500`, duplicate operation IDs=`0`, and leaves known `test_data_api_regression.py` historical-route 404 failures unresolved | Human review / PR merge decision; if accepted, create closeout/current-head refresh before further DataSourceFactory compatibility-surface cleanup |
| `backend-data-source-factory-compat-getter-final-retirement-closeout-2026-05-25.md` | G | G2.85 closeout accepted in PR `#238` at `ed033a4`: records PR `#237` merge, confirms production exact public getter hits=`0`, package export lines=`0`, route/API public getter hits=`0`, lifecycle tests `5 passed`, health route conflicts `120 passed`, touched-path ruff passed, and OpenAPI paths=`500` with duplicate operation IDs=`0` | DataSourceFactory public compatibility getter retirement lane closed; next service lifecycle lane must start from a separate authorization packet |
| `backend-service-lifecycle-di-next-lane-after-data-source-factory-2026-05-25.md` | G | G2.86 next-lane decision prepared at `ed033a4`: selects `AdvancedAnalysisService` compatibility getter Phase 1 service-internal decoupling as the next authorization candidate only; exact production getter hits are definition plus provider fallback only, route/API direct hits=`0`, GitNexus impact LOW / `0`, lifecycle tests `4 passed`, health route conflicts `120 passed`, OpenAPI paths=`500`, duplicate operation IDs=`0`; broad `get_data_service` and `get_strategy_service` seams remain CRITICAL holds, and StockSearch compatibility cleanup remains blocked by prior retain decision plus stale-aware GitNexus route-process noise | Human review / PR merge decision; if accepted, create G2.87 source-capable authorization before any AdvancedAnalysis source edit |
| `backend-advanced-analysis-compat-getter-phase1-authorization-2026-05-25.md` | G | G2.87 authorization packet prepared at `a20c92e`: authorizes only a future G2.88 Phase 1 service-internal decoupling for `AdvancedAnalysisService`; allowed future source scope is `advanced_analysis_service.py` plus focused lifecycle tests, public `get_advanced_analysis_service()` must remain, dependency provider and installer must remain, route/API direct getter hits remain `0`, GitNexus impact LOW / `0`, lifecycle tests `4 passed`, health route conflicts `120 passed`, and OpenAPI paths=`500`, duplicate operation IDs=`0` | Human review / PR merge decision; if accepted, create G2.88 implementation branch before any AdvancedAnalysis source edit |

| `backend-advanced-analysis-compat-getter-phase1-implementation-2026-05-25.md` | G | G2.88 implementation accepted in PR `#241` at `33c3d34`: private `_get_or_create_advanced_analysis_service()` added, dependency fallback retargeted away from the public getter, public getter retained, lifecycle tests `4 passed`, health route conflicts `120 passed`, and OpenAPI duplicate operation IDs=`0` | Superseded by G2.89 closeout / candidate refresh |
| `backend-advanced-analysis-compat-getter-phase1-closeout-2026-05-25.md` | G | G2.89 closeout accepted in PR `#242` at `7b6d81a`: records PR `#241` merge, confirms route/API public getter hits=`0`, package export hits=`0`, private initializer hits=`3`, dependency-provider refs=`19`, lifecycle tests `4 passed`, health route conflicts `120 passed`, and OpenAPI duplicate operation IDs=`0` | Superseded by G2.90 final-retirement authorization |
| `backend-advanced-analysis-compat-getter-final-retirement-authorization-2026-05-25.md` | G | G2.90 authorization accepted in PR `#243` at `db5ebd4`: authorizes only future G2.91 removal of public `get_advanced_analysis_service()` after TDD red/green, with private initializer, dependency provider, installer, app.state key, route/API, OpenAPI, frontend, PM2, and issue labels locked outside scope | Superseded by G2.91 implementation |
| `backend-advanced-analysis-compat-getter-final-retirement-implementation-2026-05-25.md` | G | G2.91 implementation accepted in PR `#244` at `1ebd0ae`: public `get_advanced_analysis_service()` removed, dependency provider and installer retained, focused lifecycle tests updated to `5 passed`, health route conflicts `120 passed`, and OpenAPI duplicate operation IDs=`0` | Superseded by G2.92 closeout |
| `backend-advanced-analysis-compat-getter-final-retirement-closeout-2026-05-25.md` | G | G2.92 closeout accepted in PR `#245` at `0d98e77`: records PR `#244` merge, confirms the AdvancedAnalysis public getter lane is closed, route/API public mentions=`0`, package export mentions=`0`, private initializer hits=`2`, dependency-provider refs=`19`, lifecycle tests `5 passed`, health route conflicts `120 passed`, and OpenAPI duplicate operation IDs=`0` | Superseded by G2.93 service lifecycle candidate refresh |
| `backend-service-lifecycle-candidate-refresh-after-advanced-analysis-2026-05-25.md` | G | G2.93 candidate refresh accepted in PR `#246` at `d8e1d14`: records PR `#245` merge, scans `152` service files / `575` app files / `219` API files, finds `23` getter definitions in this packet's scanner, selects `get_wencai_service` as a future G2.94 authorization candidate only, and records GitNexus impact LOW / `0` | Superseded by G2.94 Wencai getter-retirement authorization |
| `backend-wencai-compat-getter-retirement-authorization-2026-05-25.md` | G | G2.94 authorization accepted in PR `#247` at `228a94d`: authorizes only future G2.95 removal of `get_wencai_service` after TDD red/green; current scan shows app refs=`1`, route/API refs=`0`, test refs=`0`, package export refs=`0`; GitNexus impact LOW / `0`; `WencaiService` class usage remains active and outside deletion scope | Superseded by G2.95 implementation |
| `backend-wencai-compat-getter-retirement-implementation-2026-05-25.md` | G | G2.95 implementation accepted in PR `#248` at `689d619`: removes only `get_wencai_service`, adds focused absence/import regression test, records TDD red `1 failed, 1 passed`, green `2 passed`, health route conflicts `120 passed`, ruff/black passed, OpenAPI routes=`548`, paths=`500`, duplicate operation IDs=`0`, and post-change app/API/package getter refs=`0` | Superseded by G2.96 closeout |
| `backend-wencai-compat-getter-retirement-closeout-2026-05-25.md` | G | G2.96 closeout accepted in PR `#249` at `c0aa973`: records PR `#248` merge, confirms `get_wencai_service` app/API/package refs remain `0`, test refs are the focused absence assertion only, `WencaiService` remains active with app refs=`16` and route/API refs=`9`, focused test `2 passed`, and health route conflicts `120 passed` | Superseded by G2.97 service lifecycle candidate refresh |
| `backend-service-lifecycle-candidate-refresh-after-wencai-2026-05-25.md` | G | G2.97 candidate refresh accepted in PR `#250` at `dfb1dce`: records PR `#249` merge, scans `152` service files / `575` app files / `219` API files / `1007` test files, finds `22` getter definitions and `5` candidate-like definitions, confirms `get_wencai_service` is no longer present as a service getter definition, selects `get_enhanced_data_service` as a future G2.98 authorization candidate only, and records GitNexus impact LOW / `3` with no affected processes | Superseded by G2.98 EnhancedDataService getter-retirement authorization |
| `backend-enhanced-data-service-getter-retirement-authorization-2026-05-25.md` | G | G2.98 authorization accepted in PR `#251` at `8fb6db0`: authorizes only future G2.99 removal of `get_enhanced_data_service` after TDD red/green; current scan shows getter refs app=`1` file / route/API=`0` / focused tests=`0` / package exports=`0`, one module-local `__main__` smoke call, GitNexus impact LOW / `3`, and `EnhancedDataService` class usage remains active in system health route | Superseded by G2.99 EnhancedDataService getter-retirement implementation |
| `backend-enhanced-data-service-getter-retirement-implementation-2026-05-25.md` | G | G2.99 implementation accepted in PR `#252` at `e3bb781`: removes only `get_enhanced_data_service` and `_enhanced_data_service`, preserves `EnhancedDataService`, updates the module-local `__main__` smoke call to direct construction, adds focused regression coverage, records TDD red `2 failed, 1 passed`, green `3 passed`, health route conflicts `120 passed`, ruff/black passed, and OpenAPI routes=`548`, paths=`500`, duplicate operation IDs=`0` | Superseded by G2.100 closeout |
| `backend-enhanced-data-service-getter-retirement-closeout-2026-05-25.md` | G | G2.100 closeout accepted in PR `#253` at `d7be7e6`: records PR `#252` merge, confirms `get_enhanced_data_service` app/API/package refs remain `0`, test refs are focused absence assertions only, `_enhanced_data_service` app/API refs are `0`, `EnhancedDataService` remains active with app refs=`8` and route/API refs=`4`, focused test `3 passed`, and health route conflicts `120 passed` | Superseded by G2.101 service lifecycle candidate refresh |
| `backend-service-lifecycle-candidate-refresh-after-enhanced-data-service-2026-05-25.md` | G | G2.101 candidate refresh accepted in PR `#254` at `c8eae46`: records PR `#253` merge, scans `152` service files / `575` app files / `219` API files / `1008` test files, finds `18` getter definitions and `4` candidate-like definitions, confirms `get_enhanced_data_service` is no longer present as a service getter definition, selects `get_tradingview_service` as a future G2.102 authorization candidate only, and records GitNexus impact LOW / `1` with no affected processes | Superseded by G2.102 TradingView getter-retirement authorization |
| `backend-tradingview-getter-retirement-authorization-2026-05-25.md` | G | G2.102 authorization accepted in PR `#255` at `a0cfa4f`: authorizes only future G2.103 removal of `get_tradingview_service` after TDD red/green; current scan shows getter refs app=`2` / route/API=`0` / tests=`2` / package exports=`0`, direct caller `install_tradingview_service`, GitNexus impact LOW / `1`, and `TradingViewWidgetService` class plus dependency provider remain active and outside deletion scope | Superseded by G2.103 TradingView getter-retirement implementation |
| `backend-tradingview-getter-retirement-implementation-2026-05-26.md` | G | G2.103 implementation accepted in PR `#256` at `81cd619`: removed only `get_tradingview_service` and `_tradingview_service`, preserved `TradingViewWidgetService`, install/close helpers, and dependency provider, changed install fallback to direct `TradingViewWidgetService()` construction, recorded TDD red `1 failed, 7 passed`, green `8 passed`, health route conflicts `120 passed`, ruff/black passed, and schema-only OpenAPI routes=`548`, paths=`500`, duplicate operation IDs=`0` | Superseded by G2.104 TradingView getter-retirement closeout |
| `backend-tradingview-getter-retirement-closeout-2026-05-26.md` | G | G2.104 closeout accepted in PR `#257` at `750fa31`: records PR `#256` merge, confirms `get_tradingview_service` app refs=`0`, route/API refs=`0`, tests=`3`, package exports=`0`, confirms `_tradingview_service` app refs=`0`, route/API refs=`0`, tests=`2`, package exports=`0`, and preserves `TradingViewWidgetService`, install/close helpers, and dependency provider as active surfaces | Superseded by G2.105 service lifecycle candidate refresh after TradingView |
| `backend-service-lifecycle-candidate-refresh-after-tradingview-2026-05-26.md` | G | G2.105 candidate refresh accepted in PR `#258` at `9ac90c1`: current scan has service files=`152`, app files=`575`, API files=`219`, test files=`1008`, getter definitions=`17`, candidate-like definitions=`3`, holds=`14`; no direct implementation lane is selected because remaining candidate-like rows are the completed announcement hold and duplicate logical `get_email_service` rows | Superseded by G2.106 email duplicate getter ownership decision |
| `backend-email-duplicate-getter-ownership-decision-2026-05-26.md` | G | G2.106 decision accepted in PR `#259` at `6e10c49`: separates route-backed `email_service.py` ownership from legacy/helper `email_notification_service.py` ownership, records combined `get_email_service` app refs=`3`, route/API refs=`0`, tests=`3`, records active `get_email_service_dependency` route/API refs=`7`, and selects only a future G2.107 EmailNotificationService getter-retirement authorization packet | Superseded by G2.107 EmailNotificationService getter-retirement authorization |
| `backend-email-notification-getter-retirement-authorization-2026-05-26.md` | G | G2.107 authorization accepted in PR `#260` at `d120d6d`: authorizes only a future G2.108 implementation branch to retire `email_notification_service.py` module-level `_email_service` and `get_email_service`, preserves `EmailNotificationService`, keeps route-backed `email_service.py`, `get_email_service_dependency`, notification routes, OpenAPI, PM2, and OpenSpec out of scope, and records that file-path GitNexus context for `email_notification_service.py:get_email_service` has no incoming graph callers while bare `get_email_service` impact resolves to the separate route-backed `email_service.py` symbol | Superseded by G2.108 EmailNotificationService getter-retirement implementation |
| `backend-email-notification-getter-retirement-implementation-2026-05-26.md` | G | G2.108 implementation accepted in PR `#261` at `9cb643d`: removes only `email_notification_service.py:_email_service` and `email_notification_service.py:get_email_service`, preserves `EmailNotificationService`, leaves route-backed `email_service.py`, `get_email_service_dependency`, and notification routes untouched, records TDD red `1 failed`, focused green `5 passed`, health route conflicts `120 passed`, touched-file ruff and black checks passed, and exact post-change scan shows target getter refs=`0` and target singleton refs=`0` | Superseded by G2.109 EmailNotificationService getter-retirement closeout |
| `backend-email-notification-getter-retirement-closeout-2026-05-26.md` | G | G2.109 closeout accepted in PR `#262` at `ae6d2f2`: records PR `#261` merge, confirms current-head `email_notification_service.py:get_email_service` refs=`0`, `_email_service` refs=`0`, route/API direct `email_notification_service` refs=`0`, preserves `EmailNotificationService` and route-backed `get_email_service_dependency`, and re-runs focused tests `5 passed`, health route conflicts `120 passed`, ruff, and black checks | Superseded by G2.110 service lifecycle candidate refresh after EmailNotificationService |
| `backend-service-lifecycle-candidate-refresh-after-email-notification-2026-05-26.md` | G | G2.110 candidate refresh accepted in PR `#263` at `c4abd4e`: scans service files=`152`, backend app files=`575`, API files=`219`, backend test files=`199`, all test files=`1211`, getter definitions=`16`, candidate-like definitions=`9`; confirms retired `email_notification_service.py:get_email_service` is gone, records `get_market_data_service` as the only LOW / `0` next authorization candidate with route/API direct refs=`0`, and keeps streaming HIGH, TDX/data/strategy/stock search CRITICAL, and email/watchlist/announcement holds out of source scope | Superseded by G2.111 MarketDataService getter-retirement authorization |
| `backend-market-data-service-getter-retirement-authorization-2026-05-26.md` | G | G2.111 authorization prepared at `c4abd4e`: authorizes only a future G2.112 implementation branch for the package-level `market_data_service/get_market_data_service.py` `_market_data_service` and `get_market_data_service` retirement; preserves `MarketDataService`, `install_market_data_service`, and `get_market_data_service_dependency`, records GitNexus impact LOW / `0`, direct API refs=`0`, and requires future adapter/package export cleanup because `market_data_adapter.py` and package `__init__.py` still reference the getter | Human review / PR merge decision; if accepted, create G2.112 MarketDataService getter-retirement implementation before any market-data service source edit |
| `backend-service-lifecycle-di-candidate-refresh-after-stock-search-2026-05-26.md` | G | G2.129 candidate refresh accepted in PR `#282` at `cc32d0c2`: confirms Announcement/Email/StockSearch retired getters remain `0`, scans service files=`152`, app files=`575`, API files=`219`, tests=`203`, getter definitions=`12`, selects no direct implementation lane, and identifies `get_watchlist_service` only as a future authorization candidate with GitNexus MEDIUM / impacted=`15` / direct=`9` / processes=`0` | Superseded by G2.130 WatchlistService getter-retirement authorization |
| `backend-watchlist-service-getter-retirement-authorization-2026-05-26.md` | G | G2.130 authorization accepted in PR `#283` at `35dcc90`: authorizes only a future implementation branch to retire `watchlist_service.py` `get_watchlist_service` and `_watchlist_service`, while preserving `WatchlistService`, `install_watchlist_service`, `get_watchlist_service_dependency`, route paths, response contracts, and OpenAPI exposure; current scan shows getter definitions=`1`, singleton tokens=`74`, app/API direct getter calls=`0`, route dependency handlers=`7`, adapter fallback files=`2`, tests with getter refs=`4`; GitNexus impact MEDIUM / impacted=`15` / direct=`9` / processes=`0` | Superseded by G2.131 WatchlistService getter-retirement implementation |
| `backend-watchlist-service-getter-retirement-implementation-2026-05-26.md` | G | G2.131 implementation accepted in PR `#284` at `ccadd5e`: removes `watchlist_service.py` `get_watchlist_service` and module-level `_watchlist_service`, removes both adapter fallback imports/calls, preserves `WatchlistService`, `install_watchlist_service`, `get_watchlist_service_dependency`, route paths, response contracts, and OpenAPI exposure; TDD red `2 failed, 1 passed`, focused watchlist tests `28 passed`, health route conflicts `120 passed`, ruff/black/import smoke passed, exact scan reports service getter definitions=`0`, service singleton assignments=`0`, adapter fallback imports=`0`, adapter public getter calls=`0`, app/API public getter calls=`0`, route dependency handlers=`7` | Superseded by G2.132 WatchlistService getter-retirement closeout |
| `backend-watchlist-service-getter-retirement-closeout-2026-05-26.md` | G | G2.132 closeout accepted in PR `#285` at `f0e0e37`: records PR `#284` merged at `2026-05-26T03:30:49Z`, confirms current-head scan still has service getter definitions=`0`, service singleton assignments=`0`, adapter fallback imports=`0`, adapter public getter calls=`0`, app/API public getter calls=`0`, route dependency handlers=`7`, focused watchlist tests `28 passed`, and health route conflicts `120 passed`; no runtime source, tests, route paths, response contracts, OpenAPI exposure, PM2 workflow, OpenSpec change, or issue-label change is modified | Superseded by G2.133 service lifecycle candidate refresh after WatchlistService |
| `backend-service-lifecycle-di-candidate-refresh-after-watchlist-2026-05-26.md` | G | G2.133 candidate refresh accepted in PR `#286` at `bc2d2a8`: service files=`152`, app files=`575`, API files=`219`, tests=`204`, remaining service getter definitions=`11`, Announcement/Email/StockSearch/Watchlist retired public getter definitions remain `0`; no direct implementation lane is selected; six LOW graph-risk remaining candidates are shared `IntegratedServices` facade getters, `get_market_data_service` is held for graph/text disambiguation, and `get_tdx_service`, `get_data_service`, `get_strategy_service`, `get_streaming_service` remain HIGH/CRITICAL holds | Superseded by G2.134 IntegratedServices facade getter ownership decision |
| `backend-integrated-services-facade-getter-ownership-decision-2026-05-26.md` | G | G2.134 decision accepted in PR `#287` at `65498c4`: classifies `web/backend/app/services/__init__.py` getters as a shared IntegratedServices compatibility facade owned by the composition root; retains `get_integrated_services` and `get_market_data_service`; marks only `get_trading_data_service`, `get_analysis_data_service`, `get_data_api_service`, `get_database_service`, `get_websocket_service`, and `get_cache_service` as eligible for a future unused-facade retirement authorization packet; risk helper facades are out of the current service-getter queue | Superseded by G2.135 unused IntegratedServices service-facade getter retirement authorization |
| `backend-unused-integrated-services-facade-getter-retirement-authorization-2026-05-26.md` | G | G2.135 authorization accepted in PR `#288` at `4aaa5a8`: future source lane may remove only `get_trading_data_service`, `get_analysis_data_service`, `get_data_api_service`, `get_database_service`, `get_websocket_service`, and `get_cache_service` from `web/backend/app/services/__init__.py`, with one focused test file and implementation evidence; `get_integrated_services`, `get_market_data_service`, risk helper facades, HIGH/CRITICAL service getters, route/API, OpenAPI, PM2, frontend, OpenSpec, and issue labels remain locked | Superseded by G2.136 unused IntegratedServices service-facade getter retirement implementation |
| `backend-unused-integrated-services-facade-getter-retirement-implementation-2026-05-26.md` | G | G2.136 implementation accepted in PR `#289` at `541a225`: removes only `get_trading_data_service`, `get_analysis_data_service`, `get_data_api_service`, `get_database_service`, `get_websocket_service`, and `get_cache_service` from `web/backend/app/services/__init__.py`; preserves `get_integrated_services`, `get_market_data_service`, all risk helper facades, route/API, OpenAPI, PM2, frontend, OpenSpec, and issue labels; pre-edit GitNexus impact was LOW / impacted `0` for all six symbols; TDD red `1 failed, 1 passed`, focused test `2 passed`, import smoke, exact scan, Ruff, and Black passed | Superseded by G2.137 unused IntegratedServices service-facade getter retirement closeout |
| `backend-unused-integrated-services-facade-getter-retirement-closeout-2026-05-26.md` | G | G2.137 closeout prepared at `541a225`: records PR `#289` merged at `2026-05-26T04:51:23Z`, confirms current-head scan has retired facade definitions=`0` and locked facade definitions=`1`, focused closeout test `2 passed`, and import smoke `removed_absent=True` / `locked_callable=True`; no runtime source, tests, route paths, response contracts, OpenAPI exposure, PM2 workflow, OpenSpec change, or issue-label change is modified | Human review / PR merge decision; if accepted, refresh the remaining service lifecycle candidate pool |

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
| `backend-market-data-provider-design-2026-05-23.md` | G | G2.25 design packet prepared at `f97ca070853`: `MarketDataService` and `MarketDataServiceV2` stay separate; `market_v2.py` is the recommended future route-provider authorization candidate; dashboard, adapter, and market-data package provider work stay in separate lanes | Human review; if accepted, create G2.26 `MarketDataServiceV2` route-provider implementation authorization before source edits |
| `backend-market-data-service-v2-route-provider-implementation-authorization-2026-05-23.md` | G | G2.26 authorization packet prepared at `46507955f`: future source scope is limited to `market_data_service_v2.py`, `market_v2.py`, focused lifecycle tests, implementation evidence, and a future task card; dashboard, adapter, market-data package, service consolidation, route/OpenAPI, frontend, PM2, and OpenSpec work remain excluded | Human review; if accepted, create a separate implementation branch before source edits |
| `backend-market-data-service-v2-route-provider-implementation-2026-05-23.md` | G | G2.27 implementation merged by PR `#167` at `8120f01a7022472b604f525ac9af2a517150c39b`: app-state provider seam added to `market_data_service_v2.py`, 13 `market_v2.py` route-local getter calls converted to injected `MarketDataServiceV2`, compatibility getter retained, and 2 dashboard helper callers intentionally left unchanged | Superseded by G2.28 closeout packet |
| `backend-market-data-service-v2-route-provider-closeout-2026-05-23.md` | G | G2.28 closeout merged by PR `#168` at `e79029ff99e8c3ee674d07efd8b1601e7deb32e0`: PR `#167` merge recorded, focused lifecycle DI test `4 passed`, ruff and black passed, `app.main` import passed, OpenAPI smoke reports paths=`500`, `/api/v2/market` paths=`13`, duplicate operationIds=`0`, `market_v2.py` direct route getter calls=`0`, and `dashboard_data_source.py` helper calls remain `2` | Superseded by G2.29 candidate refresh packet |
| `backend-service-lifecycle-di-candidate-refresh-after-market-data-v2-2026-05-23.md` | G | G2.29 candidate refresh merged by PR `#169` at `04e2f7038386dbea1b8fc8bdcb24dd91dc7e9bb1`: scanned 152 service files, recorded 20 narrow candidate files, 5 completed route-surface DI seams, GitNexus `get_market_data_service_v2` remains CRITICAL because dashboard helper callers are active, and no direct implementation candidate is selected | Superseded by G2.30 consumer matrix packet |
| `backend-market-data-service-v2-compatibility-getter-consumer-matrix-2026-05-23.md` | G | G2.30 consumer matrix prepared at `04e2f7038386`: `market_v2.py` route direct getter calls remain `0`, `dashboard_data_source.py` has import plus 2 non-route helper getter calls, the installer still uses the compatibility getter as fallback, GitNexus reports getter CRITICAL while provider/installer targets are not indexed, and no cleanup or dashboard helper migration implementation is authorized | Human review; if accepted, create G2.31 dashboard helper provider migration authorization before source edits |
| `backend-market-data-service-v2-dashboard-helper-provider-migration-authorization-2026-05-23.md` | G | G2.31 authorization merged by PR `#171` at `0b838356e51e11f2ad27f9d3c898583611520622`: future source scope limited to `dashboard_data_source.py`, `dashboard.py`, `main.py`, focused tests, implementation evidence, and a future task card; `get_market_data_service_v2()` remains public fallback | Superseded by G2.32 dashboard helper provider migration implementation packet |
| `backend-market-data-service-v2-dashboard-helper-provider-migration-implementation-2026-05-23.md` | G | G2.32 implementation merged by PR `#172` at `40a396fabcbafcc527d4d15af1eb81034a645d87`: dashboard helper direct getter calls are `0`, route-body `get_data_source()` calls are `0`, startup prewarm passes the installed app-state service, focused tests passed, and OpenAPI stayed stable at paths=`500` | Superseded by G2.33 service lifecycle DI candidate refresh packet |
| `backend-service-lifecycle-di-candidate-refresh-after-dashboard-helper-2026-05-23.md` | G | G2.33 candidate refresh merged by PR `#173` at `78dafc38546ca9d45a1ed4bb3e5c2db24b9978b1`: scanned 152 service files, recorded 20 candidate files, confirmed `MarketDataServiceV2` route/helper direct calls remain `0`, and identified TDX dashboard helper provider migration as the next decision-only authorization candidate | Superseded by G2.34 TDX dashboard helper provider authorization packet |
| `backend-tdx-dashboard-helper-provider-migration-authorization-2026-05-23.md` | G | G2.34 authorization prepared at current HEAD `78dafc385`: records 2 direct `get_tdx_service()` helper calls in `dashboard_data_source.py`, confirms `tdx.py` already uses FastAPI dependency wiring, records CRITICAL GitNexus impact for the getter/helper chain, and limits any future implementation to a separate G2.35 branch after human review | Superseded by G2.35 TDX dashboard helper provider implementation packet |
| `backend-tdx-dashboard-helper-provider-migration-implementation-2026-05-23.md` | G | G2.35 implementation merged by PR `#175` at `efbc02db5100a4927476a4c8eb2c4cd4533a352f`: adds `install_tdx_service(app, service=None)`, makes `RealBusinessDataSource` provider-fed for `_get_major_index_quotes()` and `_get_tdx_live_market_snapshot()`, passes the installed app-state TDX service into startup prewarm, keeps `get_tdx_service()` public, leaves `tdx.py` unchanged, records direct dashboard helper getter calls at `0`, focused tests `133 passed`, ruff/black passed, `app.main` routes=`548`, OpenAPI paths=`500`, duplicate operation IDs=`0`, and staged GitNexus `risk_level=high` matching the pre-approved dashboard/prewarm helper impact | Superseded by G2.36 TDX dashboard helper provider closeout packet |
| `backend-tdx-dashboard-helper-provider-closeout-2026-05-23.md` | G | G2.36 closeout reviewed and merged by PR `#176` at `6e940a7a5596b4256f63fec888c589777456d36a`: records PR `#175` merged, direct dashboard helper `get_tdx_service()` calls remain `0`, `tdx.py` still has 5 `Depends(get_tdx_service)` sites, focused tests `133 passed`, ruff/black passed, `app.main` routes=`548`, OpenAPI paths=`500`, and duplicate operation IDs=`0`; no source/test/runtime/OpenSpec/issue-label changes were authorized | Superseded by G2.37 current-head service lifecycle DI candidate refresh packet |
| `backend-service-lifecycle-di-candidate-refresh-after-tdx-helper-2026-05-23.md` | G | G2.37 candidate refresh reviewed and merged by PR `#177` at `f0f761ffb7d848b8e9a8e5a492ab82f763870086`: scans `152` service files and `18` candidate/signal files; records direct dashboard helper TDX getter calls at `0`, private `_get_tdx_service()` calls at `3`, `/api/tdx` `Depends(get_tdx_service)` sites at `5`, GitNexus spot checks for nine singleton getters, and no implementation lane selection | Superseded by G2.38 TDX route dependency consumer matrix |
| `backend-tdx-route-dependency-consumer-matrix-2026-05-23.md` | G | G2.38 consumer matrix reviewed and merged by PR `#178` at `30c78a22dce5879396dfd5c7760cc61161377528`: OpenAPI paths=`500`, duplicate operation IDs=`0`, TDX paths=`7`; `/api/v1/tdx` has five active `Depends(get_tdx_service)` route consumers, `/api/ml/tdx` is unrelated local `TdxDataService()` usage, dashboard helper keeps `get_tdx_service` as default provider fallback, and `get_tdx_service()` must not be retired by this line | Superseded by G2.39 TDX route provider migration authorization |
| `backend-tdx-route-provider-migration-authorization-2026-05-23.md` | G | G2.39 authorization prepared at current HEAD `30c78a22dce5879396dfd5c7760cc61161377528`: future implementation scope is limited to `tdx_service.py`, `api/tdx.py`, `web/backend/tests/test_tdx_service_lifecycle_di.py`, implementation evidence, and a future task card; it may add `TDX_SERVICE_STATE_KEY` and `get_tdx_service_dependency`, convert five `/api/v1/tdx` route dependencies, and must preserve `get_tdx_service()` compatibility fallback | Human review; if accepted, create G2.40 TDX route provider migration implementation branch before source edits |
| `backend-tdx-route-provider-migration-implementation-2026-05-24.md` | G | G2.40 implementation prepared from G2.39 authorization at base `e4dc9088cabfb4dba756beb109294980c047c327`: adds `TDX_SERVICE_STATE_KEY` and `get_tdx_service_dependency(request)`, keeps `get_tdx_service()` as public fallback, converts exactly five `/api/v1/tdx` `Depends(get_tdx_service)` sites to `Depends(get_tdx_service_dependency)`, focused TDD ended at `4 passed`, ruff/black passed, `app.main` routes=`548`, OpenAPI paths=`500`, duplicate operation IDs=`0`, and TDX paths=`7` | Human review / PR merge decision; if accepted, run G2.41 closeout or current-head candidate refresh before selecting the next service lifecycle DI lane |
| `backend-tdx-route-provider-migration-closeout-2026-05-24.md` | G | G2.41 closeout prepared at current HEAD `86b0ec43c037729b28df51c40484196175c96c6e`: records PR `#180` as `MERGED`, confirms focused TDX lifecycle DI tests `4 passed`, ruff/black passed, `tdx.py` legacy route dependency sites=`0`, provider sites=`5`, `get_tdx_service()` remains public fallback, `app.main` routes=`548`, OpenAPI paths=`500`, duplicate operation IDs=`0`, and no next service lifecycle DI candidate is selected | Human review / PR merge decision; if accepted, create G2.42 current-head candidate refresh before selecting the next service lifecycle DI lane |
| `backend-service-lifecycle-di-candidate-refresh-after-tdx-route-provider-2026-05-24.md` | G | G2.42 candidate refresh prepared at current HEAD `41b0d4db7f2c644cea9abf1ddd4112e695325dcc`: scans `152` service files and `21` narrow candidate/signal files, records completed route-provider seams=`7`, confirms TDX route dependency surface closed with legacy sites=`0` and provider sites=`5`, keeps `get_tdx_service()` as public fallback, records OpenAPI paths=`500` and duplicate operation IDs=`0`, and does not select a new implementation target | Human review / PR merge decision; if accepted, create G2.43 service candidate usefulness and ownership triage packet before any source edits |
| `backend-service-candidate-usefulness-ownership-triage-2026-05-24.md` | G | G2.43 triage prepared at current HEAD `f7c6fdf5fd57cff14ef6d11f1d18fd6591a22dc5`: records PR `#182` as `MERGED`, confirms `AdvancedAnalysisService` is an active route class dependency with `14` class `Depends()` sites and no external getter reference, classifies `WencaiService` as active DB/session-backed direct construction, keeps `get_market_data_service` as active route dependency with `7` route dependency sites, classifies `UnifiedDataService` as a broad data seam, and authorizes no implementation | Human review / PR merge decision; if accepted, create G2.44 `AdvancedAnalysisService` route-provider migration authorization before any source edits |
| `backend-advanced-analysis-route-provider-migration-authorization-2026-05-24.md` | G | G2.44 authorization prepared at current HEAD `1e137abb2a32b795c403a8a168a174ad86b7f693`: records PR `#183` as `MERGED`, confirms `advanced_analysis_api.py` has `14` class `Depends()` sites, preserves `get_advanced_analysis_service()` and module singleton compatibility, records GitNexus `AdvancedAnalysisService` upstream impact as LOW / `0`, and limits any future implementation to a separate G2.45 branch after human review | Human review / PR merge decision; if accepted, create G2.45 `AdvancedAnalysisService` route-provider implementation branch before source edits |
| `backend-advanced-analysis-route-provider-migration-implementation-2026-05-24.md` | G | G2.45 implementation prepared from G2.44 authorization at base `22b617733e29c9a441e88cb1da2ce0a5d8be98cc`: adds `ADVANCED_ANALYSIS_SERVICE_STATE_KEY`, `install_advanced_analysis_service`, and `get_advanced_analysis_service_dependency`, preserves `get_advanced_analysis_service()` and module singleton compatibility, converts all `14` `advanced_analysis_api.py` service dependencies to the provider, focused TDD ended at `4 passed`, ruff/black passed, configured OpenAPI smoke reports routes=`548`, paths=`500`, duplicate operation IDs=`0`, and advanced paths=`14` | Human review / PR merge decision; if accepted, run G2.46 closeout/current-head candidate refresh before selecting the next service lifecycle DI lane |
| `backend-advanced-analysis-route-provider-closeout-and-candidate-refresh-2026-05-24.md` | G | G2.46 closeout prepared at current HEAD `059638b573c6f2586537973e2a4b396f0ce156d7`: records PR `#185` as `MERGED`, confirms `AdvancedAnalysisService` route class dependency sites=`0`, provider sites=`14`, direct compatibility getter route calls=`0`, focused test result=`4 passed`, configured OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`, advanced paths=`14`, completed provider modules=`8`, route provider dependency files=`11`, and route provider dependency sites=`72`; no next implementation target or compatibility getter retirement is authorized | Human review / PR merge decision; if accepted, create G2.47 candidate selection and usefulness/ownership triage packet before any source edits |
| `backend-service-lifecycle-di-candidate-selection-after-advanced-analysis-2026-05-24.md` | G | G2.47 candidate selection prepared at current HEAD `e09e6db4a6a85dc392c20a737e729bb6f123804d`: records PR `#186` as `MERGED`, scans `152` service files and `219` API files, confirms provider modules=`8`, route provider dependency sites=`72`, route class dependency sites=`0`, and classifies `get_market_data_service` as the next consumer matrix / authorization candidate packet while excluding `get_data_service`, `get_strategy_service`, and `get_kronos_client` from direct implementation | Human review / PR merge decision; if accepted, create G2.48 `get_market_data_service` route dependency consumer matrix / route-provider authorization candidate before any source edits |
| `backend-market-data-service-route-dependency-consumer-matrix-2026-05-24.md` | G | G2.48 consumer matrix prepared at current HEAD `0dce9ca97cd043f898039176394eb5076c353cf5`: records PR `#188` as `MERGED`, confirms `get_market_data_service` GitNexus risk=`LOW` / impacted count=`0`, identifies exactly seven active `/api/v1/market` route handlers using `Depends(get_market_data_service)`, keeps the package compatibility getter and `market_data_adapter.py` fallback surface active, excludes `services/__init__.py` IntegratedServices accessor and `MarketDataServiceV2` consolidation, configured app/OpenAPI smoke reports routes=`548`, paths=`500`, duplicate operation IDs=`0`, and focused `test_market_api_integration.py` result=`18 passed` | Human review / PR merge decision; if accepted, create G2.49 `get_market_data_service` route-provider implementation branch before source edits |
| `backend-market-data-service-route-provider-implementation-2026-05-24.md` | G | G2.49 implementation prepared from G2.48 authorization at base `7daf74ce0c3210defc2ad283583a335037daa500`: adds `MARKET_DATA_SERVICE_STATE_KEY`, `install_market_data_service`, and `get_market_data_service_dependency`, preserves `get_market_data_service()` and package compatibility, converts exactly seven `/api/v1/market` route dependencies to the provider, keeps `market_data_adapter.py`, `services/__init__.py`, and `MarketDataServiceV2` unchanged, TDD red=`4 failed, 1 passed`, green=`5 passed`, market integration tests=`18 passed`, ruff/black passed, configured OpenAPI smoke reports routes=`548`, paths=`500`, duplicate operation IDs=`0`, selected market routes=`7` | Human review / PR merge decision; if accepted, run G2.50 closeout/current-head candidate refresh before selecting the next service lifecycle DI lane |
| `backend-market-data-service-route-provider-closeout-2026-05-24.md` | G | G2.50 closeout prepared at current HEAD `33163197b59893372d5d1d68af53acbfbbb0f613`: records PR `#190` as `MERGED`, confirms `market_data_request.py` legacy dependency sites=`0`, provider dependency sites=`7`, provider import present=`true`, focused lifecycle tests=`5 passed`, market integration tests=`18 passed`, configured app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`, provider functions=`8`, route provider dependency files=`11`, and route provider dependency sites=`79`; residual `get_market_data_service()` references remain compatibility or separate helper/fallback surfaces and are not deletion candidates | Human review / PR merge decision; if accepted, create a current-head candidate refresh before selecting the next service lifecycle DI implementation lane |
| `backend-service-lifecycle-di-candidate-refresh-after-market-data-provider-2026-05-24.md` | G | G2.51 candidate refresh prepared at current HEAD `047f483dd70a5234ca3a128342511a56779194d3`: records PR `#191` as `MERGED`, scans `152` service files and `219` API files, confirms provider functions=`8`, route provider dependency files=`11`, route provider dependency sites=`79`, route getter dependency sites=`270`, OpenAPI paths=`500`, duplicate operation IDs=`0`, `get_market_data_service` legacy route dependency sites=`0`, and classifies the remaining interesting seams: `get_indicator_registry` LOW/`4` as indicator-internal design, `get_data_service` CRITICAL/`5`, `get_strategy_service` CRITICAL/`13`, `get_kronos_client` CRITICAL/`3`, and route-local `get_technical_pattern_detection_service` as D2.1a historical provider surface; no next source implementation target is selected | Human review / PR merge decision; if accepted, choose a separate decision packet before any source edits |
| `backend-indicator-registry-provider-design-2026-05-24.md` | G | G2.52 design packet prepared at current HEAD `363324bf31a89b797789403c55dbe3ca854bc7d6`: records PR `#192` as `MERGED`, confirms two same-name `get_indicator_registry()` surfaces, separates flat API registry `web/backend/app/services/indicator_registry.py` from package registry `web/backend/app/services/indicators/indicator_registry.py`, records flat API direct callers=`3`, package registry production callers=`3`, app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`, and selects no source implementation target; recommended next gate is G2.53 flat API registry consumer matrix / authorization candidate | Human review / PR merge decision; if accepted, create G2.53 flat API registry consumer matrix / authorization candidate before source edits |
| `backend-flat-api-indicator-registry-consumer-matrix-2026-05-24.md` | G | G2.53 consumer matrix prepared at current HEAD `ec3dc2920886eb24e963a33488bd2e945e98e6c9`: records PR `#193` as `MERGED`, confirms the flat API registry singleton at `web/backend/app/services/indicator_registry.py`, identifies exactly two direct registry route consumers in `indicator_cache.py`, excludes `IndicatorCalculator.__init__` from the route-provider batch, keeps the package registry startup/jobs surface separate, records configured app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`, selected indicator cache routes=`6`, and collect-only checks=`16+112+29` | Human review / PR merge decision; if accepted, create G2.54 flat API registry route-provider implementation branch before source edits |
| `backend-flat-api-indicator-registry-route-provider-implementation-2026-05-24.md` | G | G2.54 implementation prepared at current HEAD `71510bb02a845ec529c8c04f3a7288ca86b87b9c`: records PR `#194` as `MERGED`, adds `INDICATOR_REGISTRY_STATE_KEY`, `install_indicator_registry`, and `get_indicator_registry_dependency`, preserves `get_indicator_registry()`, converts exactly two registry read handlers in `indicator_cache.py`, keeps `IndicatorCalculator.__init__` and package registry startup/jobs surfaces unchanged, verifies TDD red=`2 failed`, green=`2 passed`, touched ruff/black passed, v1 indicator OpenAPI doc test=`1 passed`, configured app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`, and records legacy `/api/indicators/*` path assertions in `test_indicators.py` as residual test debt | Human review / PR merge decision; if accepted, run G2.55 closeout/current-head refresh before selecting another service lifecycle DI lane |
| `backend-flat-api-indicator-registry-route-provider-closeout-2026-05-24.md` | G | G2.55 closeout prepared at current HEAD `5b12a3c08cac3558c56af615ff14c05913d96f72`: records PR `#195` as `MERGED`, confirms flat API registry provider surface remains present, route direct `get_indicator_registry()` references under `web/backend/app/api`=`0`, provider dependency route sites=`2`, selected indicator cache routes=`6`, configured app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`, focused tests=`2+1 passed`, and GitNexus graph output is stale for the new provider symbols until index refresh | Human review / PR merge decision; if accepted, refresh GitNexus or explicitly discount stale graph output before selecting another service lifecycle DI lane |
| `backend-service-lifecycle-di-candidate-refresh-after-indicator-registry-provider-2026-05-24.md` | G | G2.56 candidate refresh prepared at current HEAD `1fc4a4c7a86cf464dedb742612c052b911d4ef5f`: records PR `#196` as `MERGED`, scans API files=`219`, service files=`152`, backend tests=`195`, provider state keys=`10`, provider functions=`20`, provider records=`30`, route dependency sites=`353`, provider-style route dependency sites=`81`, getter-style route dependency sites=`272`, confirms route direct `get_indicator_registry()` refs=`0`, provider dependency route sites=`2`, app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`, and records GitNexus refresh blocked in the linked worktree by `ENOTDIR .git/info`; no source implementation target is authorized | Human review / PR merge decision; if accepted, refresh GitNexus from a non-linked checkout or explicitly record a stale-graph waiver before creating any next service lifecycle DI authorization packet |
| `backend-gitnexus-refresh-after-indicator-registry-provider-2026-05-24.md` | G | G2.57 GitNexus refresh evidence prepared at current HEAD `3469a43855ef81d238e1a92745126fcb321b1af7`: records PR `#197` as `MERGED`, confirms a temporary non-linked clone with `.git` kind=`directory`, `gitnexus analyze` exit=`0`, nodes=`62623`, edges=`145799`, clusters=`3291`, flows=`300`, GitNexus repo `g2-57-gitnexus-index-checkout` state=`ready`, `get_indicator_registry_dependency` and `install_indicator_registry` resolve in the refreshed graph, upstream impact for `get_indicator_registry_dependency` is `LOW` with impacted count=`0`, and static route scan still reports route direct `get_indicator_registry()` refs=`0` plus provider route sites=`2`; no source implementation target is authorized | Human review / PR merge decision; if accepted, create a separate G2.58 candidate-selection or implementation-authorization packet before any next service lifecycle DI source edit |
| `backend-service-lifecycle-di-next-lane-selection-after-gitnexus-refresh-2026-05-24.md` | G | G2.58 next-lane selection prepared at current HEAD `5dbb0ca0c387dafb313e9b5f2674f3023da65962`: records PR `#198` as `MERGED`, confirms fresh non-linked GitNexus analyze exit=`0`, nodes=`62621`, edges=`145801`, flows=`300`, current static scan route dependency sites=`353`, provider-style route dependency sites=`81`, getter-style route dependency sites=`272`, classifies all ordinary provider rows as implemented/closed except `get_data_source_dependency`, which is already provider-shaped with `3` dashboard route sites, and selects `get_data_source_factory` as the next design-only seam because it has `17` direct API call sites across `9` files and refreshed GitNexus upstream impact `CRITICAL` (`22` impacted, `21` direct, `15` processes, `3` modules); no source implementation target is authorized | Human review / PR merge decision; if accepted, create G2.59 `get_data_source_factory` design/authorization packet before any backend source edit |
| `backend-data-source-factory-lifecycle-di-authorization-2026-05-24.md` | G | G2.59 authorization packet prepared at current HEAD `1880f0d1395e7c5594b70f3ba40478cff24f2d3a`: records PR `#199` as `MERGED`, confirms fresh non-linked GitNexus analyze exit=`0`, nodes=`62624`, edges=`145803`, flows=`300`, resolves `get_data_source_factory` at `web/backend/app/services/data_source_factory/data_source_factory.py:294-300`, static scan keeps direct API calls=`17` across `9` files, and refreshed GitNexus upstream impact remains `CRITICAL` (`22` impacted, `21` direct, `15` processes, `3` modules); no source, test, route, OpenAPI, OpenSpec, runtime, issue-label, or compatibility cleanup change is authorized | Human review / PR merge decision; if accepted, create G2.60 consumer-matrix / implementation-authorization packet before any backend source edit |
| `backend-data-source-factory-consumer-matrix-implementation-authorization-2026-05-24.md` | G | G2.60 consumer matrix / implementation authorization prepared at current HEAD `265f38e53bddfa3a925f14cfbc5080b00dce26e6`: records PR `#200` as `MERGED`, confirms fresh non-linked GitNexus analyze exit=`0`, nodes=`62628`, edges=`145797`, flows=`300`, keeps direct API calls=`17` across `9` files, and selects G2.61a provider-seam-only as the next possible source batch with allowed future scope limited to `data_source_factory.py`, a focused lifecycle DI test, implementation evidence, and a future task card; route migration, compatibility getter cleanup, OpenAPI changes, issue-label changes, and runtime/PM2 changes remain locked | Human review / PR merge decision; if accepted, create G2.61a provider-seam-only implementation branch before any route migration |
| `backend-data-source-factory-provider-seam-implementation-2026-05-24.md` | G | G2.61a provider-seam implementation prepared at current HEAD `ae6ba4e43b1470b524110fe506929df675bd8b93`: records PR `#201` as `MERGED`, confirms pre-edit non-linked GitNexus analyze exit=`0`, nodes=`62636`, edges=`145807`, flows=`300`, and CRITICAL impact remains expected; adds `DATA_SOURCE_FACTORY_STATE_KEY`, `install_data_source_factory`, and `get_data_source_factory_dependency` in `data_source_factory.py`, adds focused lifecycle DI tests, preserves `get_data_source_factory()` and `_global_factory`, keeps route direct calls=`17` and provider dependency API refs=`0`, TDD red=`3 failed, 1 passed`, green=`4 passed`, existing factory tests=`38 passed`, route-adjacent fallback test=`1 passed`, app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`; `tests/backend/test_data_api_regression.py` still has baseline 404 failures in both modified and unmodified checkouts and is not part of this batch | Human review / PR merge decision; if accepted, run G2.61a closeout/current-head refresh before selecting any route migration packet |
| `backend-data-source-factory-provider-seam-closeout-2026-05-24.md` | G | G2.61a closeout prepared at current HEAD `0aadb27801c86e97e65ffdb4426276e1bd14c352`: records PR `#202` as `MERGED`, confirms provider symbols remain present, route direct calls remain `17`, provider dependency API refs remain `0`, focused lifecycle DI test=`4 passed`, existing factory test=`38 passed`, route-adjacent runtime fallback=`1 passed`, ruff/black passed, app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`, and refreshed non-linked GitNexus resolves `get_data_source_factory_dependency` plus `install_data_source_factory` with LOW upstream impact and `0` callers; no source, test, route, OpenAPI, OpenSpec, issue-label, runtime, PM2, package export, or compatibility cleanup change is authorized | Human review / PR merge decision; if accepted, create G2.61b `data_quality.py` route migration authorization / consumer-matrix packet before any route edit |
| `backend-data-quality-data-source-factory-route-migration-authorization-2026-05-24.md` | G | G2.61b route migration authorization prepared at current HEAD `ee2c74f3c8e1c4f690d2a1737db29c97c39a54d2`: records PR `#203` as `MERGED`, confirms `data_quality.py` has two DataSourceFactory compatibility getter calls at lines `58` and `369`, keeps total API direct calls=`17` across `9` files and provider dependency API refs=`0`, records package export gap for `get_data_source_factory_dependency`, verifies provider lifecycle tests=`4 passed`, existing factory tests=`38 passed`, data-quality mock configuration tests=`2 passed`, ruff candidate files=`passed`, and app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`; authorizes only a future G2.61c path-limited implementation packet for `data_quality.py` plus data-source-factory package export and focused tests | Human review / PR merge decision; if accepted, create G2.61c path-limited route migration implementation branch; remaining `15` route/API consumers stay locked |
| `backend-data-quality-data-source-factory-route-migration-implementation-2026-05-24.md` | G | G2.61c implementation prepared at current HEAD `52a2aaa57150db834bcef3a526a4b78e37ac438a`: records PR `#204` as `MERGED`, refreshes non-linked GitNexus at the same HEAD with analyze exit=`0`, nodes=`62644`, edges=`145830`, flows=`300`, records LOW/0 upstream impact for `get_sources_health`, `get_system_status_overview`, `get_data_source_factory_dependency`, and `install_data_source_factory`, follows TDD red=`2 failed, 2 passed` then green=`4 passed`, re-exports `get_data_source_factory_dependency`, migrates `data_quality.py` direct calls from `2` to `0`, reduces total API direct calls from `17` to `15`, preserves `get_data_source_factory()` plus `_global_factory`, verifies provider tests=`4 passed`, existing factory tests=`38 passed`, ruff/black touched files=`passed`, app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`; remaining `15` route/API consumers stay locked | Human review / PR merge decision; if accepted, run G2.61c closeout/current-head refresh before selecting another DataSourceFactory route consumer packet |
| `backend-data-quality-data-source-factory-route-migration-closeout-2026-05-24.md` | G | G2.61c closeout prepared at current HEAD `b9d0bb31a72d362dc67a38dcd719578de56af739`: records PR `#205` as `MERGED`, confirms current-head route guard direct API calls=`15`, `data_quality.py` direct refs=`0`, provider dependency API refs=`3`, focused data-quality tests=`4 passed`, provider lifecycle tests=`4 passed`, factory tests=`38 passed`, ruff/black touched files=`passed`, app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`, and refreshed non-linked GitNexus at `b9d0bb31a` with analyze exit=`0`, nodes=`62656`, edges=`145815`, flows=`300`, LOW/0 upstream impact for `get_sources_health`, `get_system_status_overview`, and `get_data_source_factory_dependency`; recommends G2.62 authorization-only packet for the next one-call consumer candidate (`data/financial.py` or `data/market.py`) | Human review / PR merge decision; if accepted, create G2.62 consumer-selection authorization packet before any further route edit |
| `backend-data-source-factory-next-route-consumer-authorization-2026-05-24.md` | G | G2.62 authorization prepared at current HEAD `fcc438de0965f80af7d485525fb494511976595b`: records PR `#206` as `MERGED`, compares the remaining one-call candidates and selects `web/backend/app/api/data/financial.py` for future G2.63 because it has one direct factory call at line `69` inside one route function, while `web/backend/app/api/data/market.py` has one direct call at line `98` but a broader four-route file surface; this PR authorizes only a future `financial.py` implementation branch and does not edit source, tests, routes, OpenAPI, OpenSpec, issue labels, runtime, or PM2 state | Human review / PR merge decision; if accepted, create G2.63 path-limited `financial.py` implementation branch; all other remaining consumers stay locked |
| `backend-data-source-factory-financial-route-migration-implementation-2026-05-24.md` | G | G2.63 implementation prepared at current HEAD `7c1b8fce44b3931c44ac5398e12f5715a28833e3`: records PR `#207` as `MERGED`, refreshes non-linked GitNexus at the same HEAD with analyze exit=`0`, nodes=`62644`, edges=`145819`, flows=`300`, records file-level `financial.py` upstream impact LOW/2 and provider dependency LOW/0, follows TDD red=`1 failed, 112 passed` then green=`113 passed`, migrates `financial.py` direct calls from `1` to `0`, reduces total API direct calls from `15` to `14`, preserves `get_data_source_factory()` plus `_global_factory`, verifies provider lifecycle tests=`4 passed`, ruff/black touched files=`passed`, app/OpenAPI smoke routes=`548`, paths=`500`, duplicate operation IDs=`0`; remaining `14` route/API consumers stay locked | Human review / PR merge decision; if accepted, run G2.63 closeout/current-head refresh before selecting another DataSourceFactory route consumer packet |
| `backend-data-source-factory-financial-route-migration-closeout-2026-05-24.md` | G | G2.63 closeout prepared at current HEAD `229cd7fe0a21cb9bf7b9079d07e9551baaf0a4c7`: records PR `#208` as `MERGED`, confirms current-head route guard direct API calls=`14`, `financial.py` direct refs=`0`, provider dependency API refs=`5`, health route conflict tests=`113 passed`, provider lifecycle tests=`4 passed`, ruff/black touched files=`passed`, app/OpenAPI smoke routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, and refreshed non-linked GitNexus at `229cd7fe0` with analyze exit=`0`, nodes=`62659`, edges=`145822`, flows=`300`, file-level `financial.py` LOW/1 upstream impact and provider dependency LOW/0; recommends a separate G2.64 authorization-only packet before any next route consumer edit | Human review / PR merge decision; if accepted, create G2.64 authorization-only packet for the next DataSourceFactory route consumer; recommended candidate is `web/backend/app/api/data/market.py`, and all other remaining consumers stay locked |
| `backend-data-source-factory-market-route-migration-authorization-2026-05-24.md` | G | G2.64 authorization prepared at current HEAD `cfb98f079c488c7e33c270e44342408a0e10db44`: records PR `#209` as `MERGED`, selects `web/backend/app/api/data/market.py` for future G2.65 because it has one direct factory call at line `98` inside `get_market_overview`, records the four-route file surface, confirms direct API calls=`14`, provider dependency refs=`5`, health route conflict tests=`113 passed`, provider lifecycle tests=`4 passed`, app/OpenAPI smoke routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, and refreshed non-linked GitNexus at `cfb98f079` with analyze exit=`0`, nodes=`62656`, edges=`145824`, flows=`300`, file-level `market.py` LOW/1 upstream impact and provider dependency LOW/0; candidate style baseline notes existing `market.py` E701/black debt to fix inside a future same-file implementation | Human review / PR merge decision; if accepted, create G2.65 path-limited `market.py` implementation branch; all other remaining consumers stay locked |
| `backend-data-source-factory-market-route-migration-implementation-2026-05-24.md` | G | G2.65 implementation prepared at current HEAD `20a7b67f1898506586e7858840d0ae058461fe93`: records PR `#210` as `MERGED`, refreshes non-linked GitNexus before source edits with analyze exit=`0`, nodes=`62665`, edges=`145822`, flows=`300`, records file-level `market.py` upstream impact LOW/1 and provider dependency LOW/0, follows TDD red=`1 failed: KeyError factory` then green=`1 passed`, migrates `market.py` direct calls from `1` to `0`, reduces total API direct calls from `14` to `13`, clears same-file `market.py` E701/black debt inside the authorized file, preserves `get_data_source_factory()` plus `_global_factory`, verifies health route conflict tests=`114 passed`, provider lifecycle tests=`4 passed`, ruff/black touched files=`passed`, app/OpenAPI smoke routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`; remaining `13` route/API consumers stay locked | Human review / PR merge decision; if accepted, run G2.65 closeout/current-head refresh before selecting another DataSourceFactory route consumer packet |
| `backend-data-source-factory-market-route-migration-closeout-2026-05-24.md` | G | G2.65 closeout prepared at current HEAD `277fdd412b2bbf68b64c5186fee943dc50080480`: records PR `#211` as `MERGED`, confirms current-head route guard direct API calls=`13`, `market.py` direct refs=`0`, provider dependency API refs=`7`, health route conflict tests=`114 passed`, provider lifecycle tests=`4 passed`, ruff/black touched files=`passed`, app/OpenAPI smoke routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, and refreshed non-linked GitNexus at `277fdd412` with analyze exit=`0`, nodes=`62667`, edges=`145820`, flows=`300`, file-level `market.py` LOW/1 upstream impact and provider dependency LOW/0; recommends G2.66 authorization-only candidate comparison before any next route consumer edit | Human review / PR merge decision; if accepted, create G2.66 consumer-selection authorization packet; all remaining `13` route/API consumers stay locked |

| `backend-data-source-factory-route-candidate-authorization-2026-05-25.md` | G | G2.66 authorization prepared at current HEAD `d30f2c12d642fbc613689d85b39697999805bbb8`: records PR `#212` as `MERGED`, confirms remaining route/API direct factory calls=`13`, compares six candidates, selects `web/backend/app/api/data/margin.py` for future G2.67 because it has direct refs=`3`, route handlers=`3`, LOC=`155`, ruff=`pass`, black=`unchanged`, GitNexus=`LOW/1`, and expected post-implementation direct refs `3 -> 0` / total direct refs `13 -> 10`; defers `lhb.py` due black reformat debt, `market_data_request.py` due broad 11-route surface, `kline.py` and `stocks.py` due E701/black debt, and `futures.py` due a CRITICAL/91 file-level GitNexus anomaly requiring narrower impact analysis | Human review / PR merge decision; if accepted, create G2.67 path-limited `margin.py` implementation branch; all other remaining consumers stay locked |

| `backend-data-source-factory-margin-route-migration-implementation-2026-05-25.md` | G | G2.67 implementation prepared at current HEAD `7b817debccfba1c82efc5a9c71f23f0b775434c0`: records PR `#213` as `MERGED`, verifies pre-edit GitNexus `margin.py` LOW/1 and three route-handler contexts, follows TDD red=`1 failed: KeyError factory` then green=`1 passed`, migrates `get_margin_account_info`, `get_margin_detail_sse`, and `get_margin_detail_szse` to `get_data_source_factory_dependency`, removes three inline compatibility getter calls, moves `margin.py` direct refs `3 -> 0`, total direct refs `13 -> 10`, verifies health route conflict tests=`115 passed`, provider lifecycle tests=`4 passed`, ruff/black touched files=`passed`, app/OpenAPI smoke routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, and staged GitNexus detect changes risk=`low`, affected count=`0`; remaining `10` route/API consumers stay locked | Human review / PR merge decision; if accepted, run G2.67 closeout/current-head refresh before selecting another DataSourceFactory route consumer packet |

| `backend-data-source-factory-margin-route-migration-closeout-2026-05-25.md` | G | G2.67 closeout prepared at current HEAD `3f1a737a5cc62f0424951931581e410d1dd14975`: records PR `#214` as `MERGED`, confirms current-head route guard direct API calls=`10`, `margin.py` direct refs=`0`, provider dependency API refs=`8`, health route conflict tests=`115 passed`, provider lifecycle tests=`4 passed`, ruff/black touched files=`passed`, app/OpenAPI smoke routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, file-level `margin.py` LOW/1 upstream impact and provider package LOW/0; recommends G2.68 authorization-only candidate comparison before any next route consumer edit | Human review / PR merge decision; if accepted, create G2.68 consumer-selection authorization packet; all remaining `10` route/API consumers stay locked |

| `backend-data-source-factory-lhb-route-migration-authorization-2026-05-25.md` | G | G2.68 authorization prepared at current HEAD `d5a0ef78718a070180be0428573530081945c943`: records PR `#215` as `MERGED`, confirms remaining route/API direct factory calls=`10`, compares five candidates, selects `web/backend/app/api/data/lhb.py` for future G2.69 because it has direct refs=`2`, route handlers=`2`, LOC=`128`, ruff=`pass`, black=`would_reformat`, GitNexus=`LOW/1`, and expected post-implementation direct refs `2 -> 0` / total direct refs `10 -> 8`; defers `market_data_request.py` due broad 11-route surface, `kline.py` and `stocks.py` due E701/black debt, and `futures.py` due a CRITICAL/91 file-level GitNexus anomaly requiring narrower impact analysis | Human review / PR merge decision; if accepted, create G2.69 path-limited `lhb.py` implementation branch; all other remaining consumers stay locked |

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
| G2.25 market-data provider design | G/#79 | Decide the market-data provider seam before selecting an implementation authorization | Review-ready: PR `#164` merged at `f97ca070853a77afc80c226d53948e805ba33c8e`; `market_v2.py` has 13 direct `get_market_data_service_v2()` route calls, `dashboard_data_source.py` has 2 non-route helper calls, `market/market_data_request.py` already uses `Depends(get_market_data_service)` in 7 route handlers, and service consolidation is rejected | `docs/reports/quality/backend-market-data-provider-design-2026-05-23.md`; `.planning/codebase/generated/market-data-provider-design-2026-05-23.json` | Human review; if accepted, create G2.26 `MarketDataServiceV2` route-provider implementation authorization before source edits |
| G2.26 MarketDataServiceV2 route-provider implementation authorization | G/#79 | Authorize exact future implementation boundary for `MarketDataServiceV2` route-provider DI | Review-ready: PR `#165` merged at `46507955f77a3166491bd4510c56ef034b6ff1cb`; GitNexus rates `get_market_data_service_v2` CRITICAL with 18 impacted symbols and 15 direct callers; future write scope is limited to `market_data_service_v2.py`, `market_v2.py`, focused lifecycle tests, implementation evidence, and a future task card; this packet performs no source edits | `docs/reports/quality/backend-market-data-service-v2-route-provider-implementation-authorization-2026-05-23.md`; `.planning/codebase/generated/market-data-service-v2-route-provider-implementation-authorization-2026-05-23.json` | Human review; if accepted, create a separate implementation branch before source edits |
| G2.27 MarketDataServiceV2 route-provider lifecycle DI | G/#79 | Implement the approved route-provider DI seam for `MarketDataServiceV2` | Merged by PR `#167` at `8120f01a7022472b604f525ac9af2a517150c39b`: `market_v2.py` route-local getter calls are now `0`, 13 route handlers accept injected `MarketDataServiceV2`, `get_market_data_service_v2()` remains as compatibility getter, and `dashboard_data_source.py` helper callers remain unchanged | `docs/reports/quality/backend-market-data-service-v2-route-provider-implementation-2026-05-23.md`; focused lifecycle DI test file | Superseded by G2.28 closeout packet |
| G2.28 MarketDataServiceV2 route-provider closeout | G/#79 | Record the PR `#167` merge result and post-merge route/OpenAPI stability | Reviewed and merged by PR `#168` at `e79029ff99e8c3ee674d07efd8b1601e7deb32e0`: no backend source/test/runtime/OpenSpec/issue-label changes; post-merge scan shows `0` direct route getter calls in `market_v2.py`, 13 injected route params, and 2 dashboard helper compatibility calls unchanged; focused lifecycle DI test `4 passed`; ruff/black passed; `app.main` import passed; OpenAPI paths=`500`, `/api/v2/market` paths=`13`, duplicate operationIds=`0` | `docs/reports/quality/backend-market-data-service-v2-route-provider-closeout-2026-05-23.md`; `.planning/codebase/generated/market-data-service-v2-route-provider-closeout-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/168 | Superseded by G2.29 candidate refresh packet |
| G2.29 service lifecycle DI candidate refresh after MarketDataServiceV2 | G/#79 | Refresh current-head service lifecycle DI candidates after MarketDataServiceV2 route-provider closeout | Reviewed and merged by PR `#169` at `04e2f7038386dbea1b8fc8bdcb24dd91dc7e9bb1`: service scan covers 152 service files, records 20 narrow candidate files and 5 completed route-surface DI seams; `market_v2.py` direct getter calls remain `0`, `dashboard_data_source.py` helper getter calls remain `2`, GitNexus still rates `get_market_data_service_v2` CRITICAL, and no direct source implementation is authorized | `docs/reports/quality/backend-service-lifecycle-di-candidate-refresh-after-market-data-v2-2026-05-23.md`; `.planning/codebase/generated/service-lifecycle-di-candidate-refresh-after-market-data-v2-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/169 | Superseded by G2.30 consumer matrix packet |
| G2.30 MarketDataServiceV2 compatibility getter consumer matrix | G/#79 | Decide whether `get_market_data_service_v2()` cleanup is authorized after route-provider DI | Reviewed and merged by PR `#170` at `f87cb60afd399e16db0142c3eaaa7ab24c3a1ab1`: route direct getter calls remain `0`; `market_v2.py` provider refs are `14`; `dashboard_data_source.py` has import plus two active non-route helper calls; tests cover provider/fallback behavior; `get_market_data_service_v2()` remains active dashboard-helper compatibility surface; no source/test/route cleanup implementation is authorized | `docs/reports/quality/backend-market-data-service-v2-compatibility-getter-consumer-matrix-2026-05-23.md`; `.planning/codebase/generated/market-data-service-v2-compatibility-getter-consumer-matrix-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/170 | Superseded by G2.31 dashboard helper provider migration authorization packet |
| G2.31 MarketDataServiceV2 dashboard helper provider migration authorization | G/#79 | Authorize exact future implementation boundary for migrating dashboard helper callers from direct compatibility getter use to provider-fed service use | Reviewed and merged by PR `#171` at `0b838356e51e11f2ad27f9d3c898583611520622`: `dashboard_data_source.py` still had 2 direct helper calls plus import; `dashboard.py` had two routes using `Depends(get_data_source)` and `/summary` calling `get_data_source()` inside the route body; `main.py` scheduled prewarm without passing a service; future source scope was limited to `dashboard_data_source.py`, `dashboard.py`, `main.py`, focused tests, implementation evidence, and a future task card | `docs/reports/quality/backend-market-data-service-v2-dashboard-helper-provider-migration-authorization-2026-05-23.md`; `.planning/codebase/generated/market-data-service-v2-dashboard-helper-provider-migration-authorization-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/171 | Superseded by G2.32 dashboard helper provider migration implementation packet |
| G2.32 MarketDataServiceV2 dashboard helper provider migration | G/#79 | Implement approved dashboard helper provider migration while preserving compatibility getter fallback | Reviewed and merged by PR `#172` at `40a396fabcbafcc527d4d15af1eb81034a645d87`: `RealBusinessDataSource` accepts injected `MarketDataServiceV2`; `get_data_source_dependency()` bridges FastAPI dependency resolution through `get_market_data_service_v2_dependency`; `/summary`, `/market-overview`, and `/health` use dependency-provided dashboard source; startup prewarm passes the installed app-state service; `dashboard_data_source.py` direct `get_market_data_service_v2()` calls are `0`; `market_v2.py` remains unchanged with route direct getter calls `0`; focused tests `11 passed`; OpenAPI paths=`500`, `/api/v2/market` paths=`13`, duplicate operation IDs=`0` | `docs/reports/quality/backend-market-data-service-v2-dashboard-helper-provider-migration-implementation-2026-05-23.md`; focused dashboard source tests; https://github.com/chengjon/mystocks/pull/172 | Superseded by G2.33 service lifecycle DI candidate refresh packet |
| G2.33 service lifecycle DI candidate refresh after dashboard helper | G/#79 | Refresh current-head service lifecycle candidates after the dashboard helper provider migration | Reviewed and merged by PR `#173` at `78dafc38546ca9d45a1ed4bb3e5c2db24b9978b1`: scanned `152` service files and `20` candidate files; `MarketDataServiceV2` route/helper direct getter calls remain `0`; `get_market_data_service_v2` current-head GitNexus spot check is LOW; `get_tdx_service` is CRITICAL with 2 dashboard helper direct calls, so the next step is a decision-only G2.34 TDX dashboard helper provider authorization packet | `docs/reports/quality/backend-service-lifecycle-di-candidate-refresh-after-dashboard-helper-2026-05-23.md`; `.planning/codebase/generated/service-lifecycle-di-candidate-refresh-after-dashboard-helper-2026-05-23.json`; https://github.com/chengjon/mystocks/pull/173 | Superseded by G2.34 TDX dashboard helper provider authorization packet |
| G2.34 TDX dashboard helper provider migration authorization | G/#79 | Authorize exact future implementation boundary for the TDX dashboard helper provider seam | Review-ready: `dashboard_data_source.py` has 2 direct `get_tdx_service()` helper calls at lines 238 and 490; `tdx.py` already has 5 `Depends(get_tdx_service)` sites and is excluded from this lane; GitNexus rates `get_tdx_service`, `_get_major_index_quotes`, and `_get_tdx_live_market_snapshot` CRITICAL because they feed dashboard summary/market overview/prewarm flows; future implementation scope is limited to `tdx_service.py`, `dashboard_data_source.py`, conditional `main.py` prewarm wiring, focused tests, implementation evidence, and a future task card | `docs/reports/quality/backend-tdx-dashboard-helper-provider-migration-authorization-2026-05-23.md`; `.planning/codebase/generated/tdx-dashboard-helper-provider-migration-authorization-2026-05-23.json` | Human review; if accepted, create G2.35 implementation branch before source edits |
| G2.35 TDX dashboard helper provider migration | G/#79 | Implement the approved provider-fed TDX dashboard helper seam while preserving compatibility fallback | Reviewed and merged by PR `#175` at `efbc02db5100a4927476a4c8eb2c4cd4533a352f`: `tdx_service.py` adds `install_tdx_service(app, service=None)`; `RealBusinessDataSource` accepts injected/provider `TdxService`; `_get_major_index_quotes()` and `_get_tdx_live_market_snapshot()` use provider-fed service access; startup prewarm passes the installed app-state TDX service; `get_tdx_service()` remains public; `tdx.py` remains unchanged; direct dashboard helper getter calls are `0`; focused tests `133 passed`; OpenAPI paths=`500`, duplicate operation IDs=`0`; staged GitNexus `risk_level=high` was expected for the authorized dashboard/prewarm helper chain | `docs/reports/quality/backend-tdx-dashboard-helper-provider-migration-implementation-2026-05-23.md`; `web/backend/tests/test_dashboard_data_source.py`; `governance/mainline/task-cards/pr-175.yaml`; https://github.com/chengjon/mystocks/pull/175 | Superseded by G2.36 TDX dashboard helper provider closeout packet |
| G2.36 TDX dashboard helper provider closeout | G/#79 | Record the PR `#175` merge result and post-merge route/OpenAPI stability | Reviewed and merged by PR `#176` at `6e940a7a5596b4256f63fec888c589777456d36a`: no backend source/test/runtime/OpenSpec/issue-label changes; PR `#175` is `MERGED` at `efbc02db5100a4927476a4c8eb2c4cd4533a352f`; current-head scan shows `dashboard_data_source.py` direct `get_tdx_service()` calls remain `0`, private `_get_tdx_service()` calls are `3`, `tdx_service.py` still defines `get_tdx_service()` once and `install_tdx_service()` once, `tdx.py` keeps 5 `Depends(get_tdx_service)` sites, focused tests `133 passed`, ruff/black passed, `app.main` routes=`548`, OpenAPI paths=`500`, duplicate operation IDs=`0` | `docs/reports/quality/backend-tdx-dashboard-helper-provider-closeout-2026-05-23.md`; `.planning/codebase/generated/tdx-dashboard-helper-provider-closeout-2026-05-23.json`; `governance/mainline/task-cards/pr-176.yaml`; https://github.com/chengjon/mystocks/pull/176 | Superseded by G2.37 current-head service lifecycle DI candidate refresh packet |
| G2.37 service lifecycle DI candidate refresh after TDX helper | G/#79 | Refresh current-head service lifecycle DI candidates after TDX dashboard helper provider closeout | Reviewed and merged by PR `#177` at `f0f761ffb7d848b8e9a8e5a492ab82f763870086`: no backend source/test/runtime/OpenSpec/issue-label changes; scanned `152` service files and `18` candidate/signal files; direct dashboard helper TDX getter calls remain `0`, private `_get_tdx_service()` calls are `3`, `/api/tdx` keeps 5 `Depends(get_tdx_service)` sites, `tdx_service.py` still defines `get_tdx_service()` once and `install_tdx_service()` once; GitNexus spot checks mark `get_strategy_service` HIGH and `get_integrated_services` MEDIUM, so no implementation lane is selected here | `docs/reports/quality/backend-service-lifecycle-di-candidate-refresh-after-tdx-helper-2026-05-23.md`; `.planning/codebase/generated/service-lifecycle-di-candidate-refresh-after-tdx-helper-2026-05-23.json`; `governance/mainline/task-cards/pr-177.yaml`; https://github.com/chengjon/mystocks/pull/177 | Superseded by G2.38 TDX route dependency consumer matrix |
| G2.38 TDX route dependency consumer matrix | G/#79 | Decide whether `get_tdx_service()` cleanup is authorized after TDX dashboard helper closeout | Reviewed and merged by PR `#178` at `30c78a22dce5879396dfd5c7760cc61161377528`: no backend source/test/runtime/OpenSpec/issue-label changes; OpenAPI paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`; `/api/v1/tdx` has five active `Depends(get_tdx_service)` public route consumers, `/api/ml/tdx` is unrelated local `TdxDataService()` usage, dashboard helper keeps `get_tdx_service` as default provider fallback, and no `get_tdx_service_dependency` provider exists yet; decision is to retain `get_tdx_service()` and not authorize cleanup here | `docs/reports/quality/backend-tdx-route-dependency-consumer-matrix-2026-05-23.md`; `.planning/codebase/generated/tdx-route-dependency-consumer-matrix-2026-05-23.json`; `governance/mainline/task-cards/pr-178.yaml`; https://github.com/chengjon/mystocks/pull/178 | Superseded by G2.39 TDX route provider migration authorization |
| G2.39 TDX route provider migration authorization | G/#79 | Authorize exact future implementation boundary for migrating `/api/v1/tdx` from direct compatibility getter dependency to app-state provider dependency | Review-ready: no backend source/test/runtime/OpenSpec/issue-label changes; current HEAD is `30c78a22dce5879396dfd5c7760cc61161377528`; future write scope is limited to `tdx_service.py`, `api/tdx.py`, `web/backend/tests/test_tdx_service_lifecycle_di.py`, implementation evidence, and a future task card; future implementation may add `TDX_SERVICE_STATE_KEY`, add `get_tdx_service_dependency(request)`, convert exactly five `/api/v1/tdx` dependency parameters, and must preserve route/OpenAPI behavior and `get_tdx_service()` fallback | `docs/reports/quality/backend-tdx-route-provider-migration-authorization-2026-05-23.md`; `.planning/codebase/generated/tdx-route-provider-migration-authorization-2026-05-23.json`; `governance/mainline/task-cards/pr-179.yaml` | Human review; if accepted, create G2.40 implementation branch before source edits |

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
| G2.63 financial DataSourceFactory route migration closeout | Merged implementation closeout | `229cd7fe0` | PR `#208` merged and closeout evidence is recorded: `financial.py` direct factory refs remain `0`, total API direct factory calls remain `14`, health route conflict tests pass `113`, provider lifecycle tests pass `4`, OpenAPI stays paths=`500` with duplicate operation IDs=`0`, and next movement requires a separate G2.64 authorization packet for `market.py` or another selected remaining consumer |

| G2.66 DataSourceFactory route candidate authorization | Ready for review | `d30f2c12` | Candidate comparison recorded after PR `#212`: selects `margin.py` for future G2.67 because it is ruff clean, black unchanged, GitNexus LOW/1, three routes, and three direct refs; this row authorizes no source edit until human review accepts the packet |

| G2.67 margin DataSourceFactory route migration | Ready for review | `7b817deb` | Path-limited implementation migrates three margin route handlers to `get_data_source_factory_dependency`, adds focused dependency wiring coverage, moves total direct route/API factory refs `13 -> 10`, and keeps all other remaining consumers locked pending closeout |

| G2.67 margin DataSourceFactory route migration closeout | Ready for review | `3f1a737a` | Current-head closeout records PR `#214` merged, keeps total direct route/API factory refs at `10`, keeps `margin.py` at `0`, and requires G2.68 authorization-only candidate comparison before any further route migration |

| G2.68 DataSourceFactory route candidate authorization | Ready for review | `d5a0ef78` | Candidate comparison recorded after PR `#215`: selects `lhb.py` for future G2.69 because it has the smallest low-risk route surface; this row authorizes no source edit until human review accepts the packet |

| G2.69 LHB DataSourceFactory route migration | Ready for review | `a76f6dbd` | Path-limited implementation migrates two LHB route handlers to `get_data_source_factory_dependency`, adds focused dependency wiring coverage, moves total direct route/API factory refs `10 -> 8`, and keeps all other remaining consumers locked pending closeout |

| G2.69 LHB DataSourceFactory route migration closeout | Ready for review | `d25803e9` | Current-head closeout records PR `#217` merged, keeps total direct route/API factory refs at `8`, keeps `lhb.py` at `0`, and requires G2.70 authorization-only candidate comparison before any further route migration |

| G2.70 DataSourceFactory route candidate authorization | Ready for review | `2670dba0` | Candidate comparison recorded after PR `#218`: selects `market_data_request.py` for future G2.71 because it is ruff clean, black unchanged, GitNexus LOW/1, and has two direct refs; this row authorizes no source edit until human review accepts the packet |

| G2.71 market data request DataSourceFactory route migration | Ready for review | `9060b455` | Path-limited implementation migrates `get_fund_flow` and `get_market_quotes` to `get_data_source_factory_dependency`, adds focused dependency wiring coverage, moves total direct route/API factory refs `8 -> 6`, and keeps all other remaining consumers locked pending closeout |

| G2.71 market data request DataSourceFactory route migration closeout | Ready for review | `7f10db17` | Current-head closeout records PR `#220` merged, keeps total direct route/API factory refs at `6`, keeps `market_data_request.py` at `0`, and requires a new authorization-only candidate comparison before any further route migration |

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
| P2 | Review G2.32 `MarketDataServiceV2` dashboard helper provider migration implementation | Future service seam lane | PR `#171` merged; G2.32 implementation packet is review-ready, removes dashboard helper direct getter calls, preserves `get_market_data_service_v2()` fallback compatibility, and recommends a fresh service lifecycle DI candidate refresh before any next implementation lane |
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
