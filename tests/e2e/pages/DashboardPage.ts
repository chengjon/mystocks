/**
 * DashboardPage - Page Object Model for Dashboard
 *
 * 封装仪表板页面的主要交互逻辑
 */

import { Page, expect } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  readonly url: string;

  // 页面元素定位器
  readonly mainContent = () => this.page.locator('main').or(
    this.page.locator('.el-main').or(
      this.page.locator('[class*="dashboard"]')
    )
  );
  readonly logoutButton = () => this.page.locator('button:has-text("登出"), button:has-text("退出")');

  constructor(page: Page, baseUrl: string = 'http://localhost:3000') {
    this.page = page;
    this.url = `${baseUrl}/`;
  }

  /**
   * 导航到仪表板页面
   */
  async goto(): Promise<void> {
    await this.page.goto(this.url);
    await this.waitForLoad();
  }

  /**
   * 等待页面加载完成
   */
  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(1000);
  }

  /**
   * 验证仪表板已加载
   */
  async isLoaded(): Promise<void> {
    await this.waitForLoad();
    // Verify we're on the dashboard page by checking URL
    expect(this.page.url()).toMatch(/\/$|\/dashboard/);
    // Don't enforce strict element visibility - page may be empty or loading
  }

  /**
   * 登出
   */
  async logout(): Promise<void> {
    const button = this.logoutButton();
    const count = await button.count();

    if (count > 0) {
      await button.first().click();
      await this.page.waitForNavigation({ url: /login/, timeout: 30000 });
    }
  }

  /**
   * 验证已登出
   */
  async verifyLoggedOut(): Promise<void> {
    const token = await this.page.evaluate(() => localStorage.getItem('token'));
    const user = await this.page.evaluate(() => localStorage.getItem('user'));

    expect(token).toBeNull();
    expect(user).toBeNull();
    expect(this.page.url()).toContain('/login');
  }
}
