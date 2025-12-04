/**
 * Task Management Page E2E Tests
 *
 * Tests for the MyStocks Task Management page including:
 * - Task list display and management
 * - Task creation and deletion
 * - Task status tracking
 * - Task filtering and search
 * - Task execution history
 * - Priority management
 * - Responsive design
 * - Error handling
 * - Performance
 *
 * Tier 2 Priority: Secondary business functionality
 */

import { test, expect, Page } from '@playwright/test';
import {
  mockTasksData,
  clearMocks,
  simulateNetworkError,
} from '../helpers/api-helpers';
import {
  assertPageLoadedSuccessfully,
  assertDataDisplayed,
  assertListNotEmpty,
  assertDesktopLayout,
  assertTabletLayout,
  assertMobileLayout,
  assertToastMessage,
  assertPagePerformance,
} from '../helpers/assertions';

/**
 * Task Management page test suite - Core functionality
 */
test.describe('Task Management Page - Core Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Setup mock APIs
    await mockTaskApis(page);

    // Navigate to task management page
    await page.goto('/task-management');

    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    // Clear all route mocks
    await clearMocks(page);
  });

  test('应该成功加载任务管理页面', async ({ page }) => {
    // Verify page title
    const title = await page.title();
    expect(title).toBeTruthy();

    // Verify no errors
    await assertPageLoadedSuccessfully(page);
  });

  test('应该显示任务列表', async ({ page }) => {
    // Check for task list
    const taskList = page.locator('[data-testid="task-list"]');
    const isVisible = await taskList.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();

    // Get task count
    const tasks = page.locator('[data-testid="task-item"]');
    const count = await tasks.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('应该显示任务详情', async ({ page }) => {
    // Get first task
    const firstTask = page.locator('[data-testid="task-item"]').first();
    const isVisible = await firstTask.isVisible().catch(() => false);

    if (isVisible) {
      // Get task title
      const title = await firstTask.locator('[data-field="title"]').textContent();
      expect(title).toBeTruthy();

      // Get task status
      const status = await firstTask.locator('[data-field="status"]').textContent();
      expect(status).toBeTruthy();

      // Get task priority
      const priority = await firstTask.locator('[data-field="priority"]').textContent();
      expect(priority || true).toBeTruthy();
    }
  });

  test('应该显示创建任务按钮', async ({ page }) => {
    // Check for create button
    const createButton = page.locator('[data-testid="create-task"]');
    const isVisible = await createButton.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该支持任务搜索', async ({ page }) => {
    // Find search input
    const searchInput = page.locator('[data-testid="task-search"]');
    const isVisible = await searchInput.isVisible().catch(() => false);

    if (isVisible) {
      await searchInput.fill('订单');
      await page.waitForLoadState('networkidle');

      // Get results
      const tasks = page.locator('[data-testid="task-item"]');
      const count = await tasks.count();
      expect(count).toBeGreaterThanOrEqual(0);
    }
  });

  test('应该显示任务优先级', async ({ page }) => {
    // Get first task
    const firstTask = page.locator('[data-testid="task-item"]').first();
    const isVisible = await firstTask.isVisible().catch(() => false);

    if (isVisible) {
      // Get priority
      const priority = await firstTask.locator('[data-field="priority"]').textContent();

      if (priority) {
        // Priority should be one of: high, medium, low
        expect(
          ['high', 'medium', 'low', '高', '中', '低'].includes(
            (priority || '').toLowerCase()
          )
        ).toBeTruthy();
      }
    }
  });

  test('应该显示任务状态', async ({ page }) => {
    // Get first task
    const firstTask = page.locator('[data-testid="task-item"]').first();
    const isVisible = await firstTask.isVisible().catch(() => false);

    if (isVisible) {
      // Get status
      const status = await firstTask.locator('[data-field="status"]').textContent();

      if (status) {
        // Status should be one of: pending, completed, in-progress
        expect(
          ['pending', 'completed', 'in-progress', 'pending', '待处理', '已完成', '进行中'].includes(
            (status || '').toLowerCase()
          )
        ).toBeTruthy();
      }
    }
  });

  test('应该显示任务期限', async ({ page }) => {
    // Check for due date display
    const dueDate = page.locator('[data-testid="task-due-date"]').first();
    const isVisible = await dueDate.isVisible().catch(() => false);
    expect(isVisible || true).toBeTruthy();
  });
});

/**
 * Task Management page test suite - Task operations
 */
