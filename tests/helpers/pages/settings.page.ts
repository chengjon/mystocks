import { BasePage } from './base.page';

/**
 * Settings Page Object
 * Handles settings page interactions
 */
export class SettingsPage extends BasePage {
  // Selectors
  private readonly ACCOUNT_TAB = '[data-testid="account-tab"]';
  private readonly NOTIFICATIONS_TAB = '[data-testid="notifications-tab"]';
  private readonly API_KEYS_TAB = '[data-testid="api-keys-tab"]';
  private readonly USERNAME_FIELD = '[data-testid="username"]';
  private readonly EMAIL_FIELD = '[data-testid="email"]';
  private readonly SAVE_BUTTON = '[data-testid="save-account"]';
  private readonly LOADING = '[data-testid="loading-spinner"]';

  /**
   * Navigate to settings
   */
  async navigateToSettings(): Promise<void> {
    await this.navigate('/settings');
  }

  /**
   * Click account tab
   */
  async clickAccountTab(): Promise<void> {
    await this.click(this.ACCOUNT_TAB);
    await this.waitForPageLoad();
  }

  /**
   * Click notifications tab
   */
  async clickNotificationsTab(): Promise<void> {
    await this.click(this.NOTIFICATIONS_TAB);
    await this.waitForPageLoad();
  }

  /**
   * Click API keys tab
   */
  async clickApiKeysTab(): Promise<void> {
    await this.click(this.API_KEYS_TAB);
    await this.waitForPageLoad();
  }

  /**
   * Get username
   */
  async getUsername(): Promise<string> {
    return this.getText(this.USERNAME_FIELD);
  }

  /**
   * Get email
   */
  async getEmail(): Promise<string> {
    return this.getText(this.EMAIL_FIELD);
  }

  /**
   * Update username
   */
  async updateUsername(username: string): Promise<void> {
    await this.fill(this.USERNAME_FIELD, username);
    await this.click(this.SAVE_BUTTON);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Update email
   */
  async updateEmail(email: string): Promise<void> {
    await this.fill(this.EMAIL_FIELD, email);
    await this.click(this.SAVE_BUTTON);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Verify page loaded
   */
  async verifyPageLoaded(): Promise<boolean> {
    const accountTabVisible = await this.isVisible(this.ACCOUNT_TAB);
    const notifTabVisible = await this.isVisible(this.NOTIFICATIONS_TAB);
    return accountTabVisible && notifTabVisible;
  }
}
