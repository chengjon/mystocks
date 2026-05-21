# CODEBASE-MAP OpenSpec Execution Plan

> **权威来源声明**:
> 本文件是 OpenSpec 风格任务草案和人工审核输入，不代表当前仓库的唯一事实状态，也不授权代码变更、GitHub issue 状态变更或 OpenSpec proposal 创建。
> 涉及共享规则、审批门禁与执行口径时，请先核对 `architecture/STANDARDS.md`、`openspec/AGENTS.md`、当前 `openspec/changes/`、相关 GitHub issue 与最近一次实际验证结果。

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` only after this plan is approved. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` into a governed OpenSpec execution queue with explicit routing, evidence artifacts, and approval gates.

**Architecture:** Keep the codebase map as planning input, not implementation authorization. Execute blocker fixes and low-risk migration batches only after review, keep decision work separate from code movement, and attach freshness metadata as each artifact is produced.

**Tech Stack:** OpenSpec CLI, GitHub CLI, Python 3.12, FastAPI, pytest, ruff, GitNexus, markdown governance checks.

---

## Scope and Guardrails

- This plan is a reviewable draft, not an approved implementation order.
- No new OpenSpec proposal is created by this plan.
- No GitHub issue label is changed by this plan.
- No backend implementation is authorized by this plan; any source edit requires a separate approved implementation lane.
- Proposal-First remains governed by `architecture/STANDARDS.md` and `openspec/AGENTS.md`; if this plan, a report, or an OpenSpec draft appears to permit implementation without approval, treat that as non-authorizing wording and return to the governance gate.
- Runtime evidence must be refreshed against the current HEAD before it is treated as current truth.
- Pre-unblock local smoke finding before cross-line reconciliation: `ContractDriftIncidentListResponse` imported successfully; `app.main` import failed through the `web/backend/app/api/data_lineage.py` import chain because `web/backend/app/api/_data_lineage_responses.py` used `@asynccontextmanager` without importing it.
- 2026-05-20 update: `sequence-backend-architecture-unblocks` Task 2.x restored the runtime import chain in a separate approved implementation lane. Current verification records `app.main` routes=`548`, `test_health_route_conflicts.py` `112 passed`, OpenAPI paths=`500`, and duplicate operationIds=`0`. Task 3.x then closed the validation-model schema seam by moving the implementation to canonical `app.schemas.validation_models`, retaining `app.schema` as a thin compatibility shim, and proving `LEGACY_CONSUMERS=0`.
- 2026-05-20 Task 5.x update: route/OpenAPI/probe artifacts were refreshed at HEAD `7b097fffd`: route table routes=`548`; OpenAPI paths=`500`, operations=`536`, duplicate operationIds=`0`, warnings=`0`; probe matrix scanned files=`5782`, hit files=`188`. The only duplicate runtime path/method excluding `HEAD` is `GET /metrics`, split between hidden `app.main.prometheus_metrics` and visible `app.api.prometheus_exporter.metrics`.
- 2026-05-20 Task 6.x update: service seam work remains proposal-only. The refreshed heuristic inventory scans `152` service Python files and classifies `28` interface/test-double candidates needing review, but the service directory is dirty and no lifecycle implementation batch is scheduled from this evidence.
- 2026-05-20 Task 7.x / 8.x update: `sequence-backend-architecture-unblocks` tasks are complete and verified. This closes the front-door unblock/evidence branch for review, but it does not authorize route retirement, service lifecycle migration, schema shim retirement, broad refactor, or OpenSpec archive without the next human gate.

## Cross-Line Progress Inputs (2026-05-19)

