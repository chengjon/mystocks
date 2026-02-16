import { BasePage } from './base.page';

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
