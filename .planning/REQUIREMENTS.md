# Requirements: MyStocks Codebase Consolidation

> **使用说明**:
> 本文件是项目入口、工作流快照、规划工件或使用说明，不是当前共享规则、当前代码实现或当前运行状态的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码、主线任务系统与验证结果使用。
>
> 文内步骤、范围、状态或说明如未重新复核，应按其所属上下文理解，不得直接当作跨场景通用事实。


**Defined:** 2026-04-06
**Core Value:** Every file has exactly one canonical location, every import resolves cleanly, zero lint errors.

## v1 Requirements

### Lint Baseline

- [x] **LINT-01**: Duplicate adapter layer (`src/interfaces/adapters/`) deleted entirely — full deletion per CONTEXT.md D-01 ✓ Phase 1 (commit 9ac60b838)
- [x] **LINT-02**: Ruff check passes with <900 errors on `src/` and `web/backend/app/` (from ~1,456; target recalibrated per 01-RESEARCH.md measured baseline) ✓ Phase 1 (877 final)
- [x] **LINT-03**: Auto-fixable ruff rules (W293, F841, W291) produce zero violations (F401 and E701 not auto-fixable by ruff 0.9.10) ✓ Phase 1 (206 fixes)
- [ ] **LINT-04**: Frontend case-conflict directories merged into lowercase canonical names

### Dead Code Removal

- [ ] **DEAD-01**: `src/routes/` (19 files) removed — verified zero imports before deletion
- [ ] **DEAD-02**: `src/api/` (5 files) removed — verified zero imports before deletion
- [ ] **DEAD-03**: `src/data_access_pkg/` merged into canonical `src/data_access/`
- [ ] **DEAD-04**: `src/db_manager/` (empty shell) removed
- [ ] **DEAD-05**: `src/database_optimization/` merged into `src/data_access/` (canonical, per ROADMAP.md Global truth sources table)
- [ ] **DEAD-06**: All proposed deletions listed in a review document for user approval before execution

### Structural Consolidation

- [ ] **STRU-01**: Single canonical data access layer in `src/data_access/` — all others removed
- [ ] **STRU-02**: All import paths updated to point to canonical locations
- [ ] **STRU-03**: Frontend has exactly one entry point — verified truth source ( entry point ( `index.html` + Vite config)
- [ ] **STRU-04**: `views/composables/` relocated to `src/composables/`
- [ ] **STRU-05**: `views/converted.archive/` and `views/demo/` removed from source tree

### Naming & Polish

- [ ] **NAME-01**: `src/calcu/` renamed to semantic name or merged into existing module
- [ ] **NAME-02**: All `part1/part2/part3` mechanical splits replaced with semantic names
- [ ] **NAME-03**: All `*_new.py` files merged into canonical version or deleted
- [ ] **NAME-04**: Root-level shim files (`core.py`, `data_access.py`, `monitoring.py`) verified safe, removed or deprecated
- [ ] **NAME-05**: Frontend store domain boundaries clarified — no overlapping concerns (`market.ts` vs `marketData.ts`)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Mock data relocation | Keep as-is — useful for testing, not blocking anything |
| New feature development | This is cleanup only |
| Performance optimization | Out of scope unless caused by duplicate code paths |
| Mobile/responsive adaptation | Desktop-only per project constraints |
| API contract changes | Route consolidation is location only, not signature changes |
| Test framework changes | Fix existing tests, don't add frameworks |
| Backend API directory reorganization | 205-file split into subdirs is a separate initiative |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| LINT-01 | Phase 1 | ✓ Done |
| LINT-02 | Phase 1 | ✓ Done |
| LINT-03 | Phase 1 | ✓ Done |
| LINT-04 | Phase 3 | Pending |
| DEAD-01 | Phase 2 | Pending |
| DEAD-02 | Phase 2 | Pending |
| DEAD-03 | Phase 2 | Pending |
| DEAD-04 | Phase 2 | Pending |
| DEAD-05 | Phase 2 | Pending |
| DEAD-06 | Phase 2 | Pending |
| STRU-01 | Phase 3 | Pending |
| STRU-02 | Phase 3 | Pending |
| STRU-03 | Phase 3 | Pending |
| STRU-04 | Phase 3 | Pending |
| STRU-05 | Phase 3 | Pending |
| NAME-01 | Phase 4 | Pending |
| NAME-02 | Phase 4 | Pending |
| NAME-03 | Phase 4 | Pending |
| NAME-04 | Phase 4 | Pending |
| NAME-05 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0

---
*Requirements defined: 2026-04-06*
*Last updated: 2026-04-06 after initial definition*