| Report | Status absorbed into this plan | Execution-plan impact |
|---|---|---|
| `docs/reports/quality/backend-core-split-line-summary-and-next-plan-2026-05-19.md` | Core split line is runtime-gate reconciled but not fully closed. Startup blockers were unblocked in an implementation worktree via commits `71d29d3b7` and `2d6682e81`; PM2 backend startup, health/readiness smoke, and OpenAPI/route drift tasks `4.3`, `4.4`, `4.5` have evidence. OpenSpec task `3.2`, #83 evidence reconciliation, issue15 revision, and archive decision remain open. | Do not start Core helper Batch 2 until governance reconciliation is accepted and the current checkout / implementation-worktree evidence mismatch is resolved. Runtime blocker handling becomes a reconciliation task, not a blind bug-fix task. |
| `docs/reports/quality/backend-openspec-line-summary-and-next-plan-2026-05-19.md` | Backend OpenSpec publication / triage line now records issue `#80` as open with `ready-for-human`, issue `#83` as open with `ready-for-agent`, and issue15 as still unpublished with `BLOCKED_BY_TODO: shared evidence package.` unresolved. The `ready-for-agent` scope for `#83` is evidence-package work only. | Update this plan so `#83` is no longer treated as a needs-triage item. Wait for the `#83` agent evidence result before issue15 publication or placeholder replacement. Do not let `#83` fix `ContractDriftIncidentListResponse` or authorize backend implementation. |
| `docs/reports/P3-C5-exception-consolidation-completion-report.md` | P3-C5 reports `app/api` static scans at zero for `raise HTTPException`, `except HTTPException`, `response_model=APIResponse`, and `return APIResponse(...)`. It also reports all `web/backend/app/api` route source files at `<=700` lines after companion `_responses.py`, `_models.py`, and `_helpers.py` extraction. | Do not treat `app/api` HTTPException migration as an open primary task. For `#77` / P3-C5, this completion report supersedes the older live-count language in `backend-lifecycle-di-workline-summary-2026-05-19.md`. Error-contract work is now verification of the completion report, out-of-scope retained exceptions, companion-file import style, and separate UnifiedResponse guard follow-up for 266 historical routes. |
| `docs/reports/quality/backend-lifecycle-di-workline-summary-2026-05-19.md` | #78 adapter lifecycle DI has multiple low-risk adapter batches complete. #79 has a TradingView service pilot complete, but GH #79 is not done. Remaining service candidates require classification; `realtime_mtm` needs separate lifecycle proposal/design gate; `adapter_loader` remains blocked by the Core split compatibility matrix. | Service lifecycle work must use the TradingView pattern for the next stateless service only after candidate classification. `realtime_mtm` and `adapter_loader` must not be folded into generic service/adapter batches, and `#78`/`#79` should stay separated from error-contract evidence. |
| `docs/reports/evidence/miniqmt/2026-05-19-mystocks-controlled-evidence-summary-for-review.md` | MyStocks raw/candidate `mystocks_dry_run` evidence is complete; validated-forward evidence was generated locally at `docs/reports/evidence/miniqmt/2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json` for `payload_hash=268b62bb0fb0891833ef1998d4993d6531cc6a9d84aaecb911da0cd559d2357e`, evidence SHA-256 `4fe9be93061aeec011c16aeabcbb14eef17a35bf6a5ba578258c2e5388ccb24c`, and has since passed miniQMT validator / preview / apply. miniQMT manual promote to `validated` and `authoritative-ready` is complete; final `authoritative` approval remains a manual owner/operator gate. | Track as external evidence alignment only. Do not block backend codebase-map execution on miniQMT receive-side work, and do not treat MyStocks evidence apply or `authoritative-ready` maturity as backend promotion, source cutover, ClickHouse write approval, or final `authoritative` approval. |

## OpenSpec Routing Summary

| Work item | Routing target | Current status | Notes |
|---|---|---|---|
| GH #83 evidence-package execution | Existing issue 14 publication flow | OPEN / ready-for-agent | Scope is limited to C/E/F evidence package work; wait for agent output before issue15 publication |
| Issue15 publication | Existing issue 15 draft | Unpublished / blocked | Keep `BLOCKED_BY_TODO: shared evidence package.` unresolved until #83 evidence is completed or explicitly accepted |
| `_data_lineage_responses` import blocker | Bug-fix evidence first; code fix only if approved | Closed by `sequence-backend-architecture-unblocks` Task 2.x | Import seam bug, not an architecture proposal; remaining route/OpenAPI work is evidence refresh, not broad refactor approval |
| Core helper split continuation | `split-backend-core-modules-with-compatibility-wrappers` | Runtime-gate reconciled, not fully closed | Hold Batch 2 until Task 2 governance reconciliation is accepted |
| API flat→package closure records | Existing router consolidation evidence lane | Evidence-first with Task 5.x runtime artifacts available | Runtime route/OpenAPI/probe evidence now exists; classify control-plane duplicates such as `GET /metrics` separately from business API flat/package closure |
| Service seam and lifecycle DI | `migrate-backend-singletons-to-lifecycle-di` / issue 15 decision input | #78 adapter side mostly done; #79 service side in pilot; Task 6.x proposal path complete | Define canonical seams per service before replacing pass-through locators; isolate `realtime_mtm` and `adapter_loader`; no new implementation batch until a clean candidate packet and approved proposal exist |
| CSRF composition root | `05-csrf-protection` / future decision pack | Design decision | Decide test factory role and token manager ownership first |
| Error contract verification | Task 10 / P3-C5 completion review | Completion report exists | Verify current HEAD against the completion report and handle only the remaining guard / historical-route follow-up; keep it separate from service lifecycle routing |
| Schema dual directory | `sequence-backend-architecture-unblocks` Task 3.x plus future shim-retirement decision | Task 3.x complete | `validation_models.py` is canonical under `app.schemas`; `app.schema` remains a thin shim until external/generated-code consumer audit |

