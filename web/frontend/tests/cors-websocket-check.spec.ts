// tests/cors-websocket-check.spec.ts
/**
 * CORS和WebSocket错误自动检测
 *
 * 目的：自动化检测前端与后端通信中的CORS和WebSocket错误
 * 使用方法：npx playwright test tests/cors-websocket-check.spec.ts --reporter=list
 */

import { test, expect } from '@playwright/test';

test.describe('CORS和WebSocket错误自动检测', () => {
  test('应该没有CORS错误', async ({ page }) => {
    const failedRequests: { url: string; error: string }[] = [];

    // 监听请求失败
    page.on('requestfailed', request => {
      const failure = request.failure();
      if (failure) {
        failedRequests.push({
          url: request.url(),
          error: failure.errorText
        });
      }
    });

    // 导航到仪表板
    await page.goto('/#/dashboard');
    await page.waitForLoadState('domcontentloaded');

    // 等待页面稳定
    await page.waitForTimeout(2000);

    // 断言无CORS错误
    const corsErrors = failedRequests.filter(r =>
      r.error.includes('CORS') ||
      r.error.includes('blocked') ||
      r.error.includes('cross-origin')
    );

    console.log('Total failed requests:', failedRequests.length);
    console.log('CORS errors:', corsErrors.length);

    if (corsErrors.length > 0) {
      console.log('CORS error details:');
      corsErrors.forEach(err => console.log(`  - ${err.url}: ${err.error}`));
    }

    expect(corsErrors.length).toBe(0);
  });

  test('应该没有WebSocket错误', async ({ page }) => {
    const wsErrors: string[] = [];

    // 监听WebSocket错误
    page.on('pageerror', error => {
      if (error.message.includes('WebSocket')) {
        wsErrors.push(error.message);
      }
    });

    // 导航到仪表板
    await page.goto('/#/dashboard');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    console.log('WebSocket errors:', wsErrors.length);

    if (wsErrors.length > 0) {
      console.log('WebSocket error details:');
      wsErrors.forEach(err => console.log(`  - ${err}`));
    }

    expect(wsErrors.length).toBe(0);
  });

  test('应该成功加载API数据', async ({ page }) => {
    const apiRequests: { url: string; status: number }[] = [];

    // 监听所有API请求
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        apiRequests.push({ url: request.url(), status: 0 });
      }
    });

    page.on('response', response => {
      if (response.url().includes('/api/')) {
        const req = apiRequests.find(r => r.url === response.url());
        if (req) {
          req.status = response.status();
        }
      }
    });

    await page.goto('/#/dashboard');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    console.log('API requests:', apiRequests.length);
    console.log('API request details:');
    apiRequests.forEach(req => {
      console.log(`  - ${req.url}: ${req.status}`);
    });

    // 断言有API请求被发起（表明前端尝试连接后端）
    const hasApiRequests = apiRequests.length > 0;
    expect(hasApiRequests).toBe(true);

    // 断言没有失败的API请求（除了预期的404）
    const failedApiRequests = apiRequests.filter(r => r.status >= 400 && r.status !== 404);
    expect(failedApiRequests.length).toBe(0);
  });

  test('页面核心功能应该正常工作', async ({ page }) => {
    await page.goto('/#/dashboard');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 验证ArtDeco布局
    await expect(page.locator('.artdeco-dashboard')).toBeVisible();
    await expect(page.locator('.artdeco-header')).toBeVisible();

    // 验证菜单
    const expectedMenus = [
      '仪表盘',
      '市场行情',
      '股票管理',
      '投资分析',
      '风险管理',
      '策略和交易管理',
      '系统监控'
    ];

    for (const menu of expectedMenus) {
      const element = page.locator(`.nav-link:has-text("${menu}")`);
      await expect(element).toBeVisible();
    }

    console.log('All core functionalities passed!');
  });
});
