/**
 * Page Object Model (POM) for MyStocks E2E Testing
 *
 * Provides abstraction layer for frontend page interactions.
 * Centralizes selectors and operations for maintainable tests.
 *
 * Version: 1.0.0
 * Date: 2025-12-04
 */

import { Page, Locator, expect } from '@playwright/test';

/**
 * Base page class with common operations
 */
export class BasePage {
  protected page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Navigate to a specific path
   */
  async navigate(path: string = '/'): Promise<void> {
    await this.page.goto(path, { waitUntil: 'networkidle' });
  }

  /**
   * Wait for element to be visible
   */
  async waitForElement(selector: string, timeout: number = 10000): Promise<void> {
    await this.page.waitForSelector(selector, { timeout });
  }

  /**
   * Wait for page to fully load (networkidle)
   */
  async waitForPageLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Take screenshot for debugging
   */
  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({ path: `screenshots/${name}.png` });
  }

  /**
   * Get page title
   */
  async getPageTitle(): Promise<string | null> {
    return this.page.title();
  }

  /**
   * Wait for specific data to load (generic helper)
   */
  async waitForDataLoad(dataSelector: string = '[data-testid="loading"]', timeout: number = 10000): Promise<void> {
    // Wait for loading indicator to appear and disappear
    try {
      await this.page.waitForSelector(dataSelector, { timeout: 2000 });
      await this.page.waitForSelector(dataSelector, { state: 'hidden', timeout });
    } catch {
      // Loading indicator might not appear, just wait for network idle
      await this.waitForPageLoad();
    }
  }

  /**
   * Click element
   */
  async click(selector: string): Promise<void> {
    const element = this.page.locator(selector);
    await element.click();
  }

  /**
   * Fill input field
   */
  async fill(selector: string, text: string): Promise<void> {
    const element = this.page.locator(selector);
    await element.fill(text);
  }

  /**
   * Get text content of element
   */
  async getText(selector: string): Promise<string> {
    const element = this.page.locator(selector);
    return element.textContent() || '';
  }

  /**
   * Check if element is visible
   */
  async isVisible(selector: string): Promise<boolean> {
    const element = this.page.locator(selector);
    return element.isVisible();
  }
}

/**
 * Dashboard Page Object
 * Handles dashboard page interactions
 */
export class DashboardPage extends BasePage {
  // Selectors
  private readonly TOTAL_ASSET_CARD = '[data-testid="total-asset-card"]';
  private readonly DAILY_RETURN_CARD = '[data-testid="daily-return-card"]';
  private readonly POSITION_COUNT_CARD = '[data-testid="position-count-card"]';
  private readonly REFRESH_BUTTON = '[data-testid="refresh-button"]';
  private readonly GRID_LAYOUT = '[data-testid="grid-layout"]';
  private readonly LOADING_SPINNER = '[data-testid="loading-spinner"]';
  private readonly ERROR_MESSAGE = '[data-testid="error-message"]';
  private readonly ASSET_VALUE = '[data-testid="total-asset-value"]';

  // Getters for common locators
  get totalAssetCard(): Locator {
    return this.page.locator(this.TOTAL_ASSET_CARD);
  }

  get dailyReturnCard(): Locator {
    return this.page.locator(this.DAILY_RETURN_CARD);
  }

  get positionCountCard(): Locator {
    return this.page.locator(this.POSITION_COUNT_CARD);
  }

  get gridLayout(): Locator {
    return this.page.locator(this.GRID_LAYOUT);
  }

  /**
   * Navigate to dashboard
   */
  async navigateToDashboard(): Promise<void> {
    await this.navigate('/dashboard');
  }

  /**
   * Get total asset value
   */
  async getTotalAssetValue(): Promise<number> {
    const text = await this.getText(this.ASSET_VALUE);
    const match = text.match(/[\d.]+/);
    return match ? parseFloat(match[0]) : 0;
  }

  /**
   * Get daily return percentage
   */
  async getDailyReturn(): Promise<string> {
    return this.getText(`${this.DAILY_RETURN_CARD} [data-testid="value"]`);
  }

  /**
   * Get position count
   */
  async getPositionCount(): Promise<number> {
    const text = await this.getText(`${this.POSITION_COUNT_CARD} [data-testid="value"]`);
    const match = text.match(/\d+/);
    return match ? parseInt(match[0]) : 0;
  }

  /**
   * Click refresh button
   */
  async clickRefreshButton(): Promise<void> {
    await this.click(this.REFRESH_BUTTON);
  }