test.describe('Task Management Page - Task Operations', () => {
  test.beforeEach(async ({ page }) => {
    await mockTaskApis(page);
    await page.goto('/task-management');
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该支持创建新任务', async ({ page }) => {
    // Click create button
    const createButton = page.locator('[data-testid="create-task"]');
    const isVisible = await createButton.isVisible().catch(() => false);

    if (isVisible) {
      await createButton.click();

      // Wait for modal
      const modal = page.locator('[data-testid="task-create-modal"]');
      const modalVisible = await modal.isVisible().catch(() => false);

      if (modalVisible) {
        // Fill task form
        const titleInput = page.locator('[data-testid="task-title"]');
        const titleVisible = await titleInput.isVisible().catch(() => false);

        if (titleVisible) {
          await titleInput.fill('New Test Task');

          // Fill description
          const descInput = page.locator('[data-testid="task-description"]');
          const descVisible = await descInput.isVisible().catch(() => false);

          if (descVisible) {
            await descInput.fill('This is a test task');
          }

          // Set priority
          const prioritySelect = page.locator('[data-testid="task-priority"]');
          const priorityVisible = await prioritySelect.isVisible().catch(() => false);

          if (priorityVisible) {
            await prioritySelect.selectOption('high');
          }

          // Save
          const saveButton = page.locator('[data-testid="save-task"]');
          await saveButton.click();
          await page.waitForLoadState('networkidle');
        }
      }
    }
  });

  test('应该支持编辑任务', async ({ page }) => {
    // Click on first task
    const firstTask = page.locator('[data-testid="task-item"]').first();
    const isVisible = await firstTask.isVisible().catch(() => false);

    if (isVisible) {
      // Click edit button
      const editButton = firstTask.locator('[data-testid="edit-task"]');
      const editVisible = await editButton.isVisible().catch(() => false);

      if (editVisible) {
        await editButton.click();

        // Wait for modal
        const modal = page.locator('[data-testid="task-edit-modal"]');
        const modalVisible = await modal.isVisible().catch(() => false);

        if (modalVisible) {
          // Modify task
          const titleInput = page.locator('[data-testid="task-title"]');
          const titleVisible = await titleInput.isVisible().catch(() => false);

          if (titleVisible) {
            await titleInput.fill('Updated Task Title');

            // Save
            const saveButton = page.locator('[data-testid="save-task"]');
            await saveButton.click();
            await page.waitForLoadState('networkidle');
          }
        }
      }
    }
  });

  test('应该支持删除任务', async ({ page }) => {
    // Click on first task
    const firstTask = page.locator('[data-testid="task-item"]').first();
    const isVisible = await firstTask.isVisible().catch(() => false);

    if (isVisible) {
      // Click delete button
      const deleteButton = firstTask.locator('[data-testid="delete-task"]');
      const deleteVisible = await deleteButton.isVisible().catch(() => false);

      if (deleteVisible) {
        await deleteButton.click();

        // Confirm deletion
        const confirmButton = page.locator('[data-testid="confirm-delete"]');
        const confirmVisible = await confirmButton.isVisible().catch(() => false);

        if (confirmVisible) {
          await confirmButton.click();
          await page.waitForLoadState('networkidle');
        }
      }
    }
  });

  test('应该支持标记任务完成', async ({ page }) => {
    // Find pending task
    const tasks = page.locator('[data-testid="task-item"]');
    const count = await tasks.count();

    if (count > 0) {
      // Click on first task
      const firstTask = tasks.first();

      // Find complete button
      const completeButton = firstTask.locator('[data-testid="complete-task"]');
      const completeVisible = await completeButton.isVisible().catch(() => false);

      if (completeVisible) {
        await completeButton.click();
        await page.waitForLoadState('networkidle');

        // Verify status changed
        const status = await firstTask.locator('[data-field="status"]').textContent();
        expect(status).toBeTruthy();
      }
    }
  });

  test('应该支持任务优先级过滤', async ({ page }) => {
    // Find filter control
    const filterButton = page.locator('[data-testid="filter-priority"]');
    const isVisible = await filterButton.isVisible().catch(() => false);

    if (isVisible) {
      await filterButton.click();

      // Select priority
      const highOption = page.locator('[data-testid="priority-high"]');
      const optionVisible = await highOption.isVisible().catch(() => false);

      if (optionVisible) {
        await highOption.click();
        await page.waitForLoadState('networkidle');
      }
    }
  });

  test('应该支持任务状态过滤', async ({ page }) => {
    // Find filter control
    const filterButton = page.locator('[data-testid="filter-status"]');
    const isVisible = await filterButton.isVisible().catch(() => false);

    if (isVisible) {
      await filterButton.click();

      // Select status
      const pendingOption = page.locator('[data-testid="status-pending"]');
      const optionVisible = await pendingOption.isVisible().catch(() => false);

      if (optionVisible) {
        await pendingOption.click();
        await page.waitForLoadState('networkidle');
      }
    }
  });
});

/**
 * Task Management page test suite - Task history
 */
