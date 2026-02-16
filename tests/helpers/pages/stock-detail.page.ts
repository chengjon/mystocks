import { BasePage } from './base.page';

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