## Execution Waves

| Wave | Purpose | Tasks |
|---|---|---|
| Wave 1 | Reconcile runtime evidence, #83, and Core split governance | Tasks 1, 2 + Continuous Task C1 |
| Wave 2 | Low-risk evidence and decision records | Tasks 3, 4, 5, 8, 10 + Continuous Task C1 |
| Wave 3 | Runtime diff and architecture decisions | Tasks 6, 7 + Continuous Task C1 |
| Wave 4 | Conditional Batch 2 candidate packet | Task 9 only after Task 2 governance reconciliation is accepted; implementation requires a separate concrete plan |

## Continuous Task C1: Freshness and adoption metadata

**Files:**
- Modify: `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md`
- Create or update: `docs/reports/quality/codebase-map-freshness-2026-05-19.md`

- [ ] **Step C1.1: Update freshness metadata after every task**

For each generated report or snapshot, record:
- `generated_at`
- `git_head`
- `current_head_checked_at_review`
- `stale_if_head_mismatch`
- whether it is dirty-worktree, clean worktree, detached HEAD, or commit-scoped evidence

- [ ] **Step C1.2: Update the codebase map evidence index incrementally**

After each approved task completes, add its artifact path to the Evidence Artifact Index. Do not wait until the end of the line.

- [ ] **Step C1.3: Preserve authorization boundaries**

Every freshness/adoption update must keep the wording that this plan does not authorize code changes, issue creation, label changes, or a new OpenSpec proposal.

Verification:
- `git diff --check -- .planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md docs/reports/quality/codebase-map-freshness-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json .planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md docs/reports/quality/codebase-map-freshness-2026-05-19.md`

## Task 1: Reconcile GH #83 publication state and runtime import evidence

**Files:**
- Create: `docs/reports/quality/backend-openspec-issue83-runtime-triage-2026-05-19.md`
- Modify: `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md`

- [ ] **Step 1.1: Re-read the current GitHub issue state**

```bash
gh issue view 83 --json number,state,labels,body,url
gh issue view 80 --json number,state,url
```

Expected:
- issue `#83` remains `OPEN`
- labels remain exactly `enhancement` and `ready-for-agent`
- issue `#80` approval trail remains present

- [ ] **Step 1.2: Confirm which runtime evidence is current**

Read and cite:

- `docs/reports/quality/backend-core-split-line-summary-and-next-plan-2026-05-19.md`
- `docs/reports/quality/backend-core-split-runtime-gates-2026-05-19.md`, as commit-scoped evidence from `bbb399071 docs(core): record runtime gate evidence` if the file is absent from the current root checkout
- `docs/reports/quality/backend-openspec-line-summary-and-next-plan-2026-05-19.md`

The report must distinguish:

- implementation-worktree evidence that says runtime gates passed after commits `71d29d3b7` and `2d6682e81`, with evidence recorded in `bbb399071`
- current-checkout evidence from the next smoke command
- stale blocker language that still mentions `ContractDriftIncidentListResponse`
- the publication / triage line that records `#83` as `ready-for-agent` for evidence-package work only

- [ ] **Step 1.3: Record branch-state preflight before interpreting smoke**

Record:

```bash
git log -1 --oneline
git ls-remote origin refs/heads/wip/root-dirty-20260403
git merge-base --is-ancestor bbb399071 HEAD
```

The report must state:
- current local HEAD
- remote `wip/root-dirty-20260403` HEAD
- whether the current local HEAD contains `bbb399071`
- whether a failure in the current checkout should be treated as a current-branch regression or stale dirty-checkout evidence

- [ ] **Step 1.4: Re-run the current checkout import smoke**

```bash
env PYTHONPATH=web/backend python -c "from app.api.contract.schemas import ContractDriftIncidentListResponse; print(ContractDriftIncidentListResponse.__name__)"
env PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"
pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov
```

