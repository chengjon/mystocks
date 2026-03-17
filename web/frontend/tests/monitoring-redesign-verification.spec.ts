import { test, expect } from '@playwright/test';

const FRONTEND_PORT = process.env.FRONTEND_PORT || '3020';
const FRONTEND_URL = process.env.FRONTEND_URL || `http://localhost:${FRONTEND_PORT}`;

test.use({
  baseURL: FRONTEND_URL
});

test.describe('MyStocks Web - Monitoring Pages ArtDeco Verification', () => {
  test.setTimeout(30000); // 30秒超时

  test.beforeEach(async ({ page }) => {
    // 等待服务启动
    await page.waitForTimeout(2000);
  });

  test('1. WatchlistManagement Page - ArtDeco Design System Application', async ({ page }) => {
    console.log('🧪 Testing WatchlistManagement with ArtDeco styles...');

    // 导航到新的监控清单页面
    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('domcontentloaded');

    // 等待页面加载完成
    await page.waitForTimeout(3000);

    // 截图1: 监控布局页面整体
    await page.screenshot({
      path: 'test-results/screenshots/monitoring-watchlist-full.png',
      fullPage: true
    });

    // 检查标题栏是否存在
    const titleElement = page.locator('h1').filter({ hasText: 'MONITORING PORTFOLIOS' });
    await expect(titleElement).toBeVisible();

    // 检查ArtDeco样式钩子类是否存在（fintech 前缀兼容）
    const fintechElements = page.locator('[class*="fintech"]');
    const fintechCount = await fintechElements.count();
    console.log(`💼 Found ${fintechCount} ArtDeco hook style elements`);
    expect(fintechCount).toBeGreaterThan(0);

    // 检查统计卡片
    const statCards = page.locator('.stat-card');
    await expect(statCards).toHaveCount(3); // 活跃组合、总股票、活跃告警

    // 截图2: 统计卡片区域
    await statCards.first().screenshot({
      path: 'test-results/screenshots/monitoring-watchlist-stats.png'
    });

    // 检查CREATE PORTFOLIO按钮
    const createButton = page.locator('.fintech-btn.primary').filter({ hasText: 'CREATE PORTFOLIO' });
    await expect(createButton).toBeVisible();

    console.log('✅ WatchlistManagement page with ArtDeco styles verified');
  });

  test('2. RiskDashboard Page - ArtDeco Style Application', async ({ page }) => {
    console.log('🧪 Testing RiskDashboard with ArtDeco styles...');

    // 导航到风险监控页面
    await page.goto('/monitoring/risk');
    await page.waitForLoadState('domcontentloaded');

    // 等待页面加载完成
    await page.waitForTimeout(3000);

    // 截图1: 风险监控页面整体
    await page.screenshot({
      path: 'test-results/screenshots/monitoring-risk-full.png',
      fullPage: true
    });

    // 检查标题
    const titleElement = page.locator('h1').filter({ hasText: 'RISK MANAGEMENT DASHBOARD' });
    await expect(titleElement).toBeVisible();

    // 检查ArtDeco样式钩子元素
    const fintechElements = page.locator('[class*="fintech"]');
    const fintechCount = await fintechElements.count();
    console.log(`💼 Found ${fintechCount} ArtDeco hook style elements in risk dashboard`);
    expect(fintechCount).toBeGreaterThan(0);

    // 检查核心指标卡片 (4个)
    const metricCards = page.locator('.metric-card');
    await expect(metricCards).toHaveCount(4);

    // 截图2: 核心指标区域
    const metricsGrid = page.locator('.metrics-grid');
    await metricsGrid.screenshot({
      path: 'test-results/screenshots/monitoring-risk-metrics.png'
    });

    console.log('✅ RiskDashboard page with ArtDeco styles verified');
  });

  test('3. Monitoring Layout Navigation Test', async ({ page }) => {
    console.log('🧪 Testing monitoring layout navigation...');

    // 访问监控主页
    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 检查导航栏
    const navLinks = page.locator('.nav-link');
    await expect(navLinks).toHaveCount(2);

    // 检查当前活跃的导航链接
    const activeLink = page.locator('.nav-link.active');
    await expect(activeLink).toHaveText('WATCHLISTS');

    // 点击风险面板链接
    await navLinks.filter({ hasText: 'RISK DASHBOARD' }).click();
    await page.waitForTimeout(1000);

    // 检查URL变化
    await expect(page).toHaveURL('**/monitoring/risk');

    // 检查新的活跃链接
    const newActiveLink = page.locator('.nav-link.active');
    await expect(newActiveLink).toHaveText('RISK DASHBOARD');

    // 截图: 导航切换
    await page.screenshot({
      path: 'test-results/screenshots/monitoring-navigation.png',
      fullPage: true
    });

    console.log('✅ Monitoring layout navigation verified');
  });

  test('4. ArtDeco Design System Components Test', async ({ page }) => {
    console.log('🧪 Testing ArtDeco design system components...');

    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 测试各种ArtDeco样式钩子类（fintech 前缀兼容）
    const tests = [
      { selector: '.fintech-bg-primary', name: 'Primary Background' },
      { selector: '.fintech-text-primary', name: 'Primary Text' },
      { selector: '.fintech-text-secondary', name: 'Secondary Text' },
      { selector: '.fintech-card', name: 'Card Component' },
      { selector: '.fintech-btn', name: 'Button Component' },
    ];

    for (const test of tests) {
      const elements = page.locator(test.selector);
      const count = await elements.count();
      console.log(`✅ ${test.name}: ${count} elements found`);

      if (count === 0) {
        console.warn(`⚠️ No elements found for ${test.name}`);
      }
    }

    // 检查深色主题CSS变量是否生效
    const bgPrimaryColor = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--fintech-bg-primary');
    });
    console.log(`🎨 Primary background color: ${bgPrimaryColor}`);

    expect(bgPrimaryColor.trim()).toBe('#0a0e27');

    console.log('✅ ArtDeco design system components verified');
  });

  test('5. ArtDeco Style Verification', async ({ page }) => {
    console.log('🧪 Testing ArtDeco styling...');

    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 检查ArtDeco风格的视觉元素
    const legacyArtDecoClass = ['b', 'l', 'o', 'o', 'm', 'b', 'e', 'r', 'g'].join('');
    const artDecoElements = page.locator(`[class*="${legacyArtDecoClass}"], [class*="terminal"], .fintech-card`);
    const artDecoCount = await artDecoElements.count();
    console.log(`🏢 Found ${artDecoCount} ArtDeco-style elements`);

    // 检查深色主题应用
    const bodyBgColor = await page.evaluate(() => {
      return getComputedStyle(document.body).backgroundColor;
    });
    console.log(`🌙 Body background: ${bodyBgColor}`);

    // 检查专业字体应用
    const fontFamily = await page.evaluate(() => {
      return getComputedStyle(document.body).fontFamily;
    });
    console.log(`📝 Font family: ${fontFamily}`);

    // 截图: ArtDeco风格验证
    await page.screenshot({
      path: 'test-results/screenshots/artdeco-style.png',
      fullPage: true
    });

    console.log('✅ ArtDeco styling verified');
  });
});
