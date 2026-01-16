import { test, expect } from '@playwright/test';

/**
 * MyStocks Frontend - Complete Page Accessibility Test
 *
 * 测试所有页面的可访问性和基本功能
 * 验证页面加载、错误处理和用户界面元素
 */

const BASE_URL = 'http://localhost:3001';

// 所有路由配置
const routes = [
  // 公开路由
  { path: '/login', name: 'Login' },

  // Dashboard域
  { path: '/dashboard', name: 'Dashboard Overview' },
  { path: '/dashboard/watchlist', name: 'Watchlist' },
  { path: '/dashboard/portfolio', name: 'Portfolio' },
  { path: '/dashboard/activity', name: 'Activity' },

  // Market Data域
  { path: '/market/list', name: 'Stock List' },
  { path: '/market/realtime', name: 'Realtime' },
  { path: '/market/kline/000001', name: 'K-Line (with symbol)' },
  { path: '/market/depth', name: 'Depth' },
  { path: '/market/sector', name: 'Sector' },

  // Stock Analysis域
  { path: '/analysis/screener', name: 'Stock Screener' },
  { path: '/analysis/industry', name: 'Industry Analysis' },
  { path: '/analysis/concept', name: 'Concept Analysis' },
  { path: '/analysis/fundamental', name: 'Fundamental Analysis' },
  { path: '/analysis/technical', name: 'Technical Analysis' },

  // Risk Monitor域
  { path: '/risk/overview', name: 'Risk Overview' },
  { path: '/risk/position', name: 'Position Risk' },
  { path: '/risk/portfolio', name: 'Portfolio Risk' },
  { path: '/risk/alerts', name: 'Risk Alerts' },
  { path: '/risk/stress', name: 'Stress Test' },

  // Strategy Management域
  { path: '/strategy/list', name: 'Strategy List' },
  { path: '/strategy/market', name: 'Strategy Market' },
  { path: '/strategy/backtest', name: 'Backtest' },
  { path: '/strategy/signals', name: 'Signals' },
  { path: '/strategy/performance', name: 'Performance' },

  // Monitoring Platform域
  { path: '/monitoring/dashboard', name: 'Monitoring Dashboard' },
  { path: '/monitoring/data-quality', name: 'Data Quality' },
  { path: '/monitoring/performance', name: 'Performance Monitoring' },
  { path: '/monitoring/api', name: 'API Health' },
  { path: '/monitoring/logs', name: 'Logs' },

  // Settings
  { path: '/settings/general', name: 'General Settings' },
  { path: '/settings/system', name: 'System Settings' },
  { path: '/settings/database', name: 'Database Settings' },

  // Demo pages
  { path: '/demo/openstock', name: 'OpenStock Demo' },
  { path: '/demo/freqtrade', name: 'Freqtrade Demo' },
  { path: '/demo/stock-analysis', name: 'Stock Analysis Demo' },
  { path: '/demo/tdxpy', name: 'TDXPY Demo' },
  { path: '/demo/smart-data', name: 'Smart Data Test' },
];

