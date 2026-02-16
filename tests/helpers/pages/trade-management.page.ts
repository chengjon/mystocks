import { BasePage } from './base.page';

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
