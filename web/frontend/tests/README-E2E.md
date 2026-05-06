# MyStocks 端到端自动化测试套件

> **参考指南说明**:
> 本文件用于提供 Web 子系统的使用方法、操作指引、接口接入说明、排障提示或结构参考，帮助理解局部实现与协作方式。
> 其中的步骤、示例、端口、目录和操作建议应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为仓库共享规则或当前状态的唯一事实来源。


> 2026-03 基线：标准 E2E 入口为 `npm run test:e2e`，使用 `playwright.config.js`（`tests/e2e`）。
> `playwright.config.ts` 仅用于历史 legacy 专项脚本。
> 端口优先由 `.env` 注入；若缺失，当前 helper / smoke runner 会回落到标准端口：前端 `3020`（备份 `3021`），后端 `8020`（备份 `8021`）。
> CI 阻塞主线已收敛为：`Vitest stable unit` + `selector gate` + `test:e2e:business-smoke` + `test:e2e:axe` + `test:e2e:lighthouse`。
> 共享 PM2 集成测试的 canonical 执行顺序与 `pm2 save` / `pm2 resurrect` 约束，统一参考 [`docs/guides/pm2/PM2_INTEGRATION_TEST_WORKFLOW.md`](/opt/claude/mystocks_spec/docs/guides/pm2/PM2_INTEGRATION_TEST_WORKFLOW.md)。

## 概述

本测试套件基于 Playwright 实现完整的端到端自动化测试，专门针对基于 PM2 运行的 MyStocks Web 服务进行全面验证。严格按照您的要求实现，不以简单的 HTTP 状态码作为通过依据，而是进行全链路的渲染、元素、数据、交互校验。

## 测试覆盖范围

### Phase 1: 前置校验 (Preflight Checks)
- ✅ PM2 进程状态验证（前端/后端服务）
- ✅ 端口连通性检查（3020/8020）
- ✅ HTTP 响应状态验证
- ✅ 前端 HTML 内容完整性验证

### Phase 2: 页面加载完整性 (Page Load Integrity)
- ✅ DOM 元素存在性验证（导航栏、内容容器、核心按钮等 3+ 关键元素）
- ✅ 页面标题和元数据校验（UTF-8 编码、viewport 设置）
- ✅ 资源加载验证（JavaScript bundles、CSS 样式表、无失败请求）
- ✅ 控制台错误检测（JavaScript 运行时错误）
- ✅ 页面渲染完整性验证（内容高度、可见元素、无加载指示器）

### Phase 3: 前后端联动 (Frontend-Backend Integration)
- ✅ 后端 API 健康检查（/health 端点）
- ✅ 前端数据获取验证（网络请求监控）
- ✅ API 响应格式验证（JSON 结构、code/message 字段）
- ✅ 前后端数据一致性校验（股票代码等核心字段匹配）

### Phase 4: 基础交互 (Basic Interactions)
- ✅ 页面导航功能验证（URL 变化检测）
- ✅ 表单输入功能验证（文本输入接受）
- ✅ 按钮点击反馈验证（页面状态变化或加载指示）
- ✅ 无崩溃错误验证（JavaScript 运行时错误检测）

## 测试结果输出

### 📊 结构化报告
- **JSON 详细报告**: `test-results/e2e-test-report.json`
- **文本摘要报告**: `test-results/test-summary.txt`
- **控制台输出**: 实时测试进度和结果摘要

### 📸 证据收集
- **失败截图**: `test-results/screenshots/` (失败时自动截图)
- **全程录屏**: `test-results/videos/` (失败时录制)
- **错误分类**: 明确区分前端/后端/联动问题

## 使用方法

### 前置条件

确保 MyStocks 服务已通过 PM2 启动：

```bash
# 前端服务 (端口 3020)
pm2 list | grep mystocks-frontend

# 后端服务 (端口 8020)
pm2 list | grep mystocks-backend
```

注意：
- `scripts/run_e2e_pm2.sh` 只适合隔离的 CI / 测试环境，不适合复用当前共享 PM2 会话；它会执行 `pm2 delete all` 清空进程。
- 如果你已经有在线 PM2 服务，优先复用现有前端服务并启用 `PLAYWRIGHT_EXTERNAL_FRONTEND=1`。
- 若要跑完整共享 PM2 回归，不要手工拼接长链，直接执行 [`scripts/run_pm2_integration_workflow.sh`](/opt/claude/mystocks_spec/scripts/run_pm2_integration_workflow.sh) 的 `regression` 模式。

### 运行测试

#### 共享 PM2 环境（当前推荐）
如果 `mystocks-frontend` / `mystocks-backend` 已经在线，优先使用下面这组命令，不要再执行会清空进程的 `scripts/run_e2e_pm2.sh`：

```bash
cd web/frontend

# 先校验 Playwright / README / package.json 入口是否完整
npm run test:e2e:validate

# 先跑登录鉴权 smoke（UI 登录 + 受保护路由跳转）
PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
BACKEND_BASE_URL=http://127.0.0.1:8020 \
E2E_BACKEND_URL=http://127.0.0.1:8020 \
npm run test:e2e:auth

# 再跑 Chromium 业务主线 smoke（登录/菜单/行情/策略/回测/图表）
PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
BACKEND_BASE_URL=http://127.0.0.1:8020 \
E2E_BACKEND_URL=http://127.0.0.1:8020 \
npm run test:e2e:business-smoke
```

