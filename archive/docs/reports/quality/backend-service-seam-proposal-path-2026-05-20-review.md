# Review: backend-service-seam-proposal-path-2026-05-20.md

**Type**: md / proposal | **Perspective**: completeness, consistency, feasibility | **Date**: 2026-05-20

> **历史文档说明**:
> 本文件是审查快照，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

Governance record for `sequence-backend-architecture-unblocks` Task 6.x defining the service seam proposal path. All numeric claims match the companion JSON artifact. The routing strategy correctly abandons the failed "clean pilot" search in favor of interface/test-double extraction. Two factual issues: the referenced OpenSpec change directory does not exist, and the `separate_design_gate` bucket contains `StockSearchService` and `TechnicalPatternDetectionService` — not `realtime_mtm` and `adapter_loader` as stated.

## Verified

- **C1 Required sections**: Status, Current Inventory Evidence, Dirty Worktree Guard, Routing Decision, Bucket Policy, Proposal Path, Next Gate — all present
- **C4 Acceptance criteria**: Next Gate is explicit — "no new service implementation batch is scheduled from this evidence alone"
- **A9 Named entities — artifact**: `.planning/codebase/generated/service-singleton-inventory-2026-05-20.json` exists; `service_python_files=152`, `candidate_files=140` — match document
- **A9 Named entities — bucket counts**: JSON reports `external_client_wrapper=69`, `db_session_backed=24`, `cache_or_task_running=17`, `interface_test_double_candidate_needs_review=28`, `no_singleton_pattern_detected=12`, `separate_design_gate=2` — all match document table
- **A9 Named entities — pattern totals**: JSON reports `getter_function=281`, `async_getter_function=96`, `module_instance=71`, `private_instance=111`, `lru_cache=4` — all match document table
- **A9 Named entities — realtime_mtm**: `web/backend/app/api/realtime_mtm_adapter.py` and `web/backend/app/api/realtime_mtm_init.py` exist — the module exists in the codebase
- **A9 Named entities — adapter_loader**: `web/backend/app/core/adapter_loader.py` exists — the module exists in the codebase
- **C3 Implicit assumptions**: Dirty Worktree Guard section correctly identifies 18 dirty service files as a blocking factor for pilot selection
- **F1 Technical risk**: Correctly identifies that no clean pilot exists and proposes the interface/test-double strategy as the alternative
- **F5 Rollback plan**: Proposal Path section defines non-goals that constrain rollback scope
- **N1 Terminology**: "bucket", "singleton-like pattern", "interface/test-double candidate" used consistently
- **L3 cross-doc claim**: Document references "The 2026-05-19 singleton lifecycle routing matrix found no clean low-risk stateless pilot" — verified against `backend-singleton-lifecycle-routing-matrix-2026-05-19.md` which states "Low-risk stateless pilot: None selected" — claim is accurate

## Issues

- [ ] **[MED]** Referenced change lane `sequence-backend-architecture-unblocks` does not exist as an OpenSpec change directory — Status:line 12
      Evidence: `glob openspec/changes/sequence-*/**` returned no files. Same finding as the route-refresh report. The OpenSpec branch is cited as the change lane but has not been created on disk.

- [ ] **[MED]** `separate_design_gate` examples are wrong — the bucket contains `StockSearchService` and `TechnicalPatternDetectionService`, not `realtime_mtm` and `adapter_loader` — Bucket Policy section:line 78
      Evidence: JSON artifact at lines 2250 and 2447 shows the two `separate_design_gate` entries are `stock_search_service/stock_search_service.py` (class `StockSearchService`) and `technical_pattern_detection_service.py` (class `TechnicalPatternDetectionService`). The document's Bucket Policy section names `realtime_mtm` and `adapter_loader` as examples — these exist in the codebase but are classified in other buckets (they are API-layer and Core-layer respectively, not services/). The examples should match the actual bucket contents.

- [ ] **[LOW]** The 2026-05-19 routing matrix reported `111 candidate files with singleton/getter/spec-loading patterns`; this report reports `140 candidate files` — Current Inventory Evidence table
      Evidence: The 2026-05-19 matrix (`backend-singleton-lifecycle-routing-matrix-2026-05-19.md`) reported "111 files matched singleton/getter/spec-loading patterns". This 2026-05-20 report reports "140 candidate files with singleton-like or lifecycle-relevant patterns". The increase from 111 to 140 is not explained. It may be due to a broader heuristic scan (the 2026-05-20 scan uses `140` candidates vs `152` total, while the 2026-05-19 scan used `111` from `152`), but the discrepancy should be noted.

## Suggestions

- Fix the `separate_design_gate` bucket examples to match the actual JSON contents: replace "realtime_mtm" and "adapter_loader" with "StockSearchService" and "TechnicalPatternDetectionService". The `realtime_mtm` and `adapter_loader` modules exist in the codebase but are not in the `services/` scan scope — they are in `app/api/` and `app/core/` respectively.
- Add a one-line note explaining the 111 → 140 candidate count increase between the 2026-05-19 matrix and this report (e.g., "Broader heuristic scan captured additional lifecycle-relevant patterns beyond the initial singleton/getter/spec classification").
- Add a note next to `Change lane` indicating the OpenSpec branch is proposed but not yet on disk.

## Verdict
APPROVE_WITH_NOTES — Inventory data is verified against the JSON artifact. Strategy is sound. One medium factual error: the `separate_design_gate` bucket examples name modules from other directories instead of the actual bucket contents. Should be corrected to avoid misrouting future implementation work.
