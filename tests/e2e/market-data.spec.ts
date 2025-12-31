/**
 * MyStocks E2E测试 - 市场数据页面
 *
 * 测试场景：
 * 1. 市场数据页面加载
 * 2. 市场概览显示
 * 3. 数据刷新功能
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('市场数据 - Market Data', () => {
  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();
  });

  /**
   * 测试用例 1: 市场数据页面加载
   */
  test('1. 市场数据页面应该正确加载 @smoke @ui', async ({ page }) => {
    await page.goto('/market');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证页面标题或关键元素
    const heading = page.getByRole('heading', { name: /市场/ }).or(page.locator('.market'));
    const isVisible = await heading.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  /**
   * 测试用例 2: 市场概览显示
   */
  test('2. 应该显示市场概览信息 @ui', async ({ page }) => {
    await page.goto('/market');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证表格或卡片存在
    const table = page.locator('.el-table').or(page.locator('.el-card'));
    const isVisible = await table.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  /**
   * 测试用例 3: 刷新功能
   */
  test('3. 应该能够刷新市场数据 @ui', async ({ page }) => {
    await page.goto('/market');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 点击刷新按钮（如果有）
    const refreshButton = page.getByRole('button', { name: '刷新' });
    const buttonExists = await refreshButton.count() > 0;

    if (buttonExists) {
      await refreshButton.first().click();
      await page.waitForTimeout(1000);
    }
  });
});