Record actual results:
- `ContractDriftIncidentListResponse` import should pass.
- `app.main` import result must be recorded exactly.
- `web/backend/tests/test_health_route_conflicts.py` collection result must be recorded exactly.
- If `app.main` import or test collection fails in the `data_lineage.py` / `_data_lineage_responses.py` import chain, record the exact exception and failing file; do not edit code in this task, and route any source fix through a separate implementation lane.

- [ ] **Step 1.5: Stop on stale checkout or route a separate implementation-lane fix**

Task 1 must not edit backend source files. If the current checkout still fails in the `data_lineage.py` / `_data_lineage_responses.py` import chain, record one of these outcomes:
- stale checkout: current local HEAD does not contain `bbb399071`; reconcile branch/worktree state before treating the failure as current truth
- separate implementation lane required: open or route a non-#83 implementation fix with its own approval and GitNexus context / impact checks before any source edit
- unexpected regression: current local HEAD contains `bbb399071` but the import still fails; stop and produce a targeted blocker report

Do not apply a runtime import-chain fix under #83 evidence-package work.

- [ ] **Step 1.6: Record the publication/runtime alignment**

Write one report only: `docs/reports/quality/backend-openspec-issue83-runtime-triage-2026-05-19.md`.

The report must state:
- whether #83 remains `ready-for-agent` and limited to evidence-package work
- whether runtime import smoke is clean
- whether runtime OpenAPI and PM2 gates remain blocked
- whether Core split runtime gates `4.3`, `4.4`, and `4.5` should be treated as closed by the existing runtime evidence
- whether current checkout contains `bbb399071`
- whether any current-checkout failure is stale, a separate implementation-lane blocker, or an unexpected regression
- whether issue15 should remain unpublished until the `#83` evidence result is reviewed

Verification:
- `git diff --check -- docs/reports/quality/backend-openspec-issue83-runtime-triage-2026-05-19.md .planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-openspec-issue83-runtime-triage-2026-05-19.md`

## Task 2: Reconcile Core split governance before Batch 2

**Files:**
- Modify: `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md`
- Create: `docs/reports/quality/backend-core-split-governance-reconciliation-2026-05-19.md`
- Modify: `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` only for evidence indexing after validation

- [ ] **Step 2.1: Re-read the Core split governance inputs**

Read and cite:
- `docs/reports/quality/backend-core-split-line-summary-and-next-plan-2026-05-19.md`
- `docs/reports/quality/backend-core-split-runtime-gates-2026-05-19.md`, as commit-scoped evidence from `bbb399071 docs(core): record runtime gate evidence` if absent from the current root checkout
- `docs/reports/quality/backend-openspec-line-summary-and-next-plan-2026-05-19.md`
- `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md`
- `docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/15-decide-post-approval-plan.md`
- current GitHub issue `#83`

The reconciliation report must separate:
- implementation-worktree runtime evidence from current-checkout runtime evidence
- OpenSpec task `3.2` state from runtime gate tasks `4.3`, `4.4`, and `4.5`
- #83 `ready-for-agent` label state from #83 evidence-package completion
- #83 evidence-package completion from issue15 design-decision readiness
- archive readiness from local runtime-gate completion

- [ ] **Step 2.2: Decide whether the hold conditions are satisfied**

Batch 2 remains blocked unless the report explicitly says all of these are true:
- OpenSpec task `3.2` has a concrete `tasks.md` disposition: either checked complete with evidence, or unchecked with an explicit non-blocking note, owner, and scope
- #83 evidence package output is completed and accepted, or explicitly ruled outside the next helper batch
- issue15 draft has been revised or explicitly marked unchanged after the accepted #83 evidence result
- runtime-gate evidence is either current-checkout evidence or clearly labeled as commit-scoped implementation-worktree evidence
- archive remains disallowed unless the OpenSpec task list and issue-state gates say otherwise

Ambiguous wording that leaves `3.2` unresolved without owner/scope keeps Task 9 blocked.

- [ ] **Step 2.3: Update the OpenSpec task file with a non-execution note**

If Batch 2 is still blocked, add or preserve a note in `tasks.md` that says the next helper batch must not start before Task 2 reconciliation is accepted.

The task file must make `3.2` explicit:
- `[x]` only with concrete evidence and artifact links
- `[ ]` only with an explicit non-blocking note, owner, and scope
- no ambiguous “outside next helper batch” wording without a responsible owner and follow-up boundary