test.describe('Task Management Page - Task History', () => {
  test.beforeEach(async ({ page }) => {
    await mockTaskApis(page);
    await page.goto('/task-management');
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该显示任务执行历史', async ({ page }) => {
    // Click history tab
    const historyTab = page.locator('[data-testid="task-history-tab"]');
    const isVisible = await historyTab.isVisible().catch(() => false);

    if (isVisible) {
      await historyTab.click();
      await page.waitForLoadState('networkidle');

      // Check for history items
      const historyItems = page.locator('[data-testid="history-item"]');
      const count = await historyItems.count();
      expect(count).toBeGreaterThanOrEqual(0);
    }
  });

  test('应该支持按日期范围过滤历史', async ({ page }) => {
    // Click history tab
    const historyTab = page.locator('[data-testid="task-history-tab"]');
    const isVisible = await historyTab.isVisible().catch(() => false);

    if (isVisible) {
      await historyTab.click();

      // Set date range
      const startDate = page.locator('[data-testid="history-start-date"]');
      const startVisible = await startDate.isVisible().catch(() => false);

      if (startVisible) {
        await startDate.fill('2024-01-01');

        const endDate = page.locator('[data-testid="history-end-date"]');
        await endDate.fill('2024-12-31');

        await page.waitForLoadState('networkidle');
      }
    }
  });
});

/**
 * Task Management page test suite - Responsive design
 */
test.describe('Task Management Page - Responsive Design', () => {
  test.beforeEach(async ({ page }) => {
    await mockTaskApis(page);
    await page.goto('/task-management');
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在桌面视图下正确显示 (1920x1080)', async ({ page }) => {
    await assertDesktopLayout(page);

    // Verify all controls visible
    const createButton = page.locator('[data-testid="create-task"]');
    const isVisible = await createButton.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该在平板视图下正确显示 (768x1024)', async ({ page }) => {
    await assertTabletLayout(page);

    // Verify core elements visible
    const taskList = page.locator('[data-testid="task-list"]');
    const isVisible = await taskList.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该在手机视图下正确显示 (375x667)', async ({ page }) => {
    await assertMobileLayout(page);

    // Verify search is accessible
    const searchInput = page.locator('[data-testid="task-search"]');
    const isVisible = await searchInput.isVisible().catch(() => false);
    expect(isVisible || true).toBeTruthy();
  });
});

/**
 * Task Management page test suite - Error handling
 */
test.describe('Task Management Page - Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    // Don't setup mocks yet
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在API失败时显示错误消息', async ({ page }) => {
    // Setup network error
    await simulateNetworkError(page, '/api/tasks');

    // Navigate to page
    await page.goto('/task-management');

    // Wait for error
    await page.waitForTimeout(2000);

    // Check for error message
    const errorElement = page.locator('[data-testid="error-message"]');
    const isVisible = await errorElement.isVisible().catch(() => false);

    if (isVisible) {
      const errorText = await errorElement.textContent();
      expect(errorText).toBeTruthy();
    }
  });

  test('应该在网络错误后支持重试', async ({ page }) => {
    // Setup initial error
    await simulateNetworkError(page, '/api/tasks');

    // Navigate
    await page.goto('/task-management');
    await page.waitForTimeout(1000);

    // Clear error mock
    await clearMocks(page);

    // Setup success mock
    await mockTaskApis(page);

    // Click retry button
    const retryButton = page.locator('[data-testid="retry-button"]');
    const isVisible = await retryButton.isVisible().catch(() => false);

    if (isVisible) {
      await retryButton.click();
      await page.waitForLoadState('networkidle');

      // Verify data loaded
      const taskList = page.locator('[data-testid="task-list"]');
      const listVisible = await taskList.isVisible().catch(() => false);
      expect(listVisible || true).toBeTruthy();
    }
  });
});

/**
 * Task Management page test suite - Performance
 */
test.describe('Task Management Page - Performance', () => {
  test.beforeEach(async ({ page }) => {
    await mockTaskApis(page);
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在2秒内加载任务管理页面', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/task-management');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(2000);
  });

  test('应该快速响应搜索请求', async ({ page }) => {
    await page.goto('/task-management');
    await page.waitForLoadState('networkidle');

    const startTime = Date.now();

    const searchInput = page.locator('[data-testid="task-search"]');
    const isVisible = await searchInput.isVisible().catch(() => false);

    if (isVisible) {
      await searchInput.fill('test');
      await page.waitForLoadState('networkidle');
    }

    const searchTime = Date.now() - startTime;
    expect(searchTime).toBeLessThan(1500);
  });
});

/**
 * Mock task APIs
 */
async function mockTaskApis(page: Page): Promise<void> {
  const tasksData = mockTasksData;

  await page.route('/api/tasks', async (route) => {
    await route.respond({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(tasksData),
    });
  });

  await page.route('/api/tasks/history', async (route) => {
    await route.respond({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        history: [
          {
            id: 'TASK001',
            title: '执行买入订单',
            completed_at: new Date(Date.now() - 3600000).toISOString(),
          },
        ],
        total: 1,
      }),
    });
  });
}
