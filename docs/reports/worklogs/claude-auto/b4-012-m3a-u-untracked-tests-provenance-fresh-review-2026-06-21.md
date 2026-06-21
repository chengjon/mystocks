# B4.012-M3a-U Untracked Tests Provenance Fresh Review

Date: 2026-06-21
Repository: `/opt/claude/mystocks_spec`
Baseline HEAD: `3c5afab6f585671896fc5b36ce9fb24b2fe4bd91`
Mode: no-source provenance reactivation review

## Scope

This review refreshes the B4.012-M3a-U untracked tests provenance parent after B4.013 closeout and the B4.012-M3a B/C/D/E parent reactivations.

The immediate target is only:

- `b4-012-m3a-u-untracked-tests-provenance-review`

This package does not authorize preserving, deleting, moving, ignoring, staging, or editing any untracked file. It only records the current untracked test surface and restores the parent decision point.

## Current Gate Truth

- `b4-012-m3a-tests-residual-domain-audit` is `decision-prepared`.
- `b4-012-m3a-b-api-backend-contract-tests-split` is `decision-prepared`.
- `b4-012-m3a-c-adapter-data-source-tests-split` is `decision-prepared`.
- `b4-012-m3a-d-e2e-frontend-tests-split` is `decision-prepared`.
- `b4-012-m3a-d1-e2e-browser-smoke-authorization` is `authorization-prepared`, but implementation remains unapproved.
- `b4-012-m3a-e-performance-runtime-security-tests-split` is `decision-prepared`.
- `b4-012-m3a-u-untracked-tests-provenance-review` is still `blocked` only because it was paused by the B4.013 runtime-first reset.

The U parent may return to `decision-prepared` because B4.013 no longer blocks residual test-family decision work.

## Fresh Untracked Surface

Current status summary:

| Group | Count | Notes |
| --- | ---: | --- |
| All untracked status entries | 127 | Whole-worktree untracked surface; most are outside this test provenance review. |
| Test / test-helper untracked candidates | 32 | Current U review surface. |
| Fixture/data bundle | 1 status row | Directory row expands to many data/provenance files; high-review data ownership required. |
| Contract/integration candidate | 1 | Contract E2E provenance; route to contract/API ownership before preserve/delete. |
| Performance/deployment candidates | 7 | Route to future E/U performance provenance package. |
| Data-source candidate | 1 | Route to C-family/OpenStock-boundary review before preservation. |
| Governance script candidates | 3 | Route to future E/U governance-script provenance package. |
| Backend runtime regression candidate | 1 | Route to B-family backend/runtime provenance review. |
| Frontend source-tree/unit candidates | 18 | Route to D/U frontend provenance review; not accepted as active tests. |

## Current Candidate Inventory

High-review fixture/data bundle:

- `tests/fixtures/miniqmt_promotion_bundle/`

Contract / integration provenance:

- `tests/integration/contract/test_contract_validation_e2e.py`

Performance / deployment provenance:

- `tests/performance/test_benchmark_workload_classes.py`
- `tests/performance/test_collect_api_performance_baseline.py`
- `tests/performance/test_collect_frontend_runtime_gate.py`
- `tests/performance/test_validate_api_performance_drift.py`
- `tests/performance/test_validate_backend_runtime_dependencies.py`
- `tests/performance/test_validate_container_deployment_contract.py`
- `tests/performance/test_validate_deployment_env_contract.py`

Data-source / provider-boundary provenance:

- `tests/unit/data_source/`

Governance script provenance:

- `tests/unit/scripts/test_collect_tech_debt_baseline.py`
- `tests/unit/scripts/test_gitnexus_workflow_gate.py`
- `tests/unit/scripts/test_graphiti_post_commit_hook_integration.py`

Backend runtime regression provenance:

- `web/backend/tests/test_market_v2_lhb_runtime_regression.py`

Frontend source-tree / unit provenance:

- `web/frontend/src/views/__tests__/`
- `web/frontend/src/views/advanced-analysis/__tests__/`
- `web/frontend/src/views/announcement/__tests__/AnnouncementMonitor.spec.ts`
- `web/frontend/src/views/artdeco-pages/__tests__/`
- `web/frontend/src/views/artdeco-pages/analysis-tabs/__tests__/`
- `web/frontend/src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoMarketAnalysis.spec.ts`
- `web/frontend/src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoMarketOverview.spec.ts`
- `web/frontend/src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoRealtimeMonitor.spec.ts`
- `web/frontend/src/views/data/__tests__/FundFlow.spec.ts`
- `web/frontend/src/views/market/__tests__/LHB.spec.ts`
- `web/frontend/src/views/strategy/__tests__/`
- `web/frontend/src/views/technical/__tests__/`
- `web/frontend/src/views/trading-decision/__tests__/`
- `web/frontend/src/views/trading/__tests__/`
- `web/frontend/src/views/watchlist/__tests__/Screener.spec.ts`
- `web/frontend/src/views/watchlist/__tests__/Signals.spec.ts`
- `web/frontend/tests/unit/views/data-concept-refresh-fallback.spec.ts`
- `web/frontend/tests/unit/views/data-industry-refresh-fallback.spec.ts`

## Boundary Decisions

No untracked test file is accepted by this review.

Routing stays fixed:

- Fixture/data bundle requires a separate fixture ownership and data-licensing provenance decision.
- Contract/integration candidate routes to B/contract ownership before preservation.
- Performance/deployment candidates route to E/U performance provenance.
- Data-source candidate routes to C-family provenance with the OpenStock boundary retained.
- Backend runtime regression candidate routes to B-family backend/runtime provenance.
- Frontend source-tree/unit candidates route to D/U frontend provenance before any active-test acceptance.

OpenStock boundary remains fixed: OpenStock owns provider/data-source runtime. `mystocks_spec` only consumes/adapts provider data and must not reintroduce provider development through untracked tests.

## Risk Notes

- Untracked tests can silently expand repository behavior if staged without provenance.
- The miniqmt fixture bundle contains data/provenance artifacts, not just tests. It must not be preserved or deleted without ownership and licensing review.
- Frontend source-tree tests under `web/frontend/src/views/**/__tests__` are not active route/test truth until explicitly accepted.
- Data-source tests can accidentally reintroduce provider implementation responsibility into MyStocks.
- Backend/runtime/provenance tests may depend on local services, generated artifacts, or unresolved environment state.

## Recommended Next Queue

1. `B4.012-M3a-UF fixture provenance decision`
   - Candidate: `tests/fixtures/miniqmt_promotion_bundle/`
   - Decision: preserve/delete/ignore after fixture ownership, data licensing, and miniqmt promotion context review.

2. `B4.012-M3a-UD data-source untracked provenance`
   - Candidate: `tests/unit/data_source/`
   - Decision: preserve only if it validates MyStocks consumer/adaptation behavior, not provider runtime.

3. `B4.012-M3a-UE performance/deployment untracked provenance`
   - Candidate: untracked `tests/performance/**` and `tests/unit/scripts/**` governance candidates.
   - Decision: split preserve/delete/ignore from E tracked implementation packages.

4. `B4.012-M3a-UFRT frontend/runtime untracked provenance`
   - Candidate: frontend source-tree/unit tests and backend runtime regression candidate.
   - Decision: separate active-route frontend acceptance from backend runtime regression acceptance.

## Verification Plan

Before commit:

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus staged verification and staged change detection
- OPENDOG verification

After commit:

- GitNexus analyze
- staged index empty
- `b4-012-m3a-u-untracked-tests-provenance-review` is `decision-prepared`
- no untracked test files are staged, deleted, moved, or accepted