If Batch 2 is accepted, the task file should still route the implementation to Task 9 rather than mixing governance and code movement in this task.

- [ ] **Step 2.4: Record the reconciliation outcome**

Write one report only: `docs/reports/quality/backend-core-split-governance-reconciliation-2026-05-19.md`.

The report must state:
- whether Batch 2 can be scheduled
- whether #83 evidence-package output is complete, incomplete, or still pending
- whether issue15 remains blocked by `BLOCKED_BY_TODO: shared evidence package.`
- whether issue15 needs body changes before publication
- the exact `3.2` disposition from `tasks.md`
- whether runtime gates `4.3`, `4.4`, and `4.5` are accepted as closed evidence
- why archive is still blocked or newly allowed

Verification:
- `git diff --check -- openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md docs/reports/quality/backend-core-split-governance-reconciliation-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-core-split-governance-reconciliation-2026-05-19.md`
- `openspec validate split-backend-core-modules-with-compatibility-wrappers --strict`

## Task 3: Draft schema dual-directory closure record (completed by Task 3.x)

**Files:**
- Create: `docs/reports/quality/backend-schema-dual-directory-closure-2026-05-19.md`
- Implementation evidence: `docs/reports/quality/backend-schema-shim-closure-implementation-2026-05-20.md`

- [x] **Step 3.1: Record current directories and imports**

Collect current consumers of:
- `web/backend/app/schema/`
- `web/backend/app/schemas/`
- `from app.schema`
- `from app.schemas`

- [x] **Step 3.2: Decide canonical contract direction**

Decision recorded and implemented: `schemas/` remains canonical for validation models; `schema/` remains a thin compatibility shim. Do not delete the shim until external/generated-code consumers are audited.

- [x] **Step 3.3: Record migration and rollback criteria**

Include:
- import migration path
- retained wrapper path, if any
- package coverage
- OpenAPI side effects, if any
- tests to run
- rollback path

Completion status: `sequence-backend-architecture-unblocks` Task 3.x migrated the three direct legacy consumers, added canonical exports, kept compatibility exports, and verified `test_validation_models.py` `60 passed` plus import smoke for both canonical and compatibility paths.

Verification:
- `git diff --check -- docs/reports/quality/backend-schema-dual-directory-closure-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-schema-dual-directory-closure-2026-05-19.md`

## Task 4: Produce static API flat-package closure records with companion-file coverage

**Files:**
- Create: `docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md`

- [ ] **Step 4.1: Run static import and registration checks first**

For each of the six domains:
- `algorithms`
- `backup_recovery_secure`
- `indicators`
- `signal_monitoring`
- `stock_search`
- `system`

Record:
- whether the flat file is imported
- whether package routes cover the same surface
- whether `router_registry` or `VERSION_MAPPING` references the flat file
- whether frontend/tests/scripts reference the flat path
- whether companion files such as `_responses.py`, `_models.py`, or `_helpers.py` are part of the current implementation pattern
- whether each companion import is package-relative and compatible with `app.main` import collection

- [ ] **Step 4.2: Classify the closure state**

Classify each domain as:
- `active and documented`
- `runtime-only hidden from schema`
- `retired`
- `unknown pending runtime diff`

- [ ] **Step 4.3: Defer runtime route/OpenAPI diff until Task 1 is clean**

If `app.main` still cannot import, record route table and OpenAPI diff as pending. Do not invent runtime evidence. If only implementation-worktree evidence is available, cite it as external evidence and mark the closure record as `static-only pending runtime refresh`. As of the 2026-05-20 runtime-unblock report, the import chain is healthy and route/OpenAPI refresh can proceed from the verified checkout.

Verification:
- `git diff --check -- docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md`

## Task 5: Draft service lifecycle routing matrix

**Files:**
- Create: `docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md`

- [ ] **Step 5.1: Decide canonical seam per service**

For each service candidate, record:
- current implementation path
- current consumers
- whether it is canonical seam, migration shim, or pass-through locator
- whether deleting the module would remove complexity or scatter it

Minimum candidates:
- `IntegratedServices`
- `DataApiService`
- `MarketDataService`
- risk management services
- `spec_from_file_location` service shims
- `realtime_mtm`, as a separate lifecycle proposal/design-gate candidate rather than a generic service batch
- `adapter_loader`, as blocked by the Core split compatibility matrix unless Task 2 says otherwise

