# Phase 2: 前端 E2E 测试框架 - 全面测试计划

**项目**: MyStocks 量化交易系统
**阶段**: Phase 2 - 前端页面 E2E 测试
**启动日期**: 2025-12-04
**目标完成日期**: 2025-12-08
**总体目标**: 为 P2 优先级页面（20+ 页面）创建全面的 E2E 测试框架

---

## 📊 执行概览

### 当前项目状态
- **P0 测试**: ✅ 完成 (135 个单元测试，90% 覆盖)
- **P1 测试**: ✅ 完成 (39 个 API 集成测试，100% 通过)
- **前端基础**: ✅ 已部署 (Vue 3 + TypeScript, 29 个 Vue 组件)
- **E2E 基础**: ✅ 配置完成 (Playwright 4.40+, 多浏览器支持)

### Phase 2 目标
| 指标 | 目标 | 优先级 |
|------|------|--------|
| E2E 测试数量 | 40+ 个测试用例 | 必须 |
| 覆盖页面数 | 10-15 个关键页面 | 必须 |
| 测试通过率 | >= 80% | 必须 |
| 代码覆盖率增长 | 从 27% → 35%+ | 优先 |
| 执行时间 | < 5 分钟 | 优先 |

---

## 🎯 P2 优先级页面分析

### 第一批优先级页面 (Tier 1: 核心业务流程)

#### 1. **Dashboard.vue** (仪表板)
**功能**: 系统首页，用户登录后的核心工作区
- 概览卡片 (总资产、当日收益、持仓数量)
- 实时行情小部件
- 策略运行状态
- 快速操作按钮

**关键测试场景**:
- ✅ 页面加载和初始化
- ✅ 数据刷新机制 (轮询/WebSocket)
- ✅ 响应式布局 (桌面/平板)
- ✅ 性能指标 (加载时间 < 2s)

**API 依赖**:
- `GET /api/dashboard/overview` - 概览数据
- `GET /api/portfolio/positions` - 持仓信息
- `WebSocket /ws/realtime` - 实时推送

**预期测试数**: 8-10 个

---

#### 2. **Market.vue** (行情中心)
**功能**: 股票行情查询、搜索、筛选
- 行情列表 (股票代码、价格、涨跌幅等)
- 搜索功能 (按代码/名称)
- 筛选器 (行业、涨幅范围等)
- 排序功能

**关键测试场景**:
- ✅ 页面加载和数据显示
- ✅ 搜索功能 (空值、特殊字符、模糊匹配)
- ✅ 筛选和排序交互
- ✅ 分页功能

**API 依赖**:
- `GET /api/market/overview` - 市场概览
- `GET /api/market/search?query=` - 搜索
- `GET /api/market/data?filter=` - 行情数据

**预期测试数**: 10-12 个

---

#### 3. **StockDetail.vue** (股票详情)
**功能**: 单只股票的详细信息和分析
- K线图表 (日线、分时、周线等)
- 技术指标 (MA, RSI, MACD 等)
- 基本面信息 (市盈率、市净率等)
- 交易执行表单

**关键测试场景**:
- ✅ 图表加载和交互
- ✅ 时间范围切换
- ✅ 指标添加/删除
- ✅ 交易表单验证

**API 依赖**:
- `GET /api/market/stock/{symbol}/detail` - 股票详情
- `GET /api/technical/chart/{symbol}?period=` - 图表数据
- `POST /api/trading/order` - 下单接口

**预期测试数**: 12-15 个

---

#### 4. **TechnicalAnalysis.vue** (技术分析)
**功能**: 技术分析工具和指标库
- 指标库 (161 个 TA-Lib 指标)
- 参数配置
- 信号输出
- 回测验证

**关键测试场景**:
- ✅ 指标搜索和过滤
- ✅ 参数输入和验证
- ✅ 指标组合和保存
- ✅ 性能测试 (大数据集)

**API 依赖**:
- `GET /api/technical/indicators/registry` - 指标库
- `POST /api/technical/calculate` - 指标计算
- `GET /api/technical/templates` - 保存的模板

**预期测试数**: 8-10 个

---

