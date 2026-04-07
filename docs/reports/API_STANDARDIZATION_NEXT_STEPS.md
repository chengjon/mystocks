# API Standardization - Next Steps and Status Report

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## 🟢 Completed Actions

### 1. Backend Route Prefix Fixes
We have successfully refactored the following router definitions to remove hardcoded prefixes, ensuring they integrate correctly with `main.py`'s `VERSION_MAPPING` (which sets `/api/v1/...`):

*   ✅ `web/backend/app/api/market.py` (Fixed `/api/market` -> ``)
*   ✅ `web/backend/app/api/strategy.py` (Fixed `/api/strategy` -> ``)
*   ✅ `web/backend/app/api/monitoring.py` (Fixed `/api/monitoring` -> ``)
*   ✅ `web/backend/app/api/technical_analysis.py` (Fixed `/api/technical` -> ``)
*   ✅ `web/backend/app/api/tdx.py` (Fixed `/api/tdx` -> ``)
*   ✅ `web/backend/app/api/announcement.py` (Fixed `/api/announcement` -> ``)
*   ✅ `web/backend/app/api/trade/routes.py` (Fixed `/trade` -> ``)

### 2. Frontend Migration
*   ✅ `web/frontend/src/api/index.js` has been fully updated to use the standardized `/v1` paths for all 74+ endpoints.
*   ✅ Legacy endpoint compatibility is maintained via redirects in the backend.

### 3. Type System
*   ✅ `scripts/generate_frontend_types.py` has been enhanced to support `UnifiedResponse<T>` generics.
*   ✅ `web/frontend/src/api/types/generated-types.ts` has been regenerated with the new correct types.

---

## 🚀 Immediate Next Steps (This Week)

### 1. End-to-End Verification (Priority: Critical)
**Objective**: Ensure that the new paths are working and the old paths are redirecting correctly.

**Test Plan**:
1.  **Restart Backend**: `pm2 restart mystocks-backend` (or equivalent).
2.  **Verify New Path**: `curl http://localhost:8000/api/v1/market/kline?symbol=000001` (Should return 200 OK).
3.  **Verify Redirect**: `curl -I http://localhost:8000/api/market/kline?symbol=000001` (Should return 301 Moved Permanently).
4.  **Frontend Check**: Open the web application and verify that charts and data load without 404 errors in the console.

### 2. Documentation Update (Priority: High)
**Objective**: Ensure API documentation reflects the new reality.

*   Update `docs/api/API_INDEX.md` to reflect the v1 structure explicitly.
*   Generate a new `endpoints_catalog.md` using `scripts/generate_openapi.py`.

### 3. Real Data Integration Pilot (Priority: High)
**Objective**: Start switching from Mock to Real data for safe modules.

*   **Target**: `data.py` (Stock Lists, Industries, Concepts).
*   **Action**: Verify `data.py` is connecting to the real database and returning correct data.

---

## 📅 Upcoming Plan (This Month)

| Task | Est. Time | Priority |
| :--- | :--- | :--- |
| **Phase 2: OpenAPI Refinement** | 4-6h | Medium |
| **Frontend Component Integration** | 6-8h | Medium |
| **Real Data Pilot (Read-Only)** | 8-10h | High |

## ⚠️ Risk Mitigation

*   **Redirects**: We have implemented 301 redirects in `main.py` for key endpoints like `/market/kline`. We should monitor logs for access to these old paths.
*   **Rollback**: If critical issues arise, revert `main.py` to use the old router inclusion method temporarily while keeping the code refactored.
