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
│   ├── State: decision-package-prepared-for-review
│   ├── Role: Fold trading route ownership into unified route/OpenAPI governance
│   ├── Current fact: current smoke at HEAD `c24f43016` reports routes=`548`,
│   │                 OpenAPI paths=`500`, trading candidate routes=`41`
│   │                 (`40` trading-route candidates plus `1` unclassified
│   │                 trading-adjacent route),
│   │                 trading schema-exposed routes=`41`, trading schema paths=`35`,
│   │                 duplicate trading operationIds=`0`, and `/metrics` as the
│   │                 only duplicate runtime path/method; classification and
│   │                 consumer contract evidence are now prepared for review
│   └── Next gate: Review
│                  `backend-route-openapi-governance-decision-package-2026-05-22.md`;
│                  no route mutation, OpenAPI schema/exposure change, docs/API
│                  edit, implementation issue, PM2 action, source edit, or test
│                  edit is authorized
│
├── D2.4. Backup Route Ownership Planning Package
│   ├── Source evidence:
│   │   `backend-backup-route-ownership-planning-package-2026-05-21.md`
│   ├── State: decision-package-prepared-for-review
│   ├── Role: Keep backup routes as a dedicated ownership proposal candidate
│   │         with explicit safety, security, consumer, OpenAPI, and rollback
│   │         evidence before backup route mutation
│   ├── Current fact: current smoke at HEAD `553e71a90` reports routes=`548`,
│   │                 OpenAPI paths=`500`, backup candidate routes=`13`,
│   │                 backup schema-exposed routes=`13`, backup OpenAPI
│   │                 operations=`13`, duplicate backup operationIds=`0`, and
│   │                 `cleanup_old_backups.py` owning cleanup plus health routes
│   └── Next gate: Execute `define-backend-backup-route-ownership`
│                  governance/evidence tasks with current-head freshness; no
│                  backup route, module, OpenAPI, docs/API, infrastructure,
│                  PM2, source, generated client, or test mutation is authorized
│
├── D2.5. Control-Plane OpenAPI Docs Planning Package
│   ├── Source evidence:
│   │   `backend-control-plane-openapi-docs-planning-package-2026-05-21.md`
│   ├── State: approved-for-governance-execution
│   ├── Role: Stabilize control-plane OpenAPI docs taxonomy, schema exposure,
│   │         runtime-only compatibility, and probe evidence before docs/API or
│   │         route mutation
│   ├── Current fact: current smoke at HEAD `b39b7b3ee` reports routes=`548`,
│   │                 OpenAPI paths=`500`, broad control/status candidate
│   │                 routes=`128`, hidden focused docs/schema/control routes
│   │                 present, `/health/readiness` absent, duplicate focused
│   │                 operationIds=`0`, and `/metrics` as the control-plane
│   │                 duplicate runtime path/method to document
│   └── Next gate: Execute
│                  `stabilize-backend-control-plane-openapi-docs`
│                  governance/evidence tasks with current-head freshness; no
│                  docs/API, route, OpenAPI, probe, PM2, source, generated
│                  client, or test mutation is authorized
│
├── D2.6. PM2 Stateful Gate Approval Governance Package
│   ├── Source evidence:
│   │   `backend-pm2-stateful-gate-approval-governance-2026-05-21.md`
│   ├── State: approved-for-governance-execution
│   ├── Role: Define approval strategy and required approval record fields for
│   │         future stateful PM2 gates, named equivalents, and read-only
│   │         sampling before any PM2 command is executed
│   ├── Current fact: health/status task `4.7` is already closed by
│   │                 `backend-health-status-pm2-gate-2026-05-18.md`;
│   │                 `run_pm2_integration_workflow.sh` remains stateful because
│   │                 it can run `pm2 stop all` and `pm2 delete all`; no PM2
│   │                 command was executed by D2.6
│   └── Next gate: Execute `approve-backend-pm2-stateful-gate`
│                  governance/evidence tasks as policy acceptance only; no PM2
│                  command, service restart/recreation, route, OpenAPI,
│                  docs/API, source, generated client, or test mutation is
│                  authorized
│
├── D2 Closeout. Downstream Decision Rollup
│   ├── Source evidence:
│   │   `backend-openspec-issue92-downstream-rollup-closeout-2026-05-21.md`
│   ├── State: downstream-rollup-review-aligned-with-d2-1a-closed
│   ├── Role: Summarize D2.1-D2.6 as a complete downstream decision package
│   ├── Current fact: PRs `#96`-`#113` are merged; issue `#92` remains `OPEN`
│   │                 with `ready-for-human` and `ready-for-downstream`, but no
│   │                 `ready-for-agent`; the first recommended true
│   │                 implementation lane, D2.1a
│   │                 `TechnicalPatternDetectionService` DI pilot, is now closed
│   │                 end-to-end; review feedback was absorbed without expanding
│   │                 implementation authority
│   └── Next gate: Human selection of the next separate child lane. Do not treat
│                  this rollup, D2.1a closure, or issue `#92` itself as
│                  authorization for additional implementation
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
│   ├── State: approved-for-governance-execution
│   ├── Role: Classify route table, OpenAPI, operationId, probe consumer,
│   │         trading ownership, control-plane, backup, compatibility-route,
│   │         and schema-exposure evidence before route mutation
│   └── Next gate: Review
│                  `backend-route-openapi-governance-decision-package-2026-05-22.md`;
│                  no backend source, route, OpenAPI, probe, docs/API, or test
│                  mutation is authorized
│
├── G. Candidate Branch: define-backend-service-seams-and-singleton-pilots
│   ├── Source evidence: backend-singleton-lifecycle-routing-matrix-2026-05-19.md
│   ├── State: blocked
│   ├── Role: Replace the clean-pilot search with interface and test-double strategy
│   └── Next gate: Design interface extraction and test-double strategy for
│                  1-2 candidate services from the DB/session-backed bucket;
│                  full classification can proceed in parallel before any pilot
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
| D2.3 Route/OpenAPI governance decision package | D2.3/F | Governance/evidence task list executed and decision package prepared for review | Evidence-only: current HEAD `c173bbc8d` reports routes=`548`, schema-visible routes=`536`, hidden runtime routes=`12`, endpoint modules=`99`, OpenAPI paths=`500`, operations=`536`, schemas=`301`, duplicate operationIds=`0`, OpenAPI warnings=`0`, D2.3 trading candidate routes=`41`, and `/metrics` as the only duplicate runtime path/method; no backend source, frontend source, tests, generated client, docs/API, route behavior, OpenAPI schema, probe URL, PM2, or implementation issue is authorized | `docs/reports/quality/backend-route-openapi-governance-decision-package-2026-05-22.md`; `.planning/codebase/generated/backend-route-table-2026-05-22.json`; `.planning/codebase/generated/route-openapi-snapshot-2026-05-22.json`; `.planning/codebase/generated/probe-consumer-matrix-2026-05-22.json`; `.planning/codebase/generated/route-consumer-contract-matrix-2026-05-22.json` | Human review; after acceptance, update steward tree review status and decide whether any separate child lane is needed |
| D2.4 Backup route ownership planning package | D2.4 | Backup route ownership remains a dedicated proposal candidate, not a trading or generic route cleanup lane | Planning/evidence only: current smoke at HEAD `553e71a90` reports routes=`548`, OpenAPI paths=`500`, backup candidate routes=`13`, schema-exposed=`13`, backup OpenAPI paths=`13`, backup operations=`13`, duplicate backup operationIds=`0`; `cleanup_old_backups.py` owns cleanup plus health routes; no route, OpenAPI, source, frontend, test, docs/API, PM2, or OpenSpec mutation is authorized | `docs/reports/quality/backend-backup-route-ownership-planning-package-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Human review; if accepted, create a separate backup route ownership proposal or implementation issue before backup route mutation |
| D2.4 Backup route ownership OpenSpec proposal | D2.4/F | Explicit proposal created for dedicated backup route ownership after D2.4 planning acceptance | Proposal-only: `define-backend-backup-route-ownership` adds an architecture-governance gate requiring current-head backup route/OpenAPI evidence, backup ownership class taxonomy, explicit `cleanup_old_backups.py` and `backup_service_health` ownership, security/permission/audit/rollback evidence, and separate D2.3/D2.5/D2.6 lane handling before mutation; no backend source, frontend source, tests, generated client, docs/API, route behavior, OpenAPI schema, infrastructure backup code, probe URL, or PM2 changes are authorized | `openspec/changes/define-backend-backup-route-ownership/`; `docs/reports/quality/backend-backup-route-ownership-openspec-proposal-2026-05-21.md`; `governance/mainline/task-cards/pr-118.yaml` | Approved for governance/evidence task-list execution; no implementation or runtime mutation authorized |
| D2.5 Control-plane OpenAPI docs planning package | D2.5 | Control-plane OpenAPI docs stabilization remains a dedicated documentation/probe governance lane | Planning/evidence only: current smoke at HEAD `b39b7b3ee` reports routes=`548`, OpenAPI paths=`500`, broad control/status candidate routes=`128`, focused duplicate operationIds=`0`, `/health/readiness` absent, `/api/strategy-mgmt/{path:path}` runtime-only hidden, and `/metrics` as the focused duplicate runtime path/method; no route, OpenAPI, docs/API, source, frontend, test, PM2, or OpenSpec mutation is authorized | `docs/reports/quality/backend-control-plane-openapi-docs-planning-package-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Human review; if accepted, create a separate control-plane OpenAPI docs proposal or documentation issue before docs/API or route mutation |
| D2.5 Control-plane OpenAPI docs OpenSpec proposal | D2.5/F | Explicit proposal created for control-plane OpenAPI documentation stabilization after D2.5 planning acceptance | Proposal-only: `stabilize-backend-control-plane-openapi-docs` adds an API documentation gate requiring current-head route/OpenAPI/probe evidence, health/readiness taxonomy, metrics/docs/schema surface classification, runtime-vs-schema exposure classification, and separate D2.3/D2.4/D2.6 lane handling before docs/API or route mutation; no backend source, frontend source, tests, generated client, docs/API, route behavior, OpenAPI schema, probe URL, or PM2 changes are authorized | `openspec/changes/stabilize-backend-control-plane-openapi-docs/`; `docs/reports/quality/backend-control-plane-openapi-docs-openspec-proposal-2026-05-21.md`; `governance/mainline/task-cards/pr-117.yaml` | Approved for governance/evidence task-list execution; no implementation or runtime mutation authorized |
| D2.6 PM2 stateful gate approval governance package | D2.6 | Future PM2 stateful gate execution requires explicit approval or an approved named equivalent; issue `#92` remains a decision issue, not an execution issue | Governance/evidence only: health/status task `4.7` is already closed by `backend-health-status-pm2-gate-2026-05-18.md`; `run_pm2_integration_workflow.sh` includes stateful `pm2 stop all` / `pm2 delete all`; no PM2 command, runtime code, route, OpenAPI, docs/API, frontend, test, or OpenSpec mutation is authorized | `docs/reports/quality/backend-pm2-stateful-gate-approval-governance-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Human review; create `approve-backend-pm2-stateful-gate` or a named-equivalent approval runbook only when a future workline needs a fresh PM2 run |
| D2.6 PM2 stateful gate approval OpenSpec proposal | D2.6 | Explicit proposal created for PM2 stateful gate approval policy after D2.6 governance-package acceptance | Proposal-only: `approve-backend-pm2-stateful-gate` adds an architecture-governance gate requiring explicit approval records before `gate`, `regression`, `all`, read-only PM2 sampling, or named-equivalent PM2 validation; no PM2 command, service restart, backend source, frontend source, tests, generated client, docs/API, route behavior, OpenAPI schema, probe URL, or movement of issue `#92` to `ready-for-agent` is authorized | `openspec/changes/approve-backend-pm2-stateful-gate/`; `docs/reports/quality/backend-pm2-stateful-gate-openspec-proposal-2026-05-21.md`; `governance/mainline/task-cards/pr-119.yaml` | Review and approve the OpenSpec policy proposal before treating it as the PM2 approval contract |
| D2 downstream decision rollup closeout | D2 closeout | D2.1-D2.6 downstream packages are summarized as a complete decision package; issue `#92` remains a parent decision issue | Rollup/evidence only: PRs `#96`-`#113` are merged; issue `#92` is `OPEN` with `ready-for-human` and `ready-for-downstream`; `ready-for-agent` remains absent; first recommended true implementation lane, D2.1a `TechnicalPatternDetectionService` DI pilot, is now closed end-to-end | `docs/reports/quality/backend-openspec-issue92-downstream-rollup-closeout-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92`; PRs `#112` and `#113` | Human decision whether to create the next concrete child issue or OpenSpec branch; this rollup does not authorize implementation |
| D2.1a TechnicalPatternDetectionService DI implementation | D2.1a.1 | First service-tier route-level DI pilot merged; `_technical_patterns_router.py` now exposes `get_technical_pattern_detection_service()`, `detect_patterns()` receives the service through `Depends`, and focused route tests use `app.dependency_overrides` | Reviewed/pass in current thread: PR `#112` checks passed, merge commit `80582643578d587ead81ccb3d23dcd2a52668dba`; route regression `9 passed`; service+route `19 passed`; ruff passed; placeholder-env `app.main` import passed; OpenSpec strict valid; mainline scope gate passed; GitNexus compare low risk with `0` changed symbols and `0` affected processes | `https://github.com/chengjon/mystocks/pull/112`; `docs/reports/quality/backend-technical-pattern-di-pilot-implementation-2026-05-21.md`; `openspec/changes/inject-technical-pattern-detection-service-di/` | D2.1a final OpenSpec checklist governance closeout |
| D2.1a final OpenSpec checklist governance closeout | D2.1a.1 | OpenSpec task `5.3` marked complete with issue `#92` closeout comment evidence; D2.1a is closed from implementation plus checklist governance perspectives | Reviewed/pass in current thread: PR `#113` checks passed, merge commit `c7e263b8fcdeea4fc952a86d64ac555ca6dde6ce`; changed files limited to `tasks.md` and `pr-113.yaml`; mainline scope gate changed files=`2`, violations=`0`; GitNexus compare low risk with `0` changed symbols and `0` affected processes | `https://github.com/chengjon/mystocks/pull/113`; `https://github.com/chengjon/mystocks/issues/92#issuecomment-4508297089`; `openspec/changes/inject-technical-pattern-detection-service-di/tasks.md` | No further D2.1a work; select a new approved child lane before any additional implementation |
| D2.x OpenSpec proposal approvals recorded | D2.3-D2.6 | Human maintainer approval recorded for D2.3/D2.4/D2.5/D2.6 proposal task-list entry into governance/evidence execution | Approval-only: each change may execute its governance/evidence `tasks.md` checklist with current-head freshness; no backend source, frontend source, tests, generated client, docs/API edits, route behavior, OpenAPI schema/exposure, probe URL change, PM2 command execution, service restart/recreation, implementation issue creation, or movement of issue `#92` to `ready-for-agent` is authorized | `docs/reports/quality/backend-openspec-d2-proposal-approval-record-2026-05-22.md`; `governance/mainline/task-cards/pr-120.yaml` | Execute approved governance/evidence tasks and keep every downstream decision tied to refreshed evidence |