- [ ] **Step 5.2: Analyze import direction problems**

The lifecycle routing matrix must explicitly cover API-layer implementations being loaded by service-layer shims through `spec_from_file_location`. It must not treat `realtime_mtm` or `adapter_loader` as normal stateless-service candidates without a separate gate.

- [ ] **Step 5.3: Route lifecycle DI by dependency order**

Separate:
- adapter lifecycle first (`GH #78`; multiple low-risk adapter batches already completed)
- service lifecycle second (`GH #79`; `TradingViewWidgetService` pilot completed, remaining services still require candidate classification)
- core infrastructure singleton last

- [ ] **Step 5.4: Regenerate the service singleton / getter inventory**

Regenerate the current inventory for `web/backend/app/services` before choosing any next `#79` candidate.

Classify every candidate into one of these buckets:
- false positive / not a singleton candidate
- factory or helper
- external-client wrapper
- DB/session-backed service
- cache/task-running service
- intentionally retained process-level singleton
- stateless pilot candidate

Record excluded candidates and why they are excluded. Do not select a heavy service directly from the minimum-candidate list without this classification.

- [ ] **Step 5.5: Select the next service lifecycle pilot only after classification**

The routing matrix must state:
- which candidate, if any, is the next low-risk stateless pilot
- why the candidate follows the `TradingViewWidgetService` pilot pattern
- which candidates require a separate proposal or design gate
- which candidates are blocked by Core split compatibility work
- which candidates are intentionally retained

This task must not depend on Task 10 error-contract completion verification.

Verification:
- `git diff --check -- docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md`

## Task 6: Run runtime route/OpenAPI closure diff after Task 1 is clean

**Files:**
- Update: `docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md`
- Create: `docs/reports/quality/backend-route-openapi-diff-2026-05-19.md`

- [ ] **Step 6.1: Confirm `app.main` imports successfully**

```bash
env PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"
```

Expected:
- app import succeeds before runtime diff is attempted.

- [ ] **Step 6.2: Capture route table and OpenAPI diff**

Record:
- route table path count
- `app.openapi()` path count
- duplicate operationId warnings
- added/removed paths
- `include_in_schema=False` runtime-only routes
- whether runtime-only compatibility routes are intentionally hidden from schema
- snapshot metadata: `generated_at`, `git_head`, `current_head_checked_at_review`, and `stale_if_head_mismatch`

- [ ] **Step 6.3: Attach runtime evidence to each closure domain**

Update the six-domain closure report with runtime evidence only where it is actually measured. Compare against the Core split line runtime evidence (`paths=499`, `operations=535`, `duplicate_operation_ids=0`) only as a dated snapshot, not as a permanent route-count baseline.

Verification:
- `git diff --check -- docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md docs/reports/quality/backend-route-openapi-diff-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md docs/reports/quality/backend-route-openapi-diff-2026-05-19.md`

## Task 7: Draft CSRF composition-root decision pack

**Files:**
- Create: `docs/reports/quality/backend-csrf-composition-root-decision-2026-05-19.md`

- [ ] **Step 7.1: Confirm `main.py` and `app_factory.py` roles**

Record `main.py` as the production ASGI/runtime entry. Then classify `app_factory.py` as one of:
- secondary composition-root candidate
- test/bootstrap compatibility factory
- historical residue pending deletion or wrapper decision

- [ ] **Step 7.2: Decide CSRF token manager ownership**

Record whether `CSRFTokenManager`, `csrf_manager`, and CSRF middleware should live in:
- a shared security module
- the runtime root only
- the test factory only

- [ ] **Step 7.3: Decide test factory long-term model**

The decision pack must state whether tests should:
- import the canonical `main.py` app and use `dependency_overrides`, or
- keep an independent factory with no duplicated CSRF policy

Verification:
- `git diff --check -- docs/reports/quality/backend-csrf-composition-root-decision-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-csrf-composition-root-decision-2026-05-19.md`

## Task 8: Record external miniQMT evidence boundary and freshness metadata

**Files:**
- Create: `docs/reports/quality/backend-external-evidence-alignment-2026-05-19.md`
- Modify: `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` only for evidence indexing after validation
- Create or update: `docs/reports/quality/codebase-map-freshness-2026-05-19.md`

- [x] **Step 8.1: Read the miniQMT evidence handoff as external evidence**

