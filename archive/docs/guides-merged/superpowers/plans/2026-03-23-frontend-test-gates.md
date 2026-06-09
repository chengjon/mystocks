# Frontend Test Gates Implementation Plan

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the verified frontend test stack enforceable in CI by adding a real business-smoke Playwright gate, authenticated Lighthouse collection, selector-policy compliance, and corrected visual-test wiring.

**Architecture:** Keep `Vitest + Vue Test Utils + MSW` as the blocking unit/integration layer, use Playwright Chromium business smoke as the blocking E2E layer, keep cross-browser as a lighter dedicated workflow, and use LHCI with a Puppeteer auth bootstrap so protected-route audits measure real app pages instead of login redirects.

**Tech Stack:** Vitest, Vue Test Utils, MSW, Playwright, Lighthouse CI, GitHub Actions, Node.js

---

### Task 1: Lock New CI Expectations with Failing Tests

**Files:**
- Modify: `web/frontend/tests/unit/config/testing-mainline-gates.spec.ts`
- Modify: `web/frontend/tests/unit/workflows/ci-workflow-gates.spec.ts`
- Create: `web/frontend/tests/unit/config/lighthouse-mainline-gates.spec.ts`

- [ ] **Step 1: Add failing expectations for the new business-smoke scripts and workflow wiring**
- [ ] **Step 2: Add a failing Lighthouse config gate asserting auth bootstrap is enabled for protected routes**
- [ ] **Step 3: Run the targeted Vitest files and confirm they fail for the expected reasons**

### Task 2: Implement Playwright Mainline and LHCI Auth Bootstrap

**Files:**
- Modify: `web/frontend/package.json`
- Modify: `web/frontend/lighthouserc.cjs`
- Create: `web/frontend/scripts/lighthouse-auth.cjs`
- Create: `web/frontend/tests/e2e/auth-login.spec.ts`
- Modify: `web/frontend/tests/e2e/critical/menu-navigation-fixed.spec.ts`

- [ ] **Step 1: Add a canonical auth-login Playwright smoke spec using `getByRole` / `getByTestId`**
- [ ] **Step 2: Replace the remaining selector-policy violation in `menu-navigation-fixed.spec.ts`**
- [ ] **Step 3: Add `test:e2e:auth` and `test:e2e:business-smoke` package scripts**
- [ ] **Step 4: Add LHCI Puppeteer auth bootstrap so protected routes are audited in authenticated state**
- [ ] **Step 5: Run the new/updated Playwright and LHCI commands and confirm they pass**

### Task 3: Align GitHub Actions with the Verified Mainline

**Files:**
- Modify: `.github/workflows/frontend-testing.yml`
- Modify: `.github/workflows/e2e-testing.yml`
- Modify: `.github/workflows/visual-testing.yml`

- [ ] **Step 1: Make `frontend-testing.yml` run the new Chromium business-smoke gate**
- [ ] **Step 2: Keep `e2e-testing.yml` as the cross-browser workflow but align commands, versions, and smoke scope**
- [ ] **Step 3: Fix visual workflow path detection so it watches the real `web/frontend/tests/visual/**` tree**
- [ ] **Step 4: Run the workflow gate unit tests and confirm they pass**

### Task 4: Stabilize Visual Checks and Documentation

**Files:**
- Modify: `web/frontend/tests/visual/utils/helpers.ts`
- Modify: `web/frontend/tests/visual/pages/dashboard.spec.ts`
- Modify: `web/frontend/tests/README-E2E.md`
- Modify: `docs/testing/e2e/README.md`

- [ ] **Step 1: Make visual helper assertions validate rendered/computed theme state instead of brittle raw HTML color strings**
- [ ] **Step 2: Re-run the dashboard visual suite and ensure the non-screenshot dashboard checks pass**
- [ ] **Step 3: Update the E2E docs to match the actual package scripts, CI roles, and reporting expectations**
- [ ] **Step 4: Re-run the final verification commands and record the exact results**
