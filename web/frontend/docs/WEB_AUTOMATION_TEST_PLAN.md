# Web自动化测试计划 (MyStocks Frontend)

## 📋 项目概述

本文档详细规划了MyStocks前端Web应用的自动化测试策略，包括测试范围、工具选择、实施路线图和最佳实践。

## 🎯 测试目标

### 主要目标
1. **功能完整性验证** - 确保所有页面和功能正常工作
2. **用户体验一致性** - 跨浏览器兼容性测试
3. **回归测试自动化** - 快速发现代码变更引入的问题
4. **性能监控** - 识别性能瓶颈和优化点
5. **可访问性测试** - 确保应用符合WCAG标准

### 业务目标
- 减少手动测试工作量80%
- 提高测试覆盖率至95%以上
- 缩短CI/CD反馈时间至5分钟以内
- 实现零生产环境功能性bug

## 🔍 当前测试现状分析

### 已完成的测试
- ✅ 菜单基础功能测试 (15个测试用例，100%通过)
- ✅ 路由导航测试
- ✅ Vue应用挂载测试
- ✅ 资源加载测试
- ✅ 多浏览器兼容性基础测试

### 测试覆盖率
- **页面覆盖率**: 6/53 (11.3%)
- **功能模块覆盖率**: 3/20 (15%)
- **API集成覆盖率**: 2/50 (4%)
- **组件测试覆盖率**: 0/200+ (0%)

## 📊 测试分层策略

### 1. 单元测试 (Unit Tests)
**范围**: 组件级别测试
- 工具: Vitest + Vue Test Utils
- 覆盖: 独立组件逻辑、工具函数、数据处理
- 目标覆盖率: 90%

```javascript
// 示例: menu-icon组件测试
describe('MenuIcon', () => {
  it('应该正确渲染图标', () => {
    const wrapper = mount(MenuIcon, { props: { icon: 'Dashboard' } })
    expect(wrapper.find('.el-icon').exists()).toBe(true)
  })
})
```

### 2. 集成测试 (Integration Tests)
**范围**: 组件间交互测试
- 工具: Vitest + Vue Test Utils + MSW
- 覆盖: 组件通信、状态管理、API集成

```javascript
// 示例: 菜单与路由集成测试
describe('Menu Navigation Integration', () => {
  it('点击菜单应该更新路由', async () => {
    const { getByText } = render(AppWithProviders)
    await fireEvent.click(getByText('仪表盘'))
    expect(window.location.pathname).toBe('/dashboard')
  })
})
```

### 3. E2E测试 (End-to-End Tests)
**范围**: 完整用户流程测试
- 工具: Playwright
- 覆盖: 用户故事、关键业务流程

```javascript
// 示例: 完整登录流程测试
test('用户登录流程', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[data-testid="username"]', 'testuser')
  await page.fill('[data-testid="password"]', 'password123')
  await page.click('[data-testid="login-button"]')
  await expect(page).toHaveURL('/dashboard')
})
```

## 🧪 详细测试计划

### Phase 1: 核心功能测试 (Week 1)

#### 1.1 导航系统测试
- [x] 菜单渲染和显示
- [x] 路由跳转
- [ ] 面包屑导航
- [ ] 页面标题更新
- [ ] 浏览器前进/后退
- [ ] 路由守卫验证

#### 1.2 认证系统测试
- [ ] 登录表单验证
- [ ] 密码强度检查
- [ ] JWT token处理
- [ ] 自动登录功能
- [ ] 登出功能
- [ ] 会话超时处理

#### 1.3 仪表盘功能测试
- [ ] 数据加载状态
- [ ] 图表渲染
- [ ] 实时数据更新
- [ ] 响应式布局
- [ ] 数据筛选功能
- [ ] 导出功能

### Phase 2: 业务模块测试 (Week 2-3)

#### 2.1 股票管理模块
```javascript
// 测试用例示例
describe('股票管理', () => {
  test('搜索股票', async ({ page }) => {
    await page.goto('/stocks')
    await page.fill('[data-testid="search-input"]', 'AAPL')
    await page.click('[data-testid="search-button"]')
    await expect(page.locator('[data-testid="stock-item-AAPL"]')).toBeVisible()
  })

  test('添加到自选股', async ({ page }) => {
    // 完整的添加自选股流程
  })

  test('查看股票详情', async ({ page }) => {
    // K线图、技术指标等
  })
})
```

