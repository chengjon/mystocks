/**
 * 仪表盘页面端到端测试
 *
 * 测试范围:
 * 1. 仪表盘页面加载和渲染
 * 2. 市场统计数据显示
 * 3. 图表功能和交互
 * 4. 数据刷新和实时更新
 *
 * 作者: Claude Code
 * 生成时间: 2025-11-14
 */

import { test, expect, type Page } from '@playwright/test';
import { DashboardPage } from '../utils/page-objects/part-1';
import {
  UserAuth,
  ScreenshotHelper,
  PerformanceTester,
  UIHelper,
  MockDataHelper
} from '../utils/test-helpers';
import { performance } from '../playwright.config';

const DEMO_ADMIN = {
  username: 'admin',
  password: 'admin123',
};

async function loginToCurrentDashboard(page: Page) {
  await page.goto('/login', { waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('heading', { name: 'LOGIN' })).toBeVisible();
  await page.getByTestId('username-input').fill(DEMO_ADMIN.username);
  await page.getByTestId('password-input').fill(DEMO_ADMIN.password);

  await page.getByTestId('login-button').click();

  await expect(page.getByRole('heading', { name: '量化驾驶舱' })).toBeVisible({ timeout: 45_000 });
  await expect(page).toHaveURL(/\/dashboard$/);
}

test.describe('仪表盘功能 - 当前浏览器冒烟', () => {
  test.describe.configure({ mode: 'serial' });

  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.clear();
      window.sessionStorage.clear();
    });

    await loginToCurrentDashboard(page);
  });

  test('仪表盘主 shell 与内容区正常渲染', async ({ page }) => {
    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.locator('.app-shell')).toBeVisible();
    await expect(page.locator('.artdeco-sidebar-v3')).toBeVisible();
    await expect(page.getByRole('heading', { name: '量化驾驶舱' })).toBeVisible();
    await expect(page.getByText('QUANTIX · 实时洞察 · 策略执行')).toBeVisible();
  });

  test('主业务域导航入口保持可见', async ({ page }) => {
    for (const label of ['市场行情', '数据分析', '自选管理', '策略管理', '交易管理', '风险管理', '系统设置']) {
      await expect(page.getByText(label, { exact: true }).first()).toBeVisible();
    }
  });

  test('当前 dashboard 运行时面板保持主线真值', async ({ page }) => {
    await expect(page.getByText('市场资金流向概览')).toBeVisible();
    await expect(page.getByText('主要市场指标')).toBeVisible();
    await expect(page.getByText('技术指标概览')).toBeVisible();
    await expect(page.getByText('快速导航')).toBeVisible();
    await expect(page.getByText('自选池真实接口尚未接入')).toBeVisible();
  });

  test('刷新动作存在且不会破坏页面主结构', async ({ page }) => {
    await page.getByRole('button', { name: '刷新数据' }).click();

    await expect(page.getByRole('heading', { name: '量化驾驶舱' })).toBeVisible();
    await expect(page.locator('.artdeco-sidebar-v3')).toBeVisible();
  });

  test('快速导航卡片覆盖核心业务域', async ({ page }) => {
    for (const label of ['实时报价与技术分析', '自选股与投资组合', '深度数据分析工具', '信号到订单的闭环', '量化策略开发平台', '实时风险评估系统']) {
      await expect(page.getByText(label)).toBeVisible();
    }
  });

  test('当前主线不再暴露旧 mock 股票表格契约', async ({ page }) => {
    await expect(page.locator('[data-testid=favorite-stocks-table]')).toHaveCount(0);
    await expect(page.getByText('当前页面不再展示 mock 股票数据')).toBeVisible();
  });

  test('窄屏下 dashboard 仍保留主内容与侧边导航', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });

    await expect(page.getByRole('heading', { name: '量化驾驶舱' })).toBeVisible();
    await expect(page.locator('.artdeco-sidebar-v3')).toBeVisible();
    await expect(page.getByText('刷新数据')).toBeVisible();
  });
});

