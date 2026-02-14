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

