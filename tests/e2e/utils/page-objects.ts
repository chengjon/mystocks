/**
 * 页面对象模型 (Page Object Models)
 * 为Vue组件创建可复用的页面对象，简化E2E测试代码
 *
 * 作者: Claude Code
 * 生成时间: 2025-11-14
 */

import { Page, expect, Locator } from '@playwright/test';

/**
 * 基础页面对象
 */
export abstract class BasePage {
  protected page: Page;
  protected baseURL: string;

  constructor(page: Page) {
    this.page = page;
    this.baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000';  // Per port allocation spec: Frontend 3000-3009
  }

  /**
   * 导航到页面
   */
  abstract navigate(): Promise<void>;

  /**
   * 等待页面加载完成
   */
  async waitForPageLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 截取页面截图
   */
  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({
      path: `test-results/screenshots/${name}.png`,
      fullPage: true
    });
  }

  /**
   * 获取页面标题
   */
  async getPageTitle(): Promise<string> {
    return await this.page.title();
  }

  /**
   * 检查是否在当前页面
   */
  async isOnPage(expectedPath: string): Promise<boolean> {
    return this.page.url().includes(expectedPath);
  }
}

/**
 * 登录页面对象
 */
export class LoginPage extends BasePage {
  private usernameInput: Locator;
  private passwordInput: Locator;
  private loginButton: Locator;
  private errorMessage: Locator;
  private registerLink: Locator;

  constructor(page: Page) {
    super(page);
    this.usernameInput = page.locator('[data-testid=username]');
    this.passwordInput = page.locator('[data-testid=password]');
    this.loginButton = page.locator('[data-testid=login-button]');
    this.errorMessage = page.locator('[data-testid=error-message]');
    this.registerLink = page.locator('[data-testid=register-link]');
  }

  async navigate(): Promise<void> {
    await this.page.goto('/login');
    await this.waitForPageLoad();
  }

  /**
   * 输入用户名
   */
  async inputUsername(username: string): Promise<void> {
    await this.usernameInput.fill(username);
  }

  /**
   * 输入密码
   */
  async inputPassword(password: string): Promise<void> {
    await this.passwordInput.fill(password);
  }

  /**
   * 点击登录按钮
   */
  async clickLogin(): Promise<void> {
    await this.loginButton.click();
  }

  /**
   * 执行完整登录流程
   */
  async login(username: string, password: string): Promise<void> {
    await this.inputUsername(username);
    await this.inputPassword(password);
    await this.clickLogin();
  }

  /**
   * 获取错误消息
   */
  async getErrorMessage(): Promise<string | null> {
    try {
      return await this.errorMessage.textContent();
    } catch {
      return null;
    }
  }

  /**
   * 检查是否显示错误消息
   */
  async isErrorMessageVisible(): Promise<boolean> {
    return await this.errorMessage.isVisible();
  }

  /**
   * 点击注册链接
   */
  async clickRegister(): Promise<void> {
    await this.registerLink.click();
  }

  /**
   * 检查登录表单是否可见
   */
  async isLoginFormVisible(): Promise<boolean> {
    return await this.loginButton.isVisible();
  }
}

/**
 * 仪表盘页面对象
 */
export class DashboardPage extends BasePage {
  private welcomeMessage: Locator;
  private marketStatsCards: Locator;
  private marketHeatChart: Locator;
  private leadingSectorChart: Locator;
  private priceDistributionChart: Locator;
  private capitalFlowChart: Locator;
  private favoriteStocksTable: Locator;
  private strategyStocksTable: Locator;
  private industryStocksTable: Locator;
  private conceptStocksTable: Locator;
  private refreshButton: Locator;
  private userMenu: Locator;

  constructor(page: Page) {
    super(page);
    this.welcomeMessage = page.locator('[data-testid=welcome-message]');
    this.marketStatsCards = page.locator('[data-testid=stat-card]');
    this.marketHeatChart = page.locator('[data-testid=market-heat-chart]');
    this.leadingSectorChart = page.locator('[data-testid=leading-sector-chart]');
    this.priceDistributionChart = page.locator('[data-testid=price-distribution-chart]');
    this.capitalFlowChart = page.locator('[data-testid=capital-flow-chart]');
    this.favoriteStocksTable = page.locator('[data-testid=favorite-stocks-table]');
    this.strategyStocksTable = page.locator('[data-testid=strategy-stocks-table]');
    this.industryStocksTable = page.locator('[data-testid=industry-stocks-table]');
    this.conceptStocksTable = page.locator('[data-testid=concept-stocks-table]');
    this.refreshButton = page.locator('[data-testid=refresh-button]');
    this.userMenu = page.locator('[data-testid=user-menu]');
  }

  async navigate(): Promise<void> {
    await this.page.goto('/dashboard');
    await this.waitForPageLoad();
  }

  /**
   * 检查欢迎消息是否可见
   */
  async isWelcomeMessageVisible(): Promise<boolean> {
    return await this.welcomeMessage.isVisible();
  }

  /**
   * 获取统计卡片数量
   */
  async getStatsCardCount(): Promise<number> {
    return await this.marketStatsCards.count();
  }

  /**
   * 检查图表是否可见
   */
  async areChartsVisible(): Promise<boolean> {
    const charts = [
      this.marketHeatChart,
      this.leadingSectorChart,
      this.priceDistributionChart,
      this.capitalFlowChart
    ];

    for (const chart of charts) {
      if (!await chart.isVisible()) {
        return false;
      }
    }

    return true;
  }