  /**
   * Check if loading spinner is visible
   */
  async isLoading(): Promise<boolean> {
    return this.isVisible(this.LOADING_SPINNER);
  }

  /**
   * Wait for dashboard data to load
   */
  async waitForDashboardLoad(): Promise<void> {
    await this.waitForDataLoad(this.LOADING_SPINNER);
  }

  /**
   * Verify dashboard is fully loaded
   */
  async verifyDashboardLoaded(): Promise<boolean> {
    const assetCardVisible = await this.isVisible(this.TOTAL_ASSET_CARD);
    const returnCardVisible = await this.isVisible(this.DAILY_RETURN_CARD);
    const positionCardVisible = await this.isVisible(this.POSITION_COUNT_CARD);

    return assetCardVisible && returnCardVisible && positionCardVisible;
  }
}

/**
 * Market Page Object
 * Handles market/行情 page interactions
 */
export class MarketPage extends BasePage {
  // Selectors
  private readonly SEARCH_INPUT = '[data-testid="market-search-input"]';
  private readonly SEARCH_BUTTON = '[data-testid="search-button"]';
  private readonly FILTER_BUTTON = '[data-testid="filter-button"]';
  private readonly STOCK_LIST = '[data-testid="stock-list"]';
  private readonly STOCK_ITEM = '[data-testid="stock-item"]';
  private readonly PAGINATION = '[data-testid="pagination"]';
  private readonly LOADING = '[data-testid="loading-spinner"]';
  private readonly ERROR = '[data-testid="error-message"]';
  private readonly EMPTY_STATE = '[data-testid="empty-state"]';

  /**
   * Navigate to market page
   */
  async navigateToMarket(): Promise<void> {
    await this.navigate('/market');
  }