## OpenSpec Branch Register

| Change ID | State | Parent source | Primary evidence | Scope | Next action |
|---|---|---|---|---|---|
| `sequence-backend-architecture-unblocks` | `archived-merged` | Master execution plan | Runtime triage, schema closure, freshness, singleton matrix, error-contract verification | First gate branch for runtime unblock and evidence refresh | Archived by PR `#86`; future work must use the archived evidence as baseline and open a follow-up branch for new implementation |
| `canonicalize-backend-route-unified-response-contracts` | `archived-merged` | `sequence-backend-architecture-unblocks` Task 8.8 | UnifiedResponse contract guard blocker: 27 errors across 4 changed route files now reduced to 0 | Dedicated route-contract migration for `data_quality.py`, `indicator_cache.py`, `signal_history_response.py`, and `technical_analysis.py`; implementation merged via PR `#85` | Archived by PR `#86`; keep implementation notes as follow-up candidates, not blockers |
| `split-backend-core-modules-with-compatibility-wrappers` | `archived-merged` | Existing OpenSpec line | Core split reconciliation | Core helper split continuation | Archived by PR `#90`; future Core split work requires a new concrete implementation plan and approval |
| `github-issue-92-backend-openspec-issue15` | `downstream-rollup-review-aligned` | Current review-thread approval, issue `#83` acceptance, downstream split draft, human split acceptance, D2.1-D2.6 rollup, and review-aligned evidence clarification | Post-approval implementation decision boundary | Decision/design issue only; no implementation work | Human decision whether to create a concrete D2.1a implementation issue or OpenSpec branch; keep issue `#92` locked as parent decision issue |
| `select-backend-technical-pattern-di-pilot` | `design-packet-prepared` | Issue `#92` downstream split acceptance | First DI lifecycle pilot design packet | Provider shape, dependency override strategy, teardown, rollback, and verification gates for `TechnicalPatternDetectionService` | Human review before creating any implementation issue or OpenSpec branch |
| `inject-technical-pattern-detection-service-di` | `implementation-ready-for-review` | D2.1 design packet, D2.1a authorization plan, proposal review, and implementation evidence | First implementation child branch for `TechnicalPatternDetectionService` DI pilot | Route-local provider, FastAPI dependency override test seam, rollback, and focused verification for `_technical_patterns_router.py` | PR review / merge decision; do not broaden to a second service DI pilot in this branch |
| `decide-backend-core-validation-wrapper-retirement` | `active-source-migration-complete` | Issue `#92` downstream split acceptance and validation helper split archive | Core validation compatibility wrapper retirement readiness and staged migration | D2.2a active source migration is complete; docs/API examples and compatibility-test conversion remain separate gates | D2.2b docs/API examples canonicalization or explicit waiver; wrapper deletion remains blocked |
| `define-backend-backup-route-ownership` | `approved-for-governance-execution` | Issue `#92` downstream split acceptance, D2.4 planning package, D2.3 route governance proposal, and D2.5 control-plane docs proposal | Explicit OpenSpec proposal plus backup route ownership planning, `cleanup_old_backups.py`, and backup route/OpenAPI evidence | Backup, recovery, scheduler, integrity, cleanup, health, safety, security, consumer, OpenAPI, and rollback ownership gates | Review and approve the OpenSpec change before executing backup ownership tasks or opening implementation lanes |
| `stabilize-backend-control-plane-openapi-docs` | `approved-for-governance-execution` | Issue `#92` downstream split acceptance, D2.5 planning package, route/OpenAPI/probe refresh, and D2.3 route governance proposal | Explicit OpenSpec proposal plus control-plane docs/probe planning, health/readiness taxonomy, OpenAPI docs UI/schema routes, metrics/status probes, and runtime-only compat redirects | Documentation/probe governance for liveness, readiness, service health, detailed health, status, metrics, docs UI, OpenAPI schema, runtime-only compat redirects, and intentionally absent aliases | Review and approve the OpenSpec change before executing docs/probe governance tasks or opening implementation lanes |
| `approve-backend-pm2-stateful-gate` | `approved-for-governance-execution` | Issue `#92` downstream split acceptance, D2.6 approval-governance package, and historical health/status PM2 evidence | Explicit OpenSpec proposal for PM2 stateful workflow approval strategy and named-equivalent rules | Approval records for `run_pm2_integration_workflow.sh` modes, stateful service mutation, rollback, evidence artifact routing, read-only sampling, and named equivalents | Review and approve the policy proposal; create a small approval issue or approved runbook only when a future workline needs a fresh PM2 run |
| `close-backend-schema-dual-directory` | `candidate` | Master execution plan | Schema dual-directory closure | Schema exports, consumer migration, shim retirement decision | Create only after `sequence-backend-architecture-unblocks` schema tasks are accepted |
| `refresh-backend-route-openapi-governance` | `decision-package-prepared-for-review` | Master execution plan, route/OpenAPI/probe refresh, D2.3 planning package, and proposal approval record | Decision package prepared with current-head route table, OpenAPI, probe matrix, trading ownership, runtime-vs-schema, and consumer contract evidence | Route table, OpenAPI, operationId, probe matrix, trading ownership, control-plane, backup, compatibility, and schema-exposure classification; no route/OpenAPI/source/docs/API/PM2 mutation | Review `backend-route-openapi-governance-decision-package-2026-05-22.md`; do not open implementation lanes before acceptance |
| `define-backend-service-seams-and-singleton-pilots` | `candidate` | Master execution plan | Singleton lifecycle routing matrix | Service seam definition, interface/test-double pilot strategy | Create as a design proposal after complete classification |

