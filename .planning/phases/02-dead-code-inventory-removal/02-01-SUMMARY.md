---
plan: 02-01
phase: 02-dead-code-inventory-removal
status: complete
started: 2026-04-07
completed: 2026-04-07
---

> **历史实施说明**:
> 本文件属于 `.planning` 阶段执行摘要，不是当前仓库共享规则、当前审批状态或当前实施结果的唯一事实来源。
> 执行共享规则与审批门禁请优先遵循 `architecture/STANDARDS.md`；若涉及当前任务执行状态，再结合根目录 `AGENTS.md`、phase 主文档与最新验证结果核对。

# Summary: Plan 01 — Dead Code Inventory & Functional Tree

## Objective
Produce comprehensive DELETION-CANDIDATES.md with code-path AND functional-tree evidence per STANDARDS.md §4.

## What Was Built

DELETION-CANDIDATES.md at project root — a review document covering 34 files across 5 target directories.

## Key Findings

| Target | Files | Recommendation | Risk |
|--------|-------|---------------|------|
| src/routes/ | 19 | DELETE after redirect | LOW — 1 broken prod caller, 1 CI script |
| src/api/ | 5 | DELETE | LOW — zero prod callers, test imports already broken |
| src/data_access_pkg/ | 5 | DELETE (canonical wins) | LOW — 1 root shim caller (`src/data_access.py:2`) |
| src/db_manager/ | 1 | DELETE | LOW — empty shim, scripts only |
| src/database_optimization/ | 5 | MERGE 4 unique utility files → src/data_access/optimizers/ | MEDIUM — 2 test callers need redirect |

## Sweep Coverage

All 8 sweep types completed (A–H). Full evidence with grep output is in `DELETION-CANDIDATES.md` "Code Path Evidence" sections per table. Summary:

| Sweep | Type | src/routes | src/api | src/data_access_pkg | src/db_manager | src/database_optimization |
|-------|------|-----------|--------|--------------------|---------------|-------------------------|
| A | Static imports | 1 prod + 1 CI | 1 test (broken) | 1 internal | 0 | 2 tests |
| B | String/dynamic refs | 0 | 0 | 1 regression test | 1 test (4 mock patches) | 2 report refs |
| C | Dynamic imports | 0 | 0 | 0 | 0 | 0 |
| D | `__all__`/namespace | 3 `__all__` | 2 `__all__` | 1 `__all__` | 1 `__all__` | 1 `__all__` |
| E | Shell-embedded | 1 CI script | 0 | 0 | 0 | 0 |
| F | Compat shim chains | 1 external | 0 | 0 | 0 | 0 |
| G | Route registration | 11 APIRouter | 3 APIRouter | N/A | N/A | N/A |
| H | Build/packaging | 0 | 0 | 0 | 0 | 0 |

## Special Cases Documented

1. **Circular dependency**: database_service.py:155 ↔ wencai_routes.py — broken import (wrong function names)
2. **Broken test imports**: tests/api_contract_tests.py:21-23 — src/api/types/ does not exist
3. **Size discrepancy**: tdengine_access.py (23,514 bytes vs 2,770 bytes canonical) — canonical was refactored to thin facade

## Key Files

### key-files.created
- DELETION-CANDIDATES.md

### key-files.modified
- .planning/phases/02-dead-code-inventory-removal/02-01-PLAN.md → 02-01-PLAN.md (renamed)
- .planning/phases/02-dead-code-inventory-removal/02-PLAN-02-redirect-callers.md → 02-02-PLAN.md (renamed)
- .planning/phases/02-dead-code-inventory-removal/02-PLAN-03-merge-overlapping.md → 02-03-PLAN.md (renamed)
- .planning/phases/02-dead-code-inventory-removal/02-PLAN-04-approved-deletion.md → 02-04-PLAN.md (renamed)

## Deviations
- Plan files renamed from `{phase}-PLAN-{N}-{name}.md` to `{phase}-{N}-PLAN.md` to match GSD tooling convention (files were not discoverable by gsd-tools otherwise)

## Self-Check: PASSED
- [x] DELETION-CANDIDATES.md exists with all 5 target directories
- [x] BOTH code-path AND functional-tree judgments present
- [x] 8 sweep types (A-H) completed
- [x] Circular dependency documented
- [x] src/api/types/ non-existence confirmed
- [x] tdengine_access.py size discrepancy root-caused
- [x] Grep evidence inline
- [x] Status: PENDING USER APPROVAL
