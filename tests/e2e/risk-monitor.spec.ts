/**
 * MyStocks E2E测试 - 风险监控页面
 *
 * 测试场景：
 * 1. 风险监控页面加载
 * 2. 风险指标显示
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('风险监控 - Risk Monitor', () => {
  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();
  });

  /**
   * 测试用例 1: 风险监控页面加载
   */
  test('1. 风险监控页面应该正确加载 @smoke @ui', async ({ page }) => {
    await page.goto('/risk-monitor');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证页面标题
    const heading = page.getByRole('heading', { name: /风险/ });
    const isVisible = await heading.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  /**
   * 测试用例 2: 风险指标显示
   */
  test('2. 应该显示风险指标 @ui', async ({ page }) => {
    await page.goto('/risk-monitor');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证卡片或图表存在
    const cards = page.locator('.el-card').or(page.locator('[style*="height:"]'));
    const isVisible = await cards.first().isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });
});
