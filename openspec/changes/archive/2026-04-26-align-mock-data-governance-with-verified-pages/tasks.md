## 1. Governance Baseline

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Confirm the active `verified/pending` page inventory that will be used as the execution truth for this batch, and produce a table mapping each `verified` page to its adapter/service/client mock-routing status and whether silent mock fallback exists.
- [x] 1.2 Enumerate current frontend and backend mock/fallback entrypoints, and classify each by layer (`client layer`, `service layer`, `adapter layer`, `backend/runtime layer`) and disposition (`allowed for explicit mock mode`, `allowed for automation isolation`, `must be removed from verified mainline`).
- [x] 1.3 Record any historical documents or reports that still present `VITE_APP_MODE`, hybrid fallback, or mock-path success as current truth.

## 2. Frontend Mainline Alignment

- [x] 2.1 Remove silent mock fallback from `verified`-path strategy adapters and make failure return explicit error/empty-state inputs instead of mock payloads; consuming views/stores remain responsible for rendering loading/error/empty/request-id states.
- [x] 2.2 Remove silent mock fallback from `verified`-path market adapters and make failure return explicit error/empty-state inputs instead of mock payloads; consuming views/stores remain responsible for rendering loading/error/empty/request-id states.
- [x] 2.3 Remove `VITE_APP_MODE`-driven endpoint branching from `strategyService.ts`, keep the real endpoint family as the service truth, and let mock/real routing be handled only by the shared `apiClient` gate controlled by `VITE_USE_MOCK_DATA`.
- [x] 2.4 Confirm `useBackendReadiness.ts` remains compliant as a controlled explicit-mode / automation-isolation fallback path and does not require behavior changes for this change.

## 3. Documentation And Testing Alignment

- [x] 3.1 Update `web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md` so `VITE_USE_MOCK_DATA` is documented as the active frontend switch and `VITE_APP_MODE` is explicitly marked historical.
- [x] 3.2 Update mock-data governance docs to point to the final implementation truth and remove any remaining ambiguity around verified-page fallback rules.
- [x] 3.3 Review adapter/unit/E2E tests that assume silent mock fallback and update them to reflect the new verified-path behavior and explicit mock-mode-only usage.
- [x] 3.4 Create or update a lightweight audit ledger/checklist for page-level mock usage, including page status, real endpoint, mock source, client/service/adapter layer status, fallback status, and retirement condition.

## 4. Validation

- [x] 4.1 Validate the OpenSpec change with `openspec validate align-mock-data-governance-with-verified-pages --strict`.
- [x] 4.2 Run targeted frontend tests or checks that cover strategy and market integration paths after the implementation batch lands.
- [x] 4.3 Capture closeout evidence that distinguishes `mock acceptance`, `real mainline verified`, and any remaining approved pending blockers.
