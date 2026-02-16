import { BasePage } from './base.page';

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