## Dependency and Freshness Matrix

| Branch | Depends On | Last Freshened HEAD | Freshness note |
|---|---|---|---|
| A. Architecture Baseline | Current evidence artifacts | `7b097fffd` | Baseline contains stale historical snapshots; newer evidence must be linked instead of silently replacing history |
| B. Master Execution Plan | Architecture baseline and cross-line reports | `7b097fffd` | Control plan; update only when governance flow changes |
| C. `sequence-backend-architecture-unblocks` | Human approval, current runtime blocker verification | `7b097fffd` | Tasks 1.x through 8.x complete; runtime blocker closed, schema shim closure implemented, route/OpenAPI/probe evidence refreshed, service seam proposal path recorded |
| D. Core split continuation | Task 3.2 disposition, #83 evidence acceptance, runtime evidence refresh | `7b097fffd` | Batch 2 remains blocked |
| E. Schema dual-directory closure | `app.schema` consumer scan and `app.schemas` export proof | `7b097fffd` | Task 3.x complete; root checkout now has 0 legacy `app.schema` consumers and canonical exports are live |
| F. Route/OpenAPI governance | Healthy `app.main` import chain and current-head evidence refresh | `c173bbc8d` | D2.3 route/OpenAPI decision package is prepared for review with current-head route/OpenAPI/probe/consumer artifacts; D2.4 backup, D2.5 control-plane docs, and D2.6 PM2 lanes remain separate; no backup, docs/API, route mutation, OpenAPI exposure change, or PM2 approval decision is authorized until review acceptance |
| G. Service seams and singleton pilots | Full service classification plus interface/test-double strategy | `7b097fffd` | Task 6.x proposal path complete; service directory is dirty, no implementation batch is scheduled, and future work needs a clean candidate packet plus approved proposal |

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
| P2 | Prepare singleton/service seam design proposal after full classification | Future service seam lane | Task 6.x proposal path complete; candidate proposal remains uncreated until human approval |
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