#### 5. **TradeManagement.vue** (交易管理)
**功能**: 订单管理、头寸管理、交易历史
- 持仓列表
- 活跃订单
- 交易历史
- 成本价计算

**关键测试场景**:
- ✅ 订单列表显示
- ✅ 订单操作 (平仓、修改、取消)
- ✅ 搜索和过滤
- ✅ 导出功能

**API 依赖**:
- `GET /api/trading/orders` - 订单列表
- `GET /api/portfolio/positions` - 持仓列表
- `POST /api/trading/order/{id}/close` - 平仓接口

**预期测试数**: 10-12 个

---

### 第二批优先级页面 (Tier 2: 辅助功能)

#### 6. **StrategyManagement.vue** (策略管理)
- 策略列表
- 参数配置
- 回测结果
- 部署/启停

**预期测试数**: 6-8 个

#### 7. **RiskMonitor.vue** (风险监控)
- 风险指标仪表板
- 告警规则
- 仓位占比
- 杠杆比率

**预期测试数**: 6-8 个

#### 8. **TaskManagement.vue** (任务管理)
- 任务列表
- 执行历史
- 日志查看
- 定时任务配置

**预期测试数**: 6-8 个

#### 9. **Settings.vue** (设置)
- 账户设置
- 通知配置
- API 密钥管理
- 界面偏好

**预期测试数**: 6-8 个

#### 10. **RealTimeMonitor.vue** (实时监控)
- 实时行情推送
- SSE 连接状态
- 性能指标
- 告警提示

**预期测试数**: 8-10 个

---

## 🛠️ E2E 测试框架设置

### 现有基础设施

**Playwright 配置**:
- 配置文件: `/opt/claude/mystocks_spec/playwright.config.ts`
- 测试目录: `/opt/claude/mystocks_spec/tests/`
- 报告目录: `/opt/claude/mystocks_spec/playwright-report/`

**现有测试**:
```
tests/
├── e2e/
│   ├── health-check.spec.js                           # 健康检查
│   ├── realtime-monitor-integration.spec.js           # 实时监控
│   ├── stock-detail-integration.spec.js               # 股票详情
│   ├── market-data-integration.spec.js                # 行情数据
│   ├── indicator-library-integration.spec.js          # 指标库
│   ├── wencai-integration.spec.js                     # 问财工具
│   ├── industry-concept-integration.spec.js           # 行业概念
│   └── risk-monitor-integration.spec.js               # 风险监控
├── setup.ts                                            # 全局 setup
├── simple-test.spec.ts
└── comprehensive-test.spec.ts
```

**报告**: `/opt/claude/mystocks_spec/docs/reports/E2E_TEST_REPORT_2025-11-26.md`
- 110 个测试用例
- 72-80% 通过率

### Phase 2 框架增强

#### 1. 测试助手库
**位置**: `/opt/claude/mystocks_spec/tests/helpers/`

**核心模块**:
```typescript
// helpers/page-objects.ts
export class DashboardPage { ... }
export class MarketPage { ... }
export class StockDetailPage { ... }
export class TechnicalAnalysisPage { ... }
export class TradeManagementPage { ... }

// helpers/api-helpers.ts
export async function setupMockData() { ... }
export async function waitForDataLoad(page) { ... }
export async function mockWebSocketConnection() { ... }

// helpers/test-fixtures.ts
export const dashboardTests = { ... }
export const marketTests = { ... }

// helpers/assertions.ts
export function assertPageLoaded(page) { ... }
export function assertDataDisplayed(element) { ... }
```

#### 2. 测试数据管理
**位置**: `/opt/claude/mystocks_spec/tests/fixtures/`

```yaml
# fixtures/test-data.yaml
mockStocks:
  - symbol: "000001"
    name: "平安银行"
    price: 10.5
    change: 2.5
  - symbol: "600000"
    name: "浦发银行"
    price: 8.2
    change: -1.2

mockChartData:
  - timestamp: "2025-12-04 09:30:00"
    open: 10.3
    high: 10.6
    low: 10.2
    close: 10.5
```

#### 3. 测试并行化
- 使用 Playwright 的 `workers` 配置 (建议 4-6 worker)
- 隔离测试数据 (每个测试独立 session)
- 避免测试间污染

---

## 📋 Phase 2 详细实施计划

