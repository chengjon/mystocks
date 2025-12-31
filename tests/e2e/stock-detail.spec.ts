/**
 * MyStocks E2E测试 - 股票详情页面
 *
 * 测试场景：
 * 1. 股票详情页面加载
 * 2. 股票基本信息显示
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('股票详情 - Stock Detail', () => {
  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();
  });

  /**
   * 测试用例 1: 股票详情页面加载
   */
  test('1. 股票详情页面应该正确加载 @smoke @ui', async ({ page }) => {
    await page.goto('/stock-detail/600519');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证页面包含股票代码
    const content = page.locator('body');
    const text = await content.textContent();
    expect(text).toMatch(/600519|贵州茅台/);
  });

  /**
   * 测试用例 2: 股票基本信息显示
   */
  test('2. 应该显示股票基本信息 @ui', async ({ page }) => {
    await page.goto('/stock-detail/600519');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证卡片或表格存在
    const card = page.locator('.el-card').or(page.locator('.el-table'));
    const isVisible = await card.first().isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });
});
