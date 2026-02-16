import { BasePage } from './base.page';

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
