import { test, expect } from '@playwright/test';
import path from 'path';

// 设置前端端口为3001（因为3000被占用）
test.use({
  baseURL: 'http://localhost:3001'
});

test.describe('MyStocks Web Redesign - Monitoring Pages', () => {
  test.setTimeout(60000); // 60秒超时

  test.beforeEach(async ({ page }) => {
    // 等待服务启动
    await page.waitForTimeout(2000);
  });

  test('1. WatchlistManagement Page - Bloomberg Redesign Test', async ({ page }) => {
    console.log('🧪 Testing WatchlistManagement page...');

    // 导航到监控清单页面
    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('networkidle');

    // 等待页面加载完成
    await page.waitForTimeout(3000);

    // 截图1: 页面整体布局
    await page.screenshot({
      path: 'test-results/screenshots/01-watchlist-management-full.png',
      fullPage: true
    });

    // 检查标题栏是否存在
    const titleElement = page.locator('h1').filter({ hasText: 'MONITORING PORTFOLIOS' });
    await expect(titleElement).toBeVisible();

    // 检查统计卡片
    const statCards = page.locator('.stat-card');
    await expect(statCards).toHaveCount(3); // 活跃组合、总股票、活跃告警

    // 截图2: 统计卡片区域
    await statCards.first().screenshot({
      path: 'test-results/screenshots/01-watchlist-stats-cards.png'
    });

    // 检查CREATE PORTFOLIO按钮
    const createButton = page.locator('.fintech-btn.primary').filter({ hasText: 'CREATE PORTFOLIO' });
    await expect(createButton).toBeVisible();

    // 点击创建按钮，检查弹窗
    await createButton.click();
    await page.waitForTimeout(500);

    const modal = page.locator('.modal');
    await expect(modal).toBeVisible();

    // 截图3: 创建弹窗
    await modal.screenshot({
      path: 'test-results/screenshots/01-watchlist-create-modal.png'
    });

    // 关闭弹窗
    const closeButton = modal.locator('.modal-close');
    await closeButton.click();

    console.log('✅ WatchlistManagement page test completed');
  });

  test('2. RiskDashboard Page - Bloomberg Redesign Test', async ({ page }) => {
    console.log('🧪 Testing RiskDashboard page...');

    // 导航到风险监控页面
    await page.goto('/monitoring/risk');
    await page.waitForLoadState('networkidle');

    // 等待页面加载完成
    await page.waitForTimeout(3000);

    // 截图1: 页面整体布局
    await page.screenshot({
      path: 'test-results/screenshots/02-risk-dashboard-full.png',
      fullPage: true
    });

    // 检查标题
    const titleElement = page.locator('h1').filter({ hasText: 'RISK MANAGEMENT DASHBOARD' });
    await expect(titleElement).toBeVisible();

    // 检查核心指标卡片 (4个)
    const metricCards = page.locator('.metric-card');
    await expect(metricCards).toHaveCount(4);

    // 截图2: 核心指标区域
    const metricsGrid = page.locator('.metrics-grid');
    await metricsGrid.screenshot({
      path: 'test-results/screenshots/02-risk-metrics-grid.png'
    });

    // 检查告警面板
    const alertPanels = page.locator('.alert-panel');
    await expect(alertPanels).toHaveCount(3); // 紧急、风险、优化

    // 截图3: 告警面板
    const alertsSection = page.locator('.alerts-section');
    await alertsSection.screenshot({
      path: 'test-results/screenshots/02-risk-alerts-section.png'
    });

    // 检查分析面板
    const analysisPanels = page.locator('.analysis-panel');
    await expect(analysisPanels).toHaveCount(3); // 再平衡、行业配置、风险指标

    // 截图4: 分析面板
    const analysisSection = page.locator('.analysis-section');
    await analysisSection.screenshot({
      path: 'test-results/screenshots/02-risk-analysis-section.png'
    });

    console.log('✅ RiskDashboard page test completed');
  });

  test('3. HealthRadarChart Component Test', async ({ page }) => {
    console.log('🧪 Testing HealthRadarChart component...');

    // 导航到包含雷达图的页面（通过风险面板）
    await page.goto('/monitoring/risk');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    // 查找雷达图容器
    const radarContainer = page.locator('.radar-container');
    await expect(radarContainer).toBeVisible();

    // 截图1: 雷达图区域
    await radarContainer.screenshot({
      path: 'test-results/screenshots/03-health-radar-chart.png'
    });

    // 检查图例
    const legendPanel = page.locator('.legend-panel');
    await expect(legendPanel).toBeVisible();

    // 截图2: 图例面板
    await legendPanel.screenshot({
      path: 'test-results/screenshots/03-health-radar-legend.png'
    });

    // 检查底部统计
    const footerStats = page.locator('.footer-stats');
    await expect(footerStats).toBeVisible();

    // 截图3: 底部统计
    await footerStats.screenshot({
      path: 'test-results/screenshots/03-health-radar-footer.png'
    });

    console.log('✅ HealthRadarChart component test completed');
  });

  test('4. Shared Components Integration Test', async ({ page }) => {
    console.log('🧪 Testing shared components integration...');

    // 测试多个页面中共享组件的使用
    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // 检查fintech-btn类是否存在
    const fintechButtons = page.locator('.fintech-btn');
    await expect(fintechButtons.first()).toBeVisible();

    // 检查fintech-card类是否存在
    const fintechCards = page.locator('.fintech-card');
    await expect(fintechCards.first()).toBeVisible();

    // 检查文本颜色类
    const primaryText = page.locator('.fintech-text-primary');
    await expect(primaryText.first()).toBeVisible();

    // 截图: 样式系统验证
    await page.screenshot({
      path: 'test-results/screenshots/04-fintech-styles-integration.png',
      fullPage: true
    });

    console.log('✅ Shared components integration test completed');
  });

  test('5. Responsive Design Test', async ({ page }) => {
    console.log('🧪 Testing responsive design...');

    // 设置视口为桌面尺寸
    await page.setViewportSize({ width: 1920, height: 1080 });

    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // 截图1: 桌面尺寸
    await page.screenshot({
      path: 'test-results/screenshots/05-responsive-desktop.png',
      fullPage: true
    });

    // 设置为平板尺寸
    await page.setViewportSize({ width: 1024, height: 768 });

    await page.waitForTimeout(1000);

    // 截图2: 平板尺寸
    await page.screenshot({
      path: 'test-results/screenshots/05-responsive-tablet.png'
    });

    console.log('✅ Responsive design test completed');
  });

  test('6. Dark Theme Consistency Test', async ({ page }) => {
    console.log('🧪 Testing dark theme consistency...');

    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // 检查深色背景类
    const darkBg = page.locator('.fintech-bg-primary');
    await expect(darkBg).toBeVisible();

    // 检查高对比度文字
    const primaryText = page.locator('.fintech-text-primary');
    await expect(primaryText.first()).toBeVisible();

    // 截图: 深色主题验证
    await page.screenshot({
      path: 'test-results/screenshots/06-dark-theme-consistency.png',
      fullPage: true
    });

    console.log('✅ Dark theme consistency test completed');
  });

  test('7. Performance and Loading Test', async ({ page }) => {
    console.log('🧪 Testing performance and loading...');

    const startTime = Date.now();

    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;
    console.log(`📊 Page load time: ${loadTime}ms`);

    // 验证关键元素加载
    await expect(page.locator('h1')).toBeVisible({ timeout: 10000 });

    // 截图: 加载完成状态
    await page.screenshot({
      path: 'test-results/screenshots/07-performance-loading.png'
    });

    // 记录性能指标
    const performance = await page.evaluate(() => {
      const perfData = performance.getEntriesByType('navigation')[0];
      return {
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        loadComplete: perfData.loadEventEnd - perfData.loadEventStart
      };
    });

    console.log(`📊 DOM Content Loaded: ${performance.domContentLoaded}ms`);
    console.log(`📊 Load Complete: ${performance.loadComplete}ms`);

    console.log('✅ Performance and loading test completed');
  });
});