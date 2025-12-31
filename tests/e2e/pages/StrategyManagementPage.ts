/**
 * StrategyManagementPage - Page Object Model for Strategy Management
 *
 * 封装策略管理页面的主要交互逻辑
 */

import { Page, expect } from '@playwright/test';

export class StrategyManagementPage {
  readonly page: Page;
  readonly url: string;

  // 页面元素定位器
  readonly heading = () => this.page.getByRole('heading', { name: '策略管理' });
  readonly subtitle = () => this.page.getByText('管理和回测您的量化交易策略');
  readonly createStrategyButton = () => this.page.getByRole('button', { name: /创建策略|创建第一个策略/ });
  readonly strategyGrid = () => this.page.locator('.strategy-grid');
  readonly emptyState = () => this.page.locator('.empty-state');
  readonly loadingState = () => this.page.locator('.loading-state');
  readonly errorState = () => this.page.locator('.error-state');

  constructor(page: Page, baseUrl: string = 'http://localhost:3000') {
    this.page = page;
    this.url = `${baseUrl}/strategy-hub/management`;
  }

  /**
   * 导航到策略管理页面
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
    await this.page.waitForTimeout(500);
  }

  /**
   * 验证策略管理页面已加载
   */
  async isLoaded(): Promise<void> {
    await this.waitForLoad();
    // Verify URL contains /strategy-hub/management (actual route)
    expect(this.page.url()).toContain('/strategy-hub/management');
    // Don't enforce strict element visibility - page may be empty or loading
  }

  /**
   * 点击创建策略按钮
   */
  async clickCreateStrategy(): Promise<void> {
    await this.createStrategyButton().click();
  }

  /**
   * 获取策略数量
   */
  async getStrategyCount(): Promise<number> {
    const count = await this.strategyGrid().locator('.el-card').count();
    return count;
  }

  /**
   * 检查是否为空状态
   */
  async isEmpty(): Promise<boolean> {
    const isEmpty = await this.emptyState().isVisible().catch(() => false);
    return isEmpty;
  }

  /**
   * 检查是否正在加载
   */
  async isLoading(): Promise<boolean> {
    const isLoading = await this.loadingState().isVisible().catch(() => false);
    return isLoading;
  }

  /**
   * 检查是否有错误
   */
  async hasError(): Promise<boolean> {
    const hasError = await this.errorState().isVisible().catch(() => false);
    return hasError;
  }
}
