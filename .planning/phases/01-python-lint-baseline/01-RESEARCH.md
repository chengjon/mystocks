# Phase 1: Python Lint Baseline - Research

> **使用说明**:
> 本文件是项目入口、工作流快照、规划工件或使用说明，不是当前共享规则、当前代码实现或当前运行状态的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码、主线任务系统与验证结果使用。
>
> 文内步骤、范围、状态或说明如未重新复核，应按其所属上下文理解，不得直接当作跨场景通用事实。


**Researched:** 2026-04-06
**Status:** Complete

---

## Validation Architecture

### Dimension 1: Tool Compatibility

**Ruff version:** 0.9.10
**Key difference from assumed behavior:**
- `--dry-run` flag does NOT exist (use `--diff` instead)
- Auto-fixable rules marked `[*]` still require `--unsafe-fixes` flag
- F401 and E701 are marked `[ ]` (NOT auto-fixable by ruff at all)

**Fixable classification (ruff 0.9.10):**
| Rule | Count | Marked | Actually fixable? |
|------|-------|--------|-------------------|
| W293 | 95 | `[*]` | Yes, needs `--unsafe-fixes` |
| F841 | 78 | `[*]` | Yes, needs `--unsafe-fixes` |
| W291 | 28 | `[*]` | Yes, needs `--unsafe-fixes` |
| F401 | 21 | `[ ]` | No — ruff cannot auto-remove unused imports |
| E701 | 15 | `[ ]` | No — ruff cannot auto-fix multiple-statements |
| F811 | 17 | `[ ]` | No |
| E722 | 13 | `[ ]` | No |

**Total auto-fixable with --unsafe-fixes:** 201 (W293 + F841 + W291)
**NOT auto-fixable:** 66 (F401 + E701 + F811 + E722 + F601 + F823 + F403 + E741 + F402)

### Dimension 2: Corrected Error Distribution

**CRITICAL CORRECTION:** CONTEXT.md estimated ~1,000+ F821 errors in `src/interfaces/adapters/`. Actual measured count is **368 F821** (plus 10 F811).

| Source | F821 Count | Total Errors |
|--------|-----------|--------------|
| `src/interfaces/adapters/` | 368 | 378 (368 F821 + 10 F811) |
| Real code (outside adapters) | 805 | 1,078 |
| **Total** | **1,173** | **1,456** |

### Dimension 3: Post-Cleanup Projection

| Action | Errors Removed |
|--------|---------------|
| Delete `src/interfaces/adapters/` | 378 |
| Auto-fix with `ruff check --fix --unsafe-fixes --select W293,F841,W291` | 201 |
| **Total removable** | **579** |
| **Projected remaining** | **~877** |

**IMPACT:** The ROADMAP success criterion of "<50 errors" is NOT achievable in Phase 1 alone. The remaining ~877 errors are predominantly F821 (undefined-name) in real code files that need manual investigation.

**Recommended adjusted target:** Reduce from 1,456 to <900 (~40% reduction), document remaining errors for future phases.

### Dimension 4: F821 in Real Code (Top Sources)

The 805 non-adapter F821 errors are concentrated in:
- `src/adapters/akshare/` — files using `pd`, `logger`, helper functions without imports
- `src/advanced_analysis/` — undefined names in analysis modules
- `web/backend/app/` — scattered undefined references

These are NOT safe to auto-fix — each requires understanding the intended import.

### Dimension 5: Pre-Existing Issues (NOT Phase 1 Scope)

1. **FastAPI import smoke test fails** with pre-existing error:
   ```
   ImportError: cannot import name 'get_socketio_manager' from 'app.core.socketio_manager'
   Did you mean: 'get_reconnection_manager'?
   ```
   This is a naming mismatch in `web/backend/app/main.py:37` — not caused by Phase 1 changes.

2. **Pytest baseline:** 1,694 tests collected, 5 collection errors:
   - `tests/contract/test_contract_validator.py`
   - `tests/dashboard/test_dashboard.py`
   - `tests/ddd/test_concurrency_control.py`
   - `tests/ddd/test_phase12_3_realtime_integration.py`
   - `tests/ddd/test_phase_8_infrastructure.py`

3. **No ruff.toml config** in main worktree (only in .worktrees/)

### Dimension 6: Execution Safety

- `src/interfaces/adapters/` contains: 38 files total (36 .py + 2 .backup files)
- Contains 3 test files mixed in: `test_customer_adapter.py`, `test_financial_adapter.py`, `test_simple.py`
- Contains 2 backup files: `akshare_adapter.py.backup_*`, `financial_adapter.py.backup_*`
- Only 2 imports from outside → both are self-imports within the directory itself
- Zero external consumers confirmed via grep

### Dimension 7: Adapter Deletion Verification

Import grep returns exactly 2 results — both self-imports:
```
src/interfaces/adapters/financial_adapter_example.py:from src.interfaces.adapters.financial import FinancialDataSource
src/interfaces/adapters/test_financial_adapter.py:from src.interfaces.adapters.financial import FinancialDataSource
```

Both files will be deleted with the directory. Zero external breakage risk.

### Dimension 8: F401 Manual Fix Assessment

F401 (unused-import, 21 occurrences) is NOT auto-fixable by ruff 0.9.10. Assessment:
- Some may be `__init__.py` re-exports (intentional)
- Some may be type-checking imports (needed at type-check time)
- Each needs manual review — cannot blindly delete
- Recommend: handle in a follow-up pass, not Phase 1

---

## Key Research Findings for Planner

1. **CORRECTION:** Adapter deletion removes 378 errors, not 1,000+. Target needs adjustment.
2. **CORRECTION:** Auto-fix needs `--unsafe-fixes` flag for rules CONTEXT.md assumed were safe.
3. **CORRECTION:** F401 and E701 are NOT auto-fixable — cannot include in `--fix` command.
4. **PRE-EXISTING:** FastAPI smoke test has unrelated import error — must not block Phase 1.
5. **VERIFIED:** Zero external imports of `src.interfaces.adapters` — safe to delete.
6. **ADJUSTED TARGET:** <900 errors (from 1,456) is realistic; <50 is not achievable this phase.

---

*Phase: 01-python-lint-baseline*
*Research completed: 2026-04-06*
