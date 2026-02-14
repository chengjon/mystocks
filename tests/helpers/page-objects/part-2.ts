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

/**
 * Risk Monitor Page Object
 * Handles risk monitoring page interactions
 */
export class RiskMonitorPage extends BasePage {
  // Selectors
  private readonly RISK_SCORE = '[data-testid="risk-score"]';
  private readonly RISK_LEVEL = '[data-testid="risk-level"]';
  private readonly POSITION_RISK_TABLE = '[data-testid="position-risk-table"]';
  private readonly POSITION_RISK_ITEM = '[data-testid="position-risk-item"]';
  private readonly RISK_ALERTS = '[data-testid="risk-alerts"]';
  private readonly ALERT_ITEM = '[data-testid="alert-item"]';
  private readonly LOADING = '[data-testid="loading-spinner"]';

  /**
   * Navigate to risk monitor
   */
  async navigateToRiskMonitor(): Promise<void> {
    await this.navigate('/risk-monitor');
  }

  /**
   * Get risk score
   */
  async getRiskScore(): Promise<string> {
    return this.getText(this.RISK_SCORE);
  }

  /**
   * Get risk level
   */
  async getRiskLevel(): Promise<string> {
    return this.getText(this.RISK_LEVEL);
  }

  /**
   * Get position count
   */
  async getPositionCount(): Promise<number> {
    return this.page.locator(this.POSITION_RISK_ITEM).count();
  }

  /**
   * Get alert count
   */
  async getAlertCount(): Promise<number> {
    return this.page.locator(this.ALERT_ITEM).count();
  }

  /**
   * Verify page loaded
   */
  async verifyPageLoaded(): Promise<boolean> {
    const scoreVisible = await this.isVisible(this.RISK_SCORE);
    const levelVisible = await this.isVisible(this.RISK_LEVEL);
    return scoreVisible && levelVisible;
  }
}

