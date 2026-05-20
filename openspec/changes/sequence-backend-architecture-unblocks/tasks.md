# Tasks: Sequence backend architecture unblocks behind explicit OpenSpec gates

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 1. Pre-Implementation Evidence

- [x] 1.1 Reconfirm the current runtime blocker in the `web/backend/app/api/data_lineage.py` import chain with `PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"` and record the exact failing file and exception.
- [x] 1.2 Reconfirm the current `test_health_route_conflicts.py --collect-only -q --no-cov` collection result and record whether it fails, collects zero tests, or collects tests successfully.
- [x] 1.3 Reconfirm current `app.schema` consumers and compare them with `app.schemas` exports before any deletion is considered; include `from app.schema`, `import app.schema`, and dynamic import patterns in the scan.
- [x] 1.4 Reconfirm the current singleton inventory and the absence of a low-risk pilot before any new lifecycle batch is chosen.

## 2. Runtime Unblock

- [x] 2.1 Implementation lane note: source edits were performed only after explicit continuation approval; GitNexus impact checks were run for each edited runtime-unblock surface and returned LOW.
- [x] 2.2 Restore the failing runtime import chain. Initial `asynccontextmanager` repair exposed additional import-time split-helper blockers, which were repaired as one runtime-unblock batch and recorded in `docs/reports/quality/backend-sequence-runtime-unblock-implementation-2026-05-20.md`.
- [x] 2.3 Verify `PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"` succeeds after the import fixes. Result: `routes 548`.
- [x] 2.4 Verify `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov` succeeds after the import fixes. Follow-up full file result: `112 passed in 63.69s`.
- [x] 2.5 Capture minimal runtime evidence needed to unblock the next phase. Snapshot: `routes=548`, `paths=500`, `operation_ids=536`, `duplicate_operation_ids=0`, `warnings=121`.

## 3. Schema Shim Closure

- [x] 3.1 Record the exact `app.schema` consumers and the matching canonical `app.schemas` export path required for each model. Fresh scan after migration: `LEGACY_CONSUMERS=0`; pre-migration consumers are recorded in `docs/reports/quality/backend-schema-shim-closure-implementation-2026-05-20.md`.
- [x] 3.2 Add canonical exports under `web/backend/app/schemas/` for the legacy validation models before consumer migration. Canonical implementation now lives at `web/backend/app/schemas/validation_models.py`; package exports live at `web/backend/app/schemas/__init__.py`.
- [x] 3.3 Migrate the three legacy consumers to `app.schemas` / `app.schemas.validation_models`.
- [x] 3.4 Run the targeted import and validation tests that prove the compatibility surface still works. Results: schema ruff passed; `test_validation_models.py` `60 passed`; import smoke confirms `app.schemas`, `app.schemas.validation_models`, `app.schema`, and `app.schema.validation_models` all export the validation models; `app.main` routes=`548`.
- [x] 3.5 Decide whether `web/backend/app/schema/` remains a shim or can be retired. Decision: keep `web/backend/app/schema/` as a thin compatibility shim; do not delete until external/generated-code consumers are audited.

## 4. Codebase Map Consistency

- [x] 4.1 Update `docs/reports/quality/codebase-map-execution-plan-positioning-and-rollout-2026-05-20.md` or the active codebase-map review file so historical counts and current-head counts are not conflated. Updated the active codebase-map review and master execution plan to separate historical HTTPException snapshots from the current P3-C5 zero evidence and Task 3.x schema implementation evidence.
- [x] 4.2 Replace stale `GH #77` / P1.4 language in `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` with the current-head zero snapshot plus completion-report supersession language. Current GH #77 state is `CLOSED`; current working-tree scan at HEAD `7b097fffd` reports all fixed-field error-contract buckets at `0`.
- [x] 4.3 Ensure all current evidence entries include whether they are current-head, commit-scoped, or stale-aware. Evidence Artifact Index now distinguishes stale historical artifacts, current-head Task 2.x/3.x evidence, commit-scoped Core helper evidence, and current-head P3-C5 verification.

## 5. Runtime Evidence Refresh

