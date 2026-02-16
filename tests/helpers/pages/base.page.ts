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
