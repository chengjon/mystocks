import { BasePage } from './base.page';

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