- [x] 5.1 Re-run route table capture after the import chain is healthy. Artifact: `.planning/codebase/generated/backend-route-table-2026-05-20.json`; summary `total_routes=548`, `include_in_schema_true=536`, `include_in_schema_false=12`; one duplicate path/method pair excluding `HEAD`: `GET /metrics`.
- [x] 5.2 Re-run `app.openapi()` capture and record the current snapshot fields. Artifact: `.planning/codebase/generated/route-openapi-snapshot-2026-05-20.json`; summary `paths=500`, operations `536`, duplicate operationIds `0`, warnings `0`, component schemas `294`.
- [x] 5.3 Refresh the probe consumer matrix only after the runtime smoke is trustworthy again. Artifact: `.planning/codebase/generated/probe-consumer-matrix-2026-05-20.json`; scanned files `5782`, hit files `188`, hit lines `611`; category counts health `278`, openapi `276`, status `50`, strategy_compat `8`.

## 6. Singleton and Service Seam Proposal Path

- [x] 6.1 Reclassify the service inventory as interface/test-double candidates versus truly stateful services. Evidence artifact: `.planning/codebase/generated/service-singleton-inventory-2026-05-20.json`; heuristic scan buckets external-client wrapper `69`, DB/session-backed `24`, cache/task-running `17`, interface/test-double candidate needing review `28`, separate design gate `2`.
- [x] 6.2 Draft a separate proposal path for any service-seam canonicalization that needs architecture approval. Report: `docs/reports/quality/backend-service-seam-proposal-path-2026-05-20.md`; proposal candidate remains `define-backend-service-seams-and-singleton-pilots`.
- [x] 6.3 Do not schedule a new service lifecycle implementation batch until the proposal path is approved. Current disposition: proposal-only, no implementation batch scheduled from this evidence.

## 7. Verification

- [x] 7.1 Run `git diff --check` on every touched file. Path-limited `git diff --check` returned no output; generated JSON artifacts parsed successfully; added-file whitespace scan found `0` trailing-whitespace problems.
- [x] 7.2 Run `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json` on every touched markdown artifact. Result: `checked_files=10`, `errors=0`.
- [x] 7.3 Run `openspec validate sequence-backend-architecture-unblocks --strict`. Result: change is valid; PostHog `ECONNREFUSED 0.0.0.0:443` remains telemetry noise after validation success.

## 8. Closure

- [x] 8.1 Record the runtime unblock result as a report. Report: `docs/reports/quality/backend-sequence-runtime-unblock-implementation-2026-05-20.md`.
- [x] 8.2 Record the schema-shim decision as a report. Report: `docs/reports/quality/backend-schema-shim-closure-implementation-2026-05-20.md`.
- [x] 8.3 Record the service-seam proposal split as a report if it is needed. Report: `docs/reports/quality/backend-service-seam-proposal-path-2026-05-20.md`.
- [x] 8.4 Leave implementation claims out of the plan until the proposal is approved and the runtime evidence is fresh. Current disposition: runtime evidence is fresh for Task 5.x, but service seam, endpoint governance, shim retirement, and broad refactor implementation remain unapproved future lanes.
- [x] 8.5 Absorb paired report reviews for Task 5.x and Task 6.x. Reports now name the OpenSpec directory explicitly, explain `endpoint_modules=98`, map `strategy_compat=8` to `category_counts.strategy_compat`, correct the `separate_design_gate` members, and explain why the 2026-05-20 `candidate_files=140` scan is not directly comparable to the 2026-05-19 `111` count.
- [x] 8.6 Record path-limited commit readiness. Report: `docs/reports/quality/backend-sequence-unblocks-commit-readiness-2026-05-20.md`; current worktree has `1493` dirty entries, this line has `35` relevant entries, and the recommended next step is a human choice between a two-commit split, a single explicit-path commit, or more review.
- [x] 8.7 Record the combined commit attempt blocker. Report: `docs/reports/quality/backend-sequence-unblocks-commit-blocked-2026-05-20.md`; the single explicit-path commit was attempted and rejected by the `Backend Singleton None Guard` first, then by the `UnifiedResponse Contract Guard` with `checked_files=18`, `checked_routes=72`, and `errors=34`; no commit was created.
