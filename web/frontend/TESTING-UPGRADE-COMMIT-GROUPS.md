# Testing Upgrade Commit Groups

> **历史总结说明**:
> 本文件是某次 Web 功能开发、修复、集成、测试、验收或阶段性交付的历史总结快照，用于追溯当时的实施结论。
> 其中的完成度、通过数、状态和结论不应直接视为当前事实；引用前应结合 `architecture/STANDARDS.md`、当前实现、基线文件与最新验证结果重新确认。


本文件只整理本轮“前端测试门禁硬化 + MSW / axe / Lighthouse CI 补齐”相关改动，尽量与工作区中其他既有脏改动隔离。

## Group 1: CI Gates and Validation Scripts

目标：
- 收紧类型/单测/E2E 门禁
- 同步 `validate-e2e-setup` 到当前真实能力
- 把 `MSW / axe / LHCI` 入口纳入 CI 与脚本校验

建议文件：
- `/.github/workflows/frontend-testing.yml`
- `/.github/workflows/typescript-type-check.yml`
- `/.gitignore`
- `/web/frontend/vitest.config.mts`
- `/web/frontend/vitest.setup.ts`
- `/web/frontend/validate-e2e-setup.js`
- `/web/frontend/scripts/stable-unit-suite.js`
- `/web/frontend/tests/unit/config/vitest-msw-gates.spec.ts`
- `/web/frontend/tests/unit/workflows/ci-workflow-gates.spec.ts`
- `/web/frontend/tests/unit/scripts/stable-unit-suite.spec.ts`
- `/web/frontend/tests/unit/scripts/validate-e2e-setup.spec.ts`

建议提交信息：
- `test[frontend-ci]: harden gates and validate e2e entrypoints`

建议 `git add`：

```bash
git add \
  .github/workflows/frontend-testing.yml \
  .github/workflows/typescript-type-check.yml \
  .gitignore \
  web/frontend/vitest.config.mts \
  web/frontend/vitest.setup.ts \
  web/frontend/validate-e2e-setup.js \
  web/frontend/scripts/stable-unit-suite.js \
  web/frontend/tests/unit/config/vitest-msw-gates.spec.ts \
  web/frontend/tests/unit/workflows/ci-workflow-gates.spec.ts \
  web/frontend/tests/unit/scripts/stable-unit-suite.spec.ts \
  web/frontend/tests/unit/scripts/validate-e2e-setup.spec.ts
```

## Group 2: Frontend Testing Capabilities

目标：
- 接入 `MSW` 到 Vitest
- 接入 `axe` smoke 到 Playwright
- 接入 `LHCI` 隔离 mock-build 流程

建议文件：
- `/web/frontend/package.json`
- `/web/frontend/package-lock.json`
- `/web/frontend/tests/mocks/handlers.ts`
- `/web/frontend/tests/mocks/server.ts`
- `/web/frontend/src/api/services/__tests__/strategyService.msw.spec.ts`
- `/web/frontend/tests/e2e/accessibility-smoke.spec.ts`
- `/web/frontend/lighthouserc.cjs`
- `/web/frontend/tests/README-E2E.md`
- `/web/frontend/TASK-REPORT.md`

建议提交信息：
- `test[frontend]: add msw axe and lighthouse smoke coverage`

建议 `git add`：

```bash
git add \
  web/frontend/package.json \
  web/frontend/package-lock.json \
  web/frontend/tests/mocks/handlers.ts \
  web/frontend/tests/mocks/server.ts \
  web/frontend/src/api/services/__tests__/strategyService.msw.spec.ts \
  web/frontend/tests/e2e/accessibility-smoke.spec.ts \
  web/frontend/lighthouserc.cjs \
  web/frontend/tests/README-E2E.md \
  web/frontend/TASK-REPORT.md
```

## Group 3: E2E Runtime Stabilization

目标：
- 修复共享 PM2 / external frontend 模式下的 readiness 假失败
- 真正开放策略 lifecycle 动作链路
- 修正策略管理页失败态/可访问性文案

