# API-Web 集成项目验收标准 (Acceptance Standards)

**版本**: 2.0
**创建日期**: 2025-12-25
**适用范围**: 所有 API-Web 对齐 Phase（Phase 1-4）
**目标**: 确保每个 Phase 不仅是"代码完成"，而是"真正可用、稳定、且用户体验良好"

---

## 📋 目录

1. [第一层：代码交付物验收](#第一层代码交付物验收)
2. [第二层：E2E 功能验证](#第二层e2e-功能验证)
3. [第三层：用户体验验收](#第三层用户体验验收)
4. [第四层：运维友好性验收](#第四层运维友好性验收)
5. [验收流程](#验收流程)
6. [快速验收检查命令](#快速验收检查命令)

---

## 第一层：代码交付物验收

### 📦 核心交付物清单（必需）

每个 Phase 必须完成以下 **6 类文件**：

#### 1. TypeScript 类型定义
**文件**: `web/frontend/src/api/types/[module].ts`

**验收标准**:
- ✅ 完整的类型接口定义（200+ LOC）
- ✅ 枚举类型定义
- ✅ 请求/响应类型（与后端 API 对齐）
- ✅ JSDoc 注释完整

**示例**:
```typescript
/**
 * 策略实体
 */
export interface Strategy {
  id: string;
  name: string;
  type: StrategyType;      // 枚举
  status: StrategyStatus;  // 枚举
  performance?: StrategyPerformance;
}
```

#### 2. API 服务层
**文件**: `web/frontend/src/api/services/[module]Service.ts`

**验收标准**:
- ✅ 18+ 个 API 方法（策略模块标准）
- ✅ 完整的 CRUD 操作
- ✅ WebSocket 订阅方法（如需要）
- ✅ 返回 UnifiedResponse<T> 类型
- ✅ 完整的 JSDoc 注释

#### 3. 数据适配器
**文件**: `web/frontend/src/api/adapters/[module]Adapter.ts`

**验收标准**:
- ✅ API 响应转换为前端格式
- ✅ **Mock 数据自动降级策略**
- ✅ snake_case 和 camelCase 兼容
- ✅ 数据验证逻辑
- ✅ 单元测试覆盖率 > 80%

**核心方法**:
```typescript
class StrategyAdapter {
  static adaptStrategyList(
    apiResponse: UnifiedResponse<StrategyListResponse>
  ): Strategy[] {
    // 1. 检查 API 成功
    if (!apiResponse.success) {
      // 2. 自动降级到 Mock
      return mockStrategyList.strategies;
    }
    // 3. 转换数据
    return apiResponse.data.strategies.map(adapt);
  }
}
```

#### 4. Vue Composable
**文件**: `web/frontend/src/composables/use[Module].ts`

**验收标准**:
- ✅ 响应式状态管理（ref + readonly）
- ✅ 自动数据获取（onMounted）
- ✅ 完整的错误处理
- ✅ 用户友好的错误提示（中文）
- ✅ 加载状态管理

#### 5. Vue 组件
**文件**: `web/frontend/src/components/[Module].vue`

**验收标准**:
- ✅ 主页面组件
- ✅ 功能组件（卡片、对话框、面板等）
- ✅ Props down, Events up 模式
- ✅ 响应式布局（桌面/平板/手机）
- ✅ 完整的 TypeScript 类型定义

#### 6. 单元测试
**文件**: `web/frontend/src/api/__tests__/[module].test.ts`

**验收标准**:
- ✅ 测试覆盖率 > 80%
- ✅ 适配器测试（成功 + 降级场景）
- ✅ 验证逻辑测试
- ✅ 边界条件测试
- ✅ Mock 数据集成测试

---

## 第二层：E2E 功能验证

### 🌐 端到端用户旅程测试

#### 工具选择：Playwright
**推荐理由**:
- ✅ 多浏览器支持（Chrome, Firefox, WebKit, Edge）
- ✅ 强大的自动等待机制
- ✅ 网络拦截和 mock 能力
- ✅ 优秀的 TypeScript 支持
- ✅ 并行执行提升测试速度

**安装配置**:
```bash
cd web/frontend
npm install -D @playwright/test
npx playwright install
```

#### 核心用户旅程（Core User Journeys）

##### 1. 身份认证旅程
**测试场景**: 用户登录/登出流程

```typescript
// tests/e2e/auth-journey.spec.ts
import { test, expect } from '@playwright/test';

test.describe('身份认证旅程', () => {
  test('完整登录流程', async ({ page }) => {
    // 1. 访问登录页
    await page.goto('http://localhost:3001/login');

    // 2. 输入凭证
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'password123');

    // 3. 提交表单
    await page.click('[data-testid="login-button"]');

    // 4. 验证跳转到仪表板
    await expect(page).toHaveURL('http://localhost:3001/dashboard');

    // 5. 验证用户信息显示
    await expect(page.locator('[data-testid="user-avatar"]')).toBeVisible();

    // 6. 验证 JWT Token 存储在 localStorage
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token).toBeTruthy();

    // 7. 验证后续 API 请求携带 Authorization header
    const [apiRequest] = await Promise.all([
      page.waitForRequest(req =>
        req.url().includes('/api/strategy/list') &&
        req.headers()['authorization']
      ),
      page.goto('http://localhost:3001/strategy')
    ]);
    expect(apiRequest).toBeTruthy();
  });
});
```

##### 2. 数据展示旅程
**测试场景**: 用户访问页面，验证数据正确展示

```typescript
// tests/e2e/strategy-display.spec.ts
test.describe('策略数据展示', () => {
  test('策略列表正确加载和展示', async ({ page }) => {
    // 1. 登录
    await login(page);

    // 2. 访问策略管理页面
    await page.goto('http://localhost:3001/strategy');

    // 3. 等待数据加载（自动等待策略卡片出现）
    await expect(page.locator('.strategy-card')).toHaveCount(4, { timeout: 5000 });

    // 4. 验证第一个策略卡片数据
    const firstCard = page.locator('.strategy-card').first();

    await expect(firstCard.locator('.strategy-name')).toContainText('双均线趋势跟踪');
    await expect(firstCard.locator('.status-badge.active')).toContainText('运行中');
    await expect(firstCard.locator('.metric .value')).toContainText('25.60%');

    // 5. 截取网络请求，验证 API 返回数据
    const apiResponse = await page.evaluate(async () => {
      const response = await fetch('/api/strategy/list');
      return response.json();
    });

    expect(apiResponse.success).toBe(true);
    expect(apiResponse.data.strategies).toHaveLength(4);
    expect(apiResponse.data.strategies[0].name).toBe('双均线趋势跟踪');

    // 6. 验证前端展示数据与 API 数据一致
    const displayName = await firstCard.locator('.strategy-name').textContent();
    expect(displayName).toBe(apiResponse.data.strategies[0].name);
  });
});
```

##### 3. CRUD 操作旅程
**测试场景**: 创建 → 编辑 → 删除策略

```typescript
// tests/e2e/strategy-crud.spec.ts
test.describe('策略 CRUD 操作', () => {
  test('完整 CRUD 流程', async ({ page }) => {
    await login(page);
    await page.goto('http://localhost:3001/strategy');

    // === 创建策略 ===
    await page.click('[data-testid="create-strategy-button"]');

    // 填写表单
    await page.fill('[data-testid="strategy-name"]', 'E2E 测试策略');
    await page.selectOption('[data-testid="strategy-type"]', 'momentum');
    await page.fill('[data-testid="strategy-description"]', '自动化测试创建的策略');

    // 动态添加参数
    await page.click('[data-testid="add-param-button"]');
    await page.fill('[data-testid="param-key-0"]', 'lookback_period');
    await page.fill('[data-testid="param-value-0"]', '20');

    // 提交
    await page.click('[data-testid="save-strategy-button"]');

    // 验证创建成功
    await expect(page.locator('.strategy-card')).toHaveCount(5);
    await expect(page.locator('text=E2E 测试策略')).toBeVisible();

    // === 编辑策略 ===
    const newCard = page.locator('.strategy-card').filter({ hasText: 'E2E 测试策略' });
    await newCard.locator('[data-testid="edit-button"]').click();

    // 修改数据
    await page.fill('[data-testid="strategy-name"]', 'E2E 测试策略（已修改）');
    await page.click('[data-testid="save-strategy-button"]');

    // 验证修改成功
    await expect(newCard.locator('.strategy-name')).toContainText('已修改');

    // === 删除策略 ===
    page.on('dialog', dialog => dialog.accept()); // 确认删除对话框
    await newCard.locator('[data-testid="delete-button"]').click();

    // 验证删除成功
    await expect(page.locator('.strategy-card')).toHaveCount(4);
    await expect(page.locator('text=E2E 测试策略')).not.toBeVisible();
  });
});
```

##### 4. 复杂交互流
**测试场景**: 多页面/多组件协作

```typescript
// tests/e2e/backtest-workflow.spec.ts
test.describe('回测工作流', () => {
  test('从列表到回测结果的完整流程', async ({ page }) => {
    await login(page);
    await page.goto('http://localhost:3001/strategy');

    // 1. 从策略列表选择策略
    const strategyCard = page.locator('.strategy-card').first();
    const strategyName = await strategyCard.locator('.strategy-name').textContent();

    // 2. 点击"回测"按钮
    await strategyCard.locator('[data-testid="backtest-button"]').click();

    // 3. 验证回测面板打开
    await expect(page.locator('.backtest-panel')).toBeVisible();
    await expect(page.locator('[data-testid="backtest-strategy-name"]'))
      .toContainText(strategyName);

    // 4. 配置回测参数
    await page.fill('[data-testid="start-date"]', '2024-01-01');
    await page.fill('[data-testid="end-date"]', '2024-12-31');
    await page.fill('[data-testid="initial-capital"]', '100000');

    // 5. 启动回测
    await page.click('[data-testid="start-backtest-button"]');

    // 6. 验证进度视图
    await expect(page.locator('.backtest-progress')).toBeVisible();
    await expect(page.locator('.progress-bar')).toHaveAttribute('value', '100', { timeout: 10000 });

    // 7. 验证结果视图
    await expect(page.locator('.backtest-results')).toBeVisible();
    await expect(page.locator('[data-testid="total-return"]')).toContainText('%');
    await expect(page.locator('[data-testid="sharpe-ratio"]')).toBeVisible();

    // 8. 验证性能指标计算正确
    const totalReturn = await page.locator('[data-testid="total-return"]').textContent();
    expect(parseFloat(totalReturn)).toBeGreaterThan(0);
  });
});
```

### 🔍 实时数据校验

#### 数据一致性验证
```typescript
test('前端展示数据与 API 返回数据一致', async ({ page }) => {
  await login(page);
  await page.goto('http://localhost:3001/strategy');

  // 1. 拦截 API 响应
  let apiData: any;
  page.on('response', async (response) => {
    if (response.url().includes('/api/strategy/list')) {
      apiData = await response.json();
    }
  });

  // 2. 等待页面加载
  await page.waitForLoadState('networkidle');

  // 3. 验证时间戳一致性（时间戳可能有时区差异）
  const apiTimestamp = apiData.data.strategies[0].createdAt;
  const uiTimestamp = await page.locator('.strategy-card .date').first().textContent();

  // 4. 验证数值精度
  const apiReturn = apiData.data.strategies[0].performance.totalReturn;
  const uiReturn = await page.locator('.strategy-card .metric .value').first().textContent();
  expect(parseFloat(uiReturn)).toBeCloseTo(apiReturn * 100, 2);
});
```

### 🎯 控件对齐验证

#### 表单控件与 API 参数对齐
```typescript
test('筛选控件与 API 参数对齐', async ({ page }) => {
  await login(page);
  await page.goto('http://localhost:3001/strategy');

  // 1. 设置筛选条件
  await page.selectOption('[data-testid="status-filter"]', 'active');
  await page.selectOption('[data-testid="type-filter"]', 'trend_following');

  // 2. 拦截 API 请求
  let apiParams: URLSearchParams;
  page.on('request', (request) => {
    if (request.url().includes('/api/strategy/list')) {
      const url = new URL(request.url());
      apiParams = url.searchParams;
    }
  });

  // 3. 触发筛选
  await page.click('[data-testid="apply-filter-button"]');

  // 4. 验证 API 参数
  await expect(apiParams.get('status')).toBe('active');
  await expect(apiParams.get('type')).toBe('trend_following');

  // 5. 验证 UI 只显示符合条件的策略
  const visibleCards = page.locator('.strategy-card');
  await expect(visibleCards).toHaveCountGreaterThan(0);

  for (const card of await visibleCards.all()) {
    await expect(card.locator('.status-badge.active')).toBeVisible();
  }
});
```

---

## 第三层：用户体验验收

### ⚠️ 异常场景的 UI 反馈与恢复

#### 1. 友好的错误展示

##### 网络错误场景
```typescript
test.describe('异常场景处理', () => {
  test('网络中断时显示友好错误', async ({ page }) => {
    await login(page);

    // 1. 模拟网络离线
    await page.context().setOffline(true);

    // 2. 尝试加载数据
    await page.goto('http://localhost:3001/strategy');

    // 3. 验证错误提示（非白屏/崩溃）
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText('网络连接失败');

    // 4. 验证重试按钮存在
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();

    // 5. 验证 Mock 数据降级显示
    await expect(page.locator('.strategy-card')).toHaveCount(4); // Mock 数据

    // 6. 恢复网络
    await page.context().setOffline(false);

    // 7. 点击重试
    await page.click('[data-testid="retry-button"]');

    // 8. 验证重新加载成功
    await expect(page.locator('.error-message')).not.toBeVisible();
    await expect(page.locator('.strategy-card')).toHaveCount(4);
  });
});
```

##### API 错误场景
```typescript
test('401 未认证时自动弹出登录框', async ({ page }) => {
  // 1. 清除 token
  await page.evaluate(() => localStorage.removeItem('access_token'));

  // 2. 访问需要认证的页面
  await page.goto('http://localhost:3001/strategy');

  // 3. 验证自动跳转到登录页或弹出登录框
  await expect(page).toHaveURL(/\/login/, { timeout: 5000 });
  // 或者：await expect(page.locator('.login-modal')).toBeVisible();

  // 4. 验证错误提示
  await expect(page.locator('.error-message')).toContainText('登录已过期');
});

test('403 无权限时显示权限不足提示', async ({ page }) => {
  await login(page, 'limited_user'); // 使用权限不足的用户

  // 1. 尝试访问管理功能
  await page.goto('http://localhost:3001/admin');

  // 2. 验证权限提示
  await expect(page.locator('.error-message')).toContainText('权限不足');
  await expect(page.locator('.error-message .icon')).toHaveClass(/lock/);
});

test('500 服务器错误时显示友好提示', async ({ page, context }) => {
  // 1. Mock 500 错误响应
  await page.route('**/api/strategy/list', route => {
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({
        success: false,
        code: 500,
        message: '服务器内部错误',
        timestamp: new Date().toISOString(),
        request_id: 'test-req-123',
        errors: { detail: 'Database connection failed' }
      })
    });
  });

  await login(page);
  await page.goto('http://localhost:3001/strategy');

  // 2. 验证错误展示
  await expect(page.locator('.error-message')).toBeVisible();
  await expect(page.locator('.error-message')).toContainText('服务器内部错误');

  // 3. 验证 request_id 显示（用于日志追溯）
  await expect(page.locator('.error-message')).toContainText('test-req-123');
});
```

##### 422 参数验证失败
```typescript
test('422 参数验证失败时显示具体错误', async ({ page }) => {
  await login(page);
  await page.goto('http://localhost:3001/strategy');

  // 1. 点击创建策略
  await page.click('[data-testid="create-strategy-button"]');

  // 2. 提交空表单（触发验证）
  await page.click('[data-testid="save-strategy-button"]');

  // 3. 验证字段级错误提示
  await expect(page.locator('[data-testid="name-error"]')).toBeVisible();
  await expect(page.locator('[data-testid="name-error"]'))
    .toContainText('策略名称不能为空');

  // 4. 验证错误样式
  await expect(page.locator('[data-testid="strategy-name"]'))
    .toHaveClass(/error/);
});
```

#### 2. 日志可追溯性验证

```typescript
test('错误日志包含 request_id', async ({ page }) => {
  // 1. 监听 console.error
  const errors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  // 2. 触发 API 错误
  await page.route('**/api/strategy/list', route => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({
        success: false,
        code: 500,
        message: 'Server error',
        timestamp: new Date().toISOString(),
        request_id: 'trace-abc-123',
        errors: null
      })
    });
  });

  await login(page);
  await page.goto('http://localhost:3001/strategy');

  // 3. 验证错误日志包含 request_id
  const errorLog = errors.find(e => e.includes('trace-abc-123'));
  expect(errorLog).toBeTruthy();
});
```

### 🖥️ 跨浏览器兼容性（桌面端）

**项目范围**: 本项目仅限电脑端运行使用（不包含平板和手机设备）

#### 1. 主流桌面浏览器测试
```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'edge',
      use: {
        channel: 'msedge',
        viewport: { width: 1920, height: 1080 },
      },
    },
  ],
});
```

**测试命令**:
```bash
# 在所有桌面浏览器运行测试
npx playwright test

# 仅在特定浏览器运行
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

#### 2. 桌面布局验证
```typescript
// tests/e2e/desktop-layout.spec.ts
test.describe('桌面端布局验证', () => {
  const desktopViewports = [
    { width: 1920, height: 1080, name: 'Full HD' },
    { width: 1680, height: 1050, name: 'Widescreen' },
    { width: 1440, height: 900, name: 'Laptop' },
    { width: 1366, height: 768, name: 'Small Laptop' },
  ];

  for (const viewport of desktopViewports) {
    test(`${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await login(page);
      await page.goto('http://localhost:3001/strategy');

      // 验证网格布局正确显示
      await expect(page.locator('.strategy-grid')).toBeVisible();

      // 验证策略卡片在视口内可见
      const firstCard = page.locator('.strategy-card').first();
      await expect(firstCard).toBeInViewport();

      // 验证所有按钮可点击（鼠标交互）
      await expect(firstCard.locator('[data-testid="edit-button"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="backtest-button"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="delete-button"]')).toBeVisible();
    });
  }
});
```

---

## 第四层：运维友好性验收

### ✅ 部署后功能验证（Smoke Testing）

#### 冒烟测试套件
```typescript
// tests/e2e/smoke.spec.ts
test.describe('冒烟测试 - 关键功能验证', () => {
  test('核心功能快速验证', async ({ page }) => {
    // 1. 页面加载
    await page.goto('http://localhost:3001');
    await expect(page).toHaveTitle(/MyStocks/);

    // 2. 健康检查
    const healthResponse = await page.evaluate(async () => {
      const response = await fetch('/health');
      return response.json();
    });
    expect(healthResponse.status).toBe('healthy');

    // 3. 关键数据加载
    await login(page);
    await page.goto('http://localhost:3001/strategy');
    await expect(page.locator('.strategy-card')).toHaveCount(4);

    // 4. 基本操作
    await page.click('[data-testid="create-strategy-button"]');
    await expect(page.locator('.strategy-dialog')).toBeVisible();
    await page.click('[data-testid="cancel-button"]');

    // 执行时间 < 30 秒
  });
});
```

#### CI/CD 集成
```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: |
          cd web/frontend
          npm ci
          npx playwright install --with-deps

      - name: Install Playwright Browsers
        run: npx playwright install --with-deps

      - name: Run Playwright tests
        run: |
          cd web/frontend
          npx playwright test

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: web/frontend/playwright-report/
          retention-days: 30
```

---

## 验收流程

### Phase 完整验收流程

#### 阶段 1: 自验（开发者）
```bash
# 1. 代码质量检查
npm run lint
npm run type-check
npm run test:unit

# 2. 本地 E2E 测试
npx playwright test

# 3. 性能验证
npm run test:performance
```

#### 阶段 2: 代码审查（Code Review）
- [ ] 所有交付物文件已完成
- [ ] TypeScript 类型定义完整
- [ ] 错误处理逻辑完善
- [ ] Mock 降级策略正确
- [ ] 单元测试覆盖率 > 80%

#### 阶段 3: E2E 测试验证（QA）
```bash
# 在多个浏览器运行
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# 响应式测试
npx playwright test --project=mobile
```

#### 阶段 4: 部署验证（Dev/Staging）
```bash
# 1. 部署到测试环境
npm run deploy:dev

# 2. 运行冒烟测试
npx playwright test --grep @smoke

# 3. 性能验证
npm run lighthouse
```

#### 阶段 5: 最终验收（产品负责人）
- [ ] 所有核心用户旅程测试通过
- [ ] 异常场景处理正确
- [ ] 跨浏览器兼容性验证通过
- [ ] 响应式布局适配正确
- [ ] 性能指标达标
- [ ] 文档更新完整

---

## 快速验收检查命令

### 一键验收脚本

```bash
#!/bin/bash
# scripts/acceptance-test.sh

set -e

echo "🚀 开始验收测试..."

# 1. 代码质量
echo "📦 检查代码质量..."
cd web/frontend
npm run lint
npm run type-check

# 2. 单元测试
echo "🧪 运行单元测试..."
npm run test:unit -- --coverage

# 3. E2E 测试
echo "🌐 运行 E2E 测试..."
npx playwright test

# 4. 性能测试
echo "⚡ 运行性能测试..."
npx playwright test --grep @performance

# 5. 生成报告
echo "📊 生成测试报告..."
npx playwright show-report

echo "✅ 验收测试完成！"
```

### 验收检查清单

#### 第一层：代码交付物
```bash
# 检查文件完整性
ls -la src/api/types/           # 应包含 [module].ts
ls -la src/api/services/        # 应包含 [module]Service.ts
ls -la src/api/adapters/        # 应包含 [module]Adapter.ts
ls -la src/composables/         # 应包含 use[Module].ts
ls -la src/components/          # 应包含 [Module].vue
ls -la src/api/__tests__/       # 应包含 [module].test.ts

# 检查测试覆盖率
npm run test:coverage
# 验证: Coverage > 80%
```

#### 第二层：E2E 功能
```bash
# 核心用户旅程测试
npx playwright test --grep @journey

# 数据一致性验证
npx playwright test --grep @data-consistency

# 控件对齐验证
npx playwright test --grep @alignment
```

#### 第三层：用户体验
```bash
# 异常场景测试
npx playwright test --grep @error

# 跨浏览器测试
npx playwright test --project=all

# 响应式测试
npx playwright test --grep @responsive
```

#### 第四层：运维友好
```bash
# 冒烟测试
npx playwright test --grep @smoke

# 性能测试
npx playwright test --grep @performance
```

---

## 📊 验收标准评分

### 评分标准

| 层级 | 权重 | 及格分 | 优秀分 |
|------|------|--------|--------|
| 第一层：代码交付物 | 25% | 80% | 95% |
| 第二层：E2E 功能 | 30% | 75% | 90% |
| 第三层：用户体验 | 25% | 75% | 90% |
| 第四层：运维友好 | 20% | 70% | 85% |
| **总计** | **100%** | **75%** | **90%** |

### 计算示例

**Phase 2 验收评分**:
```
第一层: 25/25 = 100% (代码完整、类型安全、测试覆盖 >80%)
第二层: 25/30 = 83%  (核心旅程测试通过、数据一致性验证完成)
第三层: 20/25 = 80%  (异常场景处理良好、响应式布局适配完成)
第四层: 15/20 = 75%  (冒烟测试通过、性能达标)

总分: 85/100 = 85% (✅ 优秀)
```

---

## 🎯 验收通过标准

### 必需项（Blocking Issues = 0）
- ❌ **阻塞性问题** = 0
  - 页面白屏/崩溃
  - 数据丢失/损坏
  - 安全漏洞
  - 性能严重不达标（> 2s 加载）

### 可选项（非阻塞）
- ⚠️ **优化建议**可以延后
  - UI 微调
  - 性能优化（已达标准但可更好）
  - 代码重构（不影响功能）

### 最终决策
- ✅ **通过**: 总分 ≥ 75% + 阻塞性问题 = 0
- ⏳ **条件通过**: 总分 ≥ 75% + 阻塞性问题 < 3（必须在 3 天内修复）
- ❌ **不通过**: 总分 < 75% 或 阻塞性问题 ≥ 3

---

## 📝 验收报告模板

```markdown
# Phase [N] 验收报告

**日期**: YYYY-MM-DD
**验收人**: [姓名]
**Phase**: [Phase Name]

## 验收结果

### 总体评分: XX/100 (✅ 通过 / ❌ 不通过)

### 第一层：代码交付物 (XX/25)
- ✅ / ❌ 类型定义完整
- ✅ / ❌ API 服务完整
- ✅ / ❌ 适配器实现正确
- ✅ / ❌ Composable 响应式
- ✅ / ❌ 组件完整
- ✅ / ❌ 单元测试覆盖率 > 80%

**扣分原因**: [具体问题]

### 第二层：E2E 功能 (XX/30)
- ✅ / ❌ 核心用户旅程测试通过
- ✅ / ❌ 数据一致性验证通过
- ✅ / ❌ 控件对齐验证通过
- ✅ / ❌ 实时数据校验通过

**扣分原因**: [具体问题]

### 第三层：用户体验 (XX/25)
- ✅ / ❌ 异常场景处理友好
- ✅ / ❌ 跨浏览器兼容性通过
- ✅ / ❌ 响应式布局适配正确
- ✅ / ❌ 日志可追溯性完整

**扣分原因**: [具体问题]

### 第四层：运维友好 (XX/20)
- ✅ / ❌ 冒烟测试通过
- ✅ / ❌ 性能指标达标
- ✅ / ❌ CI/CD 集成完成

**扣分原因**: [具体问题]

## 发现的问题

### 阻塞性问题 (必须修复)
1. [问题描述] - [优先级] - [预计修复时间]

### 优化建议 (可延后)
1. [问题描述] - [优先级]

## 测试环境
- 前端版本: [commit hash]
- 后端版本: [commit hash]
- 浏览器: [Chrome / Firefox / Safari 版本]
- 设备: [桌面 / 平板 / 手机]

## 附件
- E2E 测试报告: [链接]
- 性能测试报告: [链接]
- 截图证据: [文件夹]

## 签字确认
- 开发者: ____________  日期: ______
- QA 工程师: ____________  日期: ______
- 产品负责人: ____________  日期: ______
```

---

## 📚 相关文档

- [API 集成优化计划](./API_Integration_Optimization_Plan.md)
- [API 集成实施状态](./API_INTEGRATION_IMPLEMENTATION_STATUS.md)
- [Phase 2 完成报告](./PHASE2_COMPLETION_REPORT.md)
- [Playwright 官方文档](https://playwright.dev/)
- [前端开发指南](../guides/FRONTEND_DEV_GUIDELINES.md)

---

**文档所有者**: MyStocks Development Team
**最后更新**: 2025-12-25 17:30 UTC
**版本**: 2.0
**状态**: ✅ 已审核
