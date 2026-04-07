# E2E and Kline Fallback Hardening Implementation Plan

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复当前首批前端 E2E 失败点，并给后端 K 线 fallback 增加可配置开关，确保开发/演示环境可稳定运行。

**Architecture:** 前端先聚焦失败用例对应的策略页 fallback 呈现逻辑，按 TDD 修复断言失配；后端在 `StockSearchService` 里把 fallback 行为改为环境可控（默认开启），保持上游失败时服务可用。全程保持最小变更并附回归验证。

**Tech Stack:** Vue 3 + Playwright + FastAPI + pytest + PM2。

### Task 1: Stabilize First E2E Failures (Strategy Fallback Badge)

**Files:**
- Modify: `web/frontend/tests/e2e/strategy-management-boundary.spec.ts`
- Modify: `web/frontend/tests/e2e/strategy-management-chain.spec.ts`
- Modify: `web/frontend/src/views/**` (仅当定位到真实 UI 缺陷时)

**Step 1: Write/adjust failing test expectation**
- 锁定失败断言（`.source-badge.mock`）与当前 UI 的真实结构差异。

**Step 2: Run test to verify RED**
- Run: `E2E_FRONTEND_PORT=3173 FRONTEND_BASE_URL=http://127.0.0.1:3173 npx playwright test --config web/frontend/playwright.config.js --project=chromium web/frontend/tests/e2e/strategy-management-boundary.spec.ts web/frontend/tests/e2e/strategy-management-chain.spec.ts`
- Expected: 至少包含当前已知失败断言。

**Step 3: Minimal implementation**
- 优先修复产品代码（保持 MOCK 回退状态可见），若仅选择器过时则最小更新测试选择器，避免误报。

**Step 4: Run tests to verify GREEN**
- 同命令重跑并确认通过。

### Task 2: Add Kline Fallback Feature Toggle (TDD)

**Files:**
- Modify: `web/backend/tests/test_runtime_regressions_p0.py`
- Modify: `web/backend/app/services/stock_search_service/stock_search_service.py`

**Step 1: Write failing tests**
- 新增测试覆盖：
  - 开关关闭时，上游异常不应返回 fallback（返回 `None`）
  - 开关开启时，上游异常应返回 fallback 数据。

**Step 2: Run test to verify RED**
- Run: `pytest -n 0 --no-cov web/backend/tests/test_runtime_regressions_p0.py`

**Step 3: Minimal implementation**
- 在 `StockSearchService` 读取环境变量（例如 `KLINE_FALLBACK_ENABLED`，默认 `true`）。
- 上游失败时按开关决定是否返回 fallback。

**Step 4: Run tests to verify GREEN**
- 同命令重跑确认通过。

### Task 3: Full Verification and Runtime Confirmation

**Files:**
- Modify: `docs/worklogs/...`（仅在项目流程要求时）

**Step 1: Frontend type check**
- Run: `npm --prefix web/frontend run type-check`

**Step 2: Target E2E smoke**
- Run: `bash scripts/run_e2e_pm2.sh`

**Step 3: Service and API smoke**
- Run:
  - `pm2 list`
  - `curl http://localhost:8020/health`
  - `curl http://localhost:3020`
  - 登录 + `watchlist/quotes/kline` 冒烟

**Step 4: Summarize mandatory quality status**
- 输出结构性语法、类型、PM2、E2E、回归/既有债务区分。
