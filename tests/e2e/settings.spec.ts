/**
 * MyStocks E2E测试 - 设置页面
 *
 * 测试场景：
 * 1. 设置页面加载
 * 2. 设置项显示
 *
 * 技术栈：Playwright + TypeScript + Page Object Model
 */

import { test, expect } from './fixtures/auth.fixture';
import { setupLoginTest } from './fixtures/auth.fixture';

test.describe('设置 - Settings', () => {
  test.beforeEach(async ({ page, loginPage }) => {
    await setupLoginTest(page);
    await loginPage.goto();
    await loginPage.login({ username: 'admin', password: 'admin123', role: 'admin' });
    await loginPage.verifyLoggedIn();
  });

  /**
   * 测试用例 1: 设置页面加载
   */
  test('1. 设置页面应该正确加载 @smoke @ui', async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证页面标题
    const heading = page.getByRole('heading', { name: /设置/ });
    const isVisible = await heading.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  /**
   * 测试用例 2: 设置项显示
   */
  test('2. 应该显示设置选项 @ui', async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 验证表单或卡片存在
    const form = page.locator('.el-form').or(page.locator('.el-card'));
    const isVisible = await form.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });
});
