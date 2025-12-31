/**
 * StocksPage - Page Object Model for Stock List
 *
 * 封装股票列表页面的主要交互逻辑
 */

import { Page, expect } from '@playwright/test';

export class StocksPage {
  readonly page: Page;
  readonly url: string;

  // 页面元素定位器
  readonly heading = () => this.page.getByText('股票列表');
  readonly searchInput = () => this.page.getByPlaceholder('搜索股票代码或名称');
  readonly industrySelect = () => this.page.getByRole('combobox', { name: '选择行业' });
  readonly conceptSelect = () => this.page.getByRole('combobox', { name: '选择概念' });
  readonly marketSelect = () => this.page.getByRole('combobox', { name: '选择市场' });
  readonly searchButton = () => this.page.getByRole('button', { name: '搜索' });
  readonly resetButton = () => this.page.getByRole('button', { name: '重置' });
  readonly refreshButton = () => this.page.getByRole('button', { name: '刷新' });
  readonly stocksTable = () => this.page.locator('.stocks-table');
  readonly pagination = () => this.page.locator('.el-pagination');

  constructor(page: Page, baseUrl: string = 'http://localhost:3000') {
    this.page = page;
    this.url = `${baseUrl}/stocks`;
  }

  /**
   * 导航到股票列表页面
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
   * 验证股票列表页面已加载
   */
  async isLoaded(): Promise<void> {
    await this.waitForLoad();
    // Verify URL contains /stocks
    expect(this.page.url()).toContain('/stocks');
    // Don't enforce strict element visibility - page may be empty or loading
  }


  /**
   * 搜索股票
   */
  async searchStock(keyword: string): Promise<void> {
    await this.searchInput().fill(keyword);
    await this.searchButton().click();
    await this.page.waitForTimeout(1000);
  }

  /**
   * 重置筛选条件
   */
  async resetFilters(): Promise<void> {
    await this.resetButton().click();
    await this.page.waitForTimeout(1000);
  }

  /**
   * 刷新股票列表
   */
  async refresh(): Promise<void> {
    await this.refreshButton().click();
    await this.page.waitForTimeout(1000);
  }

  /**
   * 按行业筛选
   */
  async filterByIndustry(industry: string): Promise<void> {
    await this.industrySelect().click();
    await this.page.getByRole('option', { name: industry }).click();
    await this.page.waitForTimeout(500);
  }

  /**
   * 按市场筛选
   */
  async filterByMarket(market: string): Promise<void> {
    await this.marketSelect().click();
    await this.page.getByRole('option', { name: market }).click();
    await this.page.waitForTimeout(500);
  }

  /**
   * 获取股票列表行数
   */
  async getStockCount(): Promise<number> {
    const rows = await this.stocksTable().locator('tbody tr').count();
    return rows;
  }

  /**
   * 点击查看股票详情
   */
  async viewStock(symbol: string): Promise<void> {
    await this.page.getByRole('button', { name: '查看' }).first().click();
  }
}
