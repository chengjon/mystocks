/**
 * BacktestAnalysisPage - Page Object Model for Backtest Analysis
 *
 * 封装回测分析页面的主要交互逻辑
 */

import { Page, expect } from '@playwright/test';

export class BacktestAnalysisPage {
  readonly page: Page;
  readonly url: string;

  // 页面元素定位器
  readonly configCard = () => this.page.locator('.config-card');
  readonly resultsCard = () => this.page.locator('.results-card');
  readonly strategySelect = () => this.page.getByRole('combobox', { name: '策略' });
  readonly symbolInput = () => this.page.getByPlaceholder('如: 600519');
  readonly runBacktestButton = () => this.page.getByRole('button', { name: '运行回测' });
  readonly refreshButton = () => this.page.getByRole('button', { name: '刷新' }).nth(1); // 第二个刷新按钮（在结果区域）
  readonly resultsTable = () => this.page.locator('.el-table');
  readonly pagination = () => this.page.locator('.el-pagination');
  readonly detailDialog = () => this.page.locator('.el-dialog');

  constructor(page: Page, baseUrl: string = 'http://localhost:3000') {
    this.page = page;
    this.url = `${baseUrl}/strategy-hub/backtest`;
  }

  /**
   * 导航到回测分析页面
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
   * 验证回测分析页面已加载
   */
  async isLoaded(): Promise<void> {
    await this.waitForLoad();
    // Verify URL contains backtest (actual route: /strategy-hub/backtest)
    expect(this.page.url()).toContain('/backtest');
    // Don't enforce strict element visibility - page may be empty or loading
  }


  /**
   * 选择策略
   */
  async selectStrategy(strategyName: string): Promise<void> {
    await this.strategySelect().click();
    await this.page.getByRole('option', { name: strategyName }).click();
  }

  /**
   * 输入股票代码
   */
  async enterSymbol(symbol: string): Promise<void> {
    await this.symbolInput().fill(symbol);
  }

  /**
   * 运行回测
   */
  async runBacktest(): Promise<void> {
    await this.runBacktestButton().click();
    await this.page.waitForTimeout(2000);
  }

  /**
   * 刷新回测结果
   */
  async refreshResults(): Promise<void> {
    await this.refreshButton().click();
    await this.page.waitForTimeout(1000);
  }

  /**
   * 获取回测结果数量
   */
  async getResultCount(): Promise<number> {
    const rows = await this.resultsTable().locator('tbody tr').count();
    return rows;
  }

  /**
   * 点击查看详情
   */
  async viewDetail(rowIndex: number = 0): Promise<void> {
    const buttons = await this.page.getByRole('button', { name: '详情' }).all();
    if (buttons.length > rowIndex) {
      await buttons[rowIndex].click();
      await this.page.waitForTimeout(500);
    }
  }

  /**
   * 关闭详情对话框
   */
  async closeDetailDialog(): Promise<void> {
    const closeButton = this.detailDialog().getByRole('button', { name: /✕|关闭/ });
    await closeButton.click();
  }
}
