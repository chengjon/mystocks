---
plan: 02-03
phase: 02-dead-code-inventory-removal
status: complete
started: 2026-04-07
completed: 2026-04-07
---

> **历史实施说明**:
> 本文件属于 `.planning` 阶段执行摘要，不是当前仓库共享规则、当前审批状态或当前实施结果的唯一事实来源。

# Summary: Plan 03 — Merge Overlapping Modules

## Objective
Merge unique content from `src/data_access_pkg/` and `src/database_optimization/` into their canonical counterparts in `src/data_access/`.

## What Was Done

All merge work was already completed in prior phases. Verification confirmed:

### Task 1: tdengine_access.py Size Discrepancy
- **RESOLVED**: Canonical `src/data_access/tdengine_access.py` is a thin facade that delegates to 3 sub-modules:
  - `_tdengine_query_operations.py`
  - `_tdengine_write_operations.py`
  - `_tdengine_validation.py`
- The `data_access_pkg/tdengine_access.py` (older monolithic version) is fully superseded.

### Task 2: data_access_pkg Coverage Verification
All 5 files in `src/data_access_pkg/` are fully covered by canonical `src/data_access/`:

| data_access_pkg file | Canonical counterpart | Verdict |
|---|---|---|
| `__init__.py` (6 exports) | `__init__.py` (7 exports + factory) | Canonical superset |
| `interface.py` (84 lines, 4 abstract methods) | `interfaces.py` (318 lines, 5 abstract + 5 helpers + 3 exceptions) | Canonical superset |
| `postgresql_access.py` (481 lines) | `postgresql_access.py` (500 lines, mixin absorbed) | Canonical superset |
| `tdengine_access.py` (monolithic) | `tdengine_access.py` (facade + 3 sub-modules) | Canonical refactored |
| `_postgresql_access_query_mixin.py` (270 lines) | Absorbed into canonical `postgresql_access.py` | No separate file needed |

### Task 3: Optimizer Files
All 4 optimizer files already exist in canonical `src/data_access/optimizers/`:

| database_optimization file | Canonical file | Status |
|---|---|---|
| `performance_monitor.py` (300 lines) | `performance_monitor.py` (252 lines, type-annotated) | Already merged (cleaner) |
| `postgresql_index_optimizer.py` (362 lines) | `postgresql_index_optimizer.py` (327 lines, type-annotated) | Already merged (cleaner) |
| `slow_query_analyzer.py` (311 lines) | `slow_query_analyzer.py` (277 lines, type-annotated) | Already merged (cleaner) |
| `tdengine_index_optimizer.py` (218 lines) | `tdengine_index_optimizer.py` (177 lines, type-annotated) | Already merged (cleaner) |

Canonical `optimizers/__init__.py` already exports all 6 symbols correctly.

### Task 4: Test Import Redirects
- **Zero test files** import from `src.database_optimization` or `database_optimization`.
- Only `scripts/dev/quality_gate/fix_test_imports.py` has the mapping rule (the fix script itself).
- No redirection needed.

## Key Findings

- All merge work was completed in prior phases before Phase 2 began.
- The canonical versions are refined: type-annotated, simplified docstrings, proper sub-module decomposition.
- Zero production or test code requires import redirection.

## Verification Results

```
data_access_pkg coverage: VERIFIED (canonical superset)
optimizer merge: VERIFIED (4 files already in canonical)
test imports: VERIFIED (zero stale imports)
tdengine discrepancy: RESOLVED (refactored facade + sub-modules)
```

## Self-Check: PASSED
- [x] All data_access_pkg files covered by canonical src/data_access/
- [x] All 4 optimizer files exist in src/data_access/optimizers/ with __init__.py exports
- [x] Zero test files import from database_optimization
- [x] tdengine size discrepancy root-caused (refactored architecture)
- [x] No new code changes required
