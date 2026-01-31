# ArtDeco V3.0 图表组件视觉回归测试方案

**版本**: 1.0
**创建日期**: 2026-01-25
**项目**: MyStocks量化交易数据管理系统
**状态**: 方案设计

---

## 📋 目录

1. [概述](#概述)
2. [测试目标与范围](#测试目标与范围)
3. [工具选型](#工具选型)
4. [测试策略](#测试策略)
5. [实现方案](#实现方案)
6. [测试用例设计](#测试用例设计)
7. [CI/CD集成](#cicd集成)
8. [报告与监控](#报告与监控)
9. [最佳实践](#最佳实践)
10. [实施路线图](#实施路线图)

---

## 概述

### 背景

ArtDeco V3.0 Web设计系统已完成Phase 0-3升级，包括：
- 20个ECharts图表组件应用ArtDeco主题
- 完整的颜色、字体、动效系统
- 6个生产环境图表组件新增主题应用

为确保设计系统的稳定性和一致性，需要建立**视觉回归测试**机制，防止样式退化。

### 定义

**视觉回归测试 (Visual Regression Testing)**:
通过截图对比，自动检测UI界面在代码变更后是否发生意外的视觉变化。

### 核心价值

| 价值 | 描述 |
|------|------|
| 早期发现问题 | 在CI中捕获意外的设计变更 |
| 减少人工审核 | 自动化截图对比，减少人工工作量 |
| 记录变更历史 | 保存每次构建的截图，便于追溯 |
| 保障设计一致性 | 确保所有页面符合ArtDeco V3.0规范 |

---

## 测试目标与范围

### 测试目标

1. **捕获意外变更**: 识别代码变更导致的非预期视觉变化
2. **验证设计一致性**: 确保所有图表符合ArtDeco V3.0规范
3. **监控时间序列**: 追踪设计系统的长期演变
4. **支持快速迭代**: 在不影响质量的前提下支持快速开发

### 测试范围

#### 包含范围

| 类别 | 组件数量 | 说明 |
|------|---------|------|
| **ECharts图表组件** | 20个 | 已应用ArtDeco主题的图表 |
| **Dashboard页面** | 1个 | 主仪表板页面的图表区域 |
| **技术分析页面** | 1个 | 包含K线和技术指标图表 |
| **交易管理页面** | 1个 | 统计和风险图表 |
| **回测分析页面** | 1个 | 回测结果图表 |

#### ECharts图表组件清单

| 序号 | 组件 | 文件路径 | 优先级 |
|------|------|---------|--------|
| 1 | 行业分布图 | `views/Dashboard.vue` | P0 |
| 2 | 市场热力图 | `views/Dashboard.vue` | P0 |
| 3 | 指数图表 | `views/Phase4Dashboard.vue` | P1 |
| 4 | 分布图表 | `views/Phase4Dashboard.vue` | P1 |
| 5 | 组合图表 | `views/Phase4Dashboard.vue` | P1 |
| 6 | 技术分析图 | `views/technical/TechnicalAnalysis.vue` | P0 |
| 7 | 健康雷达图 | `components/chart/HealthRadarChart.vue` | P1 |
| 8 | 资产图表 | `views/trade-management/components/StatisticsTab.vue` | P1 |
| 9 | 收益图表 | `views/trade-management/components/StatisticsTab.vue` | P1 |
| 10 | 组合风险图 | `views/components/RiskOverviewTab.vue` | P1 |
| 11 | 风险分布图 | `views/components/RiskOverviewTab.vue` | P1 |
| 12 | 资金流向图 | `components/market/FundFlowPanel.vue` | P1 |
| 13 | 高级热力图 | `components/charts/AdvancedHeatmap.vue` | P1 |
| 14 | 桑基图 | `components/charts/SankeyChart.vue` | P1 |
| 15 | 树状图 | `components/charts/TreeChart.vue` | P1 |
| 16 | 关系图 | `components/charts/RelationChart.vue` | P1 |
| 17 | 图表容器 | `components/shared/charts/ChartContainer.vue` | P1 |
| 18 | 策略卡片图 | `components/artdeco/trading/ArtDecoStrategyCard.vue` | P1 |
| 19 | 持仓卡片图 | `components/artdeco/trading/ArtDecoPositionCard.vue` | P1 |
| 20 | 交易决策图表 | `views/TradingDecisionCenter.vue` | P0 |

#### 排除范围

| 组件 | 排除原因 |
|------|---------|
| KLineChart | 使用klinecharts库，非ECharts |
| ProKLineChart | 使用klinecharts库，非ECharts |
| HeatmapCard | 自定义网格实现，非标准ECharts |
| Demo页面 | 非生产环境 |

### 测试优先级

| 优先级 | 定义 | 覆盖组件 |
|--------|------|---------|
| **P0** | 核心业务页面，必须测试 | Dashboard、技术分析、交易决策 |
| **P1** | 重要功能页面，建议测试 | Phase4Dashboard、StatisticsTab、RiskOverviewTab |
| **P2** | 一般功能页面，可选测试 | 其他图表组件 |

---

## 工具选型

### 推荐方案

#### 1. Playwright Visual Tests (主方案)

**为什么选择Playwright**:
- 内置视觉测试支持
- 跨浏览器测试能力
- 丰富的截图API
- 像素级对比功能
- 与现有测试框架集成良好

**版本要求**:
```
Playwright >= 1.40.0
Node.js >= 18.0.0
```

#### 2. 截图对比工具

**pixelmatch** (Playwright内置):
- 像素级差异检测
- 可配置阈值
- 高性能
- 支持生成差异图

#### 3. 存储方案

**方案A: 本地存储** (推荐用于开发)
```
test-results/
├── visual/
│   ├── baseline/    # 基线截图
│   ├── current/     # 当前截图
│   ├── diff/        # 差异图
│   └── report/      # HTML报告
```

**方案B: 云存储** (推荐用于CI)
- Git LFS (适合小规模)
- AWS S3 / MinIO
- Artifactory

### 备选方案

| 工具 | 优点 | 缺点 |
|------|------|------|
| Percy | 专业的视觉测试云服务 | 付费、有配额限制 |
| Chromatic | Storybook集成好 | 付费、专注于React |
| Loki | 简单易用 | 功能有限 |
| BackstopJS | 老牌工具 | 配置复杂 |

### 最终选择

**主方案**: Playwright Visual Tests + 本地存储
- 充分利用现有Playwright基础设施
- 零额外成本
- 完全可控

---

## 测试策略

### 测试类型

#### 1. 全页面截图测试

**目的**: 捕获整个页面的视觉变化

**适用场景**:
- Dashboard首页
- 技术分析页面
- 交易管理页面

**配置**:
```typescript
// 全页面截图
await page.goto('/dashboard');
await page.waitForLoadState('networkidle');
await expect(page).toHaveScreenshot('dashboard-full.png', {
  fullPage: true,
  animations: 'disabled',
});
```

#### 2. 组件截图测试

**目的**: 精确捕获单个图表组件的变化

**适用场景**:
- ECharts图表组件
- 独立卡片组件

**配置**:
```typescript
// 组件截图
const chartLocator = page.locator('#industryChart');
await expect(chartLocator).toHaveScreenshot('industry-chart.png', {
  animations: 'disabled',
});
```

#### 3. 响应式测试

**目的**: 验证不同屏幕尺寸下的显示

**测试分辨率**:
| 分辨率 | 宽度 | 用途 |
|--------|------|------|
| Desktop HD | 1920x1080 | 主要测试分辨率 |
| Desktop | 1440x900 | 常用工作分辨率 |
| Laptop | 1280x800 | 便携设备 |
| Tablet | 768x1024 | 平板横屏 |

**配置**:
```typescript
// 使用Playwright的设备模拟
const devices = ['Desktop Chrome', 'Desktop Firefox', 'iPad Pro'];
for (const device of devices) {
  test(`Dashboard on ${device}`, async ({ page }) => {
    const context = await browser.newContext({
      ...devices[device],
    });
    // 测试逻辑
  });
}
```

#### 4. 暗色模式测试

**目的**: 验证ArtDeco V3.0暗色主题正确显示

**测试内容**:
- 金色品牌元素对比度
- 数据颜色正确显示
- 背景一致性

### 触发机制

#### 自动化触发

| 触发条件 | 执行测试 |
|---------|---------|
| PR创建/更新 | 运行P0+P1级别测试 |
| 代码合并到main | 运行全部视觉测试 |
| 每日定时任务 | 运行全部视觉测试 |
| 手动触发 | 可选择运行特定测试 |

#### 测试流程

```
┌─────────────────────────────────────────────────────────────┐
│                    视觉回归测试流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 代码变更 → 2. CI触发 → 3. 生成截图 → 4. 对比分析        │
│                  ↓                                          │
│  5. 生成报告 → 6. 结果判断 → 7. 通知处理                    │
│                  ↓                                          │
│          ┌─────────────┐                                    │
│          │ 无差异 → 通过 │                                    │
│          └─────────────┘                                    │
│                  ↓                                          │
│          ┌─────────────────┐                                │
│          │ 有差异 → 人工审核 │                                │
│          └─────────────────┘                                │
│                  ↓                                          │
│          ┌─────────────┐                                    │
│          │ 批准 → 更新基线 │                                 │
│          └─────────────┘                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 对比策略

#### 像素差异阈值

```typescript
const visualConfig = {
  // 像素匹配阈值 (0-1)
  threshold: 0.2,
  
  // 最大差异像素比例
  maxDiffPixels: 0.01,  // 1%
  
 // 忽略区域 (动态内容)
  ignoreRegions: [
    '.timestamp',      // 时间戳
    '.live-indicator', // 实时指示器
    '.loading-spinner', // 加载动画
  ],
};
```

#### 差异分类

| 类别 | 像素差异 | 处理方式 |
|------|---------|---------|
| **无差异** | 0% | 测试通过 |
| **微小差异** | <0.5% | 自动通过，可记录 |
| **可接受差异** | 0.5%-1% | 人工确认后通过 |
| **显著差异** | 1%-5% | 需人工审核 |
| **严重差异** | >5% | 阻断合并，需修复 |

---

## 实现方案

### 目录结构

```
tests/
├── visual/                          # 视觉回归测试目录
│   ├── config/
│   │   ├── visual.config.ts        # 视觉测试配置
│   │   ├── thresholds.ts           # 差异阈值配置
│   │   └── breakpoints.ts          # 响应式断点配置
│   ├── pages/
│   │   ├── dashboard.visual.spec.ts
│   │   ├── technical-analysis.visual.spec.ts
│   │   ├── trade-management.visual.spec.ts
│   │   └── risk-overview.visual.spec.ts
│   ├── components/
│   │   ├── charts/
│   │   │   ├── industry-chart.visual.spec.ts
│   │   │   ├── market-heatmap.visual.spec.ts
│   │   │   └── health-radar.visual.spec.ts
│   │   └── cards/
│   │       ├── strategy-card.visual.spec.ts
│   │       └── position-card.visual.spec.ts
│   ├── utils/
│   │   ├── screenshot-helper.ts    # 截图辅助函数
│   │   ├── comparison-helper.ts    # 对比辅助函数
│   │   └── baseline-manager.ts     # 基线管理
│   ├── fixtures/
│   │   ├── visual-test.fixture.ts  # 测试夹具
│   │   └── chart-data.fixture.ts   # 图表数据夹具
│   └── README.md
│
├── e2e/
│   └── pages/
│       └── DashboardPage.ts        # 页面对象
```

### 核心配置

#### 1. 视觉测试配置文件

**文件**: `tests/visual/config/visual.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export const visualConfig = defineConfig({
  // 测试配置
  testDir: './tests/visual',
  fullyParallel: true,
  
  // 视觉测试专用配置
  expect: {
    toHaveScreenshot: {
      // 像素差异阈值
      threshold: 0.2,
      // 最大差异像素比例
      maxDiffPixels: 0.01,
      // 忽略动画
      animations: 'disabled',
      // 忽略滚动条
      styleWithLayoutIgnore: ['scrollbar', '::-webkit-scrollbar'],
    },
  },
  
  // 项目配置
  projects: [
    // P0: 核心页面测试
    {
      name: 'visual-p0',
      testMatch: /.*visual.spec.ts/,
      testIgnore: /components\//,
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
        screenshot: 'on',
        video: 'retain-on-failure',
      },
    },
    
    // P1: 组件测试
    {
      name: 'visual-p1',
      testMatch: /components\/.*\.spec.ts/,
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
      },
    },
    
    // 响应式测试
    {
      name: 'visual-responsive',
      testMatch: /.*responsive.*\.spec.ts/,
      use: {
        ...devices['iPad Pro'],
        baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
      },
    },
  ],
  
  // 截图存储
  screenshotDir: './test-results/visual',
  
  // 报告
  reporter: [
    ['html', { outputFolder: './test-results/visual-report' }],
    ['json', { outputFile: './test-results/visual-results.json' }],
  ],
});
```

#### 2. 差异阈值配置

**文件**: `tests/visual/config/thresholds.ts`

```typescript
export interface ThresholdConfig {
  // 整体像素差异阈值 (0-1)
  overallThreshold: number;
  
  // 组件特定阈值
  componentThresholds: Record<string, number>;
  
  // 忽略的选择器
  ignoreSelectors: string[];
  
  // 最大允许差异像素比例
  maxDiffRatio: number;
}

export const defaultThresholds: ThresholdConfig = {
  overallThreshold: 0.2,
  
  componentThresholds: {
    // P0组件使用更严格的阈值
    'industryChart': 0.1,
    'marketHeatChart': 0.1,
    'technicalAnalysisChart': 0.1,
    
    // P1组件使用默认阈值
    'default': 0.2,
  },
  
  ignoreSelectors: [
    // 动态内容
    '.elapsed-time',
    '.current-time',
    '.timestamp',
    '.live-indicator',
    '.loading-spinner',
    '.skeleton-loader',
    
    // 动画元素
    '.animating',
    '[class*="animate-"]',
    
    // 实时数据
    '.realtime-price',
    '.price-change',
    '.volume-value',
    
    // 工具提示（悬停时出现）
    '.el-tooltip',
    '.tippy-popper',
  ],
  
  maxDiffRatio: 0.01, // 1%
};

export const responsiveBreakpoints = {
  'Desktop HD': { width: 1920, height: 1080 },
  'Desktop': { width: 1440, height: 900 },
  'Laptop': { width: 1280, height: 800 },
  'Tablet': { width: 768, height: 1024 },
};
```

#### 3. 测试夹具

**文件**: `tests/visual/fixtures/visual-test.fixture.ts`

```typescript
import { test as base, Page, Locator } from '@playwright/test';
import { defaultThresholds } from '../config/thresholds';

// 创建自定义测试夹具
export const test = base.extend({
  // 页面上下文
  page: async ({ page }, use) => {
    // 等待网络空闲
    await page.waitForLoadState('networkidle');
    
    // 设置视口
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    await use(page);
  },
  
  // 图表定位器
  chartLocator: async ({ page }, use) => {
    const getChartLocator = (selector: string) => {
      return page.locator(selector).first();
    };
    
    await use(getChartLocator);
  },
  
  // 等待图表渲染
  waitForChartRender: async ({ page }, use) => {
    const waitForChart = async (selector: string, timeout = 10000) => {
      const chart = page.locator(selector).first();
      
      // 等待图表可见
      await chart.waitFor({ state: 'visible', timeout });
      
      // 等待ECharts实例初始化
      await page.waitForFunction(
        (sel) => {
          const el = document.querySelector(sel);
          return el && el.classList.contains('echarts-instance');
        },
        selector,
        { timeout }
      );
    };
    
    await use(waitForChart);
  },
  
  // 截图比较器
  screenshotComparator: async ({}, use) => {
    const compareScreenshots = async (
      actualBuffer: Buffer,
      expectedPath: string
    ): Promise<{ match: boolean; diffRatio: number; diffBuffer?: Buffer }> => {
      // 读取期望截图
      const fs = await import('fs');
      const path = await import('path');
      
      if (!fs.existsSync(expectedPath)) {
        return { match: false, diffRatio: 1, diffBuffer: actualBuffer };
      }
      
      const expectedBuffer = fs.readFileSync(expectedPath);
      
      // 使用Playwright内置比较
      // 这里可以集成pixelmatch进行更精细的比较
      const match = actualBuffer.equals(expectedBuffer);
      
      if (match) {
        return { match: true, diffRatio: 0 };
      }
      
      // 计算差异 (简化版，实际可使用pixelmatch)
      // 此处省略具体实现
      
      return { match: false, diffRatio: 0.01 };
    };
    
    await use(compareScreenshots);
  },
});

// 导出类型
export { expect } from '@playwright/test';
```

### 测试用例示例

#### 1. Dashboard页面视觉测试

**文件**: `tests/visual/pages/dashboard.visual.spec.ts`

```typescript
import { test, expect } from '../fixtures/visual-test.fixture';

test.describe('Dashboard Page - Visual Regression', () => {
  const dashboardPath = '/dashboard';
  
  test.beforeEach(async ({ page }) => {
    // 导航到Dashboard页面
    await page.goto(dashboardPath);
    
    // 等待页面完全加载
    await page.waitForLoadState('networkidle');
    
    // 禁用动画
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          transition-duration: 0s !important;
        }
      `,
    });
  });
  
  test('Dashboard full page - Desktop HD', async ({ page }) => {
    // 全页面截图
    await expect(page).toHaveScreenshot('dashboard-desktop-hd.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });
  
  test('Industry distribution chart', async ({ page, waitForChartRender }) => {
    // 定位行业分布图
    const industryChart = page.locator('#industryChart').first();
    
    // 等待图表渲染
    await waitForChartRender('#industryChart');
    
    // 组件截图
    await expect(industryChart).toHaveScreenshot('dashboard-industry-chart.png', {
      animations: 'disabled',
    });
  });
  
  test('Market heatmap chart', async ({ page, waitForChartRender }) => {
    // 定位市场热力图
    const heatmapChart = page.locator('#marketHeatChart').first();
    
    // 等待图表渲染
    await waitForChartRender('#marketHeatChart');
    
    // 组件截图
    await expect(heatmapChart).toHaveScreenshot('dashboard-market-heatmap.png', {
      animations: 'disabled',
    });
  });
  
  test('Statistics cards section', async ({ page }) => {
    // 定位统计卡片区域
    const statsSection = page.locator('.stats-grid').first();
    
    await expect(statsSection).toHaveScreenshot('dashboard-stats-section.png', {
      animations: 'disabled',
    });
  });
});
```

#### 2. 技术分析页面视觉测试

**文件**: `tests/visual/pages/technical-analysis.visual.spec.ts`

```typescript
import { test, expect } from '../fixtures/visual-test.fixture';

test.describe('Technical Analysis Page - Visual Regression', () => {
  const technicalAnalysisPath = '/technical-analysis';
  
  test.beforeEach(async ({ page }) => {
    await page.goto(technicalAnalysisPath);
    await page.waitForLoadState('networkidle');
    
    // 禁用动画
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          transition-duration: 0s !important;
        }
      `,
    });
  });
  
  test('Technical analysis full page', async ({ page }) => {
    await expect(page).toHaveScreenshot('technical-analysis-full.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });
  
  test('Main K-line chart with indicators', async ({ page, waitForChartRender }) => {
    await waitForChartRender('#mainChart');
    
    const mainChart = page.locator('#mainChart').first();
    await expect(mainChart).toHaveScreenshot('technical-analysis-main-chart.png');
  });
  
  test('Indicator panel', async ({ page }) => {
    const indicatorPanel = page.locator('.indicator-panel').first();
    await expect(indicatorPanel).toHaveScreenshot('technical-analysis-indicators.png');
  });
  
  test('Stock selector dropdown', async ({ page }) => {
    const stockSelector = page.locator('.stock-selector').first();
    
    // 展开下拉菜单
    await stockSelector.click();
    await page.waitForTimeout(500);
    
    await expect(stockSelector).toHaveScreenshot('technical-analysis-stock-selector.png');
  });
});
```

#### 3. ECharts图表组件视觉测试

**文件**: `tests/visual/components/charts/industry-chart.visual.spec.ts`

```typescript
import { test, expect } from '../../fixtures/visual-test.fixture';

test.describe('Industry Chart - Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到包含行业图表的页面
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // 禁用所有动画
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          transition-duration: 0s !important;
        }
      `,
    });
  });
  
  test('Industry pie chart', async ({ page, waitForChartRender }) => {
    // 定位行业饼图
    const pieChart = page.locator('.echarts-container >> nth=0');
    
    // 等待渲染
    await waitForChartRender('.echarts-container >> nth=0');
    
    // 截图
    await expect(pieChart).toHaveScreenshot('industry-pie-chart.png', {
      animations: 'disabled',
    });
  });
  
  test('Industry bar chart', async ({ page, waitForChartRender }) => {
    const barChart = page.locator('.echarts-container >> nth=1');
    await waitForChartRender('.echarts-container >> nth=1');
    
    await expect(barChart).toHaveScreenshot('industry-bar-chart.png', {
      animations: 'disabled',
    });
  });
  
  test('Chart with gold theme colors', async ({ page, waitForChartRender }) => {
    const chart = page.locator('#industryChart');
    await waitForChartRender('#industryChart');
    
    // 验证图表包含ArtDeco金色主题
    await expect(chart).toHaveScreenshot('industry-chart-gold-theme.png', {
      animations: 'disabled',
    });
  });
});
```

#### 4. 响应式视觉测试

**文件**: `tests/visual/pages/dashboard.responsive.visual.spec.ts`

```typescript
import { test, expect } from '../fixtures/visual-test.fixture';
import { devices } from '@playwright/test';

const responsiveDevices = [
  { name: 'Desktop HD', ...devices['Desktop Chrome'] },
  { name: 'Desktop', ...devices['Macbook Pro 14'] },
  { name: 'Tablet', ...devices['iPad Pro'] },
];

responsiveDevices.forEach(({ name, viewport }) => {
  test.describe(`Dashboard Responsive - ${name}`, () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      // 设置视口
      if (viewport) {
        await page.setViewportSize(viewport);
      }
      
      // 禁用动画
      await page.addStyleTag({
        content: `
          *, *::before, *::after {
            animation-duration: 0s !important;
            transition-duration: 0s !important;
          }
        `,
      });
    });
    
    test('Dashboard layout adapts to viewport', async ({ page }) => {
      await expect(page).toHaveScreenshot(`dashboard-${name.toLowerCase().replace(/\s+/g, '-')}.png`, {
        fullPage: true,
        animations: 'disabled',
      });
    });
    
    test('Charts resize correctly', async ({ page, waitForChartRender }) => {
      const chart = page.locator('#industryChart').first();
      await waitForChartRender('#industryChart');
      
      await expect(chart).toHaveScreenshot(`dashboard-chart-${name.toLowerCase().replace(/\s+/g, '-')}.png`);
    });
  });
});
```

### 基线管理工具

**文件**: `tests/visual/utils/baseline-manager.ts`

```typescript
import * as fs from 'fs';
import * as path from 'path';

export class BaselineManager {
  private baselineDir: string;
  private currentDir: string;
  private diffDir: string;
  
  constructor(baseDir = './test-results/visual') {
    this.baselineDir = path.join(baseDir, 'baseline');
    this.currentDir = path.join(baseDir, 'current');
    this.diffDir = path.join(baseDir, 'diff');
  }
  
  // 初始化目录
  async initialize(): Promise<void> {
    for (const dir of [this.baselineDir, this.currentDir, this.diffDir]) {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    }
  }
  
  // 获取基线路径
  getBaselinePath(testName: string): string {
    return path.join(this.baselineDir, `${testName}.png`);
  }
  
  // 获取当前截图路径
  getCurrentPath(testName: string): string {
    return path.join(this.currentDir, `${testName}.png`);
  }
  
  // 获取差异图路径
  getDiffPath(testName: string): string {
    return path.join(this.diffDir, `${testName}-diff.png`);
  }
  
  // 更新基线
  async updateBaseline(testName: string, screenshotBuffer: Buffer): Promise<void> {
    const baselinePath = this.getBaselinePath(testName);
    fs.writeFileSync(baselinePath, screenshotBuffer);
    console.log(`✅ Updated baseline: ${baselinePath}`);
  }
  
  // 检查基线是否存在
  baselineExists(testName: string): boolean {
    return fs.existsSync(this.getBaselinePath(testName));
  }
  
  // 列出所有基线
  listBaselines(): string[] {
    if (!fs.existsSync(this.baselineDir)) {
      return [];
    }
    return fs.readdirSync(this.baselineDir).filter(f => f.endsWith('.png'));
  }
  
  // 删除基线
  deleteBaseline(testName: string): void {
    const baselinePath = this.getBaselinePath(testName);
    if (fs.existsSync(baselinePath)) {
      fs.unlinkSync(baselinePath);
    }
  }
  
  // 清理当前和差异目录
  async cleanup(): Promise<void> {
    for (const dir of [this.currentDir, this.diffDir]) {
      if (fs.existsSync(dir)) {
        fs.rmSync(dir, { recursive: true, force: true });
      }
    }
    await this.initialize();
  }
}

// CLI工具
async function main() {
  const manager = new BaselineManager();
  const command = process.argv[2];
  
  switch (command) {
    case 'init':
      await manager.initialize();
      console.log('✅ Visual test directories initialized');
      break;
      
    case 'list':
      const baselines = manager.listBaselines();
      console.log(`Found ${baselines.length} baselines:`);
      baselines.forEach(b => console.log(`  - ${b}`));
      break;
      
    case 'update':
      const testName = process.argv[3];
      if (!testName) {
        console.error('Usage: node baseline-manager.js update <test-name>');
        process.exit(1);
      }
      console.log(`To update baseline: ${testName}, use Playwright's --update-snapshots flag`);
      break;
      
    case 'cleanup':
      await manager.cleanup();
      console.log('✅ Cleaned up current and diff directories');
      break;
      
    default:
      console.log('Usage: node baseline-manager.js <command>');
      console.log('Commands:');
      console.log('  init       - Initialize directories');
      console.log('  list       - List existing baselines');
      console.log('  update     - Update a baseline (use --update-snapshots)');
      console.log('  cleanup    - Clean up current and diff directories');
  }
}

main().catch(console.error);
```

---

## 测试用例设计

### 测试用例矩阵

| 用例ID | 页面/组件 | 测试内容 | 优先级 | 预期结果 |
|--------|----------|---------|--------|---------|
| VIS-001 | Dashboard | 全页面截图 | P0 | 匹配基线 |
| VIS-002 | Dashboard | 行业分布图 | P0 | 匹配基线 |
| VIS-003 | Dashboard | 市场热力图 | P0 | 匹配基线 |
| VIS-004 | Dashboard | 统计卡片区 | P1 | 匹配基线 |
| VIS-005 | Technical Analysis | 全页面截图 | P0 | 匹配基线 |
| VIS-006 | Technical Analysis | 主K线图 | P0 | 匹配基线 |
| VIS-007 | Technical Analysis | 指标面板 | P1 | 匹配基线 |
| VIS-008 | Trade Management | 统计图表 | P1 | 匹配基线 |
| VIS-009 | Trade Management | 收益图表 | P1 | 匹配基线 |
| VIS-010 | Risk Overview | 风险图表 | P1 | 匹配基线 |
| VIS-011 | All Pages | 响应式(1920px) | P1 | 匹配基线 |
| VIS-012 | All Pages | 响应式(1440px) | P1 | 匹配基线 |
| VIS-013 | All Pages | 响应式(768px) | P2 | 匹配基线 |
| VIS-014 | Strategy Card | 策略卡片图 | P1 | 匹配基线 |
| VIS-015 | Position Card | 持仓卡片图 | P1 | 匹配基线 |
| VIS-016 | Fund Flow | 资金流向图 | P1 | 匹配基线 |
| VIS-017 | Advanced Heatmap | 高级热力图 | P1 | 匹配基线 |
| VIS-018 | Sankey Chart | 桑基图 | P2 | 匹配基线 |
| VIS-019 | Tree Chart | 树状图 | P2 | 匹配基线 |
| VIS-020 | Relation Chart | 关系图 | P2 | 匹配基线 |

### 测试用例详情

#### VIS-001: Dashboard全页面截图

```typescript
// tests/visual/pages/dashboard.visual.spec.ts

test('Dashboard full page screenshot', async ({ page }) => {
  // 步骤1: 导航到Dashboard页面
  await page.goto('/dashboard');
  
  // 步骤2: 等待页面完全加载
  await page.waitForLoadState('networkidle');
  
  // 步骤3: 禁用所有CSS动画
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        transition-duration: 0s !important;
      }
    `,
  });
  
  // 步骤4: 等待图表渲染完成
  await page.waitForFunction(() => {
    const charts = document.querySelectorAll('.echarts-container canvas');
    return charts.length >= 2; // 假设Dashboard有至少2个图表
  });
  
  // 步骤5: 截图
  await expect(page).toHaveScreenshot('dashboard-full.png', {
    fullPage: true,
    animations: 'disabled',
  });
});
```

#### VIS-002: 行业分布图

```typescript
test('Industry distribution chart screenshot', async ({ page, waitForChartRender }) => {
  // 步骤1: 导航到Dashboard
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  
  // 步骤2: 禁用动画
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        transition-duration: 0s !important;
      }
    `,
  });
  
  // 步骤3: 定位图表容器
  const chartContainer = page.locator('#industryChart').first();
  
  // 步骤4: 等待图表渲染
  await waitForChartRender('#industryChart');
  
  // 步骤5: 确保图表可见
  await chartContainer.waitFor({ state: 'visible' });
  
  // 步骤6: 截图
  await expect(chartContainer).toHaveScreenshot('industry-chart.png', {
    animations: 'disabled',
  });
});
```

### 数据驱动测试

```typescript
// tests/visual/data/chart-scenarios.ts

export interface ChartTestScenario {
  name: string;
  path: string;
  chartSelector: string;
  waitForSelector?: string;
  priority: 'P0' | 'P1' | 'P2';
}

export const chartScenarios: ChartTestScenario[] = [
  {
    name: 'Dashboard - Industry Chart',
    path: '/dashboard',
    chartSelector: '#industryChart',
    waitForSelector: '.echarts-container canvas',
    priority: 'P0',
  },
  {
    name: 'Dashboard - Market Heatmap',
    path: '/dashboard',
    chartSelector: '#marketHeatChart',
    waitForSelector: '.echarts-container canvas',
    priority: 'P0',
  },
  {
    name: 'Technical Analysis - Main Chart',
    path: '/technical-analysis',
    chartSelector: '#mainChart',
    waitForSelector: '.echarts-container canvas',
    priority: 'P0',
  },
  // ...更多场景
];

// 数据驱动测试生成
chartScenarios.forEach((scenario) => {
  test(`${scenario.name} - Screenshot`, async ({ page, waitForChartRender }) => {
    await page.goto(scenario.path);
    await page.waitForLoadState('networkidle');
    
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          transition-duration: 0s !important;
        }
      `,
    });
    
    const chartLocator = page.locator(scenario.chartSelector).first();
    await waitForChartRender(scenario.chartSelector);
    
    const filename = scenario.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
    await expect(chartLocator).toHaveScreenshot(`${filename}.png`, {
      animations: 'disabled',
    });
  });
});
```

---

## CI/CD集成

本节遵循MyStocks项目现有的CI/CD框架规范，与现有工作流保持一致。

### GitHub Actions工作流

**文件**: `.github/workflows/visual-testing.yml`

遵循项目现有的工作流命名规范（`[test-type].yml`），与其他测试工作流保持一致。

```yaml
name: Visual Testing

on:
  push:
    branches: [main, develop]
    paths:
      - 'web/frontend/src/**'
      - 'tests/visual/**'
      - '.github/workflows/visual-testing.yml'
  pull_request:
    paths:
      - 'web/frontend/src/**'
      - 'tests/visual/**'
      - '.github/workflows/visual-testing.yml'
  schedule:
    # 遵循性能目标: CI执行时间<15分钟
    # 每周日2:00运行，避开高峰期
    - cron: '0 2 * * 0'
  workflow_dispatch:
    inputs:
      test_mode:
        description: 'Test execution mode'
        required: false
        default: 'standard'
        type: choice
        options:
          - standard
          - full
          - update-baseline

env:
  # 全局环境变量
  NODE_VERSION: '20'
  PNPM_VERSION: '8'
  E2E_BASE_URL: 'http://localhost:3000'
  PLAYWRIGHT_BROWSERS_PATH: '/mspw/.cache/mspw-playwright-browsers'

jobs:
  # 遵循现有job命名: [job-name]
  visual-testing:
    name: Visual Testing (P$P0+$P1)
    runs-on: ubuntu-latest
    timeout-minutes: 20  # 遵循CI性能目标

    steps:
      # 遵循现有步骤命名规范
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
          cache-dependency-path: web/frontend/pnpm-lock.yaml

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: ${{ env.PNPM_VERSION }}

      - name: Install dependencies
        working-directory: ./web/frontend
        run: pnpm install --frozen-lockfile

      - name: Cache Playwright browsers
        uses: actions/cache@v4
        with:
          path: ${{ env.PLAYWRIGHT_BROWSERS_PATH }}
          key: playwright-${{ runner.os }}-${{ hashFiles('**/pnpm-lock.yaml') }}
          restore-keys: |
            playwright-${{ runner.os }}-

      - name: Install Playwright browsers
        run: pnpm exec playwright install --with-deps chromium

      - name: Start frontend dev server
        working-directory: ./web/frontend
        run: |
          pnpm run dev &
          # 等待服务器启动，遵循现有超时策略
          for i in {1..30}; do
            if curl -s http://localhost:3000 > /dev/null 2>&1; then
              echo "✅ Frontend server ready"
              break
            fi
            sleep 1
          done

      - name: Execute visual tests
        working-directory: ./
        env:
          TEST_MODE: ${{ github.event.inputs.test_mode || 'standard' }}
        run: |
          case "$TEST_MODE" in
            update-baseline)
              echo "📸 Updating visual baselines..."
              pnpm exec playwright test --config=tests/visual/config/visual.config.ts --update-snapshots
              ;;
            full)
              echo "🔍 Running full visual test suite..."
              pnpm exec playwright test --config=tests/visual/config/visual.config.ts
              ;;
            standard|*)
              echo "✅ Running standard visual tests (P0+P1)..."
              pnpm exec playwright test --config=tests/visual/config/visual.config.ts --project=visual-p0,visual-p1
              ;;
          esac

      - name: Upload visual test artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: visual-test-results
          path: test-results/
          retention-days: 30  # 遵循现有artifact保留策略

      - name: Upload visual test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: visual-test-report
          path: test-results/visual-report/
          retention-days: 30

      - name: Verify visual regression results
        if: github.event.inputs.test_mode != 'update-baseline'
        run: |
          if [ -f "test-results/test-results.json" ]; then
            FAILED=$(cat test-results/test-results.json | grep -o '"failures":[0-9]*' | grep -o '[0-9]*' | head -1)
            if [ "$FAILED" != "0" ] && [ -n "$FAILED" ]; then
              echo "❌ Visual regression tests failed: $FAILED failures"
              echo "📊 View details in the artifacts"
              exit 1
            fi
          fi
          echo "✅ All visual regression tests passed"

      - name: Cleanup
        if: always()
        run: |
          pkill -f "pnpm run dev" || true
          pkill -f "vite" || true

  # 响应式测试（独立job，与现有测试类型对齐）
  visual-testing-responsive:
    name: Visual Testing (Responsive)
    runs-on: ubuntu-latest
    timeout-minutes: 15
    if: github.event.inputs.test_mode == 'full' || github.event.inputs.test_mode == 'update-baseline'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: ${{ env.PNPM_VERSION }}

      - name: Install dependencies
        working-directory: ./web/frontend
        run: pnpm install --frozen-lockfile

      - name: Install Playwright browsers
        run: pnpm exec playwright install --with-deps chromium

      - name: Start frontend dev server
        working-directory: ./web/frontend
        run: |
          pnpm run dev &
          sleep 15

      - name: Run responsive visual tests
        working-directory: ./
        run: |
          if [ "${{ github.event.inputs.test_mode }}" == "update-baseline" ]; then
            pnpm exec playwright test --config=tests/visual/config/visual.config.ts --project=visual-responsive --update-snapshots
          else
            pnpm exec playwright test --config=tests/visual/config/visual.config.ts --project=visual-responsive
          fi

      - name: Upload responsive test artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: visual-test-results-responsive
          path: test-results/
          retention-days: 30

      - name: Cleanup
        if: always()
        run: |
          pkill -f "pnpm run dev" || true
```

### 与现有CI/CD工作流集成

#### 1. 集成到code-quality.yml

在代码质量检查工作流中添加视觉测试前置检查：

```yaml
# .github/workflows/code-quality.yml (追加)

  visual-prerequisites:
    name: Check if visual tests are needed
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    outputs:
      needs_visual_test: ${{ steps.check-files.outputs.result }}
    steps:
      - name: Check for frontend changes
        id: check-files
        run: |
          if git diff --name-only ${{ github.event.pull_request.base.sha }}..${{ github.sha }} | grep -q 'web/frontend/src/'; then
            echo "result=true" >> $GITHUB_OUTPUT
          else
            echo "result=false" >> $GITHUB_OUTPUT
          fi

  visual-quality-gate:
    name: Visual Quality Gate
    needs: visual-prerequisites
    runs-on: ubuntu-latest
    if: needs.visual_test == 'true'
    # ... 同 visual-testing job
```

#### 2. 集成到e2e-testing.yml

视觉测试可作为E2E测试的补充，在e2e-testing.yml中添加：

```yaml
# .github/workflows/e2e-testing.yml (追加)

  visual-e2e:
    name: Visual E2E Tests
    runs-on: ubuntu-latest
    timeout-minutes: 25
    steps:
      # ... 同 visual-testing job 配置
```

### 基线更新流程

遵循项目现有的基线管理规范，通过独立的workflow_dispatch触发：

**文件**: `.github/workflows/visual-baseline-update.yml`

```yaml
name: Visual Baseline Update

on:
  workflow_dispatch:
    inputs:
      scope:
        description: 'Update scope'
        required: true
        type: choice
        options:
          - all
          - pages
          - components
      reason:
        description: 'Reason for update'
        required: true
        type: string

jobs:
  update-baselines:
    name: Update Visual Baselines
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          ref: ${{ github.ref }}

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: '8'

      - name: Install dependencies
        working-directory: ./web/frontend
        run: pnpm install --frozen-lockfile

      - name: Install Playwright browsers
        run: pnpm exec playwright install --with-deps chromium

      - name: Start frontend dev server
        working-directory: ./web/frontend
        run: |
          pnpm run dev &
          sleep 15

      - name: Update visual baselines
        working-directory: ./
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          BASELINE_SCOPE: ${{ github.event.inputs.scope }}
        run: |
          echo "📸 Updating visual baselines (scope: $BASELINE_SCOPE)"
          echo "Reason: ${{ github.event.inputs.reason }}"
          echo ""
          
          # 根据scope选择更新范围
          case "$BASELINE_SCOPE" in
            all)
              pnpm exec playwright test --config=tests/visual/config/visual.config.ts --update-snapshots
              ;;
            pages)
              pnpm exec playwright test --config=tests/visual/config/visual.config.ts --update-snapshots --project=visual-p0,visual-p1
              ;;
            components)
              pnpm exec playwright test --config=tests/visual/config/visual.config.ts --update-snapshots --project=visual-p1
              ;;
          esac

      - name: Commit updated baselines
        run: |
          # 检查是否有新的基线文件
          if git status --porcelain | grep -q "test-results/baseline"; then
            echo "📝 Committing updated baselines..."
            git config user.name "github-actions[bot]"
            git config user.email "github-actions[bot]@users.noreply.github.com"
            git add test-results/baseline/
            git commit -m "chore: update visual baselines

Reason: ${{ github.event.inputs.reason }}

Updated by: ${{ github.actor }}
Branch: ${{ github.ref_name }}"
            git push
            echo "✅ Baselines committed and pushed"
          else
            echo "✅ No baseline changes detected"
          fi

      - name: Cleanup
        if: always()
        run: |
          pkill -f "pnpm run dev" || true
```

### GitLab CI配置

**文件**: `.gitlab-ci.yml` (追加)

遵循现有的stage命名规范：

```yaml
# Visual Testing Stage
.visual-testing:
  stage: visual
  image: node:20
  before_script:
    - pnpm ci
    - pnpm exec playwright install --with-deps chromium
  script:
    - pnpm exec playwright test --config=tests/visual/config/visual.config.ts
  artifacts:
    when: always
    paths:
      - test-results/
      - test-results/visual-report/
    expire_in: 30 days
  only:
    changes:
      - web/frontend/src/**
      - tests/visual/**
    refs:
      - main
      - develop
      - merge_requests

.visual-baseline-update:
  stage: visual
  image: node:20
  before_script:
    - pnpm ci
    - pnpm exec playwright install --with-deps chromium
  script:
    - pnpm exec playwright test --config=tests/visual/config/visual.config.ts --update-snapshots
  artifacts:
    when: always
    paths:
      - test-results/baseline/
  only:
    - schedules
```

### CI/CD性能监控

遵循CICD_CONTINUOUS_OPTIMIZATION.md的性能目标：

| 指标 | 目标值 | 告警阈值 | 监控方式 |
|------|--------|----------|----------|
| 视觉测试执行时间 | < 15分钟 | > 20分钟 | GitHub Actions |
| 测试通过率 | > 95% | < 90% | 测试报告 |
| 基线更新成功率 | > 98% | < 95% | 工作流日志 |

### 与现有测试框架集成

#### 1. 测试结果汇总

视觉测试结果与现有测试报告系统集成：

```typescript
// tests/visual/utils/test-result-aggregator.ts

import { VisualTestResult } from './types';

export interface AggregatedTestResult {
  total: number;
  passed: number;
  failed: number;
  skipped: number;
  passRate: number;
  duration: number;
  timestamp: string;
}

export async function aggregateVisualResults(): Promise<AggregatedTestResult> {
  // 从test-results/test-results.json读取结果
  // 转换为统一格式
  // 与现有测试报告系统集成
}
```

#### 2. 通知集成

视觉测试结果通过现有通知渠道发送：

```typescript
// tests/visual/utils/notification.ts

import { sendNotification } from '../utils/notification';

export async function notifyVisualTestResult(
  result: 'passed' | 'failed',
  details: string
): Promise<void> {
  await sendNotification({
    title: result === 'passed' 
      ? '✅ Visual Tests Passed' 
      : '❌ Visual Tests Failed',
    message: result === 'passed'
      ? 'All visual regression tests passed successfully'
      : `Visual regression tests failed with ${details}`,
    status: result,
    details: details,
  });
}
```

### 故障恢复策略

遵循项目的故障恢复规范：

| 场景 | 处理策略 |
|------|---------|
| 测试超时 | 增加超时时间至30分钟，重试1次 |
| 截图失败 | 重试3次，记录详细日志 |
| 基线更新失败 | 回滚到上一版本，记录问题 |
| 服务启动失败 | 检查端口占用，重试启动 |
| 网络超时 | 增加等待时间至30秒 |
        default: 'development'
        type: choice
        options:
          - development
          - staging
          - production

jobs:
  update-baselines:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        working-directory: ./web/frontend
        run: pnpm install --frozen-lockfile
      
      - name: Install Playwright
        run: pnpm exec playwright install --with-deps chromium
      
      - name: Start server
        working-directory: ./web/frontend
        run: |
          pnpm run dev &
          sleep 15
      
      - name: Update baselines
        working-directory: ./
        env:
          E2E_BASE_URL: 'http://localhost:3000'
        run: |
          pnpm exec playwright test --config=tests/visual/config/visual.config.ts --update-snapshots
      
      - name: Commit updated baselines
        if: github.event.inputs.environment == 'production'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add test-results/baseline/
          git commit -m "Update visual baselines - $(date +%Y-%m-%d)"
          git push
```

---

## 报告与监控

### HTML报告

Playwright内置HTML报告提供:
- 测试概览
- 失败详情
- 截图对比
- 差异高亮

报告位置: `test-results/visual-report/index.html`

### 自定义报告生成

**文件**: `tests/visual/utils/report-generator.ts`

```typescript
import * as fs from 'fs';
import * as path from 'path';

interface VisualTestResult {
  testName: string;
  status: 'passed' | 'failed';
  baselinePath: string;
  currentPath: string;
  diffPath?: string;
  diffRatio: number;
  timestamp: string;
}

export class VisualReportGenerator {
  private results: VisualTestResult[] = [];
  
  addResult(result: VisualTestResult): void {
    this.results.push(result);
  }
  
  generateHtmlReport(outputPath: string): void {
    const html = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Visual Regression Test Report</title>
  <style>
    body { font-family: 'Barlow', sans-serif; background: #0A0A0A; color: #F2F0E4; }
    .container { max-width: 1400px; margin: 0 auto; padding: 24px; }
    h1 { color: #D4AF37; font-family: 'Cinzel', serif; }
    .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }
    .card { background: #1A1A1A; padding: 16px; border-radius: 8px; border: 1px solid #333; }
    .card.passed { border-color: #00E676; }
    .card.failed { border-color: #FF5252; }
    .card h3 { margin: 0; font-size: 14px; color: #A0A0A0; }
    .card .value { font-size: 32px; font-weight: bold; color: #D4AF37; }
    .test-item { background: #1A1A1A; padding: 16px; margin-bottom: 8px; border-radius: 8px; }
    .test-item.passed { border-left: 4px solid #00E676; }
    .test-item.failed { border-left: 4px solid #FF5252; }
    .test-name { font-weight: bold; }
    .test-details { margin-top: 8px; font-size: 14px; color: #A0A0A0; }
    .screenshots { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 16px; }
    .screenshot { background: #0A0A0A; padding: 8px; border-radius: 4px; }
    .screenshot img { max-width: 100%; height: auto; }
    .diff-overlay { position: relative; }
    .diff-overlay img { position: absolute; top: 0; left: 0; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🎨 Visual Regression Test Report</h1>
    <p>Generated: ${new Date().toLocaleString('zh-CN')}</p>
    
    <div class="summary">
      <div class="card">
        <h3>Total Tests</h3>
        <div class="value">${this.results.length}</div>
      </div>
      <div class="card passed">
        <h3>Passed</h3>
        <div class="value">${this.results.filter(r => r.status === 'passed').length}</div>
      </div>
      <div class="card failed">
        <h3>Failed</h3>
        <div class="value">${this.results.filter(r => r.status === 'failed').length}</div>
      </div>
      <div class="card">
        <h3>Pass Rate</h3>
        <div class="value">${((this.results.filter(r => r.status === 'passed').length / this.results.length) * 100).toFixed(1)}%</div>
      </div>
    </div>
    
    <h2>Test Results</h2>
    ${this.results.map(result => `
      <div class="test-item ${result.status}">
        <div class="test-name">${result.testName}</div>
        <div class="test-details">
          Status: ${result.status.toUpperCase()} | 
          Diff: ${(result.diffRatio * 100).toFixed(2)}% | 
          Time: ${result.timestamp}
        </div>
        <div class="screenshots">
          <div class="screenshot">
            <h4>Baseline</h4>
            <img src="${path.relative(outputPath, result.baselinePath)}" />
          </div>
          <div class="screenshot">
            <h4>Current</h4>
            <img src="${path.relative(outputPath, result.currentPath)}" />
          </div>
          ${result.diffPath ? `
            <div class="screenshot">
              <h4>Diff</h4>
              <img src="${path.relative(outputPath, result.diffPath)}" />
            </div>
          ` : ''}
        </div>
      </div>
    `).join('')}
  </div>
</body>
</html>
    `;
    
    fs.writeFileSync(outputPath, html);
  }
  
  generateJsonReport(outputPath: string): void {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        total: this.results.length,
        passed: this.results.filter(r => r.status === 'passed').length,
        failed: this.results.filter(r => r.status === 'failed').length,
        passRate: this.results.length > 0 
          ? (this.results.filter(r => r.status === 'passed').length / this.results.length * 100).toFixed(2)
          : 0,
      },
      results: this.results,
    };
    
    fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
  }
}
```

### Slack/钉钉通知

```typescript
// tests/visual/utils/notification.ts

import axios from 'axios';

interface NotificationPayload {
  title: string;
  message: string;
  status: 'success' | 'failure' | 'warning';
  details?: string;
  url?: string;
}

export async function sendNotification(payload: NotificationPayload): Promise<void> {
  const webhookUrl = process.env.SLACK_WEBHOOK_URL || process.env.DINGDING_WEBHOOK_URL;
  
  if (!webhookUrl) {
    console.log('📢 Notification skipped: No webhook URL configured');
    return;
  }
  
  const color = payload.status === 'success' ? '#00E676' 
    : payload.status === 'failure' ? '#FF5252' 
    : '#F0E68C';
  
  const blocks = [
    {
      type: 'header',
      text: {
        type: 'plain_text',
        text: `🎨 ${payload.title}`,
        emoji: true,
      },
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: payload.message,
      },
    },
    {
      type: 'context',
      elements: [
        {
          type: 'mrkdwn',
          text: `*Status:* ${payload.status.toUpperCase()}`,
        },
      ],
    },
  ];
  
  if (payload.details) {
    blocks.push({
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*Details:*\n${payload.details}`,
      },
    });
  }
  
  if (payload.url) {
    blocks.push({
      type: 'action',
      elements: [
        {
          type: 'button',
          text: {
            type: 'plain_text',
            text: 'View Report',
            emoji: true,
          },
          url: payload.url,
        },
      ],
    });
  }
  
  try {
    await axios.post(webhookUrl, { blocks });
    console.log('✅ Notification sent successfully');
  } catch (error) {
    console.error('❌ Failed to send notification:', error);
  }
}
```

### 监控指标

| 指标 | 描述 | 告警阈值 |
|------|------|---------|
| 测试通过率 | 通过的测试占比 | < 95% |
| 失败数量 | 视觉回归失败的测试数 | > 5 |
| 首次失败时间 | 第一次失败出现的提交 | 记录SHA |
| 重复失败率 | 连续失败的比例 | > 20% |

---

## 最佳实践

### 1. 稳定的测试环境

```typescript
// 确保环境一致性
test.use({
  // 固定视口
  viewport: { width: 1920, height: 1080 },
  
  // 固定区域设置
  locale: 'zh-CN',
  timezoneId: 'Asia/Shanghai',
  
  // 禁用地理定位
  geolocation: undefined,
  
  // 禁用权限提示
  permissions: [],
});
```

### 2. 等待策略

```typescript
// 推荐的等待模式
test.beforeEach(async ({ page }) => {
  // 1. 等待网络空闲
  await page.waitForLoadState('networkidle');
  
  // 2. 等待关键元素
  await page.waitForSelector('#dashboard-content', { state: 'visible' });
  
  // 3. 等待图表渲染完成
  await page.waitForFunction(() => {
    const charts = document.querySelectorAll('.echarts');
    return Array.from(charts).every(chart => {
      const canvas = chart.querySelector('canvas');
      return canvas && canvas.width > 0;
    });
  }, { timeout: 30000 });
});
```

### 3. 处理动态内容

```typescript
// 使用toHaveScreenshot的ignore选项
await expect(page).toHaveScreenshot('page.png', {
  ignore: [
    // 忽略动态区域
    '.timestamp',
    '.live-data',
    '.loading-spinner',
  ],
});

// 或使用locator定位特定区域
const stableArea = page.locator('.chart-container').first();
await expect(stableArea).toHaveScreenshot('chart-only.png');
```

### 4. 定期更新基线

```bash
# 每周更新基线
pnpm exec playwright test --config=tests/visual/config/visual.config.ts --update-snapshots

# 或通过CI手动触发
# GitHub Actions: 运行 "Update Visual Baselines" 工作流
```

### 5. 处理Flaky测试

```typescript
// 增加重试次数
test.describe.configure({
  retries: 3,
  timeout: 60000,
});

// 对不稳定测试增加等待
test('Flaky chart test', async ({ page }) => {
  const chart = page.locator('#chart');
  
  // 多次尝试截图
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      await page.waitForSelector('#chart canvas', { timeout: 10000 });
      await expect(chart).toHaveScreenshot(`chart-${attempt}.png`);
      break;
    } catch (error) {
      if (attempt === 3) throw error;
      await page.waitForTimeout(1000);
    }
  }
});
```

---

## 实施路线图

### Phase 1: 基础设施 (1周)

| 任务 | 负责人 | 状态 |
|------|--------|------|
| 创建tests/visual目录结构 | 待定 | ⏳ |
| 实现visual.config.ts | 待定 | ⏳ |
| 实现基础测试夹具 | 待定 | ⏳ |
| 实现Dashboard页面测试 | 待定 | ⏳ |

**产出**:
- 完整的测试目录结构
- 基础配置文件
- Dashboard页面视觉测试

### Phase 2: 核心测试 (1周)

| 任务 | 负责人 | 状态 |
|------|--------|------|
| Technical Analysis页面测试 | 待定 | ℽ |
| Trade Management页面测试 | 待定 | ℽ |
| 所有P0组件测试 | 待定 | ℽ |
| 响应式测试配置 | 待定 | ℽ |

**产出**:
- 所有P0页面和组件的视觉测试
- 响应式测试配置

### Phase 3: 完整覆盖 (1周)

| 任务 | 负责人 | 状态 |
|------|--------|------|
| P1组件测试 | 待定 | ℽ |
| P2组件测试 | 待定 | ℽ |
| 基线管理工具 | 待定 | ℽ |
| 报告生成器 | 待定 | ℽ |

**产出**:
- 完整的视觉测试覆盖
- 自定义报告生成
- 基线管理工具

### Phase 4: CI/CD集成 (3天)

| 任务 | 负责人 | 状态 |
|------|--------|------|
| GitHub Actions工作流 | 待定 | ℽ |
| 基线更新流程 | 待定 | ℽ |
| 通知集成 | 待定 | ℽ |
| 文档完善 | 待定 | ℽ |

**产出**:
- 自动化CI/CD流程
- 通知机制
- 完整文档

### Phase 5: 运维优化 (持续)

| 任务 | 频率 |
|------|------|
| 基线更新 | 每周 |
| 测试审查 | 每月 |
| 阈值优化 | 按需 |
| 新组件添加 | 按需 |

### 资源估算

| 阶段 | 时间 | 工作量 |
|------|------|--------|
| Phase 1 | 1周 | 20人时 |
| Phase 2 | 1周 | 30人时 |
| Phase 3 | 1周 | 25人时 |
| Phase 4 | 3天 | 15人时 |
| **合计** | **4周** | **~90人时** |

---

## 附录

### A. 快速开始指南

```bash
# 1. 安装依赖
cd web/frontend && pnpm install

# 2. 安装Playwright浏览器
pnpm exec playwright install --with-deps chromium

# 3. 初始化测试目录
node tests/visual/utils/baseline-manager.ts init

# 4. 启动开发服务器
pnpm run dev &

# 5. 运行测试
pnpm exec playwright test --config=tests/visual/config/visual.config.ts

# 6. 更新基线（如需要）
pnpm exec playwright test --config=tests/visual/config/visual.config.ts --update-snapshots
```

### B. 故障排除

| 问题 | 解决方案 |
|------|---------|
| 测试超时 | 增加waitForSelector超时时间 |
| 截图不一致 | 检查动画是否已禁用 |
| 内存不足 | 减少并行测试数 |
| 基线丢失 | 从CI artifacts恢复 |

### C. 相关文档

| 文档 | 路径 |
|------|------|
| Playwright官方文档 | https://playwright.dev/ |
| 视觉测试指南 | https://playwright.dev/docs/test-snapshots |
| ECharts官方文档 | https://echarts.apache.org/ |
| ArtDeco V3.0设计令牌 | `web/frontend/src/styles/artdeco-tokens.scss` |

---

**文档版本**: 1.0
**创建日期**: 2026-01-25
**维护者**: Claude Code (ArtDeco V3.0 Upgrade Project)
**下次审查**: 2026-02-25
