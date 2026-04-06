---
plan: 02-02
phase: 02-dead-code-inventory-removal
status: complete
started: 2026-04-07
completed: 2026-04-07
---

> **历史实施说明**:
> 本文件属于 `.planning` 阶段执行摘要，不是当前仓库共享规则、当前审批状态或当前实施结果的唯一事实来源。

# Summary: Plan 02 — Caller Redirection & Dead Import Cleanup

## Objective
Redirect or remove all callers of `src/routes/`, `src/api/`, and `src/db_manager/`.

## What Was Done

1. **database_service.py**: Already fixed in prior work — uses `WencaiService` directly via `app.services.wencai_service`. No circular import remains.
2. **tests/api_contract_tests.py**: Already fixed — no broken `src.api.types` imports present.
3. **scripts/cicd_pipeline.sh**: Updated smoke test from `from src.routes import *` → `from web.backend.app.main import app`.
4. **Dev scripts**: Already had correct mappings (`db_manager` → `src.storage.database`, `database_optimization` → `src.data_access.optimizers`).

## Key Findings

- Most redirection work was already done in prior phases
- Only `cicd_pipeline.sh` had a remaining stale reference
- Zero external callers of `src.routes.*`, `src.api.*`, `src.db_manager.*` confirmed outside target directories

## Verification Results

```
routes: CLEAN
api: CLEAN
db_manager: CLEAN
```

## Key Files

### key-files.modified
- scripts/cicd_pipeline.sh (line 184: updated smoke test import)

## Self-Check: PASSED
- [x] Zero production callers of `src.routes.*` outside src/routes/
- [x] Zero production callers of `src.api.*` outside src/api/
- [x] Zero production callers of `src.db_manager.*` outside src/db_manager/
- [x] No redirects to wrong layer (FastAPI route handlers)
- [x] `bash -n scripts/cicd_pipeline.sh` passes