test.describe.skip('仪表盘功能（legacy stale contract）', () => {
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);

    // Phase 11.1 修复: 使用 addInitScript 在页面上下文中安全操作 localStorage
    await page.addInitScript(() => {
      try {
        // 清空本地存储确保测试隔离
        localStorage.clear();
        // 模拟已登录状态，直接设置测试token
        localStorage.setItem('token', 'test-auth-token-for-phase11-1');
        console.log('localStorage cleared and test token set successfully via addInitScript');
      } catch (error) {
        console.log('localStorage not available, using fallback storage');
        // 如果localStorage不可用，设置内存存储
        (window as any).testStorage = { // TODO owner=frontend-platform issue=techdebt-expired-markers ttl=2026-06-30: replace any with typed window test storage
          token: 'test-auth-token-for-phase11-1'
        };
      }
    });

    // Phase 11.1 修复: 验证localStorage访问已修复 - 直接导航到dashboard测试页面功能
    // 绕过登录流程，专注验证localStorage修复效果
    console.log('Phase 11.1: localStorage fix validated, navigating directly to dashboard');
    await dashboardPage.navigate();
  });

  test('Phase 11.1 localStorage修复验证', async ({ page }) => {
    // Phase 11.1 专门验证localStorage修复的测试
    console.log('🔧 Phase 11.1: 验证localStorage访问修复...');

    // 验证页面可以正常导航（无localStorage错误）
    await page.goto('/dashboard');

    // 验证页面加载（URL包含dashboard）
    await expect(page).toHaveURL(/dashboard/);

    // Phase 11.1 成功标准：无localStorage安全错误，页面可正常访问
    console.log('✅ Phase 11.1 localStorage修复验证成功 - 无安全错误');

    // 简单验证页面内容存在
    const bodyVisible = await page.locator('body').isVisible();
    expect(bodyVisible).toBe(true);

    // 验证localStorage操作可以在页面上下文中执行
    const localStorageTest = await page.evaluate(() => {
      try {
        const testValue = 'phase-11-1-test';
        localStorage.setItem('test-key', testValue);
        const retrievedValue = localStorage.getItem('test-key');
        localStorage.removeItem('test-key');
        return retrievedValue === testValue;
      } catch (error) {
        return false;
      }
    });

    expect(localStorageTest).toBe(true);
    console.log('✅ Phase 11.1 localStorage读写操作验证成功');
  });

  test('仪表盘页面正常加载', async ({ page }) => {
    await dashboardPage.navigate();

    // 验证页面基本元素
    await expect(dashboardPage.welcomeMessage).toBeVisible();
    await expect(dashboardPage.marketStatsCards).toBeVisible();

    // 验证统计卡片数量
    const statsCount = await dashboardPage.getStatsCardCount();
    expect(statsCount).toBe(4);

    // 验证页面标题
    const title = await page.title();
    expect(title).toContain('仪表盘');

    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'dashboard-page-loaded');
  });

  test('仪表盘性能测试', async ({ page }) => {
    // 执行性能基准测试
    const result = await PerformanceTester.validatePerformance(
      page,
      '/dashboard',
      performance.budgets
    );

    expect(result.passed).toBeTruthy();

    if (result.violations.length > 0) {
      console.log('⚠️ Performance violations:', result.violations);
    }

    console.log('📊 Dashboard performance metrics:', result.metrics);

    // 截图保存性能报告
    await ScreenshotHelper.takeScreenshot(page, 'dashboard-performance-test');
  });

  test('市场统计数据显示', async ({ page }) => {
    await dashboardPage.navigate();

    // 验证统计卡片数据加载
    const statsCards = page.locator('[data-testid=stat-card]');
    const count = await statsCards.count();

    expect(count).toBeGreaterThan(0);

    // 验证每个统计卡片都有数据
    for (let i = 0; i < count; i++) {
      const card = statsCards.nth(i);
      await expect(card.locator('[data-testid=stat-value]')).toBeVisible();
      await expect(card.locator('[data-testid=stat-title]')).toBeVisible();
    }

    // 验证具体统计数据
    const firstCardValue = await page.locator('[data-testid=stat-card] [data-testid=stat-value]').first().textContent();
    expect(firstCardValue).toBeTruthy();
    expect(firstCardValue).not.toBe('0');

    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'market-stats-displayed');
  });

  test('图表加载和显示', async ({ page }) => {
    await dashboardPage.navigate();

    // 等待图表加载
    await UIHelper.waitForElementVisible(page, '[data-testid=market-heat-chart]');

    // 验证所有图表都可见
    const chartsVisible = await dashboardPage.areChartsVisible();
    expect(chartsVisible).toBeTruthy();

    // 验证市场热度图表
    await expect(page.locator('[data-testid=market-heat-chart] canvas')).toBeVisible();

    // 验证领涨板块图表
    await expect(page.locator('[data-testid=leading-sector-chart] canvas')).toBeVisible();

    // 验证涨跌分布图表
    await expect(page.locator('[data-testid=price-distribution-chart] canvas')).toBeVisible();

    // 验证资金流向图表
    await expect(page.locator('[data-testid=capital-flow-chart] canvas')).toBeVisible();

    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'charts-loaded');
  });

  test('图表交互功能', async ({ page }) => {
    await dashboardPage.navigate();
    await UIHelper.waitForElementVisible(page, '[data-testid=market-heat-chart]');

    // 测试市场热度图表交互
    await page.hover('[data-testid=market-heat-chart] canvas');

    // 等待图表提示显示
    await page.waitForTimeout(1000);

    // 测试切换标签页
    await page.click('[data-testid=tab-leading]');
    await expect(page.locator('[data-testid=leading-sector-chart]')).toBeVisible();

    await page.click('[data-testid=tab-distribution]');
    await expect(page.locator('[data-testid=price-distribution-chart]')).toBeVisible();

    await page.click('[data-testid=tab-capital]');
    await expect(page.locator('[data-testid=capital-flow-chart]')).toBeVisible();

    // 测试Tab切换动画
    await page.click('[data-testid=tab-heat]');
    await expect(page.locator('[data-testid=market-heat-chart]')).toBeVisible();

    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'chart-interactions');
  });

  test('数据表格加载和显示', async ({ page }) => {
    await dashboardPage.navigate();

    // 验证表格数据加载
    const tablesLoaded = await dashboardPage.areTablesLoaded();
    expect(tablesLoaded).toBeTruthy();

    // 验证自选股表格
    await expect(page.locator('[data-testid=favorite-stocks-table] tbody tr')).toHaveCount(5);

    // 验证表格列标题
    const favoriteTableHeaders = page.locator('[data-testid=favorite-stocks-table] thead th');
    await expect(favoriteTableHeaders.nth(0)).toContainText('代码');
    await expect(favoriteTableHeaders.nth(1)).toContainText('名称');
    await expect(favoriteTableHeaders.nth(2)).toContainText('现价');
    await expect(favoriteTableHeaders.nth(3)).toContainText('涨跌幅');

    // 验证自选股数据
    const favoriteStocksData = await dashboardPage.getFavoriteStocksData();
    expect(favoriteStocksData.length).toBeGreaterThan(0);

    // 验证数据格式
    const firstStock = favoriteStocksData[0];
    expect(firstStock.symbol).toMatch(/^\d{6}$/);
    expect(firstStock.price).toMatch(/^\d+\.?\d*$/);
    expect(firstStock.change).toMatch(/^[-+]?\d+\.?\d*%$/);

    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'data-tables-loaded');
  });

  test('表格标签页切换', async ({ page }) => {
    await dashboardPage.navigate();

    // 默认在自选股标签
    await expect(page.locator('[data-testid=tab-favorites]')).toHaveClass(/is-active/);
    await expect(page.locator('[data-testid=favorite-stocks-table]')).toBeVisible();

    // 切换到策略选股标签
    await page.click('[data-testid=tab-strategy]');
    await expect(page.locator('[data-testid=strategy-stocks-table]')).toBeVisible();
    await expect(page.locator('[data-testid=tab-strategy]')).toHaveClass(/is-active/);

    // 切换到行业选股标签
    await page.click('[data-testid=tab-industry]');
    await expect(page.locator('[data-testid=industry-stocks-table]')).toBeVisible();
    await expect(page.locator('[data-testid=tab-industry]')).toHaveClass(/is-active/);

    // 切换到概念选股标签
    await page.click('[data-testid=tab-concept]');
    await expect(page.locator('[data-testid=concept-stocks-table]')).toBeVisible();
    await expect(page.locator('[data-testid=tab-concept]')).toHaveClass(/is-active/);

    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'table-tabs-switching');
  });

  test('数据刷新功能', async ({ page }) => {
    await dashboardPage.navigate();

    // 获取初始数据
    const initialData = await dashboardPage.getFavoriteStocksData();

    // 点击刷新按钮
    await dashboardPage.clickRefresh();

    // 等待刷新完成
    await page.waitForTimeout(2000);

    // 获取刷新后的数据
    const refreshedData = await dashboardPage.getFavoriteStocksData();

    // 验证数据结构一致（Mock数据系统会生成新数据）
    expect(refreshedData.length).toBe(initialData.length);
    expect(refreshedData[0]).toHaveProperty('symbol');
    expect(refreshedData[0]).toHaveProperty('price');

    // 验证显示成功提示
    await expect(page.locator('.el-message--success')).toBeVisible();

    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'data-refreshed');
  });

  test('实时数据更新验证', async ({ page }) => {
    await dashboardPage.navigate();

    // 记录初始时间戳
    const initialTime = await page.locator('[data-testid=last-update-time]').textContent();

    // 等待数据自动更新（默认5秒间隔）
    await page.waitForTimeout(6000);

    // 验证时间戳更新
    const updatedTime = await page.locator('[data-testid=last-update-time]').textContent();
    expect(updatedTime).not.toBe(initialTime);

    // 验证数据有变化（Mock系统会生成新数据）
    // 这里可以通过检查特定值的变化来验证

    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'real-time-updates');
  });

  test('Mock数据验证', async ({ page }) => {
    await dashboardPage.navigate();

    // 验证Mock数据格式和内容
    const marketStats = await MockDataHelper.validateMockResponse(
      page,
      async () => {
        // 模拟获取市场统计数据
        const response = await page.request.get('/api/market/dashboard/stats');
        return await response.json();
      },
      ['total_stocks', 'active_stocks', 'data_update', 'system_status']
    );

    expect(marketStats.passed).toBeTruthy();

    // 验证自选股数据Mock
    const favoriteStocks = await MockDataHelper.validateMockResponse(
      page,
      async () => {
        const response = await page.request.get('/api/market/favorites');
        return await response.json();
      },
      ['symbol', 'name', 'price', 'change']
    );

    expect(favoriteStocks.passed).toBeTruthy();

    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'mock-data-validation');
  });

  test('响应式设计测试', async ({ page }) => {
    // 测试不同屏幕尺寸
    const viewports = [
      { width: 1920, height: 1080 }, // 桌面
      { width: 1366, height: 768 },  // 小桌面
      { width: 768, height: 1024 },  // 平板
      { width: 375, height: 667 },   // 手机
    ];

    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await dashboardPage.navigate();

      // 验证布局适应性
      await expect(page.locator('.dashboard')).toBeVisible();

      // 验证统计卡片在小屏幕上换行
      if (viewport.width < 768) {
        const statsCards = page.locator('[data-testid=stat-card]');
        await expect(statsCards.first()).toBeVisible();
      }

      // 截图保存
      await ScreenshotHelper.takeScreenshot(
        page,
        `dashboard-responsive-${viewport.width}x${viewport.height}`
      );
    }
  });

  test('API响应时间测试', async ({ page }) => {
    await dashboardPage.navigate();

    // 测试主要API端点响应时间
    const apiEndpoints = [
      { name: 'Dashboard Stats', url: '/api/market/dashboard/stats', maxTime: performance.apiResponse.dashboard },
      { name: 'Favorite Stocks', url: '/api/market/favorites', maxTime: performance.apiResponse.market },
      { name: 'Market Heat', url: '/api/market/heat', maxTime: performance.apiResponse.market },
    ];

    const { results, summary } = await import('../utils/test-helpers').then(
      module => module.APITester.testMultipleAPIs(page, apiEndpoints)
    );

    expect(summary.passed).toBe(summary.total); // 所有API都应该通过

    console.log('📊 API Response Time Summary:', summary);

    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'api-response-times');
  });

  test('错误处理和边界情况', async ({ page, context }) => {
    await dashboardPage.navigate();

    // 模拟网络错误
    await context.route('**/api/market/**', route => {
      route.abort('internetdisconnected');
    });

    // 刷新页面触发API调用
    await page.reload();

    // 验证错误处理（应该显示错误状态而不是崩溃）
    await expect(page.locator('[data-testid=error-message]')).toBeVisible();

    // 恢复网络连接
    await context.unroute('**/api/market/**');

    // 再次刷新验证恢复
    await page.reload();
    await page.waitForTimeout(3000);

    await expect(page.locator('[data-testid=error-message]')).not.toBeVisible();
    await expect(dashboardPage.welcomeMessage).toBeVisible();

    // 截图保存
    await ScreenshotHelper.takeScreenshot(page, 'error-handling');
  });
});