说明：
- `test:e2e:validate` 只做套件完整性校验，不会改 PM2 进程。
- `test:e2e:auth` 验证未登录重定向和真实后端登录响应。
- `test:e2e:business-smoke` 是当前 PR 阻塞主线，覆盖登录鉴权、菜单/路由、行情页、策略管理、回测链路、K 线图表。
- `test:e2e:stable` 当前执行 `chromium` stable 子集，适合作为共享环境下的安全回归入口。
- 若只跑 `test:e2e:stable`，必须注明这是 stable 子集，不得表述为“全量 E2E 已通过”。
- 截至 `2026-05-07`，复用 PM2 前端执行 `env PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium` 已实测 `295/295` 通过；该结果可作为当前 Chromium 全量基线，但不自动代表 Firefox / WebKit 同步通过。

#### 可访问性与性能 Smoke
新增的无障碍与性能入口和业务 E2E 分开执行：

```bash
cd web/frontend

# axe-core + Playwright：复用当前 PM2 前端，检查 serious/critical 级问题
PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
npm run test:e2e:axe

# Lighthouse CI：使用 mock build + 独立 preview，不复用当前 PM2 服务
npm run test:e2e:lighthouse

# Dashboard visual smoke
npm run test:visual:dashboard

# Chart visual smoke
npm run test:visual:charts
```

说明：
- `test:e2e:axe` 当前跑 `chromium` 两页 smoke：`/login` 和 `/strategy/repo`。
- `test:e2e:lighthouse` 会先执行 `build:lighthouse:mock`，再在隔离端口 `4273` 启一个 `dist-lighthouse` preview。
- `test:e2e:lighthouse` 不会改动 `3020/8020` 的共享 PM2 会话，适合作为 CI 中的独立性能门禁。
- `test:visual:dashboard` 和 `test:visual:charts` 当前都跑 `chromium` visual baselines，适合作为视觉回归的独立入口。

#### 方法 1: npm 脚本 (推荐)
```bash
cd web/frontend

# 当前 worktree 若受 ancestor package.json / PostCSS sandbox 阻塞，可用 /tmp 副本起前端
# 默认走真实 backend 验证；只有显式设置时才启用 mock fallback
npm run dev:sandbox-safe
VITE_USE_MOCK_DATA=true npm run dev:sandbox-safe

# 运行完整 E2E 测试套件
npm run test:e2e:comprehensive

# 运行 a11y smoke
npm run test:e2e:axe

# 运行 Lighthouse CI smoke（隔离 mock build）
npm run test:e2e:lighthouse

# 运行 API availability 最小 smoke（Data-Indicator + Watchlist-Screener）
# 如当前 backend 未启动，可让脚本自动拉起当前 worktree backend
# 脚本默认优先使用标准端口 3020/3021 与 8020/8021；主端口被占用时自动切到备份端口
START_BACKEND_IF_NEEDED=true npm run test:e2e:api-availability-smoke
```

#### 方法 2: 直接运行脚本
```bash
cd web/frontend

# 运行测试执行器
node run-comprehensive-e2e.js

# 运行 sandbox-safe API availability smoke runner
START_BACKEND_IF_NEEDED=true ./scripts/test-runner/run-api-availability-smoke.sh
```

#### 方法 3: Playwright 直接运行
该方式用于单文件 / grep / 临时调试补充，标准入口仍是 `npm run test:e2e*`。
```bash
cd web/frontend

# 标准入口（优先）
npm run test:e2e
npm run test:e2e:auth
npm run test:e2e:business-smoke
npm run test:e2e:chromium
npm run test:e2e:debug
npm run test:visual:dashboard
npm run test:visual:charts

# 复用当前已在线的 PM2 前端（例如 localhost:3020）
PLAYWRIGHT_EXTERNAL_FRONTEND=1 \
FRONTEND_BASE_URL=http://127.0.0.1:3020 \
E2E_FRONTEND_URL=http://127.0.0.1:3020 \
npm run test:e2e:stable

# npx 补充：单文件临时运行
npx playwright test tests/comprehensive-e2e-validation.spec.ts --project=chromium

npx playwright test tests/comprehensive-e2e-validation.spec.ts --debug
```

### 测试结果查看

测试完成后，查看结果：

```bash
# 查看摘要报告
cat test-results/test-summary.txt

# 查看详细 JSON 报告
cat test-results/e2e-test-report.json | jq '.summary'

# 查看截图和录屏
ls -la test-results/screenshots/
ls -la test-results/videos/
```

## 测试配置

### 服务配置
```javascript
const FRONTEND_CONFIG = {
  name: 'mystocks-frontend',
  port: 3020,
  baseUrl: 'http://localhost:3020'
};

const BACKEND_CONFIG = {
  name: 'mystocks-backend',
  port: 8020,
  baseUrl: 'http://localhost:8020'
};
```