#### 2.2 技术分析模块
- [ ] K线图交互
- [ ] 技术指标选择
- [ ] 时间周期切换
- [ ] 绘图工具
- [ ] 图表导出

#### 2.3 策略回测模块
- [ ] 策略配置
- [ ] 参数调整
- [ ] 回测执行
- [ ] 结果分析
- [ ] 报告生成

### Phase 3: 高级测试场景 (Week 4)

#### 3.1 性能测试
```javascript
// 性能测试示例
test.describe('性能测试', () => {
  test('首页加载性能', async ({ page }) => {
    const startTime = Date.now()
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    const loadTime = Date.now() - startTime
    expect(loadTime).toBeLessThan(3000) // 3秒内加载完成
  })

  test('大数据表格渲染性能', async ({ page }) => {
    // 测试1000+行数据的渲染性能
  })
})
```

#### 3.2 错误处理测试
- [ ] 网络中断处理
- [ ] API错误响应
- [ ] 数据加载失败
- [ ] 404页面
- [ ] 服务器错误

#### 3.3 可访问性测试
```javascript
// 可访问性测试示例
test('键盘导航', async ({ page }) => {
  await page.goto('/')
  await page.keyboard.press('Tab')
  await expect(page.locator(':focus')).toBeVisible()
  // 测试所有可交互元素的键盘访问
})
```

## 🛠️ 测试工具链配置

### 1. 测试框架配置

#### package.json更新
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:debug": "playwright test --debug"
  },
  "devDependencies": {
    "vitest": "^1.0.0",
    "@vue/test-utils": "^2.0.0",
    "jsdom": "^23.0.0",
    "msw": "^2.0.0",
    "@playwright/test": "^1.40.0",
    "@testing-library/vue": "^8.0.0"
  }
}
```

#### Vitest配置 (vitest.config.js)
```javascript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        'src/main.js'
      ]
    }
  }
})
```

### 2. Mock服务配置

#### MSW设置 (tests/setup.js)
```javascript
import { setupServer } from 'msw/node'
import { beforeAll, afterAll, afterEach } from 'vitest'

// 定义API mock
const handlers = [
  rest.get('/api/stocks/:symbol', (req, res, ctx) => {
    return res(ctx.json({
      symbol: req.params.symbol,
      price: 150.25,
      change: 2.50
    }))
  })
]

export const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

### 3. 测试工具函数

#### 自定义测试工具 (tests/utils/test-utils.js)
```javascript
import { render } from '@testing-library/vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'

export function renderWithProviders(component, options = {}) {
  const router = createRouter({
    history: createWebHistory(),
    routes: options.routes || []
  })

  const pinia = createPinia()

  return render(component, {
    global: {
      plugins: [router, pinia]
    },
    ...options
  })
}
```

## 📝 测试用例模板

### 1. 组件测试模板

```javascript
// tests/components/ComponentName.spec.js
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ComponentName from '@/components/ComponentName.vue'

describe('ComponentName', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(ComponentName, {
      props: {
        // 初始props
      }
    })
  })

  it('应该正确渲染', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('应该响应用户交互', async () => {
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted()).toHaveProperty('click')
  })
})
```

### 2. E2E测试模板

```javascript
// tests/e2e/feature-name.spec.js
import { test, expect } from '@playwright/test'

test.describe('功能名称', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/feature-page')
  })

  test('基础功能测试', async ({ page }) => {
    // 测试步骤
  })

  test('边界情况测试', async ({ page }) => {
    // 边界情况
  })
})
```

## 📊 测试报告和指标

### 1. 覆盖率指标
- **语句覆盖率**: ≥ 90%
- **分支覆盖率**: ≥ 85%
- **函数覆盖率**: ≥ 95%
- **行覆盖率**: ≥ 90%

### 2. 性能指标
- **首屏加载时间**: < 3秒
- **交互响应时间**: < 100ms
- **LCP (Largest Contentful Paint)**: < 2.5秒
- **FID (First Input Delay)**: < 100ms

### 3. 测试报告生成

#### HTML覆盖率报告
```bash
npm run test:coverage
# 生成覆盖率报告到 coverage/index.html
```

#### Playwright HTML报告
```bash
npm run test:e2e -- --reporter=html
# 生成可视化测试报告
```

## 🚀 CI/CD集成