### Week 1: 基础设施 & Tier 1 测试 (12 月 4-8 日)

#### Day 1-2: 准备工作 (12 月 4-5 日)
```
✓ 分析 29 个 Vue 组件依赖关系
✓ 创建 Page Object 模型 (5 个核心页面)
✓ 设计测试数据库和 mock 服务
✓ 配置 CI/CD E2E 测试流程
```

**成果物**:
- Page Object 模型 (5 个文件)
- 测试数据文件
- CI/CD 工作流更新

#### Day 3-4: Tier 1 页面测试 (12 月 6-7 日)
```
✓ Dashboard.vue: 8-10 个测试
✓ Market.vue: 10-12 个测试
✓ StockDetail.vue: 12-15 个测试
✓ TechnicalAnalysis.vue: 8-10 个测试
✓ TradeManagement.vue: 10-12 个测试
```

**成果物**:
- 48-59 个测试用例
- 测试报告和通过率分析

#### Day 5: 验证 & 报告 (12 月 8 日)
```
✓ 运行完整 E2E 测试套件 (P0 + P1 + P2)
✓ 生成 Phase 2 完成报告
✓ 性能基准测试
✓ 提交 PR 和检查清单
```

**成果物**:
- Phase 2 完成报告
- 测试覆盖率统计
- 性能指标分析

---

## 🧪 Phase 2 测试用例结构

### Dashboard 测试示例
```typescript
// tests/e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';
import { DashboardPage } from '../helpers/page-objects';

test.describe('Dashboard Page', () => {
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    await dashboardPage.navigate();
  });

  test('应该加载并显示概览数据', async () => {
    // 等待数据加载
    await dashboardPage.waitForDataLoad();

    // 验证关键元素
    await expect(dashboardPage.totalAssetCard).toBeVisible();
    await expect(dashboardPage.dailyReturnCard).toBeVisible();

    // 验证数据内容
    const assetValue = await dashboardPage.getTotalAssetValue();
    expect(assetValue).toBeGreaterThan(0);
  });

  test('应该支持数据刷新', async () => {
    const initialValue = await dashboardPage.getTotalAssetValue();

    await dashboardPage.clickRefreshButton();
    await dashboardPage.waitForDataLoad();

    const refreshedValue = await dashboardPage.getTotalAssetValue();
    // 值可能改变（市场波动）或保持不变（没有成交）
    expect(refreshedValue).toBeDefined();
  });

  test('应该响应式适配不同屏幕', async ({ page }) => {
    // 测试桌面视图
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(dashboardPage.gridLayout).toHaveClass(/grid-cols-4/);

    // 测试平板视图
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(dashboardPage.gridLayout).toHaveClass(/grid-cols-2/);

    // 测试手机视图
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(dashboardPage.gridLayout).toHaveClass(/grid-cols-1/);
  });
});
```

---

## 📊 覆盖率增长预测

### P0 + P1 + P2 总体覆盖率

| 阶段 | 单元测试 | 集成测试 | E2E 测试 | 总测试 | 覆盖率 |
|------|----------|----------|----------|--------|--------|
| P0 | 135 | 0 | 0 | 135 | 18% (后端单元) |
| P1 | 135 | 39 | 0 | 174 | 27% (混合) |
| P2 | 135 | 39 | 40-50 | 214-224 | **35%+** (全面) |

### 页面覆盖率增长

| 类型 | P1 | P2 | 增长 |
|------|----|----|------|
| API 端点 | 13 | 20+ | +7 |
| 前端页面 | 4 | 14-19 | +10-15 |
| 用户流程 | 5 | 15+ | +10 |
| 边界情景 | 39 | 40+ | +1 |

---

## 🚀 Phase 2 实施步骤

### 步骤 1: 创建 Page Object 模型

**创建文件**:
```bash
mkdir -p tests/helpers
touch tests/helpers/page-objects.ts
touch tests/helpers/api-helpers.ts
touch tests/helpers/test-fixtures.ts
touch tests/helpers/assertions.ts
```

