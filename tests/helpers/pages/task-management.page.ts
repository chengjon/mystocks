import { BasePage } from './base.page';

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