Read and cite:
- `docs/reports/evidence/miniqmt/2026-05-19-mystocks-controlled-evidence-summary-for-review.md`
- `docs/reports/evidence/miniqmt/2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json`

Treat the summary as review input until this plan and the summary are approved. Do not convert it into operational truth or backend execution authority.

Record that:
- MyStocks raw/candidate `mystocks_dry_run` evidence is complete, and miniQMT validator / preview / apply for that raw/candidate identity are complete
- validated-forward evidence was generated locally for `payload_hash=268b62bb0fb0891833ef1998d4993d6531cc6a9d84aaecb911da0cd559d2357e`
- evidence SHA-256 is `4fe9be93061aeec011c16aeabcbb14eef17a35bf6a5ba578258c2e5388ccb24c`
- miniQMT validator / preview / apply have passed for the validated-forward evidence artifact
- miniQMT manual promote to `validated` and `authoritative-ready` is complete; final `authoritative` approval remains a manual owner/operator gate
- the evidence does not authorize backend promotion, source cutover, ClickHouse writes, or production application

- [x] **Step 8.2: Capture provenance and freshness fields**

For provenance, record:
- `source_summary_path`
- `source_summary_status`, for example `For review` until accepted
- `forward_evidence_path`: `docs/reports/evidence/miniqmt/2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json`
- `forward_evidence_run_at` from the evidence JSON `run_at`
- `forward_evidence_sha256`
- `git_head`, only if the source artifact is tracked at review time; otherwise record `untracked_review_input`
- `current_head_checked_at_review`
- `stale_if_head_mismatch`
- manual-gate owner and next gate

- [x] **Step 8.3: Add the external evidence to the codebase map index**

Add both artifacts to the Evidence Artifact Index:
- `docs/reports/evidence/miniqmt/2026-05-19-mystocks-controlled-evidence-summary-for-review.md` as external review input
- `docs/reports/evidence/miniqmt/2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json` as external evidence artifact

Keep both marked as non-backend-blocking, non-source-cutover, and non-ClickHouse-write-authorizing unless a future approved plan explicitly creates a backend dependency on miniQMT receive-side results.

Verification:
- `git diff --check -- docs/reports/quality/backend-external-evidence-alignment-2026-05-19.md .planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md docs/reports/quality/codebase-map-freshness-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-external-evidence-alignment-2026-05-19.md .planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md docs/reports/quality/codebase-map-freshness-2026-05-19.md`

## Task 9: Prepare a separate Batch 2 candidate packet after governance reconciliation is accepted

**Files:**
- Create: `docs/reports/quality/backend-core-split-batch2-candidate-packet-2026-05-19.md`
- Modify: `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` only for evidence indexing after validation

- [ ] **Step 9.1: Confirm Task 2 accepted Batch 2 scheduling**

Do not start this task unless `docs/reports/quality/backend-core-split-governance-reconciliation-2026-05-19.md` explicitly says Batch 2 can be scheduled.

If Task 2 says Batch 2 remains blocked, stop here and keep Task 9 unchecked.

- [ ] **Step 9.2: Select a deep-enough low-risk helper**

Choose one helper that:
- has at least two current consumers, so the wrapper earns compatibility value
- does not touch DB, network, router, OpenAPI, security, socketio, cache, or logger
- has a small public interface that can be covered by import compatibility tests

Record the rejected candidates and the selected module in the candidate packet.

- [ ] **Step 9.3: Run impact checks on the selected helper only**

Run GitNexus impact analysis for the selected helper's exported symbols. If risk is HIGH or CRITICAL, stop and return to review.

- [ ] **Step 9.4: Draft the separate Batch 2 implementation packet**

The packet must state:
- the chosen helper module
- the canonical package target
- the wrapper shape that Batch 2 would use
- the tests that would need to exist in the separate Batch 2 implementation plan
- the rollback condition
- why this work is eligible for a separate Batch 2 implementation plan only after Task 2 approval

- [ ] **Step 9.5: Record the candidate packet outcome**

Write one report only: `docs/reports/quality/backend-core-split-batch2-candidate-packet-2026-05-19.md`.

The report must not contain executable implementation steps, placeholder import commands, or code blocks that look like a ready-to-run batch. Its purpose is to prepare the separate concrete Batch 2 implementation plan after module selection.

Verification:
- `git diff --check -- docs/reports/quality/backend-core-split-batch2-candidate-packet-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-core-split-batch2-candidate-packet-2026-05-19.md`

## Task 10: Verify P3-C5 error-contract completion independently