  /**
   * Search for stock
   */
  async searchStock(query: string): Promise<void> {
    await this.fill(this.SEARCH_INPUT, query);
    await this.click(this.SEARCH_BUTTON);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Get number of stocks displayed
   */
  async getStockCount(): Promise<number> {
    const stocks = await this.page.locator(this.STOCK_ITEM).count();
    return stocks;
  }

  /**
   * Click on stock item
   */
  async clickStock(index: number): Promise<void> {
    const stocks = this.page.locator(this.STOCK_ITEM);
    await stocks.nth(index).click();
  }

  /**
   * Apply filter
   */
  async applyFilter(filterType: string, value: string): Promise<void> {
    await this.click(this.FILTER_BUTTON);
    await this.click(`[data-testid="filter-${filterType}"]`);
    await this.fill(`[data-testid="filter-${filterType}-input"]`, value);
    await this.click('[data-testid="apply-filter"]');
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Get stock data from first item
   */
  async getFirstStockData(): Promise<{
    symbol: string;
    name: string;
    price: string;
    change: string;
  }> {
    const item = this.page.locator(this.STOCK_ITEM).first();
    return {
      symbol: await item.locator('[data-testid="symbol"]').textContent() || '',
      name: await item.locator('[data-testid="name"]').textContent() || '',
      price: await item.locator('[data-testid="price"]').textContent() || '',
      change: await item.locator('[data-testid="change"]').textContent() || '',
    };
  }

  /**
   * Verify market page loaded
   */
  async verifyMarketPageLoaded(): Promise<boolean> {
    const searchVisible = await this.isVisible(this.SEARCH_INPUT);
    const listVisible = await this.isVisible(this.STOCK_LIST);
    return searchVisible && listVisible;
  }
}

/**
 * Stock Detail Page Object
 * Handles stock detail page interactions
 */
export class StockDetailPage extends BasePage {
  // Selectors
  private readonly STOCK_NAME = '[data-testid="stock-name"]';
  private readonly STOCK_PRICE = '[data-testid="stock-price"]';
  private readonly PRICE_CHANGE = '[data-testid="price-change"]';
  private readonly CHART_CONTAINER = '[data-testid="chart-container"]';
  private readonly TIME_RANGE_SELECTOR = '[data-testid="time-range-selector"]';
  private readonly INDICATOR_SELECT = '[data-testid="indicator-select"]';
  private readonly ADD_INDICATOR_BTN = '[data-testid="add-indicator"]';
  private readonly TRADE_FORM = '[data-testid="trade-form"]';
  private readonly BUY_BUTTON = '[data-testid="buy-button"]';
  private readonly SELL_BUTTON = '[data-testid="sell-button"]';
  private readonly QUANTITY_INPUT = '[data-testid="quantity-input"]';
  private readonly PRICE_INPUT = '[data-testid="price-input"]';
  private readonly LOADING = '[data-testid="loading-spinner"]';

  /**
   * Navigate to stock detail page
   */
  async navigateToStockDetail(symbol: string): Promise<void> {
    await this.navigate(`/stock/${symbol}`);
  }

  /**
   * Get stock name
   */
  async getStockName(): Promise<string> {
    return this.getText(this.STOCK_NAME);
  }

  /**
   * Get current price
   */
  async getCurrentPrice(): Promise<number> {
    const text = await this.getText(this.STOCK_PRICE);
    const match = text.match(/[\d.]+/);
    return match ? parseFloat(match[0]) : 0;
  }

  /**
   * Get price change
   */
  async getPriceChange(): Promise<string> {
    return this.getText(this.PRICE_CHANGE);
  }

  /**
   * Select time range for chart
   */
  async selectTimeRange(range: '1D' | '5D' | '1M' | '3M' | '1Y'): Promise<void> {
    await this.click(`${this.TIME_RANGE_SELECTOR} button:has-text("${range}")`);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Add technical indicator
   */
  async addIndicator(indicatorName: string): Promise<void> {
    await this.click(this.ADD_INDICATOR_BTN);
    await this.page.locator(`text=${indicatorName}`).click();
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Fill buy order form
   */
  async fillBuyOrder(quantity: string, price?: string): Promise<void> {
    await this.fill(this.QUANTITY_INPUT, quantity);
    if (price) {
      await this.fill(this.PRICE_INPUT, price);
    }
  }

  /**
   * Submit buy order
   */
  async submitBuyOrder(): Promise<void> {
    await this.click(this.BUY_BUTTON);
  }

  /**
   * Fill sell order form
   */
  async fillSellOrder(quantity: string, price?: string): Promise<void> {
    await this.fill(this.QUANTITY_INPUT, quantity);
    if (price) {
      await this.fill(this.PRICE_INPUT, price);
    }
  }

  /**
   * Submit sell order
   */
  async submitSellOrder(): Promise<void> {
    await this.click(this.SELL_BUTTON);
  }

  /**
   * Verify stock detail page loaded
   */
  async verifyDetailPageLoaded(): Promise<boolean> {
    const nameVisible = await this.isVisible(this.STOCK_NAME);
    const priceVisible = await this.isVisible(this.STOCK_PRICE);
    const chartVisible = await this.isVisible(this.CHART_CONTAINER);
    return nameVisible && priceVisible && chartVisible;
  }

  /**
   * Check if chart is loaded
   */
  async isChartLoaded(): Promise<boolean> {
    try {
      await this.page.waitForSelector('[data-testid="chart-canvas"]', { timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }
}

/**
 * Technical Analysis Page Object
 * Handles technical analysis page interactions
 */
export class TechnicalAnalysisPage extends BasePage {
  // Selectors
  private readonly INDICATOR_SEARCH = '[data-testid="indicator-search"]';
  private readonly INDICATOR_LIST = '[data-testid="indicator-list"]';
  private readonly INDICATOR_ITEM = '[data-testid="indicator-item"]';
  private readonly CATEGORY_FILTER = '[data-testid="category-filter"]';
  private readonly PARAMETER_INPUT = '[data-testid="parameter-input"]';
  private readonly SAVE_BUTTON = '[data-testid="save-template-button"]';
  private readonly BACKTEST_BUTTON = '[data-testid="backtest-button"]';
  private readonly LOADING = '[data-testid="loading-spinner"]';
  private readonly ERROR = '[data-testid="error-message"]';

  /**
   * Navigate to technical analysis page
   */
  async navigateToTechnicalAnalysis(): Promise<void> {
    await this.navigate('/technical-analysis');
  }

  /**
   * Search for indicator
   */
  async searchIndicator(query: string): Promise<void> {
    await this.fill(this.INDICATOR_SEARCH, query);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Get number of indicators found
   */
  async getIndicatorCount(): Promise<number> {
    return this.page.locator(this.INDICATOR_ITEM).count();
  }

  /**
   * Select indicator by name
   */
  async selectIndicator(name: string): Promise<void> {
    await this.page.locator(`${this.INDICATOR_ITEM}:has-text("${name}")`).click();
  }

  /**
   * Filter by category
   */
  async filterByCategory(category: string): Promise<void> {
    await this.click(this.CATEGORY_FILTER);
    await this.page.locator(`text=${category}`).click();
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Set indicator parameter
   */
  async setParameter(paramName: string, value: string): Promise<void> {
    await this.fill(`${this.PARAMETER_INPUT}[data-param="${paramName}"]`, value);
  }

  /**
   * Save indicator template
   */
  async saveTemplate(templateName: string): Promise<void> {
    await this.click(this.SAVE_BUTTON);
    await this.fill('[data-testid="template-name-input"]', templateName);
    await this.click('[data-testid="confirm-save"]');
  }

  /**
   * Run backtest
   */
  async runBacktest(): Promise<void> {
    await this.click(this.BACKTEST_BUTTON);
    await this.waitForDataLoad(this.LOADING, 30000); // Backtest may take longer
  }

  /**
   * Click on indicator by index
   */
  async clickIndicator(index: number): Promise<void> {
    const items = this.page.locator(this.INDICATOR_ITEM);
    await items.nth(index).click();
  }

  /**
   * Get first indicator data
   */
  async getFirstIndicatorData(): Promise<{
    name: string;
    abbr: string;
    category: string;
  }> {
    const item = this.page.locator(this.INDICATOR_ITEM).first();
    const name = await item.locator('[data-field="name"]').textContent();
    const abbr = await item.locator('[data-field="abbr"]').textContent();
    const category = await item.locator('[data-field="category"]').textContent();

    return {
      name: name || '',
      abbr: abbr || '',
      category: category || '',
    };
  }

  /**
   * Verify page loaded
   */
  async verifyPageLoaded(): Promise<boolean> {
    const searchVisible = await this.isVisible(this.INDICATOR_SEARCH);
    const listVisible = await this.isVisible(this.INDICATOR_LIST);
    return searchVisible && listVisible;
  }
}

/**
 * Trade Management Page Object
 * Handles trade management page interactions
 */
export class TradeManagementPage extends BasePage {
  // Selectors
  private readonly ORDERS_TAB = '[data-testid="orders-tab"]';
  private readonly POSITIONS_TAB = '[data-testid="positions-tab"]';
  private readonly HISTORY_TAB = '[data-testid="history-tab"]';
  private readonly ORDERS_LIST = '[data-testid="orders-list"]';
  private readonly ORDER_ITEM = '[data-testid="order-item"]';
  private readonly POSITIONS_LIST = '[data-testid="positions-list"]';
  private readonly POSITION_ITEM = '[data-testid="position-item"]';
  private readonly CLOSE_BUTTON = '[data-testid="close-button"]';
  private readonly CANCEL_BUTTON = '[data-testid="cancel-button"]';
  private readonly EXPORT_BUTTON = '[data-testid="export-button"]';
  private readonly SEARCH_INPUT = '[data-testid="search-input"]';
  private readonly LOADING = '[data-testid="loading-spinner"]';
  private readonly EMPTY_STATE = '[data-testid="empty-state"]';

  /**
   * Navigate to trade management
   */
  async navigateToTradeManagement(): Promise<void> {
    await this.navigate('/trade-management');
  }

  /**
   * Switch to orders tab
   */
  async switchToOrdersTab(): Promise<void> {
    await this.click(this.ORDERS_TAB);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Switch to positions tab
   */
  async switchToPositionsTab(): Promise<void> {
    await this.click(this.POSITIONS_TAB);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Switch to history tab
   */
  async switchToHistoryTab(): Promise<void> {
    await this.click(this.HISTORY_TAB);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Get number of orders
   */
  async getOrderCount(): Promise<number> {
    return this.page.locator(this.ORDER_ITEM).count();
  }

  /**
   * Get number of positions
   */
  async getPositionCount(): Promise<number> {
    return this.page.locator(this.POSITION_ITEM).count();
  }

  /**
   * Close position
   */
  async closePosition(index: number): Promise<void> {
    const positions = this.page.locator(this.POSITION_ITEM);
    const position = positions.nth(index);
    const closeBtn = position.locator(this.CLOSE_BUTTON);
    await closeBtn.click();
    await this.page.locator('[data-testid="confirm-close"]').click();
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Cancel order
   */
  async cancelOrder(index: number): Promise<void> {
    const orders = this.page.locator(this.ORDER_ITEM);
    const order = orders.nth(index);
    const cancelBtn = order.locator(this.CANCEL_BUTTON);
    await cancelBtn.click();
    await this.page.locator('[data-testid="confirm-cancel"]').click();
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Search orders
   */
  async searchOrders(query: string): Promise<void> {
    await this.fill(this.SEARCH_INPUT, query);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Export orders
   */
  async exportOrders(): Promise<void> {
    await this.click(this.EXPORT_BUTTON);
    // Wait for download to complete
    await this.page.waitForEvent('download');
  }

  /**
   * Search positions
   */
  async searchPositions(query: string): Promise<void> {
    await this.fill(this.SEARCH_INPUT, query);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Get first order data
   */
  async getFirstOrderData(): Promise<{
    symbol?: string;
    stock?: string;
    quantity?: number;
    qty?: number;
    price?: number;
    order_price?: number;
  } | null> {
    const item = this.page.locator(this.ORDER_ITEM).first();
    const exists = await item.count();

    if (!exists) return null;

    const symbol = await item.locator('[data-field="symbol"], [data-field="stock"]').textContent();
    const quantity = await item.locator('[data-field="quantity"], [data-field="qty"]').textContent();
    const price = await item.locator('[data-field="price"], [data-field="order_price"]').textContent();

    return {
      symbol: symbol || undefined,
      quantity: quantity ? parseInt(quantity) : undefined,
      price: price ? parseFloat(price) : undefined,
    };
  }

  /**
   * Get first position data
   */
  async getFirstPositionData(): Promise<{
    symbol?: string;
    stock?: string;
    quantity?: number;
    qty?: number;
    price?: number;
    cost_price?: number;
    profit?: number;
    loss?: number;
  } | null> {
    const item = this.page.locator(this.POSITION_ITEM).first();
    const exists = await item.count();

    if (!exists) return null;

    const symbol = await item.locator('[data-field="symbol"], [data-field="stock"]').textContent();
    const quantity = await item.locator('[data-field="quantity"], [data-field="qty"]').textContent();
    const price = await item.locator('[data-field="price"], [data-field="cost_price"]').textContent();
    const profit = await item.locator('[data-field="profit"], [data-field="profit_loss"]').textContent();

    return {
      symbol: symbol || undefined,
      quantity: quantity ? parseInt(quantity) : undefined,
      price: price ? parseFloat(price) : undefined,
      profit: profit ? parseFloat(profit) : undefined,
    };
  }

  /**
   * Verify page loaded
   */
  async verifyPageLoaded(): Promise<boolean> {
    const ordersTabVisible = await this.isVisible(this.ORDERS_TAB);
    const listVisible = await this.isVisible(this.ORDERS_LIST);
    return ordersTabVisible && listVisible;
  }
}

/**
 * Strategy Management Page Object
 * Handles strategy management page interactions
 */
export class StrategyManagementPage extends BasePage {
  // Selectors
  private readonly STRATEGY_LIST = '[data-testid="strategy-list"]';
  private readonly STRATEGY_ITEM = '[data-testid="strategy-item"]';
  private readonly STRATEGY_SEARCH = '[data-testid="strategy-search"]';
  private readonly CREATE_BUTTON = '[data-testid="create-strategy"]';
  private readonly DELETE_BUTTON = '[data-testid="delete-strategy"]';
  private readonly EDIT_BUTTON = '[data-testid="edit-strategy"]';
  private readonly LOADING = '[data-testid="loading-spinner"]';
  private readonly ERROR = '[data-testid="error-message"]';

  /**
   * Navigate to strategy management
   */
  async navigateToStrategyManagement(): Promise<void> {
    await this.navigate('/strategy-management');
  }

  /**
   * Get number of strategies
   */
  async getStrategyCount(): Promise<number> {
    return this.page.locator(this.STRATEGY_ITEM).count();
  }

  /**
   * Search for strategy
   */
  async searchStrategy(query: string): Promise<void> {
    await this.fill(this.STRATEGY_SEARCH, query);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Get first strategy data
   */
  async getFirstStrategyData(): Promise<{
    name: string;
    status: string;
    win_rate?: number;
    total_return?: number;
  } | null> {
    const item = this.page.locator(this.STRATEGY_ITEM).first();
    const exists = await item.count();

    if (!exists) return null;

    const name = await item.locator('[data-field="name"]').textContent();
    const status = await item.locator('[data-field="status"]').textContent();
    const winRate = await item.locator('[data-field="win_rate"]').textContent();
    const totalReturn = await item.locator('[data-field="total_return"]').textContent();

    return {
      name: name || '',
      status: status || '',
      win_rate: winRate ? parseFloat(winRate) : undefined,
      total_return: totalReturn ? parseFloat(totalReturn) : undefined,
    };
  }

  /**
   * Verify page loaded
   */
  async verifyPageLoaded(): Promise<boolean> {
    const listVisible = await this.isVisible(this.STRATEGY_LIST);
    return listVisible;
  }
}
