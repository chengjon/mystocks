/**
 * MyStocks E2E测试 - 实时监控页面
 *
 * 测试场景：
 * 1. 实时监控页面加载
 * 2. 实时数据显示
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('实时监控 - Realtime Monitor', () => {
  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();
  });

  /**
   * 测试用例 1: 实时监控页面加载
   */
  test('1. 实时监控页面应该正确加载 @smoke @ui', async ({ page }) => {
    await page.goto('/realtime-monitor');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证页面标题
    const heading = page.getByRole('heading', { name: /监控/ });
    const isVisible = await heading.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  /**
   * 测试用例 2: 实时数据显示
   */
  test('2. 应该显示实时数据 @ui', async ({ page }) => {
    await page.goto('/realtime-monitor');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证表格或图表存在
    const table = page.locator('.el-table').or(page.locator('[style*="height:"]'));
    const isVisible = await table.first().isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });
});
