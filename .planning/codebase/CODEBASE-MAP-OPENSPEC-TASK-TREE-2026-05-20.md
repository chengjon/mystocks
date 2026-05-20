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
│   ├── Source: openspec/changes/sequence-backend-architecture-unblocks/
│   ├── State: active
│   ├── Role: First concrete branch extracted from the master plan and reports
│   ├── Scope C-shallow: Runtime unblock, schema shim closure, codebase-map
│   │                   consistency, and runtime evidence refresh
│   ├── Scope C-deep-prep: Singleton/service seam classification and proposal
│   │                     preparation only
│   └── Next gate: Continue schema shim closure and runtime evidence refresh;
│                  keep deep proposal preparation separate
│
├── D. Existing OpenSpec Branch: split-backend-core-modules-with-compatibility-wrappers
│   ├── Source: openspec/changes/split-backend-core-modules-with-compatibility-wrappers/
│   ├── State: blocked
│   ├── Role: Core helper split line
│   ├── Current fact: Batch 1 complete; Batch 2 must not start on ambiguous 3.2 state
│   └── Next gate: Explicit Task 3.2 disposition, #83 evidence acceptance,
│                  and runtime evidence refresh
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
| `canonicalize-backend-route-unified-response-contracts` implementation | C, D | Four target route modules now declare canonical `UnifiedResponse[...]` contracts and direct model/list/dict success payloads are wrapped under `data` | `APPROVE_WITH_NOTES`: GitNexus impact LOW for four target files; guard baseline `27` errors now `0`; ruff issues `0`; `app.main` routes=`548`; health route suite `112 passed`; OpenAPI paths=`500`, operations=`536`, duplicate operationIds=`0`; singleton-none guard `0` errors. Notes recorded for `data_source_config.py` response-module runtime dependency mix, `monitoring_watchlists.py` module-level fallback state, and wide commit scope. | `00101699b`; `docs/reports/quality/backend-route-unified-response-contract-implementation-2026-05-20.md`; `openspec/changes/canonicalize-backend-route-unified-response-contracts/tasks.md` | Decide push/merge path for `00101699b`; track non-blocking notes as future candidates |
| `sequence-backend-architecture-unblocks` Task 3.x | E | Schema validation models now live under canonical `app.schemas`; legacy `app.schema` remains a thin compatibility shim; direct legacy consumers are migrated | Reviewed/pass in current thread: GitNexus file impact LOW, schema ruff passed, `test_validation_models.py` `60 passed`, import smoke confirms `app.schemas`, `app.schemas.validation_models`, `app.schema`, and `app.schema.validation_models`; fresh scan reports `LEGACY_CONSUMERS=0` | `docs/reports/quality/backend-schema-shim-closure-implementation-2026-05-20.md`; `openspec/changes/sequence-backend-architecture-unblocks/tasks.md` | Task 4.x codebase-map consistency and Task 5.x route/OpenAPI evidence refresh |
| `sequence-backend-architecture-unblocks` Task 4.x | A, B, I | Codebase map and master execution plan no longer treat stale HTTPException counts or schema dual-directory status as current truth | Reviewed/pass in current thread: GH #77 currently `CLOSED`; current working-tree scan at HEAD `7b097fffd` reports fixed-field error-contract buckets all `0`; Evidence Artifact Index now distinguishes stale historical artifacts, current-head runtime/schema evidence, and commit-scoped evidence | `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md`; `docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md`; `openspec/changes/sequence-backend-architecture-unblocks/tasks.md` | Task 5.x route/OpenAPI evidence refresh |
| `sequence-backend-architecture-unblocks` Task 5.x | F | Current route table, OpenAPI snapshot, and probe consumer matrix regenerated after runtime import chain became healthy | Reviewed/pass in current thread: artifacts generated at HEAD `7b097fffd`; route table routes=`548`; OpenAPI paths=`500`, operations=`536`, duplicate operationIds=`0`, warnings=`0`; probe matrix scanned files=`5782`, hit files=`188`; duplicate runtime path/method limited to `GET /metrics` hidden+visible control-plane routes | `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20.md`; `.planning/codebase/generated/backend-route-table-2026-05-20.json`; `.planning/codebase/generated/route-openapi-snapshot-2026-05-20.json`; `.planning/codebase/generated/probe-consumer-matrix-2026-05-20.json` | Task 6.x singleton/service seam proposal path and route governance classification |
| `sequence-backend-architecture-unblocks` Task 6.x | G | Service singleton/lifecycle seam work remains proposal-only; current inventory classifies candidates but schedules no implementation batch | Reviewed/pass in current thread: service inventory artifact generated at HEAD `7b097fffd`; service directory dirty count `18`; heuristic buckets external-client wrapper `69`, DB/session-backed `24`, cache/task-running `17`, interface/test-double candidate needing review `28`, separate design gate `2`; no service code edited | `docs/reports/quality/backend-service-seam-proposal-path-2026-05-20.md`; `.planning/codebase/generated/service-singleton-inventory-2026-05-20.json` | Task 7.x verification and Task 8.x closure |
| `sequence-backend-architecture-unblocks` Task 7.x | C, E, F, G | Governance and targeted technical verification completed for the sequence branch artifacts | Reviewed/pass in current thread: path-limited `git diff --check` no output; generated JSON parse OK; added-file whitespace problems `0`; markdown governance `checked_files=10`, `errors=0`; OpenSpec strict valid; schema ruff passed; `test_validation_models.py` `60 passed` | `openspec/changes/sequence-backend-architecture-unblocks/tasks.md`; validation command outputs from current thread | Task 8.x closure |
| `sequence-backend-architecture-unblocks` Task 8.x | C, E, F, G | Runtime unblock, schema shim decision, route/OpenAPI/probe refresh, and service seam proposal split are recorded; broad implementation remains gated | Reviewed/pass in current thread: tasks.md now records 1.x through 8.x complete; no endpoint retirement, service migration, broad refactor, or OpenSpec archive performed | reports and artifacts listed above | Human review, path-limited commit decision, then OpenSpec archive decision if accepted |
| `sequence-backend-architecture-unblocks` Task 8.5 | F, G | Paired reviews for the Task 5.x and Task 6.x reports were evaluated and absorbed where technically correct | Reviewed/pass in current thread: OpenSpec directory exists in current worktree and is now named explicitly; route report explains `endpoint_modules=98` and `category_counts.strategy_compat`; service report corrects `separate_design_gate` to `StockSearchService` and `TechnicalPatternDetectionService` and explains `111` versus `140` scan-method difference | `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20-review.md`; `docs/reports/quality/backend-service-seam-proposal-path-2026-05-20-review.md`; updated target reports | Re-run markdown/OpenSpec validation, then human review / commit decision |
| `sequence-backend-architecture-unblocks` Task 8.6 | C, E, F, G | Path-limited commit readiness recorded without staging or committing | Reviewed/pass in current thread: commit boundary report separates runtime/schema source paths, governance/evidence paths, optional review-input files, and unrelated dirty worktree entries; no broad `git add` performed | `docs/reports/quality/backend-sequence-unblocks-commit-readiness-2026-05-20.md` | Human commit choice before any OpenSpec archive |

## OpenSpec Branch Register

| Change ID | State | Parent source | Primary evidence | Scope | Next action |
|---|---|---|---|---|---|
| `sequence-backend-architecture-unblocks` | `source-unblock-commit-approved-with-notes` | Master execution plan | Runtime triage, schema closure, freshness, singleton matrix, error-contract verification | First gate branch for runtime unblock and evidence refresh | Runtime source unblock and route-contract migration are committed in isolated worktree as `00101699b`; next gate is push/merge decision |
| `canonicalize-backend-route-unified-response-contracts` | `implemented-approved-with-notes` | `sequence-backend-architecture-unblocks` Task 8.8 | UnifiedResponse contract guard blocker: 27 errors across 4 changed route files now reduced to 0 | Dedicated route-contract migration for `data_quality.py`, `indicator_cache.py`, `signal_history_response.py`, and `technical_analysis.py`; governance proposal committed in `9addc2458`, review absorbed in root commit `7eafe00e2`, implementation committed as `00101699b` | Decide push/merge path; keep notes as follow-up candidates, not blockers |
| `split-backend-core-modules-with-compatibility-wrappers` | `blocked` | Existing OpenSpec line | Core split reconciliation | Core helper split continuation | Do not start Batch 2 until gate disposition is explicit |
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