### Playwright 配置
- **浏览器**: Chromium, Firefox, WebKit
- **视口**: 1920x1080 (桌面端)
- **超时**: 30秒 (页面加载), 10秒 (操作)
- **截图**: 失败时自动截图
- **录屏**: 失败时录制视频

### AXE / Lighthouse 配置
- `test:e2e:axe`: 只拦截 `serious` / `critical` 级 axe 违规，`color-contrast` 当前作为后续治理项保留在 Lighthouse/设计治理里处理
- `test:e2e:lighthouse`: 使用 `lighthouserc.cjs`，当前采集 `login`、`dashboard`、`market/realtime`、`strategy/repo`、`risk/overview`、`trade/terminal`
- `LHCI` 端口：`4273`
- `LHCI` 浏览器：显式使用 Playwright Chromium 可执行文件，避免系统 Chrome / profile 锁冲突

### Visual 配置
- `test:visual:dashboard`: 当前覆盖 dashboard 主题/布局视觉基线
- `test:visual:charts`: 当前覆盖 `market/technical` 与 `strategy/backtest` 的最小图表视觉基线
- `test:visual:charts:update`: 用于刷新 chart baselines

### Selector Policy
- `tests/e2e/**` 的新增或修改用例必须使用用户级定位：`getByRole`、`getByLabel`、`getByPlaceholder`、`getByText`、`getByTestId`
- 禁止在 canonical E2E 用例中继续引入原始 CSS 选择器，如 `page.locator(...)`
- 临时遗留例外由 `npm run test:e2e:selectors` 的显式 allowlist 管理，范围只能缩小，不能扩张
- 遇到图表 `canvas/svg` 等无语义节点时，优先补 `data-testid`；确实无法避免时，必须行内标注 `e2e-selector-exception`

## 测试验证标准

### ✅ 通过标准
- **Phase 1**: 所有前置检查通过
- **Phase 2**: 页面完全加载，无控制台错误，所有核心元素存在
- **Phase 3**: API 返回有效数据，前后端数据一致
- **Phase 4**: 用户交互正常响应，无 JavaScript 崩溃

### ❌ 失败处理
- **问题分类**: 前端加载问题 / 后端接口问题 / 前后端联动问题
- **证据收集**: 自动截图 + 录屏 + 详细错误日志
- **报告输出**: 结构化 JSON + 人类可读摘要

## 故障排查

### 前置检查失败
```bash
# 检查 PM2 服务状态
pm2 list

# 检查端口占用
lsof -i :3020
lsof -i :8020

# 启动服务 (如果未运行)
cd web/frontend && npm run pm2:start
cd web/backend && pm2 start ecosystem.config.js
```

### 测试执行失败
```bash
# 查看详细错误日志
cat test-results/e2e-test-report.json | jq '.categories'

# 调试模式运行（npm 为主）
npm run test:e2e:debug

# npx 补充：单文件/grep 临时调试
npx playwright test tests/comprehensive-e2e-validation.spec.ts --debug
npx playwright test --grep "DOM元素存在性验证"
```

### 资源加载问题
- 检查前端构建是否完整 (`npm run build`)
- 验证静态资源路径
- 检查网络连接和 CDN 访问

### Lighthouse 启动失败
```bash
# 检查隔离 preview 端口是否被占用
lsof -i :4273

# 重新执行隔离性能 smoke
npm run test:e2e:lighthouse
```

说明：
- 若 `LHCI` 失败且日志包含 Chrome profile / ProcessSingleton 错误，优先确认脚本是否仍使用 Playwright Chromium 路径。
- 若 `LHCI` 失败且日志包含端口占用，优先释放 `4273`，不要停共享 PM2 的 `3020/8020` 服务。

## 性能指标

- **测试执行时间**: ~3-5 分钟 (完整套件)
- **资源占用**: 浏览器实例 + 网络监控
- **稳定性**: 99%+ 成功率 (服务正常时)
- **可维护性**: 模块化设计，易于扩展

## 扩展开发

### 添加新的测试用例
```typescript
test('自定义测试场景', async ({ page }) => {
  // 测试逻辑
  const startTime = Date.now();

  // 执行测试步骤
  await page.goto('...');
  // ... 测试逻辑 ...

  // 记录结果
  recordTestResult('custom', 'Custom Test Name', success, {
    duration: Date.now() - startTime,
    // 其他数据
  });

  expect(success).toBe(true);
});
```

### 修改测试配置
- 编辑 `playwright.config.js` 调整标准 E2E 超时、视口等
- 编辑 `playwright.config.ts` 调整 legacy 专项脚本配置
- 修改 `run-comprehensive-e2e.js` 调整服务配置
- 更新 `package.json` 添加新的 npm 脚本

## 技术栈

- **测试框架**: Playwright 1.57+
- **编程语言**: TypeScript
- **断言库**: Playwright Test (内置)
- **报告工具**: JSON + HTML + JUnit
- **CI/CD**: 支持 GitHub Actions, Jenkins 等

## 许可证

本测试套件遵循 MyStocks 项目许可证。