建议文件：
- `/web/backend/app/api/strategy_management/get_monitoring_db.py`
- `/web/backend/tests/test_strategy_runtime_fallback.py`
- `/web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- `/web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyManagement.scss`
- `/web/frontend/src/views/artdeco-pages/strategy-tabs/strategyLifecycleAvailability.ts`
- `/web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/strategyLifecycleAvailability.test.ts`
- `/web/frontend/tests/e2e/artdeco-config-integration.spec.ts`
- `/web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`
- `/web/frontend/tests/e2e/market-data.spec.ts`
- `/web/frontend/tests/e2e/strategy-crud.spec.ts`
- `/web/frontend/tests/e2e/strategy-monitor.spec.ts`

建议提交信息：
- `fix[e2e]: stabilize external frontend flows and enable strategy lifecycle`

建议 `git add`：

```bash
git add \
  web/backend/app/api/strategy_management/get_monitoring_db.py \
  web/backend/tests/test_strategy_runtime_fallback.py \
  web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue \
  web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyManagement.scss \
  web/frontend/src/views/artdeco-pages/strategy-tabs/strategyLifecycleAvailability.ts \
  web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/strategyLifecycleAvailability.test.ts \
  web/frontend/tests/e2e/artdeco-config-integration.spec.ts \
  web/frontend/tests/e2e/comprehensive-all-pages.spec.ts \
  web/frontend/tests/e2e/market-data.spec.ts \
  web/frontend/tests/e2e/strategy-crud.spec.ts \
  web/frontend/tests/e2e/strategy-monitor.spec.ts
```

## Notes

- `test:e2e:chromium` 当前已实测 `109/109` 通过。
- `test:e2e:axe` 当前已实测 `chromium 2/2` 通过。
- `test:e2e:lighthouse` 当前已实测通过，走 `dist-lighthouse + preview:lighthouse` 隔离链路。
- 提交前建议先用 `git diff --cached --name-only` 核对 staged 文件是否只包含目标分组。

## Group 4: Testing Mainline Cleanup

目标：
- 停止将 Cypress / Puppeteer 作为活跃 Web 测试入口
- 对齐旧 `e2e-testing.yml` / `playwright.yml` 到新的主线入口
- 将活跃文档统一到 “Playwright 主线，Cypress/Puppeteer 为 legacy” 口径

建议文件：
- `/.github/workflows/e2e-testing.yml`
- `/.github/workflows/playwright.yml`
- `/docs/guides/CLAUDE_AGENTS_SUMMARY.md`
- `/docs/guides/web/WEB_TESTING_TOOLS_SETUP.md`
- `/docs/api/guides/integration/前后端整合与部署完整方案.md`
- `/web/frontend/FRONTEND_IMPLEMENTATION_SUMMARY.md`
- `/web/frontend/FRONTEND_SSE_INTEGRATION_COMPLETE.md`
- `/web/frontend/TESTING_GUIDE.md`
- `/web/frontend/README_SSE_INTEGRATION.md`
- `/web/frontend/.lighthouserc.json` (delete)
- `/web/frontend/package.json`
- `/web/frontend/package-lock.json`
- `/web/frontend/scripts/test-pages.mjs`
- `/web/frontend/tests/unit/config/testing-mainline-gates.spec.ts`
- `/web/frontend/tests/unit/port-config-consistency.spec.ts`
- `/web/frontend/scripts/stable-unit-suite.js`
- `/web/frontend/cypress.config.ts` (delete)
- `/web/frontend/cypress/e2e/my-app.cy.ts` (delete)
- `/web/frontend/test_all_pages.js` (delete)
- `/web/frontend/scripts/diagnose-pages.js` (delete)

建议提交信息：
- `refactor[testing]: retire cypress and puppeteer from active web test mainline`

建议 `git add`：

```bash
git add \
  .github/workflows/e2e-testing.yml \
  .github/workflows/playwright.yml \
  docs/guides/CLAUDE_AGENTS_SUMMARY.md \
  docs/guides/web/WEB_TESTING_TOOLS_SETUP.md \
  docs/api/guides/integration/前后端整合与部署完整方案.md \
  web/frontend/FRONTEND_IMPLEMENTATION_SUMMARY.md \
  web/frontend/FRONTEND_SSE_INTEGRATION_COMPLETE.md \
  web/frontend/TESTING_GUIDE.md \
  web/frontend/README_SSE_INTEGRATION.md \
  web/frontend/.lighthouserc.json \
  web/frontend/package.json \
  web/frontend/package-lock.json \
  web/frontend/scripts/test-pages.mjs \
  web/frontend/tests/unit/config/testing-mainline-gates.spec.ts \
  web/frontend/tests/unit/port-config-consistency.spec.ts \
  web/frontend/scripts/stable-unit-suite.js \
  web/frontend/cypress.config.ts \
  web/frontend/cypress/e2e/my-app.cy.ts \
  web/frontend/test_all_pages.js \
  web/frontend/scripts/diagnose-pages.js
```