### 1. GitHub Actions工作流

```yaml
# .github/workflows/test.yml
name: 测试流水线

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - uses: actions/checkout@v4

      - name: 设置Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: 安装依赖
        run: npm ci

      - name: 运行单元测试
        run: npm run test:coverage

      - name: 上传覆盖率到Codecov
        uses: codecov/codecov-action@v3

      - name: 安装Playwright
        run: npx playwright install --with-deps

      - name: 运行E2E测试
        run: npm run test:e2e
```

### 2. 本地预提交钩子

```json
// package.json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged && npm run test",
      "pre-push": "npm run test:e2e"
    }
  },
  "lint-staged": {
    "*.{js,vue}": [
      "eslint --fix",
      "git add"
    ]
  }
}
```

## 📋 实施计划时间线

### Week 1: 基础设施搭建
- [x] 设置测试环境
- [x] 配置Playwright
- [x] 编写首批测试用例
- [ ] 设置测试覆盖率
- [ ] 配置CI/CD

### Week 2: 核心模块测试
- [ ] 导航系统完整测试
- [ ] 认证流程测试
- [ ] 仪表盘功能测试
- [ ] API集成测试

### Week 3: 业务模块测试
- [ ] 股票管理模块
- [ ] 技术分析模块
- [ ] 策略回测模块
- [ ] 数据可视化测试

### Week 4: 高级测试和优化
- [ ] 性能测试
- [ ] 可访问性测试
- [ ] 错误处理测试
- [ ] 测试报告优化

## 🔧 测试最佳实践

### 1. 测试命名规范
- 使用描述性的测试名称
- 采用"应该/Should"格式
- 包含测试条件

```javascript
✅ 好的命名:
test('当用户点击登录按钮时，应该显示加载状态')
test('如果网络请求失败，应该显示错误消息')

❌ 避免的命名:
test('测试登录')
test('按钮点击')
```

### 2. 测试组织结构
```
tests/
├── unit/           # 单元测试
│   ├── components/
│   ├── composables/
│   └── utils/
├── integration/    # 集成测试
│   ├── api/
│   └── workflows/
├── e2e/           # E2E测试
│   ├── auth/
│   ├── dashboard/
│   └── stocks/
├── fixtures/      # 测试数据
├── utils/         # 测试工具
└── setup/         # 测试配置
```

### 3. 测试数据管理
- 使用工厂模式创建测试数据
- 避免硬编码测试数据
- 清理测试产生的数据

```javascript
// tests/factories/stockFactory.js
export function createStock(overrides = {}) {
  return {
    symbol: 'AAPL',
    name: 'Apple Inc.',
    price: 150.25,
    change: 2.50,
    ...overrides
  }
}
```

### 4. 测试断言最佳实践
- 使用精确的断言而非通用断言
- 检查UI状态而非实现细节
- 使用有意义的错误消息

```javascript
✅ 好的断言:
expect(messageElement).toHaveText('登录成功')
expect(page.locator('.error')).toHaveCount(0)

❌ 避免的断言:
expect(messageElement.text()).toContain('成功')
expect(errorElement).toBeNull()
```

## 📈 成功指标

### 短期目标 (1个月)
- [ ] 测试覆盖率达到80%
- [ ] E2E测试用例数达到100+
- [ ] CI/CD运行时间<10分钟
- [ ] 零生产环境功能性bug

### 中期目标 (3个月)
- [ ] 测试覆盖率达到90%
- [ ] 自动化测试替代80%手动测试
- [ ] 测试维护成本降低50%
- [ ] 平均缺陷修复时间<1天

### 长期目标 (6个月)
- [ ] 实现测试左移（测试在开发阶段进行）
- [ ] 建立性能基准和监控
- [ ] 实现AI辅助测试用例生成
- [ ] 建立测试数据治理体系

## 🔄 持续改进

### 1. 定期回顾
- 每周测试执行报告
- 测试失败率分析
- 测试维护成本评估
- 团队反馈收集

### 2. 测试优化
- 识别慢速测试并优化
- 重构重复的测试代码
- 改进测试数据管理
- 更新测试工具和版本

### 3. 知识分享
- 测试最佳实践文档
- 团队培训和分享
- 测试用例评审
- 跨团队经验交流

---

**文档版本**: 1.0
**最后更新**: 2025-12-06
**负责人**: 开发团队
**审核人**: QA Lead
