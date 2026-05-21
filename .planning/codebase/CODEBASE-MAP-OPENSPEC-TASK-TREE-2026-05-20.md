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
│   └── Next gate: Human review of the design packet before creating any
│                  implementation issue or moving any issue to `ready-for-agent`
│
├── D2.2. Core Validation Wrapper Retirement Readiness
│   ├── Source evidence:
│   │   `backend-core-validation-wrapper-retirement-readiness-2026-05-21.md`
│   ├── State: readiness-packet-prepared
│   ├── Role: Decide whether `app.core.validation_messages` can retire
│   ├── Current fact: wrapper deletion is not ready; active source imports remain
│   │                 in `validators.py` and `error_codes.py`, and docs still
│   │                 teach the legacy path
│   └── Next gate: Human review before creating a separate D2.2a active-source
│                  consumer migration issue; wrapper deletion stays locked
│
├── E. Candidate Branch: close-backend-schema-dual-directory
│   ├── Source evidence: backend-schema-dual-directory-closure-2026-05-19.md
│   ├── State: blocked
│   ├── Role: Migrate legacy app.schema consumers and decide shim retirement
│   └── Next gate: Prove canonical app.schemas exports and compatibility tests
│
├── F. Candidate Branch: refresh-backend-route-openapi-governance
│   ├── Source evidence: backend-api-flat-package-closure-records-2026-05-19.md
│   ├── State: ready-after-sequence-refresh
│   ├── Role: Rebuild route table, OpenAPI, operationId, and probe consumer evidence
│   └── Next gate: Use Task 2.x runtime evidence, then run route/OpenAPI/probe refresh
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
| D2.2 Core validation wrapper retirement readiness | D2.2 | Readiness packet prepared for `app.core.validation_messages` retirement; deletion is not ready because active source consumers and API docs still reference the legacy path | Review-ready readiness only: compatibility test passed `2 passed`; placeholder-env import smoke passed; active source blockers are `web/backend/app/core/validators.py` and `web/backend/app/core/error_codes.py` | `docs/reports/quality/backend-core-validation-wrapper-retirement-readiness-2026-05-21.md`; `https://github.com/chengjon/mystocks/issues/92` | Human review; if accepted, create a separate D2.2a active-source consumer migration issue before any wrapper deletion |

## OpenSpec Branch Register

| Change ID | State | Parent source | Primary evidence | Scope | Next action |
|---|---|---|---|---|---|
| `sequence-backend-architecture-unblocks` | `archived-merged` | Master execution plan | Runtime triage, schema closure, freshness, singleton matrix, error-contract verification | First gate branch for runtime unblock and evidence refresh | Archived by PR `#86`; future work must use the archived evidence as baseline and open a follow-up branch for new implementation |
| `canonicalize-backend-route-unified-response-contracts` | `archived-merged` | `sequence-backend-architecture-unblocks` Task 8.8 | UnifiedResponse contract guard blocker: 27 errors across 4 changed route files now reduced to 0 | Dedicated route-contract migration for `data_quality.py`, `indicator_cache.py`, `signal_history_response.py`, and `technical_analysis.py`; implementation merged via PR `#85` | Archived by PR `#86`; keep implementation notes as follow-up candidates, not blockers |
| `split-backend-core-modules-with-compatibility-wrappers` | `archived-merged` | Existing OpenSpec line | Core split reconciliation | Core helper split continuation | Archived by PR `#90`; future Core split work requires a new concrete implementation plan and approval |
| `github-issue-92-backend-openspec-issue15` | `downstream-split-accepted` | Current review-thread approval, issue `#83` acceptance, downstream split draft, and human split acceptance | Post-approval implementation decision boundary | Decision/design issue only; no implementation work | Draft D2.1 `TechnicalPatternDetectionService` DI design packet; keep implementation locked behind separate approval |
| `select-backend-technical-pattern-di-pilot` | `design-packet-prepared` | Issue `#92` downstream split acceptance | First DI lifecycle pilot design packet | Provider shape, dependency override strategy, teardown, rollback, and verification gates for `TechnicalPatternDetectionService` | Human review before creating any implementation issue or OpenSpec branch |
| `decide-backend-core-validation-wrapper-retirement` | `readiness-packet-prepared` | Issue `#92` downstream split acceptance and validation helper split archive | Core validation compatibility wrapper retirement readiness | Consumer scan, import smoke, compatibility tests, retirement blockers, and rollback path for `app.core.validation_messages` | Human review before creating D2.2a active-source consumer migration; wrapper deletion remains blocked |
| `close-backend-schema-dual-directory` | `candidate` | Master execution plan | Schema dual-directory closure | Schema exports, consumer migration, shim retirement decision | Create only after `sequence-backend-architecture-unblocks` schema tasks are accepted |
| `refresh-backend-route-openapi-governance` | `candidate-unblocked` | Master execution plan | API flat/package closure records | Route table, OpenAPI, operationId, probe matrix | Can be prepared after Task 5.x route/OpenAPI refresh evidence is recorded |
| `define-backend-service-seams-and-singleton-pilots` | `candidate` | Master execution plan | Singleton lifecycle routing matrix | Service seam definition, interface/test-double pilot strategy | Create as a design proposal after complete classification |

## Dependency and Freshness Matrix

| Branch | Depends On | Last Freshened HEAD | Freshness note |
|---|---|---|---|
| A. Architecture Baseline | Current evidence artifacts | `7b097fffd` | Baseline contains stale historical snapshots; newer evidence must be linked instead of silently replacing history |
| B. Master Execution Plan | Architecture baseline and cross-line reports | `7b097fffd` | Control plan; update only when governance flow changes |
| C. `sequence-backend-architecture-unblocks` | Human approval, current runtime blocker verification | `7b097fffd` | Tasks 1.x through 8.x complete; runtime blocker closed, schema shim closure implemented, route/OpenAPI/probe evidence refreshed, service seam proposal path recorded |
| D. Core split continuation | Task 3.2 disposition, #83 evidence acceptance, runtime evidence refresh | `7b097fffd` | Batch 2 remains blocked |
| E. Schema dual-directory closure | `app.schema` consumer scan and `app.schemas` export proof | `7b097fffd` | Task 3.x complete; root checkout now has 0 legacy `app.schema` consumers and canonical exports are live |
| F. Route/OpenAPI governance | Healthy `app.main` import chain | `7b097fffd` | Task 5.x refresh complete; route governance can proceed with current artifacts, with `/metrics` duplicate path/method classified as a control-plane taxonomy item |
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
