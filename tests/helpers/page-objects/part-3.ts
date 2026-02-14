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
 * Task Management Page Object
 * Handles task management page interactions
 */
export class TaskManagementPage extends BasePage {
  // Selectors
  private readonly TASK_LIST = '[data-testid="task-list"]';
  private readonly TASK_ITEM = '[data-testid="task-item"]';
  private readonly TASK_SEARCH = '[data-testid="task-search"]';
  private readonly CREATE_BUTTON = '[data-testid="create-task"]';
  private readonly DELETE_BUTTON = '[data-testid="delete-task"]';
  private readonly COMPLETE_BUTTON = '[data-testid="complete-task"]';
  private readonly LOADING = '[data-testid="loading-spinner"]';

  /**
   * Navigate to task management
   */
  async navigateToTaskManagement(): Promise<void> {
    await this.navigate('/task-management');
  }

  /**
   * Get task count
   */
  async getTaskCount(): Promise<number> {
    return this.page.locator(this.TASK_ITEM).count();
  }

  /**
   * Search for task
   */
  async searchTask(query: string): Promise<void> {
    await this.fill(this.TASK_SEARCH, query);
    await this.waitForDataLoad(this.LOADING);
  }

  /**
   * Get first task data
   */
  async getFirstTaskData(): Promise<{
    title: string;
    status: string;
    priority?: string;
  } | null> {
    const item = this.page.locator(this.TASK_ITEM).first();
    const exists = await item.count();

    if (!exists) return null;

    const title = await item.locator('[data-field="title"]').textContent();
    const status = await item.locator('[data-field="status"]').textContent();
    const priority = await item.locator('[data-field="priority"]').textContent();

    return {
      title: title || '',
      status: status || '',
      priority: priority || undefined,
    };
  }

  /**
   * Verify page loaded
   */
  async verifyPageLoaded(): Promise<boolean> {
    const listVisible = await this.isVisible(this.TASK_LIST);
    return listVisible;
  }
}

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