**Page Object 类结构**:
```typescript
export class BasePage {
  constructor(protected page: Page) {}
  async navigate(path: string): Promise<void> { ... }
  async waitForElement(selector: string): Promise<void> { ... }
}

export class DashboardPage extends BasePage {
  get totalAssetCard() { ... }
  get dailyReturnCard() { ... }
  async getTotalAssetValue(): Promise<number> { ... }
}

export class MarketPage extends BasePage {
  async searchStock(symbol: string): Promise<void> { ... }
  async applyFilter(filterName: string, value: string): Promise<void> { ... }
}
```

### 步骤 2: 编写 Tier 1 测试

**测试文件**:
```bash
touch tests/e2e/dashboard.spec.ts
touch tests/e2e/market.spec.ts
touch tests/e2e/stock-detail.spec.ts
touch tests/e2e/technical-analysis.spec.ts
touch tests/e2e/trade-management.spec.ts
```

**每个文件**: 8-15 个测试用例

### 步骤 3: 配置测试数据

**创建 fixture**:
```bash
mkdir -p tests/fixtures
touch tests/fixtures/test-data.ts
touch tests/fixtures/mock-responses.ts
touch tests/fixtures/mock-websocket.ts
```

### 步骤 4: 运行和验证

```bash
# 运行所有 E2E 测试
npx playwright test tests/e2e/*.spec.ts

# 生成 HTML 报告
npx playwright show-report

# 运行特定测试套件
npx playwright test tests/e2e/dashboard.spec.ts -g "应该加载"
```

---

## ✅ 质量保障清单

### 测试质量指标
- [ ] 所有测试有清晰的 AAA 结构 (Arrange-Act-Assert)
- [ ] 至少 80% 的测试用例有 edge case 覆盖
- [ ] 所有异步操作有适当的等待 (waitFor, poll)
- [ ] 测试间隔离 (无全局状态污染)
- [ ] 测试数据清理 (cleanup/teardown)

### 性能指标
- [ ] 单个测试 < 30 秒 (平均 < 10 秒)
- [ ] 完整运行 < 5 分钟 (4 workers)
- [ ] 脑图表加载 < 2 秒
- [ ] API 响应 < 1 秒

### 覆盖率指标
- [ ] 新增覆盖 40+ 个测试用例
- [ ] 页面覆盖 10-15 个关键页面
- [ ] 用户流程覆盖 15+ 个常见流程
- [ ] 错误处理覆盖 20+ 个异常场景

---

## 📈 预期成果

### 交付物
1. **Page Object 模型** (5 个文件, ~500 行代码)
2. **E2E 测试用例** (40-50 个, ~1,500 行代码)
3. **测试数据和 Mock 服务** (3 个文件, ~300 行代码)
4. **完成报告** (含测试统计和分析)

### 指标改进
| 指标 | 当前 | 目标 | 改进 |
|------|------|------|------|
| 测试总数 | 174 | 214-224 | +40-50 |
| E2E 测试 | 0 | 40-50 | 100% |
| 代码覆盖 | 27% | 35%+ | +8% |
| 页面覆盖 | 4 | 14-19 | +10-15 |

---

## 🔍 风险和缓解

### 风险 1: 网络不稳定导致测试间歇性失败
**缓解**:
- 使用重试机制 (Playwright retries: 2)
- 实现智能等待 (waitForLoadState, waitForFunction)
- Mock 网络不稳定场景

### 风险 2: API 响应延迟
**缓解**:
- 设置合理的超时 (30s for E2E)
- 使用 API 拦截和 mock
- 实现 circuit breaker 模式

### 风险 3: 浏览器兼容性问题
**缓解**:
- 测试 Chrome, Firefox, Safari
- 针对渲染引擎差异调整选择器
- 使用 aria-label 增强稳定性

### 风险 4: 测试执行时间过长
**缓解**:
- 并行执行 (4-6 workers)
- 优化等待时间 (避免硬 sleep)
- 分批次运行 (Tier 1 vs Tier 2)

---

## 📞 联系和反馈

**Phase 2 负责人**: Claude Code AI Assistant
**测试框架**: Playwright 4.40+
**测试报告**: `docs/reports/PHASE2_E2E_COMPLETION_REPORT.md`
**预期完成**: 2025-12-08

---

**版本**: 1.0
**最后更新**: 2025-12-04
**状态**: 规划完成，准备实施
