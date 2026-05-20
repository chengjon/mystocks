# Review: canonicalize-backend-route-unified-response-contracts (OpenSpec change)

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

**Type**: md / spec+proposal | **Perspective**: completeness, consistency, feasibility | **Date**: 2026-05-20

## Summary

OpenSpec change proposing to canonicalize 4 backend route modules to satisfy `UnifiedResponse Contract Guard`. The proposal is well-scoped: it correctly separates route-contract migration from runtime unblock, and the evidence report proves the worktree has a working `app.main` import. All 4 target files exist and their current `response_model` patterns confirm the debt described. One medium finding: `signal_history_response.py` already uses typed `response_model` declarations (not `UnifiedResponse`), which partially contradicts the "missing or non-canonical" characterization.

## Verified

- **C1 Required sections**: All 4 documents follow expected structure — proposal (Why/What/Impact/Boundaries), tasks (Preflight/Migration/Verification/Closure), spec (Scenarios), evidence report (Scope/Fixes/Verification/Gate Status)
- **A9 Named entities — target files**: All 4 route files exist: `data_quality.py`, `indicators/indicator_cache.py`, `signal_monitoring/signal_history_response.py`, `technical_analysis.py`
- **A9 Named entities — UnifiedResponse**: `web/backend/app/core/responses.py:35` defines `UnifiedResponse`, line 127 defines `UnifiedPaginatedResponse` — both exist
- **A9 Named entities — guard script**: `scripts/compliance/unified_response_contract_guard.py` exists
- **A9 Named entities — pre-commit hook**: `.pre-commit-config.yaml:328` registers the guard as a local hook — confirmed
- **A9 Named entities — worktree**: `git worktree list` shows `.worktrees/sequence-route-contract-unblock` on branch `sequence-route-contract-unblock` at HEAD `f96ff2dc5` — confirmed
- **A9 Named entities — test files**: `tests/unit/scripts/test_unified_response_contract_guard.py` and `tests/unit/scripts/test_unified_response_contract_guard_integration.py` both exist
- **F2 Dependency availability**: `app.openapi()`, `pytest`, `ruff check`, `openspec validate` — all referenced tools are available
- **C4 Acceptance criteria**: Spec scenarios use GIVEN/WHEN/THEN with verifiable conditions (`errors=0`, route count, duplicate operationId count)
- **F5 Rollback plan**: Tasks 4.2-4.3 define steward tree update and re-evaluation of `sequence-backend-architecture-unblocks` — implicit rollback path through worktree isolation
- **A1 Component boundaries**: Proposal correctly separates this lane from `sequence-backend-architecture-unblocks` — "must not archive" and "must not use `--no-verify`"
- **N5 Style consistency**: All 4 documents use consistent governance boilerplate headers and formatting

## Issues

- [ ] **[MED]** `signal_history_response.py` already has typed `response_model` declarations — `response_model=List[SignalHistoryResponse]`, `response_model=SignalQualityReportResponse`, `response_model=StrategyRealtimeMonitoringResponse` — but they use direct Pydantic models, not `UnifiedResponse[...]` — Proposal "What Changes" and Tasks 2.3
      Evidence: Grep of `signal_history_response.py` shows `response_model` appears 3 times with typed models. The evidence report claims "4 route-contract errors" for this file. The spec requires `UnifiedResponse[...]` or `UnifiedPaginatedResponse[...]` wrappers. The file does have `response_model` declarations but they are not wrapped in `UnifiedResponse` — this is consistent with the proposal's characterization of "non-canonical". However, the proposal's "missing or non-canonical" wording is ambiguous: `data_quality.py` has 9 decorators with zero `response_model` (truly missing), while `signal_history_response.py` has typed models that just lack the `UnifiedResponse` wrapper. These are different migration patterns that should be distinguished in Task 2.

- [ ] **[LOW]** Evidence report lists `indicator_cache.py` at `web/backend/app/api/indicator_cache.py` but actual path is `web/backend/app/api/indicators/indicator_cache.py` — Evidence report: "Runtime Fixes Applied" section
      Evidence: The evidence report's "Runtime Fixes Applied" section lists `web/backend/app/api/indicator_cache.py` but the file actually exists at `web/backend/app/api/indicators/indicator_cache.py` (under the `indicators/` package directory). The proposal and tasks files use the correct full path. Minor path discrepancy in the evidence report.

- [ ] **[LOW]** Evidence report references Base HEAD `93c6f6a05` but worktree HEAD is `f96ff2dc5` — Evidence report header vs `git worktree list`
      Evidence: The evidence report records `Base HEAD: 93c6f6a05` as the starting point. Current `git worktree list` shows the worktree at `f96ff2dc5`. This is expected (commits happened after the base), but the report does not record the current HEAD or the number of commits applied on top.

## Suggestions

- In Tasks section, split Task 2 into two sub-approaches: (a) files with zero `response_model` (`data_quality.py`, `technical_analysis.py`) need new declarations; (b) files with existing typed `response_model` but missing `UnifiedResponse` wrapper (`indicator_cache.py`, `signal_history_response.py`) need wrapper addition. These are different risk profiles — (a) may change OpenAPI schema shape, (b) should be a no-op for payload shape.
- Fix the `indicator_cache.py` path in the evidence report from `web/backend/app/api/indicator_cache.py` to `web/backend/app/api/indicators/indicator_cache.py`.
- Add `current_worktree_head` and `commits_since_base` fields to the evidence report for freshness tracking.

## Verdict
APPROVE_WITH_NOTES — Proposal is well-scoped and correctly separates route-contract migration from runtime unblock. All target files, tools, and guard infrastructure exist. One medium finding: the 4 target files have different migration patterns (truly missing vs non-canonical wrapper) that should be distinguished in the task breakdown. No blockers for approval.