**Files:**
- Create: `docs/reports/quality/backend-error-contract-completion-verification-2026-05-19.md`
- Modify: `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` only for evidence indexing after validation

- [ ] **Step 10.1: Read completion evidence and mark old live-count language superseded**

Read and cite:
- `docs/reports/P3-C5-exception-consolidation-completion-report.md`
- `docs/reports/quality/backend-lifecycle-di-workline-summary-2026-05-19.md`

The verification report must state that, for `#77` / P3-C5, `docs/reports/P3-C5-exception-consolidation-completion-report.md` supersedes the older live-count / AFK migration wording in the lifecycle summary.

- [ ] **Step 10.2: Regenerate the fixed-field current-HEAD snapshot if needed**

If current HEAD differs from the completion report commit range, regenerate this fixed-field snapshot and explain any delta:

```text
Live count at HEAD <sha>:
- raise HTTPException: <count>
- except HTTPException: <count>
- response_model=APIResponse: <count>
- return APIResponse(...): <count>
- HTTPException import lines: <count>
```

- [ ] **Step 10.3: Classify any non-zero bucket without reopening P3-C5 by default**

Classify any non-zero bucket as:
- out-of-scope retained framework exception
- completion-report contradiction requiring review
- UnifiedResponse guard / historical-route follow-up

The report must not reopen the main P3-C5 exception migration unless the current HEAD snapshot contradicts the completion report.

- [ ] **Step 10.4: Keep Task 10 independent from #79 service lifecycle routing**

Task 10 must not block Task 5 service candidate classification or the next `#79` stateless pilot. It only verifies the error-contract completion evidence and records follow-up lanes.

Verification:
- `git diff --check -- docs/reports/quality/backend-error-contract-completion-verification-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-error-contract-completion-verification-2026-05-19.md`

## What Is Intentionally Not In This Plan

- One-shot deletion of `IntegratedServices`
- Bulk deletion of scanner-reported orphans
- Publishing issue 15
- Replacing issue15 `BLOCKED_BY_TODO: shared evidence package.` before the #83 evidence result is accepted
- Creating a new OpenSpec proposal from the codebase map
- Using issue #83 to perform backend implementation or fix `ContractDriftIncidentListResponse`
- Starting Core helper Batch 2 before Task 2 governance reconciliation is accepted
- Executing Core helper Batch 2 implementation from Task 9 without a separate concrete implementation plan
- Treating miniQMT receive/preview/apply as backend promotion or source cutover approval
- Reopening the main P3-C5 exception migration without a current-HEAD contradiction to the completion report
- Folding `realtime_mtm` or `adapter_loader` into generic service/adapter batches
- Treating F821 bulk repair as architecture work
- Splitting `main.py` by file size alone
- Merging `schema/` and `schemas/` without a decision record
- Running runtime route/OpenAPI diff before `app.main` imports cleanly

## Review Checklist

Before approving this plan, verify that:

1. Wave 1 handles the current runtime blocker and does not rely on stale `ContractDriftIncidentListResponse` evidence.
2. Task 1 recognizes issue `#83` as already `ready-for-agent` but only for evidence-package work.
3. Task 2 decides Core split governance before Task 9 can prepare any Batch 2 candidate packet.
4. Wave 2 keeps evidence records and decision packs separate from code movement.
5. Task 5 defines canonical service seams, regenerates the `web/backend/app/services` candidate inventory, and keeps #78/#79 routing separate.
6. Task 10 verifies P3-C5 completion evidence independently and does not gate Task 5 service classification.
7. Task 8 keeps miniQMT evidence external and does not convert it into backend promotion or source-cutover approval.
8. Freshness metadata is updated continuously after each task.
9. The plan does not authorize code changes, label changes, issue creation, or new OpenSpec proposals by itself.

Recommended execution after approval:

1. Start Continuous Task C1 immediately as metadata hygiene.
2. Treat runtime smoke reconciliation as complete via `sequence-backend-architecture-unblocks` Task 2.x, then continue with schema and route/OpenAPI evidence refresh.
3. Execute Task 2 before any new Core helper split batch.
4. Execute Tasks 3, 4, 5, 8, and 10 as Wave 2 evidence / decision records.
5. Execute Tasks 6 and 7 as Wave 3 after Task 1 proves `app.main` imports successfully.
6. Execute Task 9 only if Task 2 explicitly accepts Batch 2 candidate selection; create a separate concrete implementation plan afterward.
