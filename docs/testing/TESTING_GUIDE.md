# Testing Guide (Compatibility Entry)

该文档用于承接历史引用路径 `docs/guides/TESTING_GUIDE.md`。

## 当前标准入口（2026-03）

- 标准前端 E2E：`cd web/frontend && npm run test:e2e`
- 指定浏览器：`npm run test:e2e:chromium|firefox|webkit`
- 策略链路专项：`npm run test:e2e:strategy-chain`
- 标准配置文件：`web/frontend/playwright.config.js`
- 标准测试目录：`web/frontend/tests/e2e`

## 端口来源（推荐）

- 统一从 `web/frontend/.env` 读取，不在脚本中重复硬编码。
- 关键变量：
  - `FRONTEND_PORT=3020`
  - `FRONTEND_BACKUP_PORT=3021`
  - `BACKEND_PORT=8020`
  - `BACKEND_BACKUP_PORT=8021`

## 历史链路说明

- 历史 PM2/视觉专项脚本仍可使用 `web/frontend/playwright.config.ts`（legacy）。
- 不建议直接执行未指定配置的 `playwright test`，避免误收集 Vitest 测试。

## 参考文档映射

- `docs/testing/WEB_E2E_TEST_QUICK_REFERENCE_V2.md`
- `docs/testing/WEB_E2E_TEST_QUICK_REFERENCE.md`
- `docs/guides/pm2/PM2_PLAYWRIGHT_TESTING_GUIDE.md`
- `web/frontend/TESTING_GUIDE.md`