  /**
   * 检查表格数据是否加载
   */
  async areTablesLoaded(): Promise<boolean> {
    const tables = [
      this.favoriteStocksTable,
      this.strategyStocksTable,
      this.industryStocksTable,
      this.conceptStocksTable
    ];

    for (const table of tables) {
      if (!await table.isVisible()) {
        return false;
      }
    }

    return true;
  }

  /**
   * 点击刷新按钮
   */
  async clickRefresh(): Promise<void> {
    await this.refreshButton.click();
  }

  /**
   * 获取自选股表格数据
   */
  async getFavoriteStocksData(): Promise<any[]> {
    const rows = this.favoriteStocksTable.locator('tbody tr');
    const count = await rows.count();
    const data = [];

    for (let i = 0; i < count; i++) {
      const row = rows.nth(i);
      data.push({
        symbol: await row.locator('td:nth-child(1)').textContent(),
        name: await row.locator('td:nth-child(2)').textContent(),
        price: await row.locator('td:nth-child(3)').textContent(),
        change: await row.locator('td:nth-child(4)').textContent()
      });
    }

    return data;
  }

  /**
   * 点击用户菜单
   */
  async clickUserMenu(): Promise<void> {
    await this.userMenu.click();
  }
}

/**
 * 股票搜索页面对象
 */
export class StockSearchPage extends BasePage {
  private searchInput: Locator;
  private searchResults: Locator;
  private stockItems: Locator;
  private filterOptions: Locator;
  private searchButton: Locator;

  constructor(page: Page) {
    super(page);
    this.searchInput = page.locator('[data-testid=search-input]');
    this.searchResults = page.locator('[data-testid=search-results]');
    this.stockItems = page.locator('[data-testid=stock-item]');
    this.filterOptions = page.locator('[data-testid=filter-options]');
    this.searchButton = page.locator('[data-testid=search-button]');
  }

  async navigate(): Promise<void> {
    await this.page.goto('/market/stock-search');
    await this.waitForPageLoad();
  }

  /**
   * 输入搜索关键词
   */
  async inputSearchKeyword(keyword: string): Promise<void> {
    await this.searchInput.fill(keyword);
  }

  /**
   * 执行搜索
   */
  async performSearch(keyword?: string): Promise<void> {
    if (keyword) {
      await this.inputSearchKeyword(keyword);
    }
    await this.searchButton.click();
  }

  /**
   * 检查搜索结果是否显示
   */
  async areSearchResultsVisible(): Promise<boolean> {
    return await this.searchResults.isVisible();
  }

  /**
   * 获取搜索结果数量
   */
  async getSearchResultsCount(): Promise<number> {
    return await this.stockItems.count();
  }

  /**
   * 点击第一个搜索结果
   */
  async clickFirstResult(): Promise<void> {
    await this.stockItems.first().click();
  }

  /**
   * 获取搜索结果列表
   */
  async getSearchResultsList(): Promise<any[]> {
    const items = this.stockItems;
    const count = await items.count();
    const results = [];

    for (let i = 0; i < count; i++) {
      const item = items.nth(i);
      results.push({
        symbol: await item.locator('[data-testid=stock-symbol]').textContent(),
        name: await item.locator('[data-testid=stock-name]').textContent(),
        price: await item.locator('[data-testid=stock-price]').textContent(),
        change: await item.locator('[data-testid=stock-change]').textContent()
      });
    }

    return results;
  }
}

/**
 * 技术分析页面对象
 */
export class TechnicalAnalysisPage extends BasePage {
  private stockSelector: Locator;
  private indicatorCheckboxes: Locator;
  private analyzeButton: Locator;
  private analysisResults: Locator;
  private klineChart: Locator;
  private indicatorsChart: Locator;
  private signalResults: Locator;

  constructor(page: Page) {
    super(page);
    this.stockSelector = page.locator('[data-testid=stock-selector]');
    this.indicatorCheckboxes = page.locator('[data-testid=indicator-checkbox]');
    this.analyzeButton = page.locator('[data-testid=analyze-button]');
    this.analysisResults = page.locator('[data-testid=analysis-results]');
    this.klineChart = page.locator('[data-testid=kline-chart]');
    this.indicatorsChart = page.locator('[data-testid=indicators-chart]');
    this.signalResults = page.locator('[data-testid=signal-results]');
  }

  async navigate(): Promise<void> {
    await this.page.goto('/technical-analysis');
    await this.waitForPageLoad();
  }

  /**
   * 选择股票
   */
  async selectStock(stockCode: string): Promise<void> {
    await this.stockSelector.selectOption(stockCode);
  }

  /**
   * 选择技术指标
   */
  async selectIndicators(indicators: string[]): Promise<void> {
    for (const indicator of indicators) {
      await this.page.locator(`[data-testid=indicator-${indicator}]`).check();
    }
  }

  /**
   * 执行技术分析
   */
  async performAnalysis(stockCode: string, indicators: string[]): Promise<void> {
    await this.selectStock(stockCode);
    await this.selectIndicators(indicators);
    await this.analyzeButton.click();
  }

  /**
   * 检查分析结果是否可见
   */
  async areAnalysisResultsVisible(): Promise<boolean> {
    return await this.analysisResults.isVisible();
  }

  /**
   * 检查K线图是否可见
   */
  async isKlineChartVisible(): Promise<boolean> {
    return await this.klineChart.isVisible();
  }

  /**
   * 获取分析结果数据
   */
  async getAnalysisResults(): Promise<any> {
    return await this.analysisResults.textContent();
  }
}

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
