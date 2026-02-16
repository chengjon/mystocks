import { Locator } from '@playwright/test';
import { BasePage } from './base.page';

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
