/**
 * MyStocks E2E测试 - 交易管理页面
 *
 * 测试场景：
 * 1. 交易管理页面加载
 * 2. 交易列表显示
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('交易管理 - Trade Management', () => {
  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();
  });

  /**
   * 测试用例 1: 交易管理页面加载
   */
  test('1. 交易管理页面应该正确加载 @smoke @ui', async ({ page }) => {
    await page.goto('/trade');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证页面标题
    const heading = page.getByRole('heading', { name: /交易/ });
    const isVisible = await heading.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  /**
   * 测试用例 2: 交易列表显示
   */
  test('2. 应该显示交易列表 @ui', async ({ page }) => {
    await page.goto('/trade');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证表格或卡片存在
    const table = page.locator('.el-table').or(page.locator('.el-card'));
    const isVisible = await table.first().isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });
});
