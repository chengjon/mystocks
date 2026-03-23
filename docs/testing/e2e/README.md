# 前端测试与 CI 门禁现状

## 当前主线

MyStocks Web 前端当前测试主线分为 5 层：

1. `Vitest + Vue Test Utils + MSW`
2. Playwright selector policy gate
3. Playwright Chromium business smoke
4. Playwright + `@axe-core/playwright` a11y smoke
5. Lighthouse CI authenticated performance smoke

当前阻塞式 PR 门禁落在 [frontend-testing.yml](/opt/claude/mystocks_spec/.github/workflows/frontend-testing.yml)。
跨浏览器执行落在 [e2e-testing.yml](/opt/claude/mystocks_spec/.github/workflows/e2e-testing.yml)。
视觉回归执行落在 [visual-testing.yml](/opt/claude/mystocks_spec/.github/workflows/visual-testing.yml)。
reviewer 速查表见 [PR_GATE_QUICK_REFERENCE](/opt/claude/mystocks_spec/docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md)。

## 入口命令

在 `web/frontend` 下执行：

```bash
# 套件完整性校验
npm run test:e2e:validate

# 登录鉴权 smoke
PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
BACKEND_BASE_URL=http://127.0.0.1:8020 \
E2E_BACKEND_URL=http://127.0.0.1:8020 \
npm run test:e2e:auth

# Chromium 业务主线 smoke
PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
BACKEND_BASE_URL=http://127.0.0.1:8020 \
E2E_BACKEND_URL=http://127.0.0.1:8020 \
npm run test:e2e:business-smoke

# Selector policy gate
npm run test:e2e:selectors

# 可访问性 smoke
PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
npm run test:e2e:axe

# Lighthouse CI
npm run test:e2e:lighthouse

# Dashboard visual smoke
npm run test:visual:dashboard

# Chart visual smoke
npm run test:visual:charts
```

## 业务覆盖

`test:e2e:business-smoke` 当前覆盖：

- 登录鉴权
- 菜单/路由可达性
- 行情页
- 策略管理
- 回测链路
- K 线图表基础交互

`test:e2e:auth` 单独覆盖：

- 未登录访问受保护路由时跳转 `/login?redirect=...`
- UI 登录表单提交
- 真实后端登录响应写入 `auth_token` / `auth_user`
- 登录后返回请求的受保护路由

## CI 分层

### `frontend-testing.yml`

PR 阻塞门禁，目标是快而准：

- `eslint`
- Request ID / route purity / selector policy / type ceiling
- `test:unit:stable`
- `test`
- `test:e2e:business-smoke`
- `test:e2e:axe`
- `test:e2e:lighthouse`

### `e2e-testing.yml`

跨浏览器 smoke：

- `chromium`
- `firefox`
- `webkit`

当前跨浏览器主线包含：

- `auth-login.spec.ts`
- `critical/menu-navigation-fixed.spec.ts`
- `kline-chart.spec.ts`

### `visual-testing.yml`

视觉测试当前仍为独立 workflow，不建议直接并入 PR 阻塞主线，原因：

- dashboard visual 仍以主题/结构断言为主，非完整 screenshot baseline 套件
- baseline 维护成本高于当前业务 smoke

当前已可运行的 visual 入口：

- `test:visual:dashboard`
- `test:visual:charts`
- `test:visual:update`
- `test:visual:charts:update`

## Lighthouse 说明

`lighthouserc.cjs` 已启用 `puppeteerScript` 认证引导：

- `./scripts/lighthouse-auth.cjs`
- `disableStorageReset: true`

这样受保护页面在采集前会预先注入 `auth_token` / `auth_user`，避免把 `/dashboard`、`/market/realtime`、`/strategy/repo` 全部测成登录页。

## Selector Policy

Playwright canonical E2E 用例必须优先使用用户视角定位：

- `getByRole()`
- `getByText()`
- `getByTestId()`

禁止新增原始 CSS selector：

- `page.locator(...)`
- `page.$(...)`
- `page.$$()`
- `querySelector(...)`

仅当图表 `canvas/svg` 等无语义节点确实无法替代时，允许行内标注 `e2e-selector-exception`。

## 当前结论

当前仓库已经具备可执行的前端自动化门禁主线，但仍应把 visual regression 继续从“可运行”推进到“可维护的稳定基线”后，再决定是否提升为阻塞项。