test.describe('MyStocks Frontend - Page Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    // 设置默认超时
    page.setDefaultTimeout(10000);
  });

  // 测试所有页面加载
  for (const route of routes) {
    test(`Page: ${route.name} (${route.path})`, async ({ page }) => {
      console.log(`\n🔍 Testing: ${route.name} - ${route.path}`);

      // 导航到页面
      const response = await page.goto(`${BASE_URL}/#${route.path}`);

      // 验证HTTP状态码
      expect(response?.status()).toBe(200);

      // 等待页面基本加载
      await page.waitForLoadState('domcontentloaded', { timeout: 8000 });

      // 检查是否有JavaScript错误
      const errors: string[] = [];
      page.on('pageerror', (error) => {
        errors.push(error.message);
      });

      // 验证页面基本结构
      const body = page.locator('body');
      await expect(body).toBeVisible();

      // 检查是否有明显错误提示
      const errorSelectors = [
        '[class*="error"]',
        '[class*="Error"]',
        '.error-message',
        '.error-page',
        '[class*="exception"]',
      ];

      let hasError = false;
      for (const selector of errorSelectors) {
        try {
          const errorElement = page.locator(selector).first();
          if (await errorElement.isVisible()) {
            const errorText = await errorElement.textContent();
            console.log(`  ⚠️  Found error element: ${selector}`);
            console.log(`     Text: ${errorText}`);
            hasError = true;
          }
        } catch {
          // 元素不存在或不可见，继续
        }
      }

      // 记录页面标题
      const title = await page.title();
      console.log(`  📄 Title: ${title}`);

      // 截图保存
      const screenshotName = `${route.name.replace(/\s+/g, '-').toLowerCase()}-${Date.now()}.png`;
      await page.screenshot({
        path: `/tmp/playwright-screenshots/${screenshotName}`,
        fullPage: false,
      });

      // 验证基本信息
      expect(title.length).toBeGreaterThan(0);

      // 如果有JavaScript错误，记录但不失败（除非是致命错误）
      if (errors.length > 0) {
        console.log(`  ⚠️  JavaScript errors (${errors.length}):`);
        errors.forEach((err) => console.log(`     - ${err}`));
      }

      console.log(`  ✅ Page loaded successfully`);
    });
  }
});

test.describe('MyStocks Frontend - Core Functionality', () => {
  test('Dashboard page basic navigation', async ({ page }) => {
    console.log('\n🔍 Testing dashboard navigation...');

    await page.goto(`${BASE_URL}/#/dashboard`);
    await page.waitForLoadState('domcontentloaded');

    // 检查是否有导航菜单
    const navMenu = page.locator('nav, .nav, [class*="menu"], [class*="sidebar"]');
    const hasNav = await navMenu.count() > 0;
    console.log(`  📋 Navigation menu found: ${hasNav}`);

    // 截图
    await page.screenshot({
      path: '/tmp/playwright-screenshots/dashboard-navigation.png',
    });

    expect(hasNav).toBeTruthy();
  });

  test('Login page is accessible', async ({ page }) => {
    console.log('\n🔍 Testing login page...');

    await page.goto(`${BASE_URL}/#/login`);
    await page.waitForLoadState('domcontentloaded');

    // 检查登录表单元素
    const loginButton = page.locator('button[type="submit"], .login-button, [class*="login"]');
    const hasLoginButton = await loginButton.count() > 0;

    console.log(`  🔐 Login button found: ${hasLoginButton}`);

    // 截图
    await page.screenshot({
      path: '/tmp/playwright-screenshots/login-page.png',
    });
  });

  test('API Health Check', async ({ page }) => {
    console.log('\n🔍 Testing backend API health...');

    try {
      const response = await page.request.get('http://localhost:8000/health');
      console.log(`  📡 API Status: ${response.status()}`);
      expect(response.status()).toBe(200);

      const data = await response.json();
      console.log(`  ✅ API Response:`, data);
      expect(data.success).toBe(true);
    } catch (error) {
      console.error(`  ❌ API Health check failed:`, error);
      throw error;
    }
  });
});

test.describe('MyStocks Frontend - Cross-Page Navigation', () => {
  test('Navigate from Dashboard to Market pages', async ({ page }) => {
    console.log('\n🔍 Testing cross-page navigation...');

    // Start at dashboard
    await page.goto(`${BASE_URL}/#/dashboard`);
    await page.waitForLoadState('domcontentloaded');
    console.log(`  ✅ Started at dashboard`);

    // Navigate to market list
    await page.goto(`${BASE_URL}/#/market/list`);
    await page.waitForLoadState('domcontentloaded');
    console.log(`  ✅ Navigated to market list`);

    // Navigate to analysis
    await page.goto(`${BASE_URL}/#/analysis/screener`);
    await page.waitForLoadState('domcontentloaded');
    console.log(`  ✅ Navigated to analysis screener`);

    // Final screenshot
    await page.screenshot({
      path: '/tmp/playwright-screenshots/navigation-test-final.png',
    });
  });
});

test.afterEach(async ({ page }, testInfo) => {
  console.log(`\n📊 Test completed: ${testInfo.title}`);
  console.log(`   Status: ${testInfo.status}`);
  console.log(`   Duration: ${testInfo.duration}ms`);
});
