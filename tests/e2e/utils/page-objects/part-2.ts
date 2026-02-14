/**
 * 页面对象模型 (Page Object Models)
 * 为Vue组件创建可复用的页面对象，简化E2E测试代码
 *
 * 作者: Claude Code
 * 生成时间: 2025-11-14
 */

import { Page, expect, Locator } from '@playwright/test';

/**
 * 问财查询页面对象
 */
export class WencaiPage extends BasePage {
  private querySelector: Locator;
  private customQueryInput: Locator;
  private executeQueryButton: Locator;
  private executeCustomQueryButton: Locator;
  private queryResults: Locator;
  private predefinedQueries: Locator;
  private customQueryTab: Locator;

  constructor(page: Page) {
    super(page);
    this.querySelector = page.locator('[data-testid=query-selector]');
    this.customQueryInput = page.locator('[data-testid=custom-query-input]');
    this.executeQueryButton = page.locator('[data-testid=execute-query-button]');
    this.executeCustomQueryButton = page.locator('[data-testid=execute-custom-query]');
    this.queryResults = page.locator('[data-testid=query-results]');
    this.predefinedQueries = page.locator('[data-testid=predefined-queries]');
    this.customQueryTab = page.locator('[data-testid=custom-query-tab]');
  }

  async navigate(): Promise<void> {
    await this.page.goto('/wencai');
    await this.waitForPageLoad();
  }

  /**
   * 选择预定义查询
   */
  async selectPredefinedQuery(queryName: string): Promise<void> {
    await this.querySelector.selectOption(queryName);
  }

  /**
   * 执行预定义查询
   */
  async executePredefinedQuery(queryName: string): Promise<void> {
    await this.selectPredefinedQuery(queryName);
    await this.executeQueryButton.click();
  }

  /**
   * 切换到自定义查询
   */
  async switchToCustomQuery(): Promise<void> {
    await this.customQueryTab.click();
  }

  /**
   * 输入自定义查询
   */
  async inputCustomQuery(query: string): Promise<void> {
    await this.customQueryInput.fill(query);
  }

  /**
   * 执行自定义查询
   */
  async executeCustomQuery(query: string): Promise<void> {
    await this.inputCustomQuery(query);
    await this.executeCustomQueryButton.click();
  }

  /**
   * 检查查询结果是否显示
   */
  async areQueryResultsVisible(): Promise<boolean> {
    return await this.queryResults.isVisible();
  }

  /**
   * 获取查询结果数据
   */
  async getQueryResultsData(): Promise<any[]> {
    const resultItems = this.queryResults.locator('[data-testid=query-result-item]');
    const count = await resultItems.count();
    const results = [];

    for (let i = 0; i < count; i++) {
      const item = resultItems.nth(i);
      results.push({
        content: await item.textContent(),
        type: await item.getAttribute('data-type')
      });
    }

    return results;
  }
}

/**
 * 策略管理页面对象
 */
export class StrategyPage extends BasePage {
  private strategyList: Locator;
  private strategyItems: Locator;
  private runStrategyButton: Locator;
  private strategyResults: Locator;
  private createStrategyButton: Locator;
  private strategyForm: Locator;

  constructor(page: Page) {
    super(page);
    this.strategyList = page.locator('[data-testid=strategy-list]');
    this.strategyItems = page.locator('[data-testid=strategy-item]');
    this.runStrategyButton = page.locator('[data-testid=run-strategy-button]');
    this.strategyResults = page.locator('[data-testid=strategy-results]');
    this.createStrategyButton = page.locator('[data-testid=create-strategy-button]');
    this.strategyForm = page.locator('[data-testid=strategy-form]');
  }

  async navigate(): Promise<void> {
    await this.page.goto('/strategy-management');
    await this.waitForPageLoad();
  }

  /**
   * 获取策略列表
   */
  async getStrategyList(): Promise<any[]> {
    const items = this.strategyItems;
    const count = await items.count();
    const strategies = [];

    for (let i = 0; i < count; i++) {
      const item = items.nth(i);
      strategies.push({
        name: await item.locator('[data-testid=strategy-name]').textContent(),
        status: await item.locator('[data-testid=strategy-status]').textContent(),
        description: await item.locator('[data-testid=strategy-description]').textContent()
      });
    }

    return strategies;
  }

  /**
   * 运行策略
   */
  async runStrategy(strategyIndex: number = 0): Promise<void> {
    await this.strategyItems.nth(strategyIndex).click();
    await this.runStrategyButton.click();
  }

  /**
   * 创建新策略
   */
  async createStrategy(strategyName: string, description: string): Promise<void> {
    await this.createStrategyButton.click();
    await this.page.locator('[data-testid=strategy-name-input]').fill(strategyName);
    await this.page.locator('[data-testid=strategy-description-input]').fill(description);
    await this.page.locator('[data-testid=save-strategy-button]').click();
  }

  /**
   * 检查策略结果是否显示
   */
  async areStrategyResultsVisible(): Promise<boolean> {
    return await this.strategyResults.isVisible();
  }
}

/**
 * 通用导航工具
 */
export class NavigationHelper {
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * 导航到主页
   */
  async goToHome(): Promise<void> {
    await this.page.click('[data-testid=home-link]');
  }

  /**
   * 导航到市场页面
   */
  async goToMarket(): Promise<void> {
    await this.page.click('[data-testid=market-link]');
  }

  /**
   * 导航到技术分析页面
   */
  async goToTechnicalAnalysis(): Promise<void> {
    await this.page.click('[data-testid=technical-analysis-link]');
  }

  /**
   * 导航到问财页面
   */
  async goToWencai(): Promise<void> {
    await this.page.click('[data-testid=wencai-link]');
  }

  /**
   * 导航到策略页面
   */
  async goToStrategy(): Promise<void> {
    await this.page.click('[data-testid=strategy-link]');
  }

  /**
   * 检查当前页面路径
   */
  async getCurrentPath(): Promise<string> {
    return this.page.url();
  }
}

