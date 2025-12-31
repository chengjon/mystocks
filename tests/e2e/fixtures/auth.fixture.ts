/**
 * 测试Fixtures - 认证相关
 *
 * 提供预配置的测试上下文和辅助函数
 */

import { test as base, Page } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { TEST_USERS, TEST_URLS } from './test-data';

export type TestOptions = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
};

// 扩展test对象，添加自定义fixtures
export const test = base.extend<TestOptions>({
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page, TEST_URLS.frontend);
    await use(loginPage);
  },

  dashboardPage: async ({ page }, use) => {
    const dashboardPage = new DashboardPage(page, TEST_URLS.frontend);
    await use(dashboardPage);
  },
});

export { expect } from '@playwright/test';

/**
 * 辅助函数：执行登录前的清理工作
 */
export async function setupLoginTest(page: Page): Promise<void> {
  await page.addInitScript(() => {
    try {
      localStorage.clear();
      console.log('[Setup] localStorage cleared');
    } catch (error) {
      console.log('[Setup] localStorage fallback');
    }
  });
}

/**
 * 辅助函数：验证用户已登录
 */
export async function verifyUserLoggedIn(page: Page): Promise<void> {
  const token = await page.evaluate(() => localStorage.getItem('token'));
  const user = await page.evaluate(() => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  });

  if (!token || !user) {
    throw new Error('User not logged in: token or user info missing');
  }
}

/**
 * 辅助函数：快速登录
 */
export async function quickLogin(
  page: Page,
  userType: 'admin' | 'user' = 'admin'
): Promise<void> {
  const user = TEST_USERS[userType];
  const loginPage = new LoginPage(page, TEST_URLS.frontend);

  await setupLoginTest(page);
  await loginPage.goto();
  await loginPage.login(user);
  await loginPage.verifyLoggedIn();
}
